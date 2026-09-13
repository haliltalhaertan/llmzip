#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT] BENCH-3A STEP 2 — REALTALK measurements.

Frozen eval semantics (deney1_lme/loco + race_sign.py R2C conventions):
- K=3, NT=20 trials, priorities default_rng(5_100_000 + ci*100_000 + t*100 + 99)
  with ci = 0-based chat ordinal in lexical file order (LoCoMo: conv ordinal).
- Native SIGN96: Hamming distance on sign(C)/sign(qC), rank lexsort((p, d)).
- float96 (T4C2 mirror): cosine_centered(C,qC), rank lexsort((p, -scores float64)).
- Ladder arms per width k in (80,64,48), per-archive variance subsets
  (R2C per_archive_subsets: order_desc=argsort(var,stable)[::-1];
  TOP=first k, BOT=last k, SPREAD=order_desc[floor(linspace(0,95,k)+0.5)]);
  RANDOMx10 = benchmark-global draws, seeds 93000+10*width_idx+j
  (width_idx {48:0,64:1,80:2}, RACE-2 panel formula; deney1's 91000+split*10+j
  needs train/test splits which do not exist here).
- Metric: fractional R@3 per QA per trial, mean over trials; invalid QAs
  (0 resolved gold) recorded with FR=null and EXCLUDED from means
  (frozen LoCoMo denominator rule).

Writes /tmp/b3a/details.json (per-QA FRs per arm) + /tmp/b3a/rt_summary.json.
"""
import hashlib
import json
import os
import pickle
import re
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np

OUTDIR = Path("/tmp/b3a")
REPRDIR = OUTDIR / "rt_repr"
K = 3
NT = 20
WIDTHS = (80, 64, 48)
WIDTH_IDX = {48: 0, 64: 1, 80: 2}
RAND_BASE = 93000
N_RAND = 10
TOK = re.compile(r"D\d+:\d+")


def tie_seed(ci, t):
    return 5_100_000 + ci * 100_000 + t * 100 + 99


def cosine_centered(C, q):
    C = np.asarray(C, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64).reshape(-1)
    dn = np.linalg.norm(C, axis=1)
    qn = float(np.linalg.norm(q))
    if qn <= 0 or np.any(dn <= 0):
        raise RuntimeError("[BUG] zero centered vector norm in cosine")
    return (C @ q) / (dn * qn)


def rank_hamming(dist, p):
    return np.lexsort((p, np.asarray(dist)))


def rank_float(scores, p):
    return np.lexsort((p, -np.asarray(scores, dtype=np.float64)))


def frac_r3(order, gold):
    gset = set(map(int, gold))
    return len(set(map(int, order[:K])) & gset) / len(gset)


def linspace_positions(k, dim=96):
    return np.floor(np.linspace(0, dim - 1, k) + 0.5).astype(int)


def per_archive_subsets(var, k, dim=96):
    var = np.asarray(var, dtype=float)
    assert var.shape == (dim,)
    order_desc = np.argsort(var, kind="stable")[::-1]
    parts = {"TOP": order_desc[:k], "BOT": order_desc[-k:],
             "SPREAD": order_desc[linspace_positions(k, dim)]}
    return {n: np.sort(s) for n, s in parts.items()}


def random_subset(seed, k, dim=96):
    return np.sort(np.random.default_rng(seed).choice(dim, k, replace=False))


def main():
    pkls = sorted(REPRDIR.glob("RT*.pkl"))
    assert len(pkls) == 10, len(pkls)
    arm_names = (["NATIVE96", "FLOAT96"]
                 + [f"{fam}{k}" for k in WIDTHS for fam in ("SPREAD", "TOP", "BOT")]
                 + [f"RAND{k}_s{j}" for k in WIDTHS for j in range(N_RAND)])
    rand_subs = {(k, j): random_subset(RAND_BASE + 10 * WIDTH_IDX[k] + j, k)
                 for k in WIDTHS for j in range(N_RAND)}
    per_qa, validabile = [], []
    for ci, p in enumerate(pkls):
        o = pickle.loads(p.read_bytes())
        C = np.asarray(o["C"], float)
        QC = np.asarray(o["QC"], float)
        n = C.shape[0]
        assert C.shape[1] == 96 and QC.shape[1] == 96
        D0 = C >= 0
        var = C.var(axis=0)
        subs = {k: per_archive_subsets(var, k) for k in WIDTHS}
        pris = [np.random.default_rng(tie_seed(ci, t)).random(n) for t in range(NT)]
        for qi, qid in enumerate(o["qids"]):
            gold = [int(g) for g in o["gold_rows"][qi]]
            cat = int(o["cats"][qi])
            rec = {"qid": qid, "chat": o["chat_no"], "file": o["file"], "cat": cat,
                   "N": n, "gold_count": len(gold),
                   "valid": int(len(gold) > 0), "arms": {}, "tie": {}}
            if not gold:
                for a in arm_names:
                    rec["arms"][a] = None
                rec["tie"] = {"boundary_tie": None, "tail_gap": None, "d3": None, "d4": None}
                per_qa.append(rec)
                continue
            q = QC[qi]
            Q0 = q >= 0
            dnat = np.count_nonzero(D0 != Q0[None, :], axis=1)
            sscores = cosine_centered(C, q)
            dists = {"NATIVE96": dnat}
            for k in WIDTHS:
                for fam in ("SPREAD", "TOP", "BOT"):
                    sub = subs[k][fam]
                    dists[f"{fam}{k}"] = np.count_nonzero(
                        D0[:, sub] != Q0[sub][None, :], axis=1)
                for j in range(N_RAND):
                    sub = rand_subs[(k, j)]
                    dists[f"RAND{k}_s{j}"] = np.count_nonzero(
                        D0[:, sub] != Q0[sub][None, :], axis=1)
            for a in arm_names:
                if a == "FLOAT96":
                    tot = sum(frac_r3(rank_float(sscores, p), gold) for p in pris) / NT
                else:
                    tot = sum(frac_r3(rank_hamming(dists[a], p), gold) for p in pris) / NT
                rec["arms"][a] = float(tot)
            sd = np.sort(dnat)
            d3, d4 = int(sd[K - 1]), int(sd[K])
            rec["tie"] = {"boundary_tie": int(d3 == d4), "tail_gap": int(d4 - d3),
                          "d3": d3, "d4": d4}
            per_qa.append(rec)
            validabile.append(rec)
        print(f"chat {o['chat_no']:02d}: {len(o['qids'])} qa done", flush=True)

    details = {"label": "[LOCAL EXPLORATORY PILOT]",
               "protocol": "K=3, NT=20, tie_seed=5_100_000+ci*100_000+t*100+99 (ci=0-based chat ordinal); "
                           "sign Hamming lexsort((p,d)); float cosine lexsort((p,-s)); "
                           "SPREAD/TOP/BOT per-archive variance; RAND global 93000-series",
               "n_qa": len(per_qa), "n_valid": len(validabile),
               "per_qa": per_qa}
    (OUTDIR / "details.json").write_text(json.dumps(details))

    def mean(vals):
        a = np.asarray([v for v in vals if v is not None], float)
        return float(a.mean()) if len(a) else None

    valid = [r for r in per_qa if r["valid"]]
    summ = {"label": "[LOCAL EXPLORATORY PILOT]", "n_qa": len(per_qa),
            "n_valid": len(valid),
            "arm_means": {a: mean([r["arms"][a] for r in valid]) for a in arm_names}}
    # per-category means: native/float + best-64 ladder arm
    ladder64 = [a for a in arm_names if a.endswith("64") and a not in ("NATIVE96", "FLOAT96")]
    best64 = max(ladder64, key=lambda a: summ["arm_means"][a])
    summ["best_ladder_64"] = best64
    summ["per_category"] = {}
    for c in (1, 2, 3):
        rows = [r for r in valid if r["cat"] == c]
        summ["per_category"][str(c)] = {
            "n": len(rows),
            "NATIVE96": mean([r["arms"]["NATIVE96"] for r in rows]),
            "FLOAT96": mean([r["arms"]["FLOAT96"] for r in rows]),
            best64: mean([r["arms"][best64] for r in rows])}
    # random-arm LoCoMo-style summary: mean over seeds of per-QA means == mean of seed means
    for k in WIDTHS:
        seeds = [f"RAND{k}_s{j}" for j in range(N_RAND)]
        summ["arm_means"][f"RAND{k}_MEAN"] = float(np.mean([summ["arm_means"][s] for s in seeds]))
        summ["arm_means"][f"RAND{k}_MIN"] = float(min(summ["arm_means"][s] for s in seeds))
        summ["arm_means"][f"RAND{k}_MAX"] = float(max(summ["arm_means"][s] for s in seeds))
    # tie diagnostics (native code, valid QAs)
    bt = [r["tie"]["boundary_tie"] for r in valid]
    tg = [r["tie"]["tail_gap"] for r in valid]
    summ["tie"] = {"n": len(valid),
                   "boundary_tie_share": float(np.mean(bt)),
                   "boundary_tie_count": int(np.sum(bt)),
                   "mean_tail_gap": float(np.mean(tg))}
    (OUTDIR / "rt_summary.json").write_text(json.dumps(summ, indent=2))
    print(json.dumps({k: v for k, v in summ.items() if k != "per_category"}, indent=2))
    print("best64 =", best64)
    print("wrote /tmp/b3a/details.json and /tmp/b3a/rt_summary.json")


if __name__ == "__main__":
    main()
