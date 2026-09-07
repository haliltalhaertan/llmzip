"""Stdlib-only, post-outcome validation of persisted metrics; not a retrieval audit."""
import argparse
import copy
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path

ARMS = ('NATIVE', 'SCALED_NATIVE', 'FULLHAAR_FRESH', 'SCALED_FULLHAAR',
        'BLOCK32_FRESH', 'SCALED_BLOCK32')
SEEDS = tuple(range(59001, 59011))
SPECS = {'locomo': ('LoCoMo', 1535, 0.23654714666441054),
         'longmemeval': ('LongMemEval', 470, 0.5419751773049646)}
TOL = 1e-12


def require(condition, gate):
    if not condition:
        raise ValueError(gate)


def finite_tree(value, path='summary'):
    if isinstance(value, float):
        require(math.isfinite(value), 'nonfinite:' + path)
    elif isinstance(value, dict):
        for key, item in value.items():
            finite_tree(item, path + '.' + key)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            finite_tree(item, path + '[' + str(i) + ']')


def validate(rows, summary, spec):
    dataset, n, frozen = spec
    finite_tree(summary)
    require(summary['benchmark'] == dataset, 'summary_dataset')
    require(summary['identity']['rotation_seeds'] == list(SEEDS), 'summary_seeds')
    require(set(summary['identity']['arms']) == set(ARMS) and
            len(summary['identity']['arms']) == len(ARMS), 'summary_arms')
    require(summary['identity'].get('valid_questions',
            summary['identity'].get('primary_questions')) == n, 'summary_questions')
    require(len(rows) == n * len(SEEDS) * len(ARMS), 'row_count')
    cells = {}
    scalar = {}
    ties = {}
    for row in rows:
        require(row['dataset'] == dataset, 'dataset')
        q, seed, arm = row['question_id'], int(row['rotation_seed']), row['arm']
        require(bool(q) and seed in SEEDS and arm in ARMS, 'cell_domain')
        key = (q, seed, arm)
        require(key not in cells, 'duplicate_cell')
        score, native = float(row['fractional_R3']), float(row['native_fractional_R3'])
        require(math.isfinite(score) and 0 <= score <= 1, 'score_finite_unit_interval')
        require(math.isfinite(native) and 0 <= native <= 1, 'native_scalar_finite_unit_interval')
        cells[key] = score
        require(q not in scalar or scalar[q] == native, 'native_scalar_repeat')
        scalar[q] = native
        require(q not in ties or ties[q] == row['tie_identity'], 'tie_identity_repeat')
        ties[q] = row['tie_identity']
    questions = sorted(scalar)
    require(len(questions) == n, 'question_count')
    for q in questions:
        for seed in SEEDS:
            for arm in ARMS:
                require((q, seed, arm) in cells, 'coverage')
            require(cells[q, seed, 'NATIVE'] == scalar[q], 'native_row_scalar')
            require(cells[q, seed, 'SCALED_NATIVE'] == cells[q, seed, 'NATIVE'],
                    'paired_native_scaled_native')
    native = math.fsum(scalar.values()) / n
    require(abs(native - frozen) <= TOL, 'frozen_native')
    for field in ('native_reproduction', 'frozen_native'):
        require(abs(summary['controls'][field] - native) <= TOL, 'summary_' + field)
    require(summary['controls']['per_question_actual_rows'] == len(rows) and
            summary['controls']['per_question_expected_rows'] == len(rows), 'summary_rows')
    means = {arm: math.fsum(cells[q, seed, arm] for q in questions for seed in SEEDS)
             / (n * len(SEEDS)) for arm in ARMS}
    require(set(summary['primary']['arm_means']) == set(ARMS), 'summary_mean_arms')
    for arm, mean in means.items():
        require(abs(summary['primary']['arm_means'][arm] - mean) <= TOL, 'summary_mean:' + arm)
    return {'status': 'PASS', 'rows': len(rows), 'questions': n, 'seeds': len(SEEDS),
            'arms': len(ARMS), 'native_recomputed': native, 'frozen_native': frozen,
            'arm_means_recomputed': means,
            'question_set_sha256': hashlib.sha256('\n'.join(questions).encode()).hexdigest()}


def negative_controls(rows, summary, spec):
    tests = {}
    def check(name, changed_rows, changed_summary=summary):
        try:
            validate(changed_rows, changed_summary, spec)
        except ValueError as exc:
            tests[name] = {'status': 'REJECTED', 'gate': str(exc)}
        else:
            raise AssertionError('negative control accepted: ' + name)
    def changed(index, field, value):
        result = list(rows)
        result[index] = dict(result[index], **{field: str(value)})
        return result
    check('NaN', changed(0, 'fractional_R3', 'nan'))
    check('above_one', changed(0, 'fractional_R3', 1.1))
    check('below_zero', changed(0, 'fractional_R3', -0.1))
    check('missing', rows[:-1])
    check('duplicate_replacing_cell', rows[:-1] + [rows[0]])
    index = next(i for i, row in enumerate(rows) if row['arm'] == 'SCALED_NATIVE')
    value = float(rows[index]['fractional_R3'])
    check('paired_native_tamper', changed(index, 'fractional_R3', 0.25 if value != 0.25 else 0.5))
    check('native_scalar_mismatch', changed(0, 'native_fractional_R3', 0.25))
    broken = copy.deepcopy(summary)
    broken['diagnostics']['cv_sigma_per_archive'][0]['cv_sigma_before'] = float('nan')
    check('summary_diagnostic_NaN', rows, broken)
    # Preserve aggregate native-scaled equality while breaking two paired values.
    candidates = [(i, float(r['fractional_R3'])) for i, r in enumerate(rows)
                  if r['arm'] == 'SCALED_NATIVE']
    plus = next(i for i, v in candidates if v <= 0.75)
    minus = next(i for i, v in candidates if v >= 0.25 and i != plus)
    broken_rows = changed(plus, 'fractional_R3', float(rows[plus]['fractional_R3']) + 0.25)
    broken_rows[minus] = dict(rows[minus], fractional_R3=str(float(rows[minus]['fractional_R3']) - 0.25))
    check('cancelling_paired_tamper', broken_rows)
    return tests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[4]
    report = {'scope': 'Persisted metric consistency only; no raw data, ranking, bit codes, or research imports.',
              'tolerance': TOL, 'inputs': {}, 'benchmarks': {}, 'negative_controls': {}}
    for name, spec in SPECS.items():
        folder = root / 'research' / 'v52' / (name + '_scale_outputs')
        csv_path = folder / (name + '_scale_per_question.csv.gz')
        summary_path = folder / (name + '_scale_summary.json')
        for path in (csv_path, summary_path):
            data = path.read_bytes()
            report['inputs'][path.relative_to(root).as_posix()] = {
                'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
        with gzip.open(csv_path, 'rt', newline='') as stream:
            rows = list(csv.DictReader(stream))
        summary = json.loads(summary_path.read_text(encoding='utf-8'))
        report['benchmarks'][name] = validate(rows, summary, spec)
        report['negative_controls'][name] = negative_controls(rows, summary, spec)
    report['validator_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n', encoding='utf-8', newline='\n')
    print('PASS: both persisted panels; 18 negative controls rejected')


if __name__ == '__main__':
    main()
