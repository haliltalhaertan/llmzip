import json
from collections import Counter, defaultdict
RP="/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/math_r1/repr/per_query.jsonl"
acc=defaultdict(list)
counts=Counter()
archq=defaultdict(set)
with open(RP) as f:
    for line in f:
        d=json.loads(line)
        acc[(d["benchmark"],d["arm"],d["scorer"])].append((d["hit10"],d["fr3"],d["hit3"],d["exp_hit10"]))
        counts[(d["benchmark"],d["arm"],d["scorer"])]+=1
        archq[(d["benchmark"],d["archive_id"])].add(d["qid"])
print("total rows check done")
for bench in ("RealTalk","PerLTQA"):
    print("==",bench)
    for arm in ["FULL","IDF_p0","IDF_p0.5","IDF_p1","IDF_p2","SHIFT_m0","SHIFT_m1","SHIFT_m2","SHIFT_m4"]:
        for scorer in ["sym","qscale"]:
            v=acc.get((bench,arm,scorer),[])
            if not v: print(arm,scorer,"MISSING"); continue
            m=sum(x[0] for x in v)/len(v)*100
            print(f"{arm:9s}/{scorer:6s} n={len(v):5d} hit10={m:.4f}")
print("--- archive coverage ---")
for k in sorted(archq):
    print(k,len(archq[k]))
