"""Sequential, accepted-environment synthetic replay; create-only evidence folder."""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXPECTED = {'cloudpickle': '3.1.2', 'joblib': '1.6.0', 'numpy': '2.3.5',
            'pandas': '2.2.3', 'python-dateutil': '2.9.0.post0', 'pytz': '2026.3.post1',
            'scikit-learn': '1.8.0', 'scipy': '1.17.0', 'six': '1.17.0',
            'threadpoolctl': '3.6.0', 'tzdata': '2026.3'}


def main():
    if sys.version_info[:3] != (3, 13, 15):
        raise SystemExit('interpreter mismatch')
    actual = {name: importlib.metadata.version(name) for name in EXPECTED}
    if actual != EXPECTED:
        raise SystemExit('dependency freeze mismatch')
    destination = Path(sys.argv[1])
    destination.mkdir(exist_ok=False)
    env = dict(os.environ, PYTHONHASHSEED='0', PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')
    for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        env[name] = '1'
    suites = [HERE / 'test_audit_regressions.py', HERE / 'test_integration.py',
              HERE.parent / 'membership_source_contracts_v1_2026_09_08/test_contracts.py',
              HERE.parent / 'membership_impl_v3_2026_09_07/test_membership_scaling_core.py']
    outputs = []
    for index, suite in enumerate(suites):
        result = subprocess.run([sys.executable, '-B', str(suite)], cwd=ROOT,
                                env=env, capture_output=True)
        stem = str(index) + '_' + suite.stem
        (destination / (stem + '.stdout.txt')).write_bytes(result.stdout)
        (destination / (stem + '.stderr.txt')).write_bytes(result.stderr)
        match = re.search(rb'Ran (\d+) tests?', result.stderr)
        outputs.append({'suite': str(suite.relative_to(ROOT)), 'exit_code': result.returncode,
                        'unittest_methods': int(match[1]) if match else None})
    record = {'status': 'IMPLEMENTATION_TEAM_SYNTHETIC_REPLAY', 'python': sys.version,
              'packages': actual, 'suites': outputs,
              'real_corpus_access': False, 'historical_outcomes_access': False,
              'source_sha256_on_disk': {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                                        for path in HERE.glob('*.py')}}
    (destination / 'REPLAY.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(outputs, indent=2))
    raise SystemExit(0 if all(row['exit_code'] == 0 for row in outputs) else 1)


if __name__ == '__main__':
    main()
