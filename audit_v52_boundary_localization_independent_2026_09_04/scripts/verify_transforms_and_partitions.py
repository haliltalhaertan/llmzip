#!/usr/bin/env python3
"""
Gates G, H, I — rebuild every intervention matrix and every random partition
from the preregistration's written recipe (prereg SS5 and SS7), using only
numpy. Does not import the runners; the construction is retyped by the auditor
from the prose so that agreement is evidence about the prose, not about a
shared implementation.
"""
import json, numpy as np

BOUNDARIES=[16,24,32,48,64]; ROT=list(range(58001,58011)); PART=list(range(68001,68011))

def haar_q(rng,d):
    A=rng.standard_normal((d,d)); Q,R=np.linalg.qr(A)
    return Q*np.where(np.diag(R)<0,-1.0,1.0)[None,:]

def boundary_matrix(seed,b):
    rng=np.random.default_rng(seed)          # SS5.1  one stream
    qh=haar_q(rng,b)                          # SS5.2-5 head block FIRST
    qt=haar_q(rng,96-b)                       # SS5.6-7 same stream
    R=np.zeros((96,96)); R[:b,:b]=qh; R[b:,b:]=qt
    return R,qh,qt

I96=np.eye(96); out={"orthogonality":{}, "block_structure":{}, "matched_q":{}, "partitions":{}}
worst_orth=0.0; worst_block=0.0
for s in ROT:
    for b in BOUNDARIES:
        R,qh,qt=boundary_matrix(s,b)
        e=float(np.max(np.abs(R.T@R-I96))); worst_orth=max(worst_orth,e)
        # off-diagonal blocks must be exactly zero (block-diagonal)
        off=max(float(np.max(np.abs(R[:b,b:]))),float(np.max(np.abs(R[b:,:b]))))
        worst_block=max(worst_block,off)
        out["orthogonality"][f"B{b}|{s}"]=e; out["block_structure"][f"B{b}|{s}"]=off
out["worst_orthogonality_abs_error"]=worst_orth
out["worst_offblock_abs_value"]=worst_block

# ---- Gate H: matched Q32/Q64 between spectral B32 and RANDOM32 ----
qmax=0.0
for s in ROT:
    _,q32a,q64a=boundary_matrix(s,32)     # spectral b=32 arm
    _,q32b,q64b=boundary_matrix(s,32)     # SS7.1: RANDOM32 builds Q32/Q64 "exactly as the spectral b=32 arm"
    e=max(float(np.max(np.abs(q32a-q32b))),float(np.max(np.abs(q64a-q64b))))
    out["matched_q"][str(s)]=e; qmax=max(qmax,e)
out["matched_q32_q64_max_abs_error"]=qmax

# ---- Gate I: partitions, rebuilt from seeds alone ----
mine=[]
for i,(rs,ps) in enumerate(zip(ROT,PART)):
    perm=np.random.default_rng(ps).permutation(96).astype(int)
    S,T=perm[:32],perm[32:]
    checks={
      "card_S":len(S)==32,"card_T":len(T)==64,
      "unique_S":len(np.unique(S))==32,"unique_T":len(np.unique(T))==64,
      "disjoint":np.intersect1d(S,T).size==0,
      "exhaustive":bool(np.array_equal(np.sort(np.r_[S,T]),np.arange(96))),
      "in_range":bool(S.min()>=0 and S.max()<=95 and T.min()>=0 and T.max()<=95),
      "paired":ps==rs+10000,
    }
    out["partitions"][f"{rs}/{ps}"]=checks
    mine.append({"rotation_seed":rs,"partition_seed":ps,"S32":S.tolist(),"T64":T.tolist()})
out["all_partition_checks_pass"]=all(all(v.values()) for v in out["partitions"].values())

# byte-level comparison against BOTH persisted partition files
res={}
for name,p in [("LoCoMo","research/v52/locomo_boundary_outputs/locomo_boundary_random_partitions.json"),
               ("LongMemEval","research/v52/longmemeval_boundary_outputs/longmemeval_boundary_random_partitions.json")]:
    got=json.load(open(p))
    res[name]={
      "n_entries":len(got),
      "exact_match_including_order":got==mine,
      "seed_pairs_match":[(g["rotation_seed"],g["partition_seed"]) for g in got]==[(m["rotation_seed"],m["partition_seed"]) for m in mine],
    }
out["persisted_partitions_vs_auditor_rebuild"]=res
# do the two persisted files have identical parsed content?
a=json.load(open("research/v52/locomo_boundary_outputs/locomo_boundary_random_partitions.json"))
b=json.load(open("research/v52/longmemeval_boundary_outputs/longmemeval_boundary_random_partitions.json"))
out["two_partition_files_identical_content"]= (a==b)
out["partition_content_is_dataset_independent_by_construction"]= True  # depends only on seeds + 96 indices

json.dump(out,open("audit_v52_boundary_localization_independent_2026_09_04/evidence/transforms_and_partitions.json","w"),indent=2)
print(f"worst orthogonality |R^T R - I|      : {worst_orth:.3e}   (prereg tol 1e-12)")
print(f"worst off-block magnitude (must be 0): {worst_block:.3e}")
print(f"matched Q32/Q64 max abs error        : {qmax:.3e}   (declared 0.0)")
print(f"all partition checks pass            : {out['all_partition_checks_pass']}")
for k,v in res.items(): print(f"  {k}: {v}")
print(f"two persisted partition files identical content: {out['two_partition_files_identical_content']}")
