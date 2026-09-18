import json
from collections import defaultdict
RP="/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/math_r1/repr/per_query.jsonl"
acc=defaultdict(list)
arch=defaultdict(set)
with open(RP) as f:
    for line in f:
        d=json.loads(line)
        if d["benchmark"]!="PerLTQA": continue
        acc[(d["arm"],d["scorer"])].append((d["fr3"],d["hit10"]))
        arch[d["arm"]].add(d["archive_id"])
print("PQ arms archives:", {a: len(v) for a,v in arch.items()})
def mean(v): return sum(v)/len(v)*100
for arm in ["FULL","IDF_p1","IDF_p2","SHIFT_m1"]:
    f=[x[0] for x in acc[(arm,"qscale")]]; h=[x[1] for x in acc[(arm,"qscale")]]
    ff=[x[0] for x in acc[("FULL","qscale")]]; hh=[x[1] for x in acc[("FULL","qscale")]]
    print(f"{arm}: FR3 {mean(f):.4f} d={mean(f)-mean(ff):+.4f} | Hit10 {mean(h):.4f} d={mean(h)-mean(hh):+.4f}")
import json as j
R=j.load(open('/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/coordinator/repr_results.json'))
c=R["benchmarks"]["PerLTQA"]["contrasts_vs_FULL_pp"]
for k in ["IDF_p2/qscale","SHIFT_m1/qscale","IDF_p1/qscale"]:
    print(k, j.dumps(c.get(k,{}))[:400])
