import json
R=json.load(open('/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/math_r1/quant/RESULTS.json'))
# 1. ITQ loss decreased on all 40 archives?
bad=[]
for bench in ("RealTalk","PerLTQA"):
    d=R["benchmarks"][bench]["itq_diagnostics"]
    print(bench,"n_arch:",len(d))
    for arch,v in d.items():
        if not (v["loss_final"]<v["loss_init"]):
            bad.append((bench,arch,v))
print("loss not decreased:",bad if bad else "NONE - holds on all 40")
# show RT01 values
print("RT01:",R["benchmarks"]["RealTalk"]["itq_diagnostics"]["RT01"])
# 2. bit balance
print(json.dumps(R["benchmarks"]["RealTalk"]["bit_balance"],indent=1))
print(json.dumps(R["benchmarks"]["PerLTQA"]["bit_balance"],indent=1))
# REPORT claims: FULL 0.492 / RT-min 0.309, PQ-min 0.220, max 0.66; ITQ/RAND mean~0.5 min~0.44/0.41; MED 0.5/0.5/0.502
# 3. cost
print(json.dumps(R["benchmarks"]["RealTalk"]["cost"],indent=1))
print(json.dumps(R["benchmarks"]["PerLTQA"]["cost"],indent=1))
# verify: 96*96*4=36864, *10=368640; payload 8944*12=107328; PQ 12288*12=147456
print("arith:",96*96*4,96*96*4*10,8944*12,96*96*4*30,12288*12)
# 4. ITQ-minus-random RT qscale
for k in ["ITQ_C-RAND_20260916/qscale","ITQ_C-RAND_20260917/qscale","ITQ_C-RAND_20260918/qscale"]:
    v=R["benchmarks"]["RealTalk"]["itq_minus_rand_pp"][k]["hit10"]
    print(k, round(v["mean_diff_pp"],2), round(v["ci95_lo_pp"],2), round(v["ci95_hi_pp"],2))
# 5. stratification
print(json.dumps(R["benchmarks"]["RealTalk"]["stratification_best_vs_FULL"],indent=1)[:2500])
