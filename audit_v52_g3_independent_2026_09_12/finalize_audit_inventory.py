"""Hash the audit deliverables. This is not an experiment finalizer or a seal."""
import hashlib
import json
from pathlib import Path
import subprocess

A = Path(__file__).resolve().parent
R = A.parent
C = '24d3351f068f6982148c14a9e3338c29a2769449'
PREFIX = 'drafts/v52/membership_g3_remediation_2026_09_11/'
def git(*args):
    return subprocess.check_output(['git', '-C', str(R), *args])
def sha(b):
    return hashlib.sha256(b).hexdigest()
def read(path):
    return json.loads((A / path).read_bytes())
assert not git('diff', C, '--', PREFIX), 'candidate changed'
assert git('branch', '--show-current').decode().strip() == 'codex/g3-independent-audit-2026-09-12'
identity = read('IDENTITY_RESULTS.json')
evidence = read('EVIDENCE_REVIEW.json')
suite = read('suite_once/RESULTS.json')
probe = read('LME_BINDING_REPRO.json')
assert identity['failed'] == evidence['failed'] == 0
assert suite['test_methods_observed'] == 53 and suite['status'] == 'PASS'
assert probe['reproduced'] and len(probe['mismatches']) == 2
sources = read('EXECUTED_SOURCE_BINDING.json')['sources']
for item in sources:
    assert sha((R / PREFIX / item['path']).read_bytes()) == item['sha256']
record = dict(candidate=C, candidate_branch='codex/g3-remediation-delivery-2026-09-12',
              audit_branch='codex/g3-independent-audit-2026-09-12',
              verdict='NOT_ACCEPTED_CHANGES_REQUIRED', blocking_findings=['A1'],
              full_synthetic_suite_invocations=1, test_methods=53, subtests=5959,
              failures=0, errors=0, skips=0, targeted_probe_invocations=1,
              historical_suite_invocations=0, identity_checks=identity['check_count'],
              evidence_checks=evidence['check_count'], executed_python_sources=len(sources),
              candidate_namespace_unchanged=True,
              original_preservation_observation='ORIGINAL_SOURCE_OBSERVATION.json',
              origin_refs_observed=git('ls-remote', 'origin', 'refs/heads/main',
                  'refs/heads/codex/g3-remediation-delivery-2026-09-12').decode().splitlines(),
              boundaries=dict(corpus_access=0, frozen_outcome_access=0, experiment=0,
                  production_retrieval=0, finalize=0, seal=0, HMAC=0, production_authorization=0,
                  implementation_edits=0, main_writes=0, Drive_work=0, cost_replay=0),
              scope='Independent scoped synthetic acceptance audit; no production/native/gold work.')
(A / 'DELIVERY_RECORD.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8', newline='\n')
files = []
for p in sorted(A.rglob('*')):
    rel = p.relative_to(A)
    if rel.parts[0] in ('v52', 'targeted_scratch') or not p.is_file() or rel.as_posix() == 'SHA256SUMS.json':
        continue
    raw = p.read_bytes()
    files.append(dict(path=rel.as_posix(), bytes=len(raw), sha256=sha(raw)))
inventory = dict(candidate=C, kind='Audit artifact identity only; not a pre-run seal', self_excluded=True, files=files)
(A / 'SHA256SUMS.json').write_text(json.dumps(inventory, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps(dict(audit_files=len(files) + 1, report_sha256=sha((A / 'G3_ACCEPTANCE_AUDIT.md').read_bytes()),
                     inventory_sha256=sha((A / 'SHA256SUMS.json').read_bytes()))))
