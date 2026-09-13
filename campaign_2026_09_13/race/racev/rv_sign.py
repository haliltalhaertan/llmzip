#!/usr/bin/env python3
"""RACE-V independent sign-side recomputation. Own implementation; never imports runner."""
import json, pickle, re, csv
from pathlib import Path
import numpy as np
WORK = Path("/mnt/c/Users/MDP/dev/llmzip-work")
OFF = WORK/"race_2026-09-13/official_run/sign/race_sign_details.json"
K=3; NT=20; DIM=96
def tie_seed_LME(lex,t): return 5_100_000+lex*100_000+t*100+99
def tie_seed_LOCO(ci,t): return 5_100_000+ci*100_000+t*100+99
def pris_for(seed_base_list, n):
    return [np.random.default_rng(s).random(n) for s in seed_base_list]
def measured_fr(d, gold, pris):
    gset=set(map(int,np.asarray(gold).ravel())); ng=len(gset); tot=0.0; tr=[]
    d=np.asarray(d)
    for p in pris:
        order=np.lexsort((np.asarray(p),d))
        f=len(set(map(int,order[:K]))&gset)/ng; tr.append(f); tot+=f
    return tot/len(pris), tr
def model_fr(d, gold):
    d=np.asarray(d); g=np.asarray(gold).ravel(); tot=0.0
    for gg in g:
        dg=d[int(gg)]; s=int(np.count_nonzero(d<dg)); t=int(np.count_nonzero(d==dg))
        if s>=K: p=0.0
        elif s+t<=K: p=1.0
        else: p=(K-s)/t
        tot+=p
    return tot/len(g)
def linpos(k,dim=96): return np.floor(np.linspace(0,dim-1,k)+0.5).astype(int)
def per_arch_subsets(var,k):
    od=np.argsort(np.asarray(var,float),kind="stable")[::-1]
    parts={"TOP":od[:k],"BOT":od[-k:],"SPREAD":od[linpos(k)]}
    return {n:np.sort(s) for n,s in parts.items()}
def rand_subset(seed,k): return np.sort(np.random.default_rng(seed).choice(96,k,replace=False))
def norm_ev(x):
    if x is None: return []
    if isinstance(x,str):
        v=re.findall(r"D\d+:\d+",x); return v if v else [x]
    if isinstance(x,(list,tuple)):
        out=[]
        for z in x:
            if isinstance(z,str):
                ids=re.findall(r"D\d+:\d+",z); out.extend(ids if ids else [z])
            elif isinstance(z,dict):
                did=z.get("dia_id") or z.get("id")
                if did: out.append(str(did))
        return list(dict.fromkeys(out))
    return []
def load_audit(ad):
    corr={}
    for f in sorted(Path(ad).glob("errors_conv_*.json")):
        try: rows=json.loads(Path(f).read_text())
        except Exception: continue
        if not isinstance(rows,list): continue
        for r in rows:
            if not r.get("question_id"): continue
            corr[str(r["question_id"])]={"he":("correct_evidence" in r),"ce":norm_ev(r.get("correct_evidence"))}
    return corr
out={"anchors":{},"spot":[],"agg":[],"model":[],"validity":{}}
# ---- LME load ----
data=json.load(open(WORK/"drive/longmemeval_s_cleaned.json"))
allq=sorted(str(x["question_id"]) for x in data); lex={q:i for i,q in enumerate(allq)}; del data
pkls=sorted((WORK/"regen/lme/cache_repr").glob("*.pkl"))
LME={}
for p in pkls:
    o=pickle.loads(p.read_bytes())
    LME[o["question_id"]]={"C":o["C"],"qC":o["qC"],"gold":np.asarray(o["gold"]).ravel(),"lex":lex[o["question_id"]]}
# anchor recompute (native, own impl)
frs=[]
for qid,a in LME.items():
    C,qC,g=a["C"],a["qC"],a["gold"]; n=C.shape[0]
    pris=[np.random.default_rng(tie_seed_LME(a["lex"],t)).random(n) for t in range(NT)]
    d=np.count_nonzero((C>=0)!=(qC>=0)[None,:],axis=1).astype(np.int16)
    f,_=measured_fr(d,g,pris); frs.append(f)
lme_anchor=float(np.mean(frs))
out["anchors"]["LME"]={"recomputed":lme_anchor,"expected":0.5419751773049645,"diff":lme_anchor-0.5419751773049645}
print("LME anchor:",repr(lme_anchor),"diff:",repr(lme_anchor-0.5419751773049645))
# ---- LoCoMo load ----
raw=json.loads((WORK/"drive/locomo10.json").read_text())
corr=load_audit(WORK/"drive/audit_layer")
convs=[]
for idx,item in enumerate(raw):
    qas=[]
    for qi,q in enumerate(item.get("qa",[]) or []):
        cat=int(q.get("category")) if q.get("category") is not None else None
        if cat not in (1,2,3,4): continue
        qid=q.get("question_id") or f"locomo_{idx}_qa{qi}"
        z=corr.get(str(qid))
        ce=list(z["ce"]) if (z and z["he"]) else list(norm_ev(q.get("evidence")))
        qas.append({"qid":str(qid),"cat":cat,"ce":ce})
    convs.append(qas)
reps=[pickle.load(open(WORK/f"regen/locomo/locomo_{ci}.pkl","rb")) for ci in range(10)]
def ev_rows(ids,id_to_row):
    out=[]
    for x in ids:
        if x in id_to_row: out.append(int(id_to_row[x]))
    return list(dict.fromkeys(out))
LOCO={}
for ci in range(10):
    id_to_row=reps[ci]["id_to_row"]
    C=reps[ci]["C"]; QC=reps[ci]["QC"]
    D=np.count_nonzero((QC>=0)[:,None,:]!=(C>=0)[None,:,:],axis=2).astype(np.int16)
    pris=[np.random.default_rng(tie_seed_LOCO(ci,t)).random(C.shape[0]) for t in range(NT)]
    for qi,q in enumerate(convs[ci]):
        ag=ev_rows(q["ce"],id_to_row)
        if not ag: continue
        f,_=measured_fr(D[qi],ag,pris)
        LOCO[q["qid"]]={"f":f,"ci":ci,"qi":qi,"ag":ag,"pris":pris,"dist":D[qi]}
loco_anchor=float(np.mean([v["f"] for v in LOCO.values()]))
out["anchors"]["LoCoMo"]={"recomputed":loco_anchor,"expected":0.23654714666441054,"diff":loco_anchor-0.23654714666441054,"n":len(LOCO)}
print("LoCoMo anchor:",repr(loco_anchor),"diff:",repr(loco_anchor-0.23654714666441054),"n=",len(LOCO))
json.dump(out,open("/tmp/racev/rv_sign_anchor.json","w"),indent=1)
print("saved anchor stage")
