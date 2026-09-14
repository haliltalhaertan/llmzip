#!/usr/bin/env python3
"""BOT64 survivor: artifact tests (a)-(e).

Written by the coordinator after the authoring subagent was killed by an API rate
limit. It had already completed the expensive part: evidence/rows.pkl holds
per-query strict-rival counts for TOP-m / BOT-m (m in 8..96) and 24 random-64
seeds, plus delta, N, ngold, strict_float, float_margin, arch, section.
This driver only analyses those rows; no re-measurement, no tuning.

Tests, per the brief:
 (a) random-64 subsets vs BOT64 -- if random matches, the statistic is about
     subset SIZE, not axis identity. Run first: it is the most damaging.
 (b) arm-size sweep TOP-m / BOT-m: where is |rho| maximal? Is TOP96 enough?
 (c) proxy check: partial correlations controlling N, ngold, strict_TOP96,
     float_margin.
 (d) mechanical null: shuffle delta within archive, and within (arch, ngold).
 (e) is it driven by the delta==0 mass? recompute on nonzero-delta only.
"""
import json, os, pickle
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(HERE, 'evidence')
BENCH = ['LME', 'REALTALK', 'PerLTQA', 'LoCoMo']
MS = [8, 16, 24, 32, 48, 64, 80, 96]
RNG = np.random.default_rng(20260914)


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
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 3:
        return float('nan')
    ra, rb = avgrank(a), avgrank(b)
    ra -= ra.mean(); rb -= rb.mean()
    d = np.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    return float((ra * rb).sum() / d) if d > 0 else float('nan')


def partial_spearman(a, b, controls):
    """Spearman of a,b after linearly removing rank-transformed controls."""
    ra, rb = avgrank(a), avgrank(b)
    X = np.column_stack([avgrank(c) for c in controls] + [np.ones(len(ra))])
    for v in (ra, rb):
        pass
    resid = []
    for y in (ra, rb):
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        resid.append(y - X @ beta)
    r0, r1 = resid
    d = np.sqrt((r0 ** 2).sum() * (r1 ** 2).sum())
    return float((r0 * r1).sum() / d) if d > 0 else float('nan')


def boot_ci(a, b, nboot=2000, seed=7):
    rng = np.random.default_rng(seed)
    n = len(a)
    vals = np.empty(nboot)
    for i in range(nboot):
        idx = rng.integers(0, n, n)
        vals[i] = spearman(a[idx], b[idx])
    return float(np.nanpercentile(vals, 2.5)), float(np.nanpercentile(vals, 97.5))


rows = pickle.load(open(os.path.join(EV, 'rows.pkl'), 'rb'))
out = {}

for b in BENCH:
    rs = [r for r in rows if r['bench'] == b]
    d = np.array([r['delta'] for r in rs], float)
    res = {'n': len(rs), 'frac_delta_zero': float((d == 0).mean())}

    # CONTROL: the four published survivor coefficients
    bot64 = np.array([r['sN_BOT64'] for r in rs], float)
    rho = spearman(d, bot64)
    lo, hi = boot_ci(d, bot64)
    res['control_rho_BOT64'] = rho
    res['control_ci'] = [lo, hi]

    # (a) random-64 -- the most damaging test
    seeds = sorted(k for k in rs[0] if k.startswith('sN_RND64_s'))
    rnd = [spearman(d, np.array([r[k] for r in rs], float)) for k in seeds]
    res['a_random64'] = {'n_seeds': len(seeds), 'mean': float(np.mean(rnd)),
                         'sd': float(np.std(rnd, ddof=1)),
                         'min': float(np.min(rnd)), 'max': float(np.max(rnd)),
                         'bot64_inside_random_range': bool(np.min(rnd) <= rho <= np.max(rnd))}

    # (b) arm-size sweep
    res['b_sweep'] = {}
    for fam in ('TOP', 'BOT'):
        res['b_sweep'][fam] = {}
        for m in MS:
            k = f'sN_{fam}{m}'
            if k in rs[0]:
                res['b_sweep'][fam][str(m)] = spearman(d, np.array([r[k] for r in rs], float))

    # (c) proxy / partial correlations
    N = np.array([r['N'] for r in rs], float)
    ng = np.array([r['ngold'] for r in rs], float)
    top96 = np.array([r['sN_TOP96'] for r in rs], float)
    fm = np.array([r['float_margin'] for r in rs], float)
    sf = np.array([r['strict_float'] for r in rs], float)
    res['c_partial'] = {
        'raw': rho,
        'ctrl_N': partial_spearman(d, bot64, [N]),
        'ctrl_ngold': partial_spearman(d, bot64, [ng]),
        'ctrl_TOP96': partial_spearman(d, bot64, [top96]),
        'ctrl_float_margin': partial_spearman(d, bot64, [fm]),
        'ctrl_strict_float': partial_spearman(d, bot64, [sf]),
        'ctrl_all': partial_spearman(d, bot64, [N, ng, top96, fm, sf]),
    }

    # (d) mechanical null: shuffle delta within strata
    arch = np.array([r['arch'] for r in rs])
    for label, keys in (('within_arch', [arch]),
                        ('within_arch_ngold', [arch, ng.astype(int).astype(str)])):
        strata = {}
        comb = np.array(['|'.join(str(x[i]) for x in keys) for i in range(len(rs))])
        for i, s in enumerate(comb):
            strata.setdefault(s, []).append(i)
        null = np.empty(500)
        for t in range(500):
            dd = d.copy()
            for idxs in strata.values():
                if len(idxs) > 1:
                    ii = np.array(idxs)
                    dd[ii] = dd[RNG.permutation(ii)]
            null[t] = spearman(dd, bot64)
        res[f'd_null_{label}'] = {
            'mean': float(np.nanmean(null)), 'sd': float(np.nanstd(null, ddof=1)),
            'p2.5': float(np.nanpercentile(null, 2.5)),
            'p97.5': float(np.nanpercentile(null, 97.5)),
            'observed': rho,
            'z': float((rho - np.nanmean(null)) / np.nanstd(null, ddof=1))}

    # (e) nonzero-delta only
    nz = d != 0
    if nz.sum() > 10:
        res['e_nonzero'] = {'n': int(nz.sum()),
                            'rho': spearman(d[nz], bot64[nz]),
                            'rho_all': rho}
    out[b] = res

json.dump(out, open(os.path.join(EV, 'survivor_tests.json'), 'w'), indent=1)

# ---- readable report ----
print('=== CONTROL: four published survivor coefficients ===')
tgt = {'LME': -0.185, 'REALTALK': -0.179, 'PerLTQA': -0.195, 'LoCoMo': -0.308}
for b in BENCH:
    r = out[b]
    print(f'  {b:9s} rho={r["control_rho_BOT64"]:+.4f}  CI[{r["control_ci"][0]:+.3f},'
          f'{r["control_ci"][1]:+.3f}]  published {tgt[b]:+.3f}  '
          f'diff {r["control_rho_BOT64"]-tgt[b]:+.4f}  n={r["n"]}')

print('\n=== (a) THE KILL TEST: random-64 vs BOT64 ===')
for b in BENCH:
    a = out[b]['a_random64']
    print(f'  {b:9s} BOT64={out[b]["control_rho_BOT64"]:+.4f}   random64 mean={a["mean"]:+.4f}'
          f' sd={a["sd"]:.4f} range[{a["min"]:+.4f},{a["max"]:+.4f}]'
          f'  -> BOT64 inside random range: {a["bot64_inside_random_range"]}')

print('\n=== (b) arm-size sweep (rho vs delta) ===')
print(f'  {"bench":9s} ' + ' '.join(f'{"T"+str(m):>8s}' for m in MS))
for b in BENCH:
    s = out[b]['b_sweep']['TOP']
    print(f'  {b:9s} ' + ' '.join(f'{s.get(str(m), float("nan")):>+8.4f}' for m in MS))
print(f'  {"":9s} ' + ' '.join(f'{"B"+str(m):>8s}' for m in MS))
for b in BENCH:
    s = out[b]['b_sweep']['BOT']
    print(f'  {b:9s} ' + ' '.join(f'{s.get(str(m), float("nan")):>+8.4f}' for m in MS))

print('\n=== (c) partial correlations (is it just competition?) ===')
for b in BENCH:
    c = out[b]['c_partial']
    print(f'  {b:9s} raw={c["raw"]:+.4f}  |N={c["ctrl_N"]:+.4f}  |ngold={c["ctrl_ngold"]:+.4f}'
          f'  |TOP96={c["ctrl_TOP96"]:+.4f}  |margin={c["ctrl_float_margin"]:+.4f}'
          f'  |all={c["ctrl_all"]:+.4f}')

print('\n=== (d) mechanical null (shuffled delta) ===')
for b in BENCH:
    for lab in ('within_arch', 'within_arch_ngold'):
        n = out[b][f'd_null_{lab}']
        print(f'  {b:9s} {lab:18s} null={n["mean"]:+.4f}+-{n["sd"]:.4f} '
              f'[{n["p2.5"]:+.4f},{n["p97.5"]:+.4f}]  obs={n["observed"]:+.4f}  z={n["z"]:+.1f}')

print('\n=== (e) driven by the delta==0 mass? ===')
for b in BENCH:
    e = out[b].get('e_nonzero')
    if e:
        print(f'  {b:9s} all n={out[b]["n"]} rho={e["rho_all"]:+.4f}  |  '
              f'nonzero n={e["n"]} ({100*(1-out[b]["frac_delta_zero"]):.1f}%) rho={e["rho"]:+.4f}')
print('\nWROTE', os.path.join(EV, 'survivor_tests.json'))
