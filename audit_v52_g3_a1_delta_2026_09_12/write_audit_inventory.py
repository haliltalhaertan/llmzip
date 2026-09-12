"""Audit output inventory only, with final read-only source/namespace verification."""
import hashlib
import json
from pathlib import Path
import subprocess

A=Path(__file__).resolve().parent
R=A.parent
N='23fb505ae47d06b34a75a97955e5d1a3d8586de1'
P='drafts/v52/membership_g3_remediation_2026_09_11/'
def git(*args):return subprocess.check_output(['git','-C',str(R),*args])
def sha(b):return hashlib.sha256(b).hexdigest()
def write(name,value):(A/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')
def read(name):return json.loads((A/name).read_bytes())
m=json.loads(git('cat-file','blob',N+':'+P+'FILE_HASHES.json'))
declared=[e['path'] for e in m['files']]
ordered=sorted(declared)
assert len(declared)==len(set(declared))==432 and declared!=ordered
write('A2_MANIFEST_ORDER.json',dict(candidate=N,entries=432,duplicates=0,all_payload_hashes_verified=True,
      list_order_matches_verifier=False,first_order_difference=next({'declared':a,'expected':b} for a,b in zip(declared,ordered) if a!=b),
      verifier_sha256=sha(git('cat-file','blob',N+':'+P+'package_integrity.py')),observed_exit_code=1,
      error='RuntimeError: file inventory mismatch'))
assert not git('diff','2a025ee3b85f25af80e1b939f85f23c6cf06af30','--','audit_v52_g3_independent_2026_09_12',P)
identity=read('IDENTITY_RESULTS.json')
assert identity['failed']==0
for e in read('EXECUTED_SOURCE_BINDING.json')['files']:
    assert sha((A/'v52/membership_g3_remediation_2026_09_11'/e['path']).read_bytes())==e['sha256']
test=read('new_test_retry/NEW_A1_TEST.json')
probe=read('A1_DELTA_PROBE.json')
assert test['status']=='PASS' and probe['fixed'] and probe['negative_codes']==['E-G3-I05','E-G3-I05']
write('DISPOSITION.json',dict(candidate=N,previous_candidate='24d3351f068f6982148c14a9e3338c29a2769449',
      original_audit='2a025ee3b85f25af80e1b939f85f23c6cf06af30',A1='CLOSED_SCOPED_SYNTHETIC',A2='OPEN_MANIFEST_ORDER',
      scoped_A1_repair='ACCEPTED',exact_delivery='NOT_ACCEPTED_PENDING_A2',
      independent_new_methods=1,independent_new_subtests=2,independent_prior_probe_replays=1,
      full54_replays=0,historical_suite_replays=0,identity_checks=identity['check_count'],
      audit_launcher_import_failures=1,production_holds='UNCHANGED_OPEN',main_writes=0,
      prior_audit_unchanged=True,candidate_worktree_unchanged=True))
files=[]
for f in sorted(A.rglob('*')):
    rel=f.relative_to(A)
    if not f.is_file() or rel.parts[0] in ('v52','targeted_scratch') or rel.as_posix()=='SHA256SUMS.json':continue
    b=f.read_bytes();files.append(dict(path=rel.as_posix(),bytes=len(b),sha256=sha(b)))
write('SHA256SUMS.json',dict(candidate=N,self_excluded=True,kind='Audit integrity only; no seal',files=files))
print(json.dumps(dict(files=len(files)+1,report_sha256=sha((A/'A1_DELTA_AUDIT.md').read_bytes()),inventory_sha256=sha((A/'SHA256SUMS.json').read_bytes()))))
