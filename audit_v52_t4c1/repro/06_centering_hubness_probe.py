# AUDIT DIAGNOSTIC ONLY - does length heterogeneity / hub structure flip SIGN vs ITQ?
import numpy as np, collections
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize
from scipy import sparse

def fit_itq(V,n_iter=50,seed=0):
    rng=np.random.default_rng(seed); b=V.shape[1]
    R=np.linalg.qr(rng.standard_normal((b,b)))[0]
    for _ in range(n_iter):
        B=np.where(V@R>=0,1.0,-1.0); U,S,Wt=np.linalg.svd(V.T@B); R=U@Wt
    return R

def run(seed,hetero):
    rng=np.random.default_rng(seed)
    nd,vocab,topics=500,3000,40
    T=rng.dirichlet(np.ones(vocab)*0.02,size=topics)
    mixes=rng.dirichlet(np.ones(topics)*0.3,size=nd)
    P=mixes@T; P/=P.sum(1,keepdims=True)
    if hetero: lens=np.clip(rng.lognormal(4.6,1.3,nd),15,4000).astype(int)   # 15..4000 tokens
    else:      lens=np.full(nd,220)
    docs=np.array([rng.multinomial(lens[i],P[i]) for i in range(nd)],float)
    gold=rng.integers(0,nd,size=200)
    queries=np.array([rng.multinomial(12,P[g]) for g in gold],float)
    df=(docs>0).sum(0); idf=np.log((1+nd)/(1+df))+1
    X=normalize(docs*idf); Q=normalize(queries*idf)
    svd=TruncatedSVD(96,random_state=5204)
    Y=normalize(svd.fit_transform(sparse.csr_matrix(X))); QY=normalize(svd.transform(sparse.csr_matrix(Q)))
    mu=Y.mean(0,keepdims=True); C=Y-mu; qC=QY-mu
    def top3(S): return (np.argsort(-S,axis=0)[:3].T==gold[:,None]).any(1).mean()
    def ham(D,QB): return (np.argsort((D[None,:,:]!=QB[:,None,:]).sum(2),axis=1)[:,:3]==gold[:,None]).any(1).mean()
    o={}
    o['FLOAT uncentered']=top3(Y@QY.T); o['FLOAT centered']=top3(C@qC.T)
    o['SIGN96']=ham(C>=0,qC>=0)
    o['ITQ96 correct']=np.mean([ham(C@(R:=fit_itq(C,seed=s))>=0,qC@R>=0) for s in [101,202,303]])
    # how dominant is component 1 (hub direction)?
    o['_var_frac_comp1']=float(np.var(Y[:,0])/np.var(Y,axis=0).sum())
    return o

for hetero in [False,True]:
    agg=collections.defaultdict(list)
    for sd in range(4):
        for k,v in run(sd,hetero).items(): agg[k].append(v)
    print(f"--- doc lengths {'HETEROGENEOUS (lognormal 15-4000 tok)' if hetero else 'UNIFORM (220 tok)'} ---")
    for k in ['FLOAT uncentered','FLOAT centered','SIGN96','ITQ96 correct']:
        print(f"   {k:<20} {100*np.mean(agg[k]):6.2f}%")
    print(f"   [comp-1 variance share: {np.mean(agg['_var_frac_comp1']):.3f}]")
