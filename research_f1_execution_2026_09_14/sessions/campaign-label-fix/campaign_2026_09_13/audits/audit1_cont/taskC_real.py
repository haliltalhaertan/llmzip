#!/usr/bin/env python3
"""[LOCAL AUDIT] Task C-real: mirror rb2/race_sign.py EXACTLY for arms NATIVE96, SPREAD80, RAND80_s2, BOT80, TOP48 x LME(470)+LoCoMo(1535). Compute per-gold a,t_excl and pess/exp/opt means; validate exp vs official per-q fr."""
import json, pickle, re, csv
from pathlib import Path
import numpy as np
ROOT = Path('/mnt/c/Users/MDP/dev/llmzip-work')
K=3; NT=20; DIM=96; TOL=1e-12
WIDTH_IDX={48:0,64:1,80:2}; RAND_BASE=93000
def rand_panel_seed(w,j): return RAND_BASE+10*WIDTH_IDX[w]+j
print('RAND80_s2 seed check:', rand_panel_seed(80,2), '(expect 93022)')
def tie_seed(k,t): return 5_100_000+k*100_000+t*100+99
def trial_priorities(k,n): return [np.random.default_rng(tie_seed(k,t)).random(n) for t in range(NT)]
def linspace_positions(k,dim=DIM): return np.floor(np.linspace(0,dim-1,k)+0.5).astype(int)
def per_archive_subsets(var,k,dim=DIM):
    var=np.asarray(var,float); assert var.shape==(dim,)
    od=np.argsort(var,kind='stable')[::-1]
    parts={'TOP':od[:k],'BOT':od[-k:],'SPREAD':od[linspace_positions(k,dim)]}
    out={}
    for nm,s in parts.items():
        u=np.unique(s); assert len(u)==k,(nm,k,len(u)); assert int(s.min())>=0 and int(s.max())<dim
        out[nm]=np.sort(s)
    return out
def random_subset(seed,k,dim=DIM):
    s=np.sort(np.random.default_rng(seed).choice(dim,k,replace=False)); assert len(np.unique(s))==k; return s
def measured_fr(d,gold,pris,k=K):
    d=np.asarray(d); gset=set(map(int,np.asarray(gold).ravel())); ng=len(gset); tot=0.0
    for p in pris:
        order=np.lexsort((p,d)); tot+=len(set(map(int,order[:k]))&gset)/ng
    return tot/len(pris)
def per_gold_stats(d,gold):
    d=np.asarray(d); out=[]
    for gg in np.asarray(gold).ravel():
        dg=d[int(gg)]; s=int(np.count_nonzero(d<dg)); tincl=int(np.count_nonzero(d==dg)); texcl=tincl-1
        if s>=K: e=0.0
        elif s+tincl<=K: e=1.0
        else: e=(K-s)/tincl
        p=1.0 if (s+texcl<=K-1) else 0.0
        o=1.0 if s<=K-1 else 0.0
        out.append((s,texcl,e,p,o))
    return out
def agg(stats,idx): return float(np.mean([r[idx] for r in stats]))
# ---------- LME ----------
data=json.load(open(ROOT/'drive/longmemeval_s_cleaned.json'))
allq=sorted(str(x['question_id']) for x in data); assert len(allq)==500
lex={q:i for i,q in enumerate(allq)}; del data
stored=json.load(open(ROOT/'pilots/axis_attack_2026-09-12/pilot_results.json'))['per_question_native_FR']
assert len(stored)==470
pkls=sorted((ROOT/'regen/lme/cache_repr').glob('*.pkl')); assert len(pkls)==470
arch=[]
for p in pkls:
    o=pickle.loads(p.read_bytes())
    arch.append({'qid':o['question_id'],'lex':lex[o['question_id']],'C':o['C'],'qC':o['qC'],'gold':np.asarray(o['gold']).ravel(),'stored':float(stored[o['question_id']])})
qids=[a['qid'] for a in arch]
print('LME gold counts: n1=',sum(1 for a in arch if len(a['gold'])==1),'multi=',sum(1 for a in arch if len(a['gold'])>1))
rand80s2=random_subset(93022,80)
ARMS=['NATIVE96','SPREAD80','RAND80_s2','BOT80','TOP48']
res={a:{'exp':[],'pess':[],'opt':[],'mc':[],'model_off':[],'fr_off':[]} for a in ARMS}
off=json.load(open(ROOT/'race_2026-09-13/rb2/race_sign_details.json'))
for i,a in enumerate(arch):
    C,qC,g=a['C'],a['qC'],a['gold']; n=C.shape[0]
    D0=C>=0; Q0=qC>=0
    var=C.var(axis=0); ps80=per_archive_subsets(var,80); ps48=per_archive_subsets(var,48)
    subs={'NATIVE96':None,'SPREAD80':ps80['SPREAD'],'RAND80_s2':rand80s2,'BOT80':ps80['BOT'],'TOP48':ps48['TOP']}
    pris=trial_priorities(a['lex'],n)
    for lab in ARMS:
        sub=subs[lab]
        if sub is None: d=np.count_nonzero(D0!=Q0[None,:],axis=1).astype(np.int16)
        else: d=np.count_nonzero(D0[:,sub]!=Q0[sub][None,:],axis=1).astype(np.int16)
        st=per_gold_stats(d,g)
        res[lab]['exp'].append(agg(st,2)); res[lab]['pess'].append(agg(st,3)); res[lab]['opt'].append(agg(st,4))
        res[lab]['mc'].append(measured_fr(d,g,pris))
        res[lab]['fr_off'].append(off['LME']['arms'][lab]['fr'][i])
        res[lab]['model_off'].append(off['LME']['arms'][lab]['model'][i])
    if (i+1)%100==0: print(f'  LME {i+1}/470',flush=True)
import numpy as np
print('=== LME validation: recomputed_exp vs official mc-20 fr ===')
for lab in ARMS:
    e=np.array(res[lab]['exp']); f=np.array(res[lab]['fr_off']); m=np.array(res[lab]['model_off']); mc=np.array(res[lab]['mc'])
    print(f'{lab}: max|exp-fr_off|={np.max(np.abs(e-f)):.3e} max|exp-model_off|={np.max(np.abs(e-m)):.3e} max|mc-fr_off|={np.max(np.abs(mc-f)):.3e} mean_exp={e.mean()!r} mean_fr_off={f.mean()!r}')
    # tie-free questions exact check (t_excl==0 for all golds): recompute
print('=== LME means pess/exp/opt ===')
means={}
for lab in ARMS:
    for c in ['pess','exp','opt']:
        means[(lab,c)]=float(np.mean(res[lab]['c'.replace('c',c)] if False else res[lab][c]))
    print(lab,'pess',repr(float(np.mean(res[lab]['pess']))),'exp',repr(float(np.mean(res[lab]['exp']))),'opt',repr(float(np.mean(res[lab]['opt']))),'mc',repr(float(np.mean(res[lab]['mc']))))
print('=== LME gaps SIGN-competitor (pp) ===')
for c in ['pess','exp','opt']:
    row={lab:(float(np.mean(res['NATIVE96'][c]))-float(np.mean(res[lab][c])))*100 for lab in ARMS[1:]}
    print(c,row)
json.dump({'qids':qids,'per_arm':{lab:{c:[float(v) for v in res[lab][c]] for c in ['exp','pess','opt','mc','fr_off','model_off']} for lab in ARMS}}, open('/tmp/audit1/taskC_LME_perq.json','w'))
print('wrote /tmp/audit1/taskC_LME_perq.json')
