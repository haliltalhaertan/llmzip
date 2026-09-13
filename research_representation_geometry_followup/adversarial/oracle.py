# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""Exact oracle: Sturm root counting + closed classification (own code).

Self-written Fraction-only implementation of Sturm's theorem and the
rational-root theorem. Used to (a) prove a case's root inventory is
complete (Sturm count 0 on every open subinterval between consecutive
critical points) and (b) freeze piecewise point-truth. Sampling is never
used as proof of absence: absence of roots is proved by Sturm counts.
"""
from fractions import Fraction as F

import truth as T


class OracleIncomplete(Exception):
    pass


def _strip(co):
    co = [F(c) for c in co]
    while len(co) > 1 and co[-1] == 0:
        co.pop()
    return co


def _peval(co, z):
    z = F(z)
    s = F(0)
    for c in reversed(co):
        s = s * z + c
    return s


def _pderiv(co):
    co = _strip(co)
    if len(co) <= 1:
        return [F(0)]
    return _strip([co[k] * k for k in range(1, len(co))])


def _pdivmod(A, B):
    A = [F(c) for c in A]
    B = _strip([F(c) for c in B])
    if len(B) == 1 and B[0] == 0:
        raise ZeroDivisionError("division by zero polynomial")
    Q = [F(0)] * max(len(A) - len(B) + 1, 1)
    R = [F(c) for c in A]
    while not (len(R) == 1 and R[0] == 0) and len(R) >= len(B):
        t = R[-1] / B[-1]
        k = len(R) - len(B)
        Q[k] = Q[k] + t
        for j in range(len(B)):
            R[k + j] = R[k + j] - t * B[j]
        R = _strip(R)
    return _strip(Q), _strip(R)


def _sturm_seq(P):
    P = _strip(P)
    if len(P) == 1 and P[0] == 0:
        return [P]
    S = [P, _strip(_pderiv(P))]
    if len(S[1]) == 1 and S[1][0] == 0:
        return [S[0]]
    while True:
        _, r = _pdivmod(S[-2], S[-1])
        if len(r) == 1 and r[0] == 0:
            break
        S.append([-c for c in r])
    return S


def _variations(vals):
    nz = [v for v in vals if v != 0]
    n = 0
    for i in range(1, len(nz)):
        if (nz[i] > 0) != (nz[i - 1] > 0):
            n += 1
    return n


def _deflate(P, r):
    P = _strip([F(c) for c in P])
    r = F(r)
    n = len(P) - 1
    if n < 1:
        raise OracleIncomplete("cannot deflate constant")
    Q = [F(0)] * n
    Q[-1] = P[-1]
    for k in range(n - 2, -1, -1):
        Q[k] = P[k + 1] + r * Q[k + 1]
    if not (P[0] + r * Q[0] == 0):
        raise OracleIncomplete("deflation failed at %s" % r)
    return _strip(Q)


def sturm_open_count(P, L, R):
    """Distinct roots of P in open (L,R). Deflates endpoint roots first."""
    P = _strip([F(c) for c in P])
    L, R = F(L), F(R)
    assert L < R
    if len(P) == 1 and P[0] == 0:
        return None
    Q = list(P)
    while _peval(Q, L) == 0:
        Q = _deflate(Q, L)
    while _peval(Q, R) == 0:
        Q = _deflate(Q, R)
    if len(Q) == 1 and Q[0] == 0:
        return 0
    S = _sturm_seq(Q)
    return _variations([_peval(s, L) for s in S]) - _variations([_peval(s, R) for s in S])


def _divisors(n):
    import math
    n = abs(int(n))
    if n == 0:
        return []
    out = set()
    r = int(math.isqrt(n))
    for d in range(1, r + 1):
        if n % d == 0:
            out.add(d)
            out.add(n // d)
    return sorted(out)


def rational_roots(P, limit=10 ** 6, cap=4096):
    """Rational-root theorem enumeration. Returns (roots, skipped)."""
    import math
    co = _strip([F(c) for c in P])
    if len(co) <= 1:
        return [], False
    M = 1
    for c in co:
        M = M * c.denominator // math.gcd(M, c.denominator)
    ints = [int(c * M) for c in co]
    while len(ints) > 1 and ints[-1] == 0:
        ints.pop()
    if len(ints) <= 1:
        return [], False
    A0, Ad = ints[0], ints[-1]
    if A0 == 0:
        sub, sk = rational_roots(_strip([F(x) for x in ints[1:]]), limit, cap)
        return sorted(set(sub) | {F(0)}), sk
    if max(abs(A0), abs(Ad)) > limit:
        return [], True
    roots = []
    n = 0
    for pp in _divisors(A0):
        for qq in _divisors(Ad):
            for s in (F(pp, qq), F(-pp, qq)):
                n += 1
                if n > cap:
                    return sorted(set(roots)), True
                if _peval(co, s) == 0 and s not in roots:
                    roots.append(s)
    return sorted(roots), False


def num_zero(doc, L, R):
    a, b = F(doc[0]), F(doc[1])
    if b == 0:
        return None
    z0 = -a / b
    return z0 if F(L) <= z0 <= F(R) else None


def domain_ok(p, q, L, R):
    L, R = F(L), F(R)
    for doc in (p, q):
        for z in (L, R):
            if not (F(doc[2]) + F(doc[3]) * z > 0):
                return False
    return True


def classify(p, q, L, R, known_roots=()):
    """Closed exact classification. known_roots: candidate Q-roots (verified
    by exact peval here). Raises OracleIncomplete unless the inventory closes:
    every open subinterval between consecutive critical points has Sturm
    count 0 except subintervals are not even needed around known roots --
    known roots ARE the critical points, so closure = all subinterval
    counts 0 (roots can only sit at critical points).

    Returns dict with frozen oracle facts.
    """
    p = tuple(F(x) for x in p)
    q = tuple(F(x) for x in q)
    L, R = F(L), F(R)
    if not domain_ok(p, q, L, R):
        return {"domain": "fail"}
    Q = T.poly_coeffs_ind(p, q)
    if all(c == 0 for c in Q):
        # P identically zero: order from numerator signs only; exact by
        # critical set {L,R} + numerator zeros.
        crit = {L, R}
        for doc in (p, q):
            z0 = num_zero(doc, L, R)
            if z0 is not None:
                crit.add(z0)
        pts = sorted(crit)
        truth = {str(s): T.true_cmp(p, q, s) for s in pts}
        for i in range(len(pts) - 1):
            m = (pts[i] + pts[i + 1]) / 2
            if pts[i] == pts[i + 1]:
                continue
            truth[str(m)] = T.true_cmp(p, q, m)
        return {"domain": "ok", "Q": [str(c) for c in Q], "identically_zero": True,
                "crit": [str(s) for s in pts], "truth": truth,
                "plus": any(v == 1 for v in truth.values()),
                "minus": any(v == -1 for v in truth.values())}
    for r in known_roots:
        if _peval(Q, F(r)) != 0:
            raise OracleIncomplete("claimed root %s is not a Q-root" % r)
    crit = {L, R}
    for r in known_roots:
        rr = F(r)
        if L <= rr <= R:
            crit.add(rr)
    for doc in (p, q):
        z0 = num_zero(doc, L, R)
        if z0 is not None:
            crit.add(z0)
    pts = sorted(crit)
    subintervals = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        if a == b:
            continue
        n = sturm_open_count(Q, a, b)
        if n is None or n != 0:
            raise OracleIncomplete(
                "unaccounted roots in (%s,%s): count=%s" % (a, b, n))
        m = (a + b) / 2
        subintervals.append({"lo": str(a), "hi": str(b), "count": n,
                             "mid": str(m), "mid_truth": T.true_cmp(p, q, m)})
    truth = {str(s): T.true_cmp(p, q, s) for s in pts}
    for s in subintervals:
        truth[s["mid"]] = s["mid_truth"]
    return {"domain": "ok", "Q": [str(c) for c in Q], "identically_zero": False,
            "crit": [str(s) for s in pts],
            "exact_roots_in_range": sorted({str(F(r)) for r in known_roots
                                            if L <= F(r) <= R}),
            "subintervals": subintervals, "truth": truth,
            "plus": any(v == 1 for v in truth.values()),
            "minus": any(v == -1 for v in truth.values())}
