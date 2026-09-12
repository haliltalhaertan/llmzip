"""Verify exact Git delta/manifest and materialize only Python sources into audit scratch."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import subprocess

A = Path(__file__).resolve().parent
R = A.parent
OLD = '24d3351f068f6982148c14a9e3338c29a2769449'
NEW = '23fb505ae47d06b34a75a97955e5d1a3d8586de1'
PRIOR_AUDIT = '2a025ee3b85f25af80e1b939f85f23c6cf06af30'
P = 'drafts/v52/membership_g3_remediation_2026_09_11/'
S = A / 'v52/membership_g3_remediation_2026_09_11'
def git(*args):
    return subprocess.check_output(['git', '-C', str(R), *args])
def raw(ref, path):
    return git('cat-file', 'blob', ref + ':' + path)
def sha(b):
    return hashlib.sha256(b).hexdigest()
def write(name, value):
    (A / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')
checks = []
def check(name, passed):
    checks.append(dict(name=name, passed=bool(passed)))
    assert passed, name

check('candidate parent equals original candidate', git('rev-parse', NEW+'^').decode().strip() == OLD)
check('audit branch retains original rejection', git('rev-parse', 'HEAD').decode().strip() == PRIOR_AUDIT)
check('remote candidate exact', git('rev-parse', 'origin/codex/g3-remediation-delivery-2026-09-12').decode().strip() == NEW)
check('local core.autocrlf=false', git('config', '--local', 'core.autocrlf').strip() == b'false')
changes = git('diff', '--name-status', OLD, NEW).decode().splitlines()
expected = {'A1_REMEDIATION.md', 'FILE_HASHES.json', 'README.md', 'TRACEABILITY.md',
            'evidence/a1_fixed/COMMAND.json', 'evidence/a1_fixed/RESULTS.json',
            'evidence/a1_fixed/stderr.txt', 'evidence/a1_fixed/stdout.txt',
            'evidence/a1_red/stderr.txt', 'evidence/a1_red/stdout.txt',
            'integration_g3.py', 'test_delivery_integration.py'}
check('exact twelve changed paths and no deletions', len(changes) == 12 and
      {x.split('\t')[1] for x in changes} == {P+x for x in expected} and all(x[0] in 'AM' for x in changes))
for folder in ('provenance', 'inherited', 'evidence/final'):
    check('unchanged historical '+folder, git('diff', OLD, NEW, '--', P+folder) == b'')

tree = git('ls-tree', '-r', '--name-only', NEW, '--', P).decode().splitlines()
mraw = raw(NEW, P+'FILE_HASHES.json')
m = json.loads(mraw)
check('432 payload entries exact unique coverage', len(m['files']) == len({e['path'] for e in m['files']}) == 432 and
      sorted(P+e['path'] for e in m['files']) == sorted(p for p in tree if p != P+'FILE_HASHES.json'))
hashes = []
python_sources = []
for e in m['files']:
    b = raw(NEW, P+e['path'])
    check('payload '+e['path'], sha(b) == e['sha256'] and len(b) == e['bytes'])
    hashes.append(dict(path=e['path'], bytes=len(b), sha256=sha(b)))
    parts = Path(e['path']).parts
    if e['path'].endswith('.py') and (len(parts) == 1 or (len(parts)==2 and parts[0]=='authoritative')):
        dest = S / e['path']
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b)
        python_sources.append(dict(path=e['path'], sha256=sha(b), bytes=len(b)))
        if e['path'] not in ('integration_g3.py', 'test_delivery_integration.py'):
            check('Python unchanged '+e['path'], b == raw(OLD, P+e['path']))
new_test = ast.parse(raw(NEW, P+'test_delivery_integration.py'))
old_test = ast.parse(raw(OLD, P+'test_delivery_integration.py'))
new_class = next(n for n in new_test.body if isinstance(n, ast.ClassDef) and n.name=='DeliveryIntegration')
added = [n for n in new_class.body if isinstance(n,ast.FunctionDef) and n.name=='test_A1_longmemeval_diagnostics_follow_actual_sorted_assembly']
check('one added regression method', len(added)==1)
new_class.body.remove(added[0])
check('all old test AST unchanged', ast.dump(new_test, include_attributes=False)==ast.dump(old_test, include_attributes=False))

current_receipt = json.loads(raw(NEW, P+'evidence/a1_fixed/RESULTS.json'))
check('reported full54 success', current_receipt['status']=='PASS' and current_receipt['test_methods_observed']==54
      and current_receipt['subtests_observed']==5961 and all(current_receipt[k]==0 for k in ('failures','errors','skips')))
for path, digest in current_receipt['source_sha256'].items():
    check('implementation full54 source binding '+path, sha(raw(NEW,P+path)) == digest)
evidence_dir = A / 'candidate_evidence'
evidence_dir.mkdir(exist_ok=False)
for path in ('A1_REMEDIATION.md','evidence/a1_red/stderr.txt','evidence/a1_fixed/RESULTS.json','evidence/a1_fixed/COMMAND.json'):
    dest = evidence_dir / path
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(raw(NEW,P+path))

diff = git('diff','--no-ext-diff',OLD,NEW,'--',P+'integration_g3.py',P+'test_delivery_integration.py',P+'README.md',P+'TRACEABILITY.md')
(A/'EXACT_FOCUSED_DELTA.diff').write_bytes(diff)
write('IDENTITY_RESULTS.json', dict(candidate=NEW, previous_candidate=OLD, original_audit=PRIOR_AUDIT,
      check_count=len(checks), failed=sum(not c['passed'] for c in checks), changes=changes,
      manifest_sha256=sha(mraw), checks=checks))
write('CANDIDATE_PAYLOAD_HASHES.json',dict(candidate=NEW,manifest_sha256=sha(mraw),files=hashes))
write('EXECUTED_SOURCE_BINDING.json',dict(candidate=NEW, files=python_sources))

# Preserve the previous independent probe's fixture, real numerical path and observer.
# Only new candidate/expected success and additional metadata checks are introduced.
before = raw(PRIOR_AUDIT,'audit_v52_g3_independent_2026_09_12/probe_lme_binding.py').decode()
after = before.replace(OLD,NEW).replace("'LME_BINDING_REPRO.json'", "'A1_DELTA_PROBE.json'")
after = after.replace('reproduced=len(mismatches) == 2', 'fixed=len(mismatches) == 0')
after = after.replace("assert report['reproduced'], 'Static finding not reproduced'", "assert report['fixed'], 'A1 still present'")
extra = '''
assert envelope['question_ids'] == ingested['cohort_ids'] == ids
assert envelope['records'] == prepared['records']
for diag in envelope['diagnostics']:
    actual = next(x for x in calls if x['ordinal'] == diag['archive_ordinal'])
    assert diag['question_ids'] == actual['question_ids']
    assert diag['cv_sigma_before'] == actual['diagnostics']['cv_sigma_before']
wrong = copy.deepcopy(envelope)
wrong['diagnostics'][0]['question_ids'], wrong['diagnostics'][1]['question_ids'] = (
    wrong['diagnostics'][1]['question_ids'], wrong['diagnostics'][0]['question_ids'])
binding_bytes = json.dumps({k:v for k,v in wrong.items() if k != 'binding_sha256'},
    sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')
wrong['binding_sha256'] = hashlib.sha256(binding_bytes).hexdigest()
negative_codes = []
with mock.patch.object(bridge.runner, 'compute_synthetic_results', side_effect=AssertionError('numerics reached')) as numerical:
    for validate in (bridge._validate_envelope, bridge.compute_synthetic_result):
        try:
            validate(wrong)
        except bridge.IntegrationError as exc:
            assert str(exc) == 'E-G3-I05'
            assert exc.__cause__ is None and exc.__context__ is None
            negative_codes.append(str(exc))
        else:
            raise AssertionError('Rehashed wrong IDs accepted')
    numerical.assert_not_called()
'''
after = after.replace("report = dict(candidate=",extra+"\nreport = dict(negative_codes=negative_codes, question_order_preserved=True, records_preserved=True, diagnostics_cv_matches_observer=True, candidate=")
(A/'replay_a1_probe.py').write_text(after,encoding='utf-8',newline='\n')
(A/'PROBE_ADAPTATION.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),
    fromfile=PRIOR_AUDIT+':probe_lme_binding.py',tofile='replay_a1_probe.py')),encoding='utf-8',newline='\n')
write('PROBE_LINEAGE.json',dict(original_audit=PRIOR_AUDIT,original_probe_sha256=sha(before.encode()),
      new_probe_sha256=sha(after.encode()),note='Original unsorted fixture and real computation preserved; expect zero mismatches, check CV/records/order and independently rehash wrong IDs.'))
print(json.dumps(dict(checks=len(checks),failed=0,payloads=len(hashes),sources=len(python_sources))))
