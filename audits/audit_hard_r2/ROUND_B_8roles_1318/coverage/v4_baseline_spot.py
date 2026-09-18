import json
from collections import defaultdict
acc=defaultdict(lambda:[0,0]); n=0
for line in open('/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/baseline/per_query_top10.jsonl'):
    r=json.loads(line); n+=1
    for arm in ['sign96','float_raw','float_std','asym']:
        h=r[arm].get('hit10',r[arm].get('hit_at_10'))
        acc[(r['benchmark'],arm)][0]+=h; acc[(r['benchmark'],arm)][1]+=1
print('rows',n)
for k in sorted(acc):
    print(k,'%.4f n=%d'%(acc[k][0]/acc[k][1],acc[k][1]))
