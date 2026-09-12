"""Check inherited receipts/source adaptation without executing historical suites."""
import hashlib
import json
from pathlib import Path
import subprocess

A = Path(__file__).resolve().parent
R = A.parent
N = R / 'drafts/v52/membership_g3_remediation_2026_09_11'
checks = []
def sha(b):
    return hashlib.sha256(b).hexdigest()
def check(name, value):
    checks.append(dict(name=name, passed=bool(value)))
def raw(commit, path):
    return subprocess.check_output(['git', '-C', str(R), 'cat-file', 'blob', commit + ':' + path])
def read(path):
    return json.loads((N / path).read_bytes())

for commit, package in [('07ec929243068914676a0f30efd10c9f294c7e71', 'membership_runner_ingest_codex_v5_2026_09_08'), ('ed4e22c520b7dc0ae2f43f915e0c621070c72a87', 'membership_execution_prep_v1_2026_09_08')]:
    prefix = 'drafts/v52/' + package + '/'
    m = json.loads(raw(commit, prefix + 'PAYLOAD_HASHES.json'))
    entries = m.get('files') or [dict(path=p, sha256=h) for p, h in m['sha256'].items()]
    for item in entries:
        b = raw(commit, prefix + item['path'])
        check('historical payload ' + package + '/' + item['path'], sha(b) == item['sha256'] and len(b) == item.get('bytes', len(b)))

snapshot = read('inherited/final/CURRENT_SOURCE_SNAPSHOT.json')
for path, digest in snapshot.items():
    check('inherited final snapshot ' + path, sha((N / path).read_bytes()) == digest)

# Reconstruct only reviewed import/path substitutions; never execute adapted files.
allowed = {
    ('import membership_runner_v4 as R4', 'import membership_runner_g3 as R4'),
    ('import corpus_ingest_v4 as I4', 'import corpus_ingest_g3 as I4'),
    ('"membership_runner_v4.py"', '"membership_runner_g3.py"'),
    ('"corpus_ingest_v4.py"', '"corpus_ingest_g3.py"'),
    ('import membership_runner_v4 as R\nimport corpus_ingest_v4 as I', 'if OLD:\n    import membership_runner_v4 as R\n    import corpus_ingest_v4 as I\nelse:\n    import membership_runner_g3 as R\n    import corpus_ingest_g3 as I'),
    ('import pipeline as p', 'import pipeline_g3 as p'),
}
adaptations = read('inherited/final/ADAPTATIONS.json')
test_hashes = {}
for item in adaptations:
    path = item['source'].replace('\\', '/')
    b = (N / path).read_bytes()
    check('adaptation source hash ' + path, sha(b) == item['source_sha256'])
    text = b.decode('utf-8')
    for sub in item['substitutions']:
        check('allowlisted routing-only substitution ' + path + ' ' + sub['old'],
              (sub['old'], sub['new']) in allowed and text.count(sub['old']) == sub['occurrences'])
        text = text.replace(sub['old'], sub['new'])
    check('reconstructed adaptation ' + item['destination'], sha(text.encode()) == item['adapted_sha256'])
    if path.rsplit('/', 1)[-1].startswith('test_'):
        test_hashes[item['destination'].replace('\\', '/')] = item['adapted_sha256']

receipt = read('inherited/final/RESULTS.json')
check('inherited receipt complete/no drift', receipt['complete'] and receipt['failed_suites'] == 0
      and receipt['current_sources_changed_during_run'] == [] and receipt['scripts_changed_during_run'] == [])
check('inherited launcher hash current', receipt['runner_sha256'] == sha((N / 'run_inherited.py').read_bytes()))
summary = []
for s in receipt['suites']:
    m = s['metrics']
    check('inherited suite receipt ' + s['suite'], s['exit_code'] == 0 and not s['timed_out'])
    summary.append(dict(suite=s['suite'], exit_code=s['exit_code'], check_count=m.get('check_count'),
                        unittest_tests_run=m.get('unittest_tests_run'), source_sha256=s['source_sha256']))
    suite_path = s['command'][4].replace('\\', '/')
    relative = suite_path.split('/membership_g3_remediation_2026_09_11/', 1)[1]
    want = test_hashes.get(relative)
    if want is None:
        want = sha((N / relative).read_bytes())
    check('receipt binds suite source ' + s['suite'], want == s['source_sha256'])

final = read('evidence/final/RESULTS.json')
for path, digest in final['source_sha256'].items():
    check('implementation final receipt current source ' + path, sha((N / path).read_bytes()) == digest)
prov = read('provenance/final/RESULTS.json')
check('provenance final receipt no failed checks', prov['check_count'] == 73 and prov['failed'] == 0 and all(x['passed'] for x in prov['checks']))
result = dict(scope='Static raw identities and inherited receipt consistency only; no historical suite rerun.',
              check_count=len(checks), failed=sum(not x['passed'] for x in checks), inherited_suites=summary,
              executed_source_count=len(final['source_sha256']), checks=checks)
(A / 'EVIDENCE_REVIEW.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps({k:v for k,v in result.items() if k != 'checks'}))
