#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT][NOT PREREGISTERED][NOT FOR CITATION][DISCLOSE-BEFORE-USE]
variants.py -- off-by-one and set-based tie-definition variants, on BOTH ladders.
Last search for a definition that falls 0.54 -> 0.26."""
import json, pickle, glob
import numpy as np
from collections import defaultdict

W = '/mnt/c/Users/MDP/dev/llmzip-work'
OUT = f'{W}/agent_out/scale-contradiction/evidence'
Cs, Qs = [], []
for f in sorted(glob.glob(f'{W}/regen/lme/cache_repr/*.pkl')):
    d = pickle.load(open(f, 'rb'))
    Cs.append(np.asarray(d['C'], np.float32)); Qs.append(np.asarray(d['qC'], np.float32))
nA = len(Cs); sizes = [c.shape[0] for c in Cs]; off = np.cumsum([0] + sizes)
S = np.where(np.vstack(Cs) >= 0, 1.0, -1.0).astype(np.float32)
perms = {i: np.random.default_rng(1234 + i).permutation(np.array([j for j in range(nA) if j != i])) for i in range(nA)}
K = 3


def V(sd):
    thr = sd[K - 1]
    st = int(np.searchsorted(sd, thr, 'left'))
    bc = int(np.searchsorted(sd, thr, 'right')) - st
    slots = K - st
    n = len(sd)
    o = {}
    o['V1_bc_gt_slots'] = int(bc > slots)
    o['V2_bc_ge_slots'] = int(bc >= slots)
    o['V3_bc_gt_slots_p1'] = int(bc > slots + 1)
    o['V4_bc_ge_2'] = int(bc >= 2)
    o['V5_bc_ge_3'] = int(bc >= 3)
    o['V6_uniq_top3_lt_3'] = int(len(np.unique(sd[:K])) < K)
    o['V7_uniq_top3_eq_1'] = int(len(np.unique(sd[:K])) == 1)
    o['V8_d2_eq_d3'] = int(sd[1] == sd[2])
    o['V9_any_dup_in_top3_incl_next'] = int(len(np.unique(sd[:K + 1])) < K + 1)
    o['V10_frac_tied_slots'] = (slots / K) if bc > slots else 0.0
    o['V11_bc_over_K'] = min(bc / K, 1.0)
    o['V12_overflow_size'] = float(max(bc - slots, 0))
    # "candidates within distance 1 of d3" - a soft tie band
    o['V13_band1_gt_K'] = int(int(np.sum(sd <= thr + 1)) > K)
    o['V14_band2_gt_K'] = int(int(np.sum(sd <= thr + 2)) > K)
    # normalized: expected fraction of top-K decided by coin flip
    o['V15_exp_random_frac'] = (bc - slots) / bc if bc > slots else 0.0
    return o


# ladder 1: pooling
MULT = [1, 2, 4, 10, 20, 50]
accP = defaultdict(lambda: defaultdict(list))
# ladder 2: subsample
LAD = [10, 25, 50, 100, 200, 396]
accS = defaultdict(lambda: defaultdict(list))
for i in range(nA):
    sq = np.where(Qs[i] >= 0, 1.0, -1.0).astype(np.float32)
    d_all = (96.0 - (S @ sq)) * 0.5
    for mm in MULT:
        ids = [i] + list(perms[i][:mm - 1])
        idx = np.concatenate([np.arange(off[j], off[j + 1]) for j in ids])
        for k, v in V(np.sort(d_all[idx])).items():
            accP[mm][k].append(v)
    home = d_all[off[i]:off[i + 1]]
    for N in LAD:
        for rep in range(20):
            rng = np.random.default_rng(606 + i * 13 + N * 5 + rep)
            for k, v in V(np.sort(home[rng.choice(len(home), N, replace=False)])).items():
                accS[N][k].append(v)
keys = sorted(accP[1].keys())
out = {'pool': {}, 'subsample': {}}
print('=== VARIANTS on POOLED ladder (N=493..24640) ===')
print('%-30s' % 'variant' + ''.join('%9d' % round(m * 492.8) for m in MULT) + '  trend')
for k in keys:
    v = [float(np.mean(accP[m][k])) for m in MULT]
    out['pool'][k] = v
    tr = 'RISE' if v[-1] > v[0] + 0.02 else ('FALL' if v[-1] < v[0] - 0.02 else 'flat')
    print('%-30s' % k + ''.join('%9.3f' % x for x in v) + '  ' + tr)
print('\n=== VARIANTS on SUBSAMPLE ladder (N=10..396, within-archive) ===')
print('%-30s' % 'variant' + ''.join('%9d' % N for N in LAD) + '  trend')
for k in keys:
    v = [float(np.mean(accS[N][k])) for N in LAD]
    out['subsample'][k] = v
    tr = 'RISE' if v[-1] > v[0] + 0.02 else ('FALL' if v[-1] < v[0] - 0.02 else 'flat')
    print('%-30s' % k + ''.join('%9.3f' % x for x in v) + '  ' + tr)
out['pool_N'] = [round(m * 492.8) for m in MULT]
out['subsample_N'] = LAD
# best L1 fit to 0.54 -> 0.26
print('\nL1 fit to (0.54 first, 0.26 last):')
for lab, dd, Ns in (('pool', out['pool'], out['pool_N']), ('sub', out['subsample'], LAD)):
    sc = sorted(((abs(v[0] - 0.54) + abs(v[-1] - 0.26), k, v) for k, v in dd.items()))[:3]
    for e, k, v in sc:
        print('  %-4s %-30s err=%.3f  %s' % (lab, k, e, ['%.3f' % x for x in v]))
json.dump(out, open(f'{OUT}/V_variants.json', 'w'), indent=1)
print('\nWROTE V_variants.json')
