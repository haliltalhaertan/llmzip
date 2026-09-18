# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""verify_v2.py — özgün verify.py yerine geçen denetim süiti (ek düzeltme).

Özgün 49 kontrolün tamamını kapsar: 48 aynen korunur, 1 onarılır
(S7-1plus1-unresolved: totoloji giderildi), 4 eklenir (S8 cA/cB statü+yön).
Toplam 53 kontrol. İncelenen yordam seçilebilir:
varsayılan certify_v2 (out/certify_v2.py); VERIFY_V2_PROC ortam değişkeni
mutasyon deneyinde başka modüle yönlendirir. Özgün certify_pair kodu
certify_pair_orig adıyla denetim başvurusu olarak aynen durur.
Sonuç results_v2.json dosyasına yazılır (results.json ezilmez).
Bulanık-sayım ve sağlamlık ölçümü fuzz_rates.py işidir, burada tekrarlanmaz.
"""
import importlib as _il
import json
import math
import os
import pickle
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results_v2.json")
PROC_MOD = os.environ.get("VERIFY_V2_PROC", "certify_v2")
LME_PKL = "/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/15745da0.pkl"

CHECKS = []
def check(name, cond, detail=""):
    CHECKS.append((name, bool(cond), str(detail)))
    if not cond:
        print("FAIL", name, detail, flush=True)

def fr(x):
    return x if isinstance(x, F) else F(x)

def P4(a, b, u, v):
    return (fr(a), fr(b), fr(u), fr(v))

# ---------------- primary exact comparator ----------------
class DomainError(Exception):
    pass

def NZ(p, z):
    a, b, u, v = p
    return a + b * z, u + v * z

def cmp_rank(p, q, z):
    """Exact sign of f_p(z) - f_q(z): +1 / 0 / -1. Raises DomainError."""
    z = fr(z)
    N1, D1 = NZ(p, z)
    N2, D2 = NZ(q, z)
    if not (D1 > 0 and D2 > 0):
        raise DomainError("denominator not positive")
    s1 = (N1 > 0) - (N1 < 0)
    s2 = (N2 > 0) - (N2 < 0)
    if s1 != s2:
        return (s1 > s2) - (s1 < s2)   # opposite signs / zero-vs-nonzero: no squaring
    if s1 == 0:
        return 0                        # both numerators zero: genuine tie
    c = ((N1 * N1 * D2) > (N2 * N2 * D1)) - ((N1 * N1 * D2) < (N2 * N2 * D1))
    return c if s1 > 0 else -c          # same strict sign: squared compare, flip if negative

# ---------------- independent audit comparator (integer-only path) ----------------
def _ratio(c):
    n, d = fr(c).as_integer_ratio()
    assert d > 0
    return n, d

def audit_cmp(p, q, z):
    """Re-implementation with integer-only arithmetic and product denominators.
    Never calls cmp_rank. Raises DomainError."""
    z = fr(z)
    zn, zd = z.as_integer_ratio()
    assert zd > 0
    outs = []
    for (a, b, u, v) in (p, q):
        na, da = _ratio(a); nb, db = _ratio(b)
        nu, du = _ratio(u); nv, dv = _ratio(v)
        SN = na * db * zd + nb * da * zn   # numerator of N over da*db*zd > 0
        DN = da * db * zd
        SD = nu * dv * zd + nv * du * zn   # numerator of D over du*dv*zd > 0
        DD = du * dv * zd
        assert DN > 0 and DD > 0
        if SD <= 0:
            raise DomainError("denominator not positive")
        outs.append((SN, DN, SD, DD))
    (SN1, DN1, SD1, DD1), (SN2, DN2, SD2, DD2) = outs
    s1 = (SN1 > 0) - (SN1 < 0)
    s2 = (SN2 > 0) - (SN2 < 0)
    if s1 != s2:
        return (s1 > s2) - (s1 < s2)
    if s1 == 0:
        return 0
    # V1 = SN1^2/DN1^2 * SD2/DD2  ?  V2 = SN2^2/DN2^2 * SD1/DD1 ; cross-multiply
    L = SN1 * SN1 * SD2 * DN2 * DN2 * DD1
    R = SN2 * SN2 * SD1 * DN1 * DN1 * DD2
    c = (L > R) - (L < R)
    return c if s1 > 0 else -c

# ---------------- pairwise equality polynomial, two formulations ----------------
def P_coeffs(p, q):
    """Direct expansion of (a1+b1 z)^2 (u2+v2 z) - (a2+b2 z)^2 (u1+v1 z)."""
    a1, b1, u1, v1 = p
    a2, b2, u2, v2 = q
    c0 = a1 * a1 * u2 - a2 * a2 * u1
    c1 = (2 * a1 * b1 * u2 + a1 * a1 * v2) - (2 * a2 * b2 * u1 + a2 * a2 * v1)
    c2 = (2 * a1 * b1 * v2 + b1 * b1 * u2) - (2 * a2 * b2 * v1 + b2 * b2 * u1)
    c3 = b1 * b1 * v2 - b2 * b2 * v1
    return [c0, c1, c2, c3]

def _Qeval(p, q, k):
    a1, b1, u1, v1 = p
    a2, b2, u2, v2 = q
    N1 = a1 + b1 * k; N2 = a2 + b2 * k
    D1 = u1 + v1 * k; D2 = u2 + v2 * k
    return N1 * N1 * D2 - N2 * N2 * D1

def audit_P_coeffs(p, q):
    """Independent formulation: evaluate Q at z=0,1,2,3, Newton-interpolate."""
    Q0 = _Qeval(p, q, F(0)); Q1 = _Qeval(p, q, F(1))
    Q2 = _Qeval(p, q, F(2)); Q3 = _Qeval(p, q, F(3))
    d1 = Q1 - Q0
    d2 = Q2 - 2 * Q1 + Q0
    d3 = Q3 - 3 * Q2 + 3 * Q1 - Q0
    c3 = d3 / 6
    c2 = d2 / 2 - d3 / 2
    c1 = d1 - d2 / 2 + d3 / 3
    return [Q0, c1, c2, c3]

# ---------------- exact polynomial + Sturm root isolation ----------------
def _strip(co):
    co = list(co)
    while len(co) > 1 and co[-1] == 0:
        co.pop()
    return co

def peval(co, z):
    z = fr(z)
    s = F(0)
    for c in reversed(co):
        s = s * z + c
    return s

def pderiv(co):
    if len(co) <= 1:
        return [F(0)]
    return _strip([co[k] * k for k in range(1, len(co))])

def _pdivmod(A, B):
    A = list(A); B = _strip(list(B))
    if len(B) == 1 and B[0] == 0:
        raise ZeroDivisionError
    Q = [F(0)] * max(len(A) - len(B) + 1, 1)
    R = list(A)
    while len(R) >= len(B) and not (len(R) == 1 and R[0] == 0):
        t = R[-1] / B[-1]
        k = len(R) - len(B)
        Q[k] = Q[k] + t
        for j in range(len(B)):
            R[k + j] = R[k + j] - t * B[j]
        R = _strip(R)
    return _strip(Q), _strip(R)

def sturm_seq(P):
    P = _strip([fr(c) for c in P])
    if len(P) == 1 and P[0] == 0:
        return [P]
    S = [P, _strip(pderiv(P))]
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

class Unresolved(Exception):
    pass

def _deflate(P, r):
    """Exact synthetic division of P by (z - r); asserts zero remainder."""
    P = _strip([fr(c) for c in P])
    r = fr(r)
    n = len(P) - 1
    if n < 1:
        raise Unresolved("cannot deflate constant")
    Q = [F(0)] * n
    Q[-1] = P[-1]
    for k in range(n - 2, -1, -1):
        Q[k] = P[k + 1] + r * Q[k + 1]
    assert P[0] + r * Q[0] == 0, "non-root deflation"
    return _strip(Q)

def sturm_open_count(P, L, R):
    """Exact number of DISTINCT roots of P in open interval (L,R).
    P degree<=3 exact Fractions. None if P identically zero.
    Endpoint roots are deflated exactly (all split points are rational), so the
    Sturm count applies with nonvanishing endpoints; open-interval roots of P
    coincide with those of the deflated quotient."""
    P = _strip([fr(c) for c in P])
    L, R = fr(L), fr(R)
    assert L < R
    if len(P) == 1 and P[0] == 0:
        return None
    Q = list(P)
    while peval(Q, L) == 0:
        Q = _deflate(Q, L)
    while peval(Q, R) == 0:
        Q = _deflate(Q, R)
    if len(Q) == 1 and Q[0] == 0:
        return 0
    S = sturm_seq(Q)
    return _variations([peval(s, L) for s in S]) - _variations([peval(s, R) for s in S])

# ---------------- certified pair procedure on closed J=[L,R] ----------------
def num_zero(p, L, R):
    """Exact numerator zero of N(z)=a+bz inside [L,R], or None. ('s=0' case.)"""
    a, b, _, _ = p
    if b == 0:
        return None
    z0 = -a / b
    return z0 if L <= z0 <= R else None

def _divisors(n):
    n = abs(int(n))
    if n == 0:
        return []
    ds = set()
    r = int(math.isqrt(n))
    for d in range(1, r + 1):
        if n % d == 0:
            ds.add(d)
            ds.add(n // d)
    return sorted(ds)

def rational_roots(P, limit=10 ** 6, cap=4096):
    """Exact rational roots via rational-root theorem. Returns (roots, skipped).
    skipped=True when coefficients exceed the exact-enumeration budget (honest)."""
    co = _strip([fr(c) for c in P])
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
    for p in _divisors(A0):
        for q in _divisors(Ad):
            for s in (F(p, q), F(-p, q)):
                n += 1
                if n > cap:
                    return sorted(set(roots)), True
                if peval(co, s) == 0 and s not in roots:
                    roots.append(s)
    return sorted(roots), False

def certify_pair_orig(p, q, L, R):
    """ORIGINAL procedure, kept verbatim as audit reference (not under test).
    Certificate for one pair on closed J=[L,R] (requires D>0 at endpoints,
    hence on all of J by linearity; else DOMAIN_FAIL = half-open/excluded case).
    Returns dict(status, direction, ties, notes, sturm_calls).
    status: STRICT | ISOLATED_TIES | UNRESOLVED | DOMAIN_FAIL."""
    out = {"status": None, "direction": None, "ties": [],
           "notes": [], "sturm_calls": 0}
    L, R = fr(L), fr(R)
    for doc, tag in ((p, "p"), (q, "q")):
        _, D1 = NZ(doc, L); _, D2 = NZ(doc, R)
        if not (D1 > 0 and D2 > 0):
            out["status"] = "DOMAIN_FAIL"
            out["notes"].append("denominator non-positive at endpoint (%s); "
                                "J not contained in domain (r=0 boundary)" % tag)
            return out
    cuts = {L, R}
    for doc in (p, q):
        z0 = num_zero(doc, L, R)
        if z0 is not None:
            cuts.add(z0)
    P = P_coeffs(p, q)
    assert P == audit_P_coeffs(p, q), "P expansion/interpolation disagree"
    is_zero = all(c == 0 for c in P)
    if not is_zero:
        rrs, rsk = rational_roots(P)
        if rsk:
            out["notes"].append("rational-root enumeration over budget: kept exact, "
                                "may return UNRESOLVED on same-sign interiors")
        for rr in rrs:
            if L < rr < R:
                cuts.add(rr)
    pts = sorted(cuts)
    for s in pts:  # exact verdicts at all split points (rational P-roots + s=0 loci)
        v = cmp_rank(p, q, s)
        va = audit_cmp(p, q, s)
        assert v == va, "primary/audit comparator disagree"
        if v == 0:
            out["ties"].append(str(s))
    dirs = set()
    if is_zero:
        out["notes"].append("P identically zero: |f_p|==|f_q| wherever defined; "
                            "order from numerator signs only")
    for i in range(len(pts) - 1):
        l, r = pts[i], pts[i + 1]
        if l == r:
            continue
        m = (l + r) / 2
        vm = cmp_rank(p, q, m)
        assert vm == audit_cmp(p, q, m)
        if vm == 0:
            if is_zero:
                dirs.add(0)
                out["ties"].append("persistent(%s,%s)" % (l, r))
                out["notes"].append("persistent-tie subinterval (%s,%s)" % (l, r))
                continue
            out["status"] = "UNRESOLVED"
            out["notes"].append("tie at interior sample %s with P nonzero" % m)
            return out
        dirs.add(vm)
        N1m = p[0] + p[1] * m
        N2m = q[0] + q[1] * m
        s1 = (N1m > 0) - (N1m < 0)
        s2 = (N2m > 0) - (N2m < 0)
        if s1 != s2:
            out["notes"].append("(%s,%s): opposite/single-zero signs, "
                                "no equality possible" % (l, r))
            continue
        if is_zero:
            out["notes"].append("(%s,%s): P==0 with same strict signs -> "
                                "persistent tie, contradicts sample" % (l, r))
            out["status"] = "UNRESOLVED"
            return out
        try:
            n = sturm_open_count(P, l, r)
        except Unresolved as e:
            out["status"] = "UNRESOLVED"
            out["notes"].append("sturm unresolved (%s,%s): %s" % (l, r, e))
            return out
        out["sturm_calls"] += 1
        if n is None:  # unreachable (is_zero handled)
            out["status"] = "UNRESOLVED"
            return out
        if n == 0:
            out["notes"].append("(%s,%s): sturm=0 same-sign roots, "
                                "strict order constant" % (l, r))
        else:
            out["status"] = "UNRESOLVED"
            out["notes"].append("(%s,%s): sturm=%d same-sign P-roots -> "
                                "UNRESOLVED (touch or crossing)" % (l, r, n))
            return out
    if out["status"] == "UNRESOLVED":
        return out
    nz = sorted(d for d in dirs if d != 0)
    if len(nz) > 1:
        # Certified piecewise-constant with a flip across listed tie points
        # (every interior certified; ties only at listed points).
        out["status"] = "ISOLATED_TIES"
        out["direction"] = "VARIES"
        out["notes"].append("direction flips across listed ties: certified "
                            "piecewise order, NOT stable")
        return out
    if 0 in dirs and not nz:
        out["status"] = "PERSISTENT_TIE"
        out["direction"] = 0
        return out
    if 0 in dirs:
        out["status"] = "ISOLATED_TIES"  # P==0 mixed: tie-intervals + strict parts
        out["direction"] = nz[0]
        return out
    if out["ties"]:
        out["status"] = "ISOLATED_TIES"
    else:
        out["status"] = "STRICT"
    out["direction"] = nz[0] if nz else 0
    return out

# ---------------- procedure under test (selectable) ----------------
# Varsayılan: certify_v2.certify_pair. Mutasyon deneyinde VERIFY_V2_PROC
# başka bir modüle (mutasyonlu kopya) yönlendirilir; topk_cert ve S8
# bu genel adı kullanır, dolayısıyla hep incelenen yordam çalışır.
certify_pair = _il.import_module(PROC_MOD).certify_pair


# ---------------- top-K certificates ----------------
def order_at(docs, z):
    """Total preorder at z: list of indices sorted best-first (exact, ties grouped)."""
    # insertion sort with exact comparator (deterministic, independent of sort stability)
    res = list(range(len(docs)))
    for i in range(1, len(docs)):
        j = i
        while j > 0 and cmp_rank(docs[res[j]], docs[res[j - 1]], z) > 0:
            res[j], res[j - 1] = res[j - 1], res[j]
            j -= 1
    return res

def expected_gold_topk(docs, gold, K, z):
    """Expected #golds in top-K under uniform random tie-break (exact Fraction).
    Separate object from fixed-priority top-K: depends on tie-group composition."""
    z = fr(z)
    for d in docs:
        _, D = NZ(d, z)
        if not D > 0:
            raise DomainError
    n = len(docs)
    groups = []  # best-first groups of tied indices
    placed = [False] * n
    order = order_at(docs, z)
    for i in order:
        if placed[i]:
            continue
        g = [j for j in order if not placed[j] and cmp_rank(docs[i], docs[j], z) == 0]
        for j in g:
            placed[j] = True
        groups.append(g)
    E = F(0)
    filled = 0
    for g in groups:
        if filled >= K:
            break
        take = min(len(g), K - filled)
        ng = sum(1 for j in g if j in gold)
        E += F(ng * take, len(g))
        filled += len(g)
    return E

def topk_cert(docs, K, prio, L, R):
    """Certified top-K analysis on closed J=[L,R].
    prio: dict idx->rank (lower = wins ties). Sample must be tie-free; else SAMPLE_TIED.
    Returns dict with strict/prio/unstable verdicts over K*(n-K) cross pairs only."""
    L, R = fr(L), fr(R)
    n = len(docs)
    cands = [(L + R) / 2, L, R, (2 * L + R) / 3, (L + 2 * R) / 3]
    z0 = None
    for c in cands:
        try:
            ok = True
            for i in range(n):
                for j in range(i + 1, n):
                    if cmp_rank(docs[i], docs[j], c) == 0:
                        ok = False
        except DomainError:
            ok = False
        if ok:
            z0 = c
            break
    out = {"sample": str(z0) if z0 is not None else None, "in": None,
           "pairs": {}, "strict": None, "prio": None, "unstable_witness": None,
           "cross_pairs": 0}
    if z0 is None:
        out["strict"] = out["prio"] = "SAMPLE_TIED"
        return out

    def prio_set(z):
        idx = list(range(len(docs)))
        for i in range(1, len(idx)):
            j = i
            while j > 0:
                c = cmp_rank(docs[idx[j]], docs[idx[j - 1]], z)
                if c > 0 or (c == 0 and prio[idx[j]] < prio[idx[j - 1]]):
                    idx[j], idx[j - 1] = idx[j - 1], idx[j]
                    j -= 1
                else:
                    break
        return set(idx[:K])

    # two-point instability probe (exact, needs no root isolation)
    try:
        refset = prio_set(z0)
    except DomainError:
        out["strict"] = out["prio"] = "DOMAIN_FAIL"
        return out
    for zp in (L, R):
        try:
            if prio_set(zp) != refset:
                out["in"] = sorted(refset)
                out["unstable_witness"] = {"pair": None, "kind": "probe-sets-differ",
                                           "z_a": str(z0), "z_b": str(zp),
                                           "set_a": sorted(refset),
                                           "set_b": sorted(prio_set(zp))}
                out["strict"] = out["prio"] = "CERTIFIED_UNSTABLE"
                return out
        except DomainError:
            continue
    order = order_at(docs, z0)
    In = set(order[:K])
    out["in"] = sorted(In)
    for a in sorted(In):
        for b in range(n):
            if b in In:
                continue
            out["cross_pairs"] += 1
            r = certify_pair(docs[a], docs[b], L, R)
            out["pairs"]["%dvs%d" % (a, b)] = r
            if r["status"] in ("UNRESOLVED", "DOMAIN_FAIL", "SAMPLE_TIED"):
                out["strict"] = out["prio"] = r["status"]
                return out
            if r["status"] == "STRICT" and r["direction"] != 1:
                out["unstable_witness"] = {"pair": [a, b], "kind": "strict-reversal",
                                           "cert": r}
                out["strict"] = out["prio"] = "CERTIFIED_UNSTABLE"
                return out
            if r["direction"] == "VARIES":
                out["unstable_witness"] = {"pair": [a, b], "kind": "flip-across-ties",
                                           "cert": r}
                out["strict"] = out["prio"] = "CERTIFIED_UNSTABLE"
                return out
            if r["status"] == "ISOLATED_TIES" and r["direction"] != 1:
                # interiors strictly favor the Out member: no priority can save it
                out["unstable_witness"] = {"pair": [a, b], "kind": "interior-against-In",
                                           "cert": r}
                out["strict"] = out["prio"] = "CERTIFIED_UNSTABLE"
                return out
    # all cross pairs favor In on interiors; ties decide prio vs strict
    any_tie = any(r["status"] in ("ISOLATED_TIES", "PERSISTENT_TIE")
                  for r in out["pairs"].values())
    out["strict"] = "CERTIFIED_STABLE" if not any_tie else "TIES_PRESENT"
    # prio: stable iff at every listed tie, priority favors the In member
    prio_ok = True
    for key, r in out["pairs"].items():
        a, b = (int(x) for x in key.split("vs"))
        if r["status"] in ("ISOLATED_TIES", "PERSISTENT_TIE"):
            if not prio[a] < prio[b]:
                prio_ok = False
    out["prio"] = "CERTIFIED_STABLE" if prio_ok else "PRIO_FLIPS_AT_TIE"
    return out

# ---------------- seeded BROKEN variant (negative control) ----------------
def naive_cmp(p, q, z):
    """INTENTIONALLY WRONG: squares without sign discipline; P==0 read as tie,
    P>0 read as p>q. Must fail on the fake-root witness FOR THIS REASON."""
    z = fr(z)
    N1, D1 = NZ(p, z)
    N2, D2 = NZ(q, z)
    if not (D1 > 0 and D2 > 0):
        raise DomainError
    S = N1 * N1 * D2 - N2 * N2 * D1
    if S == 0:
        return 0
    return 1 if S > 0 else -1

# ---------------- witnesses + procedure demos ----------------
RES_DATA = {"sections": {}}

def sec(name, payload):
    RES_DATA["sections"][name] = payload

def run_all():
    # S0. Sturm self-tests (known polynomials, exact expected distinct-root counts)
    sturm_tests = [
        ([-2, 3, -1], F(0), F(3), 2),   # -z^2+3z-2 roots 1,2
        ([2, -3, 1], F(0), F(1), 0),    # roots at endpoints excluded
        ([2, -3, 1], F(0), F(2), 1),
        ([1, -2, 1], F(0), F(2), 1),    # (z-1)^2 distinct count 1
        ([1, -2, 1], F(0), F(1), 0),
        ([0, 0, 0, 1], F(-1), F(1), 1),  # z^3
        ([1, 0, 1], F(-5), F(5), 0),     # z^2+1
        ([-2, 2], F(0), F(2), 1),
        ([5], F(-9), F(9), 0),
    ]
    for i, (P, L, R, e) in enumerate(sturm_tests):
        check("sturm-self-%d" % i, sturm_open_count(P, L, R) == e, (P, L, R, e))
    check("sturm-zero-poly", sturm_open_count([0, 0], F(0), F(1)) is None, "zero poly")
    rr1, sk1 = rational_roots([F(1), F(-2), F(1), F(0)])
    check("ratroot-square", rr1 == [F(1)] and not sk1, (rr1, sk1))
    rr2, sk2 = rational_roots(P_coeffs(P4(1, 1, 1, 10), P4(-1, -1, 10, 1)))
    check("ratroot-fake", rr2 == [F(-1), F(1)] and not sk2, (rr2, sk2))
    _, sk3 = rational_roots([F(10 ** 12 + 39), F(1), F(1)])
    check("ratroot-over-budget-honest", sk3 is True, sk3)
    sec("S0-sturm-selftests", {"n": len(sturm_tests) + 4})

    # S1. Prior 2+2 nonmonotone witness (shared query, fixed group baked into coeffs)
    C1 = P4(-3, 4, 5, 10)
    C2 = P4(-2, 2, 2, 10)
    Z7 = [F(1, 64), F(1, 16), F(1, 4), F(1), F(4), F(16), F(64)]
    EXP7 = [1, -1, -1, 1, 1, 1, 1]
    got7 = [cmp_rank(C1, C2, z) for z in Z7]
    aud7 = [audit_cmp(C1, C2, z) for z in Z7]
    check("S1-nonmonotone-pattern", got7 == EXP7, got7)
    check("S1-audit-agrees", aud7 == got7, aud7)
    P12 = P_coeffs(C1, C2)
    check("S1-P-dual-form", P12 == audit_P_coeffs(C1, C2), [str(c) for c in P12])
    check("S1-P-cubic", P12[3] == 120, P12[3])
    check("S1-zero-discipline-at-1", (C2[0] + C2[1] * F(1)) == 0 and
          (C1[0] + C1[1] * F(1)) == 1 and peval(P12, F(1)) == 12, "N2=0,N1=1,P=12")
    sec("S1-nonmonotone-witness",
        {"C1": [-3, 4, 5, 10], "C2": [-2, 2, 2, 10],
         "z": [str(z) for z in Z7], "verdicts_C1_minus_C2": got7,
         "P": [str(c) for c in P12]})

    # S2. Persistent tie (P identically zero, same signs -> tie everywhere)
    T1 = P4(2, 2, 4, 4)
    T2 = P4(1, 1, 1, 1)
    PT = P_coeffs(T1, T2)
    check("S2-P-identically-zero", all(c == 0 for c in PT), [str(c) for c in PT])
    tv = [cmp_rank(T1, T2, z) for z in [F(1, 16), F(1), F(16)]]
    check("S2-tie-everywhere", tv == [0, 0, 0], tv)
    check("S2-audit-agrees", [audit_cmp(T1, T2, z) for z in [F(1, 16), F(1), F(16)]] == tv, "")
    sec("S2-persistent-tie", {"T1": [2, 2, 4, 4], "T2": [1, 1, 1, 1],
                              "verdicts": tv, "P": [str(c) for c in PT]})

    # S3. Opposite-sign fake root: P(1)==0 yet strict f1>f2 (squaring spurious root)
    F1 = P4(1, 1, 1, 10)
    F2 = P4(-1, -1, 10, 1)
    PF = P_coeffs(F1, F2)
    check("S3-P-dual-form", PF == audit_P_coeffs(F1, F2), [str(c) for c in PF])
    check("S3-fake-root-at-1", peval(PF, F(1)) == 0, [str(c) for c in PF])
    fv = [cmp_rank(F1, F2, z) for z in [F(1, 16), F(1), F(16)]]
    check("S3-strict-despite-root", fv == [1, 1, 1], fv)
    check("S3-audit-agrees", [audit_cmp(F1, F2, z) for z in [F(1, 16), F(1), F(16)]] == fv, "")
    nv = naive_cmp(F1, F2, F(1))
    check("S3-mutant-fails-as-intended", nv == 0 and fv[1] == 1,
          "naive reads P==0 as tie; truth is strict (opposite signs)")
    sec("S3-fake-root", {"F1": [1, 1, 1, 10], "F2": [-1, -1, 10, 1],
                         "P": [str(c) for c in PF], "P_at_1": str(peval(PF, F(1))),
                         "verdicts": fv, "mutant_at_1": nv,
                         "mutant_status": "FAILS_AS_INTENDED"})
    # S3b. P identically zero with OPPOSITE signs: never a tie (companion lesson)
    check("S3b-P-not-identically-zero-here", not all(c == 0 for c in PF), "")
    O1 = P4(1, 0, 1, 1)
    O2 = P4(-1, 0, 1, 1)
    PO = P_coeffs(O1, O2)
    check("S3b-P-identically-zero-opposite", all(c == 0 for c in PO), [str(c) for c in PO])
    check("S3b-strict-everywhere", [cmp_rank(O1, O2, z) for z in [F(1, 4), F(2)]] == [1, 1], "")

    # S4. Tangent touch: P=(z-1)^2, genuine tie at 1, strict same side both sides
    E1 = P4(1, 1, 0, 4)
    E2 = P4(1, 0, 1, 0)
    PE = P_coeffs(E1, E2)
    check("S4-P-is-square", PE == [F(1), F(-2), F(1), F(0)], [str(c) for c in PE])
    ev = [cmp_rank(E1, E2, z) for z in [F(1, 4), F(1), F(4)]]
    check("S4-touch-no-reversal", ev == [1, 0, 1], ev)
    check("S4-audit-agrees", [audit_cmp(E1, E2, z) for z in [F(1, 4), F(1), F(4)]] == ev, "")
    check("S4-sturm-distinct-1", sturm_open_count(_strip(PE), F(0), F(2)) == 1, "")
    sec("S4-tangent", {"E1": [1, 1, 0, 4], "E2": [1, 0, 1, 0],
                       "P": [str(c) for c in PE], "verdicts_at_1/4_1_4": ev})

    # S5. Common-zero (both numerators zero) genuine tie that DOES reverse order
    G1 = P4(-1, 1, 1, 1)
    G2 = P4(-2, 2, 1, 3)
    gv = [cmp_rank(G1, G2, z) for z in [F(1, 4), F(1), F(2)]]
    check("S5-common-zero-tie-crosses", gv == [1, 0, -1], gv)
    check("S5-audit-agrees", [audit_cmp(G1, G2, z) for z in [F(1, 4), F(1), F(2)]] == gv, "")
    check("S5-P-vanishes-at-tie", peval(P_coeffs(G1, G2), F(1)) == 0, "")
    sec("S5-common-zero-tie", {"G1": [-1, 1, 1, 1], "G2": [-2, 2, 1, 3], "verdicts": gv})

    # S6. Top-K demos on J=[1/16,16] (z; t in [1/4,4]). Only K*(n-K) cross pairs used.
    J = (F(1, 16), F(16))
    Lo = P4(-100, 0, 1, 1)
    t1 = topk_cert([F1, F2, P4(-50, 0, 1, 0)], 1, {0: 0, 1: 1, 2: 2}, *J)
    check("S6-stable-despite-P-root", t1["strict"] == "CERTIFIED_STABLE"
          and t1["prio"] == "CERTIFIED_STABLE", (t1["strict"], t1["prio"]))
    check("S6-P-root-inside-J", peval(P_coeffs(F1, F2), F(1)) == 0, "")
    sec("S6a-top1-stable-fake-root", {"J": ["1/16", "16"], "strict": t1["strict"],
                                      "prio": t1["prio"], "cross_pairs": t1["cross_pairs"]})
    t2 = topk_cert([C1, C2, Lo], 1, {0: 0, 1: 1, 2: 2}, *J)
    check("S6-unstable-certified", t2["strict"] == "CERTIFIED_UNSTABLE", t2["strict"])
    sec("S6b-top1-unstable", {"J": ["1/16", "16"], "strict": t2["strict"],
                              "witness_kind": (t2["unstable_witness"] or {}).get("kind")})
    t3 = topk_cert([E1, E2], 1, {0: 0, 1: 1}, F(1, 4), F(4))
    check("S6-touch-prio-stable", t3["strict"] == "TIES_PRESENT"
          and t3["prio"] == "CERTIFIED_STABLE", (t3["strict"], t3["prio"]))
    t3b = topk_cert([E1, E2], 1, {0: 1, 1: 0}, F(1, 4), F(4))
    check("S6-touch-prio-flips", t3b["prio"] == "PRIO_FLIPS_AT_TIE", t3b["prio"])
    E_exp = [str(expected_gold_topk([E1, E2], {1}, 1, z)) for z in [F(1, 2), F(1), F(2)]]
    check("S6-expected-recall-jumps", E_exp == ["0", "1/2", "0"], E_exp)
    # remark: expectation can be stable while tie structure changes (non-necessity)
    A = P4(2, 0, 1, 0)
    B = P4(1, 0, 1, 0)
    A2 = P4(1, 0, 1, 0)
    B2 = P4(1, 0, 1, 0)
    C2b = P4(0, 0, 1, 0)
    E_r1 = expected_gold_topk([A, B, C2b], {0, 1}, 1, F(1))    # A>B>C strict, E=1
    E_r2 = expected_gold_topk([A2, B2, C2b], {0, 1}, 1, F(1))  # A=B>C tie, E=1
    check("S6-expectation-non-necessity", E_r1 == 1 and E_r2 == 1, (E_r1, E_r2))
    sec("S6c-touch-boundary-ties",
        {"strict": t3["strict"], "prio_E1first": t3["prio"], "prio_E2first": t3b["prio"],
         "expected_gold2_K1_at_1/2_1_2": E_exp,
         "expectation_remark": "tie-structure change with constant E (1 vs 1)"})

    # S7. Bounded 1+1-dim search (ONE scaled coord each side). Budget-capped,
    # deterministic lexicographic order. Params must satisfy 1-dim relations:
    # a=qc*c, b=qg*g, u=c^2, v=g^2 with FIXED shared (qc,qg). NO minimality claim.
    Z7b = Z7
    BUDGET = 40000
    evals = 0
    found11 = None
    V = list(range(-3, 4))
    QQ = [-2, -1, 1, 2]
    def nonmonotone(s):
        for i in range(len(s)):
            for j in range(i + 1, len(s)):
                for k in range(j + 1, len(s)):
                    if (s[j] - s[i]) * (s[k] - s[j]) < 0:
                        return True
        return False
    for qc in QQ:
        if found11 is not None:
            break
        for qg in QQ:
            if found11 is not None:
                break
            docs11 = [(c, g) for c in V for g in V if not (c == 0 and g == 0)]
            for i1 in range(len(docs11)):
                if found11 is not None or evals >= BUDGET:
                    break
                for i2 in range(i1 + 1, len(docs11)):
                    if found11 is not None or evals >= BUDGET:
                        break
                    evals += 1
                    (c1, g1), (c2, g2) = docs11[i1], docs11[i2]
                    p = P4(qc * c1, qg * g1, c1 * c1, g1 * g1)
                    q = P4(qc * c2, qg * g2, c2 * c2, g2 * g2)
                    try:
                        s = [cmp_rank(p, q, z) for z in Z7b]
                    except DomainError:
                        continue
                    if 0 in s:
                        continue
                    if nonmonotone(s):
                        found11 = {"qc": qc, "qg": qg, "d1": [c1, g1],
                                   "d2": [c2, g2], "verdicts": s}
    check("S7-budget-respected", evals <= BUDGET, evals)
    # ONARIM (özgün 734: `True` totolojisi): gerçek koşul koşulsuz denetlenir;
    # ızgarada tanık çıkarsa bu kontrol BAŞARISIZ olur (adı üstünde).
    check("S7-1plus1-unresolved", found11 is None, "evals=%d, no witness in grid" % evals)
    if found11 is not None:
        check("S7-1plus1-witness-audited",
              [audit_cmp(P4(found11["qc"] * found11["d1"][0],
                             found11["qg"] * found11["d1"][1],
                             found11["d1"][0] ** 2, found11["d1"][1] ** 2),
                        P4(found11["qc"] * found11["d2"][0],
                             found11["qg"] * found11["d2"][1],
                             found11["d2"][0] ** 2, found11["d2"][1] ** 2), z)
               for z in Z7b] == found11["verdicts"], found11)
    sec("S7-one-plus-one-search",
        {"budget": BUDGET, "evals": evals, "grid": "c,g in -3..3; qc,qg in +-1,+-2",
         "z": [str(z) for z in Z7b],
         "result": found11 if found11 is not None else "UNRESOLVED-in-grid"})

    # S8. OPTIONAL post-hoc LME illustration (original cache, read-only).
    # Bracket-endpoint direct-cosine comparison only; NOT out-of-sample prediction.
    lme = {"used": False}
    try:
        import numpy as np
        d = pickle.load(open(LME_PKL, "rb"))
        C = np.asarray(d["C"], dtype=float)
        qC = np.asarray(d["qC"], dtype=float)
        n = C.shape[1]
        order = np.lexsort((np.arange(n), np.abs(qC)))
        G = order[:48]
        gR, rR = 56, 368
        coord = json.load(open("/mnt/c/Users/MDP/dev/llmzip-work/"
                               "theory_benchmark_test_v1/audit_real_geometry/"
                               "COORDINATOR_LME_WITNESS.json"))
        ref = {e["t"]: e for e in coord}
        fc = {}
        for t in (0.25, 1.0, 4.0):
            Cs = C.copy()
            qs = qC.copy()
            Cs[:, G] *= t
            qs[G] *= t
            qn = float(np.linalg.norm(qs))
            row = {}
            for tag, ii in (("gold", gR), ("rival", rR)):
                dot = float(Cs[ii] @ qs)
                dn = float(np.linalg.norm(Cs[ii]))
                row[tag + "_dot"] = dot
                row[tag + "_norm"] = dn
                row[tag + "_cos"] = dot / (dn * qn)
            fc[t] = row
        match = all(abs(fc[t]["gold_cos"] - ref[t]["gold_cos"]) < 1e-9 and
                    abs(fc[t]["rival_cos"] - ref[t]["rival_cos"]) < 1e-9
                    for t in (0.25, 1.0, 4.0))
        check("S8-float-reproduces-coordinator", match, {t: fc[t]["gold_cos"] for t in fc})
        sgn = {t: (fc[t]["gold_cos"] > fc[t]["rival_cos"]) - (fc[t]["gold_cos"] < fc[t]["rival_cos"])
               for t in (0.25, 1.0, 4.0)}
        check("S8-bracket-flip-rival-to-gold", sgn[0.25] == -1 and sgn[1.0] == -1
              and sgn[4.0] == 1, sgn)
        # exact-rational reading of the two docs' float coefficients (binary-exact,
        # sums of exact products): guarantees below are about THESE rationals.
        comp = np.ones(n, dtype=bool)
        comp[G] = False
        def dot_exact(ii, mask):
            return sum(F(float(qC[k])) * F(float(C[ii][k])) for k in range(n) if mask[k])
        def norm2_exact(ii, mask):
            return sum(F(float(C[ii][k])) * F(float(C[ii][k])) for k in range(n) if mask[k])
        grp = ~comp
        pg = P4(dot_exact(gR, comp), dot_exact(gR, grp),
                norm2_exact(gR, comp), norm2_exact(gR, grp))
        pr = P4(dot_exact(rR, comp), dot_exact(rR, grp),
                norm2_exact(rR, comp), norm2_exact(rR, grp))
        ex = {str(z): cmp_rank(pg, pr, F(z)) for z in
              [F(1, 16), F(1), F(16)]}
        check("S8-exact-reading-flip", ex == {"1/16": -1, "1": -1, "16": 1}, ex)
        cA = certify_pair(pg, pr, F(1, 16), F(1))
        cB = certify_pair(pg, pr, F(1), F(16))
        # EK (özgün 804-805 hesaplanır ama 809-810 yalnız kaydedilir, hiç
        # denetlenmezdi): başlık iddiasının iki statüsü + tanımlı yönler.
        # v2 beklentisi: cA STRICT/-1, cB ISOLATED_TIES/VARIES.
        check("S8-cA-status", cA["status"] == "STRICT", cA["status"])
        check("S8-cA-direction", cA["direction"] == -1, repr(cA["direction"]))
        check("S8-cB-status", cB["status"] == "ISOLATED_TIES", cB["status"])
        check("S8-cB-direction", cB["direction"] == "VARIES", repr(cB["direction"]))
        lme = {"used": True, "float_signs_gold_minus_rival":
               {str(t): sgn[t] for t in sgn},
               "exact_reading_verdicts_gold_minus_rival": ex,
               "cert_[1/16,1]": {k: (v if k != "pairs" else None) for k, v in cA.items()},
               "cert_[1,16]": {k: (v if k != "pairs" else None) for k, v in cB.items()},
               "expected": {"cA": ["STRICT", -1], "cB": ["ISOLATED_TIES", "VARIES"]},
               "proc": PROC_MOD,
               "note": "POST-HOC explanatory only; exact certs about binary-exact "
                       "rational reading, not about BLAS float order; no prediction."}
    except Exception as e:  # missing file/numpy -> honest skip, not failure
        check("S8-skipped-honestly", True, "skipped: %r" % (e,))
        lme = {"used": False, "reason": repr(e)}
    sec("S8-lme-illustration", lme)

    # S9. Float-vs-exact note (UNCERTIFIED agreement spot-check, not a certificate)
    try:
        import numpy as np
        agree = True
        for (p, q) in [(P4(-3, 4, 5, 10), P4(-2, 2, 2, 10)),
                       (P4(1, 1, 1, 10), P4(-1, -1, 10, 1)),
                       (P4(1, 1, 0, 4), P4(1, 0, 1, 0))]:
            for z in [0.0625, 1.0, 16.0]:
                a1, b1, u1, v1 = (float(x) for x in p)
                a2, b2, u2, v2 = (float(x) for x in q)
                f1 = (a1 + b1 * z) / math.sqrt(u1 + v1 * z)
                f2 = (a2 + b2 * z) / math.sqrt(u2 + v2 * z)
                fs = (f1 > f2) - (f1 < f2)
                if fs != cmp_rank(p, q, F(str(z))):
                    agree = False
        check("S9-float-agrees-informational", agree, "UNCERTIFIED spot-check")
        sec("S9-float-note", {"agreement_on_spots": agree,
                              "status": "INFORMATIONAL-UNCERTIFIED"})
    except Exception as e:
        check("S9-skipped", True, repr(e))
        sec("S9-float-note", {"status": "skipped", "reason": repr(e)})


def main():
    run_all()
    fails = [n for (n, ok, _) in CHECKS if not ok]
    RES_DATA["env"] = {"python": sys.version.split()[0],
                       "threads": "OMP_NUM_THREADS=%s OPENBLAS_NUM_THREADS=%s" %
                       (os.environ.get("OMP_NUM_THREADS"), os.environ.get("OPENBLAS_NUM_THREADS")),
                       "bytecode": "off" if sys.flags.dont_write_bytecode else "on"}
    RES_DATA["totals"] = {"n_checks": len(CHECKS), "n_fail": len(fails), "failed": fails}
    RES_DATA["suite"] = {"name": "verify_v2", "proc": PROC_MOD,
                         "kept": 48, "repaired": ["S7-1plus1-unresolved"],
                         "added": ["S8-cA-status", "S8-cA-direction",
                                   "S8-cB-status", "S8-cB-direction"]}
    RES_DATA["labels"] = ["[LOCAL EXPLORATORY PILOT]", "[NOT PREREGISTERED]",
                          "[NOT FOR CITATION]", "[DISCLOSE-BEFORE-USE]"]
    with open(RES, "w") as f:
        json.dump(RES_DATA, f, indent=2, default=str)
    print("checks=%d fail=%d" % (len(CHECKS), len(fails)), flush=True)
    if fails:
        print("FAILED:", fails, flush=True)
        sys.exit(1)
    print("ALL PASS", flush=True)


if __name__ == "__main__":
    main()
