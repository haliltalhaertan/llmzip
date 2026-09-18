# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""Independent rational truth comparator (adversarial suite, own code).

Derivation route (deliberately NOT v2.cmp_rank): every Fraction input is
decomposed to (numerator, positive denominator) integers and the rank
comparison is reduced to integer cross products. No call into any
certifier module. Only stdlib.
"""
from fractions import Fraction as F


class DomainError(Exception):
    pass


def _nd(x):
    n, d = F(x).as_integer_ratio()
    assert d > 0
    return n, d


def true_cmp(p, q, z):
    """Rank comparison at rational z by integer cross products.

    f_d(z) = N_d(z)/D_d(z); rank orders by sign first, then |f|.
    Returns +1/0/-1 (p above / tied / below q). Raises DomainError
    unless both denominators are strictly positive.
    """
    z = F(z)
    zn, zd = _nd(z)
    terms = []
    for (a, b, u, v) in (p, q):
        na, da = _nd(a)
        nb, db = _nd(b)
        nu, du = _nd(u)
        nv, dv = _nd(v)
        # N = a + b*z = (na*db*zd + nb*da*zn) / (da*db*zd)
        SN = na * db * zd + nb * da * zn
        DN = da * db * zd
        # D = u + v*z = (nu*dv*zd + nv*du*zn) / (du*dv*zd)
        SD = nu * dv * zd + nv * du * zn
        DD = du * dv * zd
        assert DN > 0 and DD > 0
        if SD <= 0:
            raise DomainError("denominator not positive at z=%s" % z)
        terms.append((SN, DN, SD, DD))
    (SN1, DN1, SD1, DD1), (SN2, DN2, SD2, DD2) = terms
    s1 = (SN1 > 0) - (SN1 < 0)
    s2 = (SN2 > 0) - (SN2 < 0)
    if s1 != s2:
        return (s1 > s2) - (s1 < s2)
    if s1 == 0:
        return 0
    # |N1|/D1 vs |N2|/D2  <=>  SN1^2 * SD2 * DN2^2 * DD1 vs SN2^2 * SD1 * DN1^2 * DD2
    # (all denominators positive; DD/DN cancel to positive factors).
    L = SN1 * SN1 * SD2 * DN2 * DN2 * DD1
    R = SN2 * SN2 * SD1 * DN1 * DN1 * DD2
    c = (L > R) - (L < R)
    return c if s1 > 0 else -c


def poly_coeffs_ind(p, q):
    """Coefficients of Q(z) = N1(z)^2*D2(z) - N2(z)^2*D1(z) by direct
    polynomial convolution (independent route vs closed-form expansion).

    Returns [c0..c3] with Q(z) = sum c_k z^k. Exact Fractions.
    """
    def mul(A, B):
        C = [F(0)] * (len(A) + len(B) - 1)
        for i, x in enumerate(A):
            for j, y in enumerate(B):
                C[i + j] += x * y
        return C

    def add(A, B):
        n = max(len(A), len(B))
        return [ (A[i] if i < len(A) else F(0)) + (B[i] if i < len(B) else F(0))
                 for i in range(n) ]

    def sub(A, B):
        n = max(len(A), len(B))
        return [ (A[i] if i < len(A) else F(0)) - (B[i] if i < len(B) else F(0))
                 for i in range(n) ]

    N1 = [F(p[0]), F(p[1])]
    D1 = [F(p[2]), F(p[3])]
    N2 = [F(q[0]), F(q[1])]
    D2 = [F(q[2]), F(q[3])]
    Q = sub(mul(mul(N1, N1), D2), mul(mul(N2, N2), D1))
    while len(Q) < 4:
        Q.append(F(0))
    return Q[:4]


def peval(co, z):
    z = F(z)
    s = F(0)
    for c in reversed(co):
        s = s * z + c
    return s
