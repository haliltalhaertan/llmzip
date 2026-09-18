#!/usr/bin/env python3
"""Stage 2: 12 FR spot-checks, 6 aggregate means, 5 MATH-1 checks, validity callouts."""
import json, pickle, re
from pathlib import Path
import numpy as np
WORK=Path("/mnt/c/Users/MDP/dev/llmzip-work")
OFF=json.load(open(WORK/"race_2026-09-13/official_run/sign/race_sign_details.json"))
K=3; NT=20
def measured_fr(d,gold,pris):
    gset=set(map(int,np.asarray(gold).ravel())); ng=len(gset); tot=0.0
    d=np.asarray(d)
    for p in pris:
        order=np.lexsort((np.asarray(p),d))
        tot+=len(set(map(int,order[:K]))&gset)/ng
    return tot/len(pris)
def model_fr(d,gold):
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
    return {"TOP":np.sort(od[:k]),"BOT":np.sort(od[-k:]),"SPREAD":np.sort(od[linpos(k)])}
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
# LME data
data=json.load(open(WORK/"drive/longmemeval_s_cleaned.json"))
allq=sorted(str(x["question_id"]) for x in data); lex={q:i for i,q in enumerate(allq)}; del data
pkls=sorted((WORK/"regen/lme/cache_repr").glob("*.pkl"))
LME={}
for p in pkls:
    o=pickle.loads(p.read_bytes())
    LME[o["question_id"]]={"C":o["C"],"qC":o["qC"],"gold":np.asarray(o["gold"]).ravel(),"lex":lex[o["question_id"]]}
lme_qids=OFF["LME"]["qids"]
# LoCoMo data
raw=json.loads((WORK/"drive/locomo10.json").read_text()); corr=load_audit(WORK/"drive/audit_layer")
reps=[pickle.load(open(WORK/f"regen/locomo/locomo_{ci}.pkl","rb")) for ci in range(10)]
QINFO={}; conv_qas=[]
for ci in range(10):
    id_to_row=reps[ci]["id_to_row"]
    qs=[]; fqi=0
    for raw_qi,q in enumerate(raw[ci].get("qa",[])):
        cat=int(q.get("category")) if q.get("category") is not None else -1
        if cat not in (1,2,3,4): continue
        qid=q.get("question_id") or f"locomo_{ci}_qa{raw_qi}"; z=corr.get(str(qid))
        ce=list(z["ce"]) if (z and z["he"]) else list(norm_ev(q.get("evidence")))
        ag=[]
        for x in ce:
            if x in id_to_row: ag.append(int(id_to_row[x]))
        ag=list(dict.fromkeys(ag))
        QINFO[str(qid)]={"ci":ci,"qi":fqi,"ag":ag}
        qs.append(str(qid)); fqi+=1
    conv_qas.append(qs)
loco_qids=OFF["LoCoMo"]["qids"]
def arm_subset_lme(C, arm):
    var=C.var(axis=0)
    if arm=="NATIVE96": return None
    if arm.startswith("RAND"):
        k=int(arm.split("_")[0][4:]); j=int(arm.split("_s")[1])
        base=93000+10*{48:0,64:1,80:2}[k]+j
        return rand_subset(base,k)
    fam=arm[:-2]; k=int(arm[-2:])
    return per_arch_subsets(var,k)[fam]
def arm_subset_loco(ci, arm, C):
    var=np.asarray(C,float).var(axis=0)
    if arm=="NATIVE96": return None
    if arm.startswith("RAND"):
        k=int(arm.split("_")[0][4:]); j=int(arm.split("_s")[1])
        base=93000+10*{48:0,64:1,80:2}[k]+j
        return rand_subset(base,k)
    fam=arm[:-2]; k=int(arm[-2:])
    return per_arch_subsets(var,k)[fam]
# pick 12 pairs spanning arms x benchmarks (use index positions incl edges/middle)
pairs=[("LME",lme_qids[0],"NATIVE96"),("LME",lme_qids[7],"SPREAD80"),("LME",lme_qids[100],"BOT80"),
 ("LME",lme_qids[200],"RAND80_s2"),("LME",lme_qids[300],"TOP48"),("LME",lme_qids[469],"BOT48"),
 ("LoCoMo",loco_qids[0],"NATIVE96"),("LoCoMo",loco_qids[50],"SPREAD80"),("LoCoMo",loco_qids[500],"BOT80"),
 ("LoCoMo",loco_qids[900],"RAND80_s2"),("LoCoMo",loco_qids[1200],"TOP48"),("LoCoMo",loco_qids[1534],"BOT48")]
res=[]
for bench,qid,arm in pairs:
    if bench=="LME":
        a=LME[qid]; C,qC,g=a["C"],a["qC"],a["gold"]; n=C.shape[0]
        sub=arm_subset_lme(C,arm)
        D0=(C>=0); Q0=(qC>=0)
        d=(np.count_nonzero(D0!=Q0[None,:],axis=1) if sub is None else np.count_nonzero(D0[:,sub]!=Q0[sub][None,:],axis=1)).astype(np.int16)
        pris=[np.random.default_rng(5_100_000+a["lex"]*100_000+t*100+99).random(n) for t in range(NT)]
        idx=lme_qids.index(qid)
        stored=OFF["LME"]["arms"][arm]["fr"][idx]
    else:
        ci=QINFO[qid]["ci"]; qi=QINFO[qid]["qi"]; ag=QINFO[qid]["ag"]
        C=reps[ci]["C"]; QC=reps[ci]["QC"]
        sub=arm_subset_loco(ci,arm,C)
        D=(C>=0); Qm=(QC>=0)
        dd=(np.count_nonzero(Qm[:,None,:]!=D[None,:,:],axis=2) if sub is None else np.count_nonzero(Qm[:,sub][:,None,:]!=D[:,sub][None,:,:],axis=2)).astype(np.int16)
        d=dd[qi]; g=np.asarray(ag)
        pris=[np.random.default_rng(5_100_000+ci*100_000+t*100+99).random(C.shape[0]) for t in range(NT)]
        idx=loco_qids.index(qid)
        stored=OFF["LoCoMo"]["arms"][arm]["fr"][idx]
    mine=measured_fr(d,g,pris); diff=mine-stored
    res.append({"bench":bench,"qid":qid,"arm":arm,"mine":mine,"stored":stored,"diff":diff,"ok":abs(diff)<=1e-12})
    print(f"{bench} {qid} {arm}: mine={mine!r} stored={stored!r} diff={diff!r} {'EXACT' if abs(diff)<=1e-12 else 'DIFF'}")
# aggregates: 6 arm means
print("--- aggregates ---")
for bench,arm in [("LME","NATIVE96"),("LME","TOP48"),("LME","SPREAD80"),("LoCoMo","NATIVE96"),("LoCoMo","BOT80"),("LoCoMo","RAND80_s2")]:
    arr=OFF[bench]["arms"][arm]["fr"]; m=float(np.mean(arr)); st=OFF[bench]["arms"][arm]["mean"]
    print(f"{bench} {arm}: recomputed_mean={m!r} stored={st!r} diff={m-st!r}")
# MATH-1: 5 pairs
print("--- MATH-1 ---")
mpairs=[("LME",lme_qids[7],"SPREAD80"),("LME",lme_qids[300],"TOP48"),("LME",lme_qids[0],"NATIVE96"),
        ("LoCoMo",loco_qids[500],"BOT80"),("LoCoMo",loco_qids[0],"NATIVE96")]
for bench,qid,arm in mpairs:
    if bench=="LME":
        a=LME[qid]; C,qC,g=a["C"],a["qC"],a["gold"]
        sub=arm_subset_lme(C,arm); D0=(C>=0); Q0=(qC>=0)
        d=(np.count_nonzero(D0!=Q0[None,:],axis=1) if sub is None else np.count_nonzero(D0[:,sub]!=Q0[sub][None,:],axis=1)).astype(np.int16)
        idx=lme_qids.index(qid); stored=OFF["LME"]["arms"][arm]["model"][idx]
    else:
        ci=QINFO[qid]["ci"]; qi=QINFO[qid]["qi"]; ag=QINFO[qid]["ag"]
        C=reps[ci]["C"]; QC=reps[ci]["QC"]; sub=arm_subset_loco(ci,arm,C)
        D=(C>=0); Qm=(QC>=0)
        dd=(np.count_nonzero(Qm[:,None,:]!=D[None,:,:],axis=2) if sub is None else np.count_nonzero(Qm[:,sub][:,None,:]!=D[:,sub][None,:,:],axis=2)).astype(np.int16)
        d=dd[qi]; g=np.asarray(ag); idx=loco_qids.index(qid); stored=OFF["LoCoMo"]["arms"][arm]["model"][idx]
    mine=model_fr(d,g); print(f"{bench} {qid} {arm}: model_mine={mine!r} stored={stored!r} diff={mine-stored!r}")
# validity
print("--- validity ---")
print("TOP48 LME:",repr(OFF["LME"]["arms"]["TOP48"]["mean"]),"expect 0.34949468")
print("SPREAD80 LME:",repr(OFF["LME"]["arms"]["SPREAD80"]["mean"]),"expect 0.52526")
print("BOT80 LoCoMo:",repr(OFF["LoCoMo"]["arms"]["BOT80"]["mean"]),"expect 0.23546")
json.dump(res,open("/tmp/racev/rv_sign_spot.json","w"),indent=1)
