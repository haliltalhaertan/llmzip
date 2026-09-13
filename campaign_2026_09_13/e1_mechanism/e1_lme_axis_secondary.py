#!/usr/bin/env python3
"""Gold-informed E1 secondary mechanism analysis on the pre-existing 470x96 per-axis discrimination matrix.

No representation rebuild. This is explanatory only: the per-axis discrimination matrix uses gold labels and is not a deployable feature surface.
"""
from __future__ import annotations
import csv,json,math,hashlib
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
NPZ=ROOT/'campaign_2026_09_13/pilots_round1/per_axis_matrices.npz'
Q=ROOT/'docs/v52/task4c2/V52_T4C2_question_level.csv'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def ranks(x):
    order=sorted(range(len(x)),key=lambda i:x[i]); r=[0.0]*len(x); j=0
    while j<len(order):
        k=j+1
        while k<len(order) and x[order[k]]==x[order[j]]: k+=1
        a=(j+1+k)/2
        for t in range(j,k): r[order[t]]=a
        j=k
    return r
def pearson(x,y):
    mx=sum(x)/len(x); my=sum(y)/len(y); a=[v-mx for v in x]; b=[v-my for v in y]
    den=math.sqrt(sum(v*v for v in a)*sum(v*v for v in b))
    return sum(u*v for u,v in zip(a,b))/den if den else None
def spearman(x,y): return pearson(ranks(x),ranks(y))

d=np.load(NPZ,allow_pickle=False)
keys=sorted(d.files)
if 'delta' not in d or 'qids' not in d: raise SystemExit(f'NPZ_KEYS_FAIL {keys}')
D=np.asarray(d['delta'],dtype=np.float64); qids=[str(x) for x in d['qids']]
if D.shape!=(470,96) or len(qids)!=470: raise SystemExit(f'SHAPE_FAIL {D.shape} {len(qids)}')
qout={}
with Q.open(newline='',encoding='utf-8') as f:
    for r in csv.DictReader(f): qout[r['question_id']]=float(r['sign_minus_centered_float_fractional_pp'])
if set(qids)!=set(qout): raise SystemExit('QID_COVERAGE_FAIL')
rows=[]
for i,qid in enumerate(qids):
    x=D[i]; pos=np.maximum(x,0.0); neg=-np.minimum(x,0.0); ps=float(pos.sum()); p2=float(np.sum(pos*pos))
    order=np.sort(pos)[::-1]
    rows.append({
      'qid':qid,'delta_pp':qout[qid],
      'axis_delta_sum':float(x.sum()),'axis_delta_abs_sum':float(np.abs(x).sum()),
      'positive_mass':ps,'negative_mass':float(neg.sum()),
      'n_positive_axes':int(np.sum(x>0)),'n_negative_axes':int(np.sum(x<0)),
      'positive_effdim':float(ps*ps/p2) if p2>0 else None,
      'positive_top32_share':float(order[:32].sum()/ps) if ps>0 else None,
      'positive_top16_share':float(order[:16].sum()/ps) if ps>0 else None,
    })
metrics=['axis_delta_sum','axis_delta_abs_sum','positive_mass','negative_mass','n_positive_axes','n_negative_axes','positive_effdim','positive_top32_share','positive_top16_share']
y=[r['delta_pp'] for r in rows]
cor={}
for m in metrics:
    rr=[r for r in rows if r[m] is not None]
    x=[r[m] for r in rr]; yy=[r['delta_pp'] for r in rr]
    cor[m]={'n':len(rr),'pearson_r':pearson(x,yy),'spearman_rho':spearman(x,yy)}
out={
 'schema':'LLMZIP_E1_LME_AXIS_SECONDARY_V1',
 'label':'[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]',
 'scope':'Gold-informed explanatory analysis of pre-existing per-axis discrimination matrix; not deployable, not confirmatory.',
 'inputs':{'npz_sha256':sha(NPZ),'question_level_sha256':sha(Q),'npz_keys':keys,'delta_shape':list(D.shape)},
 'n':len(rows),'delta_mean_pp':sum(y)/len(y),'correlations':cor,
 'interpretation':'Tests whether concentration/distribution of marginal gold-vs-nongold axis signal tracks SIGN-minus-float advantage. This is distinct from archive variance concentration and from joint sign-bit redundancy.',
 'epistemic_note':'Post-hoc, gold-informed mechanism probe. No causal or deployment claim.'
}
print(json.dumps(out,indent=2,sort_keys=True))
