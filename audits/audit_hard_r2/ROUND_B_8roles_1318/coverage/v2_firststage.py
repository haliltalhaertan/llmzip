import json
fp='/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/ideas_r1/firststage/per_query.jsonl'
rows=[json.loads(l) for l in open(fp)]
def hit(pool,gold,M): return 1 if set(pool[:M])&set(gold) else 0
for M in [10,100]:
    for arm in ['code_top500','bm25_top500','rrf_top500']:
        h=sum(hit(r[arm],r['gold'],M) for r in rows)/len(rows)*100
        print(f'M={M} {arm} poolhit={h:.4f}')
# complementarity at 100
cb=sum(1 for r in rows if set(r['code_top500'][:100])&set(r['gold']) and not set(r['bm25_top500'][:100])&set(r['gold']))
bc=sum(1 for r in rows if set(r['bm25_top500'][:100])&set(r['gold']) and not set(r['code_top500'][:100])&set(r['gold']))
both=sum(1 for r in rows if set(r['code_top500'][:100])&set(r['gold']) and set(r['bm25_top500'][:100])&set(r['gold']))
neither=sum(1 for r in rows if not set(r['code_top500'][:100])&set(r['gold']) and not set(r['bm25_top500'][:100])&set(r['gold']))
print('M=100 code_only',cb,'bm25_only',bc,'both',both,'neither',neither,'n',len(rows))
# own hit@10 check
for arm in ['CODE','BM25','RRF']:
    h=sum(1 for r in rows if set(r['own'][arm]['top10'] if isinstance(r['own'][arm],dict) else [])&set(r['gold'])) if isinstance(r['own'],dict) else 0
print('own keys sample:',json.dumps(rows[0]['own'],indent=0)[:400])
print('pool_metrics sample:',json.dumps(rows[0]['pool_metrics'],indent=0)[:400])
