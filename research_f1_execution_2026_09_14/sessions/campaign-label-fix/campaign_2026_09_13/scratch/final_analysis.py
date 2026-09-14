import json, os
from collections import Counter

SCRATCH = r'C:\Users\MDP\dev\llmzip-work\scratch'
d1 = json.load(open(os.path.join(SCRATCH, 'drive_enum_raw.json'), encoding='utf-8'))
d2 = json.load(open(os.path.join(SCRATCH, 'drive_search_raw.json'), encoding='utf-8'))

master_ids = {fid for fid in d1['folders']}
for o in d1['files']:
    master_ids.add(o['file']['id'])

hits = {}
for tag, r in d2['queries'].items():
    if tag in ('my_drive_root', 'trash_all', 'shared_with_me'):
        continue
    for f in r.get('files', []):
        hits.setdefault(f['id'], f)

print('unique name-sweep hits (all terms):', len(hits))
inside = [f for f in hits.values() if f['id'] in master_ids]
outside = [f for f in hits.values() if f['id'] not in master_ids]
print('inside master tree:', len(inside))
print('outside master tree:', len(outside))

# outside classification via parents/name heuristics
def cls(f):
    nm = f['name']
    if nm.startswith('C0V9') or 'C0V9' in nm or nm.startswith('PHASE_C0V9') or 'c0v9' in nm.lower():
        return 'C0V9 family (PROJECT_AUTOGENESIS)'
    if nm.startswith(('C90', 'C91', 'C907', 'C908', 'C909')):
        return 'C90x/C91x (Riemann/Collatz archives)'
    if nm.startswith('PHASE_B'):
        return 'PHASE_B2B/B3 (PROJECT_AUTOGENESIS)'
    if 'CP20' in nm or 'CP19' in nm:
        return 'CP19/CP20 (Collatz archive)'
    if any(s in nm for s in ['.pyc', 'npy', 'npz', 'pkl', 'matrixlib', 'npysort', 'npyufunc', 'cachecontrol', 'caches', 'golden.json', 'embedding_in_wx3', 'test_repr', 'repr.cpython', 'repr.py', '_char_codes', '_emoji_codes', 'status_codes', 'topobathy', 'jacksboro', 'goog.npz']):
        return 'vendored python env (numpy/matplotlib/...)'
    if nm in ('cache', 'caches', 'cachecontrol'):
        return 'vendored python env (numpy/matplotlib/...)'
    return 'other/unclassified'

c = Counter(cls(f) for f in outside)
for k, v in c.most_common():
    print(f'  {v:3d}  {k}')

print()
print('--- inside-tree candidates (full list) ---')
for f in sorted(inside, key=lambda x: x['name'].lower()):
    print(f"  {str(f.get('size')):>10}  {f['modifiedTime'][:10]}  {f['name']}")

print()
print('--- other/unclassified (full list) ---')
for f in sorted(outside, key=lambda x: x['name'].lower()):
    if cls(f) == 'other/unclassified':
        print(f"  {str(f.get('size')):>10}  {f['modifiedTime'][:10]}  {f['name'][:95]}")

print()
print('--- vendored env: pkl/npy/npz/matrix-named subset ---')
for f in sorted(outside, key=lambda x: x['name'].lower()):
    nm = f['name']
    if any(t in nm.lower() for t in ['pkl', '.npy', '.npz', 'matrix', 'tensor', 'embedding', 'repr']):
        if cls(f) == 'vendored python env (numpy/matplotlib/...)':
            print(f"  {str(f.get('size')):>10}  {nm}")

# term counts table
print()
print('--- term counts ---')
seen_tags = set()
for tag, r in d2['queries'].items():
    base = tag.replace('~', '').split('~')[-1]
    print(f"  {tag:30s} {r.get('count')}")
