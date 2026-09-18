#!/usr/bin/env python3
"""[LOCAL AUDIT] Task C-real LoCoMo: mirror race_sign.run_locomo EXACTLY."""
import json, pickle, re
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/c/Users/MDP/dev/llmzip-work'); K=3; NT=20; DIM=96
WIDTH_IDX={48:0,64:1,80:2}; RAND_BASE=93000
def rand_panel_seed(w,j): return RAND_BASE+10*WIDTH_IDX[w]+j
def tie_seed(k,t): return 5_100_000+k*100_000+t*100+99
def trial_priorities(k,n): return [np.random.default_rng(tie_seed(k,t)).random(n) for t in range(NT)]
def linspace_positions(k,dim=DIM): return np.floor(np.linspace(0,dim-1,k)+0.5).astype(int)
def per_archive_subsets(var,k,dim=DIM):
    var=np.asarray(var,float); assert var.shape==(dim,)
    od=np.argsort(var,kind='stable')[::-1]
    parts={'TOP':od[:k],'BOT':od[-k:],'SPREAD':od[linspace_positions(k,dim)]}
    out={}
    for nm,s in parts.items():
        u=np.unique(s); assert len(u)==k,(nm,k); assert int(s.min())>=0 and int(s.max())<dim
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
        e=0.0 if s>=K else (1.0 if s+tincl<=K else (K-s)/tincl)
        p=1.0 if (s+texcl<=K-1) else 0.0
        o=1.0 if s<=K-1 else 0.0
        out.append((s,texcl,e,p,o))
    return out
def norm_evidence(x):
    if x is None: return []
    if isinstance(x,str):
        v=re.findall(r'D\d+:\d+',x); return v if v else [x]
    if isinstance(x,(list,tuple)):
        out=[]
        for z in x:
            if isinstance(z,str):
                ids=re.findall(r'D\d+:\d+',z); out.extend(ids if ids else [z])
            elif isinstance(z,dict):
                did=z.get('dia_id') or z.get('id')
                if did: out.append(str(did))
        return list(dict.fromkeys(out))
    return []
def load_audit_corrections(ad):
    corr={}
    for f in sorted(ad.glob('errors_conv_*.json')):
        try: rows=json.loads(f.read_text())
        except Exception: continue
        if not isinstance(rows,list): continue
        for r in rows:
            qid=r.get('question_id')
            if not qid: continue
            corr[str(qid)]={'has_correct_evidence':'correct_evidence' in r,'correct_evidence':norm_evidence(r.get('correct_evidence'))}
    return corr
def evidence_rows(ids,id_to_row):
    out=[]
    for x in ids:
        if x in id_to_row: out.append(int(id_to_row[x]))
    return list(dict.fromkeys(out))
def sign_dist_matrix(C,QC,subset=None):
    D=C[:,subset]>=0 if subset is not None else C>=0
    Qm=QC[:,subset]>=0 if subset is not None else QC>=0
    return np.count_nonzero(Qm[:,None,:]!=D[None,:,:],axis=2).astype(np.int16)
raw=json.loads((ROOT/'drive/locomo10.json').read_text(encoding='utf-8'))
corr=load_audit_corrections(ROOT/'drive/audit_layer')
convs=[]
for idx,item in enumerate(raw):
    qas=[]
    for qi,q in enumerate(item.get('qa',[]) or []):
        cat=int(q.get('category')) if q.get('category') is not None else None
        if cat not in (1,2,3,4): continue
        qid=q.get('question_id') or f'locomo_{idx}_qa{qi}'
        z=corr.get(str(qid))
        ce=list(z['correct_evidence']) if (z and z.get('has_correct_evidence',False)) else list(norm_evidence(q.get('evidence')))
        # mirror race_sign: if z exists use correct_evidence only when has_correct_evidence else raw evidence; note race uses z['correct_evidence'] directly when z truthy? re-check: race lines 268-275: if z: ce = list(correct) if has_correct else list(norm(raw)); else ce=list(norm(raw)). Same.
        qas.append({'question_id':str(qid),'category':cat,'correct_evidence':ce})
    convs.append({'conv_id':f'locomo_{idx}','qas':qas})
reps=[]
for ci in range(10):
    d=pickle.load(open(ROOT/f'regen/locomo/locomo_{ci}.pkl','rb'))
    assert d['conv_id']==f'locomo_{ci}'
    raw_ids=[q['question_id'] for q in convs[ci]['qas']]
    pkl_ids=[q['question_id'] for q in d['qas']]
    assert raw_ids==pkl_ids, f'order mismatch conv {ci}'
    assert d['QC'].shape[0]==len(d['qas'])
    reps.append(d)
qinfo={}
for ci,c in enumerate(convs):
    id_to_row=reps[ci]['id_to_row']
    for qi,q in enumerate(c['qas']):
        ag=evidence_rows(q['correct_evidence'],id_to_row)
        qinfo[q['question_id']]={'cat':q['category'],'ci':ci,'qi':qi,'ag':ag}
valid=[qid for qid,v in qinfo.items() if len(v['ag'])>0]
print('LoCoMo valid:',len(valid))
import collections
print('gold-count distribution:',collections.Counter(len(qinfo[q]['ag']) for q in valid))
ARMS=['NATIVE96','SPREAD80','RAND80_s2','BOT80','TOP48']
rand80s2=random_subset(93022,80)
arch_sub={ci:{k:per_archive_subsets(reps[ci]['C'].var(axis=0),k) for k in (48,64,80)} for ci in range(10)}
off=json.load(open(ROOT/'race_2026-09-13/rb2/race_sign_details.json'))
off_fr={lab:dict(zip(off['LoCoMo']['qids'],off['LoCoMo']['arms'][lab]['fr'])) for lab in ARMS}
off_mo={lab:dict(zip(off['LoCoMo']['qids'],off['LoCoMo']['arms'][lab]['model'])) for lab in ARMS}
res={lab:{'exp':[],'pess':[],'opt':[],'mc':[],'fr_off':[],'model_off':[]} for lab in ARMS}
for ci,(c,r) in enumerate(zip(convs,reps)):
    n=r['C'].shape[0]; pris=trial_priorities(ci,n)
    dists={'NATIVE96':sign_dist_matrix(r['C'],r['QC'])}
    for k in (48,64,80):
        for fam in ('TOP','BOT','SPREAD'):
            dists[f'{fam}{k}']=sign_dist_matrix(r['C'],r['QC'],arch_sub[ci][k][fam])
    dists['RAND80_s2']=sign_dist_matrix(r['C'],r['QC'],rand80s2)
    dists['TOP48']=dists['TOP48']
    for qi,q in enumerate(c['qas']):
        qid=q['question_id']; ag=qinfo[qid]['ag']
        if not ag: continue
        for lab in ARMS:
            dvec=dists[lab][qi]
            st=per_gold_stats(dvec,ag)
            res[lab]['exp'].append(float(np.mean([x[2] for x in st])))
            res[lab]['pess'].append(float(np.mean([x[3] for x in st])))
            res[lab]['opt'].append(float(np.mean([x[4] for x in st])))
            res[lab]['mc'].append(measured_fr(dvec,ag,pris))
            res[lab]['fr_off'].append(off_fr[lab][qid])
            res[lab]['model_off'].append(off_mo[lab][qid])
    print(f'  conv {ci+1}/10 done',flush=True)
print('=== LoCoMo validation ===')
for lab in ARMS:
    e=np.array(res[lab]['exp']); f=np.array(res[lab]['fr_off']); m=np.array(res[lab]['model_off']); mc=np.array(res[lab]['mc'])
    print(f'{lab}: max|exp-fr_off|={np.max(np.abs(e-f)):.3e} max|exp-model_off|={np.max(np.abs(e-m)):.3e} max|mc-fr_off|={np.max(np.abs(mc-f)):.3e} mean_exp={e.mean()!r} mean_fr_off={f.mean()!r}')
print('=== LoCoMo means ===')
for lab in ARMS:
    print(lab,'pess',repr(float(np.mean(res[lab]['pess']))),'exp',repr(float(np.mean(res[lab]['exp']))),'opt',repr(float(np.mean(res[lab]['opt']))),'mc',repr(float(np.mean(res[lab]['mc']))))
print('=== LoCoMo gaps SIGN-competitor (pp) ===')
for cc in ['pess','exp','opt']:
    row={lab:(float(np.mean(res['NATIVE96'][cc]))-float(np.mean(res[lab][cc])))*100 for lab in ARMS[1:]}
    print(cc,row)
json.dump({'qids':valid,'per_arm':{lab:{cc:[float(v) for v in res[lab][cc]] for cc in ['exp','pess','opt','mc','fr_off','model_off']} for lab in ARMS}}, open('/tmp/audit1/taskC_LoCoMo_perq.json','w'))
print('wrote /tmp/audit1/taskC_LoCoMo_perq.json')
