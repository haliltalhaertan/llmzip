#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT] axis ordering statistic: mean-of-squares vs variance."""
import pickle
from pathlib import Path
import numpy as np
ROOT = Path('/mnt/c/Users/MDP/dev/llmzip-work')
arch = pickle.load(open(ROOT / 'bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
agree_ord = 0; agree_top = 0; mx = 0.0; mxc = 0.0
for char, a in arch.items():
    C = np.asarray(a['C'], float)
    v_ms = (C ** 2).mean(axis=0); v_var = C.var(axis=0)
    o1 = np.argsort(-v_ms, kind='stable'); o2 = np.argsort(-v_var, kind='stable')
    agree_ord += int(np.array_equal(o1, o2))
    agree_top += int(np.array_equal(np.sort(o1[:64]), np.sort(o2[:64])))
    mx = max(mx, float(np.abs(v_ms - v_var).max()))
    mxc = max(mxc, float(np.abs(C.mean(axis=0)).max()))
print(f'archives={len(arch)}  full ordering identical: {agree_ord}/30   TOP64 set identical: {agree_top}/30')
print(f'max |mean_of_squares - variance| over all axes/archives = {mx:.3e}')
print(f'max |column mean| (centering check)                     = {mxc:.3e}')
print('=> identical because ddof=0 variance of an already-centered matrix IS the mean of squares.')
lme = None
import glob
f = sorted(glob.glob(str(ROOT / 'regen/lme/cache_repr/*.pkl')))[0]
d = pickle.load(open(f, 'rb')); C = np.asarray(d['C'], float)
print(f'LME sample {Path(f).name}: C{C.shape} col-mean absmax {np.abs(C.mean(0)).max():.3e}')
f = sorted(glob.glob(str(ROOT / 'bench3/runs/b3a_realtalk/rt_repr/RT*.pkl')))[0]
d = pickle.load(open(f, 'rb')); C = np.asarray(d['C'], float)
print(f'RT  sample {Path(f).name}: C{C.shape} col-mean absmax {np.abs(C.mean(0)).max():.3e}')
# locomo key inspection for the untestable record
for f in sorted(glob.glob(str(ROOT / 'regen/locomo/locomo_*.pkl')))[:1]:
    d = pickle.load(open(f, 'rb'))
    print('LoCoMo keys:', sorted(d.keys()))
    print('  qas[0] keys:', sorted(d['qas'][0].keys()) if d.get('qas') else None)
    print('  id_to_row size:', len(d.get('id_to_row', {})), 'sample ids:', list(d.get('id_to_row', {}))[:3])
    if d.get('qas'): print('  qas[0] sample:', {k: v for k, v in list(d['qas'][0].items())[:8]})
