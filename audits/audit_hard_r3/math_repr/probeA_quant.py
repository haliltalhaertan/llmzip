import json, collections
QP="/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/math_r1/quant/per_query.jsonl"
RJ="/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/math_r1/quant/RESULTS.json"
R=json.load(open(RJ))
# recompute means from raw rows
from collections import defaultdict
acc=defaultdict(list)
acc_fr=defaultdict(list)
acc_h3=defaultdict(list)
acc_ex=defaultdict(list)
nrows=0
with open(QP) as f:
    for line in f:
        d=json.loads(line)
        k=(d["benchmark"],d["arm"],d["scorer"])
        acc[k].append(d["hit10"]); acc_fr[k].append(d["fr3"]); acc_h3[k].append(d["hit3"]); acc_ex[k].append(d["exp_hit10"])
        nrows+=1
print("rows",nrows)
# compare to RESULTS summary
mism=0
for bench in ("RealTalk","PerLTQA"):
    summ=R["benchmarks"][bench]["summary"]
    for key,v in summ.items():
        arm,scorer=key.split("/")
        k=(bench,arm,scorer)
        m=sum(acc[k])/len(acc[k])*100
        mf=sum(acc_fr[k])/len(acc_fr[k])*100
        mh=sum(acc_h3[k])/len(acc_h3[k])*100
        me=sum(acc_ex[k])/len(acc_ex[k])*100
        for name,obs,stored in (("hit10",m,v["hit10_pct"]),("fr3",mf,v["fr3_pct"]),("hit3",mh,v["hit3_pct"]),("exp",me,v["exp_hit10_pct"])):
            if abs(obs-stored)>1e-9:
                print(f"MISMATCH {bench} {key} {name}: recomputed={obs!r} stored={stored!r} diff={obs-stored:.3e}")
                mism+=1
print("mismatches:",mism)
# check REPORT.md headline numbers vs recomputed
# REPORT quotes: RT FULL qscale 49.65, sym det 46.52/exp 46.68, ITQ qscale 32.77, etc.
checks=[(("RealTalk","FULL","qscale"),49.645390070921984),(("RealTalk","FULL","sym"),46.52482269503546),
 (("RealTalk","ITQ_C","qscale"),32.76595744680851),(("RealTalk","ITQ_C","sym"),32.340425531914896),
 (("PerLTQA","FULL","qscale"),80.0),(("PerLTQA","FULL","sym"),75.68058076225044)]
for k,target in checks:
    m=sum(acc[k])/len(acc[k])*100
    print(k, f"{m:.6f}", "target~", target, "diff:", m-target)
# row-count check
from collections import Counter
c=Counter()
with open(QP) as f:
    for line in f:
        d=json.loads(line); c[(d["benchmark"],d["arm"],d["scorer"])]+=1
print(sorted(c.items())[:6]); print("RT n=",c[("RealTalk","FULL","sym")],"PQ n=",c[("PerLTQA","FULL","sym")])
