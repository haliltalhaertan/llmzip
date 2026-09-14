"""Paired SEs for M5 clip contrasts on LongMemEval (slim, per-query paired diffs)."""
import pickle, glob
import numpy as np

K = 3

def efrak(scores, gold, k=K):
    s = np.asarray(scores, dtype=float)
    g = np.asarray(gold, dtype=int)
    thr = np.partition(s, -k)[-k] if s.size >= k else s.min()
    better = s > thr
    tied = s == thr
    n_better = int(better.sum()); bc = int(tied.sum()); slots = k - n_better
    g_strict = int(np.isin(np.where(better)[0], g).sum())
    g_tied = int(np.isin(np.where(tied)[0], g).sum())
    return (g_strict + g_tied * slots / max(bc, 1)) / max(len(g), 1)

fs = sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/*.pkl'))
diffs = {'peak-sign': [], 'tiny-sign': [], 'peak-cos': []}
for f in fs:
    d = pickle.load(open(f, 'rb'))
    C = np.asarray(d['C'], float); q = np.asarray(d['qC'], float)
    g = np.asarray(d['gold']).ravel()
    agree = ((C >= 0) == (q >= 0)).sum(axis=1).astype(float)
    nC = np.linalg.norm(C, axis=1, keepdims=True); nq = np.linalg.norm(q)
    Pn = (C * q) / np.where(nC == 0, 1, nC) / (nq if nq else 1)
    s_sign = efrak(agree, g)
    s_cos = efrak((Pn).sum(axis=1), g)
    s_peak = efrak(np.clip(Pn, -1e-3, 1e-3).sum(axis=1), g)
    s_tiny = efrak(np.clip(Pn, -1e-6, 1e-6).sum(axis=1), g)
    diffs['peak-sign'].append(s_peak - s_sign)
    diffs['tiny-sign'].append(s_tiny - s_sign)
    diffs['peak-cos'].append(s_peak - s_cos)
for name, v in diffs.items():
    v = np.array(v)
    se = v.std(ddof=1) / np.sqrt(len(v))
    print(f'{name}: mean={v.mean()*100:+.3f}pp SE={se*100:.3f}pp t={v.mean()/se:+.2f} n={len(v)}')
