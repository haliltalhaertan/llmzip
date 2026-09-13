#!/usr/bin/env python3
"""Phase 2: My Drive root children, trash, sharedWithMe, candidate name sweep. READ-ONLY."""
import json, time, os, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOK = os.path.expandvars(r'%LOCALAPPDATA%\hermes\google_token.json')
OUT = r'C:\Users\MDP\dev\llmzip-work\scratch\drive_search_raw.json'

creds = Credentials.from_authorized_user_file(TOK)
svc = build('drive', 'v3', credentials=creds)

FIELDS = ('nextPageToken, files(id,name,mimeType,modifiedTime,size,md5Checksum,'
          'parents,trashed,owners(emailAddress),shared)')
SLEEP = 0.5
calls = 0

def api_list(q, cap_pages=6):
    global calls
    out, token, pages = [], None, 0
    while True:
        calls += 1
        resp = svc.files().list(q=q, fields=FIELDS, pageSize=200, pageToken=token).execute()
        out.extend(resp.get('files', []))
        token = resp.get('nextPageToken')
        pages += 1
        if not token or pages >= cap_pages:
            break
        time.sleep(SLEEP)
    time.sleep(SLEEP)
    return out

res = {'queries': {}, 'api_calls': 0}

QUERIES = [
    ('my_drive_root', "('root' in parents) and trashed = false"),
    ('trash_all', "trashed = true"),
    ('shared_with_me', "sharedWithMe = true"),
]

TERMS = ['pkl', 'cache', 'cache_repr', 'npy', 'npz', 'matrix', 'tensor', 'emb',
         'embedding', 'representation', 'heterogeneity', 'C9', 'codes', 'queries',
         'gold', 'repr', 'sufficient', 'stat', 'frozen']
for t in TERMS:
    QUERIES.append((f'name~{t}', f"name contains '{t}' and trashed = false"))
    if t.lower() != t.upper():
        u = t.upper()
        QUERIES.append((f'name~{u}', f"name contains '{u}' and trashed = false"))

for tag, q in QUERIES:
    try:
        r = api_list(q)
        res['queries'][tag] = {'q': q, 'count': len(r),
                               'files': [{'id': f.get('id'), 'name': f.get('name'),
                                          'mimeType': f.get('mimeType'), 'size': f.get('size'),
                                          'modifiedTime': f.get('modifiedTime'),
                                          'parents': f.get('parents'),
                                          'owners': [o.get('emailAddress') for o in f.get('owners', [])],
                                          'trashed': f.get('trashed')} for f in r]}
        print(f'{tag:35s} count={len(r)}')
    except Exception as e:
        res['queries'][tag] = {'q': q, 'error': str(e)}
        print(f'{tag:35s} ERROR {e}')

res['api_calls'] = calls
json.dump(res, open(OUT, 'w', encoding='utf-8'), indent=1)
print('api calls phase2:', calls)