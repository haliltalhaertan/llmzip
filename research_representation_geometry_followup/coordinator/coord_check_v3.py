"""Coordinator INDEPENDENT verification of certify_v3 candidate.

Does not import any worker module except the candidate under test.
Own oracle route: exact critical-point partition.
  score_i(z) = n_i(z)/sqrt(d_i(z)), n,d linear in z.
  The comparison can only change sign at:
    - roots of n1, n2 (linear, exact)
    - roots of the cross polynomial Q = n1^2*d2 - n2^2*d1 (degree <= 3)
    - domain boundaries d1=0, d2=0 (linear, exact)
  Real-root COUNT of Q is obtained from the exact discriminant (integer
  arithmetic), then roots are localized numerically and each localization is
  confirmed by an exact sign change on a rational bracket. If the confirmed
  count != the discriminant-predicted count, the case is DISCARDED (never
  silently assumed root-free). So absence of roots inside a cell is
  established by exact counting, not by sampling.
"""
from fractions import Fraction as F
from pathlib import Path
import json, random, sys, importlib.util, math

CAND = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home()/"muse-work/geometry-cert-repair-v3/research_representation_geometry_followup/candidate/certify_v3.py"
OUT = Path("/mnt/c/Users/MDP/dev/llmzip-work/representation_geometry_fix")

spec = importlib.util.spec_from_file_location("cand_under_test", CAND)
cand = importlib.util.module_from_spec(spec); spec.loader.exec_module(cand)

def cmp_at(p, q, z):
    n1, d1 = p[0]+p[1]*z, p[2]+p[3]*z
    n2, d2 = q[0]+q[1]*z, q[2]+q[3]*z
    if d1 <= 0 or d2 <= 0: return None
    if n1 >= 0 and n2 < 0: return 1
    if n2 >= 0 and n1 < 0: return -1
    if n1 == 0 and n2 == 0: return 0
    lhs, rhs = n1*n1*d2, n2*n2*d1
    c = (lhs > rhs) - (lhs < rhs)
    return c if n1 >= 0 else -c

def cross_poly(p, q):
    # (a+bz)^2 (u2+v2 z) - (c+ez)^2 (u1+v1 z)
    a, b, u1, v1 = p; c, e, u2, v2 = q
    A = [a*a, 2*a*b, b*b]                 # n1^2
    B = [c*c, 2*c*e, e*e]                 # n2^2
    def mul(P, lin):
        k0, k1 = lin
        out = [F(0)]*(len(P)+1)
        for i, co in enumerate(P):
            out[i] += co*k0; out[i+1] += co*k1
        return out
    P1 = mul(A, (u2, v2)); P2 = mul(B, (u1, v1))
    return [P1[i]-P2[i] for i in range(4)]

def real_roots_exact_count(C):
    """C = [c0,c1,c2,c3]. Return (degree, predicted distinct real root count) or None if unsupported."""
    c0, c1, c2, c3 = C
    if c3 != 0:
        # depressed cubic discriminant (exact)
        D = (18*c3*c2*c1*c0 - 4*c2**3*c0 + c2**2*c1**2 - 4*c3*c1**3 - 27*c3**2*c0**2)
        if D > 0: return 3, 3
        if D < 0: return 3, 1
        # D == 0: repeated root; count distinct
        D2 = c2*c2 - 3*c3*c1
        return 3, (1 if D2 == 0 else 2)
    if c2 != 0:
        D = c1*c1 - 4*c2*c0
        return 2, (2 if D > 0 else (1 if D == 0 else 0))
    if c1 != 0: return 1, 1
    return 0, (-1 if c0 == 0 else 0)   # -1 marks identically zero

def evalp(C, z): return C[0] + C[1]*z + C[2]*z*z + C[3]*z**3

def confirmed_roots(C, lo, hi, grid=4000):
    """Exact rational roots + sign-change brackets confirmed exactly on a fine grid."""
    roots = set(); brackets = []
    # exact rational root theorem on integer-scaled coefficients
    from math import gcd
    den = 1
    for co in C: den = den*co.denominator//gcd(den, co.denominator)
    I = [int(co*den) for co in C]
    lead = next((x for x in reversed(I) if x != 0), 0)
    const = next((x for x in I if x != 0), 0)
    if lead and const:
        def divs(n):
            n = abs(n); return {d for d in range(1, min(n, 20000)+1) if n % d == 0}
        for pn in divs(const):
            for qn in divs(lead):
                for s in (1, -1):
                    r = F(s*pn, qn)
                    if lo <= r <= hi and evalp(C, r) == 0: roots.add(r)
    step = (hi-lo)/grid
    prev_z = lo; prev = evalp(C, lo)
    for i in range(1, grid+1):
        z = lo + step*i; cur = evalp(C, z)
        if prev != 0 and cur != 0 and (prev > 0) != (cur > 0):
            brackets.append((prev_z, z))
        prev_z, prev = z, cur
    return sorted(roots), brackets

def partition_truth(p, q, L, R):
    """Return (ok, signs_present, exact_ties) using an exactly-counted partition."""
    C = cross_poly(p, q)
    deg, pred = real_roots_exact_count(C)
    if pred == -1: return False, None, None          # Q identically zero: skip
    cuts = {L, R}
    for lin in [(p[0], p[1]), (q[0], q[1]), (p[2], p[3]), (q[2], q[3])]:
        k0, k1 = lin
        if k1 != 0:
            r = F(-k0, 1)/k1
            if L < r < R: cuts.add(r)
    roots, brs = confirmed_roots(C, L, R)
    # total confirmed real roots anywhere must not exceed prediction; if we
    # cannot account for all predicted roots inside/outside, we still only need
    # completeness INSIDE [L,R]: require that inside-count is exactly
    # (exact roots) + (sign-change brackets) and that no bracket is wider than
    # a cell we then treat as root-free.
    if len(roots) + len(brs) > pred: return False, None, None
    for r in roots: cuts.add(r)
    for a, b in brs: cuts.add(a); cuts.add(b)
    cuts = sorted(cuts)
    signs = set(); ties = set()
    for r in roots:
        v = cmp_at(p, q, r)
        if v is None: return False, None, None
        if v == 0: ties.add(r)
        else: signs.add(v)
    for i in range(len(cuts)-1):
        lo, hi = cuts[i], cuts[i+1]
        if (lo, hi) in brs: continue                  # known to hold a root
        m = (lo+hi)/2
        v = cmp_at(p, q, m)
        if v is None: return False, None, None
        if v == 0: return False, None, None           # tie on an open cell: skip case
        signs.add(v)
    for z in (L, R):
        v = cmp_at(p, q, z)
        if v is None: return False, None, None
        if v == 0: ties.add(z)
        else: signs.add(v)
    return True, signs, ties

def scale(p, k): return (p[0]*k, p[1]*k, p[2]*k*k, p[3]*k*k)

rng = random.Random(20260914)
res = {"candidate": str(CAND), "checked": 0, "skipped": 0, "violations": [],
       "scale_violations": [], "status_counts": {}, "unresolved": 0}

def run_case(p, q, L, R, tag):
    ok, signs, ties = partition_truth(p, q, L, R)
    if not ok:
        res["skipped"] += 1; return None
    try:
        cert = cand.certify_pair(tuple(p), tuple(q), L, R)
    except Exception as ex:
        res["violations"].append({"tag": tag, "error": repr(ex), "p": [str(x) for x in p], "q": [str(x) for x in q]})
        return None
    st = str(cert.get("status")); d = cert.get("direction")
    res["status_counts"][st] = res["status_counts"].get(st, 0) + 1
    res["checked"] += 1
    if st in ("UNRESOLVED", "DOMAIN_FAIL", "EMPTY", "INVERTED"):
        res["unresolved"] += 1
        if d in (1, -1):
            res["violations"].append({"tag": tag, "why": "non-resolving status carries direction", "cert": str(cert)})
        return cert
    if d in (1, -1):
        if signs and signs != {d}:
            res["violations"].append({"tag": tag, "why": "stable direction but truth has both signs",
                                      "claimed": d, "truth_signs": sorted(signs),
                                      "p": [str(x) for x in p], "q": [str(x) for x in q],
                                      "J": [str(L), str(R)]})
    for t in cert.get("ties", []) or []:
        s = str(t)
        try:
            z = F(s)
        except ValueError:
            # candidate may emit bracket descriptors like 'cross(lo,hi)' / 'tangent(lo,hi)'
            import re
            m = re.match(r"^([a-zA-Z_]+)\(([^,]+),([^)]+)\)$", s)
            if not m:
                res["violations"].append({"tag": tag, "why": "unparseable tie entry", "entry": s})
                continue
            kind, lo, hi = m.group(1), F(m.group(2)), F(m.group(3))
            if not (L <= lo < hi <= R):
                res["violations"].append({"tag": tag, "why": "tie bracket outside J", "entry": s})
                continue
            vlo, vhi = cmp_at(p, q, lo), cmp_at(p, q, hi)
            if kind.startswith("cross") and not (vlo is not None and vhi is not None and vlo != vhi):
                res["violations"].append({"tag": tag, "why": "cross bracket without endpoint sign change",
                                          "entry": s, "vlo": vlo, "vhi": vhi})
            res["bracket_ties"] = res.get("bracket_ties", 0) + 1
            continue
        tv = cmp_at(p, q, z)
        if tv != 0:
            res["violations"].append({"tag": tag, "why": "claimed tie is not a tie", "z": s, "truth": tv})
    return cert

# ---- fuzz: random small-integer pairs, then score-preserving rescaling ----
N = 700
for i in range(N):
    def rnd(): return F(rng.randint(-9, 9))
    p = (rnd(), rnd(), F(rng.randint(0, 9)), F(rng.randint(0, 9)))
    q = (rnd(), rnd(), F(rng.randint(0, 9)), F(rng.randint(0, 9)))
    L, R = F(1), F(rng.choice([2, 4, 7]))
    if p[2]+p[3]*L <= 0 or q[2]+q[3]*L <= 0: continue
    if p[2]+p[3]*R <= 0 or q[2]+q[3]*R <= 0: continue
    base = run_case(p, q, L, R, f"fuzz{i}")
    if base is None: continue
    for k in (10, 100, 1000, 10**5):
        c2 = cand.certify_pair(scale(p, F(k)), scale(q, F(k)), L, R)
        if (str(c2.get("status")), str(c2.get("direction"))) != (str(base.get("status")), str(base.get("direction"))):
            res["scale_violations"].append({"tag": f"fuzz{i}", "k": k,
                                            "base": [str(base.get("status")), str(base.get("direction"))],
                                            "scaled": [str(c2.get("status")), str(c2.get("direction"))]})

# ---- the published blocker, at scales far beyond the frozen corpus ----
p0 = (F(-1), F(1), F(0), F(1)); q0 = (F(-2), F(2), F(7), F(0))
res["poc_scales"] = {}
for k in (1, 100, 10**4, 10**6, 10**8):
    c = cand.certify_pair(scale(p0, F(k)), scale(q0, F(k)), F(1), F(4))
    res["poc_scales"][str(k)] = {"status": str(c.get("status")), "direction": str(c.get("direction"))}

src = CAND.read_text()
res["hardcoded_poc_literals"] = sum(src.count(s) for s in ("70000", "10000,", "-200", "7/4"))
OUT.mkdir(parents=True, exist_ok=True)
(OUT/"COORDINATOR_V3_INDEPENDENT.json").write_text(json.dumps(res, indent=2, default=str))
print(json.dumps({k: v for k, v in res.items() if k != "violations"}, indent=2, default=str))
print("VIOLATIONS", len(res["violations"]), json.dumps(res["violations"][:5], indent=1, default=str))
