#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT][NOT PREREGISTERED][NOT FOR CITATION][DISCLOSE-BEFORE-USE]
STEP 7 (post-hoc DESCRIPTIVE, explicitly NOT a rescue of the frozen rule):
separate the LEVEL (intercept) from the SLOPE. If the slope is stable across benchmarks
while the intercept is not, the sign is set by a per-benchmark offset that the gap
cannot see -- that is the next decisive measurement target, not a working rule.
"""
import json, pickle, glob
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.stats import rankdata

ROOT = Path('/mnt/c/Users/MDP/dev/llmzip-work')
OUT = Path('/mnt/c/Users/MDP/dev/llmzip-work/agent_out/perltqa-levels')
S6 = json.load(open(OUT / 'evidence' / 'step6.json'))

def spearman(x, y):
    rx = rankdata(x); ry = rankdata(y); rx = rx - rx.mean(); ry = ry - ry.mean()
    return float((rx @ ry) / np.sqrt((rx @ rx) * (ry @ ry)))

print('=== SLOPE vs LEVEL separation (descriptive) ===')
print('rho(Delta, STRICT_GAP) per benchmark:  LME %.5f  RT %.5f  PerLTQA %.5f  -> all POSITIVE'
      % (S6['LongMemEval']['rho_delta_strictgap'], S6['REALTALK']['rho_delta_strictgap'], S6['PerLTQA']['rho_delta_strictgap']))
print('mean STRICT_GAP     per benchmark:  LME %+.3f  RT %+.3f  PerLTQA %+.3f'
      % (S6['LongMemEval']['strict_gap'], S6['REALTALK']['strict_gap'], S6['PerLTQA']['strict_gap']))
print('mean Delta_pp       per benchmark:  LME %+.3f  RT %+.3f  PerLTQA %+.3f'
      % (S6['LongMemEval']['delta_pp'], S6['REALTALK']['delta_pp'], S6['PerLTQA']['delta_pp']))
print('=> LME and PerLTQA have gaps of the SAME sign (both negative) but Deltas of OPPOSITE sign.')
print('   The level therefore CANNOT set the sign. rank-corr of (bench mean gap, bench mean Delta) over 3 points:',
      spearman([S6[b]['strict_gap'] for b in ('LongMemEval', 'REALTALK', 'PerLTQA')],
               [S6[b]['delta_pp'] for b in ('LongMemEval', 'REALTALK', 'PerLTQA')]))

cr = S6['cross_rho']
print('\n=== cross-benchmark sign-consistency of per-query rho(Delta, X)  [LME, RT, PerLTQA] ===')
for k, v in sorted(cr.items(), key=lambda kv: -min(abs(x) for x in kv[1])):
    cons = all(x > 0 for x in v) or all(x < 0 for x in v)
    print(f'  {k:16s} {v[0]:+9.5f} {v[1]:+9.5f} {v[2]:+9.5f}   min|rho| {min(abs(x) for x in v):.5f}  {"CONSISTENT" if cons else "flips"}')
print('\n  strict_BOT64 is the most stable: rho ~ -0.18 in every benchmark, tighter than STRICT_GAP itself.')

# stratum test using BENCHMARK-CENTERED gap (descriptive only; needs Delta-free info it does not have)
print('\n=== descriptive: stratum accuracy if the gap is centered within its own benchmark ===')
print('   (NOT a deployable rule: centering requires knowing the benchmark offset, which is')
print('    exactly the unknown quantity. Recorded to locate the next measurement, not to rescue.)')
rows = S6['levels_rule_strata']['rows']
byb = defaultdict(list)
for r in rows: byb[r['stratum'].split('/')[0]].append(r)
nok = 0; tot = 0; npos = 0
for b, rs in byb.items():
    m = float(np.mean([r['strict_gap'] for r in rs]))
    for r in rs:
        p = '+' if (r['strict_gap'] - m) > 0 else '-'
        nok += (p == r['obs']); tot += 1; npos += (r['obs'] == '+')
maj = max(npos, tot - npos)
print(f'   centered-gap stratum accuracy {nok}/{tot} = {nok/tot:.3f} vs majority {maj}/{tot} = {maj/tot:.3f}'
      f' => {"beats" if nok>maj else "still does not beat"}')
json.dump({'centered_acc': nok / tot, 'centered_n': tot, 'majority': maj / tot},
          open(OUT / 'evidence' / 'step7.json', 'w'), indent=2)
print('\nwrote evidence/step7.json')
