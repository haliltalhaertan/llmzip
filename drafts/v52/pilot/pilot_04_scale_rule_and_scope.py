"""Resolve open questions 1 (choice of D) and 2 (per-archive vs global sigma) empirically.
Also stress-test degenerate-coordinate handling. Synthetic only."""
import numpy as np
D96,TOPK=96,3
NARCH,NDOC,NQ,NSEED=30,300,12,5
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

def build(decay, dead=0, seed0=2000):
    """dead = number of trailing coordinates forced to ~zero variance."""
    arch=[]
    for a in range(NARCH):
        rng=np.random.default_rng(seed0+a); sd=decay**np.arange(D96)
        if dead: sd[D96-dead:]=1e-18
        Y=rng.standard_normal((NDOC,D96))*sd; gold=rng.integers(0,NDOC,NQ)
        QY=Y[gold]+rng.standard_normal((NQ,D96))*sd*1.35
        mu=Y.mean(axis=0); arch.append((Y-mu,QY-mu,gold))
    return arch

def run(arch, rule, scope, eps=1e-12):
    """rule: 'inv' -> 1/sd ; 'invsqrt' -> 1/sqrt(sd). scope: 'per' or 'global'."""
    if scope=="global":
        allsd=np.sqrt(np.mean([C.var(axis=0) for C,_,_ in arch],axis=0))
    acc={k:[] for k in ("N","F","SF","B","SB")}; degen=0
    for C,QC,gold in arch:
        sd = allsd if scope=="global" else C.std(axis=0)
        ok = sd>=eps; degen += int((~ok).sum())
        base = np.where(ok, sd, 1.0)
        d = 1.0/base if rule=="inv" else 1.0/np.sqrt(base)
        d = np.where(ok, d, 1.0)
        Dm=np.diag(d); Cs,QCs=C@Dm,QC@Dm
        assert np.array_equal(Cs>=0, C>=0) and np.array_equal(QCs>=0, QC>=0), "identity broken"
        for k in range(NSEED):
            Qf=haar_q(np.random.default_rng(59001+k),D96); Rb=block(np.random.default_rng(59001+k),32)
            acc["N"].append(recall(C,QC,gold)); acc["F"].append(recall(C,QC,gold,Qf)); acc["SF"].append(recall(Cs,QCs,gold,Qf))
            acc["B"].append(recall(C,QC,gold,Rb)); acc["SB"].append(recall(Cs,QCs,gold,Rb))
    m={k:float(np.mean(v)) for k,v in acc.items()}
    ff=(m["SF"]-m["F"])/(m["N"]-m["F"]) if m["N"]>m["F"] else float("nan")
    fb=(m["SB"]-m["B"])/(m["N"]-m["B"]) if m["N"]>m["B"] else float("nan")
    return m,ff,fb,degen

print("Q1/Q2 resolution — frac = share of each arm's own loss recovered\n")
print(f"{'decay':>6} {'rule':>8} {'scope':>7} | {'FULL':>6} {'SCALED':>6} | {'frac_full':>9} {'frac_blk':>8} {'I_frac':>7}")
for decay in (0.97,0.92):
    arch=build(decay)
    for rule in ("inv","invsqrt"):
        for scope in ("per","global"):
            m,ff,fb,_=run(arch,rule,scope)
            print(f"{decay:>6} {rule:>8} {scope:>7} | {m['F']:>6.4f} {m['SF']:>6.4f} | {ff:>9.3f} {fb:>8.3f} {ff-fb:>+7.3f}")
print("\nDegenerate-coordinate stress (12 of 96 coordinates at ~zero variance, decay 0.92):")
arch=build(0.92,dead=12)
for rule in ("inv","invsqrt"):
    m,ff,fb,degen=run(arch,rule,"per")
    print(f"  rule={rule:>8}  degenerate coords handled={degen:>4}  frac_full={ff:.3f}  frac_blk={fb:.3f}  identity: OK")
