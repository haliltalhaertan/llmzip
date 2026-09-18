"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
cert_validator_v3.py -- INDEPENDENT certificate validator (BULGU-5 repair).

This module imports NOTHING from certify_v3.py (or any archived package
file): the exact comparator, the P expansion, and the Sturm coverage
machinery below are written fresh here, so a generator bug cannot certify
itself through a shared helper. The generator's claimed `direction` is
never used as an oracle: every order fact is re-derived from scratch, and
every coverage fact is re-proven with an independent Sturm count.

`validate_cert_v3(p, q, L, R, cert)` returns None (accept) or an error
string (reject). Refusals (DOMAIN_FAIL / UNRESOLVED) claim nothing and are
always accepted. Everything else must survive:

  1. every claimed exact tie re-evaluates to 0 with the independent
     comparator and lies in [L,R];
  2. every claimed bracket (from `ties` cross(...)/touch(...) entries AND
     from `xbrackets`) lies in [L,R], holds EXACTLY one P-root
     (independent Sturm count == 1), has non-root endpoints with nonzero
     verdicts, and its kind matches the re-derived endpoint orders
     (cross <=> differing nonzero orders; touch <=> agreeing nonzero);
  3. interval/root COVERAGE (not a finite sample scan): critical points =
     {L,R} + exact ties + bracket endpoints partition J; every cell outside
     proven single-root bracket interiors is re-proven P-root-free
     (independent Sturm count == 0) and sampled; a tie inside such a cell
     rejects. A finite 17/33-point scan is falsification only and is NOT
     used as a proof step here;
  4. status semantics against the re-derived evidence:
     STRICT: no ties/brackets, all cells and endpoints agree with direction.
     ISOLATED_TIES with a single direction d: no crossing evidence
       (no cross bracket, no exact tie flanked by differing cell orders),
       every cell order == d, endpoints in {d, listed-tie 0}.
     ISOLATED_TIES / VARIES: at least two distinct nonzero orders among
       cell samples and bracket endpoint verdicts (else "VARIES without
       two observed signs").
     PERSISTENT_TIE: direction 0, P identically zero, every cell a tie.

Only stdlib, only exact fractions.Fraction arithmetic. `python3 -B`.
"""
from fractions import Fraction as F


def _fr(x):
    return x if isinstance(x, F) else F(x)


def _cmp(p, q, z):
    """Independent exact comparator (fresh integer/rational code)."""
    z = _fr(z)
    (a1, b1, u1, v1), (a2, b2, u2, v2) = p, q
    n1, d1 = a1 + b1 * z, u1 + v1 * z
    n2, d2 = a2 + b2 * z, u2 + v2 * z
    if not (d1 > 0 and d2 > 0):
        raise ValueError("denominator not positive at %s" % z)
    s1 = (n1 > 0) - (n1 < 0)
    s2 = (n2 > 0) - (n2 < 0)
    if s1 != s2:
        return (s1 > s2) - (s1 < s2)
    if s1 == 0:
        return 0
    c = ((n1 * n1 * d2) > (n2 * n2 * d1)) - ((n1 * n1 * d2) < (n2 * n2 * d1))
    return c if s1 > 0 else -c


def _pcoeffs(p, q):
    (a1, b1, u1, v1), (a2, b2, u2, v2) = p, q
    return [a1 * a1 * u2 - a2 * a2 * u1,
            (2 * a1 * b1 * u2 + a1 * a1 * v2)
            - (2 * a2 * b2 * u1 + a2 * a2 * v1),
            (2 * a1 * b1 * v2 + b1 * b1 * u2)
            - (2 * a2 * b2 * v1 + b2 * b2 * u1),
            b1 * b1 * v2 - b2 * b2 * v1]


def _strip(co):
    co = [_fr(c) for c in co]
    while len(co) > 1 and co[-1] == 0:
        co.pop()
    return co


def _peval(co, z):
    z = _fr(z)
    s = F(0)
    for c in reversed(co):
        s = s * z + c
    return s


def _pderiv(co):
    if len(co) <= 1:
        return [F(0)]
    out = _strip([co[k] * k for k in range(1, len(co))])
    return out


def _pdivmod(A, B):
    A = list(A)
    B = _strip(list(B))
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


def _sturm(P):
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


def _var(vals):
    nz = [v for v in vals if v != 0]
    n = 0
    for i in range(1, len(nz)):
        if (nz[i] > 0) != (nz[i - 1] > 0):
            n += 1
    return n


def _deflate(P, r):
    P = _strip(P)
    r = _fr(r)
    n = len(P) - 1
    if n < 1:
        raise ValueError("cannot deflate constant")
    Q = [F(0)] * n
    Q[-1] = P[-1]
    for k in range(n - 2, -1, -1):
        Q[k] = P[k + 1] + r * Q[k + 1]
    if not (P[0] + r * Q[0] == 0):
        raise ValueError("non-root deflation")
    return _strip(Q)


def _open_count(P, L, R):
    """Independent Sturm count of DISTINCT P-roots on the open interval."""
    P = _strip(P)
    L, R = _fr(L), _fr(R)
    if len(P) == 1 and P[0] == 0:
        return None
    Q = list(P)
    try:
        while _peval(Q, L) == 0:
            Q = _deflate(Q, L)
        while _peval(Q, R) == 0:
            Q = _deflate(Q, R)
    except ValueError:
        return None
    if len(Q) == 1 and Q[0] == 0:
        return 0
    S = _sturm(Q)
    return _var([_peval(s, L) for s in S]) - _var([_peval(s, R) for s in S])


def _parse_ties(ties):
    """Split tie entries into exact rationals, brackets, persistent pieces."""
    exacts, brackets, persist = [], [], []
    for e in ties:
        if e.startswith("cross(") and e.endswith(")"):
            lo, hi = e[len("cross("):-1].split(",")
            brackets.append((_fr(lo), _fr(hi), "cross"))
        elif e.startswith("touch(") and e.endswith(")"):
            lo, hi = e[len("touch("):-1].split(",")
            brackets.append((_fr(lo), _fr(hi), "touch"))
        elif e.startswith("persistent(") and e.endswith(")"):
            lo, hi = e[len("persistent("):-1].split(",")
            persist.append((_fr(lo), _fr(hi)))
        else:
            exacts.append(_fr(e))
    return exacts, brackets, persist


def validate_cert_v3(p, q, L, R, cert):
    """Independent re-validation. None = accept; string = reject reason."""
    st = cert.get("status")
    if st in ("DOMAIN_FAIL", "UNRESOLVED"):
        return None
    L, R = _fr(L), _fr(R)
    if not (L < R):
        return "validator: degenerate interval with a verdict"
    P = _strip(_pcoeffs(p, q))
    is_zero = len(P) == 1 and P[0] == 0
    try:
        exacts, tbrackets, persist = _parse_ties(cert.get("ties", []))
    except Exception as e:
        return "validator: unparsable ties entry (%s)" % e
    xb = []
    for x in cert.get("xbrackets", []):
        try:
            xb.append((_fr(x["lo"]), _fr(x["hi"]), x["kind"]))
        except Exception as e:
            return "validator: unparsable xbracket (%s)" % e
    brackets = list(tbrackets) + list(xb)
    # --- 1. exact ties are genuine and in range ---
    for e in exacts:
        if not (L <= e <= R):
            return "exact tie %s out of range" % e
        try:
            v = _cmp(p, q, e)
        except ValueError:
            return "exact tie %s outside domain" % e
        if v != 0:
            return "exact tie %s not a tie" % e
    # --- 2. brackets hold exactly one root; kind matches re-derived order ---
    observed = set()
    for (a, b, kind) in brackets:
        if not (L <= a < b <= R):
            return "bracket (%s,%s) out of range" % (a, b)
        if kind not in ("cross", "touch"):
            return "unknown bracket kind %s" % kind
        if _peval(P, a) == 0 or _peval(P, b) == 0:
            return "bracket (%s,%s) endpoint is a root" % (a, b)
        if _open_count(P, a, b) != 1:
            return "bracket (%s,%s) count != 1" % (a, b)
        try:
            va, vb = _cmp(p, q, a), _cmp(p, q, b)
        except ValueError:
            return "bracket (%s,%s) endpoint outside domain" % (a, b)
        if va == 0 or vb == 0:
            return "bracket (%s,%s) endpoint is a tie" % (a, b)
        observed.add(va)
        observed.add(vb)
        if kind == "cross" and not (va != vb):
            return "cross bracket (%s,%s) without sign change" % (a, b)
        if kind == "touch" and not (va == vb):
            return "touch bracket (%s,%s) with sign change" % (a, b)
    # --- 3. coverage: partition at critical points, prove cells root-free ---
    # Numerator zeros are recomputed independently (exact linear roots):
    # they bound every sign change, so each cell has constant signs.
    # A cell with DIFFERING signs is sign-decided (no tie and no crossing
    # possible no matter how many P-roots it holds -- this is the benign
    # differing-sign P-root the generator never needs to list). A cell
    # with AGREEING signs must be re-proven P-root-free and sampled.
    numzeros = set()
    for (a, b, u, v) in (p, q):
        if b != 0:
            z0 = -a / b
            if L <= z0 <= R:
                numzeros.add(z0)
    for (a, b, _) in brackets:
        for z0 in numzeros:
            if a < z0 < b:
                return ("bracket (%s,%s) spans numerator zero %s" % (a, b, z0))
    crit = {L, R} | set(exacts) | set(numzeros)
    for (a, b, _) in brackets:
        crit.add(a)
        crit.add(b)
    pts = sorted(crit)
    cell_dirs = []  # (c0, c1, dir); bracket interiors recorded separately
    for i in range(len(pts) - 1):
        c0, c1 = pts[i], pts[i + 1]
        if c0 == c1:
            continue
        if any(a <= c0 and c1 <= b for (a, b, _) in brackets):
            if not any(a == c0 and b == c1 for (a, b, _) in brackets):
                return ("coverage gap: cell (%s,%s) inside a bracket "
                        "without matching endpoints" % (c0, c1))
            continue
        w = (c0 + c1) / 2
        try:
            vw = _cmp(p, q, w)
        except ValueError:
            return "coverage gap: cell (%s,%s) sample outside domain" % (c0, c1)
        (a1, b1, _, _), (a2, b2, _, _) = p, q
        s1 = ((a1 + b1 * w) > 0) - ((a1 + b1 * w) < 0)
        s2 = ((a2 + b2 * w) > 0) - ((a2 + b2 * w) < 0)
        if is_zero:
            # P identically zero: no P-roots can hide; the sample is the
            # verdict (0 on persistent pieces, +/- on sign-decided ones).
            cell_dirs.append((c0, c1, vw))
            observed.add(vw)
            continue
        if s1 != s2:
            for z0 in numzeros:
                if c0 < z0 < c1:
                    return ("sign change inside sign-decided cell "
                            "(%s,%s)" % (c0, c1))
            if vw == 0:
                return "tie at %s with differing numerator signs" % w
            cell_dirs.append((c0, c1, vw))
            observed.add(vw)
            continue
        if s1 == 0:
            return ("both numerators vanish inside cell "
                    "(%s,%s)" % (c0, c1))
        c = _open_count(P, c0, c1)
        if c is None or c != 0:
            return ("coverage gap: cell (%s,%s) not proven root-free "
                    "(count=%s)" % (c0, c1, c))
        if vw == 0:
            return "tie at %s inside proven root-free cell" % w
        cell_dirs.append((c0, c1, vw))
        observed.add(vw)
    # --- persistent pieces need P==0 and all-tie cells inside ---
    for (a, b) in persist:
        if not is_zero:
            return "persistent piece (%s,%s) with nonzero P" % (a, b)
        for (c0, c1, vw) in cell_dirs:
            if a <= c0 and c1 <= b and vw != 0:
                return ("persistent piece (%s,%s) contradicted at cell "
                        "(%s,%s)" % (a, b, c0, c1))
    # --- endpoints: verdicts must fit the evidence or be listed ties ---
    try:
        vL, vR = _cmp(p, q, L), _cmp(p, q, R)
    except ValueError:
        return "endpoint outside domain with a verdict"
    for vend, tag in ((vL, L), (vR, R)):
        if vend == 0 and _fr(tag) not in exacts:
            return "endpoint tie at %s not listed" % tag
    # --- 4. status semantics ---
    d = cert.get("direction")
    if st == "STRICT":
        if exacts or brackets or persist:
            return "STRICT with listed ties/brackets"
        if any(vw != d for (_, _, vw) in cell_dirs):
            return "STRICT contradicted by cell evidence"
        if vL != d or vR != d:
            return "STRICT contradicted at an endpoint"
        return None
    if st == "ISOLATED_TIES" and d == "VARIES":
        nz = sorted(v for v in observed if v != 0)
        if len(set(nz)) < 2:
            return "VARIES without two observed signs"
        return None
    if st == "ISOLATED_TIES":
        if d not in (1, -1):
            return "single-direction cert with direction %s" % (d,)
        for (a, b, kind) in brackets:
            if kind == "cross":
                return ("single-direction cert contains crossing "
                        "bracket (%s,%s)" % (a, b))
        # every exact tie must be flanked by agreeing direction-d cells
        # (or sit at J's endpoints, where one side is the endpoint tie).
        for e in exacts:
            if e == L or e == R:
                continue
            left = [vw for (c0, c1, vw) in cell_dirs if c1 == e]
            right = [vw for (c0, c1, vw) in cell_dirs if c0 == e]
            if len(left) != 1 or len(right) != 1:
                return "tie %s lacks two-sided cell evidence" % e
            if left[0] != d or right[0] != d:
                return ("tie %s flanked by non-%s cell orders "
                        "(%s vs %s)" % (e, d, left[0], right[0]))
        for (c0, c1, vw) in cell_dirs:
            if any(a <= c0 and c1 <= b for (a, b) in persist):
                if vw != 0:
                    return ("persistent piece contradicted at cell "
                            "(%s,%s)" % (c0, c1))
                continue
            if vw != d:
                return ("single-direction %s contradicted by cell "
                        "evidence %s" % (d, vw))
        if vL != d and vL != 0:
            return "single-direction %s contradicted at L" % d
        if vR != d and vR != 0:
            return "single-direction %s contradicted at R" % d
        return None
    if st == "PERSISTENT_TIE":
        if d != 0:
            return "PERSISTENT_TIE with direction %s" % (d,)
        if not is_zero:
            return "PERSISTENT_TIE with nonzero P"
        if any(vw != 0 for (_, _, vw) in cell_dirs):
            return "PERSISTENT_TIE contradicted by cell evidence"
        return None
    return "unknown status %s" % (st,)
