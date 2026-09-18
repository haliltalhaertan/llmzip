"""Own audit: Claim 5b — standardized-float reference (hr-branch challenge).

The hr/standardized-float-correction branch records that SIGN96 loses to a
sigma-STANDARDIZED float. This script tests that on the LADDER (RealTalk) pipeline
with own code, read-only C/QC caches, exact n=705 cohort.
Arms: sym_dot, float_cos (LADDER float), float_dot, float_std_cos, float_std_dot,
qscale. sigma = docs-only std, floor 1e-12 (published contract).
"""
import json, pickle
import numpy as np
from sklearn.preprocessing import normalize as N

CACHE = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_repr"
EXCL = set(json.load(open(
    "/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/data/exclusions.json",
    encoding="utf-8"))["excluded_qids"])
ARCH = [f"RT{i:02d}" for i in range(1, 11)]

def hits(S, golds):
    o = np.argsort(-S, kind="stable", axis=1)[:, :10]
    return float(np.mean([1.0 if (set(g) & set(r.tolist())) else 0.0
                          for g, r in zip(golds, o)])) * 100

tot = 0; acc = {}
for aid in ARCH:
    d = pickle.load(open(f"{CACHE}/{aid}.pkl", "rb"))
    C = np.asarray(d["C"], float); QC = np.asarray(d["QC"], float)
    keep = [k for k, q in enumerate(d["qids"]) if q not in EXCL]
    QC = QC[keep, :]; golds = [list(d["gold_rows"][k]) for k in keep]; n = len(keep)
    B = np.where(C >= 0, 1.0, -1.0); QB = np.where(QC >= 0, 1.0, -1.0)
    sig = C.std(axis=0, ddof=0); sig[sig < 1e-12] = 1e-12
    arms = {"sym_dot": QB @ B.T, "float_cos": N(QC) @ N(C).T, "float_dot": QC @ C.T,
            "float_std_cos": N(QC / sig) @ N(C / sig).T,
            "float_std_dot": (QC / sig) @ (C / sig).T,
            "qscale": (QC / sig) @ B.T}
    for k, S in arms.items():
        acc.setdefault(k, []).append((hits(S, golds), n))
    tot += n
print(f"n={tot}")
for k, v in acc.items():
    print(f"  {k:14s} Hit@10={sum(x * n for x, n in v) / tot:6.2f}")
print("REFERENCE: REPORT.md round table lists float_std(96d, uncompressed)=48.51; "
      "hr branch: SIGN96 behind standardized float (-1.83 RealTalk Hit@10).")
