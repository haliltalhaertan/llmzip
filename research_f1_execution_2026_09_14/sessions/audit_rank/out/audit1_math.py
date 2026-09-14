# Audit script 1: derive P_ij, degree bound, recompute ALL headline numbers exactly.
import sys
sys.path.insert(0, "/home/mdp/muse-work/audit_rank/out")
from fractions import Fraction as F
import importlib.util
spec = importlib.util.spec_from_file_location("vc", "/home/mdp/muse-work/audit_rank/out/verify_copy.py")
vc = importlib.util.module_from_spec(spec); spec.loader.exec_module(vc)
P4, P_coeffs, audit_P_coeffs = vc.P4, vc.P_coeffs, vc.audit_P_coeffs
peval, cmp_rank, audit_cmp = vc.peval, vc.cmp_rank, vc.audit_cmp
sturm_open_count, certify_pair = vc.sturm_open_count, vc.certify_pair

print("=== 1. Independent P derivation (symbolic convolution) ===")
def my_P(p, q):
    # (a1+b1 z)^2 (u2+v2 z) - (a2+b2 z)^2 (u1+v1 z), naive poly arithmetic
    def sq(a, b):  # (a+bz)^2 coeffs
        return [a*a, 2*a*b, b*b]
    def mul(A, B):
        C = [F(0)]*(len(A)+len(B)-1)
        for i, x in enumerate(A):
            for j, y in enumerate(B):
                C[i+j] += x*y
        return C
    a1,b1,u1,v1 = p; a2,b2,u2,v2 = q
    T1 = mul(sq(a1,b1), [u2,v2]); T2 = mul(sq(a2,b2), [u1,v1])
    n = max(len(T1), len(T2))
    T1 += [F(0)]*(n-len(T1)); T2 += [F(0)]*(n-len(T2))
    return [x-y for x, y in zip(T1, T2)]

cases = {
 "S1": (P4(-3,4,5,10), P4(-2,2,2,10)),
 "S2": (P4(2,2,4,4), P4(1,1,1,1)),
 "S3": (P4(1,1,1,10), P4(-1,-1,10,1)),
 "S3b": (P4(1,0,1,1), P4(-1,0,1,1)),
 "S4": (P4(1,1,0,4), P4(1,0,1,0)),
 "S5": (P4(-1,1,1,1), P4(-2,2,1,3)),
 "deg1": (P4(2,0,1,1), P4(1,0,1,1)),
 "deg0": (P4(1,0,1,0), P4(2,0,1,0)),
 "deg1b": (P4(0,1,1,0), P4(1,1,1,0)),
}
for name, (p, q) in cases.items():
    mine = my_P(p, q)
    code = P_coeffs(p, q)
    aud = audit_P_coeffs(p, q)
    # strip for degree
    s = list(mine)
    while len(s) > 1 and s[-1] == 0: s.pop()
    deg = len(s)-1 if not (len(s)==1 and s[0]==0) else "ZERO"
    print(f"{name}: mine==code {mine==code} code==audit {code==aud} deg={deg} P={[str(c) for c in code]}")

print()
print("=== 2. Leading-coefficient formula b1^2 v2 - b2^2 v1 ===")
for name, (p, q) in cases.items():
    a1,b1,u1,v1 = p; a2,b2,u2,v2 = q
    print(name, "c3 =", P_coeffs(p,q)[3], "formula =", b1*b1*v2 - b2*b2*v1,
          "OK" if P_coeffs(p,q)[3] == b1*b1*v2 - b2*b2*v1 else "MISMATCH")

print()
print("=== 3. Recompute S1 verdict pattern + P(1) ===")
C1, C2 = cases["S1"]
Z7 = [F(1,64),F(1,16),F(1,4),F(1),F(4),F(16),F(64)]
got = [cmp_rank(C1,C2,z) for z in Z7]
print("verdicts:", got, "prose [1,-1,-1,1,1,1,1]:", got == [1,-1,-1,1,1,1,1])
print("N2(1)=", C2[0]+C2[1]*F(1), "N1(1)=", C1[0]+C1[1]*F(1), "P(1)=", peval(P_coeffs(C1,C2),F(1)))

print()
print("=== 4. S3 factorization 9(z+1)^2(1-z) ===")
PF = P_coeffs(*cases["S3"])
# expand 9(z+1)^2(1-z) = 9(1+2z+z^2)(1-z) = 9[(1+2z+z^2)-(z+2z^2+z^3)] = 9[1+z-z^2-z^3]
print("PF =", [str(c) for c in PF], "expected [9,9,-9,-9]:", PF == [F(9),F(9),F(-9),F(-9)])
print("P(1) =", peval(PF, F(1)))
print("verdicts at 1/16,1,16:", [cmp_rank(*cases["S3"], z) for z in [F(1,16),F(1),F(16)]])
print("S3b P identically zero:", all(c==0 for c in P_coeffs(*cases["S3b"])),
      "verdicts:", [cmp_rank(*cases["S3b"], z) for z in [F(1,4),F(2)]])

print()
print("=== 5. Coordinator fix #1: single-zero P-root impossible in-domain ===")
# If N1(z0)=0, N2(z0)!=0, D1,D2>0: P = 0*D2 - N2^2*D1 = -N2^2 D1 != 0. Check on S1@z=1:
print("S1@z=1: P =", peval(P_coeffs(C1,C2),F(1)), "(prose says 12, nonzero -> consistent)")
# brute force: scan many rational pairs/points, assert no counterexample
import random
random.seed(0)
bad = 0
for _ in range(20000):
    p = P4(*[random.randint(-3,3) for _ in range(4)])
    q = P4(*[random.randint(-3,3) for _ in range(4)])
    z = F(random.randint(1,8), random.randint(1,8))
    N1,D1 = vc.NZ(p,z); N2,D2 = vc.NZ(q,z)
    if D1 > 0 and D2 > 0:
        single = (N1 == 0) != (N2 == 0)
        if single and peval(P_coeffs(p,q),z) == 0:
            bad += 1
print("random single-zero counterexamples (expect 0):", bad)

print()
print("=== 6. Squaring-validity attack: opposite-sign P-roots are spurious ===")
# S3: P(1)=0 but f1>f2. Also find MORE spurious roots by brute force.
found_spurious, found_missed = 0, 0
for _ in range(20000):
    p = P4(*[random.randint(-3,3) for _ in range(4)])
    q = P4(*[random.randint(-3,3) for _ in range(4)])
    z = F(random.randint(1,8), random.randint(1,8))
    N1,D1 = vc.NZ(p,z); N2,D2 = vc.NZ(q,z)
    if D1 > 0 and D2 > 0 and peval(P_coeffs(p,q),z) == 0:
        s1 = (N1>0)-(N1<0); s2 = (N2>0)-(N2<0)
        v = cmp_rank(p,q,z)
        if s1 == s2 and s1 != 0:
            if v != 0: found_missed += 1  # genuine root missed by comparator?!
        else:
            # spurious unless common zero
            if s1 == 0 and s2 == 0:
                if v != 0: found_missed += 1
            else:
                if v == 0: found_missed += 1
                else: found_spurious += 1
print("spurious P-roots correctly filtered:", found_spurious, "| comparator errors:", found_missed)

print()
print("=== 7. Negative-sign flip check (Thm1 ordering under shared -) ===")
errs = 0
for _ in range(20000):
    p = P4(*[random.randint(-3,3) for _ in range(4)])
    q = P4(*[random.randint(-3,3) for _ in range(4)])
    z = F(random.randint(1,8), random.randint(1,8))
    N1,D1 = vc.NZ(p,z); N2,D2 = vc.NZ(q,z)
    if D1 > 0 and D2 > 0 and ((N1>0)==(N2>0)) and N1 != 0 and N2 != 0 and N1 < 0:
        v = cmp_rank(p,q,z)
        S = N1*N1*D2 - N2*N2*D1  # P value
        expect = -((S>0)-(S<0))  # flipped
        if v != expect: errs += 1
print("shared-negative flip errors (expect 0):", errs)
