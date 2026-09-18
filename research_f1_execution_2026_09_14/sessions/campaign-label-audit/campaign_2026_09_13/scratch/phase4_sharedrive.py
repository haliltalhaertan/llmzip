#!/usr/bin/env python3
"""Phase 4: shared-drive root listing + all drives list. READ-ONLY."""
import json, time, os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOK = os.path.expandvars(r'%LOCALAPPDATA%\hermes\google_token.json')
creds = Credentials.from_authorized_user_file(TOK)
svc = build('drive', 'v3', credentials=creds)
calls = 0
out = {'drives': None, 'shared_root_children': None}

# all shared drives visible to me
calls += 1
drives = svc.drives().list(pageSize=50, fields='drives(id,name),nextPageToken').execute()
out['drives'] = drives.get('drives', [])
print('shared drives:', json.dumps(out['drives'], indent=1))
time.sleep(0.6)

# children of shared drive root
SD = '0AE7zs2LgBcb5Uk9PVA'
calls += 1
resp = svc.files().list(q=f"'{SD}' in parents and trashed = false",
                        fields='nextPageToken, files(id,name,mimeType,size,modifiedTime)',
                        pageSize=200, includeItemsFromAllDrives=True, supportsAllDrives=True,
                        corpora='drive', driveId=SD).execute()
children = resp.get('files', [])
out['shared_root_children'] = children
print(f'\nshared drive {SD} root children: {len(children)}')
for c in children:
    print('  ', c['mimeType'].split('.')[-1], '|', c.get('size'), '|', c['name'][:100], '|', c['id'][:12])
time.sleep(0.6)

# also check my drive root again for comparison count (no, already have)
json.dump(out, open(r'C:\Users\MDP\dev\llmzip-work\scratch\drive_phase4_raw.json', 'w', encoding='utf-8'), indent=1)
print('calls:', calls)
