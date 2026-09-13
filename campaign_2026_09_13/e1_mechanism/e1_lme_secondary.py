#!/usr/bin/env python3
"""E1 secondary LME analysis using only already-committed accepted surfaces.

No representation rebuild. Joins canonical T4C2 per-question outcomes to the
certified-regeneration Task1 archive geometry by question_id and prints JSON.
"""
from __future__ import annotations
import csv, hashlib, json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
Q=ROOT/'docs/v52/task4c2/V52_T4C2_question_level.csv'
G=ROOT/'campaign_2026_09_13/regen/lme/task1_extension_lme.json'


def sha256(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def ranks(x):
    order=sorted(range(len(x)),key=lambda i:x[i]); out=[0.0]*len(x); j=0
    while j<len(order):
        k=j+1
        while k<len(order) and x[order[k]]==x[order[j]]: k+=1
        avg=(j+1+k)/2.0
        for t in range(j,k): out[order[t]]=avg
        j=k
    return out

def pearson(x,y):
    mx=sum(x)/len(x); my=sum(y)/len(y)
    dx=[a-mx for a in x]; dy=[b-my for b in y]
    den=math.sqrt(sum(a*a for a in dx)*sum(b*b for b in dy))
    return sum(a*b for a,b in zip(dx,dy))/den if den else None

def spearman(x,y): return pearson(ranks(x),ranks(y))

def mean(x): return sum(x)/len(x) if x else None

qrows={}
with Q.open(newline='',encoding='utf-8') as f:
    for r in csv.DictReader(f):
        qrows[r['question_id']]={
          'delta_pp':float(r['sign_minus_centered_float_fractional_pp']),
          'question_type':r['question_type'],
          'N_csv':int(r['N_archive']),
        }
g=json.loads(G.read_text(encoding='utf-8'))
geom={r['question_id']:r for r in g['archives']}
if set(qrows)!=set(geom):
    raise SystemExit(f'JOIN_COVERAGE_FAIL q={len(qrows)} g={len(geom)} only_q={len(set(qrows)-set(geom))} only_g={len(set(geom)-set(qrows))}')
rows=[]
for qid in sorted(qrows):
    q=qrows[qid]; a=geom[qid]
    if q['N_csv']!=a['N']: raise SystemExit(f'N_MISMATCH {qid}')
    rows.append({**q,'question_id':qid,
      'cv_sigma':float(a['cv_sigma']),
      'top32_share':float(a['top32_share']),
      'corr_off_mass':float(a['corr_off_mass']),
      'corr_median_abs':float(a['corr_median_abs']),
      'corr_p95_abs':float(a['corr_p95_abs']),
      'sign_entropy':float(a['sign_entropy_gt']),
      'N':int(a['N'])})
metrics=['cv_sigma','top32_share','corr_off_mass','corr_median_abs','corr_p95_abs','sign_entropy','N']
y=[r['delta_pp'] for r in rows]
cor={m:{'pearson_r':pearson([r[m] for r in rows],y),'spearman_rho':spearman([r[m] for r in rows],y)} for m in metrics}
pos=[r for r in rows if r['delta_pp']>0]; neg=[r for r in rows if r['delta_pp']<0]; zero=[r for r in rows if r['delta_pp']==0]
groups={}
for m in metrics:
    groups[m]={'positive_delta_mean':mean([r[m] for r in pos]),'negative_delta_mean':mean([r[m] for r in neg]),'zero_delta_mean':mean([r[m] for r in zero])}
bytype={}
for qt in sorted(set(r['question_type'] for r in rows)):
    rr=[r for r in rows if r['question_type']==qt]
    bytype[qt]={'n':len(rr),'mean_delta_pp':mean([r['delta_pp'] for r in rr])}
out={
 'schema':'LLMZIP_E1_LME_SECONDARY_V1',
 'label':'[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]',
 'scope':'Secondary E1 analysis from pre-existing committed surfaces; no raw-cache E1 run.',
 'inputs':{'question_level_sha256':sha256(Q),'task1_extension_sha256':sha256(G)},
 'n':len(rows),'join_exact':True,'delta_mean_pp':mean(y),
 'delta_counts':{'positive':len(pos),'zero':len(zero),'negative':len(neg)},
 'correlations':cor,'geometry_by_delta_sign':groups,'question_type_summary':bytype,
 'epistemic_note':'Post-hoc/exploratory. task1 geometry predates E1; outcome and geometry were not generated for this correlation test. Correlation is not causal evidence.'
}
print(json.dumps(out,sort_keys=True,indent=2))
