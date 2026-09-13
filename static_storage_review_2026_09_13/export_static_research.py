from pathlib import Path
import subprocess,json,hashlib,datetime,re
home=Path.home(); r=home/'muse-work'; repo=r/'llmzip-audit'
out=Path('/mnt/c/Users/MDP/dev/llmzip-work/github_static_export'); out.mkdir(exist_ok=True)
def git(*args): return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
refs=['muse/fix-static-denominator','muse/fix-v9-concurrency','muse/harden-static-tests','muse/complete-campaign-labels']
subprocess.run(['git','-C',str(repo),'bundle','create',str(out/'completed.bundle'),*refs],check=True)
e=out/'evidence'; e.mkdir(exist_ok=True)
for name in ['static-denom','static-race','static-tests','campaign-label-audit','static-integrated','campaign-label-fix']:
 p=r/(name+'.log')
 if p.exists(): (e/p.name).write_bytes(p.read_bytes())
p=r/'static-tests-coordinator-reruns.json'
if p.exists(): (e/p.name).write_bytes(p.read_bytes())
prompts=Path('/mnt/c/Users/MDP/AppData/Local/Temp')
for name in ['muse-static-denom.txt','muse-static-race.txt','muse-static-tests.txt','muse-campaign-label-audit.txt','muse-integrate-static-v10.txt','muse-complete-campaign-labels.txt']:
 p=prompts/name; (e/name).write_bytes(p.read_bytes())
source=r/'static-integrated'; snapshot=e/'integration_work_in_progress'; snapshot.mkdir(exist_ok=True)
records=[]
for dirname in ['static_storage_integration_v10_2026_09_13','static_storage_security_regression_2026_09_13']:
 for p in sorted((source/'drafts/v52'/dirname).rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts or p.suffix in ['.pyc','.pyo']: continue
  rel=p.relative_to(source); data=p.read_bytes(); dst=snapshot/rel; dst.parent.mkdir(parents=True,exist_ok=True); dst.write_bytes(data)
  records.append({'path':rel.as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
meta={'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'WORK IN PROGRESS; NON-ATOMIC LIVE COPY; NOT VERIFIED INTEGRATED RELEASE','completed_commits':{v:git('rev-parse',v) for v in refs},'integration_head':subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip(),'integration_status':subprocess.check_output(['git','-C',str(source),'status','--porcelain'],text=True),'files':records}
(e/'SNAPSHOT_INVENTORY.json').write_text(json.dumps(meta,indent=2)+'\n')
# High-confidence secret signatures only; report paths, never matching values.
patterns=[rb'gh[pousr]_[A-Za-z0-9]{30,}',rb'AKIA[A-Z0-9]{16}',rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',rb'sk-(?:proj-|live_|test_)[A-Za-z0-9_-]{20,}']
hits=[str(p.relative_to(e)) for p in e.rglob('*') if p.is_file() and any(re.search(q,p.read_bytes()) for q in patterns)]
if hits: raise RuntimeError('Secret scan flagged files: '+str(hits))
print(json.dumps({'export':str(out),'completed_refs':meta['completed_commits'],'snapshot_files':len(records),'evidence_files':sum(p.is_file() for p in e.rglob('*')),'secret_signature_hits':hits},indent=2))
