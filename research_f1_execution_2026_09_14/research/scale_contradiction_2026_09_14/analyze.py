#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT][NOT PREREGISTERED][NOT FOR CITATION][DISCLOSE-BEFORE-USE]
analyze.py -- aggregate evidence/{A,B,C,D} into evidence/results.json + printed tables."""
import json, os
import numpy as np
from collections import defaultdict

OUT = '/mnt/c/Users/MDP/dev/llmzip-work/agent_out/scale-contradiction/evidence'
R = {}


def m(v):
    return float(np.mean(v)) if len(v) else float('nan')


def se(v):
    v = np.asarray(v, float)
    return float(v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 else float('nan')


# ======================= P0: identity check across ALL sections ==============
dis_ovf_gap0 = 0; tot = 0
for fn in ('A_pool_rows.json', 'B_subsample_rows.json', 'C_natural_rows.json'):
    rows = json.load(open(f'{OUT}/{fn}'))
    for r in rows:
        for K in (1, 3, 5, 10, 20, 50):
            a = r.get(f'sign_K{K}_tie_overflow'); b = r.get(f'sign_K{K}_gap0')
            if a is None or b is None:
                continue
            tot += 1
            if a != b:
                dis_ovf_gap0 += 1
R['P0_identity'] = {'checks': tot, 'disagreements_tie_overflow_vs_gap0': dis_ovf_gap0,
                    'verdict': 'IDENTICAL EVENTS' if dis_ovf_gap0 == 0 else 'DIFFER'}
print('P0 identity: %d checks, %d disagreements -> %s' % (tot, dis_ovf_gap0, R['P0_identity']['verdict']))

# ======================= A: pooling ladder ===================================
A = json.load(open(f'{OUT}/A_pool_rows.json'))
byM = defaultdict(list)
for r in A:
    byM[r['m']].append(r)
lad = []
for mm in sorted(byM):
    rs = byM[mm]
    rec = {'mult': mm, 'N_mean': m([r['N'] for r in rs]), 'n_q': len(rs)}
    for K in (1, 3, 5, 10, 20, 50):
        for nm in ('tie_overflow', 'tie_shared'):
            key = f'sign_K{K}_{nm}'
            if key in rs[0]:
                rec[f'sign_K{K}_{nm}'] = m([r[key] for r in rs])
        if f'sign_K{K}_bc' in rs[0]:
            rec[f'sign_K{K}_bc'] = m([r[f'sign_K{K}_bc'] for r in rs])
            rec[f'sign_K{K}_thr'] = m([r[f'sign_K{K}_thr'] for r in rs])
        if f'float_K{K}_tie_overflow' in rs[0]:
            rec[f'float_K{K}_tie_overflow'] = m([r[f'float_K{K}_tie_overflow'] for r in rs])
    fs = np.array([r['fr3_sign'] for r in rs]); ff = np.array([r['fr3_float'] for r in rs])
    rec['fr3_sign'] = float(fs.mean()); rec['fr3_float'] = float(ff.mean())
    rec['delta_pp'] = float((fs - ff).mean() * 100)
    rec['delta_se_pp'] = float((fs - ff).std(ddof=1) / np.sqrt(len(fs)) * 100)
    rec['sign_dmin'] = m([r['sign_dmin'] for r in rs])
    lad.append(rec)
R['A_pooling'] = lad
print('\n=== A: POOLING LME archives (paired, all 470 queries per rung) ===')
print('%6s %8s %8s %9s %9s %9s %9s %8s %8s %8s' % ('mult', 'N', 'K3_ovf', 'K3_shared', 'K1_ovf',
      'K10_ovf', 'K50_ovf', 'dmin', 'delta', '+-SE'))
for r in lad:
    print('%6d %8.0f %8.3f %9.3f %9.3f %9.3f %9.3f %8.2f %8.2f %8.2f' % (
        r['mult'], r['N_mean'], r['sign_K3_tie_overflow'], r['sign_K3_tie_shared'],
        r['sign_K1_tie_overflow'], r['sign_K10_tie_overflow'], r.get('sign_K50_tie_overflow', float('nan')),
        r['sign_dmin'], r['delta_pp'], r['delta_se_pp']))
print('float K3 overflow tie rate by rung:', ['%.4f' % r['float_K3_tie_overflow'] for r in lad])

# ======================= B: subsampling ======================================
B = json.load(open(f'{OUT}/B_subsample_rows.json'))
print('\n=== B: SUBSAMPLING rows inside ONE real archive ===')
Bres = {}
for fam in sorted(set(r['fam'] for r in B)):
    rs0 = [r for r in B if r['fam'] == fam]
    byN = defaultdict(list)
    for r in rs0:
        byN[r['N']].append(r)
    tab = []
    for N in sorted(byN):
        rs = byN[N]
        rec = {'N': N, 'n': len(rs)}
        for K in (1, 3, 5, 10, 20, 50):
            for nm in ('tie_overflow', 'tie_shared'):
                k = f'sign_K{K}_{nm}'
                if k in rs[0]:
                    rec[k] = m([r[k] for r in rs])
            if f'sign_K{K}_bc' in rs[0]:
                rec[f'sign_K{K}_bc'] = m([r[f'sign_K{K}_bc'] for r in rs])
                rec[f'sign_K{K}_thr'] = m([r[f'sign_K{K}_thr'] for r in rs])
            k = f'float_K{K}_tie_overflow'
            if k in rs[0]:
                rec[k] = m([r[k] for r in rs])
        rec['sign_dmin'] = m([r['sign_dmin'] for r in rs])
        d = [(r['fr3_sign'] - r['fr3_float']) for r in rs if 'fr3_sign' in r]
        rec['n_fr'] = len(d)
        rec['delta_pp'] = m(d) * 100 if d else float('nan')
        rec['delta_se_pp'] = se(d) * 100 if len(d) > 1 else float('nan')
        rec['fr3_sign'] = m([r['fr3_sign'] for r in rs if 'fr3_sign' in r])
        rec['fr3_float'] = m([r['fr3_float'] for r in rs if 'fr3_float' in r])
        tab.append(rec)
    Bres[fam] = tab
    print(f'-- family {fam} --')
    print('%7s %7s %8s %9s %9s %9s %8s %8s %8s %7s' % ('N', 'n', 'K3_ovf', 'K3_shared', 'K1_ovf',
          'K20_ovf', 'K3_bc', 'dmin', 'delta', 'nfr'))
    for r in tab:
        print('%7d %7d %8.3f %9.3f %9.3f %9.3f %8.2f %8.2f %8.2f %7d' % (
            r['N'], r['n'], r['sign_K3_tie_overflow'], r['sign_K3_tie_shared'],
            r['sign_K1_tie_overflow'], r.get('sign_K20_tie_overflow', float('nan')),
            r['sign_K3_bc'], r['sign_dmin'], r['delta_pp'], r['n_fr']))
R['B_subsample'] = Bres

# paired within-archive B: restrict to archives present at BOTH ends
print('\n-- B paired (REALTALK archives with N0>=1500 only, same queries every rung) --')
big = set(r['arch'] for r in B if r['N0'] >= 1500)
rs0 = [r for r in B if r['arch'] in big]
byN = defaultdict(list)
for r in rs0:
    byN[r['N']].append(r)
paired = []
for N in sorted(byN):
    rs = byN[N]
    paired.append({'N': N, 'n': len(rs),
                   'K3_ovf': m([r['sign_K3_tie_overflow'] for r in rs]),
                   'K3_shared': m([r['sign_K3_tie_shared'] for r in rs]),
                   'K3_bc': m([r['sign_K3_bc'] for r in rs]),
                   'K3_thr': m([r['sign_K3_thr'] for r in rs]),
                   'K1_ovf': m([r['sign_K1_tie_overflow'] for r in rs]),
                   'K20_ovf': m([r.get('sign_K20_tie_overflow', np.nan) for r in rs]),
                   'dmin': m([r['sign_dmin'] for r in rs])})
for r in paired:
    print('N=%5d n=%6d K3_ovf=%.3f K3_shared=%.3f bc=%.2f thr=%.1f K1=%.3f K20=%.3f dmin=%.1f'
          % (r['N'], r['n'], r['K3_ovf'], r['K3_shared'], r['K3_bc'], r['K3_thr'], r['K1_ovf'],
             r['K20_ovf'], r['dmin']))
R['B_paired_realtalk_big'] = paired

# ======================= C: natural spread ===================================
C = json.load(open(f'{OUT}/C_natural_rows.json'))
print('\n=== C: NATURAL N spread, per-archive then correlate with N ===')
Cres = {}
for fam in sorted(set(r['fam'] for r in C)):
    rs0 = [r for r in C if r['fam'] == fam]
    byA = defaultdict(list)
    for r in rs0:
        byA[r['arch']].append(r)
    pts = []
    for a, rs in byA.items():
        pts.append({'arch': a, 'N': rs[0]['N'], 'nq': len(rs),
                    'K3_ovf': m([r['sign_K3_tie_overflow'] for r in rs]),
                    'K3_shared': m([r['sign_K3_tie_shared'] for r in rs]),
                    'K3_bc': m([r['sign_K3_bc'] for r in rs]),
                    'K1_ovf': m([r['sign_K1_tie_overflow'] for r in rs]),
                    'K20_ovf': m([r.get('sign_K20_tie_overflow', np.nan) for r in rs]),
                    'delta_pp': m([r['fr3_sign'] - r['fr3_float'] for r in rs if 'fr3_sign' in r]) * 100})
    Ns = np.array([p['N'] for p in pts], float)
    out = {'n_arch': len(pts), 'N_min': float(Ns.min()), 'N_max': float(Ns.max()), 'pts': pts}
    for nm in ('K3_ovf', 'K3_shared', 'K1_ovf', 'K20_ovf', 'delta_pp'):
        y = np.array([p[nm] for p in pts], float)
        ok = np.isfinite(y)
        if ok.sum() > 2 and Ns[ok].std() > 0:
            out[f'pearson_{nm}_vs_N'] = float(np.corrcoef(Ns[ok], y[ok])[0, 1])
            # per-query pooled: also regression slope per +1000 rows
            out[f'slope_{nm}_per1000'] = float(np.polyfit(Ns[ok], y[ok], 1)[0] * 1000)
    Cres[fam] = out
    print('%-9s n_arch=%3d N=[%4.0f,%4.0f]  r(K3_ovf,N)=%+.3f slope/1k=%+.4f  r(K3_shared,N)=%+.3f  r(delta,N)=%+.3f'
          % (fam, out['n_arch'], out['N_min'], out['N_max'], out.get('pearson_K3_ovf_vs_N', np.nan),
             out.get('slope_K3_ovf_per1000', np.nan), out.get('pearson_K3_shared_vs_N', np.nan),
             out.get('pearson_delta_pp_vs_N', np.nan)))
    # per-query mean tie rate for reference
    out['perq_K3_ovf'] = m([r['sign_K3_tie_overflow'] for r in rs0])
    out['perarch_K3_ovf'] = m([p['K3_ovf'] for p in pts])
    print('          per-QUERY mean K3_ovf=%.4f   per-ARCHIVE mean K3_ovf=%.4f'
          % (out['perq_K3_ovf'], out['perarch_K3_ovf']))
R['C_natural'] = Cres

# ======================= D: synthetic ========================================
try:
    D = json.load(open(f'{OUT}/D_synth.json'))
    R['D_synth'] = D
    print('\n=== D: SYNTHETIC codes ===')
    print('%-10s %8s %8s %9s %8s %8s %8s' % ('kind', 'N', 'K3_ovf', 'K3_shared', 'K3_bc', 'K3_thr', 'dmin'))
    for r in D:
        print('%-10s %8d %8.3f %9.3f %8.2f %8.1f %8.1f' % (r['kind'], r['N'], r['K3_tie_overflow'],
              r['K3_tie_shared'], r['K3_bc'], r['K3_thr'], r['dmin']))
except FileNotFoundError:
    print('\n(D not ready)')

json.dump(R, open(f'{OUT}/results.json', 'w'), indent=1)
print('\nWROTE results.json')
