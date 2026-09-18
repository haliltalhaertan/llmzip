import pickle, glob, numpy as np
files = sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/*.pkl'))
print("n_lme_files", len(files))
with open(files[0],'rb') as f:
    d = pickle.load(f)
print(type(d), list(d.keys()) if isinstance(d, dict) else type(d))
for k,v in d.items():
    if isinstance(v, np.ndarray):
        print(k, v.shape, v.dtype, "flat0", v.flat[:3])
    elif isinstance(v, list):
        print(k, "list len", len(v), "sample", v[:5])
    else:
        print(k, repr(v)[:300])
print()
with open(files[1],'rb') as f:
    d2 = pickle.load(f)
print("file2 keys:", list(d2.keys()) if isinstance(d2, dict) else type(d2))
for k,v in d2.items():
    if isinstance(v, np.ndarray):
        print(k, v.shape, v.dtype)
    elif isinstance(v, list):
        print(k, "list len", len(v), "sample", v[:5])
    else:
        print(k, repr(v)[:300])
