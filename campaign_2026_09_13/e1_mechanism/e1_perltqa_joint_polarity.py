#!/usr/bin/env python3
"""E1 PerLTQA joint retrieval-polarity test from verified B3B per-QA results.

No representation rebuild or rescoring. Reads the byte-verified results.json produced by
step2_eval.py and compares Delta_q=native-float with P64_q=BOT64-TOP64.
"""
from __future__ import annotations
import hashlib, json, math
from collections import defaultdict
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
def stats(rows):
    x=[r['p64'] for r in rows]; y=[r['delta_pp'] for r in rows]
    nz=[(a,b) for a,b in zip(x,y) if a!=0 and b!=0]
    return {
      'n':len(rows),'mean_p64':mean(x),'mean_delta_pp':mean(y),
      'pearson_r':pearson(x,y),'spearman_rho':spearman(x,y),
      'same_sign_fraction_nonzero':(sum((a>0)==(b>0) for a,b in nz)/len(nz)) if nz else None,
      'n_nonzero_both':len(nz),
    }

d=json.loads(R.read_text(encoding='utf-8'))
per=d['per_q']
if len(per)!=8265: raise SystemExit(f'N_FAIL {len(per)}')
rows=[]
for qid,r in per.items():
    for key in ('native','float','BOT64','TOP64','section','char'):
        if key not in r: raise SystemExit(f'MISSING {qid} {key}')
    rows.append({'qid':qid,'section':r['section'],'char':r['char'],
      'delta_pp':100.0*(float(r['native'])-float(r['float'])),
      'p64':float(r['BOT64'])-float(r['TOP64'])})
# Gate against committed aggregate/by_section numbers in the same verified file.
agg_delta=100.0*(float(d['aggregate']['native']['mean'])-float(d['aggregate']['float']['mean']))
if abs(mean([r['delta_pp'] for r in rows])-agg_delta)>1e-12: raise SystemExit('AGG_DELTA_GATE_FAIL')
if abs(mean([r['p64'] for r in rows])-(float(d['aggregate']['BOT64']['mean'])-float(d['aggregate']['TOP64']['mean'])))>1e-12: raise SystemExit('AGG_P64_GATE_FAIL')
bysec={}
for sec in sorted({r['section'] for r in rows}):
    rr=[r for r in rows if r['section']==sec]
    s=stats(rr)
    expected_delta=100.0*(float(d['by_section'][sec]['native']['mean'])-float(d['by_section'][sec]['float']['mean']))
    expected_p=float(d['by_section'][sec]['BOT64']['mean'])-float(d['by_section'][sec]['TOP64']['mean'])
    if abs(s['mean_delta_pp']-expected_delta)>1e-12: raise SystemExit(f'SEC_DELTA_GATE_FAIL {sec}')
    if abs(s['mean_p64']-expected_p)>1e-12: raise SystemExit(f'SEC_P_GATE_FAIL {sec}')
    bysec[sec]=s
# Archive/character regime aggregation.
bychar_rows=[]
g=defaultdict(list)
for r in rows: g[r['char']].append(r)
for char,rr in sorted(g.items()):
    bychar_rows.append({'char':char,'delta_pp':mean([r['delta_pp'] for r in rr]),'p64':mean([r['p64'] for r in rr])})
char_stats=stats(bychar_rows)
# Section means as four regime points; explicitly descriptive, not independent confirmatory units.
sec_rows=[{'delta_pp':v['mean_delta_pp'],'p64':v['mean_p64']} for v in bysec.values()]
sec_regime=stats(sec_rows)
out={
 'schema':'LLMZIP_E1_PERLTQA_JOINT_POLARITY_V1',
 'label':'[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]',
 'scope':'Joint TOP64/BOT64 retrieval polarity from verified PerLTQA B3B per-QA outputs; no representation rebuild or rescoring.',
 'input':{'results_sha256':sha(R),'n_qa':len(rows),'n_char':len(bychar_rows)},
 'overall':stats(rows),'by_section':bysec,'by_character':char_stats,'section_regime_descriptive':sec_regime,
 'prediction':'E1 V2 predicts positive rho(Delta_q,P64_q); if within-section effects are weak while section means align, treat P64 as a regime-level marker rather than an individual-query law.',
 'epistemic_note':'PerLTQA outcome was already observed before E1. Sections share data-generating structure and are not independent confirmatory units.'}
print(json.dumps(out,indent=2,sort_keys=True))
