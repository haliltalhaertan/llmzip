#!/usr/bin/env python3
"""E1 LME joint retrieval-polarity test from sealed race per-question arrays.

Primary E1-V2 quantity for LME: P64_q = FR(BOT64)-FR(TOP64), compared with
Delta_q = FR(SIGN96)-FR(centered-float96). P48 is sensitivity only.
No representation rebuild or rescoring occurs.
"""
from __future__ import annotations
import csv, hashlib, json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
R=ROOT/'campaign_2026_09_13/race/rb2/race_sign_details.json'
Q=ROOT/'docs/v52/task4c2/V52_T4C2_question_level.csv'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
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
    mx=sum(x)/len(x); my=sum(y)/len(y); a=[v-mx for v in x]; b=[v-my for v in y]
    den=math.sqrt(sum(v*v for v in a)*sum(v*v for v in b))
    return sum(u*v for u,v in zip(a,b))/den if den else None
def spearman(x,y): return pearson(ranks(x),ranks(y))
def mean(x): return sum(x)/len(x) if x else None

def find_arm(obj,name,n):
    hits=[]
    def walk(x,path):
        if isinstance(x,dict):
            if name in x and isinstance(x[name],dict):
                v=x[name]
                fr=v.get('fr')
                if isinstance(fr,list) and len(fr)==n:
                    hits.append((path+(name,),v))
            for k,v in x.items(): walk(v,path+(str(k),))
        elif isinstance(x,list):
            for i,v in enumerate(x):
                if isinstance(v,(dict,list)): walk(v,path+(str(i),))
    walk(obj,())
    if len(hits)!=1:
        raise SystemExit(f'ARM_PATH_FAIL {name} hits={[(p,len(v.get("fr",[]))) for p,v in hits]}')
    return hits[0]

d=json.loads(R.read_text(encoding='utf-8'))
lme=d['LME']; qids=[str(x) for x in lme['qids']]; n=len(qids)
if n!=470 or len(set(qids))!=470: raise SystemExit(f'QID_FAIL {n}')
arms={}
paths={}
for name in ['NATIVE96','TOP48','BOT48','TOP64','BOT64']:
    path,val=find_arm(lme,name,n); paths[name]='/'.join(path); arms[name]=[float(x) for x in val['fr']]
q={}
with Q.open(newline='',encoding='utf-8') as f:
    for r in csv.DictReader(f):
        q[r['question_id']]={'delta':float(r['sign_minus_centered_float_fractional_pp']),'type':r['question_type'],'native':float(r['sign96_centered_fractional_r3'])}
if set(qids)!=set(q): raise SystemExit('QID_COVERAGE_FAIL')
# Verify sealed NATIVE per-q array equals canonical question-level native values.
max_native=max(abs(arms['NATIVE96'][i]-q[qid]['native']) for i,qid in enumerate(qids))
if max_native>1e-15: raise SystemExit(f'NATIVE_PERQ_MISMATCH {max_native}')
rows=[]
for i,qid in enumerate(qids):
    p64=arms['BOT64'][i]-arms['TOP64'][i]
    p48=arms['BOT48'][i]-arms['TOP48'][i]
    rows.append({'qid':qid,'type':q[qid]['type'],'delta_pp':q[qid]['delta'],'p64':p64,'p48':p48})
y=[r['delta_pp'] for r in rows]

def stats(rr,key):
    x=[r[key] for r in rr]; yy=[r['delta_pp'] for r in rr]
    return {'n':len(rr),'mean_p':mean(x),'mean_delta_pp':mean(yy),'pearson_r':pearson(x,yy),'spearman_rho':spearman(x,yy),'same_sign_fraction':sum((a>0)==(b>0) for a,b in zip(x,yy) if a!=0 and b!=0)/max(1,sum(a!=0 and b!=0 for a,b in zip(x,yy)))}
out={'schema':'LLMZIP_E1_LME_JOINT_POLARITY_V1','label':'[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]',
 'scope':'Joint TOP/BOT retrieval polarity from already-sealed race per-question arrays; no representation rebuild or rescoring.',
 'inputs':{'race_details_sha256':sha(R),'question_level_sha256':sha(Q),'arm_paths':paths,'native_perq_max_abs_diff':max_native},
 'primary_P64':stats(rows,'p64'),'sensitivity_P48':stats(rows,'p48'),'by_question_type':{},
 'prediction':'E1 V2 primary A predicts positive Spearman rho(Delta_q, P64_q).',
 'epistemic_note':'Mechanism validation on an already-observed benchmark, not pristine discovery. Per-question arrays predate E1.'}
for qt in sorted(set(r['type'] for r in rows)):
    rr=[r for r in rows if r['type']==qt]
    out['by_question_type'][qt]={'P64':stats(rr,'p64'),'P48':stats(rr,'p48')}
print(json.dumps(out,indent=2,sort_keys=True))
