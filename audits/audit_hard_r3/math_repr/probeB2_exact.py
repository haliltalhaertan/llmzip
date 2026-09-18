import json, numpy as np
QP="/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/math_r1/quant/per_query.jsonl"
RJ="/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/math_r1/quant/RESULTS.json"
R=json.load(open(RJ))
# rebuild store for RealTalk like code: keys sorted(store[(FULL,sym)]) = sorted (archive,qid)
store={(a,s):{} for a in ["FULL","ITQ_C","RAND_20260916","RAND_20260917","RAND_20260918","MED"] for s in ["sym","qscale"]}
with open(QP) as f:
    for line in f:
        d=json.loads(line)
        if d["benchmark"]!="RealTalk": continue
        store[(d["arm"],d["scorer"])][(d["archive_id"],d["qid"])]={"hit10":d["hit10"],"fr3":d["fr3"],"hit3":d["hit3"],"exp_hit10":d["exp_hit10"]}
METRICS=["hit10","fr3","hit3","exp_hit10"]
ordered=["RT%02d"%i for i in range(1,11)]
keys=sorted(store[("FULL","sym")].keys())
clusters=[k[0] for k in keys]
def cluster_contrast(diffs,clusters,ordered,rng,reps=20000):
    diffs=np.asarray(diffs,float); K=len(ordered)
    cs=np.array([diffs[np.array([c==cl for c in clusters])].sum() for cl in ordered])
    ns=np.array([sum(1 for c in clusters if c==cl) for cl in ordered],float)
    counts=rng.multinomial(K,[1.0/K]*K,size=reps).astype(float)
    boots=(counts@cs)/(counts@ns)
    return (float(diffs.mean()*100),float(np.percentile(boots,2.5)*100),float(np.percentile(boots,97.5)*100))
NEW_ARMS=["ITQ_C","RAND_20260916","RAND_20260917","RAND_20260918","MED"]
SCORERS=["sym","qscale"]
RAND_SEEDS=[20260916,20260917,20260918]
pairs=[((arm,s),("FULL",s),f"{arm}-FULL/{s}") for arm in NEW_ARMS for s in SCORERS]
pairs+=[(("ITQ_C",s),(f"RAND_{sd}",s),f"ITQ_C-RAND_{sd}/{s}") for sd in RAND_SEEDS for s in SCORERS]
rng=np.random.default_rng(20260916)
for (aa,sa),(ab,sb),name in pairs:
    da,db=store[(aa,sa)],store[(ab,sb)]
    for m in METRICS:
        diffs=np.array([da[k][m]-db[k][m] for k in keys])
        mean,lo,hi=cluster_contrast(diffs,clusters,ordered,rng)
        if name=="ITQ_C-FULL/qscale" and m=="hit10":
            st=R["benchmarks"]["RealTalk"]["itq_minus_rand_pp"][name][m]
            print("recomputed:",mean,lo,hi)
            print("stored:",st["mean_diff_pp"],st["ci95_lo_pp"],st["ci95_hi_pp"])
            print("match:",abs(mean-st["mean_diff_pp"])<1e-9 and abs(lo-st["ci95_lo_pp"])<1e-9 and abs(hi-st["ci95_hi_pp"])<1e-9)
