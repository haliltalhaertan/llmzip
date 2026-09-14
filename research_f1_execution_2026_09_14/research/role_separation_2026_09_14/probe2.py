#!/usr/bin/env python3
import pickle, numpy as np, json
BASE = "/mnt/c/Users/MDP/dev/llmzip-work"
A = pickle.load(open(BASE + "/bench3/runs/b3b_perltqa/cache_arch_eval.pkl", "rb"))
Q = pickle.load(open(BASE + "/bench3/runs/b3b_perltqa/cache_q_eval.pkl", "rb"))
print("n_arch", len(A), "n_q", len(Q))
k0 = list(A.keys())[0]
print("arch key", repr(k0), "sub", {k: (v.shape if hasattr(v, 'shape') else v) for k, v in A[k0].items()})
q0 = list(Q.keys())[0]
print("q key", repr(q0), "sub", {k: (v.shape if hasattr(v, 'shape') else v) for k, v in Q[q0].items()})
secs = {}
for v in Q.values():
    secs[v.get("section")] = secs.get(v.get("section"), 0) + 1
print("sections", secs)
gl = [len(np.atleast_1d(v["gold"])) for v in Q.values()]
print("gold sizes", np.bincount(gl)[:8])
R = pickle.load(open(BASE + "/bench3/runs/b3a_realtalk/rt_repr/" + __import__("os").listdir(BASE + "/bench3/runs/b3a_realtalk/rt_repr")[0], "rb"))
print("RT keys", {k: (v.shape if hasattr(v, 'shape') else (len(v) if isinstance(v, (list, dict)) else v)) for k, v in R.items()})
