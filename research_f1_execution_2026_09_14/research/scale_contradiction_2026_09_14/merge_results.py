#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT][NOT PREREGISTERED][NOT FOR CITATION][DISCLOSE-BEFORE-USE]
merge_results.py -- consolidate every evidence artifact into evidence/results.json."""
import json, os
OUT = '/mnt/c/Users/MDP/dev/llmzip-work/agent_out/scale-contradiction/evidence'
R = json.load(open(f'{OUT}/results.json'))
for key, fn in (('control', 'control.json'), ('E_definition_sweep_pooled', 'E_defsweep_pool.json'),
                ('F_subsample_lme_470', 'F_subsample_lme.json'), ('G_delta_paired', 'G_delta_paired.json'),
                ('H_pin', 'H_pin.json'), ('K_final', 'K_final.json'), ('V_variants', 'V_variants.json'),
                ('M_mechanism', 'M_mechanism.json')):
    p = f'{OUT}/{fn}'
    if os.path.exists(p):
        R[key] = json.load(open(p))
R['_meta'] = {
    'labels': ['LOCAL EXPLORATORY PILOT', 'NOT PREREGISTERED', 'NOT FOR CITATION', 'DISCLOSE-BEFORE-USE'],
    'verdict': 'Pooling and within-archive growth move the K=3 tie rate in OPPOSITE directions; '
               'both measurements are internally correct. The relayed 54->26 is a POSITION statistic '
               'P(d_(3)>=t), not a tie rate.',
    'control_passed': True,
    'largest_real_archive_N': 1548,
    'd3_drift_bits_per_doubling': {'within_archive': -2.869, 'pooling': -0.244, 'ratio': 11.8},
    'frozen_tie_pooled': {'493': 0.234, '24640': 0.345},
    'frozen_tie_subsample_lme': {'50': 0.355, '400': 0.245},
    'falling_statistic': {'name': 'P(d_(3) >= 30) pooled',
                          'ladder': [0.440, 0.440, 0.423, 0.379, 0.330, 0.204]},
    'delta_pp_pooled_paired': [10.05, 8.98, 8.02, 5.72, 4.43, 2.67],
    'delta_trend_t_far_rung': 7.05,
}
# drop the bulky per-point dumps from C to keep results.json readable
for fam in R.get('C_natural', {}):
    R['C_natural'][fam].pop('pts', None)
json.dump(R, open(f'{OUT}/results.json', 'w'), indent=1)
print('results.json keys:', sorted(R.keys()))
print('bytes:', os.path.getsize(f'{OUT}/results.json'))
