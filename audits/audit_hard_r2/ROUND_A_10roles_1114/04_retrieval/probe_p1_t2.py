"""04_retrieval probe P1: T2 CSV inventory + _rrf60 quantification + denominator checks.
Reads stored T2 CSV (read-only) and DECISION_TESTS.json copy in own dir.
Own arithmetic throughout; no source imports.
"""
import csv, json
from collections import Counter, defaultdict

CSV = ("/mnt/c/Users/MDP/dev/llmzip-work/incoming_20260916b/extracted/"
       "LLMZIP_FIKIR1_METIN_YENIDEN_SIRALAMA_2026-09-16/LLMZIP_FIKIR1_2026-09-16/"
       "results/text_rerank_per_query.csv")
DT = json.load(open("/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/04_retrieval/DECISION_TESTS.orig.json"))

rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
print(f"csv_data_rows={len(rows)} (file lines incl header = {len(rows)+1})")
print(f"columns={list(rows[0].keys())}")
ds = Counter(r["dataset"] for r in rows)
print("rows_per_dataset=" + json.dumps(dict(ds)))
meth = defaultdict(Counter)
for r in rows:
    meth[r["dataset"]][r["method"]] += 1
for d in sorted(meth):
    print(f"{d} methods(n distinct qids per method):")
    for m in sorted(meth[d]):
        nq = len({r['qid'] for r in rows if r['dataset']==d and r['method']==m})
        print(f"  {m:22s} rows={meth[d][m]} n_qids={nq}")
# denominator cross-check vs DECISION_TESTS.json
for d in sorted(ds):
    qids_csv = {r['qid'] for r in rows if r['dataset']==d and r['method']=='BM25_full'}
    n_json = DT['T2_rerank'][d]['n_queries'] if d in DT['T2_rerank'] else None
    print(f"{d}: BM25_full distinct qids={len(qids_csv)} vs DECISION_TESTS n_queries={n_json} match={len(qids_csv)==n_json}")
# verify levels arithmetic from CSV (mean fr3 per ds,method) vs stored levels
print("\n--- level verification (CSV mean vs stored, pp) ---")
maxdiff = 0
for d, v in DT['T2_rerank'].items():
    for m, stored in v['levels_fr3'].items():
        vals = [float(r['fr3']) for r in rows if r['dataset']==d and r['method']==m]
        mine = 100*sum(vals)/len(vals) if vals else float('nan')
        diff = abs(mine-stored)
        maxdiff = max(maxdiff, diff)
        flag = "OK" if diff < 1e-9 else "DIFF"
        print(f"  {d}/{m}: mine={mine:.6f} stored={stored:.6f} diff={diff:.2e} {flag}")
print(f"max_level_diff={maxdiff:.2e}")
# _rrf60 C3-style contrasts vs BM25 alone (point estimates; CIs in stored JSON only cover _bm25)
print("\n--- _rrf60 point contrasts vs BM25_full (FR@3 pp; no CI recomputed here) ---")
for d, v in DT['T2_rerank'].items():
    base = v['levels_fr3']['BM25_full']
    for m in sorted(v['levels_fr3']):
        if m.endswith('_rrf60'):
            print(f"  {d} {m}: {v['levels_fr3'][m]-base:+.4f} (levels {v['levels_fr3'][m]:.4f} vs BM25 {base:.4f})")
# inversion recomputation from stored first_stage_order
print("\n--- inversion + spread recomputation from stored levels ---")
for d, v in DT['T2_rerank'].items():
    pairs = [(r['stage'], r['fr3_before'], r['after']) for r in v['first_stage_order']]
    inv = sum(1 for i in range(len(pairs)) for j in range(i+1, len(pairs)) if pairs[i][2] < pairs[j][2])
    befores = [p[1] for p in pairs]; afters = [p[2] for p in pairs]
    print(f"  {d}: stored_inv={v['order_inversions']}/10 recomputed={inv} match={inv==v['order_inversions']}; "
          f"pre_spread={max(befores)-min(befores):.2f} post_spread={max(afters)-min(afters):.2f}")
# candidate depth field
import statistics
depths = defaultdict(list)
for r in rows:
    try: depths[(r['dataset'], r['method'])].append(int(r['actual_candidates']))
    except: pass
print("\n--- actual_candidates distribution (min/med/max per ds,method sample) ---")
for k in sorted(depths):
    v = depths[k]
    print(f"  {k[0]}/{k[1]}: n={len(v)} min={min(v)} med={statistics.median(v)} max={max(v)} n_docs_sample={rows[0].get('n_docs')}")
    if len([kk for kk in depths if kk[0]==k[0]]) > 6: pass
print("\n--- n_docs vs actual_candidates check (first 2 rows per dataset) ---")
seen = set()
for r in rows:
    k = (r['dataset'], r['method'])
    if k in seen: continue
    seen.add(k)
    print(f"  {k[0]}/{k[1]}: n_docs={r['n_docs']} actual_candidates={r['actual_candidates']} gold_count={r['gold_count']}")
    if len(seen) > 15: break
