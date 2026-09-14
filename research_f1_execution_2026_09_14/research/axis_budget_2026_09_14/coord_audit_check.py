#!/usr/bin/env python3
"""Coordinator verification of the Muse audit's three most damaging findings.

The audit says my CLAIM 2 ("low-variance axes retrieve better where sign wins") is
not a fact about the SIGN arm at all, because float_bot - float_top shows the same
effect and is LARGER. I stored float_bot and float_top in the sweep but never looked
at them. Check it directly.

Also check:
 - monotonicity, which my own readout printed and my published text contradicted;
 - the TOP/BOT overlap the audit says I never disclosed (at m=64 they share 32 axes);
 - overlap-free exclusive contrasts, which the audit says still show a real effect;
 - the m=96 mechanical-convergence question (bot-top = 0 by construction);
 - the PerLTQA extrapolation across fitting windows.
"""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, 'evidence', 'axis_budget_results.json')))
MS = [8, 12, 16, 24, 32, 48, 64, 80, 96]
BEN = ['LME', 'LoCoMo', 'REALTALK', 'PerLTQA']

print('=== FINDING A: is the bot-vs-top effect SIGN-specific, or in BOTH arms? ===')
print('  If float shows it too (and bigger), my CLAIM 2 was mis-attributed.')
print(f'  {"bench":9s} {"m":>4s} {"sign_bot-top":>13s} {"float_bot-top":>14s} {"ratio f/s":>10s}')
mis = 0
for b in BEN:
    bud = R[b]['budgets']
    for m in [32, 48, 64]:
        s = 100 * (bud[str(m)]['sign_bot']['mean'] - bud[str(m)]['sign_top']['mean'])
        f = 100 * (bud[str(m)]['float_bot']['mean'] - bud[str(m)]['float_top']['mean'])
        ratio = f / s if abs(s) > 1e-9 else float('nan')
        flag = ''
        if abs(f) > abs(s):
            flag = '  <-- FLOAT effect LARGER'
            mis += 1
        print(f'  {b:9s} {m:>4d} {s:>+13.4f} {f:>+14.4f} {ratio:>10.2f}{flag}')
print(f'\n  cells where the float effect exceeds the sign effect: {mis}/12')
print('  -> if this is most cells, the effect belongs to the AXES, not to quantization.')

print('\n=== FINDING B: monotonicity -- my own code computed it; did my text match? ===')
for b in BEN:
    dv = [R[b]['budgets'][str(m)]['delta_matched_pp'] for m in MS]
    mono = all(dv[i] <= dv[i + 1] + 1e-9 for i in range(len(dv) - 1))
    dips = [(MS[i], MS[i + 1], dv[i + 1] - dv[i])
            for i in range(len(dv) - 1) if dv[i + 1] < dv[i] - 1e-9]
    print(f'  {b:9s} monotone={str(mono):5s} total_rise={dv[-1]-dv[0]:+8.3f} pp'
          + (f'  DIPS: {dips}' if dips else ''))
print('  Published text said "all four show the SAME qualitative shape".')

print('\n=== FINDING C: TOP/BOT overlap (undisclosed in my writeup) ===')
print(f'  {"m":>4s} {"TOP_m + BOT_m":>14s} {"shared axes":>12s} {"disjoint?":>10s}')
for m in MS:
    shared = max(0, 2 * m - 96)
    print(f'  {m:>4d} {2*m:>14d} {shared:>12d} {str(shared == 0):>10s}')
print('  At m=48 TOP/BOT partition exactly. At m=64 they share 32 axes; at m=96 they')
print('  are THE SAME SET, so bot-top = 0 identically -- a mechanical convergence.')

print('\n=== FINDING D: does the m=96 identity drive the "4/4 alignment"? ===')
print('  My claim compared bot-top at m=48 against Delta at m=96 (different budgets).')
print('  Same-m comparison instead:')
print(f'  {"bench":9s} ' + ' '.join(f'{"m="+str(m):>10s}' for m in [24, 32, 48, 64, 80]))
for b in BEN:
    bud = R[b]['budgets']
    row = []
    for m in [24, 32, 48, 64, 80]:
        bt = bud[str(m)]['sign_bot']['mean'] - bud[str(m)]['sign_top']['mean']
        dm = bud[str(m)]['delta_matched_pp']
        row.append('OK' if (bt > 0) == (dm > 0) else 'MISMATCH')
    print(f'  {b:9s} ' + ' '.join(f'{x:>10s}' for x in row))
print('  (aligned means sign(bot-top) == sign(Delta) AT THE SAME m)')

print('\n=== FINDING E: PerLTQA extrapolation across fitting windows ===')
bud = R['PerLTQA']['budgets']
print(f'  {"window":>14s} {"slope pp/axis":>14s} {"implied m*":>12s}')
for lo in [8, 24, 48, 64, 80]:
    xs = np.array([m for m in MS if m >= lo], float)
    ys = np.array([bud[str(int(m))]['delta_matched_pp'] for m in xs])
    if len(xs) < 2:
        continue
    A = np.polyfit(xs, ys, 1)
    mstar = -A[1] / A[0] if A[0] > 0 else float('inf')
    print(f'  {f"{lo}..96":>14s} {A[0]:>+14.5f} {mstar:>12.0f}')
d = [bud[str(m)]['delta_matched_pp'] for m in MS]
diffs = np.diff(d) / np.diff(MS)
print(f'  per-axis slope by segment: ' + ' '.join(f'{x:+.4f}' for x in diffs))
print('  -> slope is NOT constant (concave); a linear crossover estimate is unidentified.')

print('\n=== FINDING F: overlap-free exclusive contrast (audit says effect is REAL) ===')
print('  At m=48 TOP and BOT are disjoint by construction, so m=48 is the clean test.')
print(f'  {"bench":9s} {"sign_bot-top@48":>16s} {"float_bot-top@48":>17s} {"Delta@48":>10s}')
for b in BEN:
    bud = R[b]['budgets']
    s = 100 * (bud['48']['sign_bot']['mean'] - bud['48']['sign_top']['mean'])
    f = 100 * (bud['48']['float_bot']['mean'] - bud['48']['float_top']['mean'])
    print(f'  {b:9s} {s:>+16.4f} {f:>+17.4f} {bud["48"]["delta_matched_pp"]:>+10.4f}')

print('\n=== FINDING G: random-m vs bot-m (does a low-variance RULE survive?) ===')
for b in BEN:
    bud = R[b]['budgets']
    for m in [48]:
        r = bud[str(m)]['sign_rand']['mean']; bo = bud[str(m)]['sign_bot']['mean']
        t = bud[str(m)]['sign_top']['mean']
        best = max([('top', t), ('rand', r), ('bot', bo)], key=lambda x: x[1])[0]
        print(f'  {b:9s} m={m} top={t:.6f} rand={r:.6f} bot={bo:.6f}  BEST={best}')
print('  If rand beats bot anywhere, "pick low-variance axes" is not a usable rule.')
