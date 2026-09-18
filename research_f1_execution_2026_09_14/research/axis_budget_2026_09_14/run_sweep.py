#!/usr/bin/env python3
"""Axis-budget sweep driver. Uses the subagent's axis_budget_core.py unchanged.

Written by the coordinator after the subagent that authored the core library was
killed by an API rate limit before it could write its own driver. The library is
used as-is; only the sweep loop and reporting are new.

Design decisions (recorded because they change what the numbers mean):
 - BUDGET-MATCHED float arm: the float comparison at budget m uses the SAME m
   axes as the sign arm, so the contrast isolates quantization, not dimension.
   The unfair full-96 float reference is reported SEPARATELY at every m.
 - Axis ranking is per-archive mean_i(C_ij^2) descending (== variance here,
   since C is pre-centered). TOP-m = first m, BOT-m = last m.
 - RANDOM-m averages over 10 fixed seeds, drawn per archive.
 - Metric is FR@3 with the exact tie expectation (frozen NT=20 estimator's
   expectation, no sampling noise).
"""
import json, os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from axis_budget_core import (fr_at_k_exact, hamming_batch, cos_batch,
                              LOADERS, K)

BUDGETS = [8, 12, 16, 24, 32, 48, 64, 80, 96]
NSEED = 10
EV = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'evidence')
os.makedirs(EV, exist_ok=True)


def arm_scores(C, Q, idx, quant):
    """quant='sign' -> negative Hamming on axes idx; 'float' -> cosine on axes idx."""
    Cm = C[:, idx]
    Qm = Q[:, idx]
    if quant == 'sign':
        return -hamming_batch((Cm >= 0).astype(np.uint8), (Qm >= 0).astype(np.uint8))
    return cos_batch(Cm, Qm)


def run_bench(name, loader):
    units = loader()
    # accumulators: per budget, per arm -> list of per-query FR@3
    acc = {m: {a: [] for a in ('sign_top', 'sign_bot', 'sign_rand',
                               'float_top', 'float_bot', 'float_rand',
                               'float96')} for m in BUDGETS}
    sect_acc = {}          # PerLTQA sections
    t0 = time.time()
    for ui, (C, Q, golds, labels) in enumerate(units):
        N, D = C.shape
        nq = Q.shape[0]
        gold_size = np.array([len(g) for g in golds], float)
        Gmask = np.zeros((N, nq), bool)
        for j, g in enumerate(golds):
            Gmask[g, j] = True

        order = np.argsort(-(C ** 2).mean(axis=0), kind='stable')   # high -> low
        rng = np.random.default_rng(12345 + ui)
        rand_sets = {m: [rng.choice(D, size=m, replace=False) for _ in range(NSEED)]
                     for m in BUDGETS}

        f96 = fr_at_k_exact(cos_batch(C, Q), Gmask, gold_size, K)

        for m in BUDGETS:
            top = order[:m]
            bot = order[-m:]
            vals = {
                'sign_top': fr_at_k_exact(arm_scores(C, Q, top, 'sign'), Gmask, gold_size, K),
                'sign_bot': fr_at_k_exact(arm_scores(C, Q, bot, 'sign'), Gmask, gold_size, K),
                'float_top': fr_at_k_exact(arm_scores(C, Q, top, 'float'), Gmask, gold_size, K),
                'float_bot': fr_at_k_exact(arm_scores(C, Q, bot, 'float'), Gmask, gold_size, K),
                'float96': f96,
            }
            sr = np.zeros(nq); fr_ = np.zeros(nq)
            for idx in rand_sets[m]:
                sr += fr_at_k_exact(arm_scores(C, Q, idx, 'sign'), Gmask, gold_size, K)
                fr_ += fr_at_k_exact(arm_scores(C, Q, idx, 'float'), Gmask, gold_size, K)
            vals['sign_rand'] = sr / NSEED
            vals['float_rand'] = fr_ / NSEED
            for a, v in vals.items():
                acc[m][a].append(np.asarray(v, float))
            if labels and labels[0] != '':
                for j, lab in enumerate(labels):
                    d = sect_acc.setdefault(lab, {mm: {'s': [], 'f': []} for mm in BUDGETS})
                    d[m]['s'].append(vals['sign_top'][j])
                    d[m]['f'].append(vals['float_top'][j])
        if (ui + 1) % 50 == 0:
            print(f'  {name} {ui+1}/{len(units)} units  {time.time()-t0:.0f}s', flush=True)

    out = {'benchmark': name, 'n_units': len(units), 'budgets': {}}
    for m in BUDGETS:
        row = {}
        for a in acc[m]:
            v = np.concatenate(acc[m][a])
            row[a] = {'mean': float(v.mean()), 'se': float(v.std(ddof=1) / np.sqrt(len(v))),
                      'n': int(len(v))}
        st = np.concatenate(acc[m]['sign_top']); ft = np.concatenate(acc[m]['float_top'])
        d = st - ft
        row['delta_matched_pp'] = float(100 * d.mean())
        row['delta_matched_se_pp'] = float(100 * d.std(ddof=1) / np.sqrt(len(d)))
        f96v = np.concatenate(acc[m]['float96'])
        row['delta_vs_full96_pp'] = float(100 * (st - f96v).mean())
        out['budgets'][str(m)] = row
    if sect_acc:
        out['sections'] = {}
        for lab, d in sect_acc.items():
            out['sections'][lab] = {}
            for m in BUDGETS:
                s = np.array(d[m]['s']); f = np.array(d[m]['f'])
                out['sections'][lab][str(m)] = {
                    'delta_matched_pp': float(100 * (s - f).mean()), 'n': int(len(s))}
    return out


def crossover(bud):
    """First m where the budget-matched delta changes sign; linear interpolation."""
    ms = sorted(int(x) for x in bud)
    vals = [(m, bud[str(m)]['delta_matched_pp']) for m in ms]
    for (m0, v0), (m1, v1) in zip(vals, vals[1:]):
        if v0 == 0:
            return m0
        if (v0 < 0) != (v1 < 0):
            return m0 + (m1 - m0) * (0 - v0) / (v1 - v0)
    return None


if __name__ == '__main__':
    which = sys.argv[1:] or list(LOADERS)
    results = {}
    path = os.path.join(EV, 'axis_budget_results.json')
    if os.path.exists(path):
        results = json.load(open(path))
    for name in which:
        print(f'=== {name} ===', flush=True)
        results[name] = run_bench(name, LOADERS[name])
        json.dump(results, open(path, 'w'), indent=1)      # checkpoint each bench
        b = results[name]['budgets']
        print(f'  {"m":>4} {"sign_top":>10} {"float_top":>10} {"delta_pp":>10} '
              f'{"sign_bot":>10} {"sign_rand":>10}')
        for m in BUDGETS:
            r = b[str(m)]
            print(f'  {m:>4} {r["sign_top"]["mean"]:>10.6f} {r["float_top"]["mean"]:>10.6f} '
                  f'{r["delta_matched_pp"]:>+10.4f} {r["sign_bot"]["mean"]:>10.6f} '
                  f'{r["sign_rand"]["mean"]:>10.6f}', flush=True)
        c = crossover(b)
        print(f'  crossover m* = {c if c is not None else "NONE (no sign change)"}', flush=True)
    print('WROTE', path)
