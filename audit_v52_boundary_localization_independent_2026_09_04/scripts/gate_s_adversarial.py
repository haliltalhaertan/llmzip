#!/usr/bin/env python3
"""
Gate S — the strongest case AGAINST the localization result, quantified.

Five attacks, each computed from the persisted per-question records:
  S1  ten-seed mean as an estimator: margin to the 0.25 threshold in SE units
  S2  question-level bootstrap (the seed panel is NOT the only sampling source)
  S3  sensitivity to the inherited, unquantified Full-Haar denominator
  S4  paired per-seed B32-vs-B48 comparison (shared seeds -> paired test)
  S5  how many seeds would have to move to flip S_common
NOT a new experiment: pure re-arithmetic on frozen persisted outcomes.
"""
import csv, gzip, json, math, statistics
from collections import defaultdict
import numpy as np

FROZEN={"LoCoMo":{"native":0.23654714666441054,"full":0.13770827054136,
                  "pq":"research/v52/locomo_boundary_outputs/locomo_boundary_per_question.csv.gz"},
        "LongMemEval":{"native":0.5419751773049646,"full":0.38271666666667,
                  "pq":"research/v52/longmemeval_boundary_outputs/longmemeval_boundary_per_question.csv.gz"}}
B=[16,24,32,48,64]; ROT=list(range(58001,58011)); TH=0.25
out={}
for ds,cfg in FROZEN.items():
    rows=list(csv.DictReader(gzip.open(cfg["pq"],"rt",newline="")))
    qids=sorted({r["question_id"] for r in rows}); qix={q:i for i,q in enumerate(qids)}
    arms=sorted({r["arm"] for r in rows})
    M={a:np.zeros((len(qids),len(ROT))) for a in arms}       # question x seed
    for r in rows:
        M[r["arm"]][qix[r["question_id"]], ROT.index(int(r["rotation_seed"]))]=float(r["fractional_R3"])
    n=cfg["native"]; Lf=n-cfg["full"]; d={}

    # ---- S1 margin to threshold in seed-panel SE units ----
    s1={}
    for a in arms:
        per_seed=M[a].mean(axis=0); rho=(n-per_seed)/Lf
        se=statistics.stdev(rho)/math.sqrt(10); m=rho.mean()
        s1[a]={"mean_rho":m,"se":se,"margin_to_0.25_in_SE":(TH-m)/se,
               "sufficient":bool(m<=TH)}
    d["S1_seed_panel"]=s1

    # ---- S2 question-level bootstrap (resample questions, keep all 10 seeds) ----
    rng=np.random.default_rng(20260904); Bn=4000
    idx=rng.integers(0,len(qids),size=(Bn,len(qids)))
    s2={}
    for a in arms:
        col=M[a].mean(axis=1)                     # per-question, averaged over seeds
        boot=col[idx].mean(axis=1)                # bootstrap dist of R_a
        rb=(n-boot)/Lf
        s2[a]={"rho_mean":float(rb.mean()),
               "ci95":[float(np.percentile(rb,2.5)),float(np.percentile(rb,97.5))],
               "P(rho<=0.25)":float((rb<=TH).mean())}
    d["S2_question_bootstrap"]=s2

    # ---- S3 Full-Haar denominator sensitivity ----
    s3={}
    for b in B:
        Rb=M[f"B{b}"].mean()
        # rho_b <= .25  <=>  (n-Rb) <= .25 (n-full)  <=>  full <= n - 4(n-Rb)
        crit=n-4.0*(n-Rb)
        s3[f"B{b}"]={"R_b":float(Rb),"critical_full_haar":float(crit),
                     "actual_full_haar":cfg["full"],
                     "shift_needed":float(crit-cfg["full"]),
                     "relative_shift_pct":float(100*(crit-cfg["full"])/cfg["full"]),
                     "currently_sufficient":bool(cfg["full"]<=crit)}
    d["S3_full_haar_sensitivity"]=s3

    # ---- S4 paired per-seed B32 vs B48 ----
    r32=(n-M["B32"].mean(axis=0))/Lf; r48=(n-M["B48"].mean(axis=0))/Lf
    diff=r48-r32; sd=statistics.stdev(diff)
    d["S4_paired_B32_vs_B48"]={
        "mean_rho32":float(r32.mean()),"mean_rho48":float(r48.mean()),
        "mean_paired_diff":float(diff.mean()),"sd_diff":float(sd),
        "se_diff":float(sd/math.sqrt(10)),
        "t_stat":float(diff.mean()/(sd/math.sqrt(10))),
        "n_seeds_where_B48_better_than_B32":int((diff<0).sum())}

    # ---- S5 how many seeds must move to flip membership ----
    s5={}
    for b in B:
        rho=(n-M[f"B{b}"].mean(axis=0))/Lf; srt=np.sort(rho)
        if rho.mean()<=TH:   # currently in: how far must the mean rise
            s5[f"B{b}"]={"status":"IN","mean":float(rho.mean()),
                         "total_rho_mass_to_add_to_exceed":float(10*(TH-rho.mean()))}
        else:
            s5[f"B{b}"]={"status":"OUT","mean":float(rho.mean()),
                         "total_rho_mass_to_remove_to_qualify":float(10*(rho.mean()-TH)),
                         "min_seed_rho":float(srt[0])}
    d["S5_flip_distance"]=s5
    out[ds]=d

json.dump(out,open("audit_v52_boundary_localization_independent_2026_09_04/evidence/gate_s_adversarial.json","w"),indent=2)
for ds in out:
    print(f"\n================ {ds} ================")
    print(" S1 seed-panel margin to 0.25 (in SE):")
    for a,v in out[ds]["S1_seed_panel"].items():
        print(f"    {a:9s} rho={v['mean_rho']:.4f} se={v['se']:.4f} margin={v['margin_to_0.25_in_SE']:+7.2f} SE  suff={v['sufficient']}")
    print(" S2 question-level bootstrap 95% CI on rho:")
    for a,v in out[ds]["S2_question_bootstrap"].items():
        print(f"    {a:9s} [{v['ci95'][0]:.4f},{v['ci95'][1]:.4f}]  P(rho<=.25)={v['P(rho<=0.25)']:.4f}")
    print(" S3 Full-Haar denominator shift needed to change sufficiency:")
    for a,v in out[ds]["S3_full_haar_sensitivity"].items():
        print(f"    {a:9s} suff={str(v['currently_sufficient']):5s} needs R_full shift {v['shift_needed']:+.5f} ({v['relative_shift_pct']:+.1f}%)")
    s4=out[ds]["S4_paired_B32_vs_B48"]
    print(f" S4 paired B48-B32 diff = {s4['mean_paired_diff']:+.4f} (t={s4['t_stat']:+.2f}), "
          f"seeds where B48<B32: {s4['n_seeds_where_B48_better_than_B32']}/10")
