#!/usr/bin/env python3
# verify.py — NORMALIZATION-AWARE SIGN-CODE UNCERTAINTY AND RANKING CERTIFICATE
# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
#
# Route 1 (exact): Fractions algebra, no trig, open-boundary-exact membership.
# Route 2 (independent): float trig / numpy grids / Gram-determinant formulation.
# A seeded false/broken variant must fail FOR THE INTENDED REASON (section G).
import json
import math
import sys
from fractions import Fraction as Fr

CHECKS = []


def check(name, ok, detail=""):
    ok = bool(ok)
    CHECKS.append({"name": name, "pass": ok, "detail": str(detail)})
    if not ok:
        print("FAIL %s: %s" % (name, detail), flush=True)
    return ok


# ---------------- Route 1: exact rational helpers ----------------
def vdot(a, b):
    return sum(x * y for x, y in zip(a, b))


def vnorm2(a):
    return vdot(a, a)


def proj_cone(s, v):
    """Projection of v onto closed cone K(s)={y: s_i y_i>=0}, exact."""
    return [vi if si * vi >= 0 else Fr(0) for si, vi in zip(s, v)]


def member_closed(s, x):
    return all(si * xi >= 0 for si, xi in zip(s, x))


def member_F(s, x):
    """Exact open-boundary membership: s_i=+1 allows x_i>=0; s_i=-1 needs x_i<0."""
    for si, xi in zip(s, x):
        if si > 0:
            if xi < 0:
                return False
        else:
            if xi >= 0:
                return False
    return True


def sup_closed(s, q):
    """-> ('norm', sup^2>=0 exact) or ('axis', sup value<=0 exact)."""
    p = proj_cone(s, q)
    if any(v != 0 for v in p):
        return ('norm', vnorm2(p))
    return ('axis', max(si * qi for si, qi in zip(s, q)))


def inf_closed(s, q):
    """-> ('norm', (-inf)^2 exact) or ('axis', inf value exact)."""
    p = proj_cone(s, [-qi for qi in q])
    if any(v != 0 for v in p):
        return ('norm', vnorm2(p))
    return ('axis', min(si * qi for si, qi in zip(s, q)))


def sup_attained(s, q):
    """Exact attainment of sup over OPEN feasible set F(s)."""
    kind, _ = sup_closed(s, q)
    N = [i for i, si in enumerate(s) if si < 0]
    if kind == 'norm':
        return all(q[i] < 0 for i in N)
    m = max(s[i] * q[i] for i in range(len(s)))
    return any(set(N) <= {j} for j in range(len(s)) if s[j] * q[j] == m)


def inf_attained(s, q):
    kind, _ = inf_closed(s, q)
    N = [i for i, si in enumerate(s) if si < 0]
    if kind == 'norm':
        return all(q[i] > 0 for i in N)
    m = min(s[i] * q[i] for i in range(len(s)))
    return any(set(N) <= {j} for j in range(len(s)) if s[j] * q[j] == m)


def closure_maximizer_float(s, qf):
    """Float closure-maximizer y* (axis or projected cone vector)."""
    p = [qi if si * qi >= 0 else 0.0 for si, qi in zip(s, qf)]
    n = math.sqrt(sum(v * v for v in p))
    if n > 0:
        return [v / n for v in p]
    j = max(range(len(s)), key=lambda i: s[i] * qf[i])
    return [float(s[j]) if i == j else 0.0 for i in range(len(s))]


def approach_from_inside(s, ystar, eps=1e-4):
    """Constructive density step: perturb zero N-coords strictly inside, renormalize."""
    d = len(s)
    y = list(ystar)
    for j in range(d):
        if s[j] < 0 and y[j] == 0.0:
            y[j] = -eps
    n = math.sqrt(sum(v * v for v in y))
    return [v / n for v in y]


# ---------------- Section B: Theorem 1, d=2 exhaustive ----------------
D2_PATTERNS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
D2_QUERIES = [
    (Fr(3, 5), Fr(4, 5)),
    (Fr(1, 1), Fr(0, 1)),
    (Fr(-1, 1), Fr(0, 1)),
    (Fr(3, 5), Fr(-4, 5)),
    (Fr(-3, 5), Fr(-4, 5)),
    (Fr(0, 1), Fr(1, 1)),
]


def sup_val_float(s, q):
    kind, v = sup_closed(s, q)
    return math.sqrt(float(v)) if kind == 'norm' else float(v)


def inf_val_float(s, q):
    kind, v = inf_closed(s, q)
    return -math.sqrt(float(v)) if kind == 'norm' else float(v)


def run_d2_sweep():
    import numpy as np
    n = 2880
    th = np.arange(n) * (2 * math.pi / n)
    circ = np.stack([np.cos(th), np.sin(th)], axis=1)
    for s in D2_PATTERNS:
        for q in D2_QUERIES:
            tag = "s=%s,q=(%s,%s)" % (s, q[0], q[1])
            qf = np.array([float(q[0]), float(q[1])])
            m = np.ones(n, dtype=bool)
            for i, si in enumerate(s):
                m &= (circ[:, i] >= 0) if si > 0 else (circ[:, i] < 0)
            assert m.sum() > 0, tag
            scores = circ[m] @ qf
            numax, numin = float(scores.max()), float(scores.min())
            esup, einf = sup_val_float(s, q), inf_val_float(s, q)
            # Route-2 upper fence: no interior point may exceed closed sup.
            check("B2.upper." + tag, numax <= esup + 1e-9,
                  "gridmax=%.12f sup=%.12f" % (numax, esup))
            check("B2.lower." + tag, numin >= einf - 1e-9,
                  "gridmin=%.12f inf=%.12f" % (numin, einf))
            # Density: grid must nearly reach both ends (grid step ~0.0022 rad).
            check("B2.reach-sup." + tag, esup - numax <= 0.01,
                  "gap=%.5f" % (esup - numax))
            check("B2.reach-inf." + tag, numin - einf <= 0.01,
                  "gap=%.5f" % (numin - einf))
            # Exact squared identities (route 1, no trig): sup^2==||P_K q||^2 etc.
            ks, ki = sup_closed(s, q), inf_closed(s, q)
            if ks[0] == 'norm':
                check("B2.exact-sup2." + tag,
                      ks[1] == vnorm2(proj_cone(s, q)), str(ks[1]))
            if ki[0] == 'norm':
                check("B2.exact-inf2." + tag,
                      ki[1] == vnorm2(proj_cone(s, [-qi for qi in q])), str(ki[1]))
            # Constructive approach: x(eps) in F(s) nearly attains closed sup.
            ys = closure_maximizer_float(s, [float(q[0]), float(q[1])])
            check("B2.ys-closed." + tag, member_closed(s, ys), str(ys))
            xe = approach_from_inside(s, ys)
            att = sup_attained(s, q)
            check("B2.att-consistency." + tag,
                  member_F(s, ys) == att, "member=%s att=%s" % (member_F(s, ys), att))
            if not att:
                check("B2.approach." + tag,
                      member_F(s, xe) and (float(q[0]) * xe[0] + float(q[1]) * xe[1]
                                           >= esup - 1e-3),
                      "score=%.9f sup=%.9f" % (float(q[0]) * xe[0] + float(q[1]) * xe[1], esup))


def run_d3_sweep():
    import numpy as np
    na, npol = 360, 180
    az = np.arange(na) * (2 * math.pi / na)
    pol = (np.arange(npol) + 0.5) * (math.pi / npol)
    A, P = np.meshgrid(az, pol)
    G = np.stack([np.sin(P.ravel()) * np.cos(A.ravel()),
                  np.sin(P.ravel()) * np.sin(A.ravel()),
                  np.cos(P.ravel())], axis=1)
    pats = [(a, b, c) for a in (1, -1) for b in (1, -1) for c in (1, -1)]
    queries = [[Fr(1, 3), Fr(2, 3), Fr(2, 3)],
               [Fr(1, 1), Fr(0, 1), Fr(0, 1)],
               [Fr(-1, 3), Fr(2, 3), Fr(2, 3)]]
    for s in pats:
        gm = np.ones(len(G), dtype=bool)
        for i, si in enumerate(s):
            gm &= (G[:, i] >= 0) if si > 0 else (G[:, i] < 0)
        for q in queries:
            tag = "s=%s,q=(%s,%s,%s)" % (s, q[0], q[1], q[2])
            qf = np.array([float(v) for v in q])
            sc = G[gm] @ qf
            esup, einf = sup_val_float(s, q), inf_val_float(s, q)
            check("B3.fence." + tag,
                  float(sc.max()) <= esup + 1e-9 and float(sc.min()) >= einf - 1e-9,
                  "max=%.6f sup=%.6f min=%.6f inf=%.6f"
                  % (float(sc.max()), esup, float(sc.min()), einf))
            check("B3.reach." + tag,
                  esup - float(sc.max()) <= 0.03 and float(sc.min()) - einf <= 0.03,
                  "supgap=%.4f infgap=%.4f"
                  % (esup - float(sc.max()), float(sc.min()) - einf))


# ---------------- Section C: Hamming order need not imply cosine order ----------------
def run_flip_witness():
    # q=(3/5,4/5). xA=(1,0): 2 agreements, score 3/5. xD(eps) in F((+,-)):
    # 1 agreement, score -> 4/5 from below, beats xA already at eps=0.01.
    q = (Fr(3, 5), Fr(4, 5))
    sA, sD = (1, 1), (1, -1)
    xA = (Fr(1, 1), Fr(0, 1))
    check("C.member-xA", member_F(sA, xA), "P-zeros allowed, N empty")
    check("C.score-xA", vdot(q, xA) == Fr(3, 5), str(vdot(q, xA)))
    check("C.supA-infA", abs(sup_val_float(sA, q) - 1.0) < 1e-12
          and abs(inf_val_float(sA, q) - 0.6) < 1e-12,
          "interval (3/5,1]: sup attained (N empty), inf 3/5 at axis e1")
    check("C.supD-infD", abs(sup_val_float(sD, q) - 0.6) < 1e-12
          and abs(inf_val_float(sD, q) + 0.8) < 1e-12,
          "interval [-4/5,3/5): sup NOT attained, inf attained at (0,-1)")
    check("C.supD-open", not sup_attained(sD, q)
          and not member_F(sD, (Fr(1, 1), Fr(0, 1))), "maximizer (1,0) has x2=0")
    check("C.infD-att", inf_attained(sD, q), "minimizer (0,-1) strictly inside")
    import numpy as np
    # Flip uses pattern E=(-,+) (interval [-3/5,4/5)): NOT D, since every
    # A-doc strictly beats every D-doc (sup_D = inf_A = 3/5, both unattained).
    sE = (-1, 1)
    check("C.supE-infE", abs(sup_val_float(sE, q) - 0.8) < 1e-12
          and abs(inf_val_float(sE, q) + 0.6) < 1e-12,
          "interval [-3/5,4/5): sup NOT attained (maximizer (0,1) has x1=0)")
    eps = 0.01
    xE = np.array([-eps, 1.0]) / math.sqrt(1 + eps * eps)
    sEscore = float(q[0]) * xE[0] + float(q[1]) * xE[1]
    check("C.flip", member_F(sE, [Fr(-1, 100), Fr(1, 1)]) and sEscore > 0.6,
          "1-agreement (-,+) score %.9f beats 2-agreement (1,0) score 0.6" % sEscore)
    # Equal-score pair across patterns (ordering unidentifiable from signs alone).
    lo, hi = 0.0, 100.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        v = (0.6 * mid + 0.8) / math.sqrt(mid * mid + 1) - 0.7
        if v > 0:
            lo = mid
        else:
            hi = mid
    t = 0.5 * (lo + hi)
    xA2 = (t / math.sqrt(t * t + 1), 1 / math.sqrt(t * t + 1))
    lo2, hi2 = 0.0, 1.0
    for _ in range(200):
        mid = 0.5 * (lo2 + hi2)
        v = (-0.6 * mid + 0.8) / math.sqrt(mid * mid + 1) - 0.7
        if v > 0:
            lo2 = mid
        else:
            hi2 = mid
    u = 0.5 * (lo2 + hi2)
    xE2 = (-u / math.sqrt(u * u + 1), 1 / math.sqrt(u * u + 1))
    check("C.tie-A", member_F(sA, xA2) and abs(0.6 * xA2[0] + 0.8 * xA2[1] - 0.7) < 1e-9,
          str(xA2))
    check("C.tie-E", member_F(sE, xE2) and abs(0.6 * xE2[0] + 0.8 * xE2[1] - 0.7) < 1e-9,
          str(xE2))


# ---------------- Section D: scalar-tightened cap bound, three formulations ----------------
def cap_cs(u, rho):
    """C-S / orthogonal-decomposition form."""
    disc = max(0.0, (1 - u * u) * (1 - rho * rho))
    d = math.sqrt(disc)
    return (u * rho - d, u * rho + d)


def cap_angle(u, rho):
    """Angle-addition form."""
    uc = min(1.0, max(-1.0, u))
    rc = min(1.0, max(-1.0, rho))
    be, al = math.acos(uc), math.acos(rc)
    return (math.cos(be + al), math.cos(abs(be - al)))


def cap_gram(u, rho):
    """Gram-determinant form: det>=0 is quadratic in t with the same roots."""
    a = 1.0
    b = -2 * u * rho
    # det [[1,u,r],[u,1,t],[r,t,1]] = 1+2urt-u^2-r^2-t^2 >= 0
    # -> t^2 - 2ur t + (u^2+r^2-1) <= 0
    disc = max(0.0, b * b - 4 * a * (u * u + rho * rho - 1.0))
    sq = math.sqrt(disc)
    return ((-b - sq) / 2.0, (-b + sq) / 2.0)


D_CASES = [
    # (u=q.c, rho=x.c, true t=q.x, label)
    (1.0, 0.99, 0.99, "aligned"),
    (0.0, 0.5, 0.1, "orthogonal-center"),
    (-1.0 / (5 * math.sqrt(2)), 1.0 / math.sqrt(2), -0.8, "failure-wide"),
    (1.0 / (3 * math.sqrt(3)), 5.0 / (3 * math.sqrt(3)), 4.0 / 9.0, "query-coded-doc"),
    (0.5, -0.3, 0.05, "negative-rho"),
]


def run_cap_forms():
    for (u, rho, t, label) in D_CASES:
        a, b = cap_cs(u, rho)
        c, d = cap_angle(u, rho)
        e, f = cap_gram(u, rho)
        check("D.agree." + label, abs(a - c) < 1e-12 and abs(b - d) < 1e-12
              and abs(a - e) < 1e-12 and abs(b - f) < 1e-12,
              "cs=[%.12f,%.12f] angle=[%.12f,%.12f] gram=[%.12f,%.12f]"
              % (a, b, c, d, e, f))
        check("D.contains." + label, a - 1e-12 <= t <= b + 1e-12,
              "t=%.6f in [%.6f,%.6f] width=%.4f" % (t, a, b, b - a))


# ---------------- Section E: quantized scalar payload + top-3 certificate ----------------
K_BITS = 8
K_HALF = 1.0 / 255.0 + 1e-12  # half-LSB of uniform 8-bit code on [-1,1] + fp slack


def qenc(rho):
    m = int(round((rho + 1.0) * 255.0 / 2.0))
    return min(255, max(0, m))


def qdec(m):
    return m / 255.0 * 2.0 - 1.0


def cert_interval(u, rho_true):
    """Conservative [L,U] for quantized rho: min/max over the decode
    interval, including interior stationary points -/+u of L/U."""
    m = qenc(rho_true)
    r0 = qdec(m)
    lo, hi = max(-1.0, r0 - K_HALF), min(1.0, r0 + K_HALF)
    cands_L = [lo, hi] + ([-u] if lo <= -u <= hi else [])
    cands_U = [lo, hi] + ([u] if lo <= u <= hi else [])
    L = min(cap_cs(u, r)[0] for r in cands_L)
    U = max(cap_cs(u, r)[1] for r in cands_U)
    return L, U, m


def worst_rank(L, U, i):
    """Adversarial-tie worst-case rank of i: 1 + #{j != i: U_j >= L_i}."""
    return 1 + sum(1 for j in range(len(L)) if j != i and U[j] >= L[i] - 1e-12)


def run_top3():
    import numpy as np
    q = np.array([0.5, 0.5, 0.5, 0.5])
    s = (1, 1, 1, 1)
    c = np.array([0.5, 0.5, 0.5, 0.5])
    docs = [
        np.array([0.5, 0.5, 0.5, 0.5]),
        (q + np.array([0.05, -0.05, 0.0, 0.0])),
        (q + np.array([0.10, 0.0, -0.10, 0.0])),
        np.array([1.0, 0.0, 0.0, 0.0]),
        np.array([1.0, 1.0, 0.0, 0.0]) / math.sqrt(2),
        np.array([1.0, 1.0, 1.0, 0.0]) / math.sqrt(3),
    ]
    docs = [v / np.linalg.norm(v) for v in docs]
    true_t = [float(q @ v) for v in docs]
    true_rho = [float(c @ v) for v in docs]
    # Sign-only intervals are IDENTICAL for all six (same pattern, same query).
    esup, einf = sup_val_float(s, (Fr(1, 2),) * 4), inf_val_float(s, (Fr(1, 2),) * 4)
    check("E.signonly-vacuous", abs(esup - 1.0) < 1e-12 and abs(einf - 0.5) < 1e-12,
          "all six share (0.5,1]: no pair certifiable from signs alone")
    Ls, Us, ms = [], [], []
    for j, (rho, t) in enumerate(zip(true_rho, true_t)):
        u = float(q @ c)
        L, U, m = cert_interval(u, rho)
        Ls.append(L)
        Us.append(U)
        ms.append(m)
        a, b = cap_cs(u, rho)
        check("E.contain.d%d" % (j + 1), L <= a + 1e-12 and b - 1e-12 <= U
              and L - 1e-12 <= t <= U + 1e-12,
              "true t=%.6f exact-cap=[%.6f,%.6f] cert=[%.6f,%.6f] m=%d"
              % (t, a, b, L, U, m))
    ok = all(Ls[i] > Us[j] for i in range(3) for j in range(3, 6))
    check("E.top3-certified", ok,
          "L1..3=[%s] U4..6=[%s]" % (["%.4f" % v for v in Ls[:3]],
                                     ["%.4f" % v for v in Us[3:]]))
    wr = [worst_rank(Ls, Us, i) for i in range(6)]
    check("E.worst-rank", all(r <= 3 for r in wr[:3]),
          "worst-ranks=%s (adversarial ties)" % wr)
    check("E.true-order", true_t[0] > true_t[1] > true_t[2] > true_t[5] > true_t[4] > true_t[3],
          "true scores=%s" % ["%.5f" % v for v in true_t])
    # Failure case: scalar near the cap equator stays vacuous.
    u, rho, t = D_CASES[2][0], D_CASES[2][1], D_CASES[2][2]
    a, b = cap_cs(u, rho)
    check("E.failure-wide", (b - a) >= 1.0,
          "width=%.4f: scalar adds nothing over sign-only here" % (b - a))
    Lf, Uf, _ = cert_interval(u, rho)
    check("E.failure-cert", Lf <= a + 1e-12 and b - 1e-12 <= Uf,
          "quantized cert [%.4f,%.4f] still vacuous" % (Lf, Uf))


# ---------------- Section F: query also sign-coded (frozen native protocol) ----------------
def run_query_coded():
    import numpy as np
    q = np.array([1.0, 2.0, 2.0]) / 3.0
    qhat = np.array([1.0, 1.0, 1.0]) / math.sqrt(3)
    x = np.array([2.0, 2.0, -1.0]) / 3.0
    c = np.array([1.0, 1.0, -1.0]) / math.sqrt(3)
    th_q = math.acos(min(1.0, max(-1.0, float(q @ qhat))))
    al = math.acos(min(1.0, max(-1.0, float(x @ c))))
    gam = math.acos(min(1.0, max(-1.0, float(qhat @ c))))
    t = float(q @ x)
    lo = math.cos(min(math.pi, th_q + gam + al))
    hi = math.cos(max(0.0, gam - th_q - al))
    check("F.joint-valid", lo - 1e-12 <= t <= hi + 1e-12,
          "t=%.6f in [%.6f,%.6f]; th_q=%.2fdeg gam=%.2fdeg al=%.2fdeg"
          % (t, lo, hi, math.degrees(th_q), math.degrees(gam), math.degrees(al)))
    # Hamming identity (exact): qhat.c == (2A-d)/d with zero-convention +1 codes.
    sq = [1 if v >= 0 else -1 for v in q]
    sx = [1 if v >= 0 else -1 for v in x]
    A = sum(1 for a, b in zip(sq, sx) if a == b)
    check("F.hamming-identity", abs(float(qhat @ c) - (2 * A - 3) / 3.0) < 1e-12,
          "code-cosine=%.6f A=%d/3" % (float(qhat @ c), A))
    # What is computable where: rho from doc alone; th_q,beta from query at query time.
    check("F.info-split", abs(float(x @ c) - 5.0 / (3 * math.sqrt(3))) < 1e-12
          and abs(th_q - math.acos(5.0 / (3 * math.sqrt(3)))) < 1e-12,
          "rho doc-side; theta_q query-side; gamma codes-only")


# ---------------- Section G: seeded false variants (must fail FOR THESE REASONS) ----------------
def run_seeded_falses():
    # F1 (CLOSED-SET FALLACY): "closure maximizer always lies in F(s)".
    sB, qB = (1, -1), (Fr(3, 5), Fr(4, 5))
    pB = proj_cone(sB, qB)
    nB = math.sqrt(float(vnorm2(pB)))
    ystar = [float(v) / nB for v in pB]  # (1,0)
    broken_holds = member_F(sB, [Fr(ystar[0]).limit_denominator(10**12),
                                 Fr(ystar[1]).limit_denominator(10**12)])
    check("G.F1-closed-fallacy-refuted", (not broken_holds) and ystar[1] == 0.0,
          "reason=OPEN_BOUNDARY: y*=(1,0) attains closure sup 3/5 but x2=0 violates s2=-1")
    # F2 (HAMMING-ORDERS-COSINE): "more agreements => higher cosine".
    agree2_score, agree1_score = 0.6, (0.6 * -0.01 + 0.8) / math.sqrt(1.0001)
    check("G.F2-hamming-fallacy-refuted", agree1_score > agree2_score,
          "reason=RANK_FLIP: 1-agreement %.6f beats 2-agreement 0.6" % agree1_score)
    # F3 (FREE-LUNCH QUANTIZATION): "8-bit rho payload is exact".
    rhos = [0.99751, 0.99015, 0.5, 1.0 / math.sqrt(2)]
    inexact = any(qdec(qenc(r)) != r for r in rhos)
    check("G.F3-quant-not-exact", inexact,
          "reason=ROUNDING: decode(qenc(rho))!=rho; interval widening mandatory")


# ---------------- Section H: real-data illustration (read-only transcription check) ----------------
def run_lme_illustration():
    # Values transcribed from .../audit_real_geometry/COORDINATOR_LME_WITNESS.json (t=4 row).
    gold_dot, rival_dot = 1.0299795949628008, 1.0467211966244094
    gold_cos, rival_cos = 0.5457381205243765, 0.539025678888817
    check("H.numerator-insufficient", gold_dot < rival_dot and gold_cos > rival_cos,
          "gold dot %.14f < rival %.14f yet gold cos %.14f > rival %.14f: "
          "normalization essential" % (gold_dot, rival_dot, gold_cos, rival_cos))


def main():
    run_d2_sweep()
    run_d3_sweep()
    run_flip_witness()
    run_cap_forms()
    run_top3()
    run_query_coded()
    run_seeded_falses()
    run_lme_illustration()
    npass = sum(1 for c in CHECKS if c["pass"])
    nfail = len(CHECKS) - npass
    key = {
        "d2_sup_s(1,1)_q(3/5,4/5)": sup_val_float((1, 1), (Fr(3, 5), Fr(4, 5))),
        "d2_inf_s(1,1)_q(3/5,4/5)": inf_val_float((1, 1), (Fr(3, 5), Fr(4, 5))),
        "d2_sup_s(1,-1)_q(3/5,4/5)": sup_val_float((1, -1), (Fr(3, 5), Fr(4, 5))),
        "d2_inf_s(1,-1)_q(3/5,4/5)": inf_val_float((1, -1), (Fr(3, 5), Fr(4, 5))),
        "flip_1agree_vs_2agree": [(0.6 * -0.01 + 0.8) / math.sqrt(1.0001), 0.6],
        "lme_t4": {"gold_dot": 1.0299795949628008, "rival_dot": 1.0467211966244094,
                   "gold_cos": 0.5457381205243765, "rival_cos": 0.539025678888817},
    }
    print("%d/%d checks passed" % (npass, len(CHECKS)), flush=True)
    with open("results.json", "w") as f:
        json.dump({"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                              "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
                   "passed": npass, "total": len(CHECKS), "failed": nfail,
                   "key_numbers": key, "checks": CHECKS}, f, indent=1)
    return 0 if nfail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

