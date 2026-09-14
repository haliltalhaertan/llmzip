"""CONTROL: reproduce frozen headline FR@3 numbers (sign vs float)."""
import pickle, glob
import numpy as np

def fr3_exact(scores_list, gold_list, K=3):
    """Exact tie expectation E[FR@K], order-independent."""
    tot = 0.0; n = 0
    for s, g in zip(scores_list, gold_list):
        s = np.asarray(s, float); g = list(g)
        if len(g) == 0:
            continue
        thr = np.sort(s)[::-1][min(K, len(s)-1)]
        better = np.sum(s > thr)
        tied = np.sum(s == thr)
        slots = K - better
        g_strict = sum(1 for r in g if s[r] > thr)
        g_tied = sum(1 for r in g if s[r] == thr)
        tot += (g_strict + g_tied * slots / tied) / len(g)
        n += 1
    return tot / n if n else float('nan'), n

def cosine_scores(C, q):
    Cn = C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-12)
    qn = q / (np.linalg.norm(q) + 1e-12)
    return Cn @ qn

def hamming_scores(C, q):
    return -np.sum((C >= 0) != (q >= 0), axis=1).astype(float)

# LME
fs = sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/*.pkl'))
ss, fl, gg = [], [], []
for f in fs:
    d = pickle.load(open(f, 'rb'))
    C, q = d['C'], d['qC']
    ss.append(hamming_scores(C, q)); fl.append(cosine_scores(C, q)); gg.append(list(d['gold']))
s, n = fr3_exact(ss, gg); flm, _ = fr3_exact(fl, gg)
print(f'LME VERIFIED: sign={s:.6f} float={flm:.6f} delta={(s-flm)*100:.6f}pp n={n}')
print('FROZEN CLAIM: sign=0.542134 float=0.441596 delta=+10.053783pp')
