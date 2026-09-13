"""Archive integrity/coverage, NOT mathematical certification. Stdlib only."""
from pathlib import Path
import hashlib,json,math
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent
inv=json.loads((ROOT/'SOURCE_INVENTORY.json').read_text())
assert len(inv['completed_workers'])==16
assert (inv['math_workers'],inv['benchmark_workers'],inv['audit_workers'])==(9,4,3)
seen=set()
for rec in inv['records']:
 p=ROOT/rec['path']; assert rec['path'] not in seen; seen.add(rec['path'])
 data=p.read_bytes(); assert len(data)==rec['bytes']; assert hashlib.sha256(data).hexdigest()==rec['sha256'],str(p)
for name,rel in inv['completed_workers'].items():
 for f in ('REPORT.md','COORDINATOR_REVIEW.md'):
  p=ROOT/rel/f; assert p.is_file(); text=p.read_text(encoding='utf-8'); assert all(x in '\n'.join(text.splitlines()[:12]) for x in ('[LOCAL EXPLORATORY PILOT]','[NOT PREREGISTERED]','[NOT FOR CITATION]','[DISCLOSE-BEFORE-USE]')),str(p)
specs={'lme':(470,7050,'qa_id',-0.06443262411347517),'realtalk':(705,10575,'qid',-0.0009360576381852989),'perltqa':(8265,90915,'qid',0.02464151118446995),'locomo':(1535,1535,'qid',-0.025829067783465175)}
counts={}
for name,(n,nrows,key,expected) in specs.items():
 p=ROOT/'theory_benchmark_test_v1'/name/'per_query.jsonl'
 with p.open(encoding='utf-8') as f: rows=[json.loads(x) for x in f]
 assert len(rows)==nrows
 if name=='locomo':
  ids=[x[key] for x in rows]; assert len(ids)==len(set(ids))==n
  diffs=[x['cfg']['LOW48']['4.0']['d_exp']-x['cfg']['LOW48']['0.25']['d_exp'] for x in rows]
 else:
  table={(x[key],x['group'],x['t']):x for x in rows}; assert len(table)==nrows
  ids=sorted({x[key] for x in rows}); assert len(ids)==n
  diffs=[table[(q,'LOW48',4.0)]['delta_exact']-table[(q,'LOW48',0.25)]['delta_exact'] for q in ids]
 effect=math.fsum(diffs)/n; assert abs(effect-expected)<1e-12,(name,effect,expected)
 counts[name]={'QA':n,'physical_table_rows':nrows,'effect_pp':effect*100}
manifest=ROOT/'MANIFEST.sha256'; lines=[x.split(None,1) for x in manifest.read_text().splitlines() if x.strip()]; paths=[]
for digest,rel in lines:
 rel=rel.lstrip('*'); p=REPO/rel; paths.append(rel); assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,rel
assert len(paths)==len(set(paths))
actual={p.relative_to(REPO).as_posix() for p in ROOT.rglob('*') if p.is_file() and p!=manifest}
assert set(paths)==actual,{'missing':list(actual-set(paths)),'extra':list(set(paths)-actual)}
print(json.dumps({'status':'PASS','completed_workers':16,'copied_source_records':len(seen),'manifest_entries':len(paths),'datasets':counts},indent=2))
