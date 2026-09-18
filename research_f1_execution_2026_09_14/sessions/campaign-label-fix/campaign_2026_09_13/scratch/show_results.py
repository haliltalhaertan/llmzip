import json
d = json.load(open(r'C:\Users\MDP\dev\llmzip-work\scratch\drive_search_raw.json', encoding='utf-8'))
print('total api calls:', d['api_calls'])
print()
for tag, r in d['queries'].items():
    c = r.get('count', 'ERR')
    print(f'{tag:35s} count={c}  {r.get("error","")}')

def show(tag, maxn=45):
    r = d['queries'].get(tag)
    if not r or 'files' not in r:
        return
    print(f'\n===== {tag} ({r["count"]}) =====')
    for f in r['files'][:maxn]:
        sz = f['size'] or ''
        print('  ', str(sz).rjust(10), f['modifiedTime'][:10] if f['modifiedTime'] else '', f['name'][:130])
    if r['count'] > maxn:
        print('  ... and', r['count'] - maxn, 'more')

for t in ['name~pkl', 'name~PKL', 'name~cache', 'name~CACHE', 'name~cache_repr',
          'name~npy', 'name~npy'.upper(), 'name~npz', 'name~NPZ',
          'name~matrix', 'name~tensor', 'name~emb', 'name~EMB',
          'name~embedding', 'name~EMBEDDING', 'name~representation', 'name~heterogeneity',
          'name~C9', 'name~codes', 'name~queries', 'name~gold', 'name~repr', 'name~sufficient']:
    show(t)
