#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT][NOT PREREGISTERED][NOT FOR CITATION][DISCLOSE-BEFORE-USE]
pin.py -- (H) full intermediate ladders for every definition (E pooled + F subsample);
          (I) locate the definition matching the relayed 54% -> 26%;
          (J) adversarial self-checks."""
import json, pickle, glob
import numpy as np

W = '/mnt/c/Users/MDP/dev/llmzip-work'
OUT = f'{W}/agent_out/scale-contradiction/evidence'
E = json.load(open(f'{OUT}/E_defsweep_pool.json'))
F = json.load(open(f'{OUT}/F_subsample_lme.json'))
res = {}

print('=== H: FULL intermediate ladders ===')
keys = sorted(k for k in F[0] if k.startswith('D')) + ['_thr', '_bc']
print('\n-- F: within-archive subsample, all 470 LME archives, 20 reps --')
hdr = '%-36s' % 'definition' + ''.join('%9s' % str(r['N']) for r in F)
print(hdr)
FT = {}
for k in keys:
    v = [r.get(k, float('nan')) for r in F]
    FT[k] = v
    print('%-36s' % k + ''.join('%9.3f' % x for x in v))
print('\n-- E: pooled ladder, 470 LME queries --')
print('%-36s' % 'definition' + ''.join('%9d' % round(r['mult'] * 492.8) for r in E))
ET = {}
for k in keys:
    v = [r.get(k, float('nan')) for r in E]
    ET[k] = v
    print('%-36s' % k + ''.join('%9.3f' % x for x in v))
res['H_F_ladder'] = {'N': [str(r['N']) for r in F], 'defs': FT}
res['H_E_ladder'] = {'N': [round(r['mult'] * 492.8) for r in E], 'defs': ET}

# ---------------- I: which definition falls from ~0.54 to ~0.26 ----------------
print('\n=== I: SEARCH for a definition matching relayed 0.54 -> 0.26 (falling) ===')
cands = []
for src, T, Ns in (('F_subsample', FT, [str(r['N']) for r in F]), ('E_pool', ET, [round(r['mult']*492.8) for r in E])):
    for k, v in T.items():
        v = np.asarray(v, float)
        if not np.all(np.isfinite(v)):
            continue
        if v[0] > v[-1] + 0.05:
            cands.append((src, k, list(np.round(v, 3)), Ns))
print('FALLING definitions found:')
for s, k, v, Ns in cands:
    print('  %-14s %-34s %s   (N: %s)' % (s, k, v, Ns))
res['I_falling'] = [{'source': s, 'definition': k, 'ladder': v, 'N': [str(x) for x in Ns]} for s, k, v, Ns in cands]

# targeted: sweep the threshold-position statistic P(d_(3) >= t) over t and N
print('\n=== I2: P(d_(3) >= t) vs N, targeted "concentrated mass vs sparse tail" statistic ===')
Cs, Qs, Gs = [], [], []
for f in sorted(glob.glob(f'{W}/regen/lme/cache_repr/*.pkl')):
    d = pickle.load(open(f, 'rb'))
    Cs.append(np.asarray(d['C'], np.float32)); Qs.append(np.asarray(d['qC'], np.float32))
LAD = [10, 25, 50, 100, 200, 396]
THR = [34, 36, 38, 40, 42, 44, 46, 48]
acc = {N: [] for N in LAD}
accF = {N: [] for N in LAD}
for i, C in enumerate(Cs):
    N0 = C.shape[0]
    S = np.where(C >= 0, 1.0, -1.0).astype(np.float32)
    sq = np.where(Qs[i] >= 0, 1.0, -1.0).astype(np.float32)
    df = (96.0 - (S @ sq)) * 0.5
    for N in LAD:
        for rep in range(20):
            rng = np.random.default_rng(9000 + i * 31 + N * 7 + rep)
            sub = rng.choice(N0, N, replace=False)
            sd = np.sort(df[sub])
            acc[N].append(float(sd[2]))
            st = int(np.sum(sd < sd[2])); bc = int(np.sum(sd == sd[2]))
            accF[N].append(int(bc > (3 - st)))
print('%6s %8s' % ('N', 'frozen') + ''.join('%9s' % ('d3>=%d' % t) for t in THR) + '%9s' % 'mean_d3')
i2 = {}
for N in LAD:
    a = np.asarray(acc[N])
    row = [float(np.mean(a >= t)) for t in THR]
    i2[N] = {'frozen_tie': float(np.mean(accF[N])), 'P_d3_ge': dict(zip(map(str, THR), row)), 'mean_d3': float(a.mean())}
    print('%6d %8.3f' % (N, np.mean(accF[N])) + ''.join('%9.3f' % x for x in row) + '%9.2f' % a.mean())
res['I2_threshold_position'] = i2

# ---------------- J: adversarial self-checks ----------------
print('\n=== J: ADVERSARIAL SELF-CHECKS ===')
# J1 exactness of float32 hamming
C = Cs[0]; S = np.where(C >= 0, 1.0, -1.0).astype(np.float32)
sq = np.where(Qs[0] >= 0, 1.0, -1.0).astype(np.float32)
d32 = (96.0 - (S @ sq)) * 0.5
d_ref = np.count_nonzero((C >= 0) != (Qs[0] >= 0)[None, :], axis=1).astype(float)
print('J1 float32-matmul hamming == popcount hamming:', bool(np.array_equal(d32, d_ref)))
res['J1_hamming_exact'] = bool(np.array_equal(d32, d_ref))

# J2 does pooling look like a real archive? compare distance-distribution shape
A = json.load(open(f'{OUT}/A_pool_rows.json'))
m1 = [r for r in A if r['m'] == 1]; m50 = [r for r in A if r['m'] == 50]
print('J2 pooled dmin m=1 %.2f -> m=50 %.2f (home archive always present; pooling adds only FAR mass)'
      % (np.mean([r['sign_dmin'] for r in m1]), np.mean([r['sign_dmin'] for r in m50])))
print('   pooled mean-d m=1 %.2f -> m=50 %.2f' % (np.mean([r['sign_dmean'] for r in m1]),
      np.mean([r['sign_dmean'] for r in m50])))
res['J2_pool_dmin'] = {'m1_dmin': float(np.mean([r['sign_dmin'] for r in m1])),
                       'm50_dmin': float(np.mean([r['sign_dmin'] for r in m50])),
                       'm1_dmean': float(np.mean([r['sign_dmean'] for r in m1])),
                       'm50_dmean': float(np.mean([r['sign_dmean'] for r in m50]))}

# J3 MOST DAMAGING ASSUMPTION: that the ONE real archive family with a 3.8x natural N span
#    (REALTALK 410..1548) shows the same sign as pooling. Test per-archive, unpooled.
Cn = json.load(open(f'{OUT}/C_natural_rows.json'))
rt = [r for r in Cn if r['fam'] == 'REALTALK']
byA = {}
for r in rt:
    byA.setdefault(r['arch'], []).append(r)
pts = sorted([(v[0]['N'], float(np.mean([x['sign_K3_tie_overflow'] for x in v])),
               float(np.mean([x['sign_K3_tie_shared'] for x in v])), len(v)) for v in byA.values()])
print('J3 REALTALK natural spread (NO pooling, NO subsampling) — real archives only:')
for N, t, s, n in pts:
    print('    N=%5d  frozen_tie=%.3f  shared=%.3f  nq=%d' % (N, t, s, n))
Nv = np.array([p[0] for p in pts], float); Tv = np.array([p[1] for p in pts])
print('    Pearson r(frozen_tie, N) = %+.3f over %d real archives' % (np.corrcoef(Nv, Tv)[0, 1], len(pts)))
res['J3_realtalk_natural'] = {'pts': [{'N': p[0], 'frozen': p[1], 'shared': p[2], 'nq': p[3]} for p in pts],
                              'pearson': float(np.corrcoef(Nv, Tv)[0, 1])}

# J4 does the direction survive if the FR@3 gold-forcing in F is removed? (tie stats never used gold)
print('J4 tie statistics never read gold -> gold-forcing cannot bias any tie-rate ladder. '
      'It CAN bias the F delta ladder (gold share of pool is 1/25 at N=25 vs ~1/493 at FULL).')
res['J4_note'] = 'tie stats gold-independent; F delta ladder confounded by gold prevalence'

json.dump(res, open(f'{OUT}/H_pin.json', 'w'), indent=1)
print('\nWROTE H_pin.json')
