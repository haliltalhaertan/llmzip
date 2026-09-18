#!/usr/bin/env python3
"""RACE official analysis — primary contrast, bootstrap CIs, 16-cell disposition.
Frozen rules: frozen_literals.json (rb1) + RB1 d2 notebook §3-§4.
[LOCAL] labels; no network."""
import json
import numpy as np
from pathlib import Path

B = Path('C:/Users/MDP/dev/llmzip-work')
OUT = B / 'race_2026-09-13' / 'analysis'
OUT.mkdir(parents=True, exist_ok=True)

sign = json.load(open(B / 'race_2026-09-13/official_run/sign/race_sign_details.json'))
faiss = json.load(open(B / 'race_2026-09-13/official_run/faiss/race_faiss_details.json'))
lit = json.load(open(B / 'race_2026-09-13/rb1/frozen_literals.json'))

RAND = [f'RAND48_s{j}' for j in range(10)] + [f'RAND64_s{j}' for j in range(10)] + [f'RAND80_s{j}' for j in range(10)]
COMP = {
    'LME': RAND + ['SPREAD48', 'SPREAD64', 'SPREAD80', 'BOT48', 'TOP48', 'TOP64'],
    'LoCoMo': RAND + ['SPREAD48', 'SPREAD64', 'SPREAD80', 'BOT80', 'BOT64', 'BOT48', 'TOP48'],
}
RQ = ['A4_spread_rot94101', 'A4_spread_rot94102', 'A4_spread_rot94103']
PQ = ['A6_PQ']
BENCH_KEY = {'LME': 'lme', 'LoCoMo': 'locomo'}

report = {'labels': ['[LOCAL]', '[NOT PUSHED]'], 'seeds': {'bootstrap': {'B': 5000}, 'note': 'frozen literals'},
          'benchmarks': {}}
details = {}

for bench in ('LME', 'LoCoMo'):
    qids = sign[bench]['qids']
    n = len(qids)
    sign_fr = np.array(sign[bench]['arms']['NATIVE96']['fr'], dtype=float)
    assert len(sign_fr) == n

    comp_arrays = {}
    for name in COMP[bench]:
        comp_arrays[name] = np.array(sign[bench]['arms'][name]['fr'], dtype=float)
    for name in RQ + PQ:
        d = faiss['arms_per_q'][name][BENCH_KEY[bench]]
        arr = np.array([d[q] for q in qids], dtype=float)
        comp_arrays[name] = arr

    K = len(comp_arrays)
    assert K == (40 if bench == 'LME' else 41), (bench, K)

    means = {name: arr.mean() for name, arr in comp_arrays.items()}
    best_name = max(means, key=means.get)
    sign_mean = float(sign_fr.mean())
    obs_gap_pp = (sign_mean - means[best_name]) * 100.0

    kill = lit['kill_line_pp'][bench.upper() if bench != 'LoCoMo' else 'LOCOMO']
    kill = lit['kill_line_pp']['LME'] if bench == 'LME' else lit['kill_line_pp']['LOCOMO']
    pro = lit['promote_line_pp']['LME'] if bench == 'LME' else lit['promote_line_pp']['LOCOMO']
    if obs_gap_pp < kill:
        zone = 'KILL'
    elif obs_gap_pp < -0.5:
        zone = 'LOW'
    elif obs_gap_pp < pro:
        zone = 'MID'
    else:
        zone = 'PRO'

    # ---- bootstrap: question-paired, argmax re-selected inside each resample ----
    seed = lit['bootstrap']['base_seed'] + lit['bootstrap']['offsets']['LME_primary' if bench == 'LME' else 'LOCOMO_primary']
    rng = np.random.default_rng(seed)
    Bn = lit['bootstrap']['B']
    mat = np.vstack([comp_arrays[name] for name in comp_arrays])  # K x n
    names_order = list(comp_arrays.keys())
    gap_b = np.empty(Bn)
    win_count = np.zeros(K, dtype=int)
    for b in range(Bn):
        idx = rng.integers(0, n, n)
        sm = sign_fr[idx].mean()
        cm = mat[:, idx].mean(axis=1)
        j = int(cm.argmax())
        win_count[j] += 1
        gap_b[b] = (sm - cm[j]) * 100.0
    ci = np.percentile(gap_b, [2.5, 97.5])
    win_freq = {names_order[j]: int(win_count[j]) for j in np.argsort(-win_count)[:6]}

    # secondary: fixed-argmax paired CI (seed +10), plus LoCoMo cluster CI (descriptive)
    rng2 = np.random.default_rng(seed + lit['bootstrap']['offsets']['secondaries'])
    best_arr = comp_arrays[best_name]
    gap_fixed = np.empty(Bn)
    for b in range(Bn):
        idx = rng2.integers(0, n, n)
        gap_fixed[b] = (sign_fr[idx].mean() - best_arr[idx].mean()) * 100.0
    ci_fixed = np.percentile(gap_fixed, [2.5, 97.5])

    cluster_ci = None
    if bench == 'LoCoMo':
        clust = np.array([int(q.split('_')[1]) for q in qids])  # locomo_{ci}_qa{j}
        ucl = np.unique(clust)
        rng3 = np.random.default_rng(seed + lit['bootstrap']['offsets']['secondaries'])
        gap_cl = np.empty(Bn)
        for b in range(Bn):
            pick = rng3.choice(ucl, size=len(ucl), replace=True)
            idx = np.concatenate([np.where(clust == c)[0] for c in pick])
            sm = sign_fr[idx].mean()
            cm = mat[:, idx].mean(axis=1)
            gap_cl[b] = (sm - cm.max()) * 100.0
        cluster_ci = np.percentile(gap_cl, [2.5, 97.5])

    report['benchmarks'][bench] = {
        'n': n, 'K': K, 'sign_mean': sign_mean, 'best_competitor': best_name,
        'best_competitor_mean': means[best_name], 'obs_gap_pp': obs_gap_pp,
        'kill_line_pp': kill, 'promote_line_pp': pro, 'zone': zone,
        'bootstrap_seed': int(seed),
        'primary_CI95_pp': [float(ci[0]), float(ci[1])],
        'argmax_win_freq_top': win_freq,
        'fixed_argmax_CI95_pp': [float(ci_fixed[0]), float(ci_fixed[1])],
        'cluster_CI95_pp': [float(x) for x in cluster_ci] if cluster_ci is not None else None,
        'comp_means_top5': {k: means[k] for k in sorted(means, key=means.get, reverse=True)[:5]},
    }
    details[bench] = {
        'qids': qids,
        'gap_bootstrap': gap_b.tolist(),
    }

# ---- 16-cell disposition ----
zone_lme = report['benchmarks']['LME']['zone']
zone_loco = report['benchmarks']['LoCoMo']['zone']
table = {
    ('KILL', 'KILL'): 'KILL', ('KILL', 'LOW'): 'KILL', ('KILL', 'MID'): 'KILL', ('KILL', 'PRO'): 'KILL',
    ('LOW', 'KILL'): 'KILL', ('LOW', 'LOW'): 'HOLD-weak', ('LOW', 'MID'): 'HOLD-weak', ('LOW', 'PRO'): 'HOLD-split',
    ('MID', 'KILL'): 'KILL', ('MID', 'LOW'): 'HOLD-weak', ('MID', 'MID'): 'HOLD-parity', ('MID', 'PRO'): 'PROMOTE*',
    ('PRO', 'KILL'): 'KILL', ('PRO', 'LOW'): 'HOLD-split', ('PRO', 'MID'): 'PROMOTE*', ('PRO', 'PRO'): 'PROMOTE*',
}
disp = table[(zone_lme, zone_loco)]
report['disposition'] = {'zone_LME': zone_lme, 'zone_LoCoMo': zone_loco, 'cell': disp,
                         'action': 'retain SIGN12B; no kill, no promote' if disp.startswith('HOLD') else disp}

(OUT / 'analysis_details.json').write_text(json.dumps({'report': report, 'bootstrap_arrays': {k: v['gap_bootstrap'] for k, v in details.items()}}, indent=1), encoding='utf-8')
(OUT / 'analysis_report.json').write_text(json.dumps(report, indent=1), encoding='utf-8')

print(json.dumps(report, indent=1))
