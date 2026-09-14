#!/usr/bin/env python3
"""Coordinator deep-read of the axis-budget sweep.

Two things the raw table shows that need quantifying with uncertainty:
 1. A per-benchmark crossover m* exists on 3/4 benchmarks (LME 47.3, LoCoMo 53.4,
    REALTALK 42.5) and is ABSENT on PerLTQA. Delta is monotone increasing in m on
    all four -- so the 'per-benchmark offset' is an offset in a SHARED curve shape.
 2. The TOP/BOT/RANDOM ordering REVERSES between benchmarks, and the reversal
    appears to align with the sign of Delta. The brief called this "a major
    finding" if real. Quantify it with bootstrap CIs before believing it.

Also: extrapolate PerLTQA's crossover honestly (it is an extrapolation beyond the
measured range and must be labelled as such).
"""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, 'evidence', 'axis_budget_results.json')))
MS = [8, 12, 16, 24, 32, 48, 64, 80, 96]
BEN = ['LME', 'LoCoMo', 'REALTALK', 'PerLTQA']

print('=== 1. CROSSOVER m*: where does SIGN overtake budget-matched FLOAT? ===')
print(f'  {"bench":10s} {"D(m=8)":>9s} {"D(m=48)":>9s} {"D(m=96)":>9s} {"m*":>8s} '
      f'{"monotone?":>10s}')
cross = {}
for b in BEN:
    bud = R[b]['budgets']
    dv = [bud[str(m)]['delta_matched_pp'] for m in MS]
    mono = all(dv[i] <= dv[i + 1] + 1e-9 for i in range(len(dv) - 1))
    ms = None
    for (m0, v0), (m1, v1) in zip(zip(MS, dv), zip(MS[1:], dv[1:])):
        if (v0 < 0) != (v1 < 0):
            ms = m0 + (m1 - m0) * (0 - v0) / (v1 - v0)
            break
    cross[b] = ms
    print(f'  {b:10s} {dv[0]:>+9.4f} {dv[5]:>+9.4f} {dv[-1]:>+9.4f} '
          f'{(f"{ms:.1f}" if ms else "NONE"):>8s} {str(mono):>10s}')

print('\n  PerLTQA extrapolation (EXTRAPOLATION, beyond measured range -- flagged):')
bud = R['PerLTQA']['budgets']
d80, d96 = bud['80']['delta_matched_pp'], bud['96']['delta_matched_pp']
slope = (d96 - d80) / 16.0
need = 96 + (0 - d96) / slope if slope > 0 else float('inf')
print(f'    slope over m=80..96: {slope:+.5f} pp per axis')
print(f'    linear crossover would need m ~ {need:.0f} axes (vs 96 available)')
print(f'    -> {need/96:.1f}x the available budget. NOT measurable with 96-D vectors.')

print('\n=== 2. THE ORDERING REVERSAL: is BOT better than TOP where SIGN wins? ===')
print('  advantage = sign_bot - sign_top (positive => LOW-variance axes retrieve better)')
print(f'  {"bench":10s} {"Delta96":>9s} ' + ' '.join(f'{"m="+str(m):>9s}' for m in [24, 32, 48, 64, 80]))
adv = {}
for b in BEN:
    bud = R[b]['budgets']
    row = [100 * (bud[str(m)]['sign_bot']['mean'] - bud[str(m)]['sign_top']['mean'])
           for m in [24, 32, 48, 64, 80]]
    adv[b] = row
    print(f'  {b:10s} {bud["96"]["delta_matched_pp"]:>+9.4f} ' +
          ' '.join(f'{v:>+9.4f}' for v in row))

print('\n  Per-benchmark sign of (bot - top) at m=48, against sign of Delta at m=96:')
agree = 0
for b in BEN:
    d96 = R[b]['budgets']['96']['delta_matched_pp']
    a48 = adv[b][2]
    match = (a48 > 0) == (d96 > 0)
    agree += match
    print(f'    {b:10s} bot-top={a48:>+8.4f} pp   Delta={d96:>+8.4f} pp   aligned={match}')
print(f'  -> aligned on {agree}/4 benchmarks')

print('\n=== 3. RANDOM-m as referee (does axis IDENTITY matter, or only count?) ===')
print(f'  {"bench":10s} {"m":>4s} {"top":>9s} {"rand":>9s} {"bot":>9s}   ordering')
for b in BEN:
    bud = R[b]['budgets']
    for m in [48, 64]:
        t = bud[str(m)]['sign_top']['mean']
        r = bud[str(m)]['sign_rand']['mean']
        bo = bud[str(m)]['sign_bot']['mean']
        names = sorted([('top', t), ('rand', r), ('bot', bo)], key=lambda x: -x[1])
        print(f'  {b:10s} {m:>4d} {t:>9.6f} {r:>9.6f} {bo:>9.6f}   '
              f'{" > ".join(n for n, _ in names)}')

print('\n=== 4. FAIRNESS CHECK: budget-matched vs the unfair full-96 float ===')
print(f'  {"bench":10s} {"m":>4s} {"matched_pp":>12s} {"vs_full96_pp":>14s}')
for b in BEN:
    bud = R[b]['budgets']
    for m in [48, 96]:
        print(f'  {b:10s} {m:>4d} {bud[str(m)]["delta_matched_pp"]:>+12.4f} '
              f'{bud[str(m)]["delta_vs_full96_pp"]:>+14.4f}')
print('  (at m=96 the two must coincide -- that is the internal consistency check)')

print('\n=== 5. PerLTQA sections: does the crossover story hold inside one corpus? ===')
sec = R['PerLTQA'].get('sections', {})
if sec:
    print(f'  {"section":22s} ' + ' '.join(f'{"m="+str(m):>9s}' for m in [8, 32, 64, 96]))
    for k, v in sorted(sec.items(), key=lambda x: -x[1]['96']['delta_matched_pp']):
        print(f'  {k:22s} ' + ' '.join(f'{v[str(m)]["delta_matched_pp"]:>+9.4f}'
                                       for m in [8, 32, 64, 96]))
else:
    print('  (no section breakdown captured)')

json.dump({'crossover': cross, 'bot_minus_top_pp': adv,
           'perltqa_extrapolated_m': float(need)},
          open(os.path.join(HERE, 'evidence', 'coord_readout.json'), 'w'), indent=1)
print('\nWROTE evidence/coord_readout.json')
