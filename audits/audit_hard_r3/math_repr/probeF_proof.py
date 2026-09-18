"""Independent re-verification of the sign-invariance proof (RT01 only)."""
import os, json, pickle, importlib.util
import numpy as np
def load_module(name, path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
R="/mnt/c/Users/MDP/dev/llmzip-work"
frozen=load_module("fz", R+"/drive/v52_t4d_locomo_frozen_cross_benchmark.py")
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize
from scipy import sparse
raw=json.load(open(R+"/top10_comparison_r1/data/RT01.json"))
docs=sorted(raw["docs"], key=lambda r: r["row"])
texts=[r["text"] for r in docs]
qs=[q["text"] for q in raw["queries"]]
payload=frozen.fit_input_payload(list(texts))
wv,cv,sv,Xw,Xc,Xl=frozen.fit_archive_representation(payload)
Z=sparse.hstack([sparse.csr_matrix(Xl),Xw,Xc],format="csr")
s96=TruncatedSVD(n_components=96, random_state=frozen.SVD_SEED)
Y=normalize(s96.fit_transform(Z))
mu=Y.mean(axis=0,keepdims=True)
C=(Y-mu).astype(np.float64)
Qw=normalize(wv.transform(qs)); Qc=normalize(cv.transform(qs)); Ql=normalize(sv.transform(Qw))
Zq=sparse.hstack([sparse.csr_matrix(Ql),Qw,Qc],format="csr")
QC=(normalize(s96.transform(Zq))-mu).astype(np.float64)
print("C shape",C.shape,"QC shape",QC.shape)
std=C.std(axis=0,ddof=0)
print("sigma min %.3e max %.3e n_below_floor=%d"%(std.min(),std.max(),int((std<1e-12).sum())))
sig=np.maximum(std,1e-12)
print("all sig>0:",bool(np.all(sig>0)))
print("C==0 frac:",float(np.mean(C==0.0)),"QC==0 frac:",float(np.mean(QC==0.0)))
dc=int(np.count_nonzero((C/sig[None,:]>=0)!=(C>=0)))
qc=int(np.count_nonzero((QC/sig[None,:]>=0)!=(QC>=0)))
print("doc bits changed: %d/%d  query bits changed: %d/%d"%(dc,C.size,qc,QC.size))
print("stored block: docs 0/63552 queries 0/8160")
print("C.size==63552:",C.size==63552,"QC.size==8160:",QC.size==8160)
