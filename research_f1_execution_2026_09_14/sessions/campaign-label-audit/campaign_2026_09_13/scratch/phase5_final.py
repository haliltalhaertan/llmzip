#!/usr/bin/env python3
"""Final phase 5: extra name searches + shared folder '1' listing. READ-ONLY."""
import json, time, os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOK = os.path.expandvars(r'%LOCALAPPDATA%\hermes\google_token.json')
creds = Credentials.from_authorized_user_file(TOK)
svc = build('drive', 'v3', credentials=creds)
calls = 0

def list_q(q, cap=4):
    global calls
    out, token, pages = [], None, 0
    while True:
        calls += 1
        resp = svc.files().list(q=q, fields='nextPageToken, files(id,name,mimeType,size,modifiedTime,parents)',
                                pageSize=200, pageToken=token).execute()
        out.extend(resp.get('files', []))
        token = resp.get('nextPageToken')
        pages += 1
        if not token or pages >= cap:
            break
        time.sleep(0.5)
    time.sleep(0.5)
    return out

res = {}
for t in ['C96', 'mixed96', 'cache_results', 'Frozen_Representation', 'fitted', 'npz']:
    r = list_q(f"name contains '{t}' and trashed = false")
    res['term_' + t] = r
    print(f"term {t!r}: {len(r)} -> {[f['name'][:70] for f in r[:8]]}")

# shared folder '1' from sarabrain513
sh = list_q("'1OYVWe7hv_gihkO_D9ixJCwbChsjpyLpp' in parents and trashed = false", cap=2)
res['shared_folder_1_children'] = [{'id': f['id'], 'name': f['name'], 'mimeType': f['mimeType'], 'size': f.get('size')} for f in sh]
print(f'\nshared folder "1" children: {len(sh)}')
for f in sh[:30]:
    print('  ', f['mimeType'].split('.')[-1], '|', f.get('size'), '|', f['name'][:90])

json.dump(res, open(r'C:\Users\MDP\dev\llmzip-work\scratch\drive_phase5_raw.json', 'w', encoding='utf-8'), indent=1)
print('calls:', calls)
