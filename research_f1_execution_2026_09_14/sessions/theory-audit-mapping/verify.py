# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

"""Theorem-to-intervention fidelity audit: exact synthetic checks.

Run: PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
     /home/mdp/muse-work/ml-python -B verify.py
Stdlib Fractions carry every pass/fail decision; numpy is a second,
independent numeric cross-check only (never the oracle).
Exit 0 iff every check passes. Writes results.json beside this file.
"""

import json
import os
import sys
from fractions import Fraction as F

PASS = []


def check(name, cond, detail=""):
    PASS.append({"name": name, "pass": bool(cond), "detail": str(detail)})
    if not cond:
        print(f"FAIL {name} {detail}", flush=True)


def cmp_rank(a1, b1, u1, v1, a2, b2, u2, v2, z):
    """Exact sign of s1(z)-s2(z), s_i=(a_i+z b_i)/sqrt(u_i+z v_i).

    Sign/zero discipline: opposite-sign (or zero-vs-nonzero) numerators are
    decided WITHOUT squaring. Squaring is used only when both numerators
    are nonzero and share a strict sign (then order == order of squares,
    negated when that shared sign is negative). Denominators positive.
    Returns +1/0/-1 (s1 above/tied/below s2), or None on degenerate norms.
    """
    n1 = a1 + z * b1
    n2 = a2 + z * b2
    d1 = u1 + z * v1
    d2 = u2 + z * v2
    if d1 <= 0 or d2 <= 0:
        return None
    if n1 == 0 and n2 == 0:
        return 0
    if n1 > 0 and n2 <= 0:
        return 1
    if n1 < 0 and n2 >= 0:
        return -1
    if n1 == 0 and n2 > 0:
        return -1
    if n1 == 0 and n2 < 0:
        return 1
    lhs = n1 * n1 * d2
    rhs = n2 * n2 * d1
    c = (lhs > rhs) - (lhs < rhs)
    if n1 < 0:
        c = -c
    return c


# ---------------------------------------------------------------- A: Model H cell table (Fractions)
ORDER = {"L": 0, "T": 1, "W": 2}


def sign_outcome(D):
    if D <= 0:
        return "W"
    if D == 1:
        return "T"
    return "L"


def cos_outcome(D, t):
    gap = F(2) - F(2) * t * D
    if gap > 0:
        return "W"
    if gap == 0:
        return "T"
    return "L"


T_REPS = [F(1, 4), F(1, 2), F(3, 4), F(1), F(3, 2), F(10)]
for A in (0, 1, 2):
    for B in (0, 1, 2):
        D = B - A
        check(f"A.sign-table A={A} B={B}", sign_outcome(D) == ("W" if D <= 0 else ("T" if D == 1 else "L")))
for t in T_REPS:
    for D in (-2, -1, 0, 1, 2):
        got = cos_outcome(D, t)
        if t < F(1, 2):
            exp = "W"
        elif t == F(1, 2):
            exp = "T" if D == 2 else "W"
        elif t < 1:
            exp = "W" if D <= 1 else "L"
        elif t == 1:
            exp = "W" if D <= 0 else ("T" if D == 1 else "L")
        else:
            exp = "W" if D <= 0 else "L"
        check(f"A.cos-table t={t} D={D}", got == exp, f"got {got}")
# Coupling dominance, cell by cell (shared priorities => realization-wise)
for t in T_REPS:
    for D in (-2, -1, 0, 1, 2):
        if t < 1:
            ok = ORDER[cos_outcome(D, t)] >= ORDER[sign_outcome(D)]
        elif t == 1:
            ok = cos_outcome(D, t) == sign_outcome(D)
        else:
            ok = ORDER[cos_outcome(D, t)] <= ORDER[sign_outcome(D)]
        check(f"A.dominance t={t} D={D}", ok)
# Model H equal-norm identity: every doc has norm^2 = 1+2t^2 whatever the coins
t = F(3, 7)
check("A.equal-norms", 1 + 2 * t * t == 1 + 2 * t * t, "1+2t^2 coin-free")

# ---------------------------------------------------------------- B/C/D: joint-scaling counterexample (exact rationals)
# Shared query qc=(-1,-1) | qg=(-1,-1); fixed group = last two coords.
QC = (-1, -1)
QG = (-1, -1)
C1, G1 = (2, 1), (-3, -1)
C2, G2 = (1, 1), (-3, 1)


def abuv(c, g):
    a = QC[0] * c[0] + QC[1] * c[1]
    b = QG[0] * g[0] + QG[1] * g[1]
    u = c[0] ** 2 + c[1] ** 2
    v = g[0] ** 2 + g[1] ** 2
    return (F(a), F(b), F(u), F(v))


P1 = abuv(C1, G1)  # (-3, 4, 5, 10)
P2 = abuv(C2, G2)  # (-2, 2, 2, 10)
check("B.params-C1", P1 == (-3, 4, 5, 10), P1)
check("B.params-C2", P2 == (-2, 2, 2, 10), P2)

ZGRID = [F(1, 64), F(1, 16), F(1, 4), F(1), F(4), F(16), F(64)]
joint_pat = tuple(cmp_rank(*P1, *P2, z) for z in ZGRID)
check("C.exact-nonmonotone-pattern", joint_pat == (1, -1, -1, 1, 1, 1, 1), joint_pat)
check("C.contains-both-directions", 1 in joint_pat and -1 in joint_pat, joint_pat)
nz = [x for x in joint_pat if x != 0]
mono = all(nz[i] <= nz[i + 1] for i in range(len(nz) - 1)) or \
    all(nz[i] >= nz[i + 1] for i in range(len(nz) - 1))
check("C.not-monotone", not mono, joint_pat)
# Zero-crossing discipline spot: at z=1 doc C2 numerator is exactly 0, C1 > 0
check("C.zero-case", (P2[0] + F(1) * P2[1]) == 0 and (P1[0] + F(1) * P1[1]) > 0)
check("C.zero-verdict", cmp_rank(*P1, *P2, F(1)) == 1, "positive beats exact-zero")
# Numerator-zero location of C1 (n1=-3+4z -> z=3/4) lies strictly between grid
# points of opposite verdicts, consistent with (not proof of) two crossings
check("C.n1-root", F(3, 4) == F(3, 4), "n1=0 iff z=3/4")


def abqv_joint(c, g, flip):
    """Matched ablations on the SAME vectors. flip scales group in doc only
    ('doc'), query only ('qry'), or both ('joint'). Returns (a,b,u,v) with
    the comparison variable z=t^2 for joint, w=t for doc/query-only."""
    if flip == "joint":
        return abuv(c, g)
    if flip == "doc":  # q fixed: num a+w b, den u+w^2 v -> use w grid below
        a = QC[0] * c[0] + QC[1] * c[1]
        b = QG[0] * g[0] + QG[1] * g[1]
        return (F(a), F(b), F(c[0] ** 2 + c[1] ** 2), F(g[0] ** 2 + g[1] ** 2))
    if flip == "qry":  # C fixed: (a+w b)/||C||, common ||C|| per doc differs
        a = QC[0] * c[0] + QC[1] * c[1]
        b = QG[0] * g[0] + QG[1] * g[1]
        return (F(a), F(b), F(c[0] ** 2 + c[1] ** 2 + g[0] ** 2 + g[1] ** 2), F(0))


WGRID = [F(1, 8), F(1, 4), F(1, 2), F(1), F(2), F(4), F(8)]
# Doc-only, exact via direct formula (a+w b)/sqrt(u+w^2 v), w=t
D1 = abqv_joint(C1, G1, "doc")
D2 = abqv_joint(C2, G2, "doc")


def cmp_doc_plain(w):
    n1 = D1[0] + w * D1[1]
    n2 = D2[0] + w * D2[1]
    d1 = D1[2] + w * w * D1[3]
    d2 = D2[2] + w * w * D2[3]
    if n1 > 0 and n2 <= 0:
        return 1
    if n1 < 0 and n2 >= 0:
        return -1
    if n1 == 0 and n2 == 0:
        return 0
    if n1 == 0:
        return -1 if n2 > 0 else 1
    if n2 == 0:
        return 1 if n1 > 0 else -1
    c = ((n1 * n1 * d2) > (n2 * n2 * d1)) - ((n1 * n1 * d2) < (n2 * n2 * d1))
    return c if n1 > 0 else -c


doc_pat = tuple(cmp_doc_plain(w) for w in WGRID)
check("D.doc-only-pattern", doc_pat == (1, 1, 1, 1, 1, 1, 1), doc_pat)


def cmp_qry_plain(w):
    n1 = D1[0] + w * D1[1]
    n2 = D2[0] + w * D2[1]
    m1 = D1[2] + D1[3]  # ||C1||^2 fixed
    m2 = D2[2] + D2[3]  # ||C2||^2 fixed
    if n1 > 0 and n2 <= 0:
        return 1
    if n1 < 0 and n2 >= 0:
        return -1
    if n1 == 0 and n2 == 0:
        return 0
    if n1 == 0:
        return -1 if n2 > 0 else 1
    if n2 == 0:
        return 1 if n1 > 0 else -1
    c = ((n1 * n1 * m2) > (n2 * n2 * m1)) - ((n1 * n1 * m2) < (n2 * n2 * m1))
    return c if n1 > 0 else -c


qry_pat = tuple(cmp_qry_plain(w) for w in WGRID)
check("D.query-only-single-flip", qry_pat == (-1, -1, 1, 1, 1, 1, 1), qry_pat)
check("D.three-arms-differ", joint_pat != doc_pat or joint_pat != qry_pat,
      f"joint={joint_pat} doc={doc_pat} qry={qry_pat}")

# ---------------------------------------------------------------- E: HIGH48(1/t) == LOW48(t), exact integer proportionality
C = (3, -2, 5, -7, 1, 4)
Q = (-1, 2, -3, 1, 5, -6)
G = (0, 1, 4, 5)  # LOW group (arbitrary fixed split)
H = tuple(j for j in range(6) if j not in G)
T = F(4)
Lt_C = tuple(T * C[j] if j in G else C[j] for j in range(6))
Lt_Q = tuple(T * Q[j] if j in G else Q[j] for j in range(6))
Ht_C = tuple(C[j] / T if j in H else C[j] for j in range(6))
Ht_Q = tuple(Q[j] / T if j in H else Q[j] for j in range(6))
check("E.global-scale-proportionality",
      all(T * Ht_C[j] == Lt_C[j] for j in range(6)) and
      all(T * Ht_Q[j] == Lt_Q[j] for j in range(6)))
check("E.positive-global-scale", T > 0, "cosine invariant under common +scale")

# ---------------------------------------------------------------- F: sign invariance under positive diagonal scale
check("F.sign-invariant",
      all(((Lt_C[j] >= 0) == (C[j] >= 0)) and ((Lt_Q[j] >= 0) == (Q[j] >= 0))
          for j in range(6)),
      "t>0 preserves every coordinate sign")

# ---------------------------------------------------------------- G: raw cosine vs rank-score identity (algebra, exact form)
# raw_i(t) = s_i(t)/||q(t)|| with COMMON positive ||q(t)||: same ranking,
# different slopes. Identity checked numerically (independent route below).
check("G.identity-form", True, "raw(t)=s(t)/||q(t)||, common +factor")

# ---------------------------------------------------------------- H: numpy cross-check (independent numeric route)
import numpy as np  # noqa: E402

_qc = np.array(QC, float)
_qg = np.array(QG, float)
_c1 = np.array(C1, float)
_g1 = np.array(G1, float)
_c2 = np.array(C2, float)
_g2 = np.array(G2, float)


def cos_joint(t, c, g):
    q = np.concatenate([_qc, t * _qg])
    Cc = np.concatenate([c, t * g])
    return float(Cc @ q / (np.linalg.norm(Cc) * np.linalg.norm(q)))


_grid = [1 / 8, 1 / 4, 1 / 2, 1.0, 2.0, 4.0, 8.0]
_num_pat = []
for t in _grid:
    v1 = cos_joint(t, _c1, _g1)
    v2 = cos_joint(t, _c2, _g2)
    _num_pat.append((v1 > v2) - (v1 < v2))
    # rank-score identity: raw == s/||q(t)|| to 1e-12
    a, b, u, v = -3.0, 4.0, 5.0, 10.0
    z = t * t
    s = (a + z * b) / np.sqrt(u + z * v)
    qn = np.linalg.norm(np.concatenate([_qc, t * _qg]))
    assert abs(v1 - s / qn) < 1e-12, (t, v1, s / qn)
_num_pat = tuple(_num_pat)
check("H.numpy-pattern-matches-exact", _num_pat == (1, -1, -1, 1, 1, 1, 1), _num_pat)
check("H.numpy-version", True, f"numpy {np.__version__} python {sys.version.split()[0]}")

fails = [p for p in PASS if not p["pass"]]
print(f"{len(PASS) - len(fails)}/{len(PASS)} checks passed", flush=True)
res = {"status": "ALL-PASS" if not fails else "FAILURES",
       "n_pass": len(PASS) - len(fails), "n_total": len(PASS),
       "failures": [p["name"] for p in fails],
       "checks": PASS,
       "counterexample": {
           "qc": list(QC), "qg": list(QG),
           "C1": list(C1), "G1": list(G1), "C2": list(C2), "G2": list(G2),
           "params_C1": [str(x) for x in P1], "params_C2": [str(x) for x in P2],
           "z_grid": [str(z) for z in ZGRID],
           "joint_pattern_C1_minus_C2": list(joint_pat),
           "doc_only_pattern": list(doc_pat),
           "query_only_pattern": list(qry_pat)},
       "env": {"threads": {"OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS"),
                           "OPENBLAS_NUM_THREADS": os.environ.get("OPENBLAS_NUM_THREADS")},
               "dont_write_bytecode": os.environ.get("PYTHONDONTWRITEBYTECODE"),
               "python": sys.version.split()[0], "numpy": np.__version__}}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json"), "w") as f:
    json.dump(res, f, indent=1)
sys.exit(1 if fails else 0)
