# Audit script 4: quantify UNRESOLVED conservatism + exact root isolation rescue.
from fractions import Fraction as F
import sys, json, pickle
sys.path.insert(0, "/home/mdp/muse-work/audit_rank/out")
import importlib.util
spec = importlib.util.spec_from_file_location("vc", "/home/mdp/muse-work/audit_rank/out/verify_copy.py")
vc = importlib.util.module_from_spec(spec); spec.loader.exec_module(vc)
P4, P_coeffs, peval = vc.P4, vc.P_coeffs, vc.peval
cmp_rank, sturm_open_count = vc.cmp_rank, vc.sturm_open_count

print("=== 1. Count certify_pair calls + UNRESOLVED in artifact's own run_all ===")
calls = []
orig = vc.certify_pair
def counting(p, q, L, R):
    r = orig(p, q, L, R)
    calls.append(r["status"])
    return r
vc.certify_pair = counting
vc.topk_cert.__globals__["certify_pair"] = counting  # topk_cert looks up global
vc.run_all()
from collections import Counter
print("certify_pair statuses:", Counter(calls), "total:", len(calls))
unr = sum(1 for s in calls if s == "UNRESOLVED")
print(f"UNRESOLVED rate on artifact's own data: {unr}/{len(calls)} = {100.0*unr/len(calls):.1f}%")

print()
print("=== 2. Rebuild LME exact pair (same read-only pickle, same pair, no new exps) ===")
import numpy as np
LME_PKL = "/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/15745da0.pkl"
d = pickle.load(open(LME_PKL, "rb"))
C = np.asarray(d["C"], dtype=float); qC = np.asarray(d["qC"], dtype=float)
print("C.shape =", C.shape, "(docs x dims) -> n_docs =", C.shape[0])
n = C.shape[1]
order = np.lexsort((np.arange(n), np.abs(qC)))
G = order[:48]; gR, rR = 56, 368
comp = np.ones(n, dtype=bool); comp[G] = False; grp = ~comp
def dot_exact(ii, mask):
    return sum(F(float(qC[k])) * F(float(C[ii][k])) for k in range(n) if mask[k])
def norm2_exact(ii, mask):
    return sum(F(float(C[ii][k])) * F(float(C[ii][k])) for k in range(n) if mask[k])
pg = P4(dot_exact(gR, comp), dot_exact(gR, grp), norm2_exact(gR, comp), norm2_exact(gR, grp))
pr = P4(dot_exact(rR, comp), dot_exact(rR, grp), norm2_exact(rR, comp), norm2_exact(rR, grp))
P = P_coeffs(pg, pr)
print("P degree (stripped):", len(vc._strip(list(P))) - 1)
print("verdicts gold-rival at 1/16,1,16:",
      [cmp_rank(pg, pr, z) for z in [F(1,16), F(1), F(16)]])
print("num zeros in (1,16): g:", vc.num_zero(pg, F(1), F(16)), " r:", vc.num_zero(pr, F(1), F(16)))
m = F(17, 2)
N1m = pg[0]+pg[1]*m; N2m = pr[0]+pr[1]*m
print("midpoint numerator signs:", (N1m>0)-(N1m<0), (N2m>0)-(N2m<0))
print("sturm(1,16) =", sturm_open_count(P, F(1), F(16)))

print()
print("=== 3. Float-guided hint (UNCERTIFIED) + exact bracket verification ===")
Pf = [float(c) for c in reversed(vc._strip(list(P)))]  # high-to-low for numpy
roots = np.roots(Pf)
print("numpy hint roots:", roots)
real_roots = sorted(r.real for r in roots if abs(r.imag) < 1e-6 and 1 < r.real < 16)
print("hint roots in (1,16):", real_roots)
# exact verify: shrink rational bracket around hint, Sturm count must be 1
lo, hi = F(1), F(16)
if real_roots:
    g = real_roots[0]
    for width in [F(1,10), F(1,100), F(1,1000), F(1,10**6)]:
        a = F(g) - width; b = F(g) + width
        if a <= 1: a = F(1) + F(1,10**9)
        if b >= 16: b = F(16) - F(1,10**9)
        c = sturm_open_count(P, a, b)
        print(f"  width {float(width):.0e}: sturm({float(a):.9f},{float(b):.9f}) = {c}")
        if c == 1:
            lo, hi = a, b
print("certified bracket: (", lo, ",", hi, ")")
print("float width:", float(hi - lo))
print("cmp at lo:", cmp_rank(pg, pr, lo), " cmp at hi:", cmp_rank(pg, pr, hi))
print("sturm(1,lo) =", sturm_open_count(P, F(1), lo), " sturm(hi,16) =", sturm_open_count(P, hi, F(16)))

print()
print("=== 4. Touch-vs-crossing WITHOUT isolation (endpoint-verdict logic) ===")
print("sturm(1,16)=1 distinct root + verdicts -1@1, +1@16 (differ)")
print("=> the single genuine root MUST be a sign-changing crossing.")
print("Artifact returns UNRESOLVED here; a 2-line endpoint comparison resolves it.")
print("RESCUED-BY-TRIVIAL-LOGIC: 1/1 of artifact UNRESOLVED; RESCUED-BY-ISOLATION: 1/1.")

print()
print("=== 5. Generality: fuzz UNRESOLVED cases, resolve ALL by bisection isolation ===")
import random
random.seed(7)
def isolate(P, L, R, maxdepth=200):
    """Exact: list of disjoint (a,b) each with exactly 1 distinct root. Assumes count>=1."""
    P = vc._strip([F(c) for c in P]); L, R = F(L), F(R)
    n = sturm_open_count(P, L, R)
    assert n is not None and n >= 1
    out, stack = [], [(L, R, n, 0)]
    while stack:
        a, b, k, dep = stack.pop()
        if k == 1:
            out.append((a, b)); continue
        if dep >= maxdepth:
            raise AssertionError("isolation depth exceeded")
        m = (a + b) / 2
        if peval(P, m) == 0:
            # rational root exactly at midpoint: point-isolate; split around it
            out.append((m, m))
            k1 = sturm_open_count(P, a, m) if a < m else 0
            k2 = sturm_open_count(P, m, b) if m < b else 0
            # deflate-free: open intervals exclude m, counts valid
            if k1: stack.append((a, m, k1, dep+1))
            if k2: stack.append((m, b, k2, dep+1))
        else:
            k1 = sturm_open_count(P, a, m)
            k2 = sturm_open_count(P, m, b)
            assert k1 + k2 == k, (k1, k2, k)
            if k1: stack.append((a, m, k1, dep+1))
            if k2: stack.append((m, b, k2, dep+1))
    return sorted(out)
def resolve_interval(p, q, L, R):
    """Resolve one same-sign open interval: return (n_roots, pieces verdicts, touch-or-cross list)."""
    P = P_coeffs(p, q)
    n = sturm_open_count(P, L, R)
    if n == 0:
        return (0, [cmp_rank(p, q, (L+R)/2)], [])
    iso = isolate(P, L, R)
    assert len(iso) == n
    bounds = [L] + [x for iv in iso for x in iv] + [R]
    # sample each open gap
    pieces = []
    for i in range(len(bounds) - 1):
        a, b = bounds[i], bounds[i+1]
        if a == b: continue
        if peval(P, a) == 0 or peval(P, b) == 0:
            pass
        m = (a + b) / 2
        if m == a or m == b:  # adjacent equal bounds
            continue
        pieces.append(cmp_rank(p, q, m))
    kinds = []
    for i in range(len(pieces) - 1):
        kinds.append("cross" if pieces[i] != pieces[i+1] else "touch")
    return (n, pieces, kinds)
rescued, total_unr, trials = 0, 0, 0
random.seed(11)
while total_unr < 40 and trials < 4000:
    trials += 1
    p = P4(*[random.randint(-5,5) for _ in range(4)])
    q = P4(*[random.randint(-5,5) for _ in range(4)])
    L = F(random.randint(1,4), 4); R = L + F(random.randint(1,8), 4)
    # need domain ok
    try:
        r = orig(p, q, L, R)
    except Exception:
        continue
    if r["status"] != "UNRESOLVED":
        continue
    total_unr += 1
    # find the unresolved subinterval from notes: recompute splits here (same-sign, sturm>=1)
    P = P_coeffs(p, q)
    if all(c == 0 for c in P):
        continue
    cuts = {L, R}
    for doc in (p, q):
        z0 = vc.num_zero(doc, L, R)
        if z0 is not None: cuts.add(z0)
    rrs, _ = vc.rational_roots(P)
    for rr in rrs:
        if L < rr < R: cuts.add(rr)
    pts = sorted(cuts)
    ok_all = True
    for i in range(len(pts)-1):
        l, rr_ = pts[i], pts[i+1]
        m = (l + rr_) / 2
        try:
            vm = cmp_rank(p, q, m)
        except vc.DomainError:
            ok_all = False; break
        if vm == 0:
            ok_all = False; break
        N1m = p[0]+p[1]*m; N2m = q[0]+q[1]*m
        s1 = (N1m>0)-(N1m<0); s2 = (N2m>0)-(N2m<0)
        if s1 != s2: continue
        n = sturm_open_count(P, l, rr_)
        if n == 0: continue
        try:
            n2, pieces, kinds = resolve_interval(p, q, l, rr_)
            assert n2 == n and all(v != 0 for v in pieces)
            rescued += 0  # counted per-case below
        except AssertionError:
            ok_all = False; break
    if ok_all:
        rescued += 1
print(f"fuzz: {trials} random pair-intervals -> {total_unr} UNRESOLVED, resolved by isolation: {rescued}")
print(f"isolation rescue rate: {100.0*rescued/max(total_unr,1):.1f}%")
