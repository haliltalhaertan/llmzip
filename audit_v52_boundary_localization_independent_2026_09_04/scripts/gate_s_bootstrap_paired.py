#!/usr/bin/env python3
"""
Gate S (corrected) — question-level bootstrap done PAIRED.

L_b = R_native - R_b is a per-question paired difference: the same question
contributes to both terms, and they are strongly positively correlated. The
naive unpaired bootstrap therefore OVERSTATES the uncertainty. Here the
per-question quantity resampled is  delta_q = native_q - Rb_q  directly.

The denominator L_full stays fixed: Full-Haar was never persisted per question,
so every interval below is explicitly CONDITIONAL on that inherited denominator
(exactly the limitation the package itself declares).
"""
import csv, gzip, json, math
import numpy as np

FROZEN={"LoCoMo":{"native":0.23654714666441054,"full":0.13770827054136,
                  "pq":"research/v52/locomo_boundary_outputs/locomo_boundary_per_question.csv.gz"},
        "LongMemEval":{"native":0.5419751773049646,"full":0.38271666666667,
                  "pq":"research/v52/longmemeval_boundary_outputs/longmemeval_boundary_per_question.csv.gz"}}
ROT=list(range(58001,58011)); B=[16,24,32,48,64]; TH=0.25; NB=20000
out={}
for ds,cfg in FROZEN.items():
    rows=list(csv.DictReader(gzip.open(cfg["pq"],"rt",newline="")))
    qids=sorted({r["question_id"] for r in rows}); qix={q:i for i,q in enumerate(qids)}
    arms=sorted({r["arm"] for r in rows}); nq=len(qids)
    M={a:np.zeros((nq,10)) for a in arms}; nat=np.zeros(nq)
    for r in rows:
        M[r["arm"]][qix[r["question_id"]],ROT.index(int(r["rotation_seed"]))]=float(r["fractional_R3"])
        nat[qix[r["question_id"]]]=float(r["native_fractional_R3"])
    Lf=cfg["native"]-cfg["full"]
    rng=np.random.default_rng(20260904); idx=rng.integers(0,nq,size=(NB,nq))
    d={}
    for a in arms:
        delta=nat-M[a].mean(axis=1)              # paired per-question loss
        rho_hat=delta.mean()/Lf
        boot=delta[idx].mean(axis=1)/Lf          # paired bootstrap
        # correlation between native and arm, to show why pairing matters
        corr=float(np.corrcoef(nat,M[a].mean(axis=1))[0,1])
        d[a]={"rho_point":float(rho_hat),
              "boot_se":float(boot.std(ddof=1)),
              "ci95":[float(np.percentile(boot,2.5)),float(np.percentile(boot,97.5))],
              "P(rho<=0.25)":float((boot<=TH).mean()),
              "native_arm_question_corr":corr}
    out[ds]=d

# joint: does S_common stay {32}?  resample questions on BOTH datasets independently
joint={}
data={}
for ds,cfg in FROZEN.items():
    rows=list(csv.DictReader(gzip.open(cfg["pq"],"rt",newline="")))
    qids=sorted({r["question_id"] for r in rows}); qix={q:i for i,q in enumerate(qids)}
    nq=len(qids); nat=np.zeros(nq); M={f"B{b}":np.zeros((nq,10)) for b in B}
    for r in rows:
        if r["arm"] in M: M[r["arm"]][qix[r["question_id"]],ROT.index(int(r["rotation_seed"]))]=float(r["fractional_R3"])
        nat[qix[r["question_id"]]]=float(r["native_fractional_R3"])
    data[ds]=(nat,M,nq,cfg["native"]-cfg["full"])
rng=np.random.default_rng(7771)
counts={}
for _ in range(NB):
    S={}
    for ds,(nat,M,nq,Lf) in data.items():
        i=rng.integers(0,nq,nq)
        S[ds]={b for b in B if ((nat[i]-M[f"B{b}"][i].mean(axis=1)).mean()/Lf)<=TH}
    key=tuple(sorted(S["LoCoMo"]&S["LongMemEval"]))
    counts[key]=counts.get(key,0)+1
joint={"S_common_distribution":{str(list(k)):v/NB for k,v in sorted(counts.items(),key=lambda z:-z[1])}}
out["_joint"]=joint
json.dump(out,open("audit_v52_boundary_localization_independent_2026_09_04/evidence/gate_s_bootstrap_paired.json","w"),indent=2)

for ds in ("LoCoMo","LongMemEval"):
    print(f"\n===== {ds} — PAIRED question bootstrap (conditional on frozen L_full) =====")
    for a in ["B16","B24","B32","B48","B64","RANDOM32"]:
        v=out[ds][a]
        print(f"  {a:9s} rho={v['rho_point']:.4f} bootSE={v['boot_se']:.4f} "
              f"CI95=[{v['ci95'][0]:+.4f},{v['ci95'][1]:+.4f}]  P(suff)={v['P(rho<=0.25)']:.4f}  "
              f"corr(nat,arm)={v['native_arm_question_corr']:.3f}")
print("\n===== JOINT: bootstrap distribution of S_common =====")
for k,v in out["_joint"]["S_common_distribution"].items():
    print(f"  S_common={k:12s} {v*100:6.2f}%")
