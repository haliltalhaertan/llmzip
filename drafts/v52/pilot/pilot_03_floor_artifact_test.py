"""Is the pp-interaction just a floor artifact? Compare pp gain vs FRACTION of loss recovered."""
import numpy as np
exec(open('pilot2.py').read().split('print(f"{')[0])   # reuse helpers/constants
rows=[]
for decay in (0.99,0.97,0.95,0.92,0.90,0.85):
    A={k:[] for k in ("N","F","SF","B","SB")}; cvs=[]
    for a in range(NARCH):
        rng=np.random.default_rng(2000+a); sd=decay**np.arange(D96)
        Y=rng.standard_normal((NDOC,D96))*sd; gold=rng.integers(0,NDOC,NQ)
        QY=Y[gold]+rng.standard_normal((NQ,D96))*sd*1.35
        mu=Y.mean(axis=0); C,QC=Y-mu,QY-mu
        s=C.std(axis=0); cvs.append(s.std()/s.mean())
        Dm=np.diag(np.where(s>=1e-12,1.0/np.maximum(s,1e-12),1.0)); Cs,QCs=C@Dm,QC@Dm
        for k in range(NSEED):
            Qf=haar_q(np.random.default_rng(59001+k),D96); Rb=block(np.random.default_rng(59001+k),32)
            A["N"].append(recall(C,QC,gold)); A["F"].append(recall(C,QC,gold,Qf)); A["SF"].append(recall(Cs,QCs,gold,Qf))
            A["B"].append(recall(C,QC,gold,Rb)); A["SB"].append(recall(Cs,QCs,gold,Rb))
    m={k:float(np.mean(v)) for k,v in A.items()}
    df=(m["SF"]-m["F"])*100; db=(m["SB"]-m["B"])*100
    ff=(m["SF"]-m["F"])/(m["N"]-m["F"]) if m["N"]>m["F"] else float("nan")
    fb=(m["SB"]-m["B"])/(m["N"]-m["B"]) if m["N"]>m["B"] else float("nan")
    rows.append((decay,np.mean(cvs),df,db,df-db,ff,fb,ff-fb))
print(f"{'decay':>6} {'CV(sd)':>7} | {'d_full':>7} {'d_blk':>7} {'I_pp':>7} | {'frac_full':>9} {'frac_blk':>9} {'I_frac':>7}")
for d,cv,df,db,i,ff,fb,ifr in rows:
    print(f"{d:>6} {cv:>7.3f} | {df:>+7.2f} {db:>+7.2f} {i:>+7.2f} | {ff:>9.3f} {fb:>9.3f} {ifr:>+7.3f}")
print("\nIf frac_full ~ frac_blk, the pp interaction is largely a FLOOR artifact:")
print("both arms recover the same PROPORTION of their own loss, and full simply had more loss.")
