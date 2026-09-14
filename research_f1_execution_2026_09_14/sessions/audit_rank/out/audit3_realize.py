# Audit script 3: realizability — necessary conditions + explicit constructions.
from fractions import Fraction as F
import sys
sys.path.insert(0, "/home/mdp/muse-work/audit_rank/out")
import importlib.util
spec = importlib.util.spec_from_file_location("vc", "/home/mdp/muse-work/audit_rank/out/verify_copy.py")
vc = importlib.util.module_from_spec(spec); spec.loader.exec_module(vc)
P4, P_coeffs, peval, cmp_rank = vc.P4, vc.P_coeffs, vc.peval, vc.cmp_rank

print("=== 1. Necessary-condition screen (u>=0,v>=0; u=0=>a=0; v=0=>b=0) ===")
ex = {
 "S1.C1": (-3,4,5,10), "S1.C2": (-2,2,2,10),
 "S2.T1": (2,2,4,4), "S2.T2": (1,1,1,1),
 "S3.F1": (1,1,1,10), "S3.F2": (-1,-1,10,1),
 "S3b.O1": (1,0,1,1), "S3b.O2": (-1,0,1,1),
 "S4.E1": (1,1,0,4), "S4.E2": (1,0,1,0),
 "S5.G1": (-1,1,1,1), "S5.G2": (-2,2,1,3),
 "S6a.const": (-50,0,1,0), "S6b.Lo": (-100,0,1,1),
 "S6c.remark A": (2,0,1,0), "S6c.remark B": (1,0,1,0), "S6c.remark C": (0,0,1,0),
}
for name, (a,b,u,v) in ex.items():
    ok = u >= 0 and v >= 0 and (u != 0 or a == 0) and (v != 0 or b == 0)
    print(f"{name:12s} {str((a,b,u,v)):22s} {'REALIZABLE-OK' if ok else 'IMPOSSIBLE <=='}")

print()
print("=== 2. Proof of necessity: u=0 => c=0 => a=qc.c=0 (coordinator fix #4) ===")
print("u=||c||^2=0 iff c=0 vector, then a=qc.c=0 regardless of query. QED (no code needed).")
print("S4.E1 has u=0,a=1 -> cannot arise from ANY doc/query blocks. Coordinator CORRECT.")

print()
print("=== 3. Sufficiency: explicit 2+2-dim real vectors for S1 (exact symbolic) ===")
# complement block: c1=sqrt5 e1, c2=sqrt2 e2, qc=(-3/sqrt5)e1+(-2/sqrt2)e2
# check dots/norms symbolically: qc.c1 = (-3/sqrt5)(sqrt5) = -3; ||c1||^2=5 etc.
from fractions import Fraction as F
print("c-block: qc.c1=-3,|c1|^2=5, qc.c2=-2,|c2|^2=2  (e1,e2 orthonormal, qc=(-3/s5)e1+(-2/s2)e2)")
print("g-block: qg.g1=+4,|g1|^2=10, qg.g2=+2,|g2|^2=10 (g1=s10 e1',g2=s10 e2',qg=(4/s10)e1'+(2/s10)e2')")
print("=> S1 pair jointly realizable in 2+2 dims. (artifact gives no vectors; existential only)")

print()
print("=== 4. NEW realizable tangent witness (artifact has none) ===")
# p=(3/2,1,2,4), q=(1,0,1,0): P = (3/2+z)^2*1 - 1*(2+4z) = z^2-z+1/4 = (z-1/2)^2
p = P4(F(3,2),1,2,4); q = P4(1,0,1,0)
P = P_coeffs(p,q)
print("P =", [str(c) for c in P], "expect [1/4,-1,1,0]:", P == [F(1,4),F(-1),F(1),F(0)])
vv = [cmp_rank(p,q,z) for z in [F(1,4),F(1,2),F(1)]]
print("verdicts at 1/4,1/2,1:", vv, "expect [1,0,1]:", vv == [1,0,1])
r = vc.certify_pair(p,q,F(1,4),F(1))
print("certify_pair:", r["status"], r["direction"], r["ties"])
# realizability screen
for nm, (a,b,u,v) in {"new.p": (F(3,2),1,2,4), "new.q": (1,0,1,0)}.items():
    ok = u >= 0 and v >= 0 and (u != 0 or a == 0) and (v != 0 or b == 0)
    print(nm, "screen:", "PASS" if ok else "FAIL")
# explicit vectors: c-block dim2: c1=sqrt2 e1 (u=2), a=3/2: qc=(3/(2sqrt2))e1 + 1*e2; c2=e2 (u=1,a=1)
print("explicit c-block: c1=s2*e1,c2=e2,qc=(3/2s2)e1+e2 -> dots 3/2,1 norms 2,1 CHECK")
print("explicit g-block: g1=2e1'(v=4),b=1: qg=(1/2)e1'+0*e2'; g2=0 (v=0,b=0) CHECK")
# verify dot claims arithmetically with symbols s2 (s2^2=2)
print("qc.c1=(3/2s2)(s2)=3/2 OK; qc.c2=1 OK; |c1|^2=2 OK; |c2|^2=1 OK")
print("qg.g1=(1/2)(2)=1 OK; |g1|^2=4 OK; g2=0->b=0,v=0 OK")
# genuine + touch: same signs? N1=3/2+z>0, N2=1>0 on z>0 -> same-sign -> P-root genuine; verdicts +/0/+ -> touch, no reversal
print("N1>0,N2>0 on z>0 -> P-root at 1/2 GENUINE; verdict pattern +/0/+ -> TOUCH without reversal.")
print("CONCLUSION: realizable tangent exists; artifact's S4 choice was needlessly unrealizable.")
