#!/usr/bin/env python3
"""Probe cache structures (READ-ONLY)."""
import pickle, glob, json
import numpy as np

R = '/mnt/c/Users/MDP/dev/llmzip-work'

print('=== LME ===')
fs = sorted(glob.glob(R + '/regen/lme/cache_repr/*.pkl'))
print('n files', len(fs))
d = pickle.load(open(fs[0], 'rb'))
print('keys', list(d.keys()))
for k, v in d.items():
    print('  ', k, type(v).__name__, getattr(v, 'shape', v if not hasattr(v, '__len__') or isinstance(v, str) else len(v)))
print('C dtype', np.asarray(d['C']).dtype, 'colmean absmax', np.abs(np.asarray(d['C'], float).mean(0)).max())

print()
print('=== REALTALK ===')
fs = sorted(glob.glob(R + '/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl'))
print('n files', len(fs))
d = pickle.load(open(fs[0], 'rb'))
print('keys', list(d.keys()))
for k, v in d.items():
    print('  ', k, type(v).__name__, getattr(v, 'shape', len(v) if hasattr(v, '__len__') else v))
print('gold_rows[:5]', [d['gold_rows'][i] for i in range(min(5, len(d['gold_rows'])))])
tot = 0; usable = 0
for f in fs:
    dd = pickle.load(open(f, 'rb'))
    tot += len(dd['gold_rows'])
    usable += sum(1 for g in dd['gold_rows'] if len(np.asarray(g).ravel()) > 0)
print('total q', tot, 'usable(gold>0)', usable)

print()
print('=== PERLTQA ===')
arch = pickle.load(open(R + '/bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
print('n arch', len(arch))
k0 = list(arch)[0]
print('arch keys', list(arch[k0].keys()), 'C shape', np.asarray(arch[k0]['C']).shape, 'N', arch[k0]['N'])
Q = pickle.load(open(R + '/bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
print('n q', len(Q))
q0 = list(Q)[0]
print('q keys', list(Q[q0].keys()), 'sample', {kk: (np.asarray(vv).shape if kk == 'qC' else vv) for kk, vv in Q[q0].items()})
from collections import Counter
print('sections', Counter(v['section'] for v in Q.values()))
print('Ns', sorted(a['N'] for a in arch.values())[:5], '...', sorted(a['N'] for a in arch.values())[-3:])

print()
print('=== LOCOMO ===')
fs = sorted(glob.glob(R + '/regen/locomo/locomo_*.pkl'))
print('n files', len(fs))
d = pickle.load(open(fs[0], 'rb'))
print('keys', list(d.keys()))
for k, v in d.items():
    if k == 'qas':
        print('   qas', len(v), 'qa0 keys', list(v[0].keys()))
        print('   qa0', {kk: (str(vv)[:80]) for kk, vv in v[0].items()})
    elif k == 'id_to_row':
        print('   id_to_row', len(v), list(v.items())[:3])
    else:
        print('  ', k, type(v).__name__, getattr(v, 'shape', str(v)[:60]))
# gold resolution count
tot = 0; res = 0
for f in fs:
    dd = pickle.load(open(f, 'rb'))
    i2r = dd['id_to_row']
    for qa in dd['qas']:
        tot += 1
        ev = qa.get('raw_evidence')
        if ev is None: continue
        if isinstance(ev, str): ev = [ev]
        rows = [i2r[e] for e in ev if e in i2r]
        if len(rows) > 0: res += 1
print('locomo total qas', tot, 'resolvable', res)
