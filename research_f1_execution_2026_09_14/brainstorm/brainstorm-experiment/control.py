# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# control.py — reproduce frozen LME headline Delta=+10.053783 as CONTROL (VERIFIED target)
import pickle, glob, numpy as np

def E_fr3(scores, gold, K, larger_better):
    s = np.asarray(scores, float); gold = list(int(g) for g in gold)
    thr_vals = np.sort(s if larger_better else -s)[::-1]  # descending best-first
    # K-th best value:
    part = np.partition(s, -K if larger_better else K-1)
    thr = part[-K] if larger_better else part[K-1]
    if larger_better:
        better = np.sum(s > thr); tied = np.sum(s == thr)
        strict = sum(1 for i in gold if s[i] > thr); gt = sum(1 for i in gold if s[i] == thr)
    else:
        better = np.sum(s < thr); tied = np.sum(s == thr)
        strict = sum(1 for i in gold if s[i] < thr); gt = sum(1 for i in gold if s[i] == thr)
    return (strict + gt * (K - better) / max(tied, 1)) / max(len(gold), 1)

fs = sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/*.pkl'))
ss = fs_ = 0.0; n = 0
for f in fs:
    d = pickle.load(open(f, 'rb'))
    C = np.asarray(d['C'], float); qC = np.asarray(d['qC'], float); gold = d['gold']
    cn = np.linalg.norm(C, axis=1); qn = np.linalg.norm(qC)
    cos = (C @ qC) / (cn * qn + 1e-30)
    ham = np.sum((C >= 0).astype(np.int8) != (qC >= 0).astype(np.int8), axis=1).astype(float)
    ss += E_fr3(cos, gold, 3, True); fs_ += E_fr3(ham, gold, 3, False); n += 1
print(f'LME CONTROL n={n} SIGN={fs_/n:.6f} FLOAT={ss/n:.6f} Delta={(fs_-ss)/n*100:.6f}pp  (frozen: 0.542134/0.441596/+10.053783)')
