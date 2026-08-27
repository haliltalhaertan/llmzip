import numpy as np, sys
sys.path.insert(0,'/home/user/llmzip/adapters')
import importlib.util
spec=importlib.util.spec_from_file_location("v1","/home/user/llmzip/adapters/longmemeval_v52_adapter.py")
v1=importlib.util.module_from_spec(spec); spec.loader.exec_module(v1)

rng=np.random.default_rng(0)
V=rng.normal(size=(400,96)); V-=V.mean(0,keepdims=True)

R=v1.fit_itq(V,n_iter=100,seed=101)
print("R shape:",R.shape)
print("orthogonal  ||R R^T - I||_max =", float(np.abs(R@R.T-np.eye(96)).max()))
print("det(R) =", round(float(np.linalg.det(R)),6))

def obj(V,R):  # ITQ quantization objective ||B - V R||_F^2 with B = sgn(V R)
    B=np.where(V@R>=0,1.0,-1.0); return float(((B-V@R)**2).sum())

# Independent re-derivation of the Procrustes step: maximize tr(M R), M = B^T V
def procrustes_correct(M):
    U,_,VT=np.linalg.svd(M,full_matrices=False)
    return VT.T@U.T                      # R = V_m U_m^T
def procrustes_transposed(M):
    U,_,VT=np.linalg.svd(M,full_matrices=False)
    return U@VT                          # the WRONG orientation

M=np.where(V@R>=0,1.0,-1.0).T@V
Rc, Rw = procrustes_correct(M), procrustes_transposed(M)
print("\ntr(M R) under adapter's update rule :", round(float(np.trace(M@Rc)),3))
print("tr(M R) under transposed rule       :", round(float(np.trace(M@Rw)),3))
print("nuclear norm of M (theoretical max) :", round(float(np.linalg.svd(M,compute_uv=False).sum()),3))

# monotone decrease of the objective => update is correctly oriented
def trace_itq(V,n_iter,seed,orient):
    r=np.random.default_rng(seed); A=r.normal(size=(96,96))
    U,_,VT=np.linalg.svd(A,full_matrices=False); Rr=U@VT
    hist=[obj(V,Rr)]
    for _ in range(n_iter):
        B=np.where(V@Rr>=0,1.0,-1.0); C=B.T@V
        U2,_,VT2=np.linalg.svd(C,full_matrices=False)
        Rr = VT2.T@U2.T if orient=='adapter' else U2@VT2
        hist.append(obj(V,Rr))
    return hist
hc=trace_itq(V,30,101,'adapter'); hw=trace_itq(V,30,101,'transposed')
print("\nobjective, adapter rule    : start %.1f -> end %.1f  (monotone non-increasing: %s)"%(hc[0],hc[-1],all(hc[i+1]<=hc[i]+1e-6 for i in range(len(hc)-1))))
print("objective, transposed rule : start %.1f -> end %.1f  (monotone non-increasing: %s)"%(hw[0],hw[-1],all(hw[i+1]<=hw[i]+1e-6 for i in range(len(hw)-1))))

# determinism
print("\ndeterministic across calls:", bool(np.array_equal(R, v1.fit_itq(V,n_iter=100,seed=101))))
print("seed-sensitive:", not np.array_equal(R, v1.fit_itq(V,n_iter=100,seed=202)))
import inspect
print("fit_itq signature:", inspect.signature(v1.fit_itq))
