# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""certify_v2.py — dondurulmuş verify.py yerine geçen bağımsız ikili belgeleme yordamı.

Kapsam: certify_pair'in çözebildiklerini çözmesi (R2). Yalnızca stdlib,
yalnızca kesin `fractions.Fraction` aritmetiği. Orijinalin tutuculuk
sözünü korur: yanlış bir şeyi asla belgelemez; çözemediğini UNRESOLVED bırakır.

Orijinalden farklar (geri kalan her şey aynı mantık):
  (a) Uç savları farklıysa (+1/-1) ve Sturm n>=1 ise aralıkta gerçek bir
      kesişim vardır (teğet olamaz) — ucuz ayrıştırıcı.
  (b) Aynı-işaretli içlerde Sturm-biseksiyon ile kesin kök yalıtımı; her
      farklı kök ya kesin rasyonel bağ olarak ya da dar bir (lo,hi)
      braketiyle listelenir; braket uç savlarına göre kesişim/teğet ayrımı.
Bağ dizgesi: kesin bağ "s"; kesişim "cross(lo,hi)"; teğet "touch(lo,hi)".
"""
from fractions import Fraction as F

TOL_DEFAULT = F(1, 10 ** 9)
SPLIT_CAP_DEFAULT = 4096
SUBINT_CAP_DEFAULT = 64


def fr(x):
    return x if isinstance(x, F) else F(x)


def P4(a, b, u, v):
    return (fr(a), fr(b), fr(u), fr(v))


class DomainError(Exception):
    pass


class Unresolved(Exception):
    pass


def NZ(p, z):
    a, b, u, v = p
    return a + b * z, u + v * z


def cmp_rank(p, q, z):
    z = fr(z)
    N1, D1 = NZ(p, z)
    N2, D2 = NZ(q, z)
    if not (D1 > 0 and D2 > 0):
        raise DomainError("denominator not positive")
    s1 = (N1 > 0) - (N1 < 0)
    s2 = (N2 > 0) - (N2 < 0)
    if s1 != s2:
        return (s1 > s2) - (s1 < s2)
    if s1 == 0:
        return 0
    c = ((N1 * N1 * D2) > (N2 * N2 * D1)) - ((N1 * N1 * D2) < (N2 * N2 * D1))
    return c if s1 > 0 else -c


def _ratio(c):
    n, d = fr(c).as_integer_ratio()
    assert d > 0
    return n, d


def audit_cmp(p, q, z):
    z = fr(z)
    zn, zd = z.as_integer_ratio()
    assert zd > 0
    outs = []
    for (a, b, u, v) in (p, q):
        na, da = _ratio(a); nb, db = _ratio(b)
        nu, du = _ratio(u); nv, dv = _ratio(v)
        SN = na * db * zd + nb * da * zn
        DN = da * db * zd
        SD = nu * dv * zd + nv * du * zn
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
    L = SN1 * SN1 * SD2 * DN2 * DN2 * DD1
    R = SN2 * SN2 * SD1 * DN1 * DN1 * DD2
    c = (L > R) - (L < R)
    return c if s1 > 0 else -c


def vdual(p, q, z):
    v = cmp_rank(p, q, z)
    va = audit_cmp(p, q, z)
    assert v == va, "primary/audit comparator disagree"
    return v


def P_coeffs(p, q):
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
    Q0 = _Qeval(p, q, F(0)); Q1 = _Qeval(p, q, F(1))
    Q2 = _Qeval(p, q, F(2)); Q3 = _Qeval(p, q, F(3))
    d1 = Q1 - Q0
    d2 = Q2 - 2 * Q1 + Q0
    d3 = Q3 - 3 * Q2 + 3 * Q1 - Q0
    c3 = d3 / 6
    c2 = d2 / 2 - d3 / 2
    c1 = d1 - d2 / 2 + d3 / 3
    return [Q0, c1, c2, c3]


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


def _deflate(P, r):
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


def num_zero(p, L, R):
    a, b, _, _ = p
    if b == 0:
        return None
    z0 = -a / b
    return z0 if L <= z0 <= R else None


def _divisors(n):
    import math
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
    import math
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


# ---------------- kesin kök yalıtımı (R2b) ----------------
def isolate_roots(P, l, r, n, tol=TOL_DEFAULT, cap=SPLIT_CAP_DEFAULT):
    """(l,r) içindeki n>=1 farklı kökü kesin yalıtır.

    Döner: dict(ok, exacts, brackets, sturm_calls, note).
    Değişmez: bekleyen aralıklar ayrıktır; kaydedilen kesin kökler +
    braket/bekleyen kökleri toplamı n'e eşittir. Her tutarsızlık -> ok=False.
    """
    l, R = fr(l), fr(r)
    sc = 0
    if n is None or n < 1:
        return {"ok": False, "exacts": [], "brackets": [],
                "sturm_calls": 0, "note": "no positive count to isolate"}
    pending = [(l, R, n)]
    exacts = []
    brackets = []
    splits = 0
    while pending:
        a, b, c = pending.pop()
        if c <= 0:
            continue
        if c == 1 and (b - a) <= tol:
            brackets.append((a, b))
            continue
        if (b - a) < F(1, 2 ** 200):
            return {"ok": False, "exacts": exacts, "brackets": brackets,
                    "sturm_calls": sc, "note": "width floor with c=%d" % c}
        splits += 1
        if splits > cap:
            return {"ok": False, "exacts": exacts, "brackets": brackets,
                    "sturm_calls": sc, "note": "split budget exceeded"}
        m = (a + b) / 2
        if peval(P, m) == 0:
            exacts.append(m)
            cl = sturm_open_count(P, a, m)
            cr = sturm_open_count(P, m, b)
            sc += 2
            if cl is None or cr is None or cl + cr != c - 1:
                return {"ok": False, "exacts": exacts, "brackets": brackets,
                        "sturm_calls": sc,
                        "note": "count mismatch after exact hit"}
            if cl > 0:
                pending.append((a, m, cl))
            if cr > 0:
                pending.append((m, b, cr))
        else:
            cl = sturm_open_count(P, a, m)
            cr = sturm_open_count(P, m, b)
            sc += 2
            if cl is None or cr is None or cl + cr != c:
                return {"ok": False, "exacts": exacts, "brackets": brackets,
                        "sturm_calls": sc, "note": "count mismatch at split"}
            if cl > 0:
                pending.append((a, m, cl))
            if cr > 0:
                pending.append((m, b, cr))
    if len(brackets) + len(exacts) != n:
        return {"ok": False, "exacts": exacts, "brackets": brackets,
                "sturm_calls": sc, "note": "coverage mismatch"}
    exacts.sort()
    brackets.sort()
    return {"ok": True, "exacts": exacts, "brackets": brackets,
            "sturm_calls": sc, "note": ""}


# ---------------- ikili belgeleme yordamı v2 ----------------
def certify_pair(p, q, L, R, tol=TOL_DEFAULT, isolate=True,
                 split_cap=SPLIT_CAP_DEFAULT, subint_cap=SUBINT_CAP_DEFAULT):
    """Kapalı J=[L,R] için ikili belge (v2: ayrıştırıcı + yalıtım).

    Dönüş: dict(status, direction, ties, notes, sturm_calls, xbrackets,
    disc_fired). status: STRICT | ISOLATED_TIES | PERSISTENT_TIE |
    UNRESOLVED | DOMAIN_FAIL. VARIES yönü kesişim içerir (kararlı DEĞİL).
    isolate=False: yalnızca ucuz ayrıştırıcı (kıyas ölçümü için).
    """
    out = {"status": None, "direction": None, "ties": [],
           "notes": [], "sturm_calls": 0, "xbrackets": [], "disc_fired": 0}
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
                                "bisection still finds rational hits exactly")
        for rr in rrs:
            if L < rr < R:
                cuts.add(rr)
    V = {}
    for s in sorted(cuts):
        v = vdual(p, q, s)
        V[s] = v
        if v == 0:
            out["ties"].append(str(s))
    dirs = set()
    flipped = False
    if is_zero:
        out["notes"].append("P identically zero: |f_p|==|f_q| wherever defined; "
                            "order from numerator signs only")
    pts = sorted(cuts)
    stack = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    done = 0
    while stack:
        l, r = stack.pop()
        if l == r:
            continue
        done += 1
        if done > subint_cap:
            out["status"] = "UNRESOLVED"
            out["notes"].append("subinterval budget exceeded")
            return out
        m = (l + r) / 2
        vm = vdual(p, q, m)
        if vm == 0:
            if is_zero:
                dirs.add(0)
                out["ties"].append("persistent(%s,%s)" % (l, r))
                out["notes"].append("persistent-tie subinterval (%s,%s)" % (l, r))
                continue
            if peval(P, m) != 0:
                out["status"] = "UNRESOLVED"
                out["notes"].append("tie at interior sample %s with P(m)!=0" % m)
                return out
            out["ties"].append(str(m))
            V[m] = 0
            out["notes"].append("exact rational tie at midpoint %s: split" % m)
            stack.append((l, m))
            stack.append((m, r))
            continue
        N1m = p[0] + p[1] * m
        N2m = q[0] + q[1] * m
        s1 = (N1m > 0) - (N1m < 0)
        s2 = (N2m > 0) - (N2m < 0)
        if s1 != s2:
            dirs.add(vm)
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
        if n is None:
            out["status"] = "UNRESOLVED"
            return out
        if n == 0:
            dirs.add(vm)
            out["notes"].append("(%s,%s): sturm=0 same-sign roots, "
                                "strict order constant" % (l, r))
            continue
        vl = V.get(l, vdual(p, q, l))
        vr = V.get(r, vdual(p, q, r))
        V[l] = vl
        V[r] = vr
        if vl != 0 and vr != 0 and vl != vr:
            out["disc_fired"] += 1
            out["notes"].append(
                "(%s,%s): discriminator: endpoint verdicts differ (%d vs %d) "
                "with sturm=%d -> >=1 genuine crossing" % (l, r, vl, vr, n))
            if not isolate:
                out["xbrackets"].append({"lo": l, "hi": r, "kind": "cross"})
                out["ties"].append("cross(%s,%s)" % (l, r))
                flipped = True
                continue
            iso = isolate_roots(P, l, r, n, tol=tol, cap=split_cap)
            out["sturm_calls"] += iso["sturm_calls"]
            if not iso["ok"]:
                out["status"] = "UNRESOLVED"
                out["notes"].append("(%s,%s): isolation failed: %s" % (l, r, iso["note"]))
                return out
            n_cross = 0
            for e in iso["exacts"]:
                if vdual(p, q, e) != 0:
                    out["status"] = "UNRESOLVED"
                    out["notes"].append("exact root %s is not a tie" % e)
                    return out
                out["ties"].append(str(e))
            for (a, b) in iso["brackets"]:
                if peval(P, a) == 0 or peval(P, b) == 0:
                    out["status"] = "UNRESOLVED"
                    out["notes"].append("bracket endpoint is a root")
                    return out
                va = vdual(p, q, a)
                vb = vdual(p, q, b)
                if va == 0 or vb == 0:
                    out["status"] = "UNRESOLVED"
                    out["notes"].append("contradiction: zero verdict off P-root")
                    return out
                if va != vb:
                    n_cross += 1
                    out["xbrackets"].append({"lo": a, "hi": b, "kind": "cross"})
                    out["ties"].append("cross(%s,%s)" % (a, b))
                else:
                    out["xbrackets"].append({"lo": a, "hi": b, "kind": "touch"})
                    out["ties"].append("touch(%s,%s)" % (a, b))
            if n_cross < 1:
                out["status"] = "UNRESOLVED"
                out["notes"].append("discriminator/isolator disagree")
                return out
            flipped = True
            continue
        if not isolate:
            out["status"] = "UNRESOLVED"
            out["notes"].append("(%s,%s): sturm=%d same-sign P-roots -> "
                                "UNRESOLVED (touch or crossing)" % (l, r, n))
            return out
        iso = isolate_roots(P, l, r, n, tol=tol, cap=split_cap)
        out["sturm_calls"] += iso["sturm_calls"]
        if not iso["ok"]:
            out["status"] = "UNRESOLVED"
            out["notes"].append("(%s,%s): isolation failed: %s" % (l, r, iso["note"]))
            return out
        n_cross = 0
        for e in iso["exacts"]:
            if vdual(p, q, e) != 0:
                out["status"] = "UNRESOLVED"
                out["notes"].append("exact root %s is not a tie" % e)
                return out
            out["ties"].append(str(e))
        for (a, b) in iso["brackets"]:
            if peval(P, a) == 0 or peval(P, b) == 0:
                out["status"] = "UNRESOLVED"
                out["notes"].append("bracket endpoint is a root")
                return out
            va = vdual(p, q, a)
            vb = vdual(p, q, b)
            if va == 0 or vb == 0:
                out["status"] = "UNRESOLVED"
                out["notes"].append("contradiction: zero verdict off P-root")
                return out
            if va != vb:
                n_cross += 1
                out["xbrackets"].append({"lo": a, "hi": b, "kind": "cross"})
                out["ties"].append("cross(%s,%s)" % (a, b))
            else:
                out["xbrackets"].append({"lo": a, "hi": b, "kind": "touch"})
                out["ties"].append("touch(%s,%s)" % (a, b))
        if n_cross > 0:
            flipped = True
        else:
            dirs.add(vm)
    if out["status"] == "UNRESOLVED":
        return out
    if flipped:
        out["status"] = "ISOLATED_TIES"
        out["direction"] = "VARIES"
        out["notes"].append("certified flip across listed ties/brackets: "
                            "piecewise order, NOT stable")
        return out
    nz = sorted(d for d in dirs if d != 0)
    if len(nz) > 1:
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
        out["status"] = "ISOLATED_TIES"
        out["direction"] = nz[0]
        return out
    if out["ties"]:
        out["status"] = "ISOLATED_TIES"
    else:
        out["status"] = "STRICT"
    out["direction"] = nz[0] if nz else 0
    return out


if __name__ == "__main__":
    E1 = P4(1, 1, 0, 4)
    E2 = P4(1, 0, 1, 0)
    t = certify_pair(E1, E2, F(1, 4), F(4))
    assert t["status"] == "ISOLATED_TIES" and t["direction"] == 1, t
    C1 = P4(-3, 4, 5, 10)
    C2 = P4(-2, 2, 2, 10)
    w = certify_pair(C1, C2, F(1, 16), F(16))
    print("tangent:", t["status"], t["direction"], t["ties"])
    print("witness:", w["status"], w["direction"], w["ties"][:6])
    print("SMOKE OK")
