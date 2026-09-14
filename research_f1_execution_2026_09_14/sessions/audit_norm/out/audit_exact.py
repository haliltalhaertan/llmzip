#!/usr/bin/env python3
# audit_exact.py — exact rational audit of norm_aware_sign_bounds (scratch, auditor-owned)
import sys, math, json
sys.path.insert(0, "/home/mdp/muse-work/audit_norm/out/rerun")
sys.path.insert(0, "/home/mdp/muse-work/audit_norm/out")
from fractions import Fraction as Fr
import importlib.util
spec = importlib.util.spec_from_file_location("V", "/home/mdp/muse-work/audit_norm/out/rerun/verify.py")
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)

print("=== A. d2 table: REPORT prose vs exact truth vs coordinator ===")
q = (Fr(3,5), Fr(4,5))
# REPORT.md L92-97 rows: s -> (range_str, attain_str)
report_rows = {
    (1,1):   ("(3/5,1]",  "sup yes, inf no"),
    (1,-1):  ("[-4/5,3/5)", "inf yes, sup no"),
    (-1,1):  ("[-3/5,4/5)", "neither"),
    (-1,-1): ("[-1,-3/5)",  "sup yes, inf no"),
}
for s in [(1,1),(1,-1),(-1,1),(-1,-1)]:
    ks = V.sup_closed(s,q); ki = V.inf_closed(s,q)
    sup2 = ks[1]; inf2 = ki[1]
    sa = V.sup_attained(s,q); ia = V.inf_attained(s,q)
    # exact values
    if ks[0]=='norm': supv = "sqrt(%s)"%sup2
    else: supv = str(ks[1])
    if ki[0]=='norm': infv = "-sqrt(%s)"%inf2
    else: infv = str(ki[1])
    print(f"s={s} sup_kind={ks[0]} sup={supv} sup_att(code)={sa} | inf_kind={ki[0]} inf={infv} inf_att(code)={ia} | REPORT: {report_rows[s]}")
# exact attainer membership checks (coordinator's claims)
print("--- attainer membership (exact) ---")
print("(1,0) in F((+,+)):", V.member_F((1,1),(Fr(1),Fr(0))), "score:", V.vdot(q,(Fr(1),Fr(0))))
print("(0,-1) in F((+,-)):", V.member_F((1,-1),(Fr(0),Fr(-1))), "score:", V.vdot(q,(Fr(0),Fr(-1))))
print("(1,0) in F((+,-)):", V.member_F((1,-1),(Fr(1),Fr(0))), "(sup maximizer must be OUT)")
print("(-1,0) in F((-,+)):", V.member_F((-1,1),(Fr(-1),Fr(0))), "score:", V.vdot(q,(Fr(-1),Fr(0))))
print("(0,1) in F((-,+)):", V.member_F((-1,1),(Fr(0),Fr(1))), "(sup maximizer must be OUT)")
print("-q in F((-,-)):", V.member_F((-1,-1),(-q[0],-q[1])), "score:", V.vdot(q,(-q[0],-q[1])))
print("(-1,0) in F((-,-)):", V.member_F((-1,-1),(Fr(-1),Fr(0))), "(sup axis must be OUT)")

print()
print("=== B. coordinator axis-rule counterexample (exact) ===")
s = (-1,-1,1); qc = (Fr(0),Fr(0),Fr(-1)); x = (Fr(-3,5),Fr(-4,5),Fr(0))
print("unit x:", V.vnorm2(x)==1, "| x in F(s):", V.member_F(s,x), "| score:", V.vdot(qc,x))
print("sup_closed:", V.sup_closed(s,qc), "| code sup_attained:", V.sup_attained(s,qc), "(truth: True -> code WRONG)")
for j in range(3):
    ax = [Fr(0)]*3; ax[j]=Fr(s[j])
    print(f"  axis j={j} s_j*q_j={s[j]*qc[j]} inF={V.member_F(s,ax)}")
print("--- mirror inf ---")
qm = (Fr(0),Fr(0),Fr(1))
print("score qm.x:", V.vdot(qm,x), "| inf_closed:", V.inf_closed(s,qm), "| code inf_attained:", V.inf_attained(s,qm), "(truth: True -> code WRONG)")
print("--- q=0 out-of-scope demo ---")
print("sup_attained((-1,-1),(0,0)):", V.sup_attained((-1,-1),(Fr(0),Fr(0))), "(truth: every x scores 0=sup -> always attained; q=0 excluded as non-unit)")

print()
print("=== C. Theorem 2 exact squared containment on rational unit vectors ===")
def sq_contains(qv, xv, s):
    d = len(s)
    t = sum(a*b for a,b in zip(qv,xv))          # exact rational
    sq = sum(a*si for a,si in zip(qv,s))        # sqrt(d)*u, rational
    l1 = sum(abs(b) for b in xv)                # sqrt(d)*rho for x in F(s), rational
    u2 = sq*sq/Fr(d); r2 = l1*l1/Fr(d); ur = sq*l1/Fr(d)
    lhs = (t-ur)*(t-ur); rhs = (1-u2)*(1-r2)
    return t, lhs <= rhs, lhs, rhs, u2, r2
import random
units2 = [(Fr(3,5),Fr(4,5)),(Fr(5,13),Fr(12,13)),(Fr(8,17),Fr(15,17)),(Fr(20,29),Fr(21,29)),
          (Fr(1),Fr(0)),(Fr(0),Fr(1)),(Fr(-3,5),Fr(4,5)),(Fr(3,5),Fr(-4,5)),(Fr(-3,5),Fr(-4,5))]
units3 = [(Fr(1,3),Fr(2,3),Fr(2,3)),(Fr(1),Fr(0),Fr(0)),(Fr(0),Fr(1),Fr(0)),(Fr(0),Fr(0),Fr(1)),
          (Fr(-1,3),Fr(2,3),Fr(2,3)),(Fr(2,11),Fr(6,11),Fr(9,11))]
# fix: (2,6,9)/11 -> 4+36+81=121 ok
pats2 = [(1,1),(1,-1),(-1,1),(-1,-1)]
pats3 = [(a,b,c) for a in (1,-1) for b in (1,-1) for c in (1,-1)]
n=0; bad=0; eq=0
for qv in units2:
    for xv in units2:
        for s in pats2:
            if not V.member_F(s,xv): continue
            t,ok,lhs,rhs,u2,r2 = sq_contains(qv,xv,s)
            n+=1; bad+= (not ok); eq += (lhs==rhs)
print(f"d=2 feasible combos: {n} tested, {bad} violations, {eq} exact-equality (endpoint) cases")
n=0; bad=0; eq=0
for qv in units3:
    for xv in units3:
        for s in pats3:
            if not V.member_F(s,xv): continue
            t,ok,lhs,rhs,u2,r2 = sq_contains(qv,xv,s)
            n+=1; bad+= (not ok); eq += (lhs==rhs)
print(f"d=3 feasible combos: {n} tested, {bad} violations, {eq} exact-equality cases")
# failure-wide triple is realizable: q=(-4/5,3/5), x=(1,0), s=(+,+)
qv=(Fr(-4,5),Fr(3,5)); xv=(Fr(1),Fr(0)); s=(1,1)
t,ok,lhs,rhs,u2,r2 = sq_contains(qv,xv,s)
print(f"failure-wide realized: t={t} u^2={u2} rho^2={r2} (t-ur)^2={lhs} rhs={rhs} equal={lhs==rhs} (endpoint, exact)")
# rho range: rho^2 in [1/d,1] for feasible x
mn = min(sum(abs(b) for b in xv)**2/Fr(2) for xv in units2 for s in pats2 if V.member_F(s,xv))
print("min feasible rho^2 over d2 sample:", mn, "(>=1/2 required)")
mn3 = min(sum(abs(b) for b in xv)**2/Fr(3) for xv in units3 for s in pats3 if V.member_F(s,xv))
print("min feasible rho^2 over d3 sample:", mn3, "(>=1/3 required)")
