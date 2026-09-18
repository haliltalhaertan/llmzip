#!/usr/bin/env python3
# audit_exact2.py — part 2: top3 numbers, L/U pairs, waste, tie, robustness (auditor-owned)
import sys, math, json
from fractions import Fraction as Fr
import importlib.util
spec = importlib.util.spec_from_file_location("V", "/home/mdp/muse-work/audit_norm/out/rerun/verify.py")
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
import numpy as np

print("=== D. top3 full-precision recompute (u=1 point-case) ===")
q = np.array([0.5,0.5,0.5,0.5]); c = np.array([0.5,0.5,0.5,0.5])
docs = [np.array([0.5,0.5,0.5,0.5]), (q+np.array([0.05,-0.05,0.,0.])), (q+np.array([0.10,0.,-0.10,0.])),
        np.array([1.,0.,0.,0.]), np.array([1.,1.,0.,0.])/math.sqrt(2), np.array([1.,1.,1.,0.])/math.sqrt(3)]
docs = [v/np.linalg.norm(v) for v in docs]
u = float(q@c); print("u =", repr(u))
Ls=[]; Us=[]; ts=[]; rhos=[]
for j,v in enumerate(docs):
    t=float(q@v); r=float(c@v); ts.append(t); rhos.append(r)
    L,U,m = V.cert_interval(u,r); Ls.append(L); Us.append(U)
    print(f"doc{j+1}: t={t:.15f} rho={r:.15f} m={m} L={L:.15f} U={U:.15f}")
print("REPORT L1..3=[0.9961,0.9961,0.9882] U4..6=[0.5020,0.7137,0.8706]:",
      [round(v,4) for v in Ls[:3]], [round(v,4) for v in Us[3:]])
wr=[V.worst_rank(Ls,Us,i) for i in range(6)]; print("worst-ranks:",wr,"(REPORT [3,3,3,6,5,4])")
# pairwise: certified vs true
cert=0; trueord=0; uncert_strict=0
for i in range(6):
    for j in range(i+1,6):
        if ts[i]==ts[j]: continue
        trueord+=1
        hi,lo=(i,j) if ts[i]>ts[j] else (j,i)
        if Ls[hi]>Us[lo]: cert+=1
        else: uncert_strict+=1; print(f"  UNRESOLVED strict pair: doc{hi+1} t={ts[hi]:.6f} vs doc{lo+1} t={ts[lo]:.6f} (L[{hi+1}]={Ls[hi]:.6f} <= U[{lo+1}]={Us[lo]:.6f})")
print(f"pairs: {trueord} strict-true-ordered, {cert} certified, {uncert_strict} strict-but-uncertified (non-necessity count)")
print("docs1v2 non-necessity witness: t1>t2 strict,", Ls[0], ">", Us[1], "?", Ls[0]>Us[1])

print()
print("=== E. codeword waste: feasible rho in [1/sqrt(d),1], code uniform on [-1,1] ===")
for d in (2,4):
    lo=1/math.sqrt(d); used=[m for m in range(256) if V.qdec(m)+V.K_HALF>=lo]
    print(f"d={d}: feasible rho>={lo:.4f}; codewords usable: {len(used)}/256 ({100*len(used)/256:.1f}%), wasted={256-len(used)}")
    print(f"  top3 doc rhos {sorted(round(r,4) for r in rhos)} all in bins m>=191:", all(V.qenc(r)>=191 for r in rhos))

print()
print("=== F. tie is approximate, not exact ===")
xA2=(0.991314274283428,0.13151429428742906); xE2=(-0.15131427428342797,0.988485705712571)
sA=float(0.6*xA2[0]+0.8*xA2[1]); sE=float(0.6*xE2[0]+0.8*xE2[1])
print("tie-A score:",repr(sA),"| tie-E score:",repr(sE),"| ==0.7?",sA==0.7,sE==0.7,"| |.-0.7|:",abs(sA-0.7),abs(sE-0.7))

print()
print("=== G. sweep queries all unit? (Theorem1/2 hypotheses) ===")
for qq in V.D2_QUERIES: print("d2",tuple(qq),"norm2=",sum(v*v for v in qq))
for qq in [[Fr(1,3),Fr(2,3),Fr(2,3)],[Fr(1),Fr(0),Fr(0)],[Fr(-1,3),Fr(2,3),Fr(2,3)]]: print("d3",tuple(qq),"norm2=",sum(v*v for v in qq))

print()
print("=== H. LME transcription vs witness JSON (read-only compare) ===")
w=json.load(open("/home/mdp/muse-work/mathpin/research_math_theory_2026_09_13/theory_benchmark_test_v1/audit_real_geometry/COORDINATOR_LME_WITNESS.json"))
row=[r for r in w if r.get("t")==4.0][0]
print("witness t4:",row)
mine={"gold_dot":1.0299795949628008,"rival_dot":1.0467211966244094,"gold_cos":0.5457381205243765,"rival_cos":0.539025678888817}
print("exact match on 4 transcribed floats:", all(row[k]==mine[k] for k in mine))

print()
print("=== I. att-consistency check cannot catch axis bug ===")
s=(-1,-1,1); qf=[0.0,0.0,-1.0]
ys=V.closure_maximizer_float(s,qf)
print("float maximizer ys*=",ys,"member_F(ys*)=",V.member_F(s,ys),"code att=",V.sup_attained(s,(Fr(0),Fr(0),Fr(-1))))
print("-> consistency check member==att passes (False==False) while TRUE attainment is True. Weak check.")
xe=V.approach_from_inside(s,ys); print("approach xe in F:",V.member_F(s,xe),"score:",sum(a*b for a,b in zip(qf,xe)),"(sup=0; density ok)")

print()
print("=== J. robustness gaps: member_F ignores norm; cap_cs ignores domain ===")
print("member_F((+,+),(5,5)) [non-unit] =",V.member_F((1,1),(5,5)))
print("cap_cs(u=2,rho=0.5) [non-unit u] =",V.cap_cs(2.0,0.5),"(silent point-interval garbage, true t unbounded-by-formula)")
print("cap_cs(u=0,rho=0) =",V.cap_cs(0.0,0.0),"; cap_cs(u=1,rho=0.3) =",V.cap_cs(1.0,0.3),"; cap_cs(u=-1,rho=-1) =",V.cap_cs(-1.0,-1.0))

print()
print("=== K. failure-cert + joint full precision ===")
u2,rho2,t2 = V.D_CASES[2][0],V.D_CASES[2][1],V.D_CASES[2][2]
a,b=V.cap_cs(u2,rho2); Lf,Uf,_=V.cert_interval(u2,rho2)
print("failure exact-cap:",repr(a),repr(b),"width",repr(b-a),"| cert:",repr(Lf),repr(Uf))
print("REPORT [-0.8,0.6] w=1.4, cert [-0.8010,0.6014]:",round(a,4),round(b,4),round(Lf,4),round(Uf,4))
qq=np.array([1.,2.,2.])/3; xx=np.array([2.,2.,-1.])/3
print("joint t=4/9 exact?",Fr(4,9)==sum(Fr(v).limit_denominator(10) for v in (qq*xx)), float(qq@xx)==4/9)

print()
print("=== L. check-category counts in results.json ===")
R=json.load(open("/home/mdp/muse-work/audit_norm/out/results_orig.json"))
from collections import Counter
print(Counter(c["name"].split(".")[0] for c in R["checks"]))
print("any B3 attainment/approach checks?", any(c["name"].startswith("B3.att") or c["name"].startswith("B3.approach") for c in R["checks"]))
print("any check referencing REPORT table brackets?", any("bracket" in c["name"] or "table" in c["name"] for c in R["checks"]))
