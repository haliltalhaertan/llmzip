import sys, pickle
sys.path.insert(0, "/mnt/c/Users/MDP/dev/llmzip-work/harness/ref")
import numpy as np
import measure_representation_diagnostics as m
# corrected alternating-rows checker: each column half >=0 -> H=1
c = np.tile(np.array([[-1.]*96,[1.]*96]), (25,1))
d = m.matrix_diagnostics(c)
print("checker2 shape", c.shape, "ge=%.6f gt=%.6f zm=%.6f" % (d['sign_entropy_ge'], d['sign_entropy_gt'], d['zero_mass']))
# manual independent recomputation on one real archive (no matrix_diagnostics): first LME file
from pathlib import Path
f = sorted(Path("/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr").glob("*.pkl"))[0]
dd = pickle.load(open(f,"rb")); C = np.asarray(dd["C"], float)
p_ge=(C>=0).mean(0); H=-p_ge*np.log2(np.where(p_ge==0,1,p_ge))-(1-p_ge)*np.log2(np.where(p_ge==1,1,1-p_ge)); H[(p_ge==0)|(p_ge==1)]=0
print("manual-check", f.name, "N=%d ge_manual=%.12f ge_frozen=%.12f gt_eq=%s zm=%.12f resid=%.3g" % (
 C.shape[0], float(H.mean()), m.matrix_diagnostics(C)['sign_entropy_ge'],
 bool(((C>0).mean(0)==p_ge).all()), float((C==0).mean()), float(np.abs(C.mean(0)).max())))
print("exact zeros in C:", int((C==0).sum()), "of", C.size)
