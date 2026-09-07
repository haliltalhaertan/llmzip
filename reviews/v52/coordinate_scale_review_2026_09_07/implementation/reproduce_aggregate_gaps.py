"""Synthetic only: no raw corpus, retrieval run, source edits or output writes.

Run with python -B from anywhere. Imports only the reviewed module's inert top level.
Prints validation gaps; does not import its frozen research base.
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location('audit_pure', ROOT / 'research/v52/longmemeval_coordinate_scale_shard.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

def fresh():
    values = dict(NATIVE=.6, SCALED_NATIVE=.6, FULLHAAR_FRESH=.2,
                  SCALED_FULLHAAR=.5, BLOCK32_FRESH=.4, SCALED_BLOCK32=.45)
    return [dict(qid=f'q{i}', lex=i, native=.6, max_norm=0., max_dot=0.,
                 diagnostics={'flagged': False},
                 rows=[dict(arm=a, rotation_seed=s, fractional_R3=values[a])
                       for s in r.ROTATION_SEEDS for a in r.ARMS]) for i in range(4)]

for label in ['nan_invariance', 'out_of_range_metric', 'paired_native_tamper', 'false_native_rows']:
    z = fresh()
    if label == 'nan_invariance':
        z[0]['max_dot'] = float('nan')
    if label == 'out_of_range_metric':
        for row in z[0]['rows']:
            if row['arm'] == 'SCALED_FULLHAAR':
                row['fractional_R3'] = 10.
    if label == 'paired_native_tamper':
        for i, offset in [(0, .1), (1, -.1)]:
            for row in z[i]['rows']:
                if row['arm'] == 'SCALED_NATIVE':
                    row['fractional_R3'] += offset
    if label == 'false_native_rows':
        for result in z:
            for row in result['rows']:
                if row['arm'] in ['NATIVE', 'SCALED_NATIVE']:
                    row['fractional_R3'] = .8
    try:
        _, summary = r.summarize(z, .6, 4)
        print(label, 'ACCEPTED', 'control_native=', summary['controls']['native_reproduction'],
              'primary_native=', summary['primary']['arm_means']['NATIVE'],
              'frac_full=', summary['primary']['frac_full'])
    except Exception as exc:
        print(label, 'REJECTED', str(exc))
