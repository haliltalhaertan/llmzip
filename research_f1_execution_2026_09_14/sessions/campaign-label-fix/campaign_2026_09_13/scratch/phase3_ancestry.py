#!/usr/bin/env python3
"""Phase 3: ancestry resolution + classify sibling top-level research folders. READ-ONLY."""
import json, time, os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOK = os.path.expandvars(r'%LOCALAPPDATA%\hermes\google_token.json')
OUT = r'C:\Users\MDP\dev\llmzip-work\scratch\drive_phase3_raw.json'
creds = Credentials.from_authorized_user_file(TOK)
svc = build('drive', 'v3', credentials=creds)
SLEEP = 0.5
calls = 0

def meta(fid):
    global calls
    calls += 1
    m = svc.files().get(fileId=fid, fields='id,name,mimeType,modifiedTime,size,parents,trashed,owners(emailAddress)').execute()
    time.sleep(SLEEP)
    return m

def ancestry(fid, max_depth=12):
    """Return path string walking up parents to drive root."""
    parts = []
    seen = set()
    cur = fid
    for _ in range(max_depth):
        if cur in seen:
            parts.append('[CYCLE]')
            break
        seen.add(cur)
        m = meta(cur)
        parts.append(m.get('name', cur))
        ps = m.get('parents') or []
        if not ps or ps[0] in ('root',):
            break
        cur = ps[0]
    return ' / '.join(reversed(parts)), m

def list1(fid, cap=10):
    global calls
    out, token, pages = [], None, 0
    while True:
        calls += 1
        resp = svc.files().list(q=f"'{fid}' in parents and trashed = false",
                                fields='nextPageToken, files(id,name,mimeType,size,modifiedTime)',
                                pageSize=200, pageToken=token).execute()
        out.extend(resp.get('files', []))
        token = resp.get('nextPageToken')
        pages += 1
        if not token or pages >= cap:
            break
        time.sleep(SLEEP)
    time.sleep(SLEEP)
    return out

res = {'ancestry': {}, 'listings': {}, 'api_calls': 0}

PARENTS = {
    'PHASE_B3_FROZEN_RUN_MATRIX.csv': '1ctFOnrpczo3TmnsFQngCcrbDtLSYStMl',
    'PHASE_B3_FROZEN_RUN_MATRIX_DRAFT.csv': '19jLwl6NYBTlDkhp77mb3Lj2BAevUVr1Q',
    'PHASE_B2B_PERTURBATION_MATRIX.csv': '1ruD61B5Vke6SU_nYNO6IFNTFy1Qf8i71',
    'C909A_THEOREM_TRANSFER_MATRIX.csv': '1S6dBnh0P-msqOGioh7ujKtOSbamXHsBx',
    'CP20_TASK2_SHELL_MATRIX_TABLE.csv': '1y6QynFCffPj63XH1BHMaGLvK4sLmqSlQ',
    'THREE_ENGINE_CONTRACT_MATRIX.csv': '11cZnxc5el2hM8j8t1cfoWgCHgvXJWw3N',
    'astype_copy.pkl': '1UF09ig7rFPSvnmzHnd084s1LVcYHOxDJ',
    'bivariate_normal.npy': '1BVBMpxKWDbRhY1EBROV0g-YDrYQAmuQL',
    'C0V9_RESULTS_zip_parent_probe': '1OYVWe7hv_gihkO_D9ixJCwbChsjpyLpp',
}
for label, pid in PARENTS.items():
    try:
        path, m = ancestry(pid)
        res['ancestry'][label] = {'id': pid, 'path': path, 'name': m.get('name')}
        print(f'{label}\n    -> {path}')
    except Exception as e:
        res['ancestry'][label] = {'id': pid, 'error': str(e)}
        print(label, 'ERR', e)

# Also ancestry of the PHASE_B3 file itself to double-check
try:
    path, m = ancestry('1IE5yQRW-1TwdqHnRzWl5qvjrp7b8q0Gd')
    res['ancestry']['PHASE_B3_FROZEN_RUN_MATRIX.csv:file'] = {'path': path}
    print('PHASE_B3 file ancestry ->', path)
except Exception as e:
    print('B3 file ERR', e)

# Classify sibling research folders: one-level listing
FOLDERS = {
    'FUNCTION_PRESERVING_QUANTIZATION_RESEARCH_CHECKPOINT_2026-08-24': '1e-BJkm9FKJUIJOZmnDybO2DaSGu2dPa5',
    'CP20_PUBLICATION_FACTOR_PRESSURE_V1_2026-09-04': '19y_ZYCGCL8wEn3WkruQOkCuVlxnYwaaE',
    'PROJECT_AUTOGENESIS': '1CLm7sbHoQNGK_SnQkRRaS4GJFh88DGJV',
}
for label, fid in FOLDERS.items():
    try:
        ch = list1(fid)
        res['listings'][label] = {'id': fid, 'count': len(ch),
                                  'children': [{'id': c['id'], 'name': c['name'], 'mimeType': c['mimeType']} for c in ch[:60]]}
        print(f'\n== {label}: {len(ch)} children')
        for c in ch[:25]:
            print('   ', c['mimeType'].split('.')[-1], '|', c['name'][:100])
    except Exception as e:
        print(label, 'ERR', e)

res['api_calls'] = calls
json.dump(res, open(OUT, 'w', encoding='utf-8'), indent=1)
print('\napi calls phase3:', calls)
