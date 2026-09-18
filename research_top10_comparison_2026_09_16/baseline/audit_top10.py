# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""Independent audit of per_query_top10.jsonl (baseline).

A: full structural check over all 9440 rows (no rescore).
B: full-rescore spot check on deterministic sample (30 queries) with inline
   independent ranking implementation (no import of metrics_top10 ranking).
"""
import glob
import hashlib
import json
import math
import pickle
from collections import Counter

import numpy as np

SALT = "top10-r1"


def indep_top10(scores, archive_id, k=10):
    s = np.asarray(scores, dtype=float).ravel()
    m = np.where(np.isfinite(s), s, -np.inf)
    hs = [hashlib.sha256(f"{SALT}|{archive_id}|{r}".encode()).hexdigest() for r in range(len(s))]
    return np.array(sorted(range(len(s)), key=lambda r: (-m[r], hs[r], r))[:k])


def indep_metrics(top, gold, k=10):
    top = [int(x) for x in top]
    gset = set(map(int, gold))
    inter = len([x for x in top if x in gset])
    hit = 1.0 if inter else 0.0
    rec = inter / len(gset)
    disc = [1.0 / math.log2(r + 2) for r in range(k)]
    idcg = sum(disc[:min(k, len(gset))])
    dcg = sum(disc[r] for r, d in enumerate(top) if d in gset)
    return hit, rec, (dcg / idcg if idcg else 0.0)


rows = [json.loads(l) for l in open("per_query_top10.jsonl", encoding="utf-8")]
print(f"rows={len(rows)}")
c = Counter(r["benchmark"] for r in rows)
print("counts", dict(c))
assert len(rows) == 9440 and c["PerLTQA"] == 8265 and c["LME"] == 470 and c["REALTALK"] == 705
bad = 0
for r in rows:
    for arm in ("sign96", "float_raw", "float_std", "asym"):
        a = r[arm]
        if len(a["ids"]) != 10 or len(set(a["ids"])) != 10:
            print("BAD len/dup", r["qid"], arm); bad += 1
        if any(not (0 <= x < r["N"]) for x in a["ids"]):
            print("BAD range", r["qid"], arm); bad += 1
        if any(x in (None,) for x in a["ids"]):
            print("BAD none", r["qid"]); bad += 1
        h, rc, nd = indep_metrics(a["ids"], r["gold"])
        if abs(h - a["hit10"]) > 1e-12 or abs(rc - a["recall10"]) > 1e-12 or abs(nd - a["ndcg10"]) > 1e-12:
            print("BAD metric", r["qid"], arm, (h, rc, nd), (a["hit10"], a["recall10"], a["ndcg10"])); bad += 1
print(f"structural mismatches={bad}")
assert bad == 0
# tie internal order: equal stored scores within top10 must follow hash order
tie_bad = 0
for r in rows:
    for arm in ("sign96", "float_raw", "float_std", "asym"):
        a = r[arm]
        sc = [(-np.inf if v is None else float(v)) for v in a["scores"]]
        hs = [hashlib.sha256(f"{SALT}|{r['archive_id']}|{x}".encode()).hexdigest() for x in a["ids"]]
        for i in range(9):
            if sc[i] < sc[i + 1] - 1e-12:
                print("BAD order", r["qid"], arm); tie_bad += 1; break
            if sc[i] == sc[i + 1] and not (hs[i] < hs[i + 1] or (hs[i] == hs[i + 1] and a["ids"][i] < a["ids"][i + 1])):
                print("BAD tie order", r["qid"], arm); tie_bad += 1; break
print(f"tie-order mismatches={tie_bad}")
assert tie_bad == 0
# spot full rescore: deterministic sample 10 per bench by sorted qid
sample = []
for b in ("PerLTQA", "LME", "REALTALK"):
    br = sorted([r for r in rows if r["benchmark"] == b], key=lambda r: r["qid"])
    step = max(1, len(br) // 10)
    sample.extend(br[::step][:10])
print(f"spot sample={len(sample)}")
R = "/mnt/c/Users/MDP/dev/llmzip-work"
arch = pickle.load(open(R + "/bench3/runs/b3b_perltqa/cache_arch_eval.pkl", "rb"))
Q = pickle.load(open(R + "/bench3/runs/b3b_perltqa/cache_q_eval.pkl", "rb"))
import glob as _g
lme_map = {}
for f in sorted(_g.glob(R + "/regen/lme/cache_repr/*.pkl")):
    d = pickle.loads(open(f, "rb").read())
    lme_map[d["question_id"]] = (f, d)
rt_map = {}
for f in sorted(_g.glob(R + "/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl")):
    o = pickle.loads(open(f, "rb").read())
    for qi, qid in enumerate(o["qids"]):
        rt_map[qid] = (f, o, qi)
nspot_bad = 0
for r in sample:
    if r["benchmark"] == "PerLTQA":
        C = np.asarray(arch[r["archive_id"]]["C"], float)
        q = np.asarray(Q[r["qid"]]["qC"], float)
    elif r["benchmark"] == "LME":
        _, d = lme_map[r["qid"]]
        C = np.asarray(d["C"], float); q = np.asarray(d["qC"], float)
    else:
        _, o, qi = rt_map[r["qid"]]
        C = np.asarray(o["C"], float); q = np.asarray(o["QC"][qi], float)
    N = int(C.shape[0])
    assert N == r["N"]
    std = np.std(C, axis=0, ddof=0).astype(float)
    std = np.where(std == 0, 1.0, std)
    packed = np.packbits((C >= 0), axis=-1, bitorder="big").astype(np.uint8)
    H = np.count_nonzero(np.unpackbits(packed, axis=1, bitorder="big")[:, :96].astype(bool) != (q >= 0)[None, :], axis=1)
    s_sign = (-H.astype(float))
    with np.errstate(divide="ignore", invalid="ignore"):
        s_raw = (C @ q) / (np.linalg.norm(C, axis=1) * np.linalg.norm(q))
        s_std = ((C / std[None, :]) @ (q / std)) / (np.linalg.norm(C / std[None, :], axis=1) * np.linalg.norm(q / std))
    D = np.where(np.unpackbits(packed, axis=1, bitorder="big")[:, :96].astype(bool), 1, -1).astype(float)
    s_asym = (D @ q) / float(np.sqrt(96))
    for arm, s in (("sign96", s_sign), ("float_raw", s_raw), ("float_std", s_std), ("asym", s_asym)):
        exp_top = indep_top10(s, r["archive_id"], 10).tolist()
        if exp_top != r[arm]["ids"]:
            print("SPOT MISMATCH", r["benchmark"], r["qid"], arm, exp_top[:4], r[arm]["ids"][:4]); nspot_bad += 1
print(f"spot mismatches={nspot_bad}")
assert nspot_bad == 0
print("AUDIT PASS")
