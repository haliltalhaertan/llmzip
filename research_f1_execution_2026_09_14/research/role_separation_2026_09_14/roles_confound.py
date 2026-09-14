#!/usr/bin/env python3
# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""
roles_confound.py -- The LME within-benchmark contrast (close-neighbour golds show delta
-11.15 pp lower) is the ONE result favouring the near-duplicate hypothesis. Before accepting it,
test the obvious confound: archive size N. Larger archives => more rows => smaller min-distance to
SOME non-gold row (order statistic), AND larger archives are harder for BOTH arms.
Also decompose the effect into the sign arm and the float arm separately.
"""
import json, pickle, glob, os
import numpy as np

BASE = "/mnt/c/Users/MDP/dev/llmzip-work"
EV = BASE + "/agent_out/role-separation/evidence"
rng = np.random.default_rng(4242)
RES = json.load(open(EV + "/results.json"))


def jd(o):
    def c(x):
        if isinstance(x, np.floating): return float(x)
        if isinstance(x, np.integer): return int(x)
        if isinstance(x, np.ndarray): return x.tolist()
        if isinstance(x, np.bool_): return bool(x)
        raise TypeError(str(type(x)))
    return json.dumps(o, indent=2, default=c)


def fr3(s, gold, K=3):
    s = np.asarray(s, np.float64); gold = np.asarray(gold, np.int64)
    if gold.size == 0 or s.size == 0: return float("nan")
    if s.size <= K: return 1.0
    thr = np.partition(s, -K)[-K]
    st = int((s > thr).sum()); slots = K - st; bc = int((s == thr).sum())
    gs = s[gold]; g1 = int((gs > thr).sum()); g2 = int((gs == thr).sum())
    return (g1 + g2 * slots / bc) / gold.size if bc else g1 / gold.size


def bits(C): return np.where(C >= 0, 1, -1).astype(np.int16)
def hq(B, q): return ((96 - (B @ np.where(q >= 0, 1, -1).astype(np.int16))) // 2).astype(np.float64)
def cq(C, q):
    d = np.linalg.norm(C, axis=1) * np.linalg.norm(q); d[d == 0] = 1e-300
    return (C @ q) / d


rows = []
for cp in sorted(glob.glob(BASE + "/regen/lme/cache_repr/*.pkl")):
    P = pickle.load(open(cp, "rb"))
    C = P["C"]; N = C.shape[0]; B = bits(C)
    gold = np.asarray(P["gold"]).ravel().astype(int)
    a = fr3(-hq(B, P["qC"]), gold); b = fr3(cq(C, P["qC"]), gold)
    mask = np.ones(N, bool); mask[gold] = False
    if mask.sum() == 0: continue
    Hg = ((96 - (B[gold] @ B.T)) // 2).astype(float)
    dnn = int(Hg[:, mask].min())
    rows.append(dict(d=a - b, s=a, f=b, dnn=dnn, N=N, ng=gold.size))

d = np.array([r["d"] for r in rows]); s = np.array([r["s"] for r in rows])
f = np.array([r["f"] for r in rows]); x = np.array([r["dnn"] for r in rows], float)
Nv = np.array([r["N"] for r in rows], float)
med = np.median(x); close = x <= med

K = {}
K["K0_raw"] = {
    "n": int(d.size), "dnn_median": float(med),
    "delta_close_pp": float(d[close].mean() * 100), "delta_far_pp": float(d[~close].mean() * 100),
    "effect_pp": float((d[close].mean() - d[~close].mean()) * 100),
    "sign_close": float(s[close].mean()), "sign_far": float(s[~close].mean()),
    "float_close": float(f[close].mean()), "float_far": float(f[~close].mean()),
    "sign_arm_close_minus_far_pp": float((s[close].mean() - s[~close].mean()) * 100),
    "float_arm_close_minus_far_pp": float((f[close].mean() - f[~close].mean()) * 100),
}
K["K1_confound_N"] = {
    "corr_dnn_vs_N": float(np.corrcoef(x, Nv)[0, 1]),
    "corr_dnn_vs_logN": float(np.corrcoef(x, np.log(Nv))[0, 1]),
    "corr_delta_vs_logN": float(np.corrcoef(d, np.log(Nv))[0, 1]),
    "mean_N_close": float(Nv[close].mean()), "mean_N_far": float(Nv[~close].mean()),
    "note": "If dnn is mostly an order statistic of N, the 'close neighbour' group is just big archives.",
}

# Stratify by archive size quartile, recompute effect WITHIN each stratum
qs = np.percentile(Nv, [25, 50, 75])
strat = np.digitize(Nv, qs)
within = []
for g in range(4):
    m = strat == g
    if m.sum() < 20: continue
    xm = x[m]; mm = xm <= np.median(xm)
    if mm.sum() == 0 or (~mm).sum() == 0: continue
    within.append({"stratum": int(g), "n": int(m.sum()),
                   "N_range": [float(Nv[m].min()), float(Nv[m].max())],
                   "effect_pp": float((d[m][mm].mean() - d[m][~mm].mean()) * 100),
                   "sign_arm_pp": float((s[m][mm].mean() - s[m][~mm].mean()) * 100),
                   "float_arm_pp": float((f[m][mm].mean() - f[m][~mm].mean()) * 100)})
K["K2_within_size_stratum"] = within
K["K2_pooled_within_stratum_effect_pp"] = float(np.mean([w["effect_pp"] for w in within])) if within else None

# residualise dnn on log N, then correlate with delta
A_ = np.vstack([np.log(Nv), np.ones_like(Nv)]).T
beta, *_ = np.linalg.lstsq(A_, x, rcond=None)
xr = x - A_ @ beta
bd, *_ = np.linalg.lstsq(A_, d, rcond=None)
dr = d - A_ @ bd
K["K3_residualised_on_logN"] = {
    "pearson_r_resid": float(np.corrcoef(xr, dr)[0, 1]),
    "slope_pp_per_bit": float(np.polyfit(xr, dr, 1)[0] * 100),
    "raw_pearson_r": float(np.corrcoef(x, d)[0, 1]),
    "raw_slope_pp_per_bit": float(np.polyfit(x, d, 1)[0] * 100),
}
# bootstrap the residualised slope
bs = []
n = d.size
for _ in range(3000):
    i = rng.integers(0, n, n)
    if np.std(xr[i]) > 0: bs.append(np.polyfit(xr[i], dr[i], 1)[0] * 100)
K["K3_residualised_on_logN"]["slope_CI95"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]

print(jd(K))
RES["K_LME_confound_analysis"] = K
open(EV + "/results.json", "w").write(jd(RES))
print("[SAVED]")
