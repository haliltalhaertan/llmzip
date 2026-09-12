"""Locked, fresh-process synthetic verification with observed unittest counts.

python -B verify_delivery.py --output evidence/<fresh-directory>
This is implementation evidence, never independent acceptance or a pre-run seal.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
LOCK = {'python': '3.13.15', 'numpy': '2.3.5', 'scipy': '1.17.0',
        'scikit-learn': '1.8.0', 'pandas': '2.2.3'}
MODULES = ['test_certificate', 'test_delivery_g2', 'test_delivery_pipeline', 'test_delivery_integration']
THREADS = ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'OMP_THREAD_LIMIT', 'BLIS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def runtime():
    actual = {'python': platform.python_version()}
    actual.update({k: importlib.metadata.version(k) for k in LOCK if k != 'python'})
    if actual != LOCK:
        raise RuntimeError('G3 exact runtime mismatch')
    return actual


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entries = []
        self.subtests_observed = 0
    def addSuccess(self, test):
        super().addSuccess(test)
        self.entries.append({'test': test.id(), 'status': 'PASS'})
    def addFailure(self, test, error):
        super().addFailure(test, error)
        self.entries.append({'test': test.id(), 'status': 'FAIL'})
    def addError(self, test, error):
        super().addError(test, error)
        self.entries.append({'test': test.id(), 'status': 'ERROR'})
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.entries.append({'test': test.id(), 'status': 'SKIP', 'reason': reason})
    def addSubTest(self, test, subtest, error):
        self.subtests_observed += 1
        super().addSubTest(test, subtest, error)


def child(out):
    actual = runtime()
    source_hashes = {p.relative_to(HERE).as_posix(): sha(p.read_bytes())
                     for folder in (HERE, HERE / 'authoritative') for p in sorted(folder.glob('*.py'))}
    data_events = {'allowed_synthetic': 0, 'denied': 0}
    def guard(event, args):
        if event in ('socket.connect', 'socket.getaddrinfo'):
            data_events['denied'] += 1
            raise RuntimeError('G3 network forbidden')
        if event not in ('open', 'os.scandir', 'os.listdir') or not args:
            return
        path = args[0]
        if not isinstance(path, (str, bytes, os.PathLike)):
            return
        p = Path(os.fsdecode(path)).absolute()
        lower = {part.lower() for part in p.parts}
        relevant = p.suffix.lower() in ('.json', '.jsonl', '.csv', '.gz', '.parquet')
        relevant = relevant or bool(lower & {'beam', 'dataset', 'datasets'})
        if not relevant:
            return
        if p.name == 'direct_url.json' and any(part.endswith('.dist-info') for part in p.parts):
            return
        if HERE == p or HERE in p.parents:
            data_events['allowed_synthetic'] += 1
            return
        data_events['denied'] += 1
        raise RuntimeError('G3 external data access forbidden')
    sys.addaudithook(guard)
    suite = unittest.defaultTestLoader.loadTestsFromNames(MODULES)
    result = unittest.TextTestRunner(verbosity=2, resultclass=RecordedResult).run(suite)
    success = result.wasSuccessful() and result.testsRun > 0 and not result.skipped
    report = {'status': 'PASS' if success else 'FAIL',
              'evidence_kind': 'implementation-team synthetic verification; independent audit pending',
              'runtime': actual, 'executable': sys.executable,
              'thread_environment': {k: os.environ.get(k) for k in THREADS + ('PYTHONHASHSEED',)},
              'test_methods_observed': result.testsRun, 'subtests_observed': result.subtests_observed,
              'failures': len(result.failures), 'errors': len(result.errors), 'skips': len(result.skipped),
              'tests': result.entries, 'source_sha256': source_hashes, 'data_events': data_events,
              'scope': {'experiment': False, 'corpus_access': False, 'frozen_outcome_replay': False,
                        'finalize': False, 'HMAC': False, 'seal': False, 'production_authorization': False}}
    (out / 'RESULTS.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return 0 if success else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--child', action='store_true')
    args = parser.parse_args()
    out = Path(args.output)
    out = (HERE / out).resolve() if not out.is_absolute() else out.resolve()
    if HERE not in out.parents:
        raise RuntimeError('evidence must remain inside this namespace')
    if args.child:
        return child(out)
    runtime()
    out.mkdir(parents=True, exist_ok=False)
    temp = out / 'tmp'; temp.mkdir()
    env = dict(os.environ, PYTHONHASHSEED='0', PYTHONDONTWRITEBYTECODE='1',
               TMP=str(temp), TEMP=str(temp), TMPDIR=str(temp), **{k: '1' for k in THREADS})
    command = [sys.executable, '-B', str(Path(__file__).resolve()), '--child', '--output', str(out)]
    completed = subprocess.run(command, cwd=HERE, env=env, capture_output=True)
    (out / 'stdout.txt').write_bytes(completed.stdout)
    (out / 'stderr.txt').write_bytes(completed.stderr)
    (out / 'COMMAND.json').write_text(json.dumps({'argv': command, 'exit_code': completed.returncode}, indent=2) + '\n')
    print('G3 verification exit', completed.returncode, 'evidence', out)
    return completed.returncode


if __name__ == '__main__':
    raise SystemExit(main())
