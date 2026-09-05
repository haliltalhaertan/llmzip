"""Harder synthetic regime + decay sweep, to size the interaction and calibrate decision bands."""
import numpy as np
D96, TOPK = 96, 3
NARCH, NDOC, NQ, NSEED = 30, 300, 12, 5
def haar_q(rng,d):
    A=rng.standard_normal((d,d)); Q,R=np.linalg.qr(A); return Q*np.where(np.diag(R)<0,-1.,1.)[None,:]
def block(rng,b):
    R=np.zeros((D96,D96)); R[:b,:b]=haar_q(rng,b); R[b:,b:]=haar_q(rng,D96-b); return R
def recall(C,QC,gold,T=None):
    if T is not None: C,QC=C@T,QC@T
    Db,Qb=C>=0,QC>=0; h=0
    for i in range(len(Qb)):
        d=np.count_nonzero(Db!=Qb[i],axis=1)
        if gold[i] in np.argsort(d,kind="stable")[:TOPK]: h+=1
    return h/len(Qb)
print(f"{'decay':>6} {'CV(sd)':>7} | {'NATIVE':>7} {'FULL':>7} {'B32':>7} | {'d_full':>7} {'d_blk':>7} {'I(pp)':>7}")
for decay in (0.99,0.97,0.95,0.92,0.90,0.85):
    A={k:[] for k in ("N","F","SF","B","SB")}; cvs=[]
    for a in range(NARCH):
        rng=np.random.default_rng(2000+a); sd=decay**np.arange(D96)
        Y=rng.standard_normal((NDOC,D96))*sd
        gold=rng.integers(0,NDOC,NQ)
        QY=Y[gold]+rng.standard_normal((NQ,D96))*sd*1.35      # much noisier -> off ceiling
        mu=Y.mean(axis=0); C,QC=Y-mu,QY-mu
        s=C.std(axis=0); cvs.append(s.std()/s.mean())
        Dm=np.diag(np.where(s>=1e-12,1.0/np.maximum(s,1e-12),1.0))
        Cs,QCs=C@Dm,QC@Dm
        for k in range(NSEED):
            Qf=haar_q(np.random.default_rng(59001+k),D96)
            Rb=block(np.random.default_rng(59001+k),32)
            A["N"].append(recall(C,QC,gold)); A["F"].append(recall(C,QC,gold,Qf)); A["SF"].append(recall(Cs,QCs,gold,Qf))
            A["B"].append(recall(C,QC,gold,Rb)); A["SB"].append(recall(Cs,QCs,gold,Rb))
    m={k:float(np.mean(v)) for k,v in A.items()}
    df=(m["SF"]-m["F"])*100; db=(m["SB"]-m["B"])*100
    print(f"{decay:>6} {np.mean(cvs):>7.3f} | {m['N']:>7.4f} {m['F']:>7.4f} {m['B']:>7.4f} | {df:>+7.2f} {db:>+7.2f} {df-db:>+7.2f}")
