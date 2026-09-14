# Audit script 2: domain attacks + degeneration handling + untested branches.
import sys
sys.path.insert(0, "/home/mdp/muse-work/audit_rank/out")
from fractions import Fraction as F
import importlib.util
spec = importlib.util.spec_from_file_location("vc", "/home/mdp/muse-work/audit_rank/out/verify_copy.py")
vc = importlib.util.module_from_spec(spec); spec.loader.exec_module(vc)
P4, certify_pair, cmp_rank = vc.P4, vc.certify_pair, vc.cmp_rank

print("=== 1. Domain enforcement ===")
p = P4(1,1,1,1); q = P4(2,2,2,2)
# D <= 0 at endpoint -> DOMAIN_FAIL?
r = certify_pair(P4(1,0,-5,1), P4(1,0,1,0), F(1), F(2))  # D1(1)=-4
print("D<0 at L:", r["status"], "|", r["notes"])
r = certify_pair(P4(1,0,1,-1), P4(1,0,1,0), F(0), F(2))  # D1: 1-z, pole at z=1 interior, endpoints 1,-1
print("pole interior (endpoint<0):", r["status"])
r = certify_pair(P4(1,0,0,0), P4(1,0,1,0), F(1), F(2))  # D identically 0
print("D identically 0:", r["status"])
# interior pole with BOTH endpoints >0 is impossible for linear D; prove by exhaustion:
# D linear: min on [L,R] at an endpoint. (analysis, no code needed) -> endpoint check SOUND.
try:
    cmp_rank(P4(1,0,-1,0), P4(1,0,1,0), F(1))
    print("cmp_rank negative-D: NO RAISE (BAD)")
except vc.DomainError:
    print("cmp_rank negative-D: raises DomainError (good)")

print()
print("=== 2. Degenerate J handling (NOT specified, NOT tested) ===")
r = certify_pair(p, q, F(1), F(1))
print("L==R single point:", r["status"], r["direction"], r["ties"])
r = certify_pair(p, q, F(2), F(1))
print("L>R reversed (garbage in):", r["status"], r["direction"], r["ties"])
r = certify_pair(P4(1,1,1,1), P4(2,0,1,0), F(0), F(1))
print("L=0 accepted (REPORT says z>0, code allows):", r["status"])

print()
print("=== 3. certify_pair on every degeneration (deg 3,2,1,0,const,zero) ===")
tests = {
 "cubic avenues S1 [4,16]": (P4(-3,4,5,10), P4(-2,2,2,10), F(4), F(16)),
 "quadratic tangent S4 [1/4,4]": (P4(1,1,0,4), P4(1,0,1,0), F(1,4), F(4)),
 "linear deg1 [1,4]": (P4(2,0,1,1), P4(1,0,1,1), F(1), F(4)),
 "linear w/ root deg1b [1/4,4]": (P4(0,1,1,0), P4(1,1,1,0), F(1,4), F(4)),
 "const-nonzero deg0 [1,4]": (P4(1,0,1,0), P4(2,0,1,0), F(1), F(4)),
 "zero-poly same-sign [1,4]": (P4(2,2,4,4), P4(1,1,1,1), F(1), F(4)),
 "zero-poly opposite-sign [1,4]": (P4(1,0,1,1), P4(-1,0,1,1), F(1), F(4)),
 "S5 crossing [1/4,2]": (P4(-1,1,1,1), P4(-2,2,1,3), F(1,4), F(2)),
 "S1 same-sign-root? [1/16,1]": (P4(-3,4,5,10), P4(-2,2,2,10), F(1,16), F(1)),
}
for name, (a, b, L, R) in tests.items():
    r = certify_pair(a, b, L, R)
    print(f"{name}: status={r['status']} dir={r['direction']} ties={r['ties']} sturm={r['sturm_calls']}")
    for n in r["notes"]: print("    note:", n)

print()
print("=== 4. topk branches the 49 checks never exercise ===")
# PERSISTENT_TIE via topk with K=1, tied pair + outsider below
t = vc.topk_cert([P4(2,2,4,4), P4(1,1,1,1), P4(-50,0,1,0)], 1, {0:0,1:1,2:2}, F(1,16), F(16))
print("topk persistent-tie sample:", t["strict"], t["prio"], "sample:", t["sample"])
# VARIES pair: S5 crosses on [1/4,2]; top1 with outsider below
t = vc.topk_cert([P4(-1,1,1,1), P4(-2,2,1,3), P4(-50,0,1,0)], 1, {0:0,1:1,2:2}, F(1,4), F(2))
print("topk varies-pair:", t["strict"], t["prio"], "witness:", (t["unstable_witness"] or {}).get("kind"))
# strict-reversal (no probe trigger? probe triggers first if sets differ at L/R)
t = vc.topk_cert([P4(-1,1,1,1), P4(-2,2,1,3)], 1, {0:0,1:1}, F(1,4), F(1))
print("topk 2-doc crossing [1/4,1]:", t["strict"], "witness:", (t["unstable_witness"] or {}).get("kind"))
