"""Pre-computation gate. No representation fitting or retrieval is invoked."""
import hashlib, importlib.util, importlib.metadata, json, pathlib, platform, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
AUDIT = pathlib.Path(__file__).resolve().parent
TMP = ROOT.parent / 'locomo_reproduction_tmp_20260907'
TRIGGER = '680b10b8'
def git(*args):
    return subprocess.check_output(['git', '-c', 'safe.directory='+ROOT.as_posix(), '-C', str(ROOT), *args])
def blob(path):
    return git('show', f'{TRIGGER}:{path}')
def sha(b):
    return hashlib.sha256(b).hexdigest()
def main():
    report = {'status':'BLOCKED', 'actual_runner_invocations':0, 'trigger':git('rev-parse',TRIGGER).decode().strip(), 'python':sys.version, 'platform':platform.platform(), 'files':[]}
    try:
        assert sys.version_info[:2] == (3,13), 'requires Python 3.13'
        report['packages'] = {p:importlib.metadata.version(p) for p in ['numpy','pandas','scipy','scikit-learn']}
        assert report['packages'] == {'numpy':'2.3.5','pandas':'2.2.3','scipy':'1.17.0','scikit-learn':'1.8.0'}
        sealpath = 'research/v52/V52_COORDINATE_SCALE_PRERUN_SEAL_2026-09-05.json'
        sealbytes = blob(sealpath)
        trigger = blob('research/v52/TRIGGER_COORDINATE_SCALE_2026-09-05.txt').decode().strip()
        assert trigger == 'seal_git_blob=' + git('rev-parse',f'{TRIGGER}:{sealpath}').decode().strip()
        seal = json.loads(sealbytes)
        assert seal['status'] == 'PRERUN_SEALED_NO_OUTCOME_ACCESS'
        report['seal_sha256'] = sha(sealbytes)
        for key, ent in seal.items():
            if isinstance(ent,dict) and 'git_blob_sha1' in ent:
                p=ent['path']; b=blob(p)
                actual=git('rev-parse',f'{TRIGGER}:{p}').decode().strip()
                assert actual == ent['git_blob_sha1'],key
                assert git('rev-parse',f'HEAD:{p}').decode().strip() == actual,key
                if 'sha256' in ent: assert sha(b)==ent['sha256'],key
                report['files'].append({'path':p,'git_blob':actual,'sha256':sha(b)})
        sources=['locomo_coordinate_scale.py','locomo_spectral_band_haar_causal.py','locomo_sign_mechanism_replication.py','test_coordinate_scale_pure_functions.py']
        src=TMP/'sealed_source'; src.mkdir(parents=True,exist_ok=True)
        for name in sources:
            p='research/v52/'+name; b=blob(p)
            assert git('rev-parse',f'HEAD:{p}')==git('rev-parse',f'{TRIGGER}:{p}')
            (src/name).write_bytes(b)
            report['files'].append({'execution_path':str(src/name),'sha256':sha(b),'git_blob':git('rev-parse',f'{TRIGGER}:{p}').decode().strip()})
        assert git('rev-parse',f'{TRIGGER}:research/v52/locomo_sign_mechanism_replication.py').decode().strip()=='6700454915176854a55b0b5cf6ffe922a22e35f2'
        spec=importlib.util.spec_from_file_location('common',src/'locomo_sign_mechanism_replication.py')
        common=importlib.util.module_from_spec(spec); spec.loader.exec_module(common)
        raw,audit,rows=common.acquire_and_verify(TMP/'preflight_source_bytes')
        convs,corr=common.load_dataset(raw,audit)
        report['data']={'raw_sha256':sha(raw.read_bytes()),'raw_bytes':raw.stat().st_size,'audit_rows':rows,'audit_manifest_sha256':sha(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()),'archives':len(convs),'corrections':len(corr)}
        test=subprocess.run([sys.executable,'-B',str(src/'test_coordinate_scale_pure_functions.py')],capture_output=True,text=True)
        (AUDIT/'pure_function_tests.txt').write_text(test.stdout+test.stderr,encoding='utf-8')
        assert test.returncode==0,'pure tests failed'
        report['status']='READY_FOR_ONE_INVOCATION'
    except Exception as e:
        report['error']=repr(e)
    (AUDIT/'preflight.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
    return 0 if report['status']=='READY_FOR_ONE_INVOCATION' else 1
if __name__=='__main__': sys.exit(main())
