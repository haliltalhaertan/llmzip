# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""coverage_v2.py — C1+C3 ek testleri: kapsam, mutasyon-oldurme, giris retleri.

Kaynak: dondurulmus arsivdeki verify.py'nin birebir mantik kopyasini gomulu
tasir (arsiv: .../round4/rank_crossing_certificates/verify.py, commit
1021083d4f2faebda760546e1217b4de1eef87ea). Arsive yazilmaz; duzeltme yalnizca
ek sarmalayicidir (cozum mantigi degismez). Bagimsiz denetimden GECMEMISTIR.

Kullanim:
  OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \\
  NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /home/mdp/muse-work/ml-python -B coverage_v2.py
Stdlib-only. Cikis sifirdan farkliysa bir beklenti bozulmustur.
"""
import inspect
import math
import sys
from fractions import Fraction as F

# ---------------- yardimcilar (arsivden birebir) ----------------
def fr(x):
    return x if isinstance(x, F) else F(x)

def P4(a, b, u, v):
    return (fr(a), fr(b), fr(u), fr(v))

class DomainError(Exception):
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

class Unresolved(Exception):
    pass

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

# ---------------- certify_pair: arsivden birebir (ad degisik) ----------------
def certify_pair_orig(p, q, L, R):
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
    for s in pts:
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
        if n is None:
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

def order_at(docs, z):
    res = list(range(len(docs)))
    for i in range(1, len(docs)):
        j = i
        while j > 0 and cmp_rank(docs[res[j]], docs[res[j - 1]], z) > 0:
            res[j], res[j - 1] = res[j - 1], res[j]
            j -= 1
    return res

# ---------------- topk_cert: arsivden birebir (ad degisik) ----------------
def topk_cert_orig(docs, K, prio, L, R):
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
            r = certify_pair_orig(docs[a], docs[b], L, R)
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
                out["unstable_witness"] = {"pair": [a, b], "kind": "interior-against-In",
                                           "cert": r}
                out["strict"] = out["prio"] = "CERTIFIED_UNSTABLE"
                return out
    any_tie = any(r["status"] in ("ISOLATED_TIES", "PERSISTENT_TIE")
                  for r in out["pairs"].values())
    out["strict"] = "CERTIFIED_STABLE" if not any_tie else "TIES_PRESENT"
    prio_ok = True
    for key, r in out["pairs"].items():
        a, b = (int(x) for x in key.split("vs"))
        if r["status"] in ("ISOLATED_TIES", "PERSISTENT_TIE"):
            if not prio[a] < prio[b]:
                prio_ok = False
    out["prio"] = "CERTIFIED_STABLE" if prio_ok else "PRIO_FLIPS_AT_TIE"
    return out

# ---------------- C3 duzeltmesi: adlandirilmis giris retleri ----------------
INPUT_ERROR = "INPUT_ERROR"
EMPTY_INTERVAL = "EMPTY_INTERVAL"        # L == R
INVERTED_INTERVAL = "INVERTED_INTERVAL"  # L > R
NONPOSITIVE_LEFT = "NONPOSITIVE_LEFT"    # L <= 0 (sartname: z > 0)

def validate_interval(L, R):
    """(L, R) -> hata kodu veya None. Siralama: pozitiflik, bosluk, yon."""
    L, R = fr(L), fr(R)
    if not L > 0:
        return NONPOSITIVE_LEFT
    if L == R:
        return EMPTY_INTERVAL
    if L > R:
        return INVERTED_INTERVAL
    return None

def _input_refusal(code, where):
    return {"status": INPUT_ERROR, "error": code, "direction": None, "ties": [],
            "notes": ["%s: malformed interval refused (%s); no certificate" % (where, code)],
            "sturm_calls": 0}

def certify_pair(p, q, L, R):
    code = validate_interval(L, R)
    if code is not None:
        return _input_refusal(code, "certify_pair")
    return certify_pair_orig(p, q, L, R)

def topk_cert(docs, K, prio, L, R):
    code = validate_interval(L, R)
    if code is not None:
        return {"sample": None, "in": None, "pairs": {}, "strict": INPUT_ERROR,
                "prio": INPUT_ERROR, "error": code, "unstable_witness": None,
                "cross_pairs": 0,
                "notes": ["topk_cert: malformed interval refused (%s)" % code]}
    return topk_cert_orig(docs, K, prio, L, R)

# ---------------- mutasyonlar (test gucunun kaniti; urun degil) ----------------
def _deg_of_P(p, q):
    co = P_coeffs(p, q)
    nz = [i for i, c in enumerate(co) if c != 0]
    return (max(nz) if nz else 0, all(c == 0 for c in co))

def mutant_domain(p, q, L, R):
    """DOMAIN_FAIL dali kirik varyant: hatayi STRICT diye yutar."""
    r = certify_pair_orig(p, q, L, R)
    if r["status"] == "DOMAIN_FAIL":
        r = dict(r, status="STRICT", direction=0)
    return r

def mutant_deg(p, q, L, R):
    """Dejenere-P (derece 0/1) dali kirik varyant: hep UNRESOLVED."""
    r = certify_pair_orig(p, q, L, R)
    d, z = _deg_of_P(p, q)
    if not z and d <= 1 and r["status"] == "STRICT":
        r = dict(r, status="UNRESOLVED")
    return r

def mutant_varies(p, q, L, R):
    """VARIES dali kirik varyant: donusu STRICT diye yutar."""
    r = certify_pair_orig(p, q, L, R)
    if r.get("direction") == "VARIES":
        r = dict(r, status="STRICT", direction=1)
    return r

def mutant_pt(p, q, L, R):
    """PERSISTENT_TIE kirik varyant: kalici esitligi goremeyen."""
    r = certify_pair_orig(p, q, L, R)
    if r["status"] == "PERSISTENT_TIE":
        r = dict(r, status="UNRESOLVED", direction=None)
    return r

# ---------------- izleyici: dal vuruslari + P derecesi gunlugu ----------------
class HitTracer:
    def __init__(self):
        self.hits = set()
        self.targets = {}
        for fn, tags in ((certify_pair_orig, ["DOMAIN_FAIL", "VARIES",
                                              "CERT-PERSISTENT_TIE"]),
                          (rational_roots, ["RAT-EARLY"]),
                          (topk_cert_orig, ["TOPK-PT-CHECK"])):
            src, start = inspect.getsourcelines(fn)
            for i, ln in enumerate(src):
                s = ln.strip()
                if fn is certify_pair_orig:
                    if s == 'out["status"] = "DOMAIN_FAIL"':
                        self.targets[(fn.__name__, start + i)] = "DOMAIN_FAIL-line"
                    elif s == 'out["direction"] = "VARIES"':
                        self.targets[(fn.__name__, start + i)] = "VARIES-line"
                    elif s == 'out["status"] = "PERSISTENT_TIE"':
                        self.targets[(fn.__name__, start + i)] = "CERT-PT-line"
                elif fn is rational_roots:
                    if s == "return [], False":
                        self.targets[(fn.__name__, start + i)] = "RAT-EARLY-line"
                elif fn is topk_cert_orig:
                    if "PERSISTENT_TIE" in s:
                        self.targets[(fn.__name__, start + i)] = "TOPK-PT-line"

    def _hook(self, frame, event, arg):
        if event == "line" and frame.f_code.co_filename == __file__:
            key = (frame.f_code.co_name, frame.f_lineno)
            if key in self.targets:
                self.hits.add(self.targets[key])
        return self._hook

    def run(self, fn):
        sys.settrace(self._hook)
        try:
            return fn()
        finally:
            sys.settrace(None)

DEG_LOG = []  # (cagri, deg, sifir_mi)

def _shim_rational_roots(P, limit=10 ** 6, cap=4096):
    co = _strip([fr(c) for c in P])
    DEG_LOG.append(("rational_roots", len(co) - 1, len(co) == 1 and co[0] == 0))
    return _real_rational_roots(P, limit, cap)

def _shim_sturm(P, L, R):
    co = _strip([fr(c) for c in P])
    DEG_LOG.append(("sturm", len(co) - 1, len(co) == 1 and co[0] == 0))
    return _real_sturm(P, L, R)

_real_rational_roots = rational_roots
_real_sturm = sturm_open_count

class Shimmed:
    def __enter__(self):
        g = globals()
        g["rational_roots"] = _shim_rational_roots
        g["sturm_open_count"] = _shim_sturm
        return self

    def __exit__(self, *a):
        g = globals()
        g["rational_roots"] = _real_rational_roots
        g["sturm_open_count"] = _real_sturm
        return False

# ---------------- test girdileri (hepsi Fraction) ----------------
IN = {
    "domain": (P4(0, 0, 0, 0), P4(1, 0, 1, 0), F(1, 16), F(16)),
    "deg1": (P4(-2, 0, 1, 0), P4(-2, 0, 1, 1), F(1, 4), F(2)),
    "deg0": (P4(1, 0, 1, 0), P4(2, 0, 1, 0), F(1, 4), F(2)),
    "varies": (P4(-1, 1, 1, 1), P4(-2, 2, 1, 3), F(1, 4), F(2)),
    "pt": (P4(2, 2, 4, 4), P4(1, 1, 1, 1), F(1, 16), F(16)),
}

def baseline_replay(cp, tk):
    """Arsiv testlerindeki tum certify/topk cagrilari (S6 dortlusu)."""
    F1 = P4(1, 1, 1, 10); F2 = P4(-1, -1, 10, 1)
    C1 = P4(-3, 4, 5, 10); C2 = P4(-2, 2, 2, 10)
    E1 = P4(1, 1, 0, 4); E2 = P4(1, 0, 1, 0)
    J = (F(1, 16), F(16))
    outs = []
    outs.append(tk([F1, F2, P4(-50, 0, 1, 0)], 1, {0: 0, 1: 1, 2: 2}, *J))
    outs.append(tk([C1, C2, P4(-100, 0, 1, 1)], 1, {0: 0, 1: 1, 2: 2}, *J))
    outs.append(tk([E1, E2], 1, {0: 0, 1: 1}, F(1, 4), F(4)))
    outs.append(tk([E1, E2], 1, {0: 1, 1: 0}, F(1, 4), F(4)))
    return outs

def mutant_topk_nosample(docs, K, prio, L, R):
    """Ornek-baglantisiz varyant: bag-kopisiz orneklemi atlar, ilk adayi zorlar.
    PT erisilmezlik iddiasini test eder: bu varyant PT'ye ulasir."""
    L, R = fr(L), fr(R)
    z0 = (L + R) / 2
    n = len(docs)

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
    out = {"sample": str(z0), "in": None, "pairs": {},
           "strict": None, "prio": None, "unstable_witness": None,
           "cross_pairs": 0}
    try:
        refset = prio_set(z0)
    except DomainError:
        out["strict"] = out["prio"] = "DOMAIN_FAIL"
        return out
    order = order_at(docs, z0)
    In = set(order[:K])
    out["in"] = sorted(In)
    for a in sorted(In):
        for b in range(n):
            if b in In:
                continue
            out["cross_pairs"] += 1
            r = certify_pair_orig(docs[a], docs[b], L, R)
            out["pairs"]["%dvs%d" % (a, b)] = r
    any_tie = any(r["status"] in ("ISOLATED_TIES", "PERSISTENT_TIE")
                  for r in out["pairs"].values())
    out["strict"] = "CERTIFIED_STABLE" if not any_tie else "TIES_PRESENT"
    out["prio"] = out["strict"]
    return out

# ---------------- beklentiler ----------------
EXPECTED = {
    "domain": ("DOMAIN_FAIL", None),
    "deg1": ("STRICT", -1),
    "deg0": ("STRICT", -1),
    "varies": ("ISOLATED_TIES", "VARIES"),
    "pt": ("PERSISTENT_TIE", 0),
}
MUTANT_OF = {
    "domain": mutant_domain,
    "deg1": mutant_deg,
    "deg0": mutant_deg,
    "varies": mutant_varies,
    "pt": mutant_pt,
}
C3_CASES = [
    ("empty", F(1), F(1), EMPTY_INTERVAL),
    ("inverted", F(2), F(1), INVERTED_INTERVAL),
    ("left-zero", F(0), F(1), NONPOSITIVE_LEFT),
    ("neg-left", F(-1), F(2), NONPOSITIVE_LEFT),
]

CHECKS = []
def check(name, cond, detail=""):
    CHECKS.append((name, bool(cond), str(detail)))
    if not cond:
        print("FAIL", name, detail, flush=True)

def _expect_pair(name, res):
    es, ed = EXPECTED[name]
    return res["status"] == es and res["direction"] == ed

def run_c1():
    for name, (p, q, L, R) in IN.items():
        good = certify_pair_orig(p, q, L, R)
        check("C1-%s-pass" % name, _expect_pair(name, good),
              (good["status"], good["direction"]))
        mut = MUTANT_OF[name](p, q, L, R)
        check("C1-%s-kills-mutant" % name, not _expect_pair(name, mut),
              (mut["status"], mut["direction"]))
        fixed = certify_pair(p, q, L, R)
        check("C1-%s-fixed-same" % name, fixed == good, "sarmalayici degistirmemeli")

def run_deg_log():
    DEG_LOG.clear()
    with Shimmed():
        for name, (p, q, L, R) in IN.items():
            certify_pair_orig(p, q, L, R)
    kinds = {(k, d) for (k, d, z) in DEG_LOG if not z}
    check("C1-deg1-seen", ("rational_roots", 1) in kinds
          and ("sturm", 1) in kinds, DEG_LOG)
    check("C1-deg0-seen", ("rational_roots", 0) in kinds
          and ("sturm", 0) in kinds, DEG_LOG)
    base_kinds = set()
    DEG_LOG.clear()
    with Shimmed():
        baseline_replay(certify_pair_orig, topk_cert_orig)
    base_kinds = {(k, d) for (k, d, z) in DEG_LOG if not z}
    check("C1-baseline-lacks-deg01",
          ("rational_roots", 1) not in base_kinds
          and ("rational_roots", 0) not in base_kinds, sorted(base_kinds))

def run_hits():
    tr = HitTracer()
    def body():
        for name, (p, q, L, R) in IN.items():
            certify_pair_orig(p, q, L, R)
    tr.run(body)
    for want in ("DOMAIN_FAIL-line", "VARIES-line", "CERT-PT-line",
                 "RAT-EARLY-line"):
        check("C1-hit-%s" % want, want in tr.hits, sorted(tr.hits))
    tr2 = HitTracer()
    tr2.run(lambda: baseline_replay(certify_pair_orig, topk_cert_orig))
    check("C1-baseline-misses-branches",
          "DOMAIN_FAIL-line" not in tr2.hits
          and "VARIES-line" not in tr2.hits
          and "CERT-PT-line" not in tr2.hits, sorted(tr2.hits))

def run_pt_unreach():
    T1, T2 = IN["pt"][0], IN["pt"][1]
    L, R = F(1, 16), F(16)
    cands = [(L + R) / 2, L, R, (2 * L + R) / 3, (L + 2 * R) / 3]
    tv = [cmp_rank(T1, T2, c) for c in cands]
    check("C1-PT-all5-tied", all(v == 0 for v in tv), tv)
    r = topk_cert_orig([T1, T2], 1, {0: 0, 1: 1}, L, R)
    check("C1-PT-topk-sample-tied",
          r["strict"] == "SAMPLE_TIED" and r["sample"] is None,
          (r["strict"], r["sample"]))
    m = mutant_topk_nosample([T1, T2], 1, {0: 0, 1: 1}, L, R)
    reached = any(v["status"] == "PERSISTENT_TIE"
                  for v in m["pairs"].values())
    check("C1-PT-mutant-reaches", reached, m["pairs"])
    check("C1-PT-test-kills-mutant",
          not (m["strict"] == "SAMPLE_TIED"), m["strict"])

def run_c3():
    p, q = P4(1, 0, 1, 0), P4(2, 0, 1, 0)
    docs = [p, q]
    for tag, L, R, code in C3_CASES:
        ro = certify_pair_orig(p, q, L, R)
        check("C3-pair-%s-orig-no-refusal" % tag,
              ro.get("status") != INPUT_ERROR, ro)
        rf = certify_pair(p, q, L, R)
        check("C3-pair-%s-fixed-refuses" % tag,
              rf["status"] == INPUT_ERROR and rf["error"] == code, rf)
        to = topk_cert_orig(docs, 1, {0: 0, 1: 1}, L, R)
        check("C3-topk-%s-orig-no-refusal" % tag,
              to.get("strict") != INPUT_ERROR, to.get("strict"))
        tf = topk_cert(docs, 1, {0: 0, 1: 1}, L, R)
        check("C3-topk-%s-fixed-refuses" % tag,
              tf["strict"] == INPUT_ERROR and tf["error"] == code, tf)
    ro = certify_pair_orig(p, q, F(1), F(1))
    check("C3-empty-spurious-dir0",
          ro["status"] == "STRICT" and ro["direction"] == 0, ro)
    a = certify_pair_orig(p, q, F(2), F(1))
    b = certify_pair_orig(p, q, F(1), F(2))
    check("C3-inverted-silently-swapped", a == b, (a, b))
    check("C3-validate-precedence",
          validate_interval(F(0), F(0)) == NONPOSITIVE_LEFT
          and validate_interval(F(1), F(1)) == EMPTY_INTERVAL
          and validate_interval(F(2), F(1)) == INVERTED_INTERVAL
          and validate_interval(F(1), F(2)) is None, "sira: pozitiflik, bosluk, yon")

def run_baseline():
    bo = baseline_replay(certify_pair_orig, topk_cert_orig)
    bf = baseline_replay(certify_pair, topk_cert)
    check("base-fixed-equals-orig", bo == bf, "gecerli aralikta ayni")
    ss = [o["strict"] for o in bf]
    check("base-S6-pattern", ss[0] == "CERTIFIED_STABLE"
          and ss[1] == "CERTIFIED_UNSTABLE", ss)

def main():
    run_c1()
    run_deg_log()
    run_hits()
    run_pt_unreach()
    run_c3()
    run_baseline()
    fails = [n for (n, ok, _) in CHECKS if not ok]
    print("checks=%d fail=%d" % (len(CHECKS), len(fails)), flush=True)
    print("hits/deg: C1 dallari vuruldu, deg0/1 gunlukte, PT-topk ulasilmaz.", flush=True)
    if fails:
        print("FAILED:", fails, flush=True)
        sys.exit(1)
    print("ALL PASS", flush=True)

if __name__ == "__main__":
    main()
