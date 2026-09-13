#!/usr/bin/env python3
"""E1 REALTALK joint retrieval-polarity test from committed B3A per-QA outputs.

No representation rebuild or rescoring. Uses valid QA rows only, matching B3A summary semantics.
"""
from __future__ import annotations
import hashlib,json,math
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'campaign_2026_09_13/bench3/b3a_realtalk/details.json'
S=ROOT/'campaign_2026_09_13/bench3/b3a_realtalk/rt_summary.json'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def mean(x): return sum(x)/len(x) if x else None
def ranks(x):
    o=sorted(range(len(x)),key=lambda i:x[i]); r=[0.0]*len(x); j=0
    while j<len(o):
        k=j+1
        while k<len(o) and x[o[k]]==x[o[j]]: k+=1
        a=(j+1+k)/2.0
        for t in range(j,k): r[o[t]]=a
        j=k
    return r
def pearson(x,y):
    mx=mean(x); my=mean(y); a=[v-mx for v in x]; b=[v-my for v in y]
    den=math.sqrt(sum(v*v for v in a)*sum(v*v for v in b))
    return sum(u*v for u,v in zip(a,b))/den if den else None
def spearman(x,y): return pearson(ranks(x),ranks(y))
def stats(rows):
    x=[r['p64'] for r in rows]; y=[r['delta_pp'] for r in rows]
    nz=[(a,b) for a,b in zip(x,y) if a!=0 and b!=0]
    return {'n':len(rows),'mean_p64':mean(x),'mean_delta_pp':mean(y),'pearson_r':pearson(x,y),'spearman_rho':spearman(x,y),'same_sign_fraction_nonzero':sum((a>0)==(b>0) for a,b in nz)/len(nz) if nz else None,'n_nonzero_both':len(nz)}

d=json.loads(D.read_text(encoding='utf-8')); s=json.loads(S.read_text(encoding='utf-8'))
valid=[r for r in d['per_qa'] if int(r['valid'])==1]
if len(valid)!=705 or int(d['n_valid'])!=705 or int(s['n_valid'])!=705: raise SystemExit('N_GATE_FAIL')
rows=[]
for r in valid:
    a=r['arms']
    for k in ('NATIVE96','FLOAT96','BOT64','TOP64'):
        if a.get(k) is None: raise SystemExit(f'MISSING_ARM {r["qid"]} {k}')
    rows.append({'qid':r['qid'],'chat':str(r['chat']),'cat':int(r['cat']),'delta_pp':100.0*(float(a['NATIVE96'])-float(a['FLOAT96'])),'p64':float(a['BOT64'])-float(a['TOP64'])})
# Aggregate gates against committed summary.
exp_delta=100.0*(float(s['arm_means']['NATIVE96'])-float(s['arm_means']['FLOAT96']))
exp_p=float(s['arm_means']['BOT64'])-float(s['arm_means']['TOP64'])
if abs(mean([r['delta_pp'] for r in rows])-exp_delta)>1e-12: raise SystemExit('DELTA_GATE_FAIL')
if abs(mean([r['p64'] for r in rows])-exp_p)>1e-12: raise SystemExit('P64_GATE_FAIL')
bycat={}
for c in sorted(set(r['cat'] for r in rows)):
    rr=[r for r in rows if r['cat']==c]; bycat[str(c)]=stats(rr)
# Chat aggregation.
g=defaultdict(list)
for r in rows: g[r['chat']].append(r)
chat_rows=[{'delta_pp':mean([r['delta_pp'] for r in rr]),'p64':mean([r['p64'] for r in rr])} for _,rr in sorted(g.items())]
out={'schema':'LLMZIP_E1_REALTALK_JOINT_POLARITY_V1','label':'[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]','scope':'Joint TOP64/BOT64 retrieval polarity from committed REALTALK B3A per-QA outputs; no representation rebuild or rescoring.','inputs':{'details_sha256':sha(D),'summary_sha256':sha(S),'n_valid':len(rows),'n_chat':len(chat_rows)},'overall':stats(rows),'by_category':bycat,'by_chat':stats(chat_rows),'prediction':'E1 V2 predicts positive rho(Delta_q,P64_q); aggregation-level strengthening would support a regime marker rather than a per-query law.','epistemic_note':'REALTALK outcome was observed before E1. Chat/category aggregation is descriptive.'}
print(json.dumps(out,indent=2,sort_keys=True))
