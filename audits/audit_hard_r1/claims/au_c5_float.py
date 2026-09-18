"""Own audit: Claim 5 — sign() vs float source (~10pp gap), scorer-confound check.

Key math (own derivation): all +/-1 sign rows have identical L2 norm sqrt(k), so
for sym arms dot-product and cosine rankings are IDENTICAL. For float arms they
differ. Published comparison is sym-DOT vs float-COSINE -> confounds quantization
with scorer. The fair same-scorer check is float-DOT vs sym-DOT, runnable on the
read-only cached (C, QC) with own code.

Also verifies the LADDER.json float arms 36.60/40.43/43.69 arithmetically.
NOTE: LADDER k=192/384 arms need C at those widths — NOT in rt_repr cache
(k=96 only). So: (a) verify k=96 trio exactly; (b) run the scorer-confound test
at k=96 (where all inputs exist); (c) k=192/384 gaps verified as JSON arithmetic.
"""
import json, pickle
import numpy as np
from sklearn.preprocessing import normalize as _norm

PUB = "/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10/research_top10_comparison_2026_09_16"
CACHE = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_repr"
ARCH = [f"RT{i:02d}" for i in range(1, 11)]
EXCL = set(json.load(open(
    "/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/data/exclusions.json",
    encoding="utf-8"))["excluded_qids"])

def top10_hit(scores, gold_list):
    order = np.argsort(-scores, kind="stable")[:10]
    return 1.0 if (set(gold_list) & set(order.tolist())) else 0.0

def hits(S, golds):
    return float(np.mean([top10_hit(S[j], golds[j]) for j in range(len(golds))])) * 100

acc = {k: [] for k in ("sym_dot", "float_cos", "float_dot", "qscale")}
nq = {}
for aid in ARCH:
    d = pickle.load(open(f"{CACHE}/{aid}.pkl", "rb"))
    C = np.asarray(d["C"], float); QC = np.asarray(d["QC"], float)
    keep = [i for i, q in enumerate(d["qids"]) if q not in EXCL]
    QC = QC[keep, :]; golds = [list(d["gold_rows"][i]) for i in keep]
    nq[aid] = len(keep)
    B = np.where(C >= 0, 1.0, -1.0); QB = np.where(QC >= 0, 1.0, -1.0)
    acc["sym_dot"].append((hits(QB @ B.T, golds), len(keep)))
    acc["float_cos"].append((hits(_norm(QC) @ _norm(C).T, golds), len(keep)))
    acc["float_dot"].append((hits(QC @ C.T, golds), len(keep)))
    sig = C.std(axis=0, ddof=0); sig[sig < 1e-12] = 1e-12
    acc["qscale"].append((hits((QC / sig) @ B.T, golds), len(keep)))

N = sum(nq.values())
def agg(k):
    return sum(v * n for v, n in acc[k]) / N
print(f"n={N} (exact LADDER cohort)")
res = {k: agg(k) for k in acc}
for k, v in res.items():
    print(f"  k96/{k:10s} Hit@10={v:6.2f}")
LAD = json.load(open(f"{PUB}/coordinator/LADDER.json"))["arms"]
print("LADDER.json anchors: sym=46.52 float=36.60 | mine: "
      f"sym={res['sym_dot']:.2f} float_cos={res['float_cos']:.2f}")
print(f"\nPublished gap (sym_dot - float_cos) = {res['sym_dot']-res['float_cos']:+.2f} "
      f"(LADDER k96: {LAD['k96/sym']['hit10']-LAD['k96/float']['hit10']:+.2f})")
print(f"Same-scorer gap (sym_dot - float_dot) = {res['sym_dot']-res['float_dot']:+.2f}")
print(f"Float scorer effect (float_dot - float_cos) = {res['float_dot']-res['float_cos']:+.2f}")
print("\nLADDER.json higher-k gaps (JSON arithmetic): "
      f"k192 {LAD['k192/sym']['hit10']-LAD['k192/float']['hit10']:+.2f}, "
      f"k384 {LAD['k384/sym']['hit10']-LAD['k384/float']['hit10']:+.2f}")
print("If float_dot closes the gap, the ~10pp is a SCORER artifact, not sign magic.")
