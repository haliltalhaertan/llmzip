"""CONTROL + TESTS for brainstorm-mechanism pilot.
CONTROL: reproduce frozen headlines (LME Delta +10.053783; PerLTQA section profile/events).
TEST-M1: per-section axis-budget curves on PerLTQA (profile vs events).
TEST-M5: margin-clip sweep bridging cosine -> Hamming on LongMemEval.
"""
import pickle, glob
import numpy as np

K = 3

def efrak(scores, gold, k=K):
    """Exact tie expectation E[FR@K]. scores: higher=better, shape (N,)."""
    s = np.asarray(scores, dtype=float)
    g = np.asarray(gold, dtype=int)
    thr = np.partition(s, -k)[-k] if s.size >= k else s.min()
    better = s > thr
    tied = s == thr
    n_better = int(better.sum())
    bc = int(tied.sum())
    slots = k - n_better
    g_strict = int(np.isin(np.where(better)[0], g).sum())
    g_tied = int(np.isin(np.where(tied)[0], g).sum())
    return (g_strict + g_tied * slots / max(bc, 1)) / max(len(g), 1)

def arms(C, q, gold, axes=None):
    C = np.asarray(C, float); q = np.asarray(q, float)
    if axes is not None:
        C = C[:, axes]; q = q[axes]
    agree = ((C >= 0) == (q >= 0)).sum(axis=1).astype(float)
    denom = np.linalg.norm(C, axis=1) * np.linalg.norm(q)
    cos = (C @ q) / np.where(denom == 0, 1, denom)
    return efrak(agree, gold), efrak(cos, gold)

# ---------- CONTROL 1: LongMemEval ----------
fs = sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/*.pkl'))
ss = fs_ = 0.0
ss = ff = 0.0
for f in fs:
    d = pickle.load(open(f, 'rb'))
    a, b = arms(d['C'], d['qC'], np.asarray(d['gold']).ravel())
    ss += a; ff += b
n = len(fs)
LME_S, LME_F = ss / n, ff / n
print(f'CONTROL LME: SIGN={LME_S:.6f} FLOAT={LME_F:.6f} Delta={(LME_S-LME_F)*100:.6f}pp (frozen +10.053783)')

# ---------- CONTROL 2: PerLTQA sections ----------
A = pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
Q = pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
archC = {c: np.asarray(v['C'], float) for c, v in A.items()}
secS, secF, secN = {}, {}, {}
for qid, v in Q.items():
    a, b = arms(archC[v['char']], np.asarray(v['qC'], float), np.asarray(v['gold']).ravel())
    s = v['section']
    secS[s] = secS.get(s, 0) + a; secF[s] = secF.get(s, 0) + b; secN[s] = secN.get(s, 0) + 1
for s in sorted(secN):
    print(f'CONTROL PerLTQA[{s}]: n={secN[s]} SIGN={secS[s]/secN[s]:.6f} FLOAT={secF[s]/secN[s]:.6f} '
          f'Delta={(secS[s]-secF[s])/secN[s]*100:.3f}pp (frozen profile +20.355, events -12.394)')

# ---------- TEST-M1: per-section budget curves (profile vs events) ----------
order = {}
for c, C in archC.items():
    order[c] = np.argsort((C ** 2).mean(axis=0))[::-1]
MS = [16, 32, 48, 64, 96]
res1 = {m: {'profile': [0, 0, 0], 'events': [0, 0, 0]} for m in MS}
for qid, v in Q.items():
    s = v['section']
    if s not in ('profile', 'events'):
        continue
    C = archC[v['char']]; q = np.asarray(v['qC'], float); g = np.asarray(v['gold']).ravel()
    o = order[v['char']]
    for m in MS:
        a, b = arms(C, q, g, axes=o[:m])
        r = res1[m][s]; r[0] += a; r[1] += b; r[2] += 1
print('TEST-M1 per-section budget curves (Delta pp):')
for m in MS:
    line = []
    for s in ('profile', 'events'):
        a, b, nq = res1[m][s]
        line.append(f'{s}={((a-b)/nq*100):+.3f}')
    print(f'  m={m:3d} ' + '  '.join(line))

# ---------- TEST-M5: margin-clip sweep on LME ----------
TS = [1e-6, 2e-4, 5e-4, 1e-3, 2e-3, 5e-3, 1e-2, np.inf]
acc = {t: [0.0, 0] for t in TS}
for f in fs:
    d = pickle.load(open(f, 'rb'))
    C = np.asarray(d['C'], float); q = np.asarray(d['qC'], float)
    g = np.asarray(d['gold']).ravel()
    nC = np.linalg.norm(C, axis=1, keepdims=True); nq = np.linalg.norm(q)
    Pn = (C * q) / np.where(nC == 0, 1, nC) / (nq if nq else 1)
    amax = np.abs(Pn).max()
    for t in TS:
        tt = amax if t == np.inf else t
        acc[t][0] += efrak(np.clip(Pn, -tt, tt).sum(axis=1), g)
        acc[t][1] += 1
print('TEST-M5 clip sweep LME (mean FR@3 vs clip t on normalized products):')
for t in TS:
    print(f'  t={t if t!=np.inf else "inf-cos"} -> {acc[t][0]/acc[t][1]:.6f}')
print(f'  (endpoints: sign={LME_S:.6f} cos={LME_F:.6f})')
