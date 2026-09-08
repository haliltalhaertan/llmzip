"""Replay preparation tests in the accepted interpreter; create-only evidence directory."""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
EXPECTED = {'numpy': '2.3.5', 'scipy': '1.17.0', 'scikit-learn': '1.8.0', 'pandas': '2.2.3'}

def main():
    if sys.version_info[:3] != (3, 13, 15):
        raise SystemExit('interpreter mismatch')
    actual = {k: importlib.metadata.version(k) for k in EXPECTED}
    if actual != EXPECTED:
        raise SystemExit('dependency mismatch')
    out = Path(sys.argv[1])
    out.mkdir(exist_ok=False)
    env = dict(os.environ, PYTHONHASHSEED='0', PYTHONDONTWRITEBYTECODE='1')
    for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        env[k] = '1'
    result = subprocess.run([sys.executable, '-B', str(HERE / 'test_pipeline.py')],
                            env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out / 'stdout.txt').write_bytes(result.stdout)
    (out / 'stderr.txt').write_bytes(result.stderr)
    record = {'exit_code': result.returncode, 'python': sys.version, 'packages': actual,
              'scope': 'implementation-team synthetic tests, NOT independent audit',
              'real_data_authorized': False,
              'sources': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in HERE.glob('*.py')}}
    (out / 'RESULTS.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'exit_code': result.returncode, 'test_methods': 7}))
    raise SystemExit(result.returncode)

if __name__ == '__main__':
    main()
