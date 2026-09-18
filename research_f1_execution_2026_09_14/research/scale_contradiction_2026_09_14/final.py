#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT][NOT PREREGISTERED][NOT FOR CITATION][DISCLOSE-BEFORE-USE]
final.py -- (K) pin the FALLING definition on the SAME N ladder that makes the frozen tie RISE;
            (L) pure-random subsample ladder (NO gold forcing) over the widest possible real N span."""
import json, pickle, glob
import numpy as np
from collections import defaultdict

W = '/mnt/c/Users/MDP/dev/llmzip-work'
OUT = f'{W}/agent_out/scale-contradiction/evidence'
res = {}

# -------- load LME --------
Cs, Qs, Gs = [], [], []
for f in sorted(glob.glob(f'{W}/regen/lme/cache_repr/*.pkl')):
    d = pickle.load(open(f, 'rb'))
    Cs.append(np.asarray(d['C'], np.float32)); Qs.append(np.asarray(d['qC'], np.float32))
    Gs.append(np.asarray(d['gold']).ravel().astype(int))
nA = len(Cs); sizes = [c.shape[0] for c in Cs]; off = np.cumsum([0] + sizes)
Call = np.vstack(Cs)
S = np.where(Call >= 0, 1.0, -1.0).astype(np.float32)
perms = {i: np.random.default_rng(1234 + i).permutation(np.array([j for j in range(nA) if j != i])) for i in range(nA)}

# ===== K: same pooled ladder, frozen tie vs "d3 in the concentrated mass" =====
MULT = [1, 2, 4, 10, 20, 50]
THR = list(range(24, 42, 2))
acc = defaultdict(lambda: defaultdict(list))
for i in range(nA):
    sq = np.where(Qs[i] >= 0, 1.0, -1.0).astype(np.float32)
    d_all = (96.0 - (S @ sq)) * 0.5
    for mm in MULT:
        ids = [i] + list(perms[i][:mm - 1])
        idx = np.concatenate([np.arange(off[j], off[j + 1]) for j in ids])
        sd = np.sort(d_all[idx])
        thr = sd[2]; st = int(np.sum(sd < thr)); bc = int(np.sum(sd == thr))
        acc[mm]['frozen'].append(int(bc > (3 - st)))
        acc[mm]['d3'].append(float(thr))
        for t in THR:
            acc[mm][f'd3_ge_{t}'].append(int(thr >= t))
print('=== K: POOLED LME ladder — the SAME N rungs, two different statistics ===')
print('%8s %9s %8s' % ('N', 'frozen', 'mean_d3') + ''.join('%8s' % ('>=%d' % t) for t in THR))
K = []
for mm in MULT:
    N = round(mm * 492.8)
    rec = {'N': N, 'frozen': float(np.mean(acc[mm]['frozen'])), 'mean_d3': float(np.mean(acc[mm]['d3']))}
    for t in THR:
        rec[f'P_d3_ge_{t}'] = float(np.mean(acc[mm][f'd3_ge_{t}']))
    K.append(rec)
    print('%8d %9.3f %8.2f' % (N, rec['frozen'], rec['mean_d3']) + ''.join('%8.3f' % rec[f'P_d3_ge_{t}'] for t in THR))
res['K_pooled_two_statistics'] = K
best = None
for t in THR:
    v = [r[f'P_d3_ge_{t}'] for r in K]
    err = abs(v[0] - 0.54) + abs(v[-1] - 0.26)
    if best is None or err < best[0]:
        best = (err, t, v)
print('\nBEST MATCH to relayed 0.54->0.26 on the POOLED ladder: P(d3 >= %d) = %s  (L1 err %.3f)'
      % (best[1], ['%.3f' % x for x in best[2]], best[0]))
res['K_best_match'] = {'threshold': best[1], 'ladder': best[2], 'L1_err': best[0],
                       'N': [r['N'] for r in K]}

# ===== L: PURE random subsample (no gold forcing), widest real N span =====
print('\n=== L: PURE random subsample within ONE real archive (no gold forcing) ===')
arch = []
for f in sorted(glob.glob(f'{W}/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl')):
    d = pickle.load(open(f, 'rb'))
    arch.append(('REALTALK', np.asarray(d['C'], np.float32), np.asarray(d['QC'], np.float32)))
for i in range(10):
    d = pickle.load(open(f'{W}/regen/locomo/locomo_{i}.pkl', 'rb'))
    arch.append(('LOCOMO', np.asarray(d['C'], np.float32), np.asarray(d['QC'], np.float32)))
for i in range(120):
    arch.append(('LME', Cs[i], Qs[i][None, :]))
LAD = [10, 25, 50, 100, 200, 400, 800, 1400]
acc2 = defaultdict(lambda: defaultdict(list))
for fam, C, QC in arch:
    N0 = C.shape[0]
    Sx = np.where(C >= 0, 1.0, -1.0).astype(np.float32)
    for j in range(QC.shape[0]):
        sq = np.where(QC[j] >= 0, 1.0, -1.0).astype(np.float32)
        df = (96.0 - (Sx @ sq)) * 0.5
        for N in LAD:
            if N > N0:
                continue
            for rep in range(10):
                rng = np.random.default_rng(4242 + N * 17 + rep * 3 + j)
                sd = np.sort(df[rng.choice(N0, N, replace=False)])
                thr = sd[2]; st = int(np.sum(sd < thr)); bc = int(np.sum(sd == thr))
                acc2[(fam, N)]['frozen'].append(int(bc > (3 - st)))
                acc2[(fam, N)]['shared'].append(int(bc > 1))
                acc2[(fam, N)]['d3'].append(float(thr))
                acc2[(fam, N)]['d3_ge_40'].append(int(thr >= 40))
                acc2[(fam, N)]['d3_ge_36'].append(int(thr >= 36))
L = []
for fam in ('LME', 'LOCOMO', 'REALTALK'):
    print(f'-- {fam} --')
    print('%7s %8s %9s %9s %8s %9s %9s' % ('N', 'n', 'frozen', 'shared', 'mean_d3', 'P(d3>=40)', 'P(d3>=36)'))
    for N in LAD:
        k = (fam, N)
        if k not in acc2:
            continue
        a = acc2[k]
        rec = {'fam': fam, 'N': N, 'n': len(a['frozen']), 'frozen': float(np.mean(a['frozen'])),
               'shared': float(np.mean(a['shared'])), 'mean_d3': float(np.mean(a['d3'])),
               'P_d3_ge_40': float(np.mean(a['d3_ge_40'])), 'P_d3_ge_36': float(np.mean(a['d3_ge_36']))}
        L.append(rec)
        print('%7d %8d %9.3f %9.3f %8.2f %9.3f %9.3f' % (N, rec['n'], rec['frozen'], rec['shared'],
              rec['mean_d3'], rec['P_d3_ge_40'], rec['P_d3_ge_36']))
res['L_pure_subsample'] = L
json.dump(res, open(f'{OUT}/K_final.json', 'w'), indent=1)
print('\nWROTE K_final.json')
