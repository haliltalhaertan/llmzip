#!/usr/bin/env python3
"""Build deliverables: drive_inventory.csv (+ print stats for the MD report)."""
import json, os, csv
from collections import OrderedDict

SCRATCH = r'C:\Users\MDP\dev\llmzip-work\scratch'
REPORTS = r'C:\Users\MDP\dev\llmzip-work\reports'
os.makedirs(REPORTS, exist_ok=True)

d1 = json.load(open(os.path.join(SCRATCH, 'drive_enum_raw.json'), encoding='utf-8'))
d2 = json.load(open(os.path.join(SCRATCH, 'drive_search_raw.json'), encoding='utf-8'))
d5 = json.load(open(os.path.join(SCRATCH, 'drive_phase5_raw.json'), encoding='utf-8'))

MASTER = '1uM2bLBC3XQmvbdkTpjhvR6_N6OO7Qyxv'
C4C3 = '1S03jlMp_wZFD3Mon2ZGvFkt64yBsl9eb'
C4C2 = '1wDpyMSL'  # 4C2 folder id prefix, full id below from folders

folders = d1['folders']

# --- canonical folder paths (fix the 4 root entries that were overwritten by seeding) ---
CANON = {}
for fid, f in folders.items():
    CANON[fid] = f['path']
CANON[MASTER] = 'LLM_TOKEN_ZIP_RESEARCH_MASTER'
CANON['1u1sYaFav17j7i5-3Nd6RrOvRpWy8juZF'] = 'LLM_TOKEN_ZIP_RESEARCH_MASTER/V52_TASK_4D_LOCOMO_FROZEN_CROSS_BENCHMARK_REPLICATION_2026-08-29'
CANON['17JSHz_64KvKIJwzEPshUuwgld8Smczht'] = 'LLM_TOKEN_ZIP_RESEARCH_MASTER/V52_CAUSAL_SPECTRAL_BAND_HAAR_2026-09-04'
CANON['1ABFEBsp7KfNxtIRkdaqU-6ImTFbsXAnv'] = 'LLM_TOKEN_ZIP_RESEARCH_MASTER/V52_TASK_4C3_COORDINATE_AXIS_CAUSAL_PROBE/FINAL_2026-08-28_FULL_470'

# sanity: folder parent paths exist
for fid in list(CANON):
    parent = None
    if fid in folders:
        parent = None
# we don't have parents for all folders in `folders`, but paths are already canonical from master walk

def folder_parent_path(fid):
    p = CANON.get(fid, '')
    if '/' in p:
        return p.rsplit('/', 1)[0]
    return '(My Drive root)'

rows = []   # (folder_path, name, id, mimeType, size, modifiedTime)
seen_ids = set()

def add(scope_path, name, fid, mime, size, mod):
    if fid in seen_ids:
        return
    seen_ids.add(fid)
    rows.append((scope_path, name, fid, mime, str(size) if size not in (None, '') else '', mod or ''))

# 1) master-tree folders
for fid, f in folders.items():
    add(folder_parent_path(fid), f['name'], fid, 'application/vnd.google-apps.folder', '', '')

# 2) master-tree files, canonical path from real parent
uniq_files = {}
for o in d1['files']:
    f = o['file']
    uniq_files.setdefault(f['id'], f)
dual = 0
for o in d1['files']:
    pass
pathset = {}
for o in d1['files']:
    pathset.setdefault(o['file']['id'], set()).add(o['folder_path'])
dual = sum(1 for v in pathset.values() if len(v) > 1)

for fid, f in uniq_files.items():
    parent = (f.get('parents') or [''])[0]
    fp = CANON.get(parent, '(unknown)')
    add(fp, f['name'], fid, f['mimeType'], f.get('size'), f['modifiedTime'])

# 3) top-level My Drive items
for f in d2['queries']['my_drive_root']['files']:
    add('(My Drive root)', f['name'], f['id'], f['mimeType'], f.get('size'), f.get('modifiedTime'))

# 4) trash
for f in d2['queries']['trash_all']['files']:
    add('(Trash)', f['name'], f['id'], f['mimeType'], f.get('size'), f.get('modifiedTime'))

# 5) outside classified files
outside = {}
# collect C0V9-family from all sweeps
for tag, r in d2['queries'].items():
    for f in r.get('files', []):
        nm = f['name']
        if 'C0V9' in nm:
            outside[f['id']] = f
resolved = {
    # C0V9 results set (all in same RESULTS folder)
    '15Hd-LMFcMuhwM9H-RJAcXTzjsiL992Bo': 'PROJECT_AUTOGENESIS/CURRENT_RESEARCH_2026_08_25/C0V9_POSITIVE_CONTROL_FAILURE_VERIFY_001/RESULTS',
}
for fid, f in outside.items():
    par = (f.get('parents') or [''])[0]
    fp = resolved.get(par, '(outside llmzip tree)')
    add(fp, f['name'], fid, f['mimeType'], f.get('size'), f.get('modifiedTime'))

extra = [
    ('PROJECT_AUTOGENESIS/02_PHASES/11_PHASE_B3/02_FROZEN_PREPRODUCTION_CHECKPOINT_2026-08-16', 'PHASE_B3_FROZEN_RUN_MATRIX.csv', '1IE5yQRW-1TwdqHnRzWl5qvjrp7b8q0Gd', 'text/csv', '3892430', '2026-08-16'),
    ('PROJECT_AUTOGENESIS/02_PHASES/11_PHASE_B3/00_PREREGISTRATION_DRAFT_2026-08-16', 'PHASE_B3_FROZEN_RUN_MATRIX_DRAFT.csv', '1O31523rKjLfBYFN89xzDCPbUaWlFD8ZV', 'text/csv', '3892430', '2026-08-16'),
    ('PROJECT_AUTOGENESIS/02_PHASES/11_PHASE_B3/00_PREREGISTRATION_DRAFT_2026-08-16', 'PHASE_B3_RUN_MATRIX_VALIDATION_DRAFT.json', '1vj98ZxRbNbpTBHjHATnddQDkh0-kKxZu', 'application/json', '618', '2026-08-16'),
    ('PROJECT_AUTOGENESIS/02_PHASES/06_PHASE_B2B_ORIGINAL', 'PHASE_B2B_PERTURBATION_MATRIX.csv', '1uShpCCFMWSDeAnClCc4O3JguspQzL_TM', 'text/csv', '193385', '2026-08-15'),
    ('Riemann Hipotezi — Araştırma Arşivi/02_COMPUTATION', 'C909A_THEOREM_TRANSFER_MATRIX.csv', '1acvk7JCGHb4OvyY_6eFZL6hTL_N0zKBG', 'text/csv', '1144', '2026-08-16'),
    ('Collatz Problemi — Araştırma Arşivi/CP20/Task 2 — Superlinear State-Growth Barrier/RESULTS_AND_ALL_ARTIFACTS/ALL_ARTIFACTS', 'CP20_TASK2_SHELL_MATRIX_TABLE.csv', '1PMaJLo07VeETWMRb1X4V8XXmZ_0rbWc4', 'text/csv', '2469', '2026-08-26'),
    ('PROJECT_AUTOGENESIS/CURRENT_RESEARCH_2026_08_25/ENGINE_RETENTION_SUPPORT_EQUIVALENCE_VERIFY_001/RESULTS', 'THREE_ENGINE_CONTRACT_MATRIX.csv', '1-3j9JQC4593gZ3fRb4kvJGepOJeKuBZC', 'text/csv', '592', '2026-08-25'),
    ('autogenesis-meta/.venv/Lib/site-packages/numpy/_core/tests/data', 'astype_copy.pkl', '1RXUKuUPD-a_PiPzC7GiM-Ey1iI9-scNI', 'application/octet-stream', '716', '2026-08-20'),
    ('autogenesis-meta/.venv/Lib/site-packages/numpy/random/tests/data', 'generator_pcg64_np126.pkl.gz', '1o3zHZXS8UtkwUNdYBKFKCpAWZRYpk12h', 'application/gzip', '208', '2026-08-20'),
    ('autogenesis-meta/.venv/Lib/site-packages/matplotlib/mpl-data/sample_data/axes_grid', 'bivariate_normal.npy', '1KlVgH1Z56EsUgByjd8QyBzhZejZnyA5O', 'application/octet-stream', '1880', '2026-08-20'),
    ('autogenesis-meta/.venv (numpy sample data)', 'topobathy.npz', '1wAZzK5XmaIXWp4rdkQR6szqZpusWahs_', 'application/octet-stream', '45224', '2026-08-20'),
    ('(shared by sarabrain513@gmail.com)', '1 (folder)', '1OYVWe7hv_gihkO_D9ixJCwbChsjpyLpp', 'application/vnd.google-apps.folder', '', ''),
    ('(shared by sarabrain513@gmail.com)', 'Stellaris Galaxy Edition.(v.3.14.15)-Oyunindirvip.zip', None, 'application/x-zip-compressed', '7082271855', ''),
]
for fp, nm, fid, mime, size, mod in extra:
    if fid is None:
        rows.append((fp, nm, '', mime, size, mod))
    else:
        add(fp, nm, fid, mime, size, mod)

# dedupe exact (folder_path,id) and sort
rows = list(OrderedDict.fromkeys(rows))
rows.sort(key=lambda r: (r[0], r[1].lower()))

out_csv = os.path.join(REPORTS, 'drive_inventory.csv')
with open(out_csv, 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh)
    w.writerow(['folder_path', 'name', 'id', 'mimeType', 'size', 'modifiedTime'])
    for r in rows:
        w.writerow(r)

# stats
total_bytes = sum(int(f.get('size') or 0) for f in uniq_files.values())
per_folder = {}
for fid, f in uniq_files.items():
    parent = (f.get('parents') or [''])[0]
    fp = CANON.get(parent, '(unknown)')
    per_folder[fp] = per_folder.get(fp, 0) + 1
print('CSV rows:', len(rows))
print('unique master-tree files:', len(uniq_files))
print('dual-path files (occurrence artifacts):', dual)
print('master-tree total bytes:', total_bytes)
print('files per folder:')
for k in sorted(per_folder):
    print(f'  {per_folder[k]:3d}  {k}')
print()
print('longmemeval files:')
for f in uniq_files.values():
    if 'longmemeval_s_cleaned' in f['name']:
        parent = (f.get('parents') or [''])[0]
        print('  ', CANON.get(parent), '|', f['name'], '|', f.get('size'), '|', f['id'])
print('locomo10.json:')
for f in uniq_files.values():
    if f['name'] == 'locomo10.json':
        parent = (f.get('parents') or [''])[0]
        print('  ', CANON.get(parent), '|', f.get('size'), '|', f['id'])
print('out_csv:', out_csv)
print('outside rows added:', len(outside), 'c0v9-family; extras:', len(extra))
