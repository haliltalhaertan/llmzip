from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "longmemeval_spectral_band_haar_causal.py"
PREREG_GIT_BLOB = "0d34207be55a75194b585789c7139cbc8aeb264d"
BASE_GIT_BLOB = "79dd4a5ec462102da5d82530088a4b7e89bef437"
SEEDS = [56001,56002,56003,56004,56005]
HEAD=np.arange(0,32,dtype=int);TAIL=np.arange(32,96,dtype=int);FULL=np.arange(0,96,dtype=int)
TOL=1e-12


def load_base():
    spec=importlib.util.spec_from_file_location("lm_head_tail_base",BASE_PATH)
    if spec is None or spec.loader is None: raise RuntimeError("cannot import base")
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def haar_q(rng,d):
    A=rng.standard_normal((d,d));Q,R=np.linalg.qr(A);sg=np.where(np.diag(R)<0,-1.0,1.0);return Q*sg[None,:]


def transform(seed):
    rng=np.random.default_rng(seed);R=np.zeros((96,96),float);R[:32,:32]=haar_q(rng,32);R[32:,32:]=haar_q(rng,64);return R


def subset_r3(base,D,qb,priorities,gold,idx):
    d=np.count_nonzero(D[:,idx] != qb[None,idx],axis=1).astype(np.int16);return base.mean_r3(d,priorities,gold)


def pairwise(D,qb,gold,idx):
    G=np.asarray(gold,dtype=int);mask=np.ones(len(D),bool);mask[G]=False;NG=np.flatnonzero(mask)
    if len(G)==0 or len(NG)==0:return 0,0.0,0.0,0.0
    dg=np.count_nonzero(D[G][:,idx] != qb[None,idx],axis=1);dn=np.count_nonzero(D[NG][:,idx] != qb[None,idx],axis=1)
    comp=dg[:,None]-dn[None,:];n=int(comp.size);disc=float(np.sum(comp<0)+0.5*np.sum(comp==0));adv=(float(dn.mean())-float(dg.mean()))/len(idx)*n
    return n,disc,adv,float(np.sum(comp==0))


def eval_one(item,lex,tforms):
    b=load_base();a2=b.load_module(b.A2_PATH,f"lm_ht_v2_{os.getpid()}_{lex}");qid,C,qC,gold=b.build_rep(item,a2);n=len(C)
    priorities=[np.random.default_rng(5_100_000+lex*100_000+t*100+99).random(n) for t in range(b.N_NUISANCE)]
    D0=C>=0;qb0=qC>=0;d0=np.count_nonzero(D0 != qb0[None,:],axis=1).astype(np.int16);native=b.mean_r3(d0,priorities,gold)
    rsp=np.random.default_rng(SEEDS[0]);perm=rsp.permutation(96);sg=rsp.choice(np.array([-1.0,1.0]),96)
    Ds=(C[:,perm]*sg)>=0;qs=(qC[perm]*sg)>=0;dsp=np.count_nonzero(Ds != qs[None,:],axis=1).astype(np.int16)
    if not np.array_equal(d0,dsp):raise RuntimeError(f"signed permutation failure {qid}")
    rows=[];subs=[];pairs=[];resc=[];max_norm=0.0;max_dot=0.0
    for s,R in tforms.items():
        Cr=C@R;qr=qC@R
        max_norm=max(max_norm,float(np.max(np.abs(np.linalg.norm(Cr,axis=1)-np.linalg.norm(C,axis=1)))),abs(float(np.linalg.norm(qr)-np.linalg.norm(qC))))
        max_dot=max(max_dot,float(np.max(np.abs(Cr@qr-C@qC))))
        D=Cr>=0;qb=qr>=0;dist=np.count_nonzero(D != qb[None,:],axis=1).astype(np.int16);rows.append((s,b.mean_r3(dist,priorities,gold)))
        for name,idx in [("Head32",HEAD),("Tail64",TAIL),("Full96",FULL)]:
            subs.append((s,name,subset_r3(b,D,qb,priorities,gold,idx)));pc=pairwise(D,qb,gold,idx);pairs.append((s,name,*pc))
        hf=b.hard_pair(D,qb,gold,HEAD);ff=b.hard_pair(D,qb,gold,FULL)
        if hf and ff:resc.append((s,hf[0]<hf[1],ff[0]<ff[1]))
    if max_norm>TOL or max_dot>TOL:raise RuntimeError(f"continuous invariance {qid} {max_norm} {max_dot}")
    return {"qid":qid,"native":native,"rows":rows,"subs":subs,"pairs":pairs,"rescue":resc,"max_norm":max_norm,"max_dot":max_dot}


def run_shard(dataset,idx,nshards,out):
    b=load_base()
    if dataset.stat().st_size!=b.DATASET_BYTES or b.sha256_file(dataset)!=b.DATASET_SHA256:raise RuntimeError("dataset identity mismatch")
    if b.sha256_file(b.A1_PATH)!=b.A1_SHA256 or b.sha256_file(b.A2_PATH)!=b.A2_SHA256:raise RuntimeError("adapter identity mismatch")
    data=json.loads(dataset.read_text(encoding="utf-8"));prim=[x for x in data if not str(x["question_id"]).endswith("_abs")]
    if len(data)!=500 or len(prim)!=b.EXPECTED_PRIMARY:raise RuntimeError("cohort mismatch")
    allq=sorted(str(x["question_id"]) for x in data);lex={q:i for i,q in enumerate(allq)};chosen=[x for i,x in enumerate(prim) if i%nshards==idx]
    tforms={s:transform(s) for s in SEEDS}
    for s,R in tforms.items():
        e=float(np.max(np.abs(R.T@R-np.eye(96))))
        if e>TOL:raise RuntimeError(f"orthogonality {s} {e}")
    results=[eval_one(x,lex[str(x["question_id"])],tforms) for x in chosen]
    q=[z["qid"] for z in results]
    if len(q)!=len(set(q)) or len(q)!=len(chosen):raise RuntimeError("shard integrity")
    out.write_bytes(pickle.dumps({"shard_index":idx,"num_shards":nshards,"count":len(results),"results":results},pickle.HIGHEST_PROTOCOL))
    print(json.dumps({"shard":idx,"count":len(results),"max_norm":max(z["max_norm"] for z in results),"max_dot":max(z["max_dot"] for z in results)}))


def aggregate(shard_dir,out):
    b=load_base();files=sorted(shard_dir.rglob("shard_*.pkl"));ps=[pickle.loads(p.read_bytes()) for p in files]
    ns={int(p["num_shards"]) for p in ps}
    if len(ns)!=1:raise RuntimeError("mixed shards")
    n=ns.pop();inds=sorted(int(p["shard_index"]) for p in ps)
    if inds!=list(range(n)):raise RuntimeError(f"missing shards {inds}")
    results=[z for p in ps for z in p["results"]];qids=[z["qid"] for z in results]
    if len(results)!=470 or len(set(qids))!=470:raise RuntimeError("470/470 integrity failure")
    native=float(np.mean([z["native"] for z in results]));repro=abs(native-b.FROZEN_NATIVE_R3)
    if repro>TOL:raise RuntimeError(f"native reproduction {native} {repro}")
    max_norm=max(z["max_norm"] for z in results);max_dot=max(z["max_dot"] for z in results)
    if max_norm>TOL or max_dot>TOL:raise RuntimeError("continuous invariance aggregate")
    sr=[]
    for s in SEEDS:
        vals=[v for z in results for ss,v in z["rows"] if ss==s]
        if len(vals)!=470:raise RuntimeError("seed row count")
        sr.append({"seed":s,"Fractional_R3":float(np.mean(vals))})
    sdf=pd.DataFrame(sr);sdf["native_minus_intervention_pp"]=(native-sdf.Fractional_R3)*100;out.mkdir(parents=True,exist_ok=True);sdf.to_csv(out/"longmemeval_head_tail_seed_results.csv",index=False)
    mean_two=float(sdf.Fractional_R3.mean());L_full=native-b.FROZEN_FULL_HAAR_R3;L2=native-mean_two;rho2=L2/L_full
    regime="[HEAD-TAIL TWO-SUBSPACE SUFFICIENCY LEAD]" if rho2<=0.25 else ("[THREE-BAND OR FINER STRUCTURE REQUIRED LEAD]" if rho2>=0.75 else "[MIXED TWO-SUBSPACE / FINER-STRUCTURE REGIME]")
    sub=[]
    for s in SEEDS:
        for name in ["Head32","Tail64","Full96"]:
            vals=[v for z in results for ss,nn,v in z["subs"] if ss==s and nn==name];sub.append({"seed":s,"subset":name,"Fractional_R3":float(np.mean(vals))})
    pd.DataFrame(sub).to_csv(out/"longmemeval_head_tail_subset_r3.csv",index=False)
    prows=[]
    for s in SEEDS:
        for name in ["Head32","Tail64","Full96"]:
            vals=[r for z in results for r in z["pairs"] if r[0]==s and r[1]==name];N=sum(r[2] for r in vals);disc=sum(r[3] for r in vals);adv=sum(r[4] for r in vals);tie=sum(r[5] for r in vals)
            prows.append({"seed":s,"subset":name,"pair_count":N,"pairwise_gold_vs_nongold_discrimination":disc/N,"gold_minus_nongold_same_sign_advantage":adv/N,"tie_fraction":tie/N})
    pd.DataFrame(prows).to_csv(out/"longmemeval_head_tail_pairwise.csv",index=False)
    rr=[]
    for s in SEEDS:
        flags=[(hg,fg) for z in results for ss,hg,fg in z["rescue"] if ss==s];bad=sum(not hg for hg,_ in flags);badgood=sum((not hg) and fg for hg,fg in flags);good=sum(hg for hg,_ in flags);goodbad=sum(hg and (not fg) for hg,fg in flags)
        rr.append({"seed":s,"head_bad":bad,"head_good":good,"head_wrong_or_tie_to_full_rescue":badgood/bad if bad else math.nan,"head_correct_to_full_degrade":goodbad/good if good else math.nan})
    pd.DataFrame(rr).to_csv(out/"longmemeval_head_tail_hard_negative_rescue.csv",index=False)
    summary={"status":"PREREGISTERED_HEAD_TAIL_CAUSAL_RESULT","execution":"SHARDED_EXACT","benchmark":"LongMemEval","prereg_git_blob":PREREG_GIT_BLOB,"base_runner_git_blob":BASE_GIT_BLOB,
             "identity":{"dataset_sha256":b.DATASET_SHA256,"dataset_bytes":b.DATASET_BYTES,"adapter_v1_sha256":b.A1_SHA256,"adapter_v2_sha256":b.A2_SHA256,"primary_questions":470,"shards":n},
             "controls":{"native_reproduction":native,"frozen_native":b.FROZEN_NATIVE_R3,"absolute_reproduction_error":repro,"signed_permutation_exact_pass":True,"continuous_norm_max_abs_error":max_norm,"continuous_dot_max_abs_error":max_dot},
             "primary":{"native_R3":native,"frozen_full_haar_R3":b.FROZEN_FULL_HAAR_R3,"head_tail_haar_mean_R3":mean_two,"L_full":L_full,"L_2":L2,"rho_2":rho2,"regime":regime,"seed_R3":{str(int(x.seed)):float(x.Fractional_R3) for x in sdf.itertuples()}},
             "interpretation_ceiling":"Fixed-benchmark preregistered causal-intervention evidence; no population-level generalization."}
    (out/"longmemeval_head_tail_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    (out/"LONGMEMEVAL_HEAD_TAIL_CAUSAL_CHECKPOINT.md").write_text(f"# V52 LongMemEval Head32 vs Tail64 Causal Result\n\nVerdict: `{regime}`\n\nNative R@3: {native*100:.12f}%\nHead32⊕Tail64 Haar mean R@3: {mean_two*100:.12f}%\nFrozen Full-Haar R@3: {b.FROZEN_FULL_HAAR_R3*100:.12f}%\nL_full: {L_full*100:.6f} pp\nL_2: {L2*100:.6f} pp\nrho_2: {rho2:.9f}\n\nNative reproduction error: {repro:.3e}\nSigned permutation: PASS\nContinuous norm max abs error: {max_norm:.3e}\nContinuous dot max abs error: {max_dot:.3e}\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--dataset",type=Path);ap.add_argument("--shard-index",type=int);ap.add_argument("--num-shards",type=int);ap.add_argument("--shard-out",type=Path);ap.add_argument("--aggregate-dir",type=Path);ap.add_argument("--out",type=Path);a=ap.parse_args()
    if a.aggregate_dir is not None:aggregate(a.aggregate_dir,a.out)
    else:run_shard(a.dataset,a.shard_index,a.num_shards,a.shard_out)
if __name__=="__main__":main()
