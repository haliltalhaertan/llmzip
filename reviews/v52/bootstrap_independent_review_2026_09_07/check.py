"""Independent persisted-output check; stdlib only; no producer imports or resampling."""
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / 'reviews/v52/coordinate_scale_uncertainty_2026_09_07'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def close(a, b):
    assert math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12), (a, b)

def q(values, p):
    ordered = sorted(values)
    position = (len(ordered) - 1) * p
    lo, hi = math.floor(position), math.ceil(position)
    return ordered[lo] * (hi - position) + ordered[hi] * (position - lo) if lo != hi else ordered[lo]

def main():
    manifest = json.loads((SOURCE / 'ANALYSIS_HASHES.json').read_text())
    results = json.loads((SOURCE / 'outputs/RESULTS.json').read_text())
    checked = []
    for entry in manifest['files']:
        path = ROOT / entry['path']
        assert path.stat().st_size == entry['bytes']
        assert digest(path) == entry['sha256']
        checked.append(entry['path'])
    checkpoint = results['precomputation_commit']
    assert checkpoint == manifest['precomputation_commit']
    subprocess.run(['git', 'merge-base', '--is-ancestor', checkpoint, 'HEAD'], cwd=ROOT, check=True)
    tree = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', checkpoint, str(SOURCE.relative_to(ROOT)).replace('\\', '/')], cwd=ROOT, text=True).splitlines()
    assert len(tree) == 3 and all(Path(p).name in ['bootstrap.py', 'ANALYSIS_PLAN.md', 'test_bootstrap.py'] for p in tree)
    for path in tree:
        blob = subprocess.check_output(['git', 'show', checkpoint + ':' + path], cwd=ROOT)
        assert blob == (ROOT / path).read_bytes()
    assert digest(SOURCE / 'bootstrap.py') == results['code_sha256']
    assert digest(SOURCE / 'ANALYSIS_PLAN.md') == results['plan_sha256']
    for name, expected in results['input_sha256'].items():
        assert digest(ROOT / f'research/v52/{name}_scale_outputs/{name}_scale_per_question.csv.gz') == expected
    output = {'checkpoint': checkpoint, 'manifest_files_checked': len(checked), 'input_hashes_checked': 2, 'schemes': {}}
    for name, scheme in results['schemes'].items():
        path = SOURCE / 'outputs' / (name + '.csv')
        assert digest(path) == scheme['replicates_csv_sha256']
        with path.open(newline='') as stream:
            rows = list(csv.DictReader(stream))
        total = len(rows)
        assert total == scheme['planned_replicates'] == results['replicates_per_scheme'] == 10000
        assert [int(row['replicate']) for row in rows] == list(range(1, total + 1))
        sizes = [int(row['n_questions']) for row in rows]
        assert [min(sizes), max(sizes)] == scheme['sample_size_range']
        if name.endswith('_question'):
            assert set(sizes) == {1535 if name.startswith('locomo') else 470}
        summary = {}
        for key, entry in scheme['statistics'].items():
            values = [float(row[key]) for row in rows if row[key]]
            assert all(math.isfinite(v) for v in values)
            assert len(values) == entry['finite'] and total-len(values) == entry['undefined']
            quantiles = [q(values, p) for p in [.025, .5, .975]]
            for actual, expected in zip(quantiles, entry['percentiles_2_5_50_97_5']):
                close(actual, expected)
            assert min(values) == entry['min'] and max(values) == entry['max']
            if key.endswith('_I'):
                close(sum(v > 0 for v in values)/total, entry['positive_fraction_of_all_replicates'])
            else:
                counts = {'little': sum(v <= .2 for v in values), 'partial': sum(.2 < v < .7 for v in values), 'most': sum(v >= .7 for v in values)}
                for band, count in counts.items():
                    close(count/total, entry['band_frequencies_of_all_replicates'][band])
                assert sum(counts.values()) + entry['undefined'] == total
            summary[key] = {'finite': len(values), 'quantiles': quantiles}
        for row in rows:
            for route in ['A', 'B']:
                full, block, interaction = [row[route+'_'+s] for s in ['full', 'block', 'I']]
                if not full or not block:
                    assert not interaction
                else:
                    close(float(full)-float(block), float(interaction))
        summary['independent_any_seed_nonpositive_counts'] = {}
        for arm, entry in scheme['denominators'].items():
            low = [float(row['den_'+arm+'_min']) for row in rows]
            high = [float(row['den_'+arm+'_max']) for row in rows]
            mean = [float(row['den_'+arm+'_mean']) for row in rows]
            assert all(a <= b <= c for a,b,c in zip(low,mean,high))
            assert sum(v < 0 for v in low) == entry['replicates_any_seed_negative']
            summary['independent_any_seed_nonpositive_counts'][arm] = sum(v <= 0 for v in low)
            assert sum(a < 0 < b for a,b in zip(low,high)) == entry['replicates_seed_signs_cross_zero']
            assert [min(low), max(high)] == entry['seed_denominator_range']
            assert sum(v < 0 for v in mean) == entry['aggregate_negative']
            assert sum(v == 0 for v in mean) == entry['aggregate_zero']
            assert sum(abs(v) <= 1e-12 for v in mean) == entry['aggregate_near_zero_1e_12']
            assert [min(mean), max(mean)] == entry['aggregate_range']
        output['schemes'][name] = summary
    assert q([0, 2], .25) == .5
    try:
        close(q([0, 2], .25), .75)
    except AssertionError:
        output['wrong_quantile_negative_control'] = 'rejected'
    else:
        raise AssertionError('negative control failed')
    text = json.dumps(output, indent=2) + '\n'
    (HERE / 'CHECK_RESULTS.json').write_text(text, encoding='utf-8', newline='\n')
    print('PASS: manifest, input hashes, checkpoint ancestry, 54 quantiles, frequencies, extrema, interactions, reconstructible denominator diagnostics')

if __name__ == '__main__':
    main()
