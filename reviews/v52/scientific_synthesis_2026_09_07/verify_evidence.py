"""Reconstruct the synthesis source inventory from exact Git objects; no execution."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
SOURCES=[
('canonical_state','a0944522d122cfc3edb36b1d54bca3a1ade6661f','ops/CURRENT_STATE.json'),
('original_review','4769c2a3a6e5770a3a9e9dc77a0029b4792cc34f','reviews/v52/coordinate_scale_review_2026_09_07/REVIEW.md'),
('resolution_proposal','1aa61843135b1ffb5a4590c56f63fe13c4c13a06','reviews/v52/coordinate_scale_followup_2026_09_07/resolution/RESOLUTION_PROPOSAL.md'),
('bootstrap_report','398c2ea4b661bf094afca25d543e96a9e50c615a','reviews/v52/coordinate_scale_uncertainty_2026_09_07/REPORT.md'),
('bootstrap_results','398c2ea4b661bf094afca25d543e96a9e50c615a','reviews/v52/coordinate_scale_uncertainty_2026_09_07/outputs/RESULTS.json'),
('bootstrap_independent_report','a131341392efa71b78b24b375e4bb8997c4d9ab2','reviews/v52/bootstrap_independent_review_2026_09_07/REPORT.md'),
('bootstrap_independent_correction','a131341392efa71b78b24b375e4bb8997c4d9ab2','reviews/v52/bootstrap_independent_review_2026_09_07/CORRECTION.md'),
('reproduction_report','692f599eedeb7e7a649443f24ff507e8c4d1c17d','audit_v52_locomo_reproduction_2026_09_07/REPORT.md'),
('reproduction_comparison','692f599eedeb7e7a649443f24ff507e8c4d1c17d','audit_v52_locomo_reproduction_2026_09_07/comparison.json'),
('reproduction_receipt','692f599eedeb7e7a649443f24ff507e8c4d1c17d','audit_v52_locomo_reproduction_2026_09_07/run_receipt.json')]

def blob(commit,path):
    return subprocess.check_output(['git','cat-file','blob',commit+':'+path],cwd=ROOT)

def check_lock(saved,actual):
    if saved!=actual: raise ValueError('evidence lock mismatch')

def main():
    entries=[]; data={}
    for label,commit,path in SOURCES:
        raw=blob(commit,path)
        data[label]=raw
        entries.append({'label':label,'commit':commit,'path':path,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
                        'git_blob_sha1':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()})
    state=json.loads(data['canonical_state'])
    assert state['task_state']['task_4f1_run']=='BLOCKED'
    assert state['task_state']['retrieval_quality_outcome_access']=='FORBIDDEN'
    comparison=json.loads(data['reproduction_comparison'])
    assert comparison['rows']==92100 and comparison['max_absolute_numeric_difference']==0
    assert comparison['csv_after_crlf_to_lf_equal']
    assert not any(d['path'].startswith('/primary/') for d in comparison['summary_differences'])
    receipt=json.loads(data['reproduction_receipt'])
    assert receipt['returncode']==0 and receipt['invocation_count']==1
    bootstrap=json.loads(data['bootstrap_results'])
    for scheme in bootstrap['schemes'].values():
        for name in ['A_I','B_I']:
            q=scheme['statistics'][name]['percentiles_2_5_50_97_5']
            assert q[0]<0<q[2]
        for name in ['A_full','B_full']:
            q=scheme['statistics'][name]['percentiles_2_5_50_97_5']
            assert q[0]<.7<q[2]
    text=json.dumps({'schema':'SCIENTIFIC_SYNTHESIS_INPUTS_V1','sources':entries},indent=2)+'\n'
    path=HERE/'EVIDENCE_LOCK.json'
    if '--write-lock' in sys.argv:
        if path.exists(): raise SystemExit('refuse overwrite')
        path.write_text(text,encoding='utf-8',newline='\n')
    else:
        check_lock(json.loads(path.read_text()),json.loads(text))
    altered=json.loads(text);altered['sources'][0]['sha256']='0'*64
    try: check_lock(altered,json.loads(text))
    except ValueError: pass
    else: raise AssertionError('changed hash accepted')
    print('10/10 exact source objects PASS; synthesis numeric statements PASS; altered lock REJECTED')

if __name__=='__main__':main()
