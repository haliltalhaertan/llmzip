#!/usr/bin/env python3
# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# Coordinator verification of six relayed ideas, computed first-hand from unsealed E1 LME caches.
# NOT the preregistered Task4F1 scale experiment. Pooled-archive probe only.
import pickle, glob, json, random, math
from math import comb
import numpy as np

ROOT = "/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr"
K = 3
rng = np.random.default_rng(20260914)
out = {}

files = sorted(glob.glob(ROOT + "/*.pkl"))
print(f"archives found: {len(files)}", flush=True)

arcs = []
for f in files:
    d = pickle.load(open(f, "rb"))
    arcs.append((d["question_id"], np.asarray(d["C"], dtype=np.float32),
                 np.asarray(d["qC"], dtype=np.float32),
                 [int(g) for g in np.atleast_1d(d["gold"])]))
Ns = np.array([a[1].shape[0] for a in arcs])
out["cohort"] = {"n_archives": len(arcs), "N_min": int(Ns.min()), "N_max": int(Ns.max()),
                 "N_median": float(np.median(Ns)), "dim": int(arcs[0][1].shape[1])}
print("COHORT:", out["cohort"], flush=True)


def exp_all_at_k(d, gold, K):
    """Expected ALL@K under uniform random tie-breaking (order-independent)."""
    sd = np.sort(d)
    thr = sd[K - 1]
    strictly = int((d < thr).sum())
    slots = K - strictly
    bc = int((d == thr).sum())
    g_strict = sum(1 for g in gold if d[g] < thr)
    g_tied = sum(1 for g in gold if d[g] == thr)
    if len(gold) - g_strict - g_tied > 0:
        return 0.0, (bc > slots), bc
    if g_tied == 0:
        return 1.0, (bc > slots), bc
    if g_tied > slots:
        return 0.0, True, bc
    return comb(bc - g_tied, slots - g_tied) / comb(bc, slots), (bc > slots), bc


def arms(C, q, gold, K=3):
    mu = C.mean(axis=0)
    Cc = C - mu
    qc = q - mu
    B = (Cc >= 0)
    qb = (qc >= 0)
    dh = (B != qb).sum(axis=1).astype(np.float64)          # SIGN96 Hamming
    nb = np.linalg.norm(Cc, axis=1)
    nq = np.linalg.norm(qc)
    cos = (Cc @ qc) / (nb * nq + 1e-30)
    codes = np.where(B, 1.0, -1.0)
    aqs = codes @ qc                                        # AQS: sign codes . continuous query
    hs, tie_h, bc_h = exp_all_at_k(dh, gold, K)
    hf, tie_f, _ = exp_all_at_k(-cos.astype(np.float64), gold, K)
    ha, tie_a, bc_a = exp_all_at_k(-aqs.astype(np.float64), gold, K)
    return hs, hf, ha, tie_h, bc_h, tie_a


# ---------- 1+6: tie rate / accuracy at native N, plus AQS ----------
rows = []
for qid, C, q, gold in arcs:
    hs, hf, ha, tie_h, bc_h, tie_a = arms(C, q, gold, K)
    rows.append((C.shape[0], hs, hf, ha, tie_h, bc_h, tie_a))
R = np.array([[r[0], r[1], r[2], r[3], float(r[4]), r[5], float(r[6])] for r in rows])
out["native"] = {
    "n": len(R),
    "sign_all3": float(R[:, 1].mean()),
    "float_all3": float(R[:, 2].mean()),
    "aqs_all3": float(R[:, 3].mean()),
    "delta_sign_minus_float_pp": float(100 * (R[:, 1].mean() - R[:, 2].mean())),
    "delta_aqs_minus_sign_pp": float(100 * (R[:, 3].mean() - R[:, 1].mean())),
    "hamming_boundary_tie_rate": float(R[:, 4].mean()),
    "aqs_boundary_tie_rate": float(R[:, 6].mean()),
}
tied = R[:, 4] > 0
out["native"]["aqs_resolves_frac_of_hamming_ties"] = float(1.0 - R[tied, 6].mean()) if tied.any() else None
print("NATIVE:", json.dumps(out["native"], indent=1), flush=True)

# ---------- 5: heavy tails / hubness ----------
samp = rng.choice(len(arcs), size=60, replace=False)
vals, skews, kurts = [], [], []
for i in samp:
    C = arcs[i][1]
    Cc = (C - C.mean(axis=0)).astype(np.float64)
    m2 = (Cc ** 2).mean(axis=0)
    m3 = (Cc ** 3).mean(axis=0)
    m4 = (Cc ** 4).mean(axis=0)
    skews.append(m3 / (m2 ** 1.5 + 1e-300))
    kurts.append(m4 / (m2 ** 2 + 1e-300) - 3.0)
    vals.append(Cc.ravel()[rng.choice(Cc.size, size=min(20000, Cc.size), replace=False)])
sk = np.concatenate(skews)
ku = np.concatenate(kurts)
allv = np.concatenate(vals)
m2 = (allv ** 2).mean()
out["tails"] = {
    "per_coord_median_excess_kurtosis": float(np.median(ku)),
    "per_coord_median_skew": float(np.median(sk)),
    "per_coord_p90_excess_kurtosis": float(np.quantile(ku, 0.90)),
    "pooled_excess_kurtosis": float((allv ** 4).mean() / m2 ** 2 - 3.0),
    "pooled_skew": float((allv ** 3).mean() / m2 ** 1.5),
    "claim_kurtosis_9_71": "REFUTED" if np.median(ku) < 3 else "NOT_REFUTED",
}
print("TAILS:", json.dumps(out["tails"], indent=1), flush=True)

# ---------- 4: spectral decay exponent p ----------
ps, mass12 = [], []
for i in samp:
    C = arcs[i][1]
    Cc = (C - C.mean(axis=0)).astype(np.float64)
    s = np.linalg.svd(Cc, compute_uv=False)
    s = s[s > 0]
    idx = np.arange(1, len(s) + 1)
    lo, hi = 0, min(len(s), 96)
    A = np.vstack([np.log(idx[lo:hi]), np.ones(hi - lo)]).T
    slope, _ = np.linalg.lstsq(A, np.log(s[lo:hi]), rcond=None)[0]
    ps.append(-slope)
    mass12.append(float((s[:12] ** 2).sum() / (s ** 2).sum()))
out["spectrum"] = {
    "n_archives_sampled": int(len(samp)),
    "p_median": float(np.median(ps)),
    "p_p10": float(np.quantile(ps, 0.10)),
    "p_p90": float(np.quantile(ps, 0.90)),
    "mass_first12_median": float(np.median(mass12)),
    "claim_p_range_0_25_0_55": "INSIDE" if 0.25 <= np.median(ps) <= 0.55 else "OUTSIDE",
    "claim_mass12_20_30pct": "INSIDE" if 0.20 <= np.median(mass12) <= 0.30 else "OUTSIDE",
}
print("SPECTRUM:", json.dumps(out["spectrum"], indent=1), flush=True)

# ---------- 1: scale dependence via pooled-archive probe ----------
scale = []
for k_pool in [1, 2, 4, 10, 20, 50]:
    n_q = 120 if k_pool <= 20 else 60
    accS = accF = accA = tierate = 0.0
    Nsum = 0
    picks = rng.choice(len(arcs), size=n_q, replace=False)
    for p in picks:
        qid, C0, q, gold0 = arcs[p]
        others = [j for j in rng.choice(len(arcs), size=k_pool * 3, replace=False) if j != p][: k_pool - 1]
        blocks = [C0] + [arcs[j][1] for j in others]
        C = np.vstack(blocks)
        gold = list(gold0)  # C0 occupies rows 0..N0-1, gold indices unchanged
        hs, hf, ha, tie_h, bc_h, tie_a = arms(C, q, gold, K)
        accS += hs
        accF += hf
        accA += ha
        tierate += float(tie_h)
        Nsum += C.shape[0]
    scale.append({
        "pool_archives": k_pool, "n_queries": n_q, "N_mean": Nsum / n_q,
        "sign_all3": accS / n_q, "float_all3": accF / n_q, "aqs_all3": accA / n_q,
        "delta_pp": 100 * (accS - accF) / n_q,
        "hamming_tie_rate": tierate / n_q,
    })
    print("SCALE:", json.dumps(scale[-1]), flush=True)
out["scale_probe"] = scale

out["role_separation"] = {"status": "UNAVAILABLE",
                          "reason": "LME cache_repr keys are question_id/C/qC/gold/hetero; no speaker-role labels"}
out["l3_hierarchy_arithmetic"] = {
    "float32_768d_bytes_per_turn": 768 * 4,
    "one_million_turns_GB": 768 * 4 * 1e6 / 1e9,
    "sign96_bytes_per_turn": 12,
    "one_million_turns_MiB": 12 * 1e6 / 1048576,
    "note": "arithmetic checks out; but query-time embedding needs the fitted pipeline "
            "(44,220,235 B measured this session, VERIFIED) which is ~3.7x the 12 MB code set "
            "and does not fit L3 either",
}

json.dump(out, open("/mnt/c/Users/MDP/dev/llmzip-work/coord_eval_ideas_results.json", "w"), indent=1)
print("\nWROTE coord_eval_ideas_results.json")
