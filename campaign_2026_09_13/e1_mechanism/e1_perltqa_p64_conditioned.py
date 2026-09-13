#!/usr/bin/env python3
"""Condition E1 PerLTQA P64-vs-Delta association on native K=3 boundary tie status.

No representation rebuild or rescoring. This tests whether the P64 marker is merely a
by-product of native Hamming boundary ties.
"""
from __future__ import annotations
import hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
R=ROOT/'campaign_2026_09_13/bench3/b3b_perltqa/results.json'
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
def stats(rr):
    x=[r['p64'] for r in rr]; y=[r['delta_pp'] for r in rr]; nz=[(a,b) for a,b in zip(x,y) if a!=0 and b!=0]
    return {'n':len(rr),'mean_p64':mean(x),'mean_delta_pp':mean(y),'pearson_r':pearson(x,y),'spearman_rho':spearman(x,y),'same_sign_fraction_nonzero':sum((a>0)==(b>0) for a,b in nz)/len(nz) if nz else None,'n_nonzero_both':len(nz)}
d=json.loads(R.read_text(encoding='utf-8'))
rows=[]
for qid,r in d['per_q'].items():
    rows.append({'section':r['section'],'tie':int(r['tie']),'delta_pp':100.0*(float(r['native'])-float(r['float'])),'p64':float(r['BOT64'])-float(r['TOP64'])})
out={'schema':'LLMZIP_E1_PERLTQA_P64_TIE_CONDITIONED_V1','label':'[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]','input':{'results_sha256':sha(R)},'overall':{'untied':stats([r for r in rows if not r['tie']]),'tied':stats([r for r in rows if r['tie']])},'by_section':{},'interpretation_rule':'If positive P64-vs-Delta association and profile/events P64 sign separation persist among untied questions, P64 is not merely a boundary-tie artifact.','epistemic_note':'Post-hoc conditioning on an observed retrieval property; explanatory only.'}
for s in sorted(set(r['section'] for r in rows)):
    rr=[r for r in rows if r['section']==s]
    out['by_section'][s]={'untied':stats([r for r in rr if not r['tie']]),'tied':stats([r for r in rr if r['tie']])}
print(json.dumps(out,indent=2,sort_keys=True))
