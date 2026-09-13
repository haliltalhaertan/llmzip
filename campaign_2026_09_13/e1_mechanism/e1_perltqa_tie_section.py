#!/usr/bin/env python3
"""E1 PerLTQA native-boundary-tie section analysis from verified results.json.

Tests whether the profile/events SIGN-float reversal can be reduced to native Hamming
K=3 boundary-tie incidence. No rescoring or representation rebuild.
"""
from __future__ import annotations
import hashlib,json,math
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

d=json.loads(R.read_text(encoding='utf-8')); per=d['per_q']
rows=[]
for qid,r in per.items():
    rows.append({'qid':qid,'section':r['section'],'char':r['char'],'tie':int(r['tie']),'tie_bc':int(r['tie_bc']),'gap':float(r['gap']),'gold_size':int(r['gold_size']),'delta_pp':100.0*(float(r['native'])-float(r['float']))})
if len(rows)!=8265: raise SystemExit('N_FAIL')
# Gate overall tie rate to committed summary.
if abs(mean([r['tie'] for r in rows])-float(d['ties']['native_tie_rate']))>1e-15: raise SystemExit('TIE_GATE_FAIL')
def groupstats(rr):
    tied=[r for r in rr if r['tie']]; untied=[r for r in rr if not r['tie']]
    return {'n':len(rr),'tie_rate':mean([r['tie'] for r in rr]),'mean_delta_pp':mean([r['delta_pp'] for r in rr]),'delta_tied_pp':mean([r['delta_pp'] for r in tied]),'delta_untied_pp':mean([r['delta_pp'] for r in untied]),'tied_minus_untied_delta_pp':mean([r['delta_pp'] for r in tied])-mean([r['delta_pp'] for r in untied]) if tied and untied else None,'mean_tie_bc':mean([r['tie_bc'] for r in rr]),'mean_gap':mean([r['gap'] for r in rr])}
bysec={s:groupstats([r for r in rows if r['section']==s]) for s in sorted(set(r['section'] for r in rows))}
# Character-level tie rate vs character-level SIGN-float delta, overall and within sections.
def corr_units(group_key, subset=None):
    g=defaultdict(list)
    for r in rows:
        if subset is not None and r['section']!=subset: continue
        g[r[group_key]].append(r)
    units=[{'tie_rate':mean([r['tie'] for r in rr]),'delta_pp':mean([r['delta_pp'] for r in rr])} for rr in g.values()]
    return {'n_units':len(units),'pearson_r':pearson([u['tie_rate'] for u in units],[u['delta_pp'] for u in units]),'spearman_rho':spearman([u['tie_rate'] for u in units],[u['delta_pp'] for u in units])}
out={'schema':'LLMZIP_E1_PERLTQA_TIE_SECTION_V1','label':'[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]','scope':'Native Hamming boundary-tie incidence vs SIGN-minus-float section reversal; committed verified results only.','input':{'results_sha256':sha(R),'overall_native_tie_rate':mean([r['tie'] for r in rows])},'by_section':bysec,'character_level_overall':corr_units('char'),'character_level_within_section':{s:corr_units('char',s) for s in bysec},'interpretation_rule':'A simple tie-rate explanation would require the losing events regime to have materially higher native tie incidence and/or tie-rate changes to track character-level Delta. Failure means aggregate boundary ties are insufficient, though richer strictly-closer/gold-distance tie geometry may still matter.','epistemic_note':'Post-hoc explanatory analysis; tie incidence is not randomly assigned.'}
print(json.dumps(out,indent=2,sort_keys=True))
