import json
from collections import defaultdict
hit=defaultdict(dict)
n=0
for line in open('/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/math_r1/repr/per_query.jsonl'):
    r=json.loads(line)
    if r.get('benchmark')=='RealTalk' and r.get('arm')=='FULL' and r.get('scorer') in ('sym','qscale'):
        hit[r['qid']][r['scorer']]=r['hit10']
pool={}
for line in open('/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/ideas_r1/firststage/per_query.jsonl'):
    r=json.loads(line)
    pool[r['qid']]=(set(r['code_top500'][:100]),set(r['gold']))
both=[q for q,d in hit.items() if d.get('sym')==0.0 and d.get('qscale')==0.0]
print('qids with both scorers:',len(hit),'both-miss:',len(both))
in100=sum(1 for q in both if pool[q][0]&pool[q][1])
print('in_top100:',in100,'outside:',len(both)-in100)
