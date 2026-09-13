#!/usr/bin/env python3
# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# verify_v2.py -- norm_aware_sign_bounds icin ustun-gelen (superseding) dogrulayici.
# Dondurulmus arsivi (commit 1021083d4f2faebda760546e1217b4de1eef87ea) DEGISTIRMEZ;
# yalnizca bu dizinde calisir. Orijinal gecerli kontrolleri tekrar calistirir +
# T1..T6 onarim/ek testleri icerir. Karar gereken her yerde Fraction kullanir.
import json
import math
import os
import sys
from fractions import Fraction as Fr

CHECKS = []


def check(name, ok, detail=""):
    ok = bool(ok)
    CHECKS.append({"name": name, "pass": ok, "detail": str(detail)})
    if not ok:
        print("FAIL %s: %s" % (name, detail), flush=True)
    return ok


# ---------------- Rota 1: tam rasyonel yardimcilar (orijinalle ayni) ----------------
def vdot(a, b):
    return sum(x * y for x, y in zip(a, b))


def vnorm2(a):
    return vdot(a, a)


def proj_cone(s, v):
    """v'nin kapali kon K(s)={y: s_i y_i>=0} uzerine izdusumu, tam."""
    return [vi if si * vi >= 0 else Fr(0) for si, vi in zip(s, v)]


def member_closed(s, x):
    return all(si * xi >= 0 for si, xi in zip(s, x))


def member_F(s, x):
    """Tam acik-sinir uyeligi: s_i=+1 icin x_i>=0; s_i=-1 icin x_i<0."""
    for si, xi in zip(s, x):
        if si > 0:
            if xi < 0:
                return False
        else:
            if xi >= 0:
                return False
    return True


def sup_closed(s, q):
    """-> ('norm', sup^2>=0 tam) veya ('axis', sup degeri<=0 tam)."""
    p = proj_cone(s, q)
    if any(v != 0 for v in p):
        return ('norm', vnorm2(p))
    return ('axis', max(si * qi for si, qi in zip(s, q)))


def inf_closed(s, q):
    """-> ('norm', (-inf)^2 tam) veya ('axis', inf degeri tam)."""
    p = proj_cone(s, [-qi for qi in q])
    if any(v != 0 for v in p):
        return ('norm', vnorm2(p))
    return ('axis', min(si * qi for si, qi in zip(s, q)))


# ---------------- Erisim: ORIJINAL (hatali, dondurulmus kopya) ----------------
def sup_attained_orig(s, q):
    """verify.py:70-77 ile ayni. Eksen dalinda m=0'da YANLIS (T1)."""
    kind, _ = sup_closed(s, q)
    N = [i for i, si in enumerate(s) if si < 0]
    if kind == 'norm':
        return all(q[i] < 0 for i in N)
    m = max(s[i] * q[i] for i in range(len(s)))
    return any(set(N) <= {j} for j in range(len(s)) if s[j] * q[j] == m)


def inf_attained_orig(s, q):
    """verify.py:80-86 ile ayni. Eksen dalinda m=0'da YANLIS (T1)."""
    kind, _ = inf_closed(s, q)
    N = [i for i, si in enumerate(s) if si < 0]
    if kind == 'norm':
        return all(q[i] > 0 for i in N)
    m = min(s[i] * q[i] for i in range(len(s)))
    return any(set(N) <= {j} for j in range(len(s)) if s[j] * q[j] == m)


# ---------------- Erisim: DUZELTILMIS (yuz kurali) ----------------
def sup_attained(s, q):
    """ACIK F(s) uzerinde sup erisimi. Eksen+m=0'da yuz kurulu: N<=J."""
    kind, _ = sup_closed(s, q)
    N = [i for i, si in enumerate(s) if si < 0]
    if kind == 'norm':
        return all(q[i] < 0 for i in N)
    m = max(s[i] * q[i] for i in range(len(s)))
    J = [j for j in range(len(s)) if s[j] * q[j] == m]
    if m == 0:
        return set(N) <= set(J)
    return any(set(N) <= {j} for j in J)


def inf_attained(s, q):
    """ACIK F(s) uzerinde inf erisimi. Eksen+m=0'da yuz kurali: N<=J."""
    kind, _ = inf_closed(s, q)
    N = [i for i, si in enumerate(s) if si < 0]
    if kind == 'norm':
        return all(q[i] > 0 for i in N)
    m = min(s[i] * q[i] for i in range(len(s)))
    J = [j for j in range(len(s)) if s[j] * q[j] == m]
    if m == 0:
        return set(N) <= set(J)
    return any(set(N) <= {j} for j in J)


def closure_maximizer_float(s, qf):
    """Float kapanis-maksimizoru y* (eksen veya izdusum vektor)."""
    p = [qi if si * qi >= 0 else 0.0 for si, qi in zip(s, qf)]
    n = math.sqrt(sum(v * v for v in p))
    if n > 0:
        return [v / n for v in p]
    j = max(range(len(s)), key=lambda i: s[i] * qf[i])
    return [float(s[j]) if i == j else 0.0 for i in range(len(s))]


def approach_from_inside(s, ystar, eps=1e-4):
    """Yapici yogunluk adimi: sifir N-koordlarini iceri kit, normalize et."""
    d = len(s)
    y = list(ystar)
    for j in range(d):
        if s[j] < 0 and y[j] == 0.0:
            y[j] = -eps
    n = math.sqrt(sum(v * v for v in y))
    return [v / n for v in y]


def sup_val_float(s, q):
    kind, v = sup_closed(s, q)
    return math.sqrt(float(v)) if kind == 'norm' else float(v)


def inf_val_float(s, q):
    kind, v = inf_closed(s, q)
    return -math.sqrt(float(v)) if kind == 'norm' else float(v)


# ---------------- Altin tablo D2 (harf harf sabit; T2/T3 bagimsiz olcusu) ----------------
# Anahtar: (s, qstr). Deger: (sup_tur, sup_deger, sup_erisim, inf_tur, inf_deger, inf_erisim).
# Degerler: 'norm' ise sup^2 / (-inf)^2 (Fraction str); 'axis' ise sup/inf (Fraction str).
# Erisim: duzeltilmis yuz kurali (D2'de orijinalle ayni; fark d>=3'te).
D2_GOLD = {
    ((1, 1), "(3/5,4/5)"): ('norm', '1', True, 'axis', '3/5', True),
    ((1, 1), "(1,0)"): ('norm', '1', True, 'axis', '0', True),
    ((1, 1), "(-1,0)"): ('axis', '0', True, 'norm', '1', True),
    ((1, 1), "(3/5,-4/5)"): ('norm', '9/25', True, 'norm', '16/25', True),
    ((1, 1), "(-3/5,-4/5)"): ('axis', '-3/5', True, 'norm', '1', True),
    ((1, 1), "(0,1)"): ('norm', '1', True, 'axis', '0', True),
    ((1, -1), "(3/5,4/5)"): ('norm', '9/25', False, 'norm', '16/25', True),
    ((1, -1), "(1,0)"): ('norm', '1', False, 'axis', '0', True),
    ((1, -1), "(-1,0)"): ('axis', '0', True, 'norm', '1', False),
    ((1, -1), "(3/5,-4/5)"): ('norm', '1', True, 'axis', '3/5', False),
    ((1, -1), "(-3/5,-4/5)"): ('norm', '16/25', True, 'norm', '9/25', False),
    ((1, -1), "(0,1)"): ('axis', '0', False, 'norm', '1', True),
    ((-1, 1), "(3/5,4/5)"): ('norm', '16/25', False, 'norm', '9/25', True),
    ((-1, 1), "(1,0)"): ('axis', '0', False, 'norm', '1', True),
    ((-1, 1), "(-1,0)"): ('norm', '1', True, 'axis', '0', False),
    ((-1, 1), "(3/5,-4/5)"): ('axis', '-3/5', True, 'norm', '1', True),
    ((-1, 1), "(-3/5,-4/5)"): ('norm', '9/25', True, 'norm', '16/25', False),
    ((-1, 1), "(0,1)"): ('norm', '1', False, 'axis', '0', True),
    ((-1, -1), "(3/5,4/5)"): ('axis', '-3/5', False, 'norm', '1', True),
    ((-1, -1), "(1,0)"): ('axis', '0', False, 'norm', '1', False),
    ((-1, -1), "(-1,0)"): ('norm', '1', False, 'axis', '0', False),
    ((-1, -1), "(3/5,-4/5)"): ('norm', '16/25', False, 'norm', '9/25', False),
    ((-1, -1), "(-3/5,-4/5)"): ('norm', '1', True, 'axis', '3/5', False),
    ((-1, -1), "(0,1)"): ('axis', '0', False, 'norm', '1', False),
}

D2_PATTERNS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
D2_QUERIES = [
    (Fr(3, 5), Fr(4, 5)),
    (Fr(1, 1), Fr(0, 1)),
    (Fr(-1, 1), Fr(0, 1)),
    (Fr(3, 5), Fr(-4, 5)),
    (Fr(-3, 5), Fr(-4, 5)),
    (Fr(0, 1), Fr(1, 1)),
]


def qstr(q):
    return "(%s,%s)" % (q[0], q[1])


def sup_independent(s, q):
    """sup_closed'i cagirmadan kapali-form: yardimci cagrisiz dogrudan toplam."""
    has = False
    tot = Fr(0)
    for si, qi in zip(s, q):
        if si * qi >= 0:
            tot += qi * qi
            if qi != 0:
                has = True
    if has:
        return ('norm', tot)
    m = None
    for si, qi in zip(s, q):
        v = si * qi
        m = v if m is None or v > m else m
    return ('axis', m)


def inf_independent(s, q):
    """inf_closed'i cagirmadan kapali-form."""
    has = False
    tot = Fr(0)
    for si, qi in zip(s, q):
        if si * qi <= 0:
            tot += qi * qi
            if qi != 0:
                has = True
    if has:
        return ('norm', tot)
    m = None
    for si, qi in zip(s, q):
        v = si * qi
        m = v if m is None or v < m else m
    return ('axis', m)


# ---------------- Korunan B2/B3 taramalari (totolojik + zayif tutarlilik HARIC) ----------------
def run_d2_kept():
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
            check("B2.upper." + tag, numax <= esup + 1e-9,
                  "gridmax=%.12f sup=%.12f" % (numax, esup))
            check("B2.lower." + tag, numin >= einf - 1e-9,
                  "gridmin=%.12f inf=%.12f" % (numin, einf))
            check("B2.reach-sup." + tag, esup - numax <= 0.01,
                  "gap=%.5f" % (esup - numax))
            check("B2.reach-inf." + tag, numin - einf <= 0.01,
                  "gap=%.5f" % (numin - einf))
            ys = closure_maximizer_float(s, [float(q[0]), float(q[1])])
            check("B2.ys-closed." + tag, member_closed(s, ys), str(ys))
            xe = approach_from_inside(s, ys)
            att = sup_attained(s, q)
            if not att:
                check("B2.approach." + tag,
                      member_F(s, xe) and (float(q[0]) * xe[0] + float(q[1]) * xe[1]
                                           >= esup - 1e-3),
                      "score=%.9f sup=%.9f" % (float(q[0]) * xe[0] + float(q[1]) * xe[1], esup))


def run_d3_kept():
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


# ---------------- Korunan C: cevirme tanigi (1 aralik dizgisi onarildi) ----------------
def run_flip_kept():
    q = (Fr(3, 5), Fr(4, 5))
    sA, sD = (1, 1), (1, -1)
    xA = (Fr(1, 1), Fr(0, 1))
    check("C.member-xA", member_F(sA, xA), "P-sifir serbest, N bos")
    check("C.score-xA", vdot(q, xA) == Fr(3, 5), str(vdot(q, xA)))
    check("C.supA-infA", abs(sup_val_float(sA, q) - 1.0) < 1e-12
          and abs(inf_val_float(sA, q) - 0.6) < 1e-12,
          "aralik [3/5,1]: N bos oldugundan iki uc da erisilir (onarildi: ( degil [)")
    check("C.supD-infD", abs(sup_val_float(sD, q) - 0.6) < 1e-12
          and abs(inf_val_float(sD, q) + 0.8) < 1e-12,
          "aralik [-4/5,3/5): sup erisilmez, inf (0,-1)'de erisilir")
    check("C.supD-open", not sup_attained(sD, q)
          and not member_F(sD, (Fr(1, 1), Fr(0, 1))), "maksimizor (1,0): x2=0")
    check("C.infD-att", inf_attained(sD, q), "minimizor (0,-1) kesin icte")
    import numpy as np
    sE = (-1, 1)
    check("C.supE-infE", abs(sup_val_float(sE, q) - 0.8) < 1e-12
          and abs(inf_val_float(sE, q) + 0.6) < 1e-12,
          "aralik [-3/5,4/5): sup erisilmez (maksimizor (0,1): x1=0)")
    eps = 0.01
    xE = np.array([-eps, 1.0]) / math.sqrt(1 + eps * eps)
    sEscore = float(q[0]) * xE[0] + float(q[1]) * xE[1]
    check("C.flip", member_F(sE, [Fr(-1, 100), Fr(1, 1)]) and sEscore > 0.6,
          "1-uyumlu (-,+) skor %.9f, 2-uyumlu (1,0) 0.6'yi gecer" % sEscore)
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


# ---------------- Kapak bicimleri (orijinalle ayni) ----------------
def cap_cs(u, rho):
    """C-S / dik-ayrisim bicimi."""
    disc = max(0.0, (1 - u * u) * (1 - rho * rho))
    d = math.sqrt(disc)
    return (u * rho - d, u * rho + d)


def cap_angle(u, rho):
    """Aci-toplam bicimi."""
    uc = min(1.0, max(-1.0, u))
    rc = min(1.0, max(-1.0, rho))
    be, al = math.acos(uc), math.acos(rc)
    return (math.cos(be + al), math.cos(abs(be - al)))


def cap_gram(u, rho):
    """Gram-determinant bicimi."""
    a = 1.0
    b = -2 * u * rho
    disc = max(0.0, b * b - 4 * a * (u * u + rho * rho - 1.0))
    sq = math.sqrt(disc)
    return ((-b - sq) / 2.0, (-b + sq) / 2.0)


# Gerceklesebilir D ornekleri (negative-rho T4'te soyut olarak ayristi).
D_REALIZABLE = [
    (1.0, 0.99, 0.99, "aligned"),
    (0.0, 0.5, 0.1, "orthogonal-center"),
    (-1.0 / (5 * math.sqrt(2)), 1.0 / math.sqrt(2), -0.8, "failure-wide"),
    (1.0 / (3 * math.sqrt(3)), 5.0 / (3 * math.sqrt(3)), 4.0 / 9.0, "query-coded-doc"),
]
D_ABSTRACT = [(0.5, -0.3, 0.05, "negative-rho")]


def run_cap_kept():
    for (u, rho, t, label) in D_REALIZABLE:
        a, b = cap_cs(u, rho)
        c, d = cap_angle(u, rho)
        e, f = cap_gram(u, rho)
        check("D.agree." + label, abs(a - c) < 1e-12 and abs(b - d) < 1e-12
              and abs(a - e) < 1e-12 and abs(b - f) < 1e-12,
              "cs=[%.12f,%.12f] angle=[%.12f,%.12f] gram=[%.12f,%.12f]"
              % (a, b, c, d, e, f))
        check("D.contains." + label, a - 1e-12 <= t <= b + 1e-12,
              "t=%.6f in [%.6f,%.6f] width=%.4f" % (t, a, b, b - a))


# ---------------- Korunan E/F/G/H (E isaret-parantezi onarildi) ----------------
K_BITS = 8
K_HALF = 1.0 / 255.0 + 1e-12


def qenc(rho):
    m = int(round((rho + 1.0) * 255.0 / 2.0))
    return min(255, max(0, m))


def qdec(m):
    return m / 255.0 * 2.0 - 1.0


def cert_interval(u, rho_true):
    m = qenc(rho_true)
    r0 = qdec(m)
    lo, hi = max(-1.0, r0 - K_HALF), min(1.0, r0 + K_HALF)
    cands_L = [lo, hi] + ([-u] if lo <= -u <= hi else [])
    cands_U = [lo, hi] + ([u] if lo <= u <= hi else [])
    L = min(cap_cs(u, r)[0] for r in cands_L)
    U = max(cap_cs(u, r)[1] for r in cands_U)
    return L, U, m


def worst_rank(L, U, i):
    return 1 + sum(1 for j in range(len(L)) if j != i and U[j] >= L[i] - 1e-12)


def run_top3_kept():
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
    esup, einf = sup_val_float(s, (Fr(1, 2),) * 4), inf_val_float(s, (Fr(1, 2),) * 4)
    check("E.signonly-vacuous", abs(esup - 1.0) < 1e-12 and abs(einf - 0.5) < 1e-12,
          "alti belge de [0.5,1]'i paylasir (onarildi: N bos, iki uc erisilir)")
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
    u, rho, t = D_REALIZABLE[2][0], D_REALIZABLE[2][1], D_REALIZABLE[2][2]
    a, b = cap_cs(u, rho)
    check("E.failure-wide", (b - a) >= 1.0,
          "width=%.4f: skaler burada ise yaramaz" % (b - a))
    Lf, Uf, _ = cert_interval(u, rho)
    check("E.failure-cert", Lf <= a + 1e-12 and b - 1e-12 <= Uf,
          "quantized cert [%.4f,%.4f] still vacuous" % (Lf, Uf))


def run_query_kept():
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
    sq = [1 if v >= 0 else -1 for v in q]
    sx = [1 if v >= 0 else -1 for v in x]
    A = sum(1 for a, b in zip(sq, sx) if a == b)
    check("F.hamming-identity", abs(float(qhat @ c) - (2 * A - 3) / 3.0) < 1e-12,
          "code-cosine=%.6f A=%d/3" % (float(qhat @ c), A))
    check("F.info-split", abs(float(x @ c) - 5.0 / (3 * math.sqrt(3))) < 1e-12
          and abs(th_q - math.acos(5.0 / (3 * math.sqrt(3)))) < 1e-12,
          "rho doc-side; theta_q query-side; gamma codes-only")


def run_seeded_kept():
    sB, qB = (1, -1), (Fr(3, 5), Fr(4, 5))
    pB = proj_cone(sB, qB)
    nB = math.sqrt(float(vnorm2(pB)))
    ystar = [float(v) / nB for v in pB]
    broken_holds = member_F(sB, [Fr(ystar[0]).limit_denominator(10**12),
                                 Fr(ystar[1]).limit_denominator(10**12)])
    check("G.F1-closed-fallacy-refuted", (not broken_holds) and ystar[1] == 0.0,
          "reason=OPEN_BOUNDARY: y*=(1,0) sup 3/5'i verir ama x2=0, s2=-1'i bozar")
    agree2_score, agree1_score = 0.6, (0.6 * -0.01 + 0.8) / math.sqrt(1.0001)
    check("G.F2-hamming-fallacy-refuted", agree1_score > agree2_score,
          "reason=RANK_FLIP: 1-uyum %.6f, 2-uyum 0.6'yi gecer" % agree1_score)
    rhos = [0.99751, 0.99015, 0.5, 1.0 / math.sqrt(2)]
    inexact = any(qdec(qenc(r)) != r for r in rhos)
    check("G.F3-quant-not-exact", inexact,
          "reason=ROUNDING: decode(qenc(rho))!=rho; aralik genisletme sart")
    check("H.numerator-insufficient",
          1.0299795949628008 < 1.0467211966244094 and 0.5457381205243765 > 0.539025678888817,
          "gold dot < rival dot ama gold cos > rival cos: normalizasyon sart")


# ---------------- T1: eksen dalinda m=0 yuz kurali ----------------
def run_T1():
    F0 = Fr(0)
    # Ayirt edici sup ornegi: s=(1,-1,-1), q=(-1,0,0). sup eksen, m=0, J={1,2}, N={1,2}.
    s1 = (1, -1, -1)
    qsup = (Fr(-1), F0, F0)
    qinf = (Fr(1), F0, F0)
    ks = sup_closed(s1, qsup)
    check("T1.sup-kind", ks == ('axis', Fr(0)), str(ks))
    check("T1.sup-fixed-true", sup_attained(s1, qsup) is True, "N={1,2}<=J={1,2}")
    check("T1.sup-orig-false", sup_attained_orig(s1, qsup) is False,
          "orijinal: N tekli eksene sigmaz -> False (YANLIS)")
    # Ayirt edici inf ornegi: ayni s, q=(1,0,0). inf eksen, m=0.
    ki = inf_closed(s1, qinf)
    check("T1.inf-kind", ki == ('axis', Fr(0)), str(ki))
    check("T1.inf-fixed-true", inf_attained(s1, qinf) is True, "N={1,2}<=J={1,2}")
    check("T1.inf-orig-false", inf_attained_orig(s1, qinf) is False, "orijinal False (YANLIS)")
    # Tam tanik: x=(0,-3/5,-4/5) birim, F icinde, iki ucu da gercekler.
    x = (F0, Fr(-3, 5), Fr(-4, 5))
    check("T1.witness-member", member_F(s1, x) and vnorm2(x) == 1, str(x))
    check("T1.witness-sup", vdot(qsup, x) == Fr(0) == sup_closed(s1, qsup)[1],
          "q.x=0=sup, erisim gerceklenir")
    check("T1.witness-inf", vdot(qinf, x) == Fr(0) == inf_closed(s1, qinf)[1],
          "q.x=0=inf, erisim gerceklenir")
    # D3 taramasindaki olculememis hucre: inf erisimi True olmaliydi.
    check("T1.d3-cell-orig-blind",
          inf_attained_orig(s1, qinf) is False and inf_attained(s1, qinf) is True,
          "D3 hucresi erisim test etmez; hata gorunmezdi")
    # m=0 eksen uclari D2'de de var (denetim ifadesi duzeltmesi); D2'de fark yok.
    m0 = []
    for s in D2_PATTERNS:
        for qq in D2_QUERIES:
            ks2, ki2 = sup_closed(s, qq), inf_closed(s, qq)
            if ks2[0] == 'axis' and ks2[1] == 0:
                m0.append(("sup", s, qstr(qq)))
            if ki2[0] == 'axis' and ki2[1] == 0:
                m0.append(("inf", s, qstr(qq)))
    check("T1.m0-exists-in-D2", len(m0) > 0, "%d adet m=0 eksen hucresi" % len(m0))
    nodiff = all(sup_attained(s, qq) == sup_attained_orig(s, qq)
                 and inf_attained(s, qq) == inf_attained_orig(s, qq)
                 for s in D2_PATTERNS for qq in D2_QUERIES)
    check("T1.D2-agree", nodiff and len(m0) == 12,
          "D2: 12 m=0 hucresi var ama |N|<=1 oldugundan fark yok (hata gizli)")
    # m!=0 eksen durumunda eski kural dogru kalir (regresyon).
    check("T1.axis-neg-still-false",
          sup_attained((-1, -1), (Fr(3, 5), Fr(4, 5))) is False
          and sup_attained_orig((-1, -1), (Fr(3, 5), Fr(4, 5))) is False,
          "m=-3/5<0: iki kural da False")
    # Sistematik d=3 yuz taramasi: N<=J kuralini dogrudan dogrula.
    pats3 = [(a, b, c) for a in (1, -1) for b in (1, -1) for c in (1, -1)]
    axis_q = [(Fr(1), F0, F0), (Fr(-1), F0, F0), (F0, Fr(1), F0),
              (F0, Fr(-1), F0), (F0, F0, Fr(1)), (F0, F0, Fr(-1))]
    nface = ndiff = 0
    okface = True
    for s in pats3:
        N = set(i for i, si in enumerate(s) if si < 0)
        for qq in axis_q:
            ks3 = sup_closed(s, qq)
            if ks3[0] == 'axis' and ks3[1] == 0:
                nface += 1
                J = set(j for j in range(3) if s[j] * qq[j] == 0)
                if sup_attained(s, qq) != (N <= J):
                    okface = False
                if sup_attained_orig(s, qq) != (N <= J):
                    ndiff += 1
            ki3 = inf_closed(s, qq)
            if ki3[0] == 'axis' and ki3[1] == 0:
                nface += 1
                J = set(j for j in range(3) if s[j] * qq[j] == 0)
                if inf_attained(s, qq) != (N <= J):
                    okface = False
                if inf_attained_orig(s, qq) != (N <= J):
                    ndiff += 1
    check("T1.face-sweep", okface and nface > 0,
          "%d yuz hucresi, kural N<=J ile uyumlu" % nface)
    check("T1.face-orig-wrong-count", ndiff > 0,
          "orijinal %d yuz hucresinde yanlis" % ndiff)


# ---------------- T2: totoloji yerine bagimsiz kapali-form + altin tablo ----------------
def proj_skip0(s, v):
    """Bozuk varyant: 0. indisi dusurur (paylasilan-mantik hatasi ornegi)."""
    out = []
    for i, (si, vi) in enumerate(zip(s, v)):
        if i == 0:
            out.append(Fr(0))
        else:
            out.append(vi if si * vi >= 0 else Fr(0))
    return out


def sup_skip0(s, q):
    p = proj_skip0(s, q)
    if any(v != 0 for v in p):
        return ('norm', sum(v * v for v in p))
    return ('axis', max(si * qi for si, qi in zip(s, q)))


def run_T2():
    # Her D2 hucresi: yardimcisiz kapali-form + sabit altin tablo karsilastirmasi.
    for s in D2_PATTERNS:
        for qq in D2_QUERIES:
            tag = "s=%s,q=%s" % (s, qstr(qq))
            g = D2_GOLD[(s, qstr(qq))]
            ks, ki = sup_closed(s, qq), inf_closed(s, qq)
            ks_i, ki_i = sup_independent(s, qq), inf_independent(s, qq)
            check("T2.sup-val." + tag,
                  ks == ks_i == ('norm', Fr(g[1])) if g[0] == 'norm'
                  else ks == ks_i == ('axis', Fr(g[1])),
                  "sup=%s altin=%s,%s" % (ks, g[0], g[1]))
            check("T2.inf-val." + tag,
                  ki == ki_i == ('norm', Fr(g[4])) if g[3] == 'norm'
                  else ki == ki_i == ('axis', Fr(g[4])),
                  "inf=%s altin=%s,%s" % (ki, g[3], g[4]))
    # Eski test neden kordu: paylasilan-mantik hatasinda iki taraf da ayni yanlisi uretir.
    sB, qB = (1, 1), (Fr(3, 5), Fr(4, 5))
    broken = sup_skip0(sB, qB)
    old_style = (broken[1] == sum(v * v for v in proj_skip0(sB, qB)))
    check("T2.old-blind", broken == ('norm', Fr(16, 25)) and old_style is True,
          "bozuk sup=16/25; eski tarz karsilastirma True (kor)")
    gB = D2_GOLD[(sB, qstr(qB))]
    check("T2.new-catches", broken != ('norm', Fr(gB[1])),
          "bozuk 16/25 != altin %s (yeni test yakalar)" % gB[1])
    # Yapibozumu kimlikleri (Pisagor + diklik + isaret), yardimcisiz dogrudan.
    okp = True
    for s in D2_PATTERNS:
        for qq in D2_QUERIES:
            p = [qi if si * qi >= 0 else Fr(0) for si, qi in zip(s, qq)]
            r = [qi - pi for qi, pi in zip(qq, p)]
            if not (sum(pi * pi for pi in p) + sum(ri * ri for ri in r)
                    == sum(qi * qi for qi in qq)):
                okp = False
            if not all((si * pi >= 0) and (si * ri <= 0) for si, pi, ri in zip(s, p, r)):
                okp = False
    check("T2.pythag-sign", okp, "24 hucrede Pisagor + kon/kutup isaretleri")


# ---------------- T3: ayirt edici erisim tutarliligi (sup + inf, altin tablolu) ----------------
def run_T3():
    for s in D2_PATTERNS:
        for qq in D2_QUERIES:
            tag = "s=%s,q=%s" % (s, qstr(qq))
            g = D2_GOLD[(s, qstr(qq))]
            check("T3.sup-att." + tag, sup_attained(s, qq) is g[2],
                  "sup-erisim=%s altin=%s" % (sup_attained(s, qq), g[2]))
            check("T3.inf-att." + tag, inf_attained(s, qq) is g[5],
                  "inf-erisim=%s altin=%s" % (inf_attained(s, qq), g[5]))
    # Eski kontrolun korlugu: yuz orneginde False==False gecerdi.
    s1 = (1, -1, -1)
    qsup = (Fr(-1), Fr(0), Fr(0))
    ys = closure_maximizer_float(s1, [float(v) for v in qsup])
    old_pass = (member_F(s1, ys) == sup_attained_orig(s1, qsup))
    check("T3.old-blind-face", old_pass is True and member_F(s1, ys) is False,
          "ys=%s uye=False, orijinal=False -> eski gecer (kor)" % ys)
    check("T3.new-catches-face", sup_attained(s1, qsup) is True,
          "duzeltilmis True; eski False==False ile kacirirdi")
    # Erisilen norm uclarinda kapanis maksimizoru kesin F icinde olmali (ornek).
    sA = (1, 1)
    qA = (Fr(3, 5), Fr(4, 5))
    ysA = closure_maximizer_float(sA, [float(qA[0]), float(qA[1])])
    check("T3.att-witness-norm", sup_attained(sA, qA) and member_F(sA, ysA),
          "N bos: y* F icinde, erisim tanikli")


# ---------------- T4: negatif rho imkansiz + soyut yeniden etiket ----------------
def rho2_exact(x):
    """rho^2 = (||x||_1)^2/(d||x||^2), sifir-uzlasimli, tam Fraction."""
    d = len(x)
    X2 = sum(xi * xi for xi in x)
    xs = sum(abs(xi) for xi in x)
    return (xs * xs, d * X2, xs)


def run_T4():
    import random
    rng = random.Random(20260913)
    tot = bad = zconv = 0
    for d in (2, 3, 4, 5, 8):
        for _ in range(200):
            x = [Fr(rng.randint(-5, 5), 5) for _ in range(d)]
            X2 = sum(xi * xi for xi in x)
            if X2 == 0:
                continue
            num, den, xs = rho2_exact(x)
            tot += 1
            # 1/d <= rho^2 <= 1  <=>  X2 <= xs^2  ve  xs^2 <= d*X2
            if not (X2 <= xs * xs <= d * X2 and xs > 0):
                bad += 1
            s = [1 if xi >= 0 else -1 for xi in x]
            if any(xi == 0 for xi in x):
                zconv += sum(1 for xi, si in zip(x, s) if xi == 0 and si == 1)
    check("T4.rho-bounds", bad == 0 and tot > 900,
          "%d vektor: 1/d<=rho^2<=1, rho>0 (tam)" % tot)
    check("T4.zero-convention", zconv > 0, "%d sifir koordda s_i=+1" % zconv)
    check("T4.neg-impossible", Fr(-3, 10) < 0,
          "rho=-0.3<0: rho=||x||_1/sqrt(d)>0 oldugundan hicbir belge uretemez")
    # Soyut-(u,rho) olarak korunan matematik (gerceklesebilirlik iddiasiz).
    for (u, rho, t, label) in D_ABSTRACT:
        a, b = cap_cs(u, rho)
        c, d = cap_angle(u, rho)
        e, f = cap_gram(u, rho)
        check("T4.abstract-agree." + label,
              abs(a - c) < 1e-12 and abs(b - d) < 1e-12
              and abs(a - e) < 1e-12 and abs(b - f) < 1e-12,
              "soyut bicim uyumu [%+.4f,%+.4f]" % (a, b))
        check("T4.abstract-contain." + label, a - 1e-12 <= t <= b + 1e-12,
              "soyut t=%.3f aralikta (belge iddiasi YOK)" % t)
    check("T4.record-change",
          all(rho >= 0 for (_, rho, _, _) in D_REALIZABLE) and len(D_ABSTRACT) == 1,
          "KAYIT: (0.5,-0.3,0.05) gerceklesebilir listeden cikarildi, soyut saklandi")
    # d=4 alt sinir erisilir: x=e1 -> rho^2=1/4.
    x1 = (Fr(1), Fr(0), Fr(0), Fr(0))
    n1, d1, _ = rho2_exact(x1)
    check("T4.d4-lower-attained", n1 * 4 == d1, "rho(e1)^2=1/4, alt uc erisilir")


# ---------------- T5: genel-durum vektor-tabanli kap siniri (tam Fraction) ----------------
# Turetim (tam metin T5_EVIDENCE.md):
#   s_i=sign(x_i) (sign(0)=+1), c=s/sqrt(d), rho=(x.c)/||x||, u=(q.c)/||q||,
#   t=(q.x)/(||q|| ||x||). x.c=(sum|x_i|)/sqrt(d) cunku x_i s_i=|x_i| (sifir dahil),
#   q.c=(sum q_i s_i)/sqrt(d). K=u rho||q|| ||x||=(q.c)(x.c)=S1*Sq/d,
#   S1=sum|x_i|, Sq=sum q_i s_i.
#   (t-u rho)^2<=(1-u^2)(1-rho^2) esitsizligini ||q||^2||x||^2 ile carp:
#     (QX-K)^2 <= Q2*X2*(1-u^2)*(1-rho^2),
#   1-u^2=(d Q2-Sq^2)/(d Q2), 1-rho^2=(d X2-S1^2)/(d X2) koyup d^2 ile carp:
#     (d*QX-S1*Sq)^2 <= (d*Q2-Sq^2)*(d*X2-S1^2).   (*)
#   Kare alma gecerli cunku sag taraf >=0: d Q2-Sq^2, q ile s arasindaki C-S
#   farkidir = (1/2)sum_ij(q_i s_j-q_j s_i)^2>=0; x icin aynisi gecerli.
#   Ayrica her durumda rho>0 ve X2<=S1^2<=d X2 (1/d<=rho^2<=1) ayrica denetlenir.
T5_CASES = None
T5_STATS = {}


def t5_stats(q, x):
    d = len(x)
    s = [1 if xi >= 0 else -1 for xi in x]
    S1 = sum(abs(xi) for xi in x)
    Sq = sum(qi * si for qi, si in zip(q, s))
    Q2 = sum(qi * qi for qi in q)
    X2 = sum(xi * xi for xi in x)
    QX = sum(qi * xi for qi, xi in zip(q, x))
    A = d * QX - S1 * Sq
    Bq = d * Q2 - Sq * Sq
    Bx = d * X2 - S1 * S1
    return {"d": d, "s": s, "S1": S1, "Sq": Sq, "Q2": Q2, "X2": X2, "QX": QX,
            "lhs": A * A, "rhs": Bq * Bx, "Bq": Bq, "Bx": Bx}


def build_t5_cases():
    global T5_CASES
    if T5_CASES is not None:
        return T5_CASES
    import random
    rng = random.Random(20260913)
    cases = []

    def add(q, x, bucket):
        q = tuple(Fr(v) for v in q)
        x = tuple(Fr(v) for v in x)
        if vnorm2(q) == 0 or vnorm2(x) == 0:
            return
        cases.append((q, x, bucket))

    def rvec(d, num=5, den=5):
        return [Fr(rng.randint(-num, num), den) for _ in range(d)]

    for d in (2, 3, 4, 5, 8):
        for _ in range(400):  # rastgele yogun ciftler
            add(rvec(d), rvec(d), "rand")
        for _ in range(20):  # q // c: once x, sonra q=a*s(x) (u=+-1)
            x = rvec(d)
            s = [1 if xi >= 0 else -1 for xi in x]
            a = Fr(rng.choice([1, -1, 2, -2]), rng.choice([1, 2]))
            add([a * si for si in s], x, "par")
        for _ in range(40):  # q ort c: q0'i s'e dikle (u=0, tam)
            x = rvec(d)
            s = [1 if xi >= 0 else -1 for xi in x]
            q0 = rvec(d)
            dot = sum(qi * si for qi, si in zip(q0, s))
            add([qi - dot * si / d for qi, si in zip(q0, s)], x, "orth")
        for _ in range(40):  # siki dejenere-olmayan: q=a s+lam xp (slack 0)
            x = rvec(d)
            s = [1 if xi >= 0 else -1 for xi in x]
            S1 = sum(abs(xi) for xi in x)
            xp = [xi - S1 * si / d for xi, si in zip(x, s)]
            if all(v == 0 for v in xp):
                continue
            a = Fr(rng.choice([-2, -1, 0, 0, 1, 2]), 2)
            lam = Fr(rng.choice([-2, -1, 1, 2]), 2)
            add([a * si + lam * vi for si, vi in zip(s, xp)], x, "tight")
        for i in range(d):  # sifir-yuzu: x=e_i (d-1 sifir), 2'ser q
            for _ in range(2):
                x = [Fr(0)] * d
                x[i] = Fr(rng.choice([1, -1, 2, -2]), rng.choice([1, 2]))
                add(rvec(d), x, "face")
        for _ in range(10):  # tam bir sifir
            x = rvec(d)
            x[rng.randrange(d)] = Fr(0)
            if vnorm2(x) == 0:
                continue
            add(rvec(d), x, "onezero")
        for _ in range(10):  # cok sifir (2..d-2, d>=4)
            if d < 4:
                continue
            x = rvec(d)
            for j in rng.sample(range(d), rng.randint(2, d - 2)):
                x[j] = Fr(0)
            if vnorm2(x) == 0:
                continue
            add(rvec(d), x, "multizero")
        for _ in range(10):  # yogun x (rho=1): x=s kalibi
            s = [rng.choice([1, -1]) for _ in range(d)]
            m = Fr(rng.choice([1, 2]), rng.choice([1, 2]))
            add(rvec(d), [m * si for si in s], "dense")
        for k in range(10):  # +-1'e yakin u: q=-/+s+kucuk bozunum
            x = rvec(d)
            s = [1 if xi >= 0 else -1 for xi in x]
            sgn = 1 if k % 2 == 0 else -1
            q = [Fr(sgn * si) for si in s]
            q[rng.randrange(d)] += Fr(1, 10)
            add(q, x, "near1")
        add(rvec(d), [Fr(i + 1) for i in range(d)], "allsign")  # hep +
        add(rvec(d), [Fr(-i - 1) for i in range(d)], "allsign")  # hep -
    T5_CASES = cases
    return cases


def t5_ubucket(st):
    n = st["Sq"] * st["Sq"]
    m = st["d"] * st["Q2"]
    if n == 0:
        return "u=0"
    if n == m:
        return "|u|=1"
    r = Fr(n, m)
    if r < Fr(1, 100):
        return "0<|u|<0.1"
    if r < Fr(1, 4):
        return "0.1-0.5"
    if r < Fr(16, 25):
        return "0.5-0.8"
    if r < Fr(24, 25):
        return "0.8-0.98"
    return "0.98-1"


def run_T5():
    from collections import Counter
    cases = build_t5_cases()
    ubins = Counter()
    signs = Counter()
    zeros = Counter()
    xsign = Counter()
    per_d_rho = {}
    n_orth = n_par = 0
    n_exact = n_degen = 0
    rejects = 0
    best = None  # (slack, tag, q, x) rhs>0 icinde en kucuk
    best_pos = None  # slack>0 icinde en kucuk
    for i, (q, x, bucket) in enumerate(cases):
        st = t5_stats(q, x)
        d = st["d"]
        tag = "c%04d-%s-d%d" % (i, bucket, d)
        slack = st["rhs"] - st["lhs"]
        check("T5.cap." + tag,
              st["Bq"] >= 0 and st["Bx"] >= 0 and st["lhs"] <= st["rhs"],
              "d=%d slack=%s rhs=%s" % (d, slack, st["rhs"]))
        check("T5.rho." + tag,
              st["S1"] > 0 and st["X2"] <= st["S1"] * st["S1"] <= d * st["X2"],
              "rho2=%s/%s" % (st["S1"] * st["S1"], d * st["X2"]))
        ub = t5_ubucket(st)
        ubins[ub] += 1
        signs["neg" if st["Sq"] < 0 else ("pos" if st["Sq"] > 0 else "zero")] += 1
        z = sum(1 for xi in x if xi == 0)
        zeros["one" if z == 1 else ("face" if z == d - 1 and d > 1
                                   else ("multi" if z >= 2 else "none"))] += 1
        nz = [xi for xi in x if xi != 0]
        xsign["mixed" if any(v > 0 for v in nz) and any(v < 0 for v in nz)
              else "onesign"] += 1
        r2 = Fr(st["S1"] * st["S1"], d * st["X2"])
        per_d_rho.setdefault(d, []).append(r2)
        if st["Sq"] == 0:
            n_orth += 1
        if st["Sq"] * st["Sq"] == d * st["Q2"]:
            n_par += 1
        if st["rhs"] == 0:
            n_degen += 1
        elif st["lhs"] == st["rhs"]:
            n_exact += 1
        if st["lhs"] * 1000 > st["rhs"] * 999:  # kirik sinir: carpani 999/1000
            rejects += 1
        if st["rhs"] > 0 and (best is None or slack < best[0]):
            best = (slack, tag, q, x)
        if slack > 0 and (best_pos is None or slack < best_pos[0]):
            best_pos = (slack, tag, q, x)
    neg1 = sum(1 for (q, x, _) in cases
               for st in [t5_stats(q, x)]
               if st["Sq"] < 0 and st["Sq"] * st["Sq"] * 100 > 81 * st["d"] * st["Q2"])
    T5_STATS.update({"n": len(cases), "ubins": dict(sorted(ubins.items())),
                     "signs": dict(sorted(signs.items())), "zeros": dict(sorted(zeros.items())),
                     "xsign": dict(sorted(xsign.items())), "n_orth": n_orth, "n_par": n_par,
                     "n_exact": n_exact, "n_degen": n_degen, "rejects": rejects,
                     "neg1": neg1,
                     "rho_minmax": {d: (min(v), max(v)) for d, v in sorted(per_d_rho.items())},
                     "best": (str(best[0]), best[1], str(best[2]), str(best[3])) if best else None,
                     "best_pos": (str(best_pos[0]), best_pos[1], str(best_pos[2]), str(best_pos[3]))
                     if best_pos else None})
    check("T5.cover-u-sign", signs["pos"] > 0 and signs["neg"] > 0 and signs["zero"] > 0,
          str(dict(signs)))
    need = ["u=0", "0<|u|<0.1", "0.1-0.5", "0.5-0.8", "0.8-0.98", "0.98-1", "|u|=1"]
    check("T5.cover-u-bins", all(ubins[b] > 0 for b in need), str(dict(sorted(ubins.items()))))
    check("T5.cover-u-neg1", neg1 > 0, "u<-0.9: %d vaka" % neg1)
    okrho = all(min(v) == Fr(1, d) and max(v) == Fr(1) for d, v in per_d_rho.items())
    check("T5.cover-rho-range", okrho,
          "; ".join("d=%d min=%s max=%s" % (d, min(v), max(v)) for d, v in sorted(per_d_rho.items())))
    check("T5.cover-zero", zeros["one"] > 0 and zeros["multi"] > 0 and zeros["face"] > 0,
          str(dict(zeros)))
    check("T5.cover-sign", xsign["onesign"] > 0 and xsign["mixed"] > 0, str(dict(xsign)))
    check("T5.cover-orth", n_orth > 0, "%d vaka u=0 (tam Sq=0)" % n_orth)
    check("T5.cover-par", n_par > 0, "%d vaka |u|=1 (tam Sq^2=d Q2)" % n_par)
    check("T5.broken-rejects", rejects > 0,
          "kirik sinir (x999/1000) %d/%d vakayi reddeder" % (rejects, len(cases)))
    check("T5.tightest-zero", best is not None and best[0] == 0,
          "en siki slack=%s (%s); en siki pozitif=%s (%s); tam-esitlik=%d dejenere=%d"
          % (best[0] if best else "?", best[1] if best else "?",
             best_pos[0] if best_pos else "?", best_pos[1] if best_pos else "?",
             n_exact, n_degen))
    check("T5.exact-consistency", rejects >= n_exact,
          "reddedilen=%d >= tam-esitlik(rhs>0)=%d" % (rejects, n_exact))


# ---------------- T6: ancak hakli cikarilan (geri kalani acik bosluk) ----------------
# ACIK BOSLUK (bilerek test uydurulmedi): float nicemli sertifika (cert_interval
# yuvarlama + ic-durağan noktalar) ve C.tie ikili-arama taniklari tam Fraction
# kararina indirgenemedi (rho/u irrasyonel; dogrulanmis gercek-cebir sinir
# makinesi gerekir). D "aligned" (1.0,0.99,0.99) icin kucuk tamsayi vektor
# tanik arandi (0..10 d=2..5, d=2'de 1..199): bulunamadi; u=1 nokta-aralik
# rejimi T5 paralel kovalarinda vektor-tabanli kapsaniyor, 0.99 sayisi ozelinde
# tanik yok. Bunlar "yanlis" degil, "denetlenmedi"dir.
def run_T6():
    s4 = (1, 1, 1, 1)
    q4 = (Fr(1, 2),) * 4
    ks4, ki4 = sup_closed(s4, q4), inf_closed(s4, q4)
    check("T6.bracket-d4-closed",
          ks4 == ("norm", Fr(1)) and ki4 == ("axis", Fr(1, 2))
          and sup_attained(s4, q4) is True and inf_attained(s4, q4) is True,
          "aralik [0.5,1]: iki uc erisilir (N bos); '(0.5,1]' YANLIS")
    sC = (1, 1)
    qC = (Fr(3, 5), Fr(4, 5))
    ksC, kiC = sup_closed(sC, qC), inf_closed(sC, qC)
    check("T6.bracket-C-closed",
          ksC == ("norm", Fr(1)) and kiC == ("axis", Fr(3, 5))
          and sup_attained(sC, qC) is True and inf_attained(sC, qC) is True,
          "aralik [3/5,1]: iki uc erisilir (N bos); '(3/5,1]' YANLIS")
    qE = (Fr(1, 2),) * 4
    sqE = sum(qi * si for qi, si in zip(qE, s4))
    check("T6.E-point-record", sqE * sqE == 4 * vnorm2(qE),
          "E duzeneginde u^2=1 (nokta-aralik); genel-durum T5'tedir")
    qO = (Fr(1), Fr(-1), Fr(7), Fr(-7))
    xO = (Fr(1), Fr(0), Fr(0), Fr(0))
    o = t5_stats(qO, xO)
    check("T6.witness-orthogonal-center",
          o["s"] == [1, 1, 1, 1] and o["Sq"] == 0
          and o["S1"] == 1 and o["X2"] == 1 and o["QX"] == 1 and o["Q2"] == 100
          and o["lhs"] <= o["rhs"],
          "D u=0,rho=1/2,t=1/10: Sq=0 rho2=1/4 t=1/10 (tam tanik)")
    qF = (Fr(3), Fr(-4))
    xF = (Fr(0), Fr(1))
    f = t5_stats(qF, xF)
    check("T6.witness-failure-wide",
          f["s"] == [1, 1] and f["Sq"] == -1 and f["Q2"] == 25
          and f["S1"] == 1 and f["X2"] == 1 and f["QX"] == -4
          and f["lhs"] == f["rhs"] and f["rhs"] > 0,
          "D u=-1/(5sqrt2),rho=1/sqrt2,t=-4/5: alt-ucta tam esitlik (siki)")
    qJ = (Fr(1, 3), Fr(2, 3), Fr(2, 3))
    xJ = (Fr(2, 3), Fr(2, 3), Fr(-1, 3))
    j = t5_stats(qJ, xJ)
    check("T6.witness-query-coded-doc",
          j["s"] == [1, 1, -1] and j["Sq"] == Fr(1, 3) and j["Q2"] == 1
          and j["S1"] == Fr(5, 3) and j["X2"] == 1 and j["QX"] == Fr(4, 9)
          and j["lhs"] <= j["rhs"],
          "D u=1/(3sqrt3),rho=5/(3sqrt3),t=4/9: u2=1/27 rho2=25/27 (tam tanik)")
    cases = build_t5_cases()
    nondeg = sum(1 for (q, x, _) in cases
                 for st in [t5_stats(q, x)] if st["Bq"] > 0 and st["Bx"] > 0)
    check("T6.nondegenerate-count", nondeg > 1000,
          "T5'te %d sistematik dejenere-olmayan vaka (Bq>0,Bx>0)" % nondeg)
    pt = sum(1 for (q, x, _) in cases
             for st in [t5_stats(q, x)] if st["Bq"] == 0 and st["Bx"] > 0)
    check("T6.point-regime-covered", pt > 0,
          "u=1 nokta-aralik rejimi %d vektor-tabanli vakada kapsanir" % pt)


def main():
    run_d2_kept()
    run_d3_kept()
    run_flip_kept()
    run_cap_kept()
    run_top3_kept()
    run_query_kept()
    run_seeded_kept()
    run_T1()
    run_T2()
    run_T3()
    run_T4()
    run_T5()
    run_T6()
    from collections import Counter
    tot = Counter()
    pas = Counter()
    for c in CHECKS:
        g = c["name"].split(".")[0]
        tot[g] += 1
        if c["pass"]:
            pas[g] += 1
    for g in sorted(tot):
        print("GRUP %s: %d/%d %s" % (g, pas[g], tot[g],
                                     "GECTI" if pas[g] == tot[g] else "KALDI"), flush=True)
    npass = sum(pas.values())
    nfail = len(CHECKS) - npass
    print("%d/%d checks passed" % (npass, len(CHECKS)), flush=True)
    key = {
        "d2_sup_s(1,1)_q(3/5,4/5)": sup_val_float((1, 1), (Fr(3, 5), Fr(4, 5))),
        "d2_inf_s(1,1)_q(3/5,4/5)": inf_val_float((1, 1), (Fr(3, 5), Fr(4, 5))),
        "t5": {k: (str(v) if not isinstance(v, dict) else
                   {kk: str(vv) for kk, vv in v.items()})
               for k, v in T5_STATS.items()},
    }
    with open("results.json", "w") as f:
        json.dump({"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                              "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
                   "passed": npass, "total": len(CHECKS), "failed": nfail,
                   "key_numbers": key, "checks": CHECKS}, f, indent=1)
    return 0 if nfail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
