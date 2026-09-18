import json
# V1: PQ equal-budget control 33.05 — recompute from stored per_query rows (self-contained gold)
pq='/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/pq/per_query.jsonl'
n=hit=hit_stored=0; per={}; mism=0
for line in open(pq):
    r=json.loads(line); n+=1
    h_indep=1 if set(r['top10_rows'][:10])&set(r['gold_rows']) else 0
    h_stored=r['hit10']
    hit+=h_indep; hit_stored+=h_stored
    if h_indep!=h_stored: mism+=1
    per.setdefault(r['archive_id'],[0,0]); per[r['archive_id']][0]+=h_indep; per[r['archive_id']][1]+=1
print('rows',n,'indep_hit10',hit/n,'stored_hit10',hit_stored/n,'flag_mismatch',mism)
s=json.load(open('/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/pq/SUMMARY.json'))
print('SUMMARY',s['metrics_overall']['hit10'],'n',s['metrics_overall']['n'])
for a in sorted(per):
    mine=per[a][0]/per[a][1]; pub=s['per_archive_hit10'][a]['hit10']
    print(a,'mine %.4f pub %.4f diff %+.6f n=%d'%(mine,pub,mine-pub,per[a][1]))
# cross-check gold identity vs canonical data export for one archive
d=json.load(open('/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/data/RT01.json'))
print('RT01 data keys:',list(d.keys()),'n_queries',len(d['queries']),'sample',json.dumps(d['queries'][0],indent=0)[:300])
