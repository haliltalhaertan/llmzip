# Sampled verification: sigma>0 on real cached columns (quant REPORT:26 premise)
"""Read-only scan of cached RealTalk C frames; reports per-archive min column std."""
import glob
import json
import os
import pickle

import numpy as np

out = {}
files = sorted(glob.glob("/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl"))
for p in files:
    with open(p, "rb") as f:
        o = pickle.load(f)
    C = np.asarray(o["C"], dtype=np.float64)
    s = np.std(C, axis=0, ddof=0)
    out[os.path.basename(p)] = {"shape": list(C.shape), "min_std": float(s.min()),
                                "n_zero": int(np.count_nonzero(s == 0.0))}
mins = [v["min_std"] for v in out.values()]
print("archives:", len(out))
print("global min std: %.6g" % min(mins))
print("any exact-zero column:", any(v["n_zero"] for v in out.values()))
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs", "sigma_scan.json"), "w") as f:
    json.dump(out, f, indent=1)
