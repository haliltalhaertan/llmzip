#!/usr/bin/env python3
"""E1 post-hoc regime decomposition.

Question: do aggregate P64/Delta correlations survive after holding semantic section/category fixed?
Uses only already-committed per-QA outputs; no representation rebuild or rescoring.
"""
from __future__ import annotations
import json, math, hashlib
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'campaign_2026_09_13/bench3/b3b_perltqa/results.json'
R=ROOT/'campaign_2026_09_13/bench3/b3a_realtalk/details.json'

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
    return {'n_units':len(rows),'pearson_r':pearson(x,y),'spearman_rho':spearman(x,y),'same_sign_fraction_nonzero':sum((a>0)==(b>0) for a,b in nz)/len(nz) if nz else None,'n_nonzero_both':len(nz),'mean_p64':mean(x),'mean_delta_pp':mean(y)}

# PerLTQA character x section aggregates.
p=json.loads(P.read_text(encoding='utf-8'))['per_q']
g=defaultdict(list)
for qid,r in p.items():
    g[(r['section'],r['char'])].append({'delta_pp':100.0*(float(r['native'])-float(r['float'])),'p64':float(r['BOT64'])-float(r['TOP64'])})
psec={}
for sec in sorted({k[0] for k in g}):
    rows=[]
    for (s,char),rr in sorted(g.items()):
        if s!=sec: continue
        rows.append({'unit':char,'n_q':len(rr),'delta_pp':mean([x['delta_pp'] for x in rr]),'p64':mean([x['p64'] for x in rr])})
    psec[sec]=stats(rows)
    psec[sec]['n_q_total']=sum(r['n_q'] for r in rows)

# REALTALK chat x category aggregates, valid only.
r=json.loads(R.read_text(encoding='utf-8'))
g=defaultdict(list)
for q in r['per_qa']:
    if not int(q['valid']): continue
    a=q['arms']; g[(int(q['cat']),str(q['chat']))].append({'delta_pp':100.0*(float(a['NATIVE96'])-float(a['FLOAT96'])),'p64':float(a['BOT64'])-float(a['TOP64'])})
rcat={}
for cat in sorted({k[0] for k in g}):
    rows=[]
    for (c,chat),rr in sorted(g.items()):
        if c!=cat: continue
        rows.append({'unit':chat,'n_q':len(rr),'delta_pp':mean([x['delta_pp'] for x in rr]),'p64':mean([x['p64'] for x in rr])})
    rcat[str(cat)]=stats(rows); rcat[str(cat)]['n_q_total']=sum(x['n_q'] for x in rows)

out={'schema':'LLMZIP_E1_REGIME_DECOMPOSE_V1','label':'[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]','scope':'Post-hoc archive-unit correlations after holding semantic section/category fixed; committed outputs only.','inputs':{'perltqa_results_sha256':sha(P),'realtalk_details_sha256':sha(R)},'perltqa_character_within_section':psec,'realtalk_chat_within_category':rcat,'interpretation_rule':'If archive-unit correlation remains positive within semantic strata, archive regime contributes beyond section/category composition. If it collapses within strata, semantic task type is the stronger regime marker.','epistemic_note':'Post-hoc decomposition; small numbers of archives/chats and no confirmatory inference.'}
print(json.dumps(out,indent=2,sort_keys=True))
