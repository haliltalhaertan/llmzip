from pathlib import Path
import shutil,hashlib,json,re,datetime
W=Path('/mnt/c/Users/MDP/dev/llmzip-work'); workers=Path.home()/'muse-work'
D=W/'github-publish-static/research_math_theory_2026_09_13'; D.mkdir(exist_ok=True)
records=[]; excluded=[]
def cp(src,dst,kind):
 data=src.read_bytes()
 if len(data)>95*1024*1024: raise RuntimeError('Oversize file:'+str(src))
 patterns=[rb'gh[pousr]_[A-Za-z0-9]{30,}',rb'AKIA[A-Z0-9]{16}',rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',rb'sk-(?:proj-|live_|test_)[A-Za-z0-9_-]{20,}']
 if any(re.search(p,data) for p in patterns): raise RuntimeError('Secret signature in '+str(src))
 dst.parent.mkdir(parents=True,exist_ok=True); dst.write_bytes(data)
 records.append({'source':str(src),'path':dst.relative_to(D).as_posix(),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'kind':kind})
for root in ['math_discovery_2026_09_13','theory_benchmark_test_v1']:
 for p in sorted((W/root).rglob('*')):
  if not p.is_file(): continue
  if '__pycache__' in p.parts or p.suffix in ['.pyc','.pyo','.pkl']:
   excluded.append({'source':str(p),'reason':'derived cache/bytecode, not unique findings'}); continue
  cp(p,D/root/p.relative_to(W/root),'coordinator_preserved')
mapping={
'math-ranking-bounds':'math_discovery_2026_09_13/ranking_bounds',
'math-sign-mechanism':'math_discovery_2026_09_13/sign_mechanism',
'math-bit-allocation':'math_discovery_2026_09_13/bit_allocation',
'math2-sharp-bounds':'math_discovery_2026_09_13/round2/sharp_bounds',
'math2-allocation-optimality':'math_discovery_2026_09_13/round2/allocation_optimality',
'math3-joint-gold-bounds':'math_discovery_2026_09_13/round3/joint_gold_bounds',
'math3-all-n-ranking':'math_discovery_2026_09_13/round3/all_n_ranking',
'math4-norm-aware-sign-bounds':'math_discovery_2026_09_13/round4/norm_aware_sign_bounds',
'math4-rank-crossing-certificates':'math_discovery_2026_09_13/round4/rank_crossing_certificates',
 'theorybench-lme':'theory_benchmark_test_v1/lme',
 'theorybench-locomo':'theory_benchmark_test_v1/locomo',
 'theorybench-realtalk':'theory_benchmark_test_v1/realtalk',
 'theorybench-perltqa':'theory_benchmark_test_v1/perltqa',
 'theory-audit-locomo-provenance':'theory_benchmark_test_v1/audit_locomo_provenance',
 'theory-audit-mapping':'theory_benchmark_test_v1/audit_mapping',
 'theory-audit-real-geometry':'theory_benchmark_test_v1/audit_real_geometry'}
for name,dest in mapping.items():
 source=workers/name; assert source.is_dir(),name
 for p in sorted(source.rglob('*')):
  if not p.is_file(): continue
  if '__pycache__' in p.parts or p.suffix in ['.pyc','.pyo','.pkl']:
   excluded.append({'source':str(p),'reason':'derived cache/bytecode; tabular outcomes preserved','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}); continue
  target=D/dest/p.relative_to(source)
  if not target.exists(): cp(p,target,'supplemental_worker_file')
  elif target.read_bytes()!=p.read_bytes(): cp(p,D/'worker_versions'/name/p.relative_to(source),'different_worker_version_preserved')
 for required in ['REPORT.md','COORDINATOR_REVIEW.md']:
  assert (D/dest/required).exists(),str(D/dest/required)
allnames=list(mapping)+['math2-conditional-ranking']
for name in allnames:
 prompt=Path('/mnt/c/Users/MDP/AppData/Local/Temp')/('muse-'+name+'.txt')
 assert prompt.exists(),str(prompt)
 cp(prompt,D/'tasking'/prompt.name,'prompt')
 for p in sorted(workers.glob(name+'*.log')): cp(p,D/'worker_logs'/p.name,'worker_stdout')
cp(Path('/mnt/c/Users/MDP/dev/llmzip-work/archive_math_research.py'),D/'ops/archive_math_research.py','preservation_tool')
inv={'captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'completed_workers':mapping,'failed_attempt_with_no_output':'math2-conditional-ranking; initial/retry logs retained','math_workers':sum(n.startswith('math') for n in mapping),'benchmark_workers':sum(n.startswith('theorybench') for n in mapping),'audit_workers':sum(n.startswith('theory-audit') for n in mapping),'records':records,'excluded':excluded}
(D/'SOURCE_INVENTORY.json').write_bytes((json.dumps(inv,indent=2)+'\n').encode())
paths=[x['path'] for x in records]; assert len(paths)==len(set(paths))
print(json.dumps({'destination':str(D),'completed_workers':len(mapping),'math_workers':inv['math_workers'],'benchmark_workers':inv['benchmark_workers'],'audit_workers':inv['audit_workers'],'copied_files':len(records),'bytes':sum(x['bytes'] for x in records),'excluded_cache_files':len(excluded),'largest':sorted([(x['bytes'],x['path']) for x in records],reverse=True)[:5]},indent=2))
