#!/usr/bin/env python3
# Coordinator check of audit findings F-6 and F-2 against my own published claims.
import pickle, glob, json
import numpy as np
from math import comb

ROOT = "/mnt/c/Users/MDP/dev/llmzip-work"
K = 3


def efr(sc, gold, K=3):
    s = np.asarray(sc, float)
    ss = np.sort(s)[::-1]
    thr = ss[K - 1]
    strictly = int((s > thr).sum())
    slots = K - strictly
    bc = int((s == thr).sum())
    g_s = sum(1 for x in gold if s[x] > thr)
    g_t = sum(1 for x in gold if s[x] == thr)
    return (g_s + g_t * (slots / bc)) / len(gold)


def all3(sc, gold, K=3):
    s = np.asarray(sc, float)
    ss = np.sort(s)[::-1]
    thr = ss[K - 1]
    strictly = int((s > thr).sum())
    slots = K - strictly
    bc = int((s == thr).sum())
    g_s = sum(1 for x in gold if s[x] > thr)
    g_t = sum(1 for x in gold if s[x] == thr)
    if len(gold) - g_s - g_t > 0:
        return 0.0
    if g_t == 0:
        return 1.0
    if g_t > slots:
        return 0.0
    return comb(bc - g_t, slots - g_t) / comb(bc, slots)


def arms(C, q, recenter):
    """recenter=False -> frozen (C already centered). recenter=True -> my E1 error."""
    if recenter:
        mu = C.mean(axis=0)
        C = C - mu
        q = q - mu
    D0 = C >= 0
    Q0 = q >= 0
    dh = (D0 != Q0[None, :]).sum(axis=1).astype(float)
    cs = (C @ q) / (np.linalg.norm(C, axis=1) * np.linalg.norm(q))
    return -dh, cs


# LongMemEval, four combinations: {FR@3, ALL@3} x {no re-center, re-center}
data = []
for f in sorted(glob.glob(f"{ROOT}/regen/lme/cache_repr/*.pkl")):
    d = pickle.load(open(f, "rb"))
    g = [int(x) for x in np.atleast_1d(d["gold"])]
    if g:
        data.append((np.asarray(d["C"], float), np.asarray(d["qC"], float), g))

res = {}
for metric_name, metric in (("FR@3", efr), ("ALL@3", all3)):
    for rc in (False, True):
        s = f = 0.0
        for C, q, g in data:
            dh, cs = arms(C, q, rc)
            s += metric(dh, g)
            f += metric(cs, g)
        n = len(data)
        res[f"{metric_name}_recenter={rc}"] = {"sign": s / n, "float": f / n,
                                               "delta_pp": 100 * (s - f) / n}

print("=== F-6 CHECK: isolate each of my two errata errors (LongMemEval) ===")
for k, v in res.items():
    print(f"  {k:22s} delta_pp = {v['delta_pp']:+.6f}")
base = res["FR@3_recenter=False"]["delta_pp"]
print(f"\n  correct (FR@3, no re-center)        : {base:+.6f}")
print(f"  effect of E1 (re-centering) ALONE   : {res['FR@3_recenter=True']['delta_pp'] - base:+.6f} pp")
print(f"  effect of E2 (ALL@3) ALONE          : {res['ALL@3_recenter=False']['delta_pp'] - base:+.6f} pp")
print(f"  both together                       : {res['ALL@3_recenter=True']['delta_pp'] - base:+.6f} pp")
print(f"  my published wrong number was       : +9.677305 (diff from ALL@3+recenter: "
      f"{res['ALL@3_recenter=True']['delta_pp'] - 9.677305:+.6f})")

# F-2: the contract's 1e-12 headline gate against frozen references
print("\n=== F-2 CHECK: contract headline gate at 1e-12 vs frozen references ===")
FROZEN = {"LME": (0.5419751773049645, 0.4415957446808511)}
mine = (res["FR@3_recenter=False"]["sign"], res["FR@3_recenter=False"]["float"])
fs, ff = FROZEN["LME"]
print(f"  LME sign : mine={mine[0]!r} frozen={fs!r} diff={mine[0]-fs:+.3e} "
      f"{'PASS' if abs(mine[0]-fs) <= 1e-12 else 'FAIL'}")
print(f"  LME float: mine={mine[1]!r} frozen={ff!r} diff={mine[1]-ff:+.3e} "
      f"{'PASS' if abs(mine[1]-ff) <= 1e-12 else 'FAIL'}")
print("  -> the float arm is EXACT (no tie-break randomness); the sign arm differs")
print("     because the frozen reference averages NT=20 sampled permutations.")

json.dump(res, open(f"{ROOT}/coord_errata_check.json", "w"), indent=1)
