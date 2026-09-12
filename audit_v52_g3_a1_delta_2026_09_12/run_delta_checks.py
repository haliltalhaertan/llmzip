"""Only the new A1 method and the prior independent A1 probe; no full-suite replay."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

A = Path(__file__).resolve().parent
S = A / 'v52/membership_g3_remediation_2026_09_11'
PY = A.parent.parent / '.venvs/g3-lock-20260912/Scripts/python.exe'
NEW = '23fb505ae47d06b34a75a97955e5d1a3d8586de1'
THREADS = ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS',
           'OMP_THREAD_LIMIT','BLIS_NUM_THREADS','VECLIB_MAXIMUM_THREADS')
RETRY = '--retry-new-test' in sys.argv
OUT = A / ('new_test_retry' if RETRY else 'focused_runtime')
def write(name, value):
    (OUT / name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

if '--child' in sys.argv:
    assert Path(sys.executable).resolve() == PY.resolve()
    assert sys.dont_write_bytecode and not sys.flags.optimize
    assert os.environ['PYTHONHASHSEED']=='0' and all(os.environ[n]=='1' for n in THREADS)
    sys.path.insert(0,str(S))
    import verify_delivery as launcher
    runtime = launcher.runtime()
    bindings = json.loads((A/'EXECUTED_SOURCE_BINDING.json').read_bytes())
    for f in bindings['files']:
        assert digest(S/f['path']) == f['sha256']
    events = {'allowed_synthetic':0,'denied':0}
    def guard(event,args):
        if event in ('socket.connect','socket.getaddrinfo','subprocess.Popen','os.system'):
            events['denied'] += 1
            raise RuntimeError('external execution forbidden')
        if event not in ('open','os.listdir','os.scandir') or not args or not isinstance(args[0],(str,bytes,os.PathLike)):
            return
        p=Path(os.fsdecode(args[0])).resolve()
        if (p.name == 'direct_url.json' and p.parent.name.endswith('.dist-info')
                and p.parent.parent == (PY.parent.parent / 'Lib/site-packages').resolve()):
            return  # Installed package metadata only; same exception as README launcher.
        data=p.suffix.lower() in ('.json','.jsonl','.csv','.gz','.parquet')
        if data:
            if A in p.parents:
                events['allowed_synthetic'] += 1
            else:
                events['denied'] += 1
                raise RuntimeError('external data forbidden')
    sys.addaudithook(guard)
    name='test_delivery_integration.DeliveryIntegration.test_A1_longmemeval_diagnostics_follow_actual_sorted_assembly'
    suite=unittest.defaultTestLoader.loadTestsFromName(name)
    result=unittest.TextTestRunner(verbosity=2,resultclass=launcher.RecordedResult).run(suite)
    passed=result.wasSuccessful() and result.testsRun==1 and result.subtests_observed==2 and not result.skipped
    write('NEW_A1_TEST.json',dict(candidate=NEW,status='PASS' if passed else 'FAIL',runtime=runtime,
        executable=sys.executable,test_methods=result.testsRun,subtests=result.subtests_observed,
        failures=len(result.failures),errors=len(result.errors),skips=len(result.skipped),tests=result.entries,
        data_events=events,source_binding='EXECUTED_SOURCE_BINDING.json',
        scope='Only newly added A1 regression. Existing setUpClass generates LoCoMo integration fixture. No full54 or historical suite run.'))
    sys.exit(0 if passed else 1)

OUT.mkdir(exist_ok=False)
temp=OUT/'tmp'
temp.mkdir()
env=dict(os.environ,PYTHONHASHSEED='0',PYTHONDONTWRITEBYTECODE='1',TMP=str(temp),TEMP=str(temp),TMPDIR=str(temp),
         **{n:'1' for n in THREADS})
rows=[]
commands=[('new_a1_method',[str(PY),'-B',str(Path(__file__).resolve()),'--child']),
          ('independent_a1_probe',[str(PY),'-B',str(A/'replay_a1_probe.py')]),
          ('package_integrity',[str(PY),'-B',str(A.parent/'drafts/v52/membership_g3_remediation_2026_09_11/package_integrity.py'),'--ref',NEW])]
if RETRY:
    commands = [('new_a1_method', [str(PY), '-B', str(Path(__file__).resolve()), '--child', '--retry-new-test'])]
for name,argv in commands:
    result=subprocess.run(argv,cwd=A.parent,env=env,capture_output=True)
    (OUT/(name+'.stdout.txt')).write_bytes(result.stdout)
    (OUT/(name+'.stderr.txt')).write_bytes(result.stderr)
    rows.append(dict(name=name,argv=argv,exit_code=result.returncode))
write('COMMANDS.json',dict(candidate=NEW,executions=rows))
print(json.dumps(rows))
assert all(r['exit_code']==0 for r in rows[:2]), 'A1 checks failed'
