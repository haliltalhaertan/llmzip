# 03_geometry probe: scorer algebra + tie sameness + norm_math witnesses
# READ-ONLY wrt sources; writes only to CWD (outputs/).
# Env: PYTHONDONTWRITEBYTECODE=1, single-thread BLAS, via compute.sh.
"""Algebraic invariants for sym/asym/qscale/raw/std under the SAME exact ties."""
import hashlib
import json
import math
import os
from fractions import Fraction as Fr

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "outputs")
os.makedirs(OUT, exist_ok=True)
SALT = "audit-03-geometry"
rng = np.random.default_rng(20260917)

results = {"labels": "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]",
           "checks": {}}


def check(name, ok, detail=""):
    results["checks"][name] = {"pass": bool(ok), "detail": str(detail)}
    print(("PASS " if ok else "FAIL ") + name + (" | " + str(detail) if detail else ""), flush=True)
    return bool(ok)


def cosine_raw(C, q):
    C = np.asarray(C, float)
    q = np.asarray(q, float).ravel()
    with np.errstate(divide="ignore", invalid="ignore"):
        return (C @ q) / (np.linalg.norm(C, axis=1) * np.linalg.norm(q))


def fit_std_quant(C):
    return np.maximum(np.std(np.asarray(C, float), axis=0, ddof=0), 1e-12)


def fit_std_base(C):
    s = np.std(np.asarray(C, float), axis=0, ddof=0)
    return np.where(s == 0, 1.0, s)


def cosine_std(C, q, std):
    return cosine_raw(C / std[None, :], q / std)


def det_topk(scores, archive_id, k):
    s = np.asarray(scores, float).ravel()
    m = np.where(np.isfinite(s), s, -np.inf)
    hs = [hashlib.sha256(f"{SALT}|{archive_id}|{r}".encode()).hexdigest() for r in range(len(s))]
    tb = np.array(sorted(range(len(s)), key=lambda r: (hs[r], r)))
    return tb[np.argsort(-m[tb], kind="stable")][:k]


def expected_hit(scores, gold, k):
    s = np.asarray(scores, float).ravel()
    m = np.where(np.isfinite(s), s, -np.inf)
    gset = set(int(g) for g in np.asarray(gold).ravel().tolist())
    uniq = np.unique(m)[::-1]
    better = 0
    for lv in uniq:
        idx = np.nonzero(m == lv)[0]
        B = len(idx)
        if better >= k:
            return 0.0
        if better + B <= k:
            if any(int(i) in gset for i in idx):
                return 1.0  # gold inside a fully-included bucket: always retrieved
            better += B
            continue
        gb = sum(1 for i in idx if int(i) in gset)
        take = k - better
        if gb == 0:
            return 0.0
        if take >= B:
            return 1.0
        return 1.0 - math.comb(B - gb, take) / math.comb(B, take)
    # all fit inside k
    top = det_topk(scores, "x", k)
    return 1.0 if any(int(t) in gset for t in top) else 0.0


# ---------- Fixture F1: benign coherent clusters, d=4 ----------
Y = np.array([
    [0.9, 0.8, 0.1, 0.0],
    [0.8, 0.9, 0.0, 0.1],
    [0.85, 0.75, 0.2, -0.1],
    [-0.8, -0.7, 0.9, 0.8],
    [-0.7, -0.8, 0.8, 0.9],
    [0.1, 0.0, -0.9, -0.8],
], float)
yq = np.array([0.9, 0.85, 0.05, 0.0], float)
gold = [0, 1]
mu = Y.mean(axis=0, keepdims=True)
C = Y - mu
QC = (yq - mu.ravel())
sig_q = fit_std_quant(C)
sig_b = fit_std_base(C)
d = Y.shape[1]

Db = (C >= 0)
Dpm = np.where(Db, 1.0, -1.0)
qb = (QC >= 0)
sym = -np.count_nonzero(Db != qb[None, :], axis=1).astype(float)
asym_c = (Dpm @ QC) / math.sqrt(d)
qscale = Dpm @ (QC / sig_q)
f_c = cosine_raw(C, QC)
f_u = cosine_raw(Y, yq)
f_std = cosine_std(C, QC, sig_q)

check("T1_sign_sigma_invariance",
      bool(np.array_equal(np.sign(C / sig_q[None, :]), np.sign(C))),
      "sign(C/sig)==sign(C) elementwise on F1 (sig>0 everywhere: %s)" % np.array2string(sig_q, precision=4))
sym_scaled = -np.count_nonzero((C / sig_q[None, :] >= 0) != qb[None, :], axis=1).astype(float)
check("T2_sym_rank_invariant_under_sigma", bool(np.array_equal(sym, sym_scaled)),
      "Hamming vectors equal: %s" % sym.tolist())
check("T3_float_moves_under_sigma", bool(float(np.max(np.abs(f_c - f_std))) > 1e-12),
      "max|cos_c - cos_std| = %.6f" % float(np.max(np.abs(f_c - f_std))))
o_c = det_topk(f_c, "F1", 3).tolist()
o_s = det_topk(f_std, "F1", 3).tolist()
check("T3bF1_coherent_top3_agrees", o_c == o_s,
      "top3 centered %s vs standardized %s (coherent fixture need not separate arms)" % (o_c, o_s))
n_flip_bits = int(np.count_nonzero((Y >= 0) != (C >= 0)))
check("T4_centering_flips_bits", n_flip_bits > 0,
      "%d/24 bits differ between sign(Y) and sign(C); mu=%s" % (n_flip_bits, np.array2string(mu.ravel(), precision=4)))
o_sym = det_topk(sym, "F1", 3).tolist()
o_asym = det_topk(asym_c, "F1", 3).tolist()
check("T5F1_coherent_top3_agrees", o_sym == o_asym,
      "sym top3 %s scores %s | asym top3 %s (coherent fixture need not separate arms)" % (o_sym, sym[o_sym].tolist(), o_asym))
o_qs = det_topk(qscale, "F1", 3).tolist()
check("T6F1_coherent_top3_agrees", o_qs == o_asym,
      "asym top3 %s vs qscale top3 %s" % (o_asym, o_qs))

# All scorers under SAME ties: full table
table = {}
for nm, sc in [("sym", sym), ("asym_c", asym_c), ("qscale", qscale),
               ("float_c", f_c), ("float_u", f_u), ("float_std", f_std)]:
    top = det_topk(sc, "F1", 3).tolist()
    table[nm] = {"scores": [float(v) for v in np.asarray(sc).ravel().tolist()],
                 "top3": top, "exp_hit3": expected_hit(sc, gold, 3),
                 "det_hit3": float(1 if any(t in set(gold) for t in top) else 0)}
results["F1_table"] = table
n_same = sum(1 for a in table for b in table if table[a]["top3"] == table[b]["top3"])
check("T6bF1_coherent_all_agree", n_same == 36,
      "%d/36 ordered pairs share top3 on coherent F1 (separation lives in F1b)" % n_same)

# ---------- T7: ties — duplicate codes, exact expectation vs Monte Carlo ----------
Y2 = np.array([[0.5, 0.4, -0.2, 0.3],
               [0.6, 0.5, -0.1, 0.2],   # same sign pattern as row 0
               [-0.5, -0.4, 0.2, -0.3],
               [-0.4, 0.6, 0.5, 0.4]], float)
q2 = np.array([0.55, 0.45, -0.15, 0.25], float)
mu2 = Y2.mean(axis=0, keepdims=True)
C2 = Y2 - mu2
Q2 = q2 - mu2.ravel()
Db2 = (C2 >= 0)
sym2 = -np.count_nonzero(Db2 != (Q2 >= 0)[None, :], axis=1).astype(float)
check("T7a_sym_tie_exists", bool(np.count_nonzero(sym2 == sym2.max()) >= 2),
      "sym scores %s" % sym2.tolist())
eh = expected_hit(sym2, [0], 2)
# Monte Carlo within-bucket tiebreak
s2 = np.where(np.isfinite(sym2), sym2, -np.inf)
uniq = np.unique(s2)[::-1]
mc_n = 40000
hits = 0
rr = np.random.default_rng(7)
for _ in range(mc_n):
    perm = np.arange(len(s2))
    # random priority within each equal-score bucket
    pri = rr.random(len(s2))
    order = sorted(range(len(s2)), key=lambda i: (-s2[i], pri[i]))[:2]
    if 0 in order:
        hits += 1
mc = hits / mc_n
check("T7b_expected_hit_matches_MC", abs(eh - mc) < 0.01,
      "exact %.4f vs MC(%d) %.4f" % (eh, mc_n, mc))
results["T7"] = {"sym2": sym2.tolist(), "exact": eh, "mc": mc, "n": mc_n}

# ---------- Fixture F1b: zero-mean C, heterogeneous axis scales ----------
# Columns sum to 0 (valid centered frame). Axis 0 has tiny scale, rest moderate.
C1b = np.array([
    [-0.10, 0.50, 0.50, 0.50],   # a
    [0.10, -0.50, -0.50, 0.50],  # b
    [0.10, -0.50, -0.50, -0.50], # a'
    [-0.10, 0.50, 0.50, -0.50],  # b'
], float)
assert np.allclose(C1b.mean(axis=0), 0.0)
Q1b = np.array([3.0, 0.10, 0.10, 0.10], float)
sig1b = fit_std_quant(C1b)
Db1b = (C1b >= 0)
Dpm1b = np.where(Db1b, 1.0, -1.0)
qb1b = (Q1b >= 0)
sym1b = -np.count_nonzero(Db1b != qb1b[None, :], axis=1).astype(float)
asym1b = (Dpm1b @ Q1b) / math.sqrt(C1b.shape[1])
qs1b = Dpm1b @ (Q1b / sig1b)
fc1b = cosine_raw(C1b, Q1b)
fs1b = cosine_std(C1b, Q1b, sig1b)
results["F1b"] = {"sigma": sig1b.tolist(),
                  "sym": sym1b.tolist(), "asym": asym1b.tolist(),
                  "qscale": qs1b.tolist(), "float_c": fc1b.tolist(),
                  "float_std": fs1b.tolist()}


def disagrees(x, y):
    x = np.asarray(x, float).ravel()
    y = np.asarray(y, float).ravel()
    for i in range(len(x)):
        for j in range(i + 1, len(x)):
            a = int(x[i] > x[j]) - int(x[i] < x[j])
            b = int(y[i] > y[j]) - int(y[i] < y[j])
            if a != 0 and b != 0 and a != b:
                return True, (i, j)
    return False, None


d_sa, w_sa = disagrees(sym1b, asym1b)
check("T5_sym_vs_asym_disagree_F1b", bool(d_sa),
      "witness docs %s sym %s asym %s" % (w_sa, sym1b.tolist(), np.array2string(asym1b, precision=3)))
d_qa, w_qa = disagrees(qs1b, asym1b)
check("T6F1b_qscale_asym_agree_here", not d_qa,
      "F1b orders coincide (values differ: qscale %s vs asym %s)" % (np.array2string(qs1b, precision=3), np.array2string(asym1b, precision=3)))
d_fs, w_fs = disagrees(fc1b, fs1b)
check("T3bF1b_float_orders_agree_here", not d_fs,
      "F1b float_c %s vs float_std %s coincide in order (magnitudes differ)" % (np.array2string(fc1b, precision=4), np.array2string(fs1b, precision=4)))
d_sq, w_sq = disagrees(sym1b, qs1b)
check("T6b_sym_vs_qscale_disagree_F1b", bool(d_sq),
      "witness docs %s" % (w_sq,))
# NOTE F1b: qscale vs asym agree in order here (both positive-weight linear
# forms in D can coincide); F1c below separates them. Same for float_c/std.

# ---------- Fixture F1c: extreme axis-scale heterogeneity (raw frame) ----------
# sigma is doc-fitted as usual; zero-mean NOT imposed (irrelevant to the
# scorer algebra; F1/F1b already cover centered frames).
C1c = np.array([
    [10.0, 0.0],   # u  signs ++
    [0.0, 1.0],    # v  signs ++
    [-10.0, 0.0],  # w  signs -+
    [-5.0, 0.5],   # t  signs -+
    [5.0, -0.5],   # s  signs +-
], float)
Q1c = np.array([2.0, 1.0], float)
sig1c = fit_std_quant(C1c)
Dpm1c = np.where((C1c >= 0), 1.0, -1.0)
sym1c = -np.count_nonzero((C1c >= 0) != (Q1c >= 0)[None, :], axis=1).astype(float)
asym1c = (Dpm1c @ Q1c) / math.sqrt(C1c.shape[1])
qs1c = Dpm1c @ (Q1c / sig1c)
fc1c = cosine_raw(C1c, Q1c)
fs1c = cosine_std(C1c, Q1c, sig1c)
results["F1c"] = {"sigma": sig1c.tolist(),
                  "sym": sym1c.tolist(), "asym": asym1c.tolist(),
                  "qscale": qs1c.tolist(), "float_c": fc1c.tolist(),
                  "float_std": fs1c.tolist()}
d_f, w_f = disagrees(fc1c, fs1c)
check("T3c_float_rank_flips_F1c", bool(d_f),
      "sigma=%s witness docs %s float_c %s float_std %s"
      % (np.array2string(sig1c, precision=3), w_f,
         np.array2string(fc1c, precision=4), np.array2string(fs1c, precision=4)))
d_qa2, w_qa2 = disagrees(qs1c, asym1c)
check("T6c_qscale_vs_asym_disagree_F1c", bool(d_qa2),
      "witness docs %s qscale %s asym %s"
      % (w_qa2, np.array2string(qs1c, precision=4), np.array2string(asym1c, precision=4)))

# ---------- T8: sigma floor conventions ----------
Y3 = np.array([[1.0, 0.5], [2.0, 0.5], [3.0, 0.5]], float)  # col1 constant
C3 = Y3 - Y3.mean(axis=0, keepdims=True)
check("T8_zero_variance_column", bool(np.std(C3[:, 1], ddof=0) == 0.0),
      "quant floor -> %g; baseline -> %g" % (fit_std_quant(C3)[1], fit_std_base(C3)[1]))

# ---------- T9: cache centering (read-only, one archive) ----------
import pickle
t9 = {}
try:
    with open("/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_repr/RT01.pkl", "rb") as f:
        o = pickle.load(f)
    t9["keys"] = sorted(map(str, o.keys())) if isinstance(o, dict) else type(o).__name__
    Cc = np.asarray(o["C"], float)
    t9["C_shape"] = list(Cc.shape)
    cm = Cc.mean(axis=0)
    t9["colmean_abs_max"] = float(np.max(np.abs(cm)))
    t9["colmean_abs_med"] = float(np.median(np.abs(cm)))
    t9["centered_like"] = bool(float(np.max(np.abs(cm))) < 1e-9)
except Exception as e:
    t9["error"] = repr(e)
results["T9_cache"] = t9
print("T9 cache keys:", t9.get("keys"), "| colmean|max|=%.3g med=%.3g" % (t9.get("colmean_abs_max", float("nan")), t9.get("colmean_abs_med", float("nan"))), flush=True)

# ---------- T10: norm_math witnesses, exact Fractions ----------
# D1: q=(0,0,-1), s=(-1,-1,1), x=(-3/5,-4/5,0)
q = [Fr(0), Fr(0), Fr(-1)]
s = [-1, -1, 1]
x = [Fr(-3, 5), Fr(-4, 5), Fr(0)]
m = max(si * qi for si, qi in zip(s, q))
inF = (x[0] < 0 and x[1] < 0 and x[2] >= 0)
unit = sum(v * v for v in x) == 1
score = sum(qi * xi for qi, xi in zip(q, x))
axes = [[Fr(-1), Fr(0), Fr(0)], [Fr(0), Fr(-1), Fr(0)]]
ax_inF = [not (a[0] < 0 and a[1] < 0 and a[2] >= 0) or (a[0] == 0 or a[1] == 0) for a in axes]
# axis (-1,0,0): N-coord x1=0 fails strict <0 -> outside F; same for (0,-1,0)
ax_out = [(a[0] < 0 and a[1] < 0 and a[2] >= 0) for a in axes]
check("T10a_D1_witness", bool(m == 0 and unit and inF and score == 0 and ax_out == [False, False]),
      "m=%s unit=%s inF=%s q.x=%s axes_inF=%s" % (m, unit, inF, score, ax_out))
# D3 lemma: rho=|x|_1/sqrt(d) in [1/sqrt(d),1]
def rho(xv):
    dd = len(xv)
    return sum(abs(v) for v in xv) / math.sqrt(dd)
r_axis = rho([Fr(1), Fr(0), Fr(0), Fr(0)])
r_cent = rho([Fr(1, 2)] * 4)
check("T10b_D3_rho_support", abs(float(r_axis) - 0.5) < 1e-12 and abs(float(r_cent) - 1.0) < 1e-12,
      "rho(e1)=%.4f rho(c)=%.4f; rho=-0.3 impossible since min is +1/sqrt(d)" % (float(r_axis), float(r_cent)))
# D4: d=4 q=c=(1/2 x4): e1 score 1/2 attains lower bound
qd = [Fr(1, 2)] * 4
e1 = [Fr(1), Fr(0), Fr(0), Fr(0)]
check("T10c_D4_closed_endpoint", bool(sum(a * b for a, b in zip(qd, e1)) == Fr(1, 2)),
      "q.e1 = 1/2 -> interval [0.5,1] closed")

with open(os.path.join(OUT, "probe_results.json"), "w") as f:
    json.dump(results, f, indent=1)
npass = sum(1 for v in results["checks"].values() if v["pass"])
print("SUMMARY %d/%d checks passed" % (npass, len(results["checks"])), flush=True)
