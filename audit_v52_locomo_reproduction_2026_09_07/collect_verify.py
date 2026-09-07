"""Post-run verification and derived-artifact collection; no fitting/ranking."""
import hashlib, json, pathlib, shutil, subprocess, sys
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parent
TMP=ROOT.parent/'locomo_reproduction_tmp_20260907'
def main():
    receipt=json.loads((HERE/'run_receipt.json').read_bytes())
    assert receipt['invocation_count']==1
    assert receipt['status']=='COMPLETED', 'No success claims after failed invocation'
    gate=json.loads((HERE/'preflight.json').read_bytes())
    out=TMP/'reproduction_output'
    source=out/'source_bytes'
    rows=[]
    expected=[{'file':'locomo10.json','bytes':gate['data']['raw_bytes'],'sha256':gate['data']['raw_sha256']}]+[dict(r,file='audit/'+r['file']) for r in gate['data']['audit_rows']]
    for entry in expected:
        p=source/entry['file']; raw=p.read_bytes()
        actual={'file':entry['file'],'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        assert actual==entry,actual
        rows.append(actual)
    (HERE/'actual_source_identity.json').write_text(json.dumps({'status':'PASS','files':rows},indent=2),encoding='utf-8')
    dest=HERE/'reproduced_outputs'; dest.mkdir(exist_ok=False)
    for name in ['locomo_scale_per_question.csv.gz','locomo_scale_summary.json']:
        shutil.copyfile(out/name,dest/name)
        assert (out/name).read_bytes()==(dest/name).read_bytes()
    proc=subprocess.run([sys.executable,str(HERE/'compare.py'),str(ROOT/'research/v52/locomo_scale_outputs/locomo_scale_per_question.csv.gz'),str(dest/'locomo_scale_per_question.csv.gz'),str(HERE/'comparison.json')],capture_output=True,text=True)
    (HERE/'comparison_stdout_stderr.txt').write_text(proc.stdout+proc.stderr,encoding='utf-8')
    print(proc.stdout+proc.stderr)
    assert proc.returncode==0,'comparison structure failed'
    result=json.loads((HERE/'comparison.json').read_bytes())
    assert result['numeric_within_1e_12'],'comparison numerical mismatch: retain and stop'
if __name__=='__main__': main()
