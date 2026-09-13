#!/usr/bin/env python3
import json,re,pickle
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/data/e1v2_raw_audit/raw')
_ALLOWED={('numpy._core.multiarray','_reconstruct'),('numpy.core.multiarray','_reconstruct'),('numpy','ndarray'),('numpy','dtype'),('numpy._core.numeric','_frombuffer'),('numpy.core.numeric','_frombuffer'),('numpy._core.multiarray','scalar'),('numpy.core.multiarray','scalar')}
class RU(pickle.Unpickler):
 def find_class(self,m,n):
  if (m,n) in _ALLOWED:
   mod=__import__(m,fromlist=[n]);return getattr(mod,n)
  raise pickle.UnpicklingError

def load(p):
 with open(p,'rb') as f:return RU(f).load()
def norm(x):
 if x is None:return []
 if isinstance(x,str):
  z=re.findall(r'D\d+:\d+',x);return z if z else [x]
 out=[]
 if isinstance(x,(list,tuple)):
  for y in x:
   if isinstance(y,str):
    z=re.findall(r'D\d+:\d+',y);out += z if z else [y]
   elif isinstance(y,dict):
    q=y.get('dia_id') or y.get('id')
    if q:out.append(str(q))
 return list(dict.fromkeys(out))
def corrections():
 d={}
 for p in (ROOT/'drive/audit_layer').glob('errors_conv_*.json'):
  for r in json.loads(p.read_text()):
   if r.get('question_id'):d[str(r['question_id'])]=('correct_evidence'in r,norm(r.get('correct_evidence')))
 return d
def pris(ci,n):return np.vstack([np.random.default_rng(5_100_000+ci*100_000+t*100+99).random(n) for t in range(20)])
def score(d,gold,P):
 d=np.asarray(d);g=np.unique(np.asarray(gold,int));kth=np.partition(d,2)[2];s=np.flatnonzero(d<kth);tied=np.flatnonzero(d==kth);need=3-len(s);mask=np.zeros(len(d),bool);mask[g]=1;h0=mask[s].sum();hits=[]
 if need==0:hits=[h0]*20
 else:
  sel=np.argsort(P[:,tied],axis=1,kind='stable')[:,:need]
  for j in range(20):hits.append(h0+mask[tied[sel[j]]].sum())
 h=np.asarray(hits,float);return np.mean(h/len(g)),np.mean(h>0),np.mean(h==len(g))
def cosine(C,q):return -((C@q)/(np.linalg.norm(C,axis=1)*np.linalg.norm(q)))
corr=corrections(); vals={'audit_sign':[],'audit_float':[],'raw_sign':[],'raw_float':[]}; changed=0; comparable_changed=0
for ci,p in enumerate(sorted((ROOT/'regen/locomo').glob('locomo_*.pkl'))):
 o=load(p);C=np.asarray(o['C'],float);B=C>=0;P=pris(ci,len(C));id2=o['id_to_row']
 for qi,qa in enumerate(o['qas']):
  qid=str(qa['question_id']);raw=norm(qa.get('raw_evidence'));z=corr.get(qid);clean=z[1] if z and z[0] else raw
  if clean!=raw:changed+=1
  rg=list(dict.fromkeys(id2[x] for x in raw if x in id2));ag=list(dict.fromkeys(id2[x] for x in clean if x in id2));q=np.asarray(o['QC'][qi],float);dn=np.count_nonzero(B!=(q>=0)[None,:],axis=1);df=cosine(C,q)
  if ag:
   vals['audit_sign'].append(score(dn,ag,P));vals['audit_float'].append(score(df,ag,P))
  if rg:
   vals['raw_sign'].append(score(dn,rg,P));vals['raw_float'].append(score(df,rg,P))
  if ag and rg and ag!=rg:comparable_changed+=1
res={'changed_evidence_q':changed,'changed_comparable_q':comparable_changed}
for k,arr in vals.items():
 a=np.asarray(arr,float);res[k]={'n':len(arr),'fractional':float(a[:,0].mean()),'any':float(a[:,1].mean()),'all':float(a[:,2].mean())}
for mode in ['audit','raw']:
 res[mode+'_delta_pp']={m:100*(res[mode+'_sign'][m]-res[mode+'_float'][m]) for m in ['fractional','any','all']}
Path('/mnt/data/e1v2_raw_audit/postlead/LOCOMO_VARIANTS.json').write_text(json.dumps(res,indent=2,sort_keys=True));print(json.dumps(res,indent=2))
