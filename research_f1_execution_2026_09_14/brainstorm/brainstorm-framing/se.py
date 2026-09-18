"""Paired SEs for headline comparisons, K=3 only, LME + PerLTQA. READ-ONLY on caches."""
import pickle, glob, numpy as np
def fr_exp(scores, gold, K, hb):
    gold=np.asarray(gold,int); n=len(gold)
    if hb: thr=np.sort(scores)[::-1][K-1]; nb=(scores>thr).sum(); be=(scores==thr).sum()
    else: thr=np.sort(scores)[K-1]; nb=(scores<thr).sum(); be=(scores==thr).sum()
    g=np.asarray(scores)[gold]
    if hb: gs=(g>thr).sum(); gt=(g==thr).sum()
    else: gs=(g<thr).sum(); gt=(g==thr).sum()
    return (gs+gt*(K-nb)/be)/n
def per_query(C,q,g):
    Cn=np.linalg.norm(C,axis=1); qn=np.linalg.norm(q)
    cos=(C@q)/np.maximum(Cn*qn,1e-300)
    ham=((C>=0)!=(q>=0)).sum(axis=1).astype(float)
    sd=C.std(axis=0); sd[sd==0]=1.0
    Zs=C/sd; zs=q/sd
    zcos=(Zs@zs)/np.maximum(np.linalg.norm(Zs,axis=1)*np.linalg.norm(zs),1e-300)
    M=np.vstack([C,q]); r=np.argsort(np.argsort(M,axis=1),axis=1).astype(float)
    rc=r-r.mean(); s2=np.sqrt((rc**2).sum(axis=1)); s2[s2==0]=1
    sp=(rc[:-1]@rc[-1])/(s2[:-1]*s2[-1])
    return {m:fr_exp(s,g,3,hb) for m,(s,hb) in
            {'sign':(ham,False),'cos':(cos,True),'zcos':(zcos,True),'spear':(sp,True)}.items()}
def summarize(name, rows):
    import numpy as np
    A=np.array([[r[m] for m in ['sign','cos','zcos','spear']] for r in rows])
    n=len(A)
    for a,b,label in [(0,1,'sign-cos'),(2,0,'zcos-sign'),(3,0,'spear-sign'),(2,1,'zcos-cos')]:
        d=A[:,a]-A[:,b]; m=d.mean(); se=d.std(ddof=1)/np.sqrt(n)
        print(f'{name} {label}: {100*m:+.4f}pp SE {100*se:.4f}pp 95%CI [{100*(m-1.96*se):+.4f},{100*(m+1.96*se):+.4f}] n={n}')
L=[]
for f in sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/*.pkl')):
    d=pickle.load(open(f,'rb')); L.append(per_query(d['C'],d['qC'],list(d['gold'])))
summarize('LME',L)
arch=pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_arch_eval.pkl','rb'))
qq=pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_q_eval.pkl','rb'))
P=[per_query(arch[v['char']]['C'],v['qC'],list(v['gold'])) for v in qq.values()]
summarize('PerLTQA',P)
