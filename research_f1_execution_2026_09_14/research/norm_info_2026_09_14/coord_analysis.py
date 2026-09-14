#!/usr/bin/env python3
"""Coordinator analysis of the norm-informativeness results.

DISCIPLINE DISCLOSURE: the subagent that produced evidence/results.json was killed
by an API rate limit BEFORE it wrote PREDICTION.md. No prediction was frozen for
this measurement. Everything below is therefore POST-HOC and must be labelled as
such: the hypothesis ("norm is informative precisely where SIGN loses") is stated
in the dispatch brief, which is on the record, but it was not frozen by the
measuring party before seeing the numbers. Treated as EXPLORATORY, not as a test.
"""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, 'evidence', 'results.json')))
B = d['benchmarks']

print('=== BENCHMARK LEVEL: does norm informativeness track where SIGN loses? ===')
print(f'  {"bench":12s} {"Delta_pp":>10s} {"normAUC":>9s} {"AUC CI":>20s} '
      f'{"normonly-rand_pp":>17s} {"cliffs_d":>9s}')
rowsB = []
for k, v in B.items():
    if 'norm_auc_mean' not in v:
        continue
    ci = v.get('norm_auc_ci', [float('nan')] * 2)
    print(f'  {k:12s} {v["delta_sign_minus_cosine_pp"]:>+10.4f} {v["norm_auc_mean"]:>9.4f} '
          f'[{ci[0]:+.3f},{ci[1]:+.3f}]  {v["delta_normonly_minus_random_pp"]:>+17.4f} '
          f'{v.get("cliffs_delta", float("nan")):>+9.4f}')
    rowsB.append((k, v['delta_sign_minus_cosine_pp'], v['norm_auc_mean']))

sign_wins = [r for r in rowsB if r[1] > 0]
sign_loses = [r for r in rowsB if r[1] < 0]
print(f'\n  SIGN WINS  ({len(sign_wins)}): AUC = ' +
      ', '.join(f'{r[0]} {r[2]:.4f}' for r in sign_wins))
print(f'  SIGN LOSES ({len(sign_loses)}): AUC = ' +
      ', '.join(f'{r[0]} {r[2]:.4f}' for r in sign_loses))
allbelow = all(r[2] < 0.5 for r in sign_wins)
allabove = all(r[2] > 0.5 for r in sign_loses)
print(f'  every SIGN-WIN benchmark has AUC < 0.5 : {allbelow}')
print(f'  every SIGN-LOSS benchmark has AUC > 0.5: {allabove}')
print(f'  -> benchmark-level pattern holds {sum([allbelow, allabove])}/2 '
      f'(n={len(rowsB)} benchmarks, so this is 4 data points, NOT a test)')

print('\n=== SECTION LEVEL (PerLTQA): the same pattern, or a counterexample? ===')
sec = d.get('sections') or B.get('perltqa', {}).get('sections') or {}
if not sec:
    for k, v in B.items():
        if isinstance(v, dict) and 'sections' in v:
            sec = v['sections']
print(f'  {"section":22s} {"Delta_pp":>10s} {"normAUC":>9s} {"normonly":>10s} {"rand":>10s}')
rowsS = []
for k, v in sorted(sec.items(), key=lambda x: -x[1].get('delta_sign_minus_cosine_pp', 0)):
    auc = v.get('norm_auc_mean', float('nan'))
    print(f'  {k:22s} {v.get("delta_sign_minus_cosine_pp", float("nan")):>+10.4f} '
          f'{auc:>9.4f} {v.get("normonly", float("nan")):>10.6f} '
          f'{v.get("random", float("nan")):>10.6f}')
    rowsS.append((k, v.get('delta_sign_minus_cosine_pp'), auc))

viol = [r for r in rowsS if r[1] is not None and not np.isnan(r[2])
        and ((r[1] > 0 and r[2] > 0.5) or (r[1] < 0 and r[2] < 0.5))]
print(f'\n  counterexamples to the benchmark-level pattern: {len(viol)}/{len(rowsS)}')
for k, dd, a in viol:
    print(f'    {k}: Delta={dd:+.4f} pp but AUC={a:.4f}')

print('\n=== STORAGE PRICE: does norm-awareness earn its extra bytes? ===')
print(f'  {"bench":12s} {"sign(12B)":>11s} {"sign*norm(16B)":>15s} {"gain_pp":>9s} '
      f'{"CI":>20s} {"cos(384B)":>11s}')
for k, v in B.items():
    if 'signxnorm' not in v:
        continue
    ci = v.get('ci_signxnorm_minus_sign_pp', [float('nan')] * 2)
    star = '' if (ci[0] < 0 < ci[1]) else '  SIGNIFICANT'
    print(f'  {k:12s} {v["sign"]:>11.6f} {v["signxnorm"]:>15.6f} '
          f'{v["delta_signxnorm_minus_sign_pp"]:>+9.4f} [{ci[0]:+.3f},{ci[1]:+.3f}]'
          f' {v["cosine"]:>11.6f}{star}')

print('\n=== CONSISTENCY: do the two families agree that norm helps? ===')
print('  (rawdot - cosine) isolates norm inside FLOAT; (signxnorm - sign) inside SIGN')
for k, v in B.items():
    if 'delta_rawdot_minus_cosine_pp' not in v:
        continue
    a = v['delta_rawdot_minus_cosine_pp']; b = v['delta_signxnorm_minus_sign_pp']
    print(f'  {k:12s} float-family {a:>+8.4f} pp | sign-family {b:>+8.4f} pp | '
          f'agree: {(a > 0) == (b > 0)}')

print('\n=== IN-SAMPLE TUNING WARNING ===')
for k, v in B.items():
    if 'signadd_best_lambda_INSAMPLE' in v:
        print(f'  {k:12s} best lambda={v["signadd_best_lambda_INSAMPLE"]} '
              f'gain={v["signadd_best_gain_over_sign_pp_INSAMPLE"]:+.4f} pp '
              f'-- chosen ON the evaluation data, NOT a held-out result')
