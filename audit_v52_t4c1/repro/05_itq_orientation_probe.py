# AUDIT DIAGNOSTIC ONLY - synthetic plausibility probe for ITQ-vs-SIGN direction.
# NOT a new method, NOT tuned, NOT imported into any 4C1 claim.
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from scipy import sparse

def fit_itq(V,n_iter=50,seed=0,orient='correct'):
    rng=np.random.default_rng(seed); b=V.shape[1]
    R=np.linalg.qr(rng.standard_normal((b,b)))[0]
    for _ in range(n_iter):
        B=np.where(V@R>=0,1.0,-1.0)          # fix R -> B = sgn(V R)
        U,S,Wt=np.linalg.svd(V.T@B)          # fix B -> Procrustes
        R=U@Wt
    return R

def synth(nd=500,seed=0,vocab=3000,topics=40):
    rng=np.random.default_rng(seed)
    # topic-mixture documents -> counts (LSA-like, heavy-tailed, non-negative)
    T=rng.dirichlet(np.ones(vocab)*0.02,size=topics)
    docs=[];qs=[];gold=[]
    for i in range(nd):
        mix=rng.dirichlet(np.ones(topics)*0.3)
        p=mix@T; p/=p.sum()
        docs.append(rng.multinomial(220,p))
    docs=np.array(docs,float)
    # queries: short, from same topic mixture as their gold doc (out-of-distribution length)
    for i in range(nd):
        mix=rng.dirichlet(np.ones(topics)*0.3)
        p=mix@T; p/=p.sum()
    return docs

def run(seed):
    rng=np.random.default_rng(seed)
    nd,vocab,topics=500,3000,40
    T=rng.dirichlet(np.ones(vocab)*0.02,size=topics)
    mixes=rng.dirichlet(np.ones(topics)*0.3,size=nd)
    P=mixes@T; P/=P.sum(1,keepdims=True)
    docs=np.array([rng.multinomial(220,P[i]) for i in range(nd)],float)
    # each query is a SHORT sample from its gold doc's topic mixture
    gold=rng.integers(0,nd,size=200)
    queries=np.array([rng.multinomial(12,P[g]) for g in gold],float)
    # tf-idf
    df=(docs>0).sum(0); idf=np.log((1+nd)/(1+df))+1
    X=normalize(docs*idf); Q=normalize(queries*idf)
    svd=TruncatedSVD(96,random_state=5204)
    Y=normalize(svd.fit_transform(sparse.csr_matrix(X)))
    QY=normalize(svd.transform(sparse.csr_matrix(Q)))
    mu=Y.mean(0,keepdims=True); C=Y-mu; qC=QY-mu
    out={}
    out['FLOAT(uncentered cos)']=(np.argsort(-(Y@QY.T),axis=0)[:3].T==gold[:,None]).any(1).mean()
    out['FLOAT(centered cos)']=(np.argsort(-(C@qC.T),axis=0)[:3].T==gold[:,None]).any(1).mean()
    def ham(D,QB): return (np.argsort((D[None,:,:]!=QB[:,None,:]).sum(2),axis=1)[:,:3]==gold[:,None]).any(1).mean()
    out['SIGN96']=ham(C>=0,qC>=0)
    for nm,orient in [('ITQ96 correct (V@R)','correct'),('ITQ96 wrong (V@R.T)','wrong')]:
        accs=[]
        for s in [101,202,303]:
            R=fit_itq(C,seed=s)
            Ruse=R if orient=='correct' else R.T
            accs.append(ham(C@Ruse>=0,qC@Ruse>=0))
        out[nm]=np.mean(accs)
    accs=[]
    for s in [101,202,303]:
        Rr=np.linalg.qr(np.random.default_rng(s).standard_normal((96,96)))[0]
        accs.append(ham(C@Rr>=0,qC@Rr>=0))
    out['RANDOM rotation (LSH)']=np.mean(accs)
    return out

import collections
agg=collections.defaultdict(list)
for sd in range(4):
    for k,v in run(sd).items(): agg[k].append(v)
print("SYNTHETIC LSA-GEOMETRY PROBE — ANY R@3 (mean of 4 synthetic corpora)")
print("(audit diagnostic only; not a 4C1 result)")
for k in ['FLOAT(uncentered cos)','FLOAT(centered cos)','SIGN96','ITQ96 correct (V@R)','ITQ96 wrong (V@R.T)','RANDOM rotation (LSH)']:
    print(f"  {k:<26} {100*np.mean(agg[k]):6.2f}%")
