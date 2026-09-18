"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Two decisive read-only checks (no refitting, no rescoring of shipped arms):
A. FLOAT-DOT SETTLER (for 1a): score the SAME uncompressed 96-dim C with a
   qscale-style unnormalized dot s = C @ (QC/sigma) instead of standardized
   cosine. If float-dot >= BM25, the 'representation bottleneck' verdict is
   confounded by scorer choice. If float-dot ~= float_std < BM25, it survives.
B. IDF_p2 LEAVE-ONE-ARCHIVE-OUT (for 1c): recompute the rare-band FR@3 gain
   dropping each archive in turn, using the coordinator's own banding recipe.
   If dropping ONE archive kills the effect, it is an archive idiosyncrasy.
C. PerLTQA text stats (for 1b): doc/query lengths + vocab from cache_items.json
   and the PerLTQA query cache, vs the measured RealTalk numbers.
"""
import json, math, os, pickle, re
from collections import defaultdict
import numpy as np

R = "/mnt/c/Users/MDP/dev/llmzip-work"
BRAIN = "/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/digest_r1/brain"
OUT = BRAIN + "/check_decisive.json"
out = {"_label": "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]"}
WORD = re.compile(r"\w+", re.UNICODE)
TOKEN = re.compile(r"[a-z0-9]+")

# ============ A. float-dot on RealTalk ============
RT = R + "/bench3/runs/b3a_realtalk/rt_repr"
hits_dot, hits_cos_approx, nq = 0, 0, 0
per_arch_dot = {}
for i in range(1, 11):
    a = f"RT{i:02d}"
    o = pickle.loads(open(f"{RT}/{a}.pkl", "rb").read())
    C = np.asarray(o["C"], np.float64)
    sg = np.maximum(np.std(C, axis=0, ddof=0), 1e-12)
    for qi, qid in enumerate(o["qids"]):
        gold = set(int(x) for x in o["gold_rows"][qi])
        if not gold:
            continue
        qC = np.asarray(o["QC"][qi], np.float64)
        s = C @ (qC / sg)
        top10 = set(int(x) for x in np.argsort(-s, kind="stable")[:10])
        h = 1.0 if (top10 & gold) else 0.0
        hits_dot += h
        nq += 1
        d = per_arch_dot.setdefault(a, [0, 0])
        d[0] += h
        d[1] += 1
out["A_float_dot"] = {"n": nq, "hit10_pct": round(100 * hits_dot / nq, 2),
    "per_archive": {a: round(100 * v[0] / v[1], 2) for a, v in sorted(per_arch_dot.items())},
    "compare": {"float_std_cosine": 48.51, "sign96": 46.68, "qscale": 49.65, "BM25": 54.18,
                "note": "float_std/qscale/BM25 are coordinator re-derived values from the digest"}}

# ============ B. LOO on IDF_p2 rare-band FR@3 ============
SRC = R + "/top10_comparison_r1/math_r1/repr/per_query.jsonl"
RT_DATA = R + "/top10_comparison_r1/data"


def toks(s):
    return set(TOKEN.findall((s or "").lower()))


fr3 = {}
arch = {}
with open(SRC, encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if r.get("benchmark") != "RealTalk":
            continue
        if r.get("scorer") != "qscale" or r.get("arm") not in ("FULL", "IDF_p2"):
            continue
        qid = r["qid"]
        gold = set(r.get("gold") or [])
        top = r.get("top10") or []
        fr3[(r["arm"], qid)] = (len(gold & set(top[:3])) / len(gold)) if gold else 0.0
        arch[qid] = r.get("archive") or r.get("archive_id")

bands = {}
for i in range(1, 11):
    D = json.load(open(os.path.join(RT_DATA, f"RT{i:02d}.json"), encoding="utf-8"))
    docs = D["docs"]
    N = len(docs)
    df = defaultdict(int)
    dt = []
    for d_ in docs:
        t = toks(d_.get("text"))
        dt.append(t)
        for w in t:
            df[w] += 1
    row_of = {d_["row"]: j for j, d_ in enumerate(docs)}
    for q in D["queries"]:
        qt = toks(q.get("text"))
        best = -1.0
        for g in q.get("gold", []):
            j = row_of.get(g)
            if j is None:
                continue
            for w in (qt & dt[j]):
                best = max(best, math.log(N / df[w]))
        bands[q["qid"]] = ("no_shared" if best < 0 else "common" if best < 2
                           else "mid" if best < 4 else "rare")

rare_qs = [q for (arm, q) in fr3 if arm == "FULL" and bands.get(q) == "rare"]
rare_qs = sorted(set(rare_qs))
d_all = np.array([fr3[("IDF_p2", q)] - fr3[("FULL", q)] for q in rare_qs])
out["B_loo"] = {"n_rare": len(rare_qs),
                "full_mean_diff_pp": round(100 * d_all.mean(), 2)}
loo = []
for a in sorted(set(arch.values())):
    keep = [i for i, q in enumerate(rare_qs) if arch[q] != a]
    d = d_all[keep]
    # per-archive contribution: mean diff within dropped archive
    drop = [i for i, q in enumerate(rare_qs) if arch[q] == a]
    loo.append({"dropped": a, "n_dropped": len(drop),
                "kept_diff_pp": round(100 * d.mean(), 2),
                "dropped_arch_diff_pp": round(100 * d_all[drop].mean(), 2) if drop else None})
out["B_loo"]["rows"] = loo

# ============ C. PerLTQA text stats ============
items = json.load(open(R + "/bench3/runs/b3b_perltqa/cache_items.json", encoding="utf-8"))
dlens, vcb = [], set()
narch = len(items)
ndocs = 0
for k, v in items.items():
    for iid, text in v["items"]:
        t = WORD.findall(text.lower())
        dlens.append(len(t))
        vcb.update(t)
        ndocs += 1
dlens_sorted = sorted(dlens)


def pct(p):
    return dlens_sorted[min(len(dlens_sorted) - 1, int(p * len(dlens_sorted)))]


out["C_perltqa_text"] = {"n_arch": narch, "n_docs": ndocs,
    "doc_mean_tok": round(sum(dlens) / len(dlens), 1), "doc_median_tok": pct(0.5),
    "doc_p10_tok": pct(0.10), "doc_p90_tok": pct(0.90), "vocab": len(vcb),
    "sample_texts": [t for _, t in items[list(items.keys())[0]]["items"][:6]],
    "compare_realtalk": {"doc_mean_tok": 21.2, "doc_median_tok": 14,
                         "query_mean_tok": 9.1, "vocab_per_archive": "2006-2816"}}

json.dump(out, open(OUT, "w"), indent=1)
print(json.dumps(out, indent=1)[:4000])
