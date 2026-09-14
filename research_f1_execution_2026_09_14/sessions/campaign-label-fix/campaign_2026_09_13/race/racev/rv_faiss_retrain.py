#!/usr/bin/env python3
"""Independent PQ/A4 retrain with runner's exact call sequence (faiss 1.15.0, threads=1)."""
import os
os.environ.setdefault("OMP_NUM_THREADS","1"); os.environ.setdefault("OPENBLAS_NUM_THREADS","1")
os.environ.setdefault("MKL_NUM_THREADS","1"); os.environ.setdefault("NUMEXPR_NUM_THREADS","1")
import json, pickle, re, hashlib
from pathlib import Path
import numpy as np, faiss
faiss.omp_set_num_threads(1)
WORK=Path("/mnt/c/Users/MDP/dev/llmzip-work")
D=json.load(open(WORK/"race_2026-09-13/official_run/faiss/race_faiss_details.json"))
K=3; NT=20
def fr_from_dist(dist,gold,pris):
    d=np.asarray(dist,float); g=set(map(int,gold)); ng=len(g); fr=[]
    for p in pris:
        order=np.lexsort((np.asarray(p,float),d))
        fr.append(len(set(map(int,order[:K]))&g)/ng)
    return float(np.mean(fr))
def A6_build(Xf):
    idx=faiss.IndexPQ(96,12,8); idx.train(Xf)
    assert idx.is_trained
    idx.add(Xf)
    assert np.all(np.isfinite(faiss.vector_to_array(idx.pq.centroids)))
    return idx
def A6_query(idx,q,n):
    D,I=idx.search(q.reshape(1,-1).astype(np.float32),int(n))
    return D[0].astype(np.float64),I[0].astype(int)
def full_dist(D,I,n):
    d=np.empty(int(n)); d[np.asarray(I,int)]=np.asarray(D,float); return d
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
# ---- LME items ----
data=json.load(open(WORK/"drive/longmemeval_s_cleaned.json"))
allq=sorted(str(x["question_id"]) for x in data); lex={q:i for i,q in enumerate(allq)}; del data
pkls=sorted((WORK/"regen/lme/cache_repr").glob("*.pkl"))
items=[]
for p in pkls:
    o=pickle.loads(p.read_bytes())
    items.append({"qid":str(o["question_id"]),"C":np.asarray(o["C"],float),"qC":np.asarray(o["qC"],float),
      "gold":set(map(int,np.asarray(o["gold"]).ravel())),"N":int(o["C"].shape[0]),"lex":lex[str(o["question_id"])]})
# ---- LoCoMo ----
raw=json.loads((WORK/"drive/locomo10.json").read_text()); corr=load_audit(WORK/"drive/audit_layer")
reps=[pickle.load(open(WORK/f"regen/locomo/locomo_{ci}.pkl","rb")) for ci in range(10)]
print("=== 3b: PQ deterministic retrain on 2 archives (LME items[0] + locomo_1) ===")
# archive 1: LME items[0]
it=items[0]
Xf=np.ascontiguousarray(it["C"],dtype=np.float32)
i1=A6_build(Xf); i2=A6_build(Xf)
c1=faiss.vector_to_array(i1.codes).tobytes(); c2=faiss.vector_to_array(i2.codes).tobytes()
print("LME",it["qid"],"N=",it["N"],"retrain codes bit-identical:",c1==c2,"sha:",hashlib.sha256(c1).hexdigest()[:16])
# archive 2: locomo_1
r=reps[1]; Xl=np.ascontiguousarray(np.asarray(r["C"],float),dtype=np.float32)
j1=A6_build(Xl); j2=A6_build(Xl)
d1=faiss.vector_to_array(j1.codes).tobytes(); d2=faiss.vector_to_array(j2.codes).tobytes()
print("locomo_1 N=",Xl.shape[0],"retrain codes bit-identical:",d1==d2,"sha:",hashlib.sha256(d1).hexdigest()[:16])
print("per-archive codes NOT persisted in JSON (only aggregate codes_sha256) -> code-hash vs runner: NOT CHECKABLE; FR functional check below")
print("=== 5 A6 FRs on those archives ===")
# LME qid
qf=np.ascontiguousarray(it["qC"],dtype=np.float32)
DD,II=A6_query(i1,qf,Xf.shape[0]); dd=full_dist(DD,II,Xf.shape[0])
pris=[np.random.default_rng(5_100_000+it["lex"]*100_000+t*100+99).random(it["N"]) for t in range(NT)]
mine=fr_from_dist(dd,it["gold"],pris); st=D["arms_per_q"]["A6_PQ"]["lme"][it["qid"]]
print(f"A6 LME {it['qid']}: mine={mine!r} stored={st!r} diff={mine-st!r} {'EXACT' if abs(mine-st)<=1e-12 else 'DIFF'}")
# 4 locomo_1 questions
Q={}; id_to_row=r["id_to_row"]
fqi=0; targets=[]
for raw_qi,q in enumerate(raw[1].get("qa",[])):
    cat=int(q.get("category")) if q.get("category") is not None else -1
    if cat not in (1,2,3,4): continue
    qid=q.get("question_id") or f"locomo_1_qa{raw_qi}"; z=corr.get(str(qid))
    ce=list(z["ce"]) if (z and z["he"]) else list(norm_ev(q.get("evidence")))
    ag=list(dict.fromkeys([int(id_to_row[x]) for x in ce if x in id_to_row]))
    if ag: targets.append((str(qid),fqi,set(ag)))
    fqi+=1
print("locomo_1 valid:",len(targets))
Qf=np.ascontiguousarray(np.asarray(r["QC"],float),dtype=np.float32)
for qid,fqi,ag in targets[:4]:
    DD,II=A6_query(j1,Qf[fqi],Xl.shape[0]); dd=full_dist(DD,II,Xl.shape[0])
    pris=[np.random.default_rng(5_100_000+1*100_000+t*100+99).random(Xl.shape[0]) for t in range(NT)]
    mine=fr_from_dist(dd,ag,pris); st=D["arms_per_q"]["A6_PQ"]["locomo"][qid]
    print(f"A6 locomo {qid}: mine={mine!r} stored={st!r} diff={mine-st!r} {'EXACT' if abs(mine-st)<=1e-12 else 'DIFF'}")
print("=== 3d: RaBitQ32 arm A4_spread_rot94101, 3 FRs ===")
def spread_cols(var,k=32):
    od=np.argsort(np.asarray(var,float),kind="stable")[::-1]
    idx=np.round(np.linspace(0,95,k)).astype(int)
    return np.sort(od[idx].astype(int))
def seeded_rot(seed,d=32):
    A=np.random.default_rng(seed).standard_normal((d,d)); Q,Rm=np.linalg.qr(A)
    return (Q*np.where(np.diag(Rm)<0,-1.0,1.0)[None,:]).astype(np.float64)
R=seeded_rot(94101)
def a4_dist_lme(C,qC):
    cols=spread_cols(C.var(axis=0),32)
    Xf=np.ascontiguousarray((C[:,cols]@R),dtype=np.float32); qf=(qC[cols]@R).astype(np.float32)
    idx=faiss.IndexRaBitQ(32); idx.train(Xf); idx.add(Xf)
    DD,II=idx.search(qf.reshape(1,-1).astype(np.float32),Xf.shape[0])
    return full_dist(DD[0].astype(np.float64),II[0].astype(int),Xf.shape[0])
for it2 in [items[0],items[5],items[100]]:
    dd=a4_dist_lme(np.asarray(it2["C"],float),np.asarray(it2["qC"],float))
    pris=[np.random.default_rng(5_100_000+it2["lex"]*100_000+t*100+99).random(it2["N"]) for t in range(NT)]
    mine=fr_from_dist(dd,it2["gold"],pris); st=D["arms_per_q"]["A4_spread_rot94101"]["lme"][it2["qid"]]
    print(f"A4 LME {it2['qid']}: mine={mine!r} stored={st!r} diff={mine-st!r} {'EXACT' if abs(mine-st)<=1e-12 else 'DIFF'}")
