#!/usr/bin/env python3
"""Phase 1: recursive Drive enumeration of llmzip project roots. READ-ONLY."""
import json, time, os, sys
from collections import deque
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOK = os.path.expandvars(r'%LOCALAPPDATA%\hermes\google_token.json')
OUT = r'C:\Users\MDP\dev\llmzip-work\scratch\drive_enum_raw.json'

creds = Credentials.from_authorized_user_file(TOK)
svc = build('drive', 'v3', credentials=creds)

FIELDS = ('nextPageToken, files(id,name,mimeType,modifiedTime,size,md5Checksum,'
          'parents,trashed,createdTime,owners(emailAddress),'
          'shortcutDetails(targetId,targetMimeType),shared)')
SLEEP = 0.4
calls = 0

def api_list(q, cap_pages=20):
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

def meta(fid):
    global calls
    calls += 1
    m = svc.files().get(fileId=fid, fields='id,name,mimeType,modifiedTime,size,parents,trashed,owners(emailAddress)').execute()
    time.sleep(SLEEP)
    return m

ROOTS = [
    '1uM2bLBC3XQmvbdkTpjhvR6_N6OO7Qyxv',
    '1u1sYaFav17j7i5-3Nd6RrOvRpWy8juZF',
    '1ABFEBsp7KfNxtIRkdaqU-6ImTFbsXAnv',
    '17JSHz_64KvKIJwzEPshUuwgld8Smczht',
]

FOLDER_MIME = 'application/vnd.google-apps.folder'
data = {'roots': {}, 'folders': {}, 'files': [], 'api_calls': 0}

for r in ROOTS:
    try:
        data['roots'][r] = meta(r)
    except Exception as e:
        data['roots'][r] = {'error': str(e)}

visited_folders = set()
folders = {}
occ = []

for r in ROOTS:
    rn = data['roots'][r].get('name', r)
    folders[r] = {'name': rn, 'path': rn, 'root': r}
    visited_folders.add(r)
    q = deque([(r, rn)])
    while q:
        fid, path = q.popleft()
        try:
            children = api_list(f"'{fid}' in parents and trashed = false")
        except Exception as e:
            print('ERR listing', fid, path, e)
            continue
        for f in children:
            if f['mimeType'] == FOLDER_MIME:
                if f['id'] not in visited_folders:
                    visited_folders.add(f['id'])
                    sp = path + '/' + f['name']
                    folders[f['id']] = {'name': f['name'], 'path': sp, 'root': r}
                    q.append((f['id'], sp))
                else:
                    if f['id'] in folders:
                        folders[f['id']].setdefault('alt_paths', []).append(path + '/' + f['name'])
            else:
                occ.append({'folder_path': path, 'folder_id': fid, 'file': f})

data['folders'] = folders
data['files'] = occ
data['api_calls'] = calls
json.dump(data, open(OUT, 'w', encoding='utf-8'), indent=1)
print('roots:', {k: v.get('name') for k, v in data['roots'].items()})
print('folders visited:', len(visited_folders))
print('file occurrences:', len(occ))
print('unique file ids:', len({o['file']['id'] for o in occ}))
print('api calls phase1:', calls)