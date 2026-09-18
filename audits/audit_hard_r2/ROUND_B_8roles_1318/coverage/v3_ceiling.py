import json
# V3a: ceiling @100 values in rerank_ceiling.json vs REPORT section 5
c=json.load(open('/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/coordinator/rerank_ceiling.json'))
for b in ['PerLTQA','LME','REALTALK']:
    r=c['results'][b]
    print(b,'n',r['n'],'fr3_now %.2f'%r['fr3_now'],'ceil100 %.2f'%r['fr3_ceiling']['100'],'gain %+.1f'%(r['fr3_ceiling']['100']-r['fr3_now']))
print('REPORT claims: PQ 53.24->76.52 (+23.3); LME 54.27->92.62 (+38.4); RT 22.41->61.30 (+38.9)')
# V3b: decomposition 350/183/172 from firststage CODE pools
fp='/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/ideas_r1/firststage/per_query.jsonl'
rows=[json.loads(l) for l in open(fp)]
hit10=sum(1 for r in rows if set(r['code_top500'][:10])&set(r['gold']))
hit100=sum(1 for r in rows if set(r['code_top500'][:100])&set(r['gold']))
print('CODE hit@10 count',hit10,'hit@100 count',hit100,'reachable',hit100-hit10,'unreachable',len(rows)-hit100)
# both-miss 328 check: both CODE and BM25 miss @10?
bothmiss=sum(1 for r in rows if not set(r['code_top500'][:10])&set(r['gold']) and not set(r['bm25_top500'][:10])&set(r['gold']))
print('both miss @10:',bothmiss,'(REPORT: 328)')
# of both-miss, gold outside top100?
import itertools
o=sum(1 for r in rows if (not set(r['code_top500'][:10])&set(r['gold']) and not set(r['bm25_top500'][:10])&set(r['gold'])) and (not set(r['code_top500'][:100])&set(r['gold']) and not set(r['bm25_top500'][:100])&set(r['gold'])))
print('both-miss AND outside both top100:',o)
