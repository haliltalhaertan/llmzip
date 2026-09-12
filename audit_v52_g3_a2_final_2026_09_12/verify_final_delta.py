"""Byte-only A2 delta verification; no test, corpus, or experiment execution."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

A = Path(__file__).resolve().parent
R = A.parent
OLD = '23fb505ae47d06b34a75a97955e5d1a3d8586de1'
NEW = '7266160ac03bdd064fe75f058eae3430fbe14496'
PRIOR_AUDIT = '214afbda06a93e083f1357c25fc40cd023701ee4'
P = 'drafts/v52/membership_g3_remediation_2026_09_11/'
EXPECTED = '9508d1257e0adb515f48c616e67dd410b640fd93d4d472eb54afbffcd148f33d'
def git(*args):
    return subprocess.check_output(['git', '-C', str(R), *args])
def raw(ref, path):
    return git('cat-file','blob',ref+':'+path)
def sha(b):
    return hashlib.sha256(b).hexdigest()
def write(name,value):
    (A/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')
checks=[]
def check(name,value):
    checks.append(dict(name=name,passed=bool(value)))
    assert value,name

check('candidate direct parent',git('rev-parse',NEW+'^').decode().strip()==OLD)
check('exact remote candidate',git('rev-parse','origin/codex/g3-remediation-delivery-2026-09-12').decode().strip()==NEW)
check('prior audit HEAD',git('rev-parse','HEAD').decode().strip()==PRIOR_AUDIT)
check('only one changed path',git('diff','--name-status',OLD,NEW).decode().splitlines()==['M\t'+P+'FILE_HASHES.json'])
manifest=raw(NEW,P+'FILE_HASHES.json')
check('declared manifest raw SHA256',sha(manifest)==EXPECTED)
m=json.loads(manifest)
old=json.loads(raw(OLD,P+'FILE_HASHES.json'))
paths=git('ls-tree','-r','--name-only',NEW,'--',P).decode().splitlines()
expected_paths=[p for p in paths if p!=P+'FILE_HASHES.json']
declared=[P+e['path'] for e in m['files']]
check('432 exact unique canonically ordered paths',len(declared)==len(set(declared))==432 and declared==sorted(expected_paths))
check('payload manifest records unchanged by path',
      {e['path']:e for e in m['files']}=={e['path']:e for e in old['files']})
check('manifest self excluded',m['manifest_self_excluded'] is True)
check('generic status left as canonical writer metadata',m['status']=='SCOPED_SYNTHETIC_CANDIDATE_AWAITING_INDEPENDENT_AUDIT')

# Read only the candidate's declared synthetic payloads from raw Git objects.
# Batch avoids hundreds of separate Git processes; no historical outcome file is read.
specs=[NEW+':'+p for p in declared]
data=subprocess.check_output(['git','-C',str(R),'cat-file','--batch'],input=('\n'.join(specs)+'\n').encode())
cursor=0
for e in m['files']:
    end=data.index(b'\n',cursor)
    header=data[cursor:end].decode().split()
    check('blob type '+e['path'],len(header)==3 and header[1]=='blob')
    size=int(header[2]);start=end+1;b=data[start:start+size];cursor=start+size+1
    check('payload bytes '+e['path'],len(b)==e['bytes'] and sha(b)==e['sha256'])
check('batch fully consumed',cursor==len(data))

# Same Git object IDs imply no payload/source change, independently of manifest claims.
def tree(ref):
    return dict((line.split('\t',1)[1],line.split('\t',1)[0]) for line in
                git('ls-tree','-r',ref,'--',P).decode().splitlines() if not line.endswith('/FILE_HASHES.json'))
check('all432 payload Git objects unchanged',tree(OLD)==tree(NEW) and len(tree(NEW))==432)
bound=json.loads((R/'audit_v52_g3_a1_delta_2026_09_12/EXECUTED_SOURCE_BINDING.json').read_bytes())
for e in bound['files']:
    check('previous independently exercised source '+e['path'],sha(raw(NEW,P+e['path']))==e['sha256'])

verifier=R/P/'package_integrity.py'
check('executed verifier equals candidate raw bytes',verifier.read_bytes()==raw(NEW,P+'package_integrity.py'))
py=R.parent/'.venvs/g3-lock-20260912/Scripts/python.exe'
check('exact locked executable',Path(sys.executable).resolve()==py.resolve())
command=[str(py),'-B',str(verifier),'--ref',NEW]
result=subprocess.run(command,cwd=R,capture_output=True)
(A/'package_integrity.stdout.txt').write_bytes(result.stdout)
(A/'package_integrity.stderr.txt').write_bytes(result.stderr)
write('COMMAND.json',dict(argv=command,exit_code=result.returncode))
check('unchanged package-integrity tool passes exact ref',result.returncode==0)
output=json.loads(result.stdout)
check('verifier exact432refhash result',output==dict(status='PASS',files=432,ref=NEW,manifest_sha256=EXPECTED))
(A/'FILE_HASHES.raw.json').write_bytes(manifest)
write('VERIFICATION_RESULTS.json',dict(candidate=NEW,previous_candidate=OLD,prior_audit=PRIOR_AUDIT,
      status='PASS',check_count=len(checks),failed=0,payloads_verified=432,executed_source_hashes_retained=len(bound['files']),
      manifest_sha256=EXPECTED,suite_runs=0,scope='Byte-only manifest delta and unchanged read-only package verifier.',checks=checks))
print(json.dumps(dict(status='PASS',checks=len(checks),payloads=432,retained_source_hashes=len(bound['files']),manifest_sha256=EXPECTED)))
