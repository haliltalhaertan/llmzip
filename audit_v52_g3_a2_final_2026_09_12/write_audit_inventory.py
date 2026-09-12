"""Create external scoped acceptance and audit integrity inventory; not a pre-run seal."""
import hashlib
import json
from pathlib import Path
import subprocess

A=Path(__file__).resolve().parent
R=A.parent
N='7266160ac03bdd064fe75f058eae3430fbe14496'
def git(*args):return subprocess.check_output(['git','-C',str(R),*args])
def sha(b):return hashlib.sha256(b).hexdigest()
def write(name,value):(A/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')
r=json.loads((A/'VERIFICATION_RESULTS.json').read_bytes())
assert r['status']=='PASS' and r['failed']==0 and r['candidate']==N
assert not git('diff','214afbda06a93e083f1357c25fc40cd023701ee4','--',
               'drafts','audit_v52_g3_independent_2026_09_12','audit_v52_g3_a1_delta_2026_09_12')
assert git('branch','--show-current').decode().strip()=='codex/g3-independent-audit-2026-09-12'
report_sha=sha((A/'FINAL_SCOPED_ACCEPTANCE.md').read_bytes())
write('SCOPED_ACCEPTANCE.json',dict(candidate=N,verdict='PASS',
      disposition='ACCEPTED_SCOPED_SYNTHETIC_G3_REMEDIATION',A1='CLOSED',A2='CLOSED',
      unresolved_in_scope_blockers=[],manifest_sha256=r['manifest_sha256'],
      acceptance_report='FINAL_SCOPED_ACCEPTANCE.md',acceptance_report_sha256=report_sha,
      previous_candidate='23fb505ae47d06b34a75a97955e5d1a3d8586de1',
      previous_audit='214afbda06a93e083f1357c25fc40cd023701ee4',
      original_audit='2a025ee3b85f25af80e1b939f85f23c6cf06af30',
      delta_paths=['drafts/v52/membership_g3_remediation_2026_09_11/FILE_HASHES.json'],
      payloads_unchanged=432,retained_source_hashes=21,byte_identity_checks=r['check_count'],
      package_integrity_exit_code=0,test_suite_runs_this_delta=0,historical_suite_runs_this_delta=0,
      numerical_probe_runs_this_delta=0,manifest_status_requires_change=False,
      obligation4='SYNTHETIC_BRIDGE_ACCEPTED; REAL_SOURCE_PROVENANCE_OPEN',
      obligation5='SYNTHETIC_COMPONENTS_AND_INDEPENDENT_SCOPED_ACCEPTANCE_SUPPORTED; FULL_CHAIN_PARTIAL_OPEN',
      remaining_open=['real_ingestion_integration_review','actual_native_anchor_binding','real_cohort_identity',
        'corrected_raw_gold_reconciliation_and_dual_reporting','production_shard_integration',
        'pre_run_seal','production_readiness'],
      authority_note='Independent scoped audit only. HR acceptance and canonical main ledger/state recording are parent-owned.',
      boundaries=dict(main_writes=0,implementation_edits=0,prior_audit_edits=0,corpus_access=0,
        frozen_outcome_access=0,experiment=0,production_retrieval=0,seal=0,finalize=0,HMAC=0,production_authorization=0)))
files=[]
for p in sorted(A.iterdir()):
    if p.is_file() and p.name!='SHA256SUMS.json':
        raw=p.read_bytes();files.append(dict(path=p.name,bytes=len(raw),sha256=sha(raw)))
write('SHA256SUMS.json',dict(candidate=N,self_excluded=True,kind='Audit integrity inventory only; not a seal',files=files))
print(json.dumps(dict(verdict='PASS',candidate=N,files=len(files)+1,report_sha256=report_sha,
    inventory_sha256=sha((A/'SHA256SUMS.json').read_bytes()))))
