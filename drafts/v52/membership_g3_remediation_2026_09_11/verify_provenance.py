"""Raw Git provenance and source-only inheritance. No checkout, corpus, or execution.

Run with the pinned Python, -B, --evidence-dir provenance/<fresh-name>.
Recovery identity is checked against the preserved pre-edit bytes; current edits
are reported separately and are never silently treated as recovered originals.
"""
from __future__ import annotations

import argparse
import ast
import difflib
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys

NS = Path(__file__).resolve().parent
REPO = NS.parents[2]
PYTHON = REPO.parent / '.venvs/g3-lock-20260912/Scripts/python.exe'
V5 = '07ec929243068914676a0f30efd10c9f294c7e71'
PREP = 'ed4e22c520b7dc0ae2f43f915e0c621070c72a87'
CORE = 'dcb568d0a6c33154c1568500325ad457b4d6f455'
CORE_HASH = 'bc2282d3fccfe83c3e9fc36a59d7df8e4f748048ff94baebdfa4010584404e72'
ARITH = '692f599eedeb7e7a649443f24ff507e8c4d1c17d'
ARITH_PATH = 'research/v52/locomo_sign_mechanism_replication.py'
ARITH_HASH = 'a6ecee02e5d6a8735a922ec2d5f0a024b3c024e0cdf03b336e16e4357f20e74b'
DOCUMENTS = [
    ('grant', 'b6b06e0c7e51089aa402dcdbddf03f692d690948',
     'docs/v52/V52_G3_REMEDIATION_GRANT_HR_DECISION_2026-09-11.md',
     '533bf10ec66fa7ab225a60d43161e129791d0f168f7e0ab520ce0afc7f23548f'),
    ('decision', '8671128a13877c97754da182421ba615422dd2ec',
     'docs/v52/V52_OBLIGATION_1_AND_F3_N1_DECISION_2026-09-09.md',
     '03f5fe7d7ff838936bf8bc3bc4a406836613d611fefd94f79228cb8e2cbd4970'),
    ('prep_audit', '5126766cac9201bbede178ccb558efa428f9488c',
     'audit_v52_execution_prep_v1_review_2026_09_08/EXECUTION_PREP_V1_REVIEW.md',
     'aea5d05c220571076b7961afd07cd8356c93e989eb1416e873772349bd62b9bb'),
    ('v5_audit', '2cf602090a6c4c42dba44f66d95d8dfed0e0f2e8',
     'audit_v52_codex_v5_repair_review_2026_09_08/CODEX_V5_REVIEW.md',
     'fd10e53324787965e11155cb6cd31952496199f0e8250fe9416c996abf227cea'),
    ('delivery_base_ledger', '4f2429b257546d6899f3ed48f605cd18210aeae0',
     'docs/CONTINUITY_LEDGER.md',
     '3deef4740f0691d109960d659ec636f19ef58b81f04522fb5dabb5cba665180f'),
]
LOCK = {'numpy': '2.3.5', 'scipy': '1.17.0', 'scikit-learn': '1.8.0', 'pandas': '2.2.3'}
PACKAGES = {
    'core': 'membership_impl_v3_2026_09_07',
    'v3': 'membership_runner_ingest_v3_2026_09_08',
    'v4': 'membership_runner_ingest_v4_2026_09_08',
    'v5': 'membership_runner_ingest_codex_v5_2026_09_08',
    'prep': 'membership_execution_prep_v1_2026_09_08',
}
SOURCES = NS / 'inherited/sources'
THREAD_ENV = {key: '1' for key in (
    'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
    'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'BLIS_NUM_THREADS',
    'OMP_THREAD_LIMIT')}
THREAD_ENV.update(PYTHONHASHSEED='0', PYTHONDONTWRITEBYTECODE='1')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])


def raw(commit, path):
    return git('cat-file', 'blob', commit + ':' + path)


def safe_relative(value):
    p = PurePosixPath(value)
    if p.is_absolute() or '..' in p.parts or '\\' in value or ':' in value:
        raise ValueError('unsafe relative source path')
    return p


def fresh_dir(value):
    dest = Path(value)
    dest = (NS / dest).resolve() if not dest.is_absolute() else dest.resolve()
    if not any(root.resolve() in dest.parents for root in (NS / 'inherited', NS / 'provenance')):
        raise ValueError('evidence must be a fresh subdirectory under inherited/ or provenance/')
    dest.mkdir(parents=True, exist_ok=False)
    return dest


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def immutable(path, data):
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError('existing inherited source differs: ' + str(path))
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def runtime():
    if Path(sys.executable).resolve() != PYTHON.resolve():
        raise RuntimeError('use pinned Python: ' + str(PYTHON))
    if not sys.dont_write_bytecode or sys.flags.optimize:
        raise RuntimeError('require -B and assertions enabled (no -O)')
    if os.environ.get('PYTHONHASHSEED') != '0':
        raise RuntimeError('launch with PYTHONHASHSEED=0')
    os.environ.update(THREAD_ENV)
    if sys.version_info[:3] != (3, 13, 15):
        raise RuntimeError('require locked Python 3.13.15')
    installed = {name: metadata.version(name) for name in LOCK}
    if installed != LOCK:
        raise RuntimeError('installed package versions differ from accepted lock: ' + json.dumps(installed))


def verify(out):
    checks, blobs, materialized = [], [], []

    def check(label, passed, **details):
        checks.append(dict(label=label, passed=bool(passed), **details))
        print(('ok   ' if passed else 'FAIL ') + label, flush=True)

    head = git('rev-parse', 'HEAD').decode().strip()
    document_records = []
    for label, commit, path, expected in DOCUMENTS:
        data = raw(commit, path)
        check('document raw identity ' + label, sha(data) == expected)
        document_records.append(dict(label=label, commit=commit, path=path, expected_sha256=expected,
                                     sha256=sha(data), bytes=len(data),
                                     git_blob=git('rev-parse', commit + ':' + path).decode().strip()))
    write_json(out / 'SOURCE_DOCUMENTS.json', dict(documents=document_records,
        scope='Raw identity only. Audit prose is not executed or adopted as authorization; user-accepted decisions govern scope.'))
    head_ancestry = {}
    for short, full in [('07ec929', V5), ('ed4e22c', PREP), ('dcb568d', CORE)]:
        check('resolved pin ' + short, git('rev-parse', short).decode().strip() == full)
        relation = subprocess.run(['git', '-C', str(REPO), 'merge-base', '--is-ancestor', full, head]).returncode
        check('HEAD ancestry query completed ' + short, relation in (0, 1))
        head_ancestry[full] = relation == 0
    for older, newer in [(CORE, V5), (V5, PREP)]:
        check('ancestry ' + older[:7] + ' -> ' + newer[:7],
              subprocess.run(['git', '-C', str(REPO), 'merge-base', '--is-ancestor', older, newer]).returncode == 0)

    for key, commit, expected_count in [('v5', V5, 27), ('prep', PREP, 8)]:
        prefix = 'drafts/v52/' + PACKAGES[key] + '/'
        data = raw(commit, prefix + 'PAYLOAD_HASHES.json')
        manifest = json.loads(data)
        (out / (key + '_PAYLOAD_HASHES.raw.json')).write_bytes(data)
        entries = manifest.get('files') or [dict(path=p, sha256=h) for p, h in manifest['sha256'].items()]
        check(key + ' manifest entry count', len(entries) == expected_count, actual=len(entries))
        check(key + ' manifest unique paths', len({e['path'] for e in entries}) == len(entries))
        for e in entries:
            p = str(safe_relative(e['path']))
            b = raw(commit, prefix + p)
            record = dict(commit=commit, path=prefix + p, git_blob=git('rev-parse', commit + ':' + prefix + p).decode().strip(),
                          expected_sha256=e['sha256'], sha256=sha(b), bytes=len(b))
            blobs.append(record)
            check(key + ' raw payload ' + p, sha(b) == e['sha256'] and len(b) == e.get('bytes', len(b)))
        check(key + ' manifest base ancestry', subprocess.run(['git', '-C', str(REPO), 'merge-base', '--is-ancestor', manifest['base_commit'], commit]).returncode == 0)

    core_path = 'drafts/v52/' + PACKAGES['core'] + '/membership_scaling_core.py'
    core = raw(CORE, core_path)
    check('pinned core raw hash', sha(core) == CORE_HASH, sha256=sha(core))
    check('core unchanged at v5 and prep', raw(V5, core_path) == core == raw(PREP, core_path))
    (out / 'core_raw_identity.json').write_text(json.dumps(dict(commit=CORE, path=core_path, sha256=sha(core), bytes=len(core)), indent=2))

    recovery_bytes = (NS / 'RECOVERY_INPUT.json').read_bytes()
    recovery = json.loads(recovery_bytes)
    check('recovery entry count', len(recovery['files']) == 11)
    current = []
    for e in recovery['files']:
        p = str(safe_relative(e['path']))
        snap = (NS / 'provenance/pre_edit' / p).read_bytes()
        check('recovery pre-edit ' + p, sha(snap) == e['sha256'] and len(snap) == e['bytes'])
        now = (NS / p).read_bytes()
        current.append(dict(path=p, recovery_sha256=e['sha256'], current_sha256=sha(now),
                            bytes=len(now), changed_since_recovery=now != snap))
        diff_path = out / 'recovery_to_current' / (p + '.diff')
        diff_path.parent.mkdir(parents=True, exist_ok=True)
        diff_path.write_text(''.join(difflib.unified_diff(snap.decode().splitlines(True), now.decode().splitlines(True),
                             fromfile='verified_pre_edit/' + p, tofile='current/' + p)), encoding='utf-8', newline='')
    check('current core remains bound raw bytes', sha((NS / 'membership_scaling_core.py').read_bytes()) == CORE_HASH)

    for old, new in [('membership_runner_v4.py', 'membership_runner_g3.py'), ('corpus_ingest_v4.py', 'corpus_ingest_g3.py')]:
        before = raw(V5, 'drafts/v52/' + PACKAGES['v5'] + '/' + old)
        snap = (NS / 'provenance/pre_edit' / new).read_bytes()
        check('pre-edit raw v5 capture ' + old, (NS / 'provenance/pre_edit' / ('v5_' + old)).read_bytes() == before)
        for label, after in [('pre_edit', snap), ('current', (NS / new).read_bytes())]:
            diff = ''.join(difflib.unified_diff(before.decode().splitlines(True), after.decode().splitlines(True), fromfile=V5 + ':' + old, tofile=label + '/' + new))
            (out / (label + '_' + new + '.diff')).write_text(diff, encoding='utf-8', newline='')

    # Explicit dependency allowlist: no validation/replay launcher or historical results.
    shared = ['authoritative/__init__.py', 'authoritative/accepted_configuration.py',
              'authoritative/resolve_sources.py', 'errors.py', 'safe_report.py']
    selection = {
        'core': ['membership_scaling_core.py', 'test_membership_scaling_core.py', 'README_IMPL_V3.md', 'GOVERNING_DOCUMENTS.md'],
        'v3': shared + ['membership_runner_v3.py', 'corpus_ingest_v3.py'],
        'v4': shared + ['membership_runner_v4.py', 'corpus_ingest_v4.py'],
        'v5': shared + ['membership_runner_v4.py', 'corpus_ingest_v4.py', 'test_runner_ingest_v4.py', 'test_codex_v5.py', 'README.md'],
        'prep': ['pipeline.py', 'test_pipeline.py', 'README.md'],
    }
    for key, files in selection.items():
        commit = CORE if key == 'core' else PREP if key == 'prep' else V5
        for name in files:
            source = 'drafts/v52/' + PACKAGES[key] + '/' + name
            b = raw(commit, source)
            if name.endswith('.py'):
                ast.parse(b)  # Syntax only, no import or execution.
            dest = SOURCES / PACKAGES[key] / name
            immutable(dest, b)
            materialized.append(dict(commit=commit, source=source, destination=str(dest.relative_to(NS)), sha256=sha(b), bytes=len(b)))
    arithmetic = raw(ARITH, ARITH_PATH)
    check('pinned arithmetic raw hash', sha(arithmetic) == ARITH_HASH)
    immutable(SOURCES / 'pinned_arithmetic_source.py', arithmetic)
    materialized.append(dict(commit=ARITH, source=ARITH_PATH, destination=str((SOURCES / 'pinned_arithmetic_source.py').relative_to(NS)), sha256=sha(arithmetic), bytes=len(arithmetic)))
    names = {'topks_by_hamming', 'fractional', 'stable_archive_seed'}
    selected = [n for n in ast.parse(arithmetic).body if isinstance(n, ast.FunctionDef) and n.name in names]
    check('arithmetic has exactly three selected functions', len(selected) == 3 and {n.name for n in selected} == names)
    write_json(out / 'MATERIALIZED.json', materialized)
    write_json(out / 'RAW_BLOBS.json', blobs)
    write_json(out / 'CURRENT_VS_RECOVERY.json', current)
    result = dict(head=head, pins_are_ancestors_of_head=head_ancestry,
                  head_ancestry_note='Delivery HEAD ancestry is an observation; required source chain is core -> v5 -> prep.',
                  python=sys.executable, environment={k: os.environ.get(k) for k in THREAD_ENV},
                  python_version=sys.version, locked_package_versions=LOCK,
                  recovery_manifest_sha256=sha(recovery_bytes), verifier_sha256=sha(Path(__file__).read_bytes()),
                  checks=checks, check_count=len(checks), failed=sum(not c['passed'] for c in checks),
                  scope='Raw identity and Git ancestry only. Synthetic evidence hashed in memory; no corpus or historical result materialized.')
    write_json(out / 'RESULTS.json', result)
    (out / 'checks.log').write_text('\n'.join(('PASS ' if c['passed'] else 'FAIL ') + c['label'] for c in checks) + '\n')
    print(f"PROVENANCE: {len(checks)} checks; {result['failed']} failed")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-dir', required=True)
    args = parser.parse_args()
    runtime()
    out = fresh_dir(args.evidence_dir)
    temporary = out / 'tmp'
    temporary.mkdir()
    os.environ.update(TMP=str(temporary), TEMP=str(temporary), TMPDIR=str(temporary))
    try:
        return int(verify(out)['failed'] != 0)
    except Exception as exc:
        write_json(out / 'ERROR.json', dict(type=type(exc).__name__, message=str(exc)))
        raise


if __name__ == '__main__':
    raise SystemExit(main())
