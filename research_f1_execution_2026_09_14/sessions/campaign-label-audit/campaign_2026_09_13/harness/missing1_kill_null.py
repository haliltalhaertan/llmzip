#!/usr/bin/env python3
"""D5-missing-1: KILL OR-rule null simulation (selection-lift quantification).

[LOCAL EXPLORATORY] [NOT PREREGISTERED] [DISCLOSE-BEFORE-USE]
Question (D5 C1): the pre-declared rule "KILL if mean-vs-best < +1.0pp OR wins < 7/10" is
kill-biased under the null, because best-of-10 (a max statistic) sits above the pool mean by
selection lift alone. How negative SHOULD a no-edge arm look, and where does the observed
drop64/alone64/SPREAD64 sit relative to that null?

Method (reads only the stored round-3 per-question arrays):
- Per split, per-seed mean FRs m_j (j=1..10) of the RANDOM64 panels.
- Null draws (no-edge arm ⇒ behaves like one more independent subset with the same mean
  distribution): leave-one-out gap_j = m_j − max_{i≠j} m_i (arm vs best-of-9 pool).
- Strict-10 correction δ: mean over splits of (max10 − max(9 others)), bracket reported.
- Observed per-arm gaps from the stored run rows; position in the null (sd units, percentile).
"""
import json
import numpy as np
from pathlib import Path

R3 = Path('C:/Users/MDP/dev/llmzip-work/pilots/axis_attack_2026-09-12/round3')
OUT = R3 / 'muse_sessions' / 'd5' / 'missing1_kill_null.json'
MD = R3 / 'muse_sessions' / 'd5' / 'missing1_kill_null.md'


def analyze(fname, arms):
    d = json.loads((R3 / fname).read_text(encoding='utf-8'))
    null, null_wins, n = [], 0, 0
    deltas = []
    obs = {a: [] for a in arms}
    for sp in d['splits']:
        seeds = sp['random_seeds']
        ms = np.array([np.mean(sp['per_q_test'][f'RANDOM64_s{sd}']) for sd in seeds])
        for j in range(len(seeds)):
            g = (ms[j] - np.delete(ms, j).max()) * 100.0
            null.append(g)
            null_wins += int(g > 0)
            n += 1
        deltas.append((ms.max() - np.mean([np.delete(ms, j).max() for j in range(len(seeds))])) * 100.0)
        obs['drop64'].append(sp['run']['gap64_vs_best_pp'])
        if 'alone64' in arms:
            obs['alone64'].append(sp['run']['gap64_alone_vs_best_pp'])
        obs['SPREAD64'].append((sp['arms']['SPREAD64']['test_FR'] - ms.max()) * 100.0)
    null = np.array(null)
    res = {'null_mean_pp': float(null.mean()), 'null_sd_pp': float(null.std(ddof=1)),
           'null_range_pp': [float(null.min()), float(null.max())],
           'null_winrate': float(null_wins / n),
           'strict10_correction_delta_pp': float(np.mean(deltas)),
           'strict10_null_mean_pp': float(null.mean() - np.mean(deltas))}
    for a in arms:
        arr = np.array(obs[a]); m = float(arr.mean())
        res[a] = {'mean_pp': m,
                  'sd_units_vs_null': float((m - null.mean()) / null.std(ddof=1)),
                  'percentile_in_null': float((null < m).mean() * 100.0),
                  'mean_pp_strict10_units': float((m - (null.mean() - np.mean(deltas))) / null.std(ddof=1))}
    return res


r_lme = analyze('deney1_lme_details.json', ['drop64', 'alone64', 'SPREAD64'])
r_loco = analyze('deney1_loco_details.json', ['drop64', 'alone64', 'SPREAD64'])
out = {'labels': ['[LOCAL EXPLORATORY]', '[NOT PREREGISTERED]', '[DISCLOSE-BEFORE-USE]',
                  'D5 missing-analysis #1: kill OR-rule null (selection-lift) quantification'],
       'LME': r_lme, 'LOCOMO': r_loco}
OUT.write_text(json.dumps(out, indent=1), encoding='utf-8')
lines = ['# D5-missing-1 — kill OR-rule null simulation (selection lift)', '']
for bench, r in [('LME', r_lme), ('LOCOMO', r_loco)]:
    lines.append(f"## {bench}")
    lines.append(f"- Null (no-edge arm vs best-of-9): mean **{r['null_mean_pp']:+.2f}pp**, sd {r['null_sd_pp']:.2f}, "
                 f"range [{r['null_range_pp'][0]:+.2f}, {r['null_range_pp'][1]:+.2f}], null win-rate {r['null_winrate']*100:.0f}%")
    lines.append(f"- Strict-10 correction δ = {r['strict10_correction_delta_pp']:+.2f}pp → strict null mean {r['strict10_null_mean_pp']:+.2f}pp")
    for a in ['drop64', 'alone64', 'SPREAD64']:
        v = r[a]
        lines.append(f"- {a}: observed {v['mean_pp']:+.2f}pp = {v['sd_units_vs_null']:+.2f} sd of null "
                     f"(percentile {v['percentile_in_null']:.0f}; strict-10: {v['mean_pp_strict10_units']:+.2f} sd)")
    lines.append('')
MD.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
print('\n'.join(lines))
print('wrote', OUT)
print('MISSING1_DONE')
