#!/usr/bin/env python3
import json, time, os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file(os.path.expandvars(r'%LOCALAPPDATA%\hermes\google_token.json'))
svc = build('drive', 'v3', credentials=creds)
calls = 0
for t in ['locomo10', 'longmemeval']:
    calls += 1
    r = svc.files().list(q=f"name contains '{t}' and trashed = false",
                         fields='nextPageToken, files(id,name,mimeType,size,modifiedTime,parents)',
                         pageSize=200).execute()
    fs = r.get('files', [])
    print(f"term {t!r}: {len(fs)}")
    for f in fs:
        print('   ', str(f.get('size')).rjust(12), f['id'][:12], '|', f['name'][:90], '| parents:', f.get('parents'))
    time.sleep(0.6)

# key ids from enumeration
d1 = json.load(open(r'C:\Users\MDP\dev\llmzip-work\scratch\drive_enum_raw.json', encoding='utf-8'))
uniq = {}
for o in d1['files']:
    uniq.setdefault(o['file']['id'], o['file'])
print()
for nm in ['V52_T4C3_native_heterogeneity.csv', 'V52_T4C3_rotated_heterogeneity.csv',
           'V52_T4C3_ALL_OUTPUTS.zip', 'V52_T4D_ALL_OUTPUTS.zip', 'V52_T4C3_heterogeneity_quintiles.csv',
           'V52_T4C3_heterogeneity_alignment.csv', 'v52_t4c3_coordinate_axis_probe.py']:
    for fid, f in uniq.items():
        if f['name'] == nm:
            parent = (f.get('parents') or [''])[0]
            print(f"{nm}: id={fid} size={f.get('size')} parent={parent}")
print('calls:', calls)
