import json, numpy as np
from collections import defaultdict
QP="/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/math_r1/quant/per_query.jsonl"
# Build per-query paired diffs for RT qscale hit10 ITQ_C - FULL, with archive clusters
full={}; new={}
arch={}
with open(QP) as f:
    for line in f:
        d=json.loads(line)
        if d["benchmark"]!="RealTalk" or d["scorer"]!="qscale": continue
        k=(d["archive_id"],d["qid"])
        arch[k]=d["archive_id"]
        if d["arm"]=="FULL": full[k]=d["hit10"]
        elif d["arm"]=="ITQ_C": new[k]=d["hit10"]
keys=sorted(set(full)&set(new))
diffs=np.array([new[k]-full[k] for k in keys])
clusters=[arch[k] for k in keys]
ordered=sorted(set(clusters))
K=len(ordered)
cs=np.array([diffs[np.array([c==cl for c in clusters])].sum() for cl in ordered])
ns=np.array([sum(1 for c in clusters if c==cl) for cl in ordered],dtype=float)
rng=np.random.default_rng(20260916)
counts=rng.multinomial(K,[1.0/K]*K,size=20000).astype(float)
boots=(counts@cs)/(counts@ns)
print("mean_diff_pp",diffs.mean()*100)
print("ci95",np.percentile(boots,2.5)*100,np.percentile(boots,97.5)*100)
print("stored: -16.8794 [-24.2120,-9.4183]")
