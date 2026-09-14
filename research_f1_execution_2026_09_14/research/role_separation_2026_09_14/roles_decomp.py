#!/usr/bin/env python3
# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""
roles_decomp.py -- The LME close-neighbour effect (-11.15 pp) is real and survives archive size.
DECISIVE QUESTION: is it caused by *conversational adjacency* near-duplicates (the "both speakers
indexed" story), or by GENERIC gold-neighbourhood density that has nothing to do with roles?

Three discriminating tests:
 L1. Within the close-neighbour group, split by whether the nearest non-gold neighbour is an
     ADJACENT turn. The role story predicts adjacency carries the damage.
 L2. Replace Hamming-dnn with COSINE-dnn (float-space proximity). If the effect is equally strong
     with cosine-dnn, it is generic proximity, NOT sign-quantization-specific.
 L3. Does dnn predict the FLOAT arm too? A quantization-specific effect must hit sign only.
     Also: is dnn just a proxy for "gold is not distinctive" (gold's own query distance)?
"""
import json, pickle, glob, os
import numpy as np

BASE = "/mnt/c/Users/MDP/dev/llmzip-work"
EV = BASE + "/agent_out/role-separation/evidence"
rng = np.random.default_rng(9090)
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


R = []
for cp in sorted(glob.glob(BASE + "/regen/lme/cache_repr/*.pkl")):
    qid = os.path.basename(cp)[:-4]
    d = json.load(open(BASE + "/regen/lme/items/" + qid + ".json"))
    sess = []
    for si, sx in enumerate(d["haystack_sessions"]):
        if isinstance(sx, list):
            for t in sx:
                if isinstance(t, dict): sess.append(si)
    sess = np.array(sess)
    P = pickle.load(open(cp, "rb"))
    C = P["C"]; N = C.shape[0]; B = bits(C); qC = P["qC"]
    gold = np.asarray(P["gold"]).ravel().astype(int)
    hq = ((96 - (B @ np.where(qC >= 0, 1, -1).astype(np.int16))) // 2).astype(float)
    nrm = np.linalg.norm(C, axis=1) * np.linalg.norm(qC); nrm[nrm == 0] = 1e-300
    cqv = (C @ qC) / nrm
    a = fr3(-hq, gold); b = fr3(cqv, gold)
    mask = np.ones(N, bool); mask[gold] = False
    if mask.sum() == 0: continue
    Hg = ((96 - (B[gold] @ B.T)) // 2).astype(float); Hg[:, ~mask] = 1e9
    gi, ni = np.unravel_index(np.argmin(Hg), Hg.shape)
    dnn_h = float(Hg[gi, ni]); grow = int(gold[gi]); nrow = int(ni)
    nn_adj = bool(abs(nrow - grow) == 1 and sess[nrow] == sess[grow])
    # cosine dnn
    U = C / np.maximum(np.linalg.norm(C, axis=1, keepdims=True), 1e-300)
    Sg = U[gold] @ U.T; Sg[:, ~mask] = -1e9
    dnn_c = float(Sg.max())
    R.append(dict(d=a - b, s=a, f=b, dh=dnn_h, dc=dnn_c, adj=nn_adj, N=N,
                  gq_h=float(hq[gold].min()), gq_c=float(cqv[gold].max())))

d = np.array([r["d"] for r in R]); s = np.array([r["s"] for r in R]); f = np.array([r["f"] for r in R])
dh = np.array([r["dh"] for r in R]); dc = np.array([r["dc"] for r in R])
adj = np.array([r["adj"] for r in R], bool)
gq_h = np.array([r["gq_h"] for r in R]); gq_c = np.array([r["gq_c"] for r in R])
close = dh <= np.median(dh)

L = {}


def boot(mask_a, mask_b, vals, n=3000):
    out = []
    idx = np.arange(vals.size)
    for _ in range(n):
        i = rng.integers(0, vals.size, vals.size)
        A, Bm = mask_a[i], mask_b[i]
        if A.any() and Bm.any(): out.append((vals[i][A].mean() - vals[i][Bm].mean()) * 100)
    return [float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))] if out else None


# L1: within the CLOSE group, does adjacency matter?
ca, cn = close & adj, close & ~adj
L["L1_adjacency_within_close_group"] = {
    "n_close_and_nn_adjacent": int(ca.sum()), "n_close_and_nn_NOT_adjacent": int(cn.sum()),
    "delta_close_adj_pp": float(d[ca].mean() * 100), "delta_close_nonadj_pp": float(d[cn].mean() * 100),
    "effect_adj_minus_nonadj_pp": float((d[ca].mean() - d[cn].mean()) * 100),
    "CI95": boot(ca, cn, d),
    "interpretation": ("The 'both speakers indexed' story requires adjacency to carry the damage. "
                       "If this is ~0, the damage is generic proximity, not role pairing."),
}
# also overall adjacency effect on delta
L["L1b_adjacency_overall"] = {
    "n_adj": int(adj.sum()), "n_nonadj": int((~adj).sum()),
    "delta_adj_pp": float(d[adj].mean() * 100), "delta_nonadj_pp": float(d[~adj].mean() * 100),
    "effect_pp": float((d[adj].mean() - d[~adj].mean()) * 100),
    "CI95": boot(adj, ~adj, d),
    "mean_dnn_h_when_adj": float(dh[adj].mean()), "mean_dnn_h_when_nonadj": float(dh[~adj].mean()),
}

# L2: cosine-dnn vs hamming-dnn as predictors
closec = dc >= np.median(dc)   # high cosine similarity = close
L["L2_cosine_dnn_vs_hamming_dnn"] = {
    "corr_hamming_dnn_vs_cosine_dnn": float(np.corrcoef(dh, dc)[0, 1]),
    "effect_using_HAMMING_dnn_pp": float((d[close].mean() - d[~close].mean()) * 100),
    "effect_using_COSINE_dnn_pp": float((d[closec].mean() - d[~closec].mean()) * 100),
    "CI95_cosine": boot(closec, ~closec, d),
    "interpretation": ("If cosine-dnn produces the same effect, gold-neighbourhood density is a "
                       "property of the FLOAT geometry, not of sign quantization."),
}

# L3: arm decomposition + distinctiveness confound
L["L3_arm_decomposition"] = {
    "sign_arm_close_minus_far_pp": float((s[close].mean() - s[~close].mean()) * 100),
    "float_arm_close_minus_far_pp": float((f[close].mean() - f[~close].mean()) * 100),
    "sign_CI95": boot(close, ~close, s), "float_CI95": boot(close, ~close, f),
    "corr_dnn_h_vs_gold_query_hamming": float(np.corrcoef(dh, gq_h)[0, 1]),
    "corr_dnn_h_vs_gold_query_cosine": float(np.corrcoef(dh, gq_c)[0, 1]),
    "note": ("gq_h = gold row's own Hamming distance to the query. If dnn correlates with it, "
             "'close neighbour' is partly just 'gold sits in a generic/undistinctive region'."),
}
# residualise dnn on gold-query distance, re-test
A_ = np.vstack([gq_h, np.ones_like(gq_h)]).T
beta, *_ = np.linalg.lstsq(A_, dh, rcond=None); dhr = dh - A_ @ beta
bd, *_ = np.linalg.lstsq(A_, d, rcond=None); dr = d - A_ @ bd
L["L3_residualised_on_gold_query_distance"] = {
    "raw_r": float(np.corrcoef(dh, d)[0, 1]),
    "resid_r": float(np.corrcoef(dhr, dr)[0, 1]),
    "resid_slope_pp_per_bit": float(np.polyfit(dhr, dr, 1)[0] * 100),
    "raw_slope_pp_per_bit": float(np.polyfit(dh, d, 1)[0] * 100),
}
print(jd(L))
RES["L_LME_decomposition"] = L
open(EV + "/results.json", "w").write(jd(RES))
print("[SAVED]")
