#!/usr/bin/env python3
"""STEP 2b: frozen eval — native SIGN96 vs float96 FR@3 + ladder arms + tie diagnostics."""
import json, pickle, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

K = 3; NT = 20
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/tmp/b3b/results.json')

arch = pickle.load(open('/tmp/b3b/cache_arch_eval.pkl', 'rb'))
QDAT = pickle.load(open('/tmp/b3b/cache_q_eval.pkl', 'rb'))
ORD = json.load(open('/tmp/b3b/resolution.json'))['ordinals']

def met(top, g):
    s = set(map(int, top)); gg = set(map(int, g))
    x = len(s & gg)
    return float(x > 0), float(x == len(gg) and len(gg) > 0), float(x / len(gg))

def rh(d, p): return np.lexsort((p, np.asarray(d)))
def rf(s, p): return np.lexsort((p, -np.asarray(s, dtype=np.float64)))
def cos(C, q):
    dn = np.linalg.norm(C, axis=1); qn = np.linalg.norm(q)
    return (C @ q) / (dn * qn)

# per-archive static structures
A = {}
for char, a in arch.items():
    C = np.asarray(a['C'], float); N = a['N']
    D0 = C >= 0
    v = C.var(axis=0)
    order_desc = np.argsort(-v, kind='stable')
    arms = {}
    for k in (80, 64, 48):
        arms[f'TOP{k}'] = np.sort(order_desc[:k]).astype(int)
        arms[f'BOT{k}'] = np.sort(order_desc[-k:]).astype(int)
        pos = np.round(np.linspace(0, 95, k)).astype(int)
        assert len(np.unique(pos)) == k
        arms[f'SPREAD{k}'] = np.sort(order_desc[pos]).astype(int)
        for j in range(10):
            sd = 91000 + j
            arms[f'RANDOM{k}_s{sd}'] = np.sort(np.random.default_rng(sd).choice(96, k, replace=False)).astype(int)
    pr = [np.random.default_rng(5_100_000 + ORD[char] * 100_000 + t * 100 + 99).random(N) for t in range(NT)]
    A[char] = dict(C=C, N=N, D0=D0, arms=arms, pr=pr)

METHODS = ['native', 'float'] + [f'TOP{k}' for k in (80, 64, 48)] + [f'BOT{k}' for k in (80, 64, 48)] + \
    [f'SPREAD{k}' for k in (80, 64, 48)] + [f'RANDOM{k}_s{91000+j}' for k in (80, 64, 48) for j in range(10)]
per_q = {}
tie_nat = []; gap_nat = []; tie_flt = []; gap_flt = []
nan_cos = 0
for n, (qid, q) in enumerate(QDAT.items()):
    if n % 2000 == 0: print(f'  {n}/{len(QDAT)}', flush=True)
    char = q['char']; sec = q['section']; g = np.asarray(q['gold']).ravel(); qC = np.asarray(q['qC'], float)
    a = A[char]; C = a['C']; pr = a['pr']
    D0 = a['D0']; Q0 = qC >= 0
    d0 = np.count_nonzero(D0 != Q0[None, :], axis=1)
    base = cos(C, qC)
    if not np.all(np.isfinite(base)):
        nan_cos += 1
    row = {'char': char, 'section': sec, 'gold_size': int(len(g))}
    # native
    acc = [met(rh(d0, p)[:K], g) for p in pr]
    row['native'] = float(np.mean([x[2] for x in acc])); row['native_any'] = float(np.mean([x[0] for x in acc])); row['native_all'] = float(np.mean([x[1] for x in acc]))
    sd = np.sort(d0); d3 = int(sd[K - 1]); lt = int(np.sum(d0 < d3)); bc = int(np.sum(d0 == d3)); slots = K - lt
    tie_nat.append(int(bc > slots)); gap_nat.append(float(sd[K] - sd[K - 1]) if len(sd) > K else float('nan'))
    row['tie'] = int(bc > slots); row['tie_bc'] = bc; row['gap'] = float(sd[K] - sd[K - 1])
    # float
    acc = [met(rf(base, p)[:K], g) for p in pr]
    row['float'] = float(np.mean([x[2] for x in acc])); row['float_any'] = float(np.mean([x[0] for x in acc])); row['float_all'] = float(np.mean([x[1] for x in acc]))
    ss = np.sort(np.asarray(base, float))[::-1]; s3 = float(ss[K - 1])
    fbc = int(np.sum(np.asarray(base, float) == s3)); flt_ = int(np.sum(np.asarray(base, float) > s3)); fslots = K - flt_
    tie_flt.append(int(fbc > fslots)); gap_flt.append(float(ss[K - 1] - ss[K]))
    # arms (hamming on column subsets, native sign codes)
    for name, cols in a['arms'].items():
        d = np.count_nonzero(D0[:, cols] != Q0[cols][None, :], axis=1)
        acc = [met(rh(d, p)[:K], g) for p in pr]
        row[name] = float(np.mean([x[2] for x in acc]))
    per_q[qid] = row

print('QAs scored:', len(per_q), 'nonfinite-cos QAs:', nan_cos, flush=True)
agg = {}
for m in METHODS:
    vals = np.array([r[m] for r in per_q.values()])
    agg[m] = {'n': int(len(vals)), 'mean': float(vals.mean()), 'min': float(vals.min()), 'max': float(vals.max())}
by_sec = defaultdict(lambda: defaultdict(list))
for r in per_q.values():
    for m in METHODS:
        by_sec[r['section']][m].append(r[m])
sec_agg = {s: {m: {'n': len(v), 'mean': float(np.mean(v))} for m, v in d.items()} for s, d in by_sec.items()}
ties = {'native_tie_rate': float(np.mean(tie_nat)), 'native_tie_n': int(np.sum(tie_nat)),
        'native_mean_gap': float(np.mean(gap_nat)), 'float_tie_rate': float(np.mean(tie_flt)),
        'float_tie_n': int(np.sum(tie_flt)), 'float_mean_gap': float(np.mean(gap_flt)), 'n': len(per_q)}
out = {'n_qa': len(per_q), 'K': K, 'NT': NT, 'aggregate': agg, 'by_section': sec_agg, 'ties': ties,
       'arm_defs': {'TOPk': 'stable-descending archive variance order, first k', 'BOTk': 'same order, last k',
                    'SPREADk': 'round(linspace(0,95,k)) positions over descending-variance order (deney1 repaired)',
                    'RANDOMk': 'default_rng(91000+j).choice(96,k,replace=False) sorted, j=0..9 (deney1 split-0 formula)'},
       'per_q': per_q}
OUT.write_text(json.dumps(out))
print('HEADLINE native=%.4f float=%.4f' % (agg['native']['mean'], agg['float']['mean']), flush=True)
print('wrote', str(OUT), flush=True)
