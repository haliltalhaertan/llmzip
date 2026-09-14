import json, time, os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

d = json.load(open(r'C:\Users\MDP\dev\llmzip-work\scratch\drive_enum_raw.json', encoding='utf-8'))
d2 = json.load(open(r'C:\Users\MDP\dev\llmzip-work\scratch\drive_search_raw.json', encoding='utf-8'))

# All unique files by name -> id
byid = {}
for o in d['files']:
    f = o['file']
    byid.setdefault(f['id'], f)

print('=== target zip ids from enumeration ===')
targets = ['V52_T4C2_ALL_OUTPUTS.zip', 'V52_T4C2_BINARY_GEOMETRY.zip', 'V52_T1_COMPUTE_INPUT_BUNDLE.zip',
           'LLM_MEMORY_RESEARCH_FULL_ARCHIVE_V51.zip', 'EXTERNAL_LLM_HANDOFF_BUNDLE.zip',
           'V52_T4E0_ALL_OUTPUTS.zip', 'V52_T4F0_ALL_OUTPUTS.zip',
           'V52_LONGMEMEVAL_BOUNDARY_LOCALIZATION_FINAL_2026-09-04.zip',
           'V52_LOCOMO_BOUNDARY_LOCALIZATION_RESULTS_2026-09-04.zip',
           'V52_LONGMEMEVAL_MATCHED_RANDOM_PARTITION_NULL_FINAL_2026-09-04.zip',
           'V52_LOCOMO_MATCHED_RANDOM_PARTITION_NULL_RESULTS_2026-09-04.zip',
           'V52_LONGMEMEVAL_HEAD_TAIL_CAUSAL_FINAL_2026-09-04.zip',
           'V52_LONGMEMEVAL_CAUSAL_SHARDED_FINAL_2026-09-04.zip',
           'V52_LOCOMO_HEAD_TAIL_CAUSAL_RESULTS_2026-09-04.zip',
           'V52_CAUSAL_SPECTRAL_BAND_HAAR_INTERIM_DOUBLE_BACKUP_2026-09-04.zip',
           'V52_LOCOMO_CAUSAL_BAND_HAAR_RESULTS_2026-09-04.zip']
found = {}
for f in byid.values():
    if f['name'] in targets:
        found.setdefault(f['name'], []).append((f['id'], f.get('size'), f['modifiedTime'][:10]))
# find folders for each
folders = {fid: f for fid, f in json.load(open(r'C:\Users\MDP\dev\llmzip-work\scratch\drive_enum_raw.json', encoding='utf-8'))['folders'].items()}
occ = {}
for o in d['files']:
    occ.setdefault(o['file']['id'], []).append(o['folder_path'])
for t in targets:
    for fid, sz, mt in found.get(t, []):
        print(f"{t}\n   id={fid} size={sz} mod={mt} path={occ.get(fid)}")

print()
print('=== C0V9 files from sweep ===')
for tag, r in d2['queries'].items():
    for f in r.get('files', []):
        if f['name'].startswith('C0V9') or 'C0V9' in f['name']:
            print(f"  {f['id']} | {f['name'][:80]} | parents={f.get('parents')}")

# ancestry of C0V9 parent + PHASE_C0V9 zips
creds = Credentials.from_authorized_user_file(os.path.expandvars(r'%LOCALAPPDATA%\hermes\google_token.json'))
svc = build('drive', 'v3', credentials=creds)
calls = 0
def meta(fid):
    global calls
    calls += 1
    m = svc.files().get(fileId=fid, fields='id,name,mimeType,size,parents').execute()
    time.sleep(0.5)
    return m

def ancestry(fid, max_depth=12):
    parts, seen, cur = [], set(), fid
    for _ in range(max_depth):
        if cur in seen: parts.append('[CYCLE]'); break
        seen.add(cur)
        m = meta(cur)
        parts.append(m.get('name', cur))
        ps = m.get('parents') or []
        if not ps or ps[0] == 'root':
            break
        cur = ps[0]
    return ' / '.join(reversed(parts))

# resolve ancestry for first C0V9 file and the two PHASE_C0V9 zips
c0v9_probe = None
for tag, r in d2['queries'].items():
    for f in r.get('files', []):
        if f['name'] == 'C0V9_POSITIVE_CONTROL_FAILURE_VERIFY_001_RESULTS.zip':
            c0v9_probe = f['id']
print()
if c0v9_probe:
    print('C0V9_RESULTS.zip ancestry ->', ancestry(c0v9_probe))
for zid, nm in [('1_lF9qwH8ShVUGqPgIdvBWV3xatLCyJA1', 'PHASE_C0V9_PREINTERACTION_PROGRESS_CHECKPOINT_2026-08-22.zip')]:
    print(nm, 'ancestry ->', ancestry(zid))
print('calls used:', calls)
