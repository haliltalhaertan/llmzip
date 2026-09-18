#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT][NOT PREREGISTERED][NOT FOR CITATION][DISCLOSE-BEFORE-USE]
mech.py -- quantify the resolving mechanism: how fast does d_(3) move left per doubling of N,
under pooling vs within-archive growth? Plus a fine threshold fit to the relayed 0.54->0.26."""
import json, pickle, glob
import numpy as np
from collections import defaultdict

W = '/mnt/c/Users/MDP/dev/llmzip-work'
OUT = f'{W}/agent_out/scale-contradiction/evidence'
res = {}
Cs, Qs = [], []
for f in sorted(glob.glob(f'{W}/regen/lme/cache_repr/*.pkl')):
    d = pickle.load(open(f, 'rb'))
    Cs.append(np.asarray(d['C'], np.float32)); Qs.append(np.asarray(d['qC'], np.float32))
nA = len(Cs); sizes = [c.shape[0] for c in Cs]; off = np.cumsum([0] + sizes)
S = np.where(np.vstack(Cs) >= 0, 1.0, -1.0).astype(np.float32)
perms = {i: np.random.default_rng(1234 + i).permutation(np.array([j for j in range(nA) if j != i])) for i in range(nA)}

SUB = [10, 25, 50, 100, 200, 300, 396]
MULT = [1, 2, 4, 10, 20, 50]
aS = defaultdict(lambda: defaultdict(list)); aP = defaultdict(lambda: defaultdict(list))
for i in range(nA):
    sq = np.where(Qs[i] >= 0, 1.0, -1.0).astype(np.float32)
    d_all = (96.0 - (S @ sq)) * 0.5
    home = d_all[off[i]:off[i + 1]]
    for N in SUB:
        for rep in range(20):
            rng = np.random.default_rng(808 + i * 7 + N * 3 + rep)
            sd = np.sort(home[rng.choice(len(home), N, replace=False)])
            thr = sd[2]; st = int(np.sum(sd < thr)); bc = int(np.sum(sd == thr))
            aS[N]['d3'].append(float(thr)); aS[N]['bc'].append(bc)
            aS[N]['tie'].append(int(bc > (3 - st)))
    for mm in MULT:
        ids = [i] + list(perms[i][:mm - 1])
        idx = np.concatenate([np.arange(off[j], off[j + 1]) for j in ids])
        sd = np.sort(d_all[idx])
        thr = sd[2]; st = int(np.sum(sd < thr)); bc = int(np.sum(sd == thr))
        aP[mm]['d3'].append(float(thr)); aP[mm]['bc'].append(bc)
        aP[mm]['tie'].append(int(bc > (3 - st)))

print('=== MECHANISM: how fast does d_(3) move left per DOUBLING of N? ===')
for lab, keys, Ns, acc in (('WITHIN-ARCHIVE (subsample LME)', SUB, SUB, aS),
                           ('POOLING (unrelated LME archives)', MULT, [round(m * 492.8) for m in MULT], aP)):
    d3 = np.array([np.mean(acc[k]['d3']) for k in keys])
    bc = np.array([np.mean(acc[k]['bc']) for k in keys])
    ti = np.array([np.mean(acc[k]['tie']) for k in keys])
    Nl = np.log2(np.array(Ns, float))
    slope = np.polyfit(Nl, d3, 1)[0]
    print(f'\n-- {lab} --')
    print('%8s %9s %8s %8s' % ('N', 'mean_d3', 'mean_bc', 'tie'))
    for n, a, b, t in zip(Ns, d3, bc, ti):
        print('%8d %9.2f %8.2f %8.3f' % (n, a, b, t))
    print('  d_(3) slope = %+.3f bits per doubling of N   (tie %.3f -> %.3f)' % (slope, ti[0], ti[-1]))
    res[lab] = {'N': [int(x) for x in Ns], 'd3': list(map(float, d3)), 'bc': list(map(float, bc)),
                'tie': list(map(float, ti)), 'd3_bits_per_doubling': float(slope)}

# fine threshold fit to relayed 0.54 -> 0.26
print('\n=== FINE FIT: P(d_(3) >= t) ladders, all integer t ===')
best = []
for lab, keys, Ns, acc in (('subsample', SUB, SUB, aS), ('pool', MULT, [round(m * 492.8) for m in MULT], aP)):
    for t in range(20, 50):
        v = [float(np.mean(np.asarray(acc[k]['d3']) >= t)) for k in keys]
        e = abs(v[0] - 0.54) + abs(v[-1] - 0.26)
        best.append((e, lab, t, v, Ns))
best.sort()
for e, lab, t, v, Ns in best[:6]:
    print('  %-10s P(d3>=%2d) err=%.3f  %s  N=%s' % (lab, t, e, ['%.3f' % x for x in v], Ns))
res['fine_fit_top'] = [{'ladder': l, 't': t, 'err': float(e), 'vals': v, 'N': [int(x) for x in Ns]}
                       for e, l, t, v, Ns in best[:6]]
json.dump(res, open(f'{OUT}/M_mechanism.json', 'w'), indent=1)
print('\nWROTE M_mechanism.json')
