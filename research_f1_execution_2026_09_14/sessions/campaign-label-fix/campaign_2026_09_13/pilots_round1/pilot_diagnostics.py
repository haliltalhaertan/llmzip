"""Pilot diagnostics: WHY does the top-variance axis subset underperform random subsets?

Loads the 470 pkls + the pilot's per-axis matrices and, for axis-sets
(TOP48/TOP16 by variance, RAND48/RAND16 seeds, BOT48/BOT16), computes per question:
  - delta_sum      : sum of per-axis gold-discrimination delta (from pilot matrices)
  - dup_frac       : duplicate 48/16-bit code fraction of the archive under the set
  - tie_rate       : top-3 boundary tie indicator (candidates at boundary > slots)
  - mean_abs_phi   : mean pairwise |phi| (sign correlation) between axes of the set
  - dist_std       : std of query->doc Hamming distances (spread)
  - gold_dist_gap  : mean distance(gold) - mean distance(non-gold)  [separation]
LOCAL EXPLORATORY PILOT — NOT PREREGISTERED — NOT FOR CITATION.
"""
import json
import pickle
from pathlib import Path

import numpy as np

WORK = Path(r"C:/Users/MDP/dev/llmzip-work")
PIL = WORK / "pilots" / "axis_attack_2026-09-12"
PKL_DIR = WORK / "regen" / "lme" / "cache_repr"
K = 3

d_pilot = json.loads((PIL / "pilot_results.json").read_text())
npz = np.load(PIL / "per_axis_matrices.npz", allow_pickle=False)
delta_mat = npz["delta"]                      # (470, 96)
qids = [str(q) for q in npz["qids"]]

sets = {}
for k in (16, 48):
    sets[f"TOP{k}"] = ("desc", k, None)
    sets[f"BOT{k}"] = ("asc", k, None)
    for s in range(3):
        sets[f"RAND{k}_s{s}"] = ("rand", k, s)

def set_idx(mode, k, s, var):
    if mode == "desc":
        return np.argsort(var, kind="stable")[::-1][:k]
    if mode == "asc":
        return np.argsort(var, kind="stable")[:k]
    return np.random.default_rng(12000 + s).choice(96, k, replace=False)

acc = {name: {kk: [] for kk in ("delta_sum", "dup_frac", "tie_rate", "mean_abs_phi", "dist_std", "gold_gap")}
       for name in sets}
pkls = sorted(PKL_DIR.glob("*.pkl"))
assert len(pkls) == 470

for qi, p in enumerate(pkls):
    with open(p, "rb") as f:
        o = pickle.loads(f.read())
    qid = o["question_id"]
    assert qid == qids[qi], (qid, qids[qi])
    C = o["C"]; qC = o["qC"]; g = np.asarray(o["gold"]).ravel()
    n = len(C)
    D0 = C >= 0; Q0 = qC >= 0
    var = C.var(axis=0)
    gm = np.zeros(n, dtype=bool); gm[g] = True

    for name, (mode, k, s) in sets.items():
        idx = set_idx(mode, k, s, var)
        Dk = D0[:, idx]; Qk = Q0[idx]
        d = np.count_nonzero(Dk != Qk[None, :], axis=1)
        # duplicate code fraction
        pk = np.packbits(Dk, axis=1, bitorder="big")
        uniq = len(np.unique(pk, axis=0))
        # top-3 boundary tie
        srt = np.sort(d); d3 = int(srt[K - 1]); lt = int(np.sum(d < d3)); bc = int(np.sum(d == d3))
        tie = 1.0 if bc > (K - lt) else 0.0
        # mean |phi| between axes of the set (sign correlation over docs)
        X = Dk.astype(np.float64)
        X = X - X.mean(axis=0)
        sd = X.std(axis=0)
        keep = sd > 0
        Xs = X[:, keep] / sd[keep]
        if Xs.shape[1] >= 2:
            phi = (Xs.T @ Xs) / n
            iu = np.triu_indices(Xs.shape[1], k=1)
            mphi = float(np.abs(phi[iu]).mean())
        else:
            mphi = float("nan")
        a = acc[name]
        a["delta_sum"].append(float(delta_mat[qi, idx].sum()))
        a["dup_frac"].append(1.0 - uniq / n)
        a["tie_rate"].append(tie)
        a["mean_abs_phi"].append(mphi)
        a["dist_std"].append(float(d.std()))
        a["gold_gap"].append(float(d[gm].mean() - d[~gm].mean()))
    if (qi + 1) % 100 == 0:
        print(f"  {qi+1}/470", flush=True)

out = {name: {kk: float(np.mean(vv)) for kk, vv in a.items()} for name, a in acc.items()}
(PIL / "diagnostics.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(json.dumps(out, indent=2))
