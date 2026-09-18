import json
d = json.load(open(r'C:\Users\MDP\dev\llmzip-work\scratch\drive_search_raw.json', encoding='utf-8'))
print('===== my_drive_root (top level) =====')
for f in d['queries']['my_drive_root']['files']:
    print(' ', f['id'], '|', f['mimeType'].split('.')[-1], '|', f['name'])
print()
print('===== trash =====')
for f in d['queries']['trash_all']['files']:
    print(' ', f.get('id'), '|', f['mimeType'].split('.')[-1], '|', f['name'], '| size', f.get('size'))
print()
print('===== shared_with_me =====')
for f in d['queries']['shared_with_me']['files']:
    print(' ', f['id'], '|', f['mimeType'].split('.')[-1], '|', f['name'], '| owner', f.get('owners'))

# classify interesting hits: which parents
interesting = ['PHASE_B3_FROZEN_RUN_MATRIX.csv', 'PHASE_B3_FROZEN_RUN_MATRIX_DRAFT.csv',
               'PHASE_B3_RUN_MATRIX_VALIDATION_DRAFT.json', 'PHASE_B2B_PERTURBATION_MATRIX.csv',
               'C909A_THEOREM_TRANSFER_MATRIX.csv', 'golden.json', 'bivariate_normal.npy',
               'astype_copy.pkl', 'generator_pcg64_np126.pkl.gz', 'topobathy.npz',
               'CP20_TASK2_SHELL_MATRIX_TABLE.csv', 'THREE_ENGINE_CONTRACT_MATRIX.csv']
seen = {}
for tag, r in d['queries'].items():
    for f in r.get('files', []):
        if f['name'] in interesting and f['name'] not in seen:
            seen[f['name']] = f
for nm in interesting:
    f = seen.get(nm)
    if f:
        print(f"{nm:45s} parents={f.get('parents')} id={f['id']} size={f.get('size')}")
    else:
        print(f'{nm:45s} (not found in sweep)')