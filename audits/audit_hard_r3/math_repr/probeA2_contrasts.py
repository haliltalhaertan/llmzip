import json
from collections import defaultdict
QP="/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/math_r1/quant/per_query.jsonl"
RJ="/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/math_r1/quant/RESULTS.json"
R=json.load(open(RJ))
rows=defaultdict(dict)  # (bench,arch,qid,scorer,arm)->hit
arch_of={}
with open(QP) as f:
    for line in f:
        d=json.loads(line)
        rows[(d["benchmark"],d["archive_id"],d["qid"],d["scorer"])][d["arm"]]=d["hit10"]
        arch_of[(d["benchmark"],d["archive_id"],d["qid"])]=d["archive_id"]
def meandiff(bench,scorer,new,base="FULL",metric="hit10"):
    # need fr3 too; reload for fr3
    return None
# recompute hit10 mean diffs from RESULTS summary (summary means already verified) vs contrasts mean_diff
for bench in ("RealTalk","PerLTQA"):
    summ=R["benchmarks"][bench]["summary"]
    cont=R["benchmarks"][bench].get("contrasts_vs_FULL_pp",{})
    print("==",bench,"contrast keys:",list(cont.keys())[:10])
    for ck,cv in cont.items():
        for scorer in ("sym","qscale"):
            for m in ("hit10","fr3"):
                try:
                    stored=cv[scorer][m]["mean_diff_pp"]
                except KeyError: continue
                base=summ[f"FULL/{scorer}"][("hit10_pct" if m=="hit10" else "fr3_pct")]
                new=summ[f"{ck}/{scorer}"][("hit10_pct" if m=="hit10" else "fr3_pct")]
                recom=new-base
                if abs(recom-stored)>1e-9:
                    print(f"MISMATCH {bench} {ck}/{scorer}/{m}: summary-diff={recom} stored contrast={stored}")
print("contrast-vs-summary-diff check done")
# REPORT.md spot checks (rounded): RT qscale ITQ-FULL should be 32.7659-49.6454=-16.8794 -> -16.88
print("RT qscale ITQ-FULL:",32.76595744680851-49.645390070921984)
print("RT sym ITQ-FULL det:",32.340425531914896-46.52482269503546)
print("PQ qscale ITQ-FULL:",R["benchmarks"]["PerLTQA"]["summary"]["ITQ_C/qscale"]["hit10_pct"]-R["benchmarks"]["PerLTQA"]["summary"]["FULL/qscale"]["hit10_pct"])
print("PQ sym ITQ-FULL:",R["benchmarks"]["PerLTQA"]["summary"]["ITQ_C/sym"]["hit10_pct"]-R["benchmarks"]["PerLTQA"]["summary"]["FULL/sym"]["hit10_pct"])
# Check REPORT rare-term band counts: RT FULL bands reproduce 24/224/116/341
import re
print(json.dumps(R["benchmarks"]["RealTalk"].get("mechanism",{}),indent=1)[:2000])
