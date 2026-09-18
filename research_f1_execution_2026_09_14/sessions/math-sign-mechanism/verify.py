"""Exact rational / exhaustive small-case checks for the sign-vs-cosine model.

Stdlib only (fractions, itertools, json, math for display only).
Decisions are made with Fraction arithmetic; floats appear only in displays.
Writes results.json next to itself. Exit nonzero on any failed expectation.
"""
import itertools
import json
from fractions import Fraction as F

OUT = []
def emit(s=""):
    OUT.append(s)
    print(s)

def exact_cos_cmp(a, r2, b, s2):
    """Compare a/sqrt(r2) vs b/sqrt(s2); a,b = dots (Fraction), r2,s2 = squared
    norms (Fraction, >0). Returns -1/0/1 with zero floating point."""
    assert r2 > 0 and s2 > 0
    if (a <= 0) != (b <= 0):
        # strictly different signs (or one zero): order decided
        if a < b and (a <= 0 <= b) and not (a == 0 and b == 0):
            pass
        if a == 0 and b == 0:
            return 0
        return -1 if a < b else 1
    if a == 0 and b == 0:
        return 0
    # same nonzero sign: square (monotone on each half-line)
    left, right = a * a * s2, b * b * r2
    if left == right:
        return 0
    if a > 0:  # increasing in value
        return -1 if left < right else 1
    return -1 if left > right else 1  # both negative: larger square = smaller value

def hamming(s1, s2):
    return sum(1 for a, b in zip(s1, s2) if a != b)

def sgn_vec(v):
    # frozen protocol convention: C >= 0  -> +1
    return tuple(1 if x >= 0 else -1 for x in v)

# ---------------------------------------------------------------- E1 / E2
emit("== E1: sign correct, cosine wrong (d=3, strict, convention-independent) ==")
q  = (F(1), F(1), F(1))
R  = (F(1), F(1, 10), F(1, 10))      # gold
I  = (F(-1), F(5), F(5))             # distractor
hR, hI = hamming(sgn_vec(q), sgn_vec(R)), hamming(sgn_vec(q), sgn_vec(I))
dR = sum(qi * ri for qi, ri in zip(q, R))
dI = sum(qi * ii for qi, ii in zip(q, I))
nR2 = sum(ri * ri for ri in R)
nI2 = sum(ii * ii for ii in I)
nq2 = sum(qi * qi for qi in q)
c = exact_cos_cmp(dR, nR2 * nq2, dI, nI2 * nq2)
emit(f"  Hamming: gold={hR} *-distractor={hI} -> sign ranks gold first: {hR < hI}")
emit(f"  dots: gold={float(dR)} distractor={float(dI)}; "
     f"cos gold={float(dR) / (float(nR2) ** .5 * float(nq2) ** .5):.6f}, "
     f"cos distr={float(dI) / (float(nI2) ** .5 * float(nq2) ** .5):.6f}")
emit(f"  exact cos cmp (gold vs distr) = {c} (expect -1: cosine ranks distractor first)")
assert hR == 0 and hI == 1 and c == -1
# certificate identity: 9/sqrt(51) > 1.2/sqrt(1.02)  <=> 81*1.02 > 1.44*51
assert F(81) * F(102, 100) > F(144, 100) * F(51)
emit("  E1 OK (exact: 81*1.02=82.62 > 1.44*51=73.44, both dots positive)")

emit("== E2: cosine correct, sign wrong (d=3, strict, convention-independent) ==")
R2 = (F(1), F(-1, 10), F(-1, 10))    # gold
I2 = (F(-1), F(1, 10), F(1, 10))     # distractor
hR2 = hamming(sgn_vec(q), sgn_vec(R2))
hI2 = hamming(sgn_vec(q), sgn_vec(I2))
dR2 = sum(qi * ri for qi, ri in zip(q, R2))
dI2 = sum(qi * ii for qi, ii in zip(q, I2))
nR22 = sum(ri * ri for ri in R2)
nI22 = sum(ii * ii for ii in I2)
c2 = exact_cos_cmp(dR2, nR22 * nq2, dI2, nI22 * nq2)
emit(f"  Hamming: gold={hR2} distractor={hI2} -> sign ranks distractor first: {hR2 > hI2}")
emit(f"  dots: gold={float(dR2)} distractor={float(dI2)} (norms equal) -> cosine exact cmp = {c2}")
assert hR2 == 2 and hI2 == 1 and dR2 == F(4, 5) and dI2 == F(-4, 5) and c2 == 1
emit("  E2 OK (exact: dots +0.8 vs -0.8, equal norms)")

# ------------------------------------------------- Model H (probabilistic)
emit("== Model H: 1 signal + 2 nuisance coords, shared nuisance scale t > 0 ==")
def model_H(t):
    """Exhaustive 16-state enumeration. Returns dict of exact Fractions."""
    t = F(t)
    W = L = T = 0  # sign strict-win / loss / tie masses (gold vs one non-gold)
    cW = cL = cT = 0
    detail = {}
    for e2, e3, d2, d3 in itertools.product((1, -1), repeat=4):
        A = (e2 + 1) // 2 + (e3 + 1) // 2   # gold nuisance agreements (0..2)
        B = (d2 + 1) // 2 + (d3 + 1) // 2   # non-gold nuisance agreements
        if A > B - 1:
            W += 1
        elif A == B - 1:
            T += 1
        else:
            L += 1
        E = e2 + e3 - (d2 + d3)              # in {-4,-2,0,2,4}
        thr = F(-2, 1) / t
        if E > thr:
            cW += 1
        elif E == thr:
            cT += 1
        else:
            cL += 1
    n = F(16)
    S = lambda x: str(x / n)
    out = dict(t=str(t), sign_win=S(W), sign_tie=S(T), sign_loss=S(L),
               cos_win=S(cW), cos_tie=S(cT), cos_loss=S(cL),
               sign_exp=str((W + F(T, 2)) / n), cos_exp=str((cW + F(cT, 2)) / n),
               sign_pess=S(W), cos_pess=S(cW),
               sign_opt=str((W + T) / n), cos_opt=str((cW + cT) / n))
    return out

H_lo = model_H(F(1, 2))    # t = 0.5
H_hi = model_H(F(10))      # t = 10
for H in (H_lo, H_hi):
    emit(f"  t={H['t']}: sign win/tie/loss = {H['sign_win']} {H['sign_tie']} {H['sign_loss']} "
         f"exp={float(F(H['sign_exp'])):.4f}; "
         f"cos win/tie/loss = {H['cos_win']} {H['cos_tie']} {H['cos_loss']} "
         f"exp={float(F(H['cos_exp'])):.4f}")
assert F(H_lo["sign_exp"]) == F(13, 16) and F(H_hi["sign_exp"]) == F(13, 16)
assert F(H_lo["cos_exp"]) == F(31, 32) and F(H_hi["cos_exp"]) == F(11, 16)
assert F(H_lo["cos_exp"]) > F(H_lo["sign_exp"])      # LOSE regime (sign worse)
assert F(H_hi["cos_exp"]) < F(H_hi["sign_exp"])      # WIN regime (sign better)
assert F(H_lo["cos_pess"]) > F(H_lo["sign_pess"])    # lose holds under pess
assert F(H_hi["cos_pess"]) == F(H_hi["sign_pess"])   # win ties under pess: disclosed
assert F(H_hi["cos_opt"]) < F(H_hi["sign_opt"])      # win holds under opt
emit("  H OK: P_sign(exp)=13/16 for all t>0; P_cos(1/2)=31/32; P_cos(10)=11/16")

# ------------------------------------------- transport: pairwise -> top-3
emit("== Transport lemma: single gold, N-1 iid non-golds, exact E[FR@3] ==")
def expected_fr3(N, u, v):
    """u=P(non-gold strictly closer), v=P(tied), w=rest. Exact Fraction."""
    from math import comb
    w = F(1) - u - v
    assert w >= 0
    total = F(0)
    for i in range(N):          # i = # strictly closer
        for j in range(N - i):  # j = # tied (excl. gold)
            rest = N - 1 - i - j
            if rest < 0:
                continue
            from math import factorial
            mult = F(factorial(N - 1),
                     factorial(i) * factorial(j) * factorial(rest))
            p = mult * u**i * v**j * w**rest
            T = j + 1
            if i >= 3:
                f = F(0)
            elif i + T <= 3:
                f = F(1)
            else:
                f = F(3 - i, T)
            total += p * f
    return total

transport = {}
for N in (6, 10):
    sN = expected_fr3(N, F(1, 16), F(4, 16))    # sign arm (both regimes)
    cN_lo = expected_fr3(N, F(0), F(1, 16))     # cosine at t=1/2
    cN_hi = expected_fr3(N, F(5, 16), F(0))     # cosine at t=10
    transport[N] = dict(sign=str(sN), cos_lo=str(cN_lo), cos_hi=str(cN_hi))
    emit(f"  N={N}: sign E[FR@3]={float(sN):.6f} ({sN}); "
         f"cos(t=1/2)={float(cN_lo):.6f} ({cN_lo}); cos(t=10)={float(cN_hi):.6f} ({cN_hi})")
    assert cN_lo > sN > cN_hi, f"transport direction failed at N={N}"
emit("  transport OK: pairwise gaps preserve direction at top-3 for N=6,10")

# ------------------------------------------- variance-selection micro-model V
emit("== Model V: fresh top-variance-selection counterexample (6-doc archive) ==")
docs = {  # coord values (Fractions); gold = G
    "G":  (F(10), F(-10), F(1), F(1)),
    "D1": (F(9), F(-9), F(-1), F(-1)),
    "D2": (F(-9), F(9), F(-1), F(1)),
    "D3": (F(-9), F(-9), F(1), F(-1)),
    "D4": (F(9), F(-9), F(-1), F(1)),
    "D5": (F(8), F(-10), F(1), F(-1)),
}
qv = (F(1), F(1), F(1), F(1))
qs = sgn_vec(qv)
def popvar(xs):
    m = sum(xs, F(0)) / len(xs)
    return sum((x - m) ** 2 for x in xs) / len(xs)
cols = list(zip(*docs.values()))
variances = [popvar(c) for c in cols]
order = sorted(range(4), key=lambda j: variances[j], reverse=True)
emit(f"  per-coordinate population variances: {[float(v) for v in variances]}")
emit(f"  variance rank (desc): {order}")
assert order[:2] == [0, 1] and order[2:] == [2, 3]
def fr3_subset(sub):
    dg = hamming(tuple(qs[j] for j in sub),
                 tuple(sgn_vec(docs["G"])[j] for j in sub))
    S = T = 0
    for k, d in docs.items():
        if k == "G":
            continue
        dd = hamming(tuple(qs[j] for j in sub),
                     tuple(sgn_vec(d)[j] for j in sub))
        if dd < dg:
            S += 1
        elif dd == dg:
            T += 1
    T += 1
    if S >= 3:
        return F(0), S, T
    if S + T <= 3:
        return F(1), S, T
    return F(3 - S, T), S, T
f_top, S_top, T_top = fr3_subset([0, 1])
f_bot, S_bot, T_bot = fr3_subset([2, 3])
f_full, S_full, T_full = fr3_subset([0, 1, 2, 3])
emit(f"  TOP2-var subset FR@3={float(f_top)} (S={S_top},T={T_top}); "
     f"BOT2-var={float(f_bot)} (S={S_bot},T={T_bot}); full={float(f_full)}")
assert f_top == F(3, 5) and f_bot == F(1) and f_full == F(1)
emit("  V OK: BOT2 (1.0) strictly beats TOP2 (0.6); full code perfect (1.0)")

# ------------------------------------------- F1: d=2 symmetric trap (falsified idea)
emit("== F1: d=2 symmetric-signal model -> cosine ALWAYS correct (proof check) ==")
import random
random.seed(7)
for trial in range(6):
    u = F(random.randint(1, 5), 2)
    vr = F(random.randint(0, 6), 2)
    vi = F(random.randint(0, 6), 2)
    # R=(u,vr), I=(-u,vi), q=(1,1): f_R=(vr+u)^2/(u^2+vr^2) >= 1 > f_I
    assert (vr + u) ** 2 >= u * u + vr * vr
    assert (vi - u) ** 2 < u * u + vi * vi or vi == 0 or u == 0
emit("  F1 OK: (v+u)^2>=u^2+v^2 and (v-u)^2<u^2+v^2 (u,v>0) hold; cosine unbeatable there")

results = {
    "labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED", "NOT FOR CITATION",
               "DISCLOSE-BEFORE-USE"],
    "E1": {"q": [1, 1, 1], "R": ["1", "0.1", "0.1"], "I": ["-1", "5", "5"],
           "hamming_gold": hR, "hamming_distractor": hI, "cos_cmp_gold_vs_distr": c,
           "certificate": "81*1.02=82.62 > 1.44*51=73.44, both dots positive"},
    "E2": {"q": [1, 1, 1], "R": ["1", "-0.1", "-0.1"], "I": ["-1", "0.1", "0.1"],
           "hamming_gold": hR2, "hamming_distractor": hI2,
           "dots": [str(dR2), str(dI2)], "cos_cmp_gold_vs_distr": c2},
    "model_H": {"t_lo": H_lo, "t_hi": H_hi,
                "reading": "sign exp 13/16 all t>0; cos exp 31/32 at t=1/2, 11/16 at t=10"},
    "transport": {str(k): v for k, v in transport.items()},
    "model_V": {"variances": [str(v) for v in variances], "rank_desc": order,
                "FR_TOP2": str(f_top), "FR_BOT2": str(f_bot), "FR_full": str(f_full)},
}
with open("/home/mdp/muse-work/math-sign-mechanism/results.json", "w") as f:
    json.dump(results, f, indent=2)
emit("wrote results.json")
emit("ALL CHECKS PASSED")
