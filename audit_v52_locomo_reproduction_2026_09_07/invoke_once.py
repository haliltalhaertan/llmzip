"""Exclusive one-invocation latch; no retry and no alteration of sealed runner."""
import datetime, hashlib, importlib.metadata, json, os, pathlib, platform, subprocess, sys, time
HERE=pathlib.Path(__file__).resolve().parent
TMP=HERE.parent.parent/'locomo_reproduction_tmp_20260907'
def main():
    gatebytes=(HERE/'preflight.json').read_bytes(); gate=json.loads(gatebytes)
    assert gate['status']=='READY_FOR_ONE_INVOCATION'
    assert sys.version_info[:2]==(3,13)
    assert {p:importlib.metadata.version(p) for p in gate['packages']}==gate['packages']
    for entry in gate['files']:
        if 'execution_path' in entry:
            assert hashlib.sha256(pathlib.Path(entry['execution_path']).read_bytes()).hexdigest()==entry['sha256']
    assert len(sys.argv)==2, 'Pass parent published gate receipt commit'
    out=TMP/'reproduction_output'
    assert not out.exists(), 'refuse output reuse'
    command=[sys.executable,'-B',str(TMP/'sealed_source'/'locomo_coordinate_scale.py'),'--out',str(out)]
    receipt={'status':'STARTED','invocation_count':1,'utc_start':datetime.datetime.now(datetime.timezone.utc).isoformat(),'gate_sha256':hashlib.sha256(gatebytes).hexdigest(),'published_gate_receipt_commit':sys.argv[1],'command':command,'platform':platform.platform(),'python':sys.version,'thread_environment':{k:os.environ.get(k) for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']}}
    with (HERE/'run_receipt.json').open('x',encoding='utf-8') as f: json.dump(receipt,f,indent=2)
    with (HERE/'environment.txt').open('w',encoding='utf-8') as f:
        p=subprocess.run([sys.executable,'-m','pip','freeze'],stdout=f,stderr=subprocess.STDOUT,text=True)
        assert p.returncode==0
    with (HERE/'numerical_configuration.txt').open('w',encoding='utf-8') as f:
        subprocess.run([sys.executable,'-c','import numpy,scipy; numpy.show_config(); scipy.show_config()'],stdout=f,stderr=subprocess.STDOUT,text=True,check=True)
    start=time.monotonic()
    with (HERE/'runner_stdout_stderr.txt').open('w',encoding='utf-8') as f:
        proc=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,text=True)
    receipt.update(status='COMPLETED' if proc.returncode==0 else 'FAILED_NO_RETRY',returncode=proc.returncode,elapsed_seconds=time.monotonic()-start,utc_finish=datetime.datetime.now(datetime.timezone.utc).isoformat())
    receipt['outputs']=[{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.glob('*')) if p.is_file()]
    (HERE/'run_receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(json.dumps(receipt,indent=2))
    return proc.returncode
if __name__=='__main__': sys.exit(main())
