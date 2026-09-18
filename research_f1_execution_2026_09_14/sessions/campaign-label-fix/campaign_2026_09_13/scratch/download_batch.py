#!/usr/bin/env python3
"""Download batch: READ-ONLY fetch of candidate files. Usage: python download_batch.py manifest.json"""
import json, time, os, sys, io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

TOK = os.path.expandvars(r'%LOCALAPPDATA%\hermes\google_token.json')
DEST = r'C:\Users\MDP\dev\llmzip-work\drive'
creds = Credentials.from_authorized_user_file(TOK)
svc = build('drive', 'v3', credentials=creds)
calls = 0

def dl(fid, outname):
    global calls
    out = os.path.join(DEST, outname)
    if os.path.exists(out):
        print('SKIP exists:', outname); return
    calls += 1
    m = svc.files().get(fileId=fid, fields='id,name,mimeType,size').execute()
    mt = m['mimeType']
    time.sleep(0.4)
    if mt.startswith('application/vnd.google-apps'):
        export_map = {'application/vnd.google-apps.document': 'text/plain',
                      'application/vnd.google-apps.spreadsheet': 'text/csv'}
        emt = export_map.get(mt, 'application/pdf')
        calls += 1
        data = svc.files().export(fileId=fid, mimeType=emt).execute()
        open(out, 'wb').write(data)
        print(f'EXPORTED {outname} ({mt} -> {emt}, {len(data)} bytes)')
    else:
        calls += 1
        fh = io.FileIO(out, 'wb')
        dlr = MediaIoBaseDownload(fh, svc.files().get_media(fileId=fid), chunksize=10*1024*1024)
        done = False
        while not done:
            status, done = dlr.next_chunk()
        fh.close()
        print(f'DOWNLOADED {outname} ({os.path.getsize(out)} bytes)')
    time.sleep(0.4)

manifest = json.load(open(sys.argv[1], encoding='utf-8'))
for fid, outname in manifest:
    try:
        dl(fid, outname)
    except Exception as e:
        print('ERR', outname, repr(e))
print('calls:', calls)
