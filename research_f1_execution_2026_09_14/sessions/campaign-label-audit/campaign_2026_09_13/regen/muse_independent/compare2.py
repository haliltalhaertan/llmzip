import json
mine = json.load(open("/tmp/task1indep/results.json"))["loc_summ"]
other = json.load(open("/mnt/c/Users/MDP/dev/llmzip-work/regen/locomo/task1_locoMo_stats.json"))
pairs = [("sign_entropy_ge","D1_ge"),("sign_entropy_gt","D1_gt"),("zero_mass","zero_mass"),("cv_sigma","D2_cv_sigma"),
         ("D4_off_mass","D4_off_mass"),("D4_median_abs","D4_median_abs"),("D4_p95_abs","D4_p95_abs"),
         ("residual_mean_max_abs","residual_mean_max_abs" if "residual_mean_max_abs" in other else None)]
for mk, ok in pairs:
    if ok is None or ok not in other:
        print(f"{mk}: mine={mine[mk]} vs other-file KEY MISSING ({ok})"); continue
    o = other[ok]
    m = mine[mk]
    # other uses summary() keys mean/sd_ddof1/min/max; mine uses mean/sd_ddof1/min/max + n_valid
    match = all(abs(m[k]-o[k2])==0 for k,k2 in [("mean","mean"),("sd_ddof1","sd_ddof1"),("min","min"),("max","max")])
    print(f"{mk} vs {ok}: exact_match={match}")
    if not match:
        print("  mine :", {k:m[k] for k in ("mean","sd_ddof1","min","max")})
        print("  other:", {k:o[k] for k in ("mean","sd_ddof1","min","max")})
print("other keys incl residual?", [k for k in other.keys() if 'resid' in k.lower() or 'mean_max' in k.lower()])
