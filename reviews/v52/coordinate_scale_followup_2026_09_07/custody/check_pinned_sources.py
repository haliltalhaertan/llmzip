"""Retrospective Git-byte checks only, not runtime closure certification."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
INSTALL = '59ae1b53d3c4e524621d87a08b396f72a8332816'
TRIGGER = '680b10b8a3ef3dd55a5a05fe47f6fb5fa6d931d0'
RESULT = '591e5d0fd7af8c265ac12a6176761475a19b2f02'
SEAL = 'research/v52/V52_COORDINATE_SCALE_PRERUN_SEAL_2026-09-05.json'

def read(ref, path):
    return subprocess.check_output(['git', 'cat-file', 'blob', ref+':'+path], cwd=ROOT)

def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def check(data, expected):
    if blob(data) != expected:
        raise ValueError('blob mismatch')

def main():
    raw = read(TRIGGER, SEAL)
    seal = json.loads(raw)
    bound = {k:v for k,v in seal.items() if isinstance(v, dict) and 'git_blob_sha1' in v}
    evidence = {'scope':'pinned Git source bytes, no research imports or execution', 'bound':{}, 'extra_sources':{}}
    for key, entry in bound.items():
        for ref in [INSTALL, TRIGGER, RESULT]:
            check(read(ref, entry['path']), entry['git_blob_sha1'])
        evidence['bound'][key] = entry
    assert len(bound) == 10
    assert read(TRIGGER, seal['trigger_path']).decode().strip() == 'seal_git_blob='+blob(raw)
    extra = ['research/v52/locomo_sign_mechanism_replication.py',
             'adapters/longmemeval_v52_adapter.py', 'adapters/longmemeval_v52_adapter_v2.py']
    for path in extra:
        data = read(TRIGGER, path)
        assert data == read(INSTALL,path) == read(RESULT,path)
        evidence['extra_sources'][path] = {'git_blob_sha1':blob(data), 'sha256':hashlib.sha256(data).hexdigest(), 'bytes':len(data), 'unchanged_install_trigger_result':True}
    try:
        check(raw+b'changed', blob(raw))
    except ValueError:
        evidence['mutation_negative_control'] = 'REJECTED'
    else:
        raise AssertionError('negative control unexpectedly accepted')
    evidence['explicit_entries_at_three_commits'] = '30/30 PASS'
    evidence['limitation'] = 'Extra-source hashes are retrospective, not additions to the original seal. Does not certify external dataset bytes, Actions history, third-party closure, or raw retrieval.'
    output = Path(__file__).with_name('RESULTS.json')
    output.write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('30/30 explicit entries PASS; 3/3 extra sources unchanged; mutation REJECTED')

if __name__ == '__main__':
    main()
