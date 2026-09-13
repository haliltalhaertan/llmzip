#!/usr/bin/env python3
import re,json,pickle,hashlib
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.stats import rankdata
ROOT=Path('/mnt/data/e1v2_raw_audit/raw')
ST=Path('/mnt/data/e1v2_raw_audit/independent_stage1')
OUT=Path('/mnt/data/e1v2_raw_audit/postlead'); OUT.mkdir(exist_ok=True)
_ALLOWED={('numpy._core.multiarray','_reconstruct'),('numpy.core.multiarray','_reconstruct'),('numpy','ndarray'),('numpy','dtype'),('numpy._core.numeric','_frombuffer'),('numpy.core.numeric','_frombuffer'),('numpy._core.multiarray','scalar'),('numpy.core.multiarray','scalar')}
class RU(pickle.Unpickler):
 def find_class(self,m,n):
  if (m,n) in _ALLOWED:
   mod=__import__(m,fromlist=[n]); return getattr(mod,n)
  raise pickle.UnpicklingError(f'blocked {m}.{n}')
def load(p):
 with open(p,'rb') as f:return RU(f).load()
def rho(x,y):
 x=np.asarray(x,float);y=np.asarray(y,float);ok=np.isfinite(x)&np.isfinite(y);x=x[ok];y=y[ok]
 if len(x)<2:return None
 rx=rankdata(x,method='average');ry=rankdata(y,method='average')
 if np.std(rx)==0 or np.std(ry)==0:return None
 return float(np.corrcoef(rx,ry)[0,1])
def norm_evidence(x):
 if x is None:return []
 if isinstance(x,str):
  z=re.findall(r'D\d+:\d+',x);return z if z else [x]
 out=[]
 if isinstance(x,(list,tuple)):
  for y in x:
   if isinstance(y,str):
    z=re.findall(r'D\d+:\d+',y);out.extend(z if z else [y])
   elif isinstance(y,dict):
    q=y.get('dia_id') or y.get('id')
    if q:out.append(str(q))
 return list(dict.fromkeys(out))
def corrections():
 out={}
 for p in sorted((ROOT/'drive/audit_layer').glob('errors_conv_*.json')):
  rows=json.loads(p.read_text())
  for r in rows:
   qid=r.get('question_id')
   if qid:out[str(qid)]={'has':'correct_evidence'in r,'ev':norm_evidence(r.get('correct_evidence'))}
 return out
def rows_evid(ids,m):return list(dict.fromkeys(int(m[x]) for x in ids if x in m))
def topbot(C):
 v=np.mean(np.asarray(C,float)**2,axis=0); order=np.argsort(v,kind='stable')[::-1];return order[:64],order[-64:]
def metrics(d,gold):
 gold=np.unique(np.asarray(gold,int)); n=len(d); non=np.ones(n,bool);non[gold]=False
 ns=[];nt=[];as_=[];at=[]
 for g in gold:
  dg=d[g]
  ns.append(np.count_nonzero(non&(d<dg)));nt.append(np.count_nonzero(non&(d==dg)))
  as_.append(np.count_nonzero(d<dg));at.append(np.count_nonzero(d==dg))
 dmin=np.min(d[gold])
 return {'pg_non_strict':float(np.mean(ns)),'pg_non_tie':float(np.mean(nt)),'pg_all_strict':float(np.mean(as_)),'pg_all_tie':float(np.mean(at)),'min_all_strict':float(np.count_nonzero(d<dmin)),'min_all_tie':float(np.count_nonzero(d==dmin)),'gold_n':int(len(gold))}
def calc(C,q,gold):
 C=np.asarray(C,float);q=np.asarray(q,float);B=C>=0;qb=q>=0;t,b=topbot(C)
 dt=np.count_nonzero(B[:,t]!=qb[t][None,:],axis=1); db=np.count_nonzero(B[:,b]!=qb[b][None,:],axis=1)
 a=metrics(dt,gold);c=metrics(db,gold); out={'gold_n':a['gold_n']}
 for k in a:
  if k!='gold_n': out[k+'_gap']=a[k]-c[k]
 return out
stage=json.loads((ST/'INDEPENDENT_QUERY_ROWS.json').read_text()); delta={bn:{r['qid']:r['delta'] for r in rows} for bn,rows in stage.items()}
out=defaultdict(list)
for p in sorted((ROOT/'regen/lme/cache_repr').glob('*.pkl')):
 o=load(p);qid=str(o['question_id']);m=calc(o['C'],o['qC'],o['gold']);m['qid']=qid;m['delta']=delta['LME'][qid];out['LME'].append(m)
for p in sorted((ROOT/'bench3/runs/b3a_realtalk/rt_repr').glob('RT*.pkl')):
 o=load(p)
 for qi,qid in enumerate(o['qids']):
  gold=np.asarray(o['gold_rows'][qi],int)
  if not len(gold):continue
  qid=str(qid);m=calc(o['C'],o['QC'][qi],gold);m['qid']=qid;m['delta']=delta['REALTALK'][qid];m['cluster']=str(o['chat_no']);out['REALTALK'].append(m)
arch=load(ROOT/'bench3/runs/b3b_perltqa/cache_arch_eval.pkl'); qdat=load(ROOT/'bench3/runs/b3b_perltqa/cache_q_eval.pkl')
for qid,q in qdat.items():
 qid=str(qid);m=calc(arch[q['char']]['C'],q['qC'],q['gold']);m['qid']=qid;m['delta']=delta['PERLTQA'][qid];m['section']=str(q['section']);m['cluster']=str(q['char']);out['PERLTQA'].append(m)
corr=corrections()
for p in sorted((ROOT/'regen/locomo').glob('locomo_*.pkl')):
 o=load(p);id2=o['id_to_row']
 for qi,qa in enumerate(o['qas']):
  qid=str(qa['question_id']); raw=norm_evidence(qa.get('raw_evidence')); z=corr.get(qid); clean=z['ev'] if z and z['has'] else raw; gold=rows_evid(clean,id2)
  if not gold:continue
  m=calc(o['C'],o['QC'][qi],gold);m['qid']=qid;m['delta']=delta['LOCOMO'][qid];m['cluster']=str(o['conv_id']);out['LOCOMO'].append(m)
keys=['pg_non_strict_gap','pg_non_tie_gap','pg_all_strict_gap','pg_all_tie_gap','min_all_strict_gap','min_all_tie_gap']
summary={}
for bn,rows in out.items():
 s={'n':len(rows),'multi_gold_n':sum(r['gold_n']>1 for r in rows),'multi_gold_rate':sum(r['gold_n']>1 for r in rows)/len(rows),'rho':{k:rho([r['delta'] for r in rows],[r[k] for r in rows]) for k in keys}}
 if bn=='PERLTQA':
  secs={}
  for sec in sorted(set(r['section'] for r in rows)):
   rr=[r for r in rows if r['section']==sec];secs[sec]={'n':len(rr),'multi_gold_n':sum(r['gold_n']>1 for r in rr),'multi_gold_rate':sum(r['gold_n']>1 for r in rr)/len(rr),'rho':{k:rho([r['delta'] for r in rr],[r[k] for r in rr]) for k in keys}}
  s['sections']=secs
 summary[bn]=s
(OUT/'COMPETITION_VARIANTS.json').write_text(json.dumps({'summary':summary,'rows':out},indent=2,sort_keys=True))
print(json.dumps(summary,indent=2,sort_keys=True))
