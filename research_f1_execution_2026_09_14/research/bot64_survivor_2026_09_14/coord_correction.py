#!/usr/bin/env python3
"""CORRECTION to artifact test (d) + the two follow-ups the results demand.

MY BUG (coordinator, disclosed): in artifact_tests.py the mechanical null shuffles
Delta WITHIN archive. LongMemEval has 470 archives with exactly ONE query each, so
that permutation is the identity: the "null" was the observed value by construction
(sd=0.0000, z=+1.0 meaningless). The LME row of test (d) was VACUOUS. The other
three benchmarks have 70-275 queries per archive and are unaffected.

Fix: for LME use a GLOBAL permutation (no within-archive structure exists to
preserve). Also add a stratified-by-ngold null for LME, which IS meaningful.

Follow-ups forced by the results:
 F1. Test (c) showed controlling for strict_TOP96 collapses rho. Quantify how much
     of the survivor is independent of plain competition, per benchmark, with CIs.
 F2. Test (e) showed rho STRENGTHENS on nonzero-Delta queries on 3/4 benchmarks
     (LoCoMo -0.31 -> -0.74) but WEAKENS on PerLTQA (-0.20 -> -0.17). PerLTQA is
     the sign-reversed benchmark. Check whether that asymmetry is real.
"""
import json, os, pickle
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(HERE, 'evidence')
BENCH = ['LME', 'REALTALK', 'PerLTQA', 'LoCoMo']


def avgrank(v):
    v = np.asarray(v, float)
    order = np.argsort(v, kind='stable')
    r = np.empty(len(v), float)
    sv = v[order]
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and sv[j + 1] == sv[i]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = avgrank(a), avgrank(b)
    ra = ra - ra.mean(); rb = rb - rb.mean()
    d = np.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    return float((ra * rb).sum() / d) if d > 0 else float('nan')


def partial(a, b, ctrl):
    ra, rb = avgrank(a), avgrank(b)
    X = np.column_stack([avgrank(c) for c in ctrl] + [np.ones(len(ra))])
    res = []
    for y in (ra, rb):
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        res.append(y - X @ beta)
    d = np.sqrt((res[0] ** 2).sum() * (res[1] ** 2).sum())
    return float((res[0] * res[1]).sum() / d) if d > 0 else float('nan')


def boot(fn, n, nboot=1500, seed=11):
    rng = np.random.default_rng(seed)
    v = np.empty(nboot)
    for i in range(nboot):
        v[i] = fn(rng.integers(0, n, n))
    return float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))


rows = pickle.load(open(os.path.join(EV, 'rows.pkl'), 'rb'))
RNG = np.random.default_rng(4242)
out = {}

print('=== (d) CORRECTED mechanical null ===')
print('  LME previously used a within-archive shuffle that was the IDENTITY (1 query/archive).')
print(f'  {"bench":9s} {"null_type":20s} {"null mean+-sd":>18s} {"95% null":>20s} '
      f'{"observed":>9s} {"z":>7s}')
for b in BENCH:
    rs = [r for r in rows if r['bench'] == b]
    d = np.array([r['delta'] for r in rs], float)
    bot64 = np.array([r['sN_BOT64'] for r in rs], float)
    ng = np.array([r['ngold'] for r in rs], float)
    arch = np.array([r['arch'] for r in rs])
    obs = spearman(d, bot64)
    out.setdefault(b, {})['observed'] = obs

    nq_per_arch = len(rs) / len(set(arch))
    kinds = [('global', None), ('within_ngold', ng.astype(int).astype(str))]
    if nq_per_arch > 1.5:
        kinds.append(('within_arch', arch))
    for label, key in kinds:
        null = np.empty(1000)
        for t in range(1000):
            dd = d.copy()
            if key is None:
                dd = dd[RNG.permutation(len(dd))]
            else:
                for u in np.unique(key):
                    ii = np.where(key == u)[0]
                    if len(ii) > 1:
                        dd[ii] = dd[RNG.permutation(ii)]
            null[t] = spearman(dd, bot64)
        m, s = float(np.nanmean(null)), float(np.nanstd(null, ddof=1))
        z = (obs - m) / s if s > 0 else float('nan')
        out[b][f'null_{label}'] = {'mean': m, 'sd': s, 'z': float(z),
                                   'p2.5': float(np.nanpercentile(null, 2.5)),
                                   'p97.5': float(np.nanpercentile(null, 97.5))}
        print(f'  {b:9s} {label:20s} {m:>+9.4f}+-{s:<7.4f} '
              f'[{np.nanpercentile(null,2.5):+.4f},{np.nanpercentile(null,97.5):+.4f}] '
              f'{obs:>+9.4f} {z:>+7.1f}')

print('\n=== F1. How much of the survivor is NOT plain competition? ===')
print('  strict_TOP96 IS the full sign arm rival count. If rho dies controlling for it,')
print('  BOT64 adds nothing beyond "gold has many rivals".')
print(f'  {"bench":9s} {"raw":>9s} {"|TOP96":>9s} {"CI(|TOP96)":>20s} {"survives?":>10s}')
for b in BENCH:
    rs = [r for r in rows if r['bench'] == b]
    d = np.array([r['delta'] for r in rs], float)
    bot = np.array([r['sN_BOT64'] for r in rs], float)
    t96 = np.array([r['sN_TOP96'] for r in rs], float)
    raw = spearman(d, bot)
    pt = partial(d, bot, [t96])
    lo, hi = boot(lambda ix: partial(d[ix], bot[ix], [t96[ix]]), len(d))
    surv = not (lo < 0 < hi)
    out[b]['partial_TOP96'] = {'value': pt, 'ci': [lo, hi], 'excludes_zero': bool(surv)}
    print(f'  {b:9s} {raw:>+9.4f} {pt:>+9.4f} [{lo:+.4f},{hi:+.4f}] {str(surv):>10s}')

print('\n=== F2. The nonzero-Delta asymmetry ===')
print('  rho on ALL queries vs rho on queries where SIGN and FLOAT actually differ')
print(f'  {"bench":9s} {"all":>9s} {"nonzero":>9s} {"CI(nonzero)":>20s} {"n_nz":>6s} {"Delta96":>9s}')
d96 = {'LME': +10.0538, 'REALTALK': +5.3001, 'PerLTQA': -6.2747, 'LoCoMo': +6.6550}
for b in BENCH:
    rs = [r for r in rows if r['bench'] == b]
    d = np.array([r['delta'] for r in rs], float)
    bot = np.array([r['sN_BOT64'] for r in rs], float)
    nz = d != 0
    rn = spearman(d[nz], bot[nz])
    lo, hi = boot(lambda ix: spearman(d[nz][ix], bot[nz][ix]), int(nz.sum()))
    out[b]['nonzero'] = {'rho': rn, 'ci': [lo, hi], 'n': int(nz.sum())}
    print(f'  {b:9s} {spearman(d,bot):>+9.4f} {rn:>+9.4f} [{lo:+.4f},{hi:+.4f}] '
          f'{int(nz.sum()):>6d} {d96[b]:>+9.4f}')

print('\n  Is PerLTQA (the sign-REVERSED benchmark) different from the other three?')
per = out['PerLTQA']['nonzero']
others = [out[b]['nonzero'] for b in ('LME', 'REALTALK', 'LoCoMo')]
sep = all(per['ci'][0] > o['ci'][1] for o in others)
print(f'    PerLTQA nonzero rho={per["rho"]:+.4f} CI[{per["ci"][0]:+.4f},{per["ci"][1]:+.4f}]')
for b in ('LME', 'REALTALK', 'LoCoMo'):
    o = out[b]['nonzero']
    print(f'    {b:9s} nonzero rho={o["rho"]:+.4f} CI[{o["ci"][0]:+.4f},{o["ci"][1]:+.4f}]')
print(f'    PerLTQA CI disjoint from ALL three sign-positive benchmarks: {sep}')

json.dump(out, open(os.path.join(EV, 'survivor_corrected.json'), 'w'), indent=1)
print('\nWROTE evidence/survivor_corrected.json')
