"""Fresh-process historical and G3 synthetic regressions, with attributable routing.

Usage: pinned python -B run_inherited.py --evidence-dir inherited/<fresh-name>
Only source suites are run. Historical assertions are never edited or skipped.
The G3 pipeline's old certificate-contract errors are reported separately and
still make this command fail; Decision 2 coverage belongs to the lead's suite.
"""
from __future__ import annotations

import argparse
import ast
import difflib
import functools
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys
import tempfile
import time
import traceback
import unittest

import verify_provenance as P


def adapt(source, destination, replacements, ledger):
    before = source.read_bytes()
    text = before.decode('utf-8')
    applied = []
    for old, new, count in replacements:
        if text.count(old) != count:
            raise RuntimeError('adaptation precondition failed: ' + str(source) + ': ' + old)
        text = text.replace(old, new)
        applied.append(dict(old=old, new=new, occurrences=count))
    after = text.encode('utf-8')
    ast.parse(after) if destination.suffix == '.py' else None
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(after)
    ledger.append(dict(source=str(source.relative_to(P.NS)), destination=str(destination.relative_to(P.NS)),
                       source_sha256=P.sha(before), adapted_sha256=P.sha(after), substitutions=applied,
                       diff=''.join(difflib.unified_diff(before.decode().splitlines(True), text.splitlines(True),
                                                       fromfile=str(source), tofile=str(destination)))))


def layout(out):
    """Snapshot exact current sources and route inherited imports to that snapshot."""
    ledger = []
    base = out / 'g3'
    recovery = json.loads((P.NS / 'RECOVERY_INPUT.json').read_bytes())
    current = {}
    for e in recovery['files']:
        rel = str(P.safe_relative(e['path']))
        if not rel.endswith('.py'):
            raise RuntimeError('non-source in recovery source list')
        if Path(rel).name.startswith('test_'):
            continue  # Lead tests and the recovery test are not inherited inputs.
        current[rel] = (P.NS / rel).read_bytes()
    # Follow newly added local source imports (e.g. the lead's record boundary).
    # This never copies data, installed packages, or unrelated root scripts.
    pending = list(current)
    while pending:
        rel = pending.pop()
        for node in ast.walk(ast.parse(current[rel])):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else (
                [node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
            for name in names:
                dep = name.replace('.', '/') + '.py'
                source = P.NS / dep
                if dep not in current and source.is_file():
                    current[dep] = source.read_bytes()
                    pending.append(dep)
    candidate = base / P.PACKAGES['v5']
    for rel, data in current.items():
        dest = candidate / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        ledger.append(dict(source=rel, destination=str(dest.relative_to(P.NS)), source_sha256=P.sha(data),
                           adapted_sha256=P.sha(data), substitutions=[]))
    for key in ('core', 'v3', 'v4', 'prep'):
        for source in sorted((P.SOURCES / P.PACKAGES[key]).rglob('*')):
            if source.is_file():
                adapt(source, base / source.relative_to(P.SOURCES), [], ledger)
    core_dest = base / P.PACKAGES['core'] / 'membership_scaling_core.py'
    if core_dest.read_bytes() != current['membership_scaling_core.py']:
        raise RuntimeError('G3 core differs from raw pinned core')
    src = P.SOURCES / P.PACKAGES['v5']
    adapt(src / 'test_runner_ingest_v4.py', candidate / 'test_runner_ingest_v4.py', [
        ('import membership_runner_v4 as R4', 'import membership_runner_g3 as R4', 1),
        ('import corpus_ingest_v4 as I4', 'import corpus_ingest_g3 as I4', 1),
        ('"membership_runner_v4.py"', '"membership_runner_g3.py"', 1),
        ('"corpus_ingest_v4.py"', '"corpus_ingest_g3.py"', 1),
    ], ledger)
    # OLD retains the original v4 modules and its original assertions.
    adapt(src / 'test_codex_v5.py', candidate / 'test_codex_v5.py', [
        ('import membership_runner_v4 as R\nimport corpus_ingest_v4 as I',
         'if OLD:\n    import membership_runner_v4 as R\n    import corpus_ingest_v4 as I\nelse:\n    import membership_runner_g3 as R\n    import corpus_ingest_g3 as I', 1),
    ], ledger)
    prep = base / P.PACKAGES['prep']
    # G3 pipeline imports can grow during lead remediation. Preserve the exact
    # same local module graph as the candidate snapshot without altering code.
    for rel in current:
        if rel.startswith('test_'):
            continue
        (prep / rel).parent.mkdir(parents=True, exist_ok=True)
        (prep / rel).write_bytes(current[rel])
        ledger.append(dict(source=rel, destination=str((prep / rel).relative_to(P.NS)),
                           source_sha256=P.sha(current[rel]), adapted_sha256=P.sha(current[rel]), substitutions=[]))
    adapt(P.SOURCES / P.PACKAGES['prep'] / 'test_pipeline.py', prep / 'test_pipeline.py', [
        ('import pipeline as p', 'import pipeline_g3 as p', 1),
    ], ledger)
    P.write_json(out / 'ADAPTATIONS.json', ledger)
    (out / 'ADAPTATIONS.diff').write_text('\n'.join(x.get('diff', '') for x in ledger), encoding='utf-8')
    P.write_json(out / 'CURRENT_SOURCE_SNAPSHOT.json', {k: P.sha(v) for k, v in current.items()})
    return base, current


def child(suite, temporary, report, old_control=False):
    """Observe Python I/O, check calls and unittest outcomes without changing tests."""
    P.runtime()
    suite, temporary, report = Path(suite).resolve(), Path(temporary).resolve(), Path(report).resolve()
    if not all(any(root.resolve() in p.parents for root in (P.NS / 'inherited', P.NS / 'provenance'))
               for p in (suite, temporary, report)):
        raise RuntimeError('child paths outside owned evidence trees')
    tempfile.tempdir = str(temporary)
    os.environ.update(TMP=str(temporary), TEMP=str(temporary), TMPDIR=str(temporary))
    os.chdir(temporary)
    # The launcher lives beside live G3 modules; do not let its script directory
    # accidentally satisfy a missing snapshot dependency.
    sys.path[:] = [p for p in sys.path if Path(p or os.curdir).resolve() != P.NS]
    sys.path.insert(0, str(suite.parent))
    sys.argv = [str(suite)] + (['--old-control'] if old_control else [])
    observations, calls, outcomes = [], [], []
    assertion_calls = 0
    tests_run = 0
    subprocess_routing = []

    original_popen = subprocess.Popen

    class SourcePopen(original_popen):
        def __init__(self, argv, *args, **kwargs):
            if argv == ['git', 'show', P.ARITH + ':' + P.ARITH_PATH]:
                # Git for Windows otherwise stats a >260-character revision/path
                # relative to the deep fixture cwd. This is cwd-only routing.
                kwargs['cwd'] = str(P.REPO)
                subprocess_routing.append(dict(argv=argv, cwd=str(P.REPO), reason='raw arithmetic Git path resolution'))
            super().__init__(argv, *args, **kwargs)

    subprocess.Popen = SourcePopen

    def guard(event, args):
        if event in ('socket.connect', 'socket.getaddrinfo', 'os.system'):
            observations.append(dict(event=event, allowed=False))
            raise PermissionError('inherited suite network/shell forbidden')
        if event == 'subprocess.Popen':
            argv = args[1]
            commands = [['git', 'show', P.ARITH + ':' + P.ARITH_PATH],
                        [str(P.PYTHON), '-B', str(suite), '--old-control'],
                        [sys.executable, '-B', str(suite), '--old-control']]
            # Windows audits the CreateProcess command line after list2cmdline.
            allowed = any(argv == subprocess.list2cmdline(command) if isinstance(argv, str)
                          else isinstance(argv, (tuple, list)) and list(argv) == command
                          for command in commands)
            observations.append(dict(event=event, allowed=allowed, argv=argv))
            if not allowed:
                raise PermissionError('inherited suite subprocess outside source-test allowlist')
        if event not in ('open', 'os.scandir', 'os.listdir', 'os.mkdir', 'os.remove', 'os.rmdir', 'os.rename') or not args:
            return
        if not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(args[0])).resolve()
        in_tmp = path == temporary or temporary in path.parents
        writing = event in ('os.mkdir', 'os.remove', 'os.rmdir', 'os.rename')
        if event == 'open':
            mode, flags = args[1:3]
            writing = bool((isinstance(mode, str) and any(c in mode for c in 'wax+'))
                           or (isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)))
        if writing:
            allowed = in_tmp or path == report
            if event == 'os.rename':
                target = Path(os.fsdecode(args[1])).resolve()
                allowed = allowed and (target == temporary or temporary in target.parents)
            observations.append(dict(event=event, write=True, allowed=allowed))
            if not allowed:
                raise PermissionError('inherited suite write outside synthetic temporary directory')
        data = path.suffix.lower() in {'.json', '.jsonl', '.csv', '.gz', '.parquet', '.npy', '.npz'}
        corpus_tree = any(p.lower() in {'beam', 'dataset', 'datasets', 'corpus'} for p in path.parts)
        metadata = path.name == 'direct_url.json' and '.dist-info' in str(path) and 'site-packages' in path.parts
        if data or corpus_tree:
            allowed = in_tmp or metadata
            observations.append(dict(event=event, data=True, allowed=allowed))
            if not allowed:
                raise PermissionError('inherited suite data outside synthetic temporary directory')

    def profile(frame, event, arg):
        nonlocal assertion_calls
        if event != 'return':
            return
        if frame.f_code.co_filename == str(suite) and frame.f_code.co_name == 'check':
            values = frame.f_locals
            cond = next((values[k] for k in ('condition', 'cond', 'ok') if k in values), False)
            label = values.get('label', values.get('name', 'unnamed'))
            calls.append(dict(label=str(label), passed=bool(cond)))
        if frame.f_code.co_name.startswith('assert') and frame.f_globals.get('__name__') == 'unittest.case':
            assertion_calls += 1

    class ObservedResult(unittest.TextTestResult):
        def stopTestRun(self):
            nonlocal tests_run
            tests_run = self.testsRun
            super().stopTestRun()

        def addSuccess(self, test):
            outcomes.append(dict(test=test.id(), status='PASS'))
            super().addSuccess(test)

        def addError(self, test, err):
            outcomes.append(dict(test=test.id(), status='ERROR', type=err[0].__name__, message=str(err[1])))
            super().addError(test, err)

        def addFailure(self, test, err):
            outcomes.append(dict(test=test.id(), status='FAIL', type=err[0].__name__, message=str(err[1])))
            super().addFailure(test, err)

        def addSkip(self, test, reason):
            outcomes.append(dict(test=test.id(), status='SKIP', message=reason))
            super().addSkip(test, reason)

    unittest.TextTestRunner.resultclass = ObservedResult
    # Count unittest assertions at their boundary, without profiling numerical
    # libraries or the exact-Fraction oracle millions of times.
    def observe_assertion(original):
        @functools.wraps(original)
        def counted(*args, **kwargs):
            nonlocal assertion_calls
            assertion_calls += 1
            return original(*args, **kwargs)
        return counted

    for name in dir(unittest.TestCase):
        if name.startswith('assert') and callable(getattr(unittest.TestCase, name)):
            setattr(unittest.TestCase, name, observe_assertion(getattr(unittest.TestCase, name)))
    sys.addaudithook(guard)
    if suite.name != 'test_pipeline.py':
        sys.setprofile(profile)
    code = 0
    try:
        runpy.run_path(str(suite), run_name='__main__')
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else (1 if exc.code else 0)
    except BaseException:
        traceback.print_exc()
        code = 1
    finally:
        sys.setprofile(None)
        if any(not x['allowed'] for x in observations) or any(not x['passed'] for x in calls):
            code = 1
        modules = {}
        unexpected_modules = []
        for name, module in list(sys.modules.items()):
            filename = getattr(module, '__file__', None)
            if filename and Path(filename).suffix == '.py' and P.NS in Path(filename).resolve().parents:
                path = Path(filename).resolve()
                modules[name] = dict(path=str(path), sha256=P.sha(path.read_bytes()))
                if (path not in (Path(__file__).resolve(), Path(P.__file__).resolve())
                        and suite.parent.parent not in path.parents):
                    unexpected_modules.append(dict(module=name, path=str(path)))
        if unexpected_modules:
            code = 1
        # .txt is deliberate: the historical prep guard refuses every .json open.
        P.write_json(report, dict(exit_code=code, check_count=len(calls), checks=calls,
                                 unittest_tests_run=tests_run, unittest_assertion_calls=assertion_calls,
                                 unittest_outcomes=outcomes, io_events=observations, modules=modules,
                                 subprocess_path_routing=subprocess_routing,
                                 unexpected_source_modules=unexpected_modules,
                                 python=sys.executable, environment={k: os.environ.get(k) for k in P.THREAD_ENV},
                                 scope='Python audit events only; native I/O not an OS sandbox. Nested old-control uses its own source guard.'))
    return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-dir')
    parser.add_argument('--suite-timeout', type=int, default=600,
                        help='seconds per fresh suite subprocess (default: 600)')
    parser.add_argument('--child', nargs=3, metavar=('SUITE', 'TMP', 'REPORT'))
    parser.add_argument('--old-control', action='store_true')
    args = parser.parse_args()
    if args.child:
        return child(*args.child, old_control=args.old_control)
    if not args.evidence_dir:
        parser.error('--evidence-dir required')
    if args.suite_timeout <= 0:
        parser.error('--suite-timeout must be positive')
    P.runtime()
    script_hashes = {str(path): P.sha(path.read_bytes()) for path in (Path(__file__).resolve(), Path(P.__file__).resolve())}
    out = P.fresh_dir(args.evidence_dir)
    temporary = out / 'tmp'
    temporary.mkdir()
    os.environ.update(TMP=str(temporary), TEMP=str(temporary), TMPDIR=str(temporary))
    provenance = out / 'provenance'
    provenance.mkdir()
    verified = P.verify(provenance)
    if verified['failed']:
        raise RuntimeError('raw provenance failed; tests refused')
    g3, current = layout(out)
    suites = []
    for mode, root in [('historical', P.SOURCES), ('g3', g3)]:
        for key, filename, flags in [
            ('core', 'test_membership_scaling_core.py', []),
            ('v5', 'test_runner_ingest_v4.py', []),
            ('v5', 'test_codex_v5.py', []),
            ('v5', 'test_codex_v5.py', ['--old-control']),
            ('prep', 'test_pipeline.py', []),
        ]:
            name = mode + '_' + filename.removesuffix('.py') + ('_old_control' if flags else '')
            suites.append((name, root / P.PACKAGES[key] / filename, flags))
    results = []
    for name, suite, flags in suites:
        print('RUN ' + name, flush=True)
        tmp = temporary / name
        tmp.mkdir()
        report = out / (name + '.metrics.txt')
        command = [str(P.PYTHON), '-B', str(Path(__file__).resolve()), '--child', str(suite), str(tmp), str(report), *flags]
        started = time.monotonic()
        try:
            completed = subprocess.run(command, cwd=tmp, env=os.environ.copy(), capture_output=True, timeout=args.suite_timeout)
            stdout, stderr, code = completed.stdout, completed.stderr, completed.returncode
        except subprocess.TimeoutExpired as exc:
            stdout, stderr, code = exc.stdout or b'', exc.stderr or b'', 124
        (out / (name + '.stdout.txt')).write_bytes(stdout)
        (out / (name + '.stderr.txt')).write_bytes(stderr)
        metrics = json.loads(report.read_bytes()) if report.exists() else {}
        row = dict(suite=name, command=command, source_sha256=P.sha(suite.read_bytes()), exit_code=code,
                   timeout_seconds=args.suite_timeout, timed_out=code == 124,
                   seconds=time.monotonic() - started, metrics=metrics,
                   printed_ok_count=len(re.findall(rb'^ok\s', stdout, re.MULTILINE)))
        if not metrics or not (metrics.get('check_count') or metrics.get('unittest_tests_run')):
            row['exit_code'] = row['exit_code'] or 1
            row['harness_error'] = 'missing metrics or no checks executed'
        # Classification is additive; no xfail, skip, assertion rewrite or green override.
        row['certificate_contract_incompatibilities'] = [x for x in metrics.get('unittest_outcomes', [])
            if name == 'g3_test_pipeline' and x['status'] == 'ERROR' and x.get('type') == 'PipelineError'
            and 'E-M-031' in x.get('message', '')]
        results.append(row)
        P.write_json(out / 'RESULTS.json', dict(complete=False, suites=results))
        print(f"DONE {name}: exit={row['exit_code']} checks={metrics.get('check_count', 0)} tests={metrics.get('unittest_tests_run', 0)}", flush=True)
    changed = [k for k, b in current.items() if (P.NS / k).read_bytes() != b]
    final = dict(complete=True, suites=results, failed_suites=sum(x['exit_code'] != 0 for x in results),
                 current_sources_changed_during_run=changed, runner_sha256=P.sha(Path(__file__).read_bytes()),
                 scripts_at_start=script_hashes,
                 scripts_changed_during_run=[path for path, digest in script_hashes.items() if P.sha(Path(path).read_bytes()) != digest],
                 decision2_note='Old certificate incompatibilities remain failures; lead supplies new Decision 2 coverage.',
                 scope='Synthetic source tests only. No validate_candidate, replay, corpus or historical results executed.')
    P.write_json(out / 'RESULTS.json', final)
    print(f"INHERITED: {len(results)} suites; {final['failed_suites']} failed; source drift={len(changed)}")
    return int(bool(final['failed_suites'] or changed or final['scripts_changed_during_run']))


if __name__ == '__main__':
    raise SystemExit(main())
