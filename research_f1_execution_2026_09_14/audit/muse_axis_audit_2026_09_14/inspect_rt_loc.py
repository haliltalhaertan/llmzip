import pickle, glob, numpy as np
fs = sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl'))
print("n_rt", len(fs))
with open(fs[0],'rb') as f:
    d = pickle.load(f)
print(list(d.keys()))
for k,v in d.items():
    if isinstance(v, np.ndarray):
        print(" ", k, v.shape, v.dtype, v.flat[:3])
    elif isinstance(v, list):
        print(" ", k, "list", len(v), repr(v[:3])[:200])
    else:
        print(" ", k, type(v), repr(v)[:200])
print()
fs2 = sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/locomo/locomo_*.pkl'))
print("n_loc", len(fs2))
with open(fs2[0],'rb') as f:
    d = pickle.load(f)
print(list(d.keys()))
for k,v in d.items():
    if isinstance(v, np.ndarray):
        print(" ", k, v.shape, v.dtype, v.flat[:3])
    elif isinstance(v, list):
        print(" ", k, "list", len(v), repr(v[:2])[:300])
    elif isinstance(v, dict):
        ks = list(v.keys())[:3]
        print(" ", k, "dict", len(v), ks)
    else:
        print(" ", k, type(v), repr(v)[:200])
qa = d['qas'][0]
print("qa0:", repr(qa)[:400])
