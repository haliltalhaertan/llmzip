import json
from collections import defaultdict
RP="/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/math_r1/repr/per_query.jsonl"
QP="/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/math_r1/quant/per_query.jsonl"
# 1. selfcheck bit-exact: IDF_p0/SHIFT_m0 top10 identical to FULL per query per scorer?
diff_p0=diff_m0=tot=0
store=defaultdict(dict)
with open(RP) as f:
    for line in f:
        d=json.loads(line)
        store[(d["benchmark"],d["archive_id"],d["qid"],d["scorer"])][d["arm"]]=(d["hit10"],d["fr3"],d["hit3"],d["exp_hit10"],tuple(d["top10"]))
for k,v in store.items():
    tot+=1
    if v["IDF_p0"]!=v["FULL"]: diff_p0+=1
    if v["SHIFT_m0"]!=v["FULL"]: diff_m0+=1
print("nkeys",tot,"IDF_p0!=FULL:",diff_p0,"SHIFT_m0!=FULL:",diff_m0)
# 2. repr FULL vs quant FULL on RealTalk: identical rows?
qstore={}
with open(QP) as f:
    for line in f:
        d=json.loads(line)
        if d["benchmark"]=="RealTalk" and d["arm"]=="FULL":
            qstore[(d["archive_id"],d["qid"],d["scorer"])]=(d["hit10"],d["fr3"],d["hit3"],d["exp_hit10"],tuple(d["top10"]))
ndiff=ntot=0
examples=[]
with open(RP) as f:
    for line in f:
        d=json.loads(line)
        if d["benchmark"]=="RealTalk" and d["arm"]=="FULL":
            ntot+=1
            q=(d["hit10"],d["fr3"],d["hit3"],d["exp_hit10"],tuple(d["top10"]))
            if q!=qstore[(d["archive_id"],d["qid"],d["scorer"])]:
                ndiff+=1
                if len(examples)<3: examples.append((d["archive_id"],d["qid"],d["scorer"],q,qstore[(d["archive_id"],d["qid"],d["scorer"])]))
print("RT FULL repr-vs-quant rows:",ntot,"diffs:",ndiff)
for e in examples: print(e)
# 3. PerLTQA subset FULL vs quant FULL on overlapping 2967 qids
qstore2={}
with open(QP) as f:
    for line in f:
        d=json.loads(line)
        if d["benchmark"]=="PerLTQA" and d["arm"]=="FULL":
            qstore2[(d["archive_id"],d["qid"],d["scorer"])]=(d["hit10"],d["fr3"],d["hit3"],d["exp_hit10"],tuple(d["top10"]))
ndiff2=ntot2=0
with open(RP) as f:
    for line in f:
        d=json.loads(line)
        if d["benchmark"]=="PerLTQA" and d["arm"]=="FULL":
            ntot2+=1
            q=(d["hit10"],d["fr3"],d["hit3"],d["hit3"],tuple(d["top10"]))
            ref=qstore2.get((d["archive_id"],d["qid"],d["scorer"]))
            if ref is None:
                print("MISSING qid in quant:",d["archive_id"],d["qid"]); break
            if (d["hit10"],d["fr3"],d["hit3"],d["exp_hit10"],tuple(d["top10"]))!=ref:
                ndiff2+=1
print("PQ-subset FULL repr-vs-quant rows:",ntot2,"diffs:",ndiff2)
