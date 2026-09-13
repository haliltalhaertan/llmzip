#!/usr/bin/env python3
"""E1 contextual-axis secondary probe using pre-existing round-1 NPZ.

Gold-informed explanatory analysis only. `alone` measures one-bit retrieval FR;
`native - drop` measures one-axis contextual contribution inside the full 96-bit code.
TOP/BOT are defined by the pre-existing per-question archive variance ranks.
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

d=np.load(NPZ,allow_pickle=False)
alone=np.asarray(d['alone'],float); drop=np.asarray(d['drop'],float); vr=np.asarray(d['var_rank'],int); qids=[str(x) for x in d['qids']]
if alone.shape!=(470,96) or drop.shape!=(470,96) or vr.shape!=(470,96): raise SystemExit('SHAPE_FAIL')
qout={}
with Q.open(newline='',encoding='utf-8') as f:
    for r in csv.DictReader(f):
        qout[r['question_id']]={'native':float(r['sign96_centered_fractional_r3']),'delta_pp':float(r['sign_minus_centered_float_fractional_pp'])}
if set(qids)!=set(qout): raise SystemExit('QID_COVERAGE_FAIL')
rows=[]
for i,qid in enumerate(qids):
    top=vr[i] < 48; bot=vr[i] >= 48
    if int(top.sum())!=48 or int(bot.sum())!=48: raise SystemExit(f'RANK_SPLIT_FAIL {qid}')
    native=qout[qid]['native']; loss=native-drop[i]
    at=float(alone[i,top].mean()); ab=float(alone[i,bot].mean())
    lt=float(loss[top].mean()); lb=float(loss[bot].mean())
    rows.append({'qid':qid,'delta_pp':qout[qid]['delta_pp'],
      'alone_top_mean':at,'alone_bot_mean':ab,'alone_bot_minus_top':ab-at,
      'drop_loss_top_mean':lt,'drop_loss_bot_mean':lb,'drop_loss_bot_minus_top':lb-lt,
      'drop_positive_top':int(np.sum(loss[top]>0)),'drop_positive_bot':int(np.sum(loss[bot]>0)),
      'drop_negative_top':int(np.sum(loss[top]<0)),'drop_negative_bot':int(np.sum(loss[bot]<0))})
metrics=['alone_top_mean','alone_bot_mean','alone_bot_minus_top','drop_loss_top_mean','drop_loss_bot_mean','drop_loss_bot_minus_top','drop_positive_top','drop_positive_bot','drop_negative_top','drop_negative_bot']
y=[r['delta_pp'] for r in rows]
cor={m:{'pearson_r':pearson([r[m] for r in rows],y),'spearman_rho':spearman([r[m] for r in rows],y)} for m in metrics}
pos=[r for r in rows if r['delta_pp']>0]; neg=[r for r in rows if r['delta_pp']<0]; zero=[r for r in rows if r['delta_pp']==0]
out={'schema':'LLMZIP_E1_LME_CONTEXTUAL_AXIS_V1','label':'[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]',
 'scope':'Gold-informed contextual axis-importance probe from pre-existing NPZ. No representation rebuild.',
 'inputs':{'npz_sha256':sha(NPZ),'question_level_sha256':sha(Q)},'n':len(rows),'correlations':cor,
 'aggregate_means':{m:mean([r[m] for r in rows]) for m in metrics},
 'by_delta_sign':{g:{m:mean([r[m] for r in rr]) for m in metrics} for g,rr in [('positive',pos),('zero',zero),('negative',neg)]},
 'predicted_direction':'Spearman(delta_pp, drop_loss_bot_minus_top) > 0 under the complementarity hypothesis. alone_bot_minus_top is expected to be <=0 overall and is a discriminating control.',
 'epistemic_note':'Post-hoc and gold-informed. Mechanism-only, not deployable or causal.'}
print(json.dumps(out,indent=2,sort_keys=True))
