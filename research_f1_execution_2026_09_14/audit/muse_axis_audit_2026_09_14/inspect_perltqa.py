import pickle, numpy as np
with open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_arch_eval.pkl','rb') as f:
    A = pickle.load(f)
print(type(A), len(A))
k0 = next(iter(A))
print("arch key sample:", repr(k0)[:100])
v0 = A[k0]
print(type(v0), list(v0.keys()) if isinstance(v0, dict) else v0)
for k,v in v0.items():
    if isinstance(v, np.ndarray):
        print(" ", k, v.shape, v.dtype, v.flat[:3])
    else:
        print(" ", k, type(v), repr(v)[:300])
with open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_q_eval.pkl','rb') as f:
    Q = pickle.load(f)
print("nq", len(Q))
q0 = next(iter(Q))
print("qid sample:", repr(q0)[:100])
w0 = Q[q0]
print(type(w0), list(w0.keys()) if isinstance(w0, dict) else w0)
for k,v in w0.items():
    if isinstance(v, np.ndarray):
        print(" ", k, v.shape, v.dtype, v.flat[:5])
    else:
        print(" ", k, type(v), repr(v)[:400])
