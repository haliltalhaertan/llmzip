#!/usr/bin/env python3
"""Faiss JSON self-consistency: summary vs per-q means, W/T/L recompute, masks."""
import json, math
import numpy as np
W=__import__("pathlib").Path("/mnt/c/Users/MDP/dev/llmzip-work")
d=json.load(open(W/"race_2026-09-13/official_run/faiss/race_faiss_details.json"))
nat_lme=d["native"]["lme_per_q"]; nat_lo=d["native"]["locomo_per_q"]
TOL=1e-12
print("arms:",list(d["arms_summary"].keys()))
worst_mean=0.0; worst_wtl=None
for name,s in d["arms_summary"].items():
    pq=d["arms_per_q"][name]
    ml=float(np.mean(list(pq["lme"].values())))
    vs=[v for v in pq["locomo"].values() if v is not None and not (isinstance(v,float) and math.isnan(v))]
    mo=float(np.mean(vs))
    dm_lme=ml-s["LME_FR"]; dm_lo=mo-s["LoCoMo_FR"]
    worst_mean=max(worst_mean,abs(dm_lme),abs(dm_lo))
    # WTL recompute
    for bench,nat in (("LME",nat_lme),("LoCoMo",nat_lo)):
        per=pq["lme"] if bench=="LME" else pq["locomo"]
        qs=[q for q in nat if q in per and per[q] is not None and not (isinstance(per[q],float) and math.isnan(per[q])) and not (isinstance(nat[q],float) and math.isnan(nat[q]))]
        gap=np.array([per[q]-nat[q] for q in qs])
        Wc=int(np.sum(gap>TOL)); Tc=int(np.sum(np.abs(gap)<=TOL)); Lc=int(np.sum(gap<-TOL))
        key="WTL_vs_SIGN_LME" if bench=="LME" else "WTL_vs_SIGN_LoCoMo"
        st=s[key]
        ok=(Wc==st["W"] and Tc==st["T"] and Lc==st["L"] and len(qs)==st["n"])
        mg=float(np.mean(gap)*100) if len(gap) else float("nan")
        ok2=abs(mg-st["mean_gap_pp"])<=1e-9
        print(f"{name} {bench}: mean diff={dm_lme if bench=='LME' else dm_lo!r} WTL mine={Wc}/{Tc}/{Lc} stored={st['W']}/{st['T']}/{st['L']} n={len(qs)}/{st['n']} gap_pp diff={mg-st['mean_gap_pp']!r} -> {'EXACT' if (ok and ok2) else 'DIFF'}")
    print(f"  {name}: masked={s['masked']} n_lme={s['LME_n']} n_loco={s['LoCoMo_n']}")
print("worst summary-vs-perq mean abs diff:",repr(worst_mean))
# mask stats
print("A6 masked:",d["arms_summary"]["A6_PQ"]["masked"])
# codes persistence?
print("has per-archive codes in JSON:", any("codes" in str(k).lower() for k in d["arms_per_q"].keys()))
import pickle
print("smoke S4 min-N:",d["smokes"]["S4"]["lme_min_N"],d["smokes"]["S4"]["lme_min_qid"],d["smokes"]["S4"]["locomo_min_N"],d["smokes"]["S4"]["locomo_min_arch"])
print("S5:",{k:v for k,v in d["smokes"]["S5"].items() if 'verdict' in k or 'identical' in k})
