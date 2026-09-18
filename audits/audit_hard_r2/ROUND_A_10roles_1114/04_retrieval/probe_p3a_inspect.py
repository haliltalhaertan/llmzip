"""04_retrieval probe P3: candidate recall + rerank ceiling from firststage per-query rows.
Own arithmetic on stored per_query.jsonl.gz (705 rows, CODE/BM25/RRF top-500 lists).
Verifies REPORT §4-5: 350 hit@10 / 183 reachable / 172 unreachable; 49 CODE-only / 67 BM25-only @100.
"""
import gzip, json
from collections import Counter

P = ("/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10/research_top10_comparison_2026_09_16/"
     "ideas_r1/firststage/per_query.jsonl.gz")
rows = [json.loads(l) for l in gzip.open(P, "rt", encoding="utf-8")]
print(f"n_rows={len(rows)} keys={sorted(rows[0].keys())}")
r0 = rows[0]
for k, v in r0.items():
    s = json.dumps(v)
    print(f"  {k}: {s[:160]}")

def pool_hit(lst, gold, M):
    return 1.0 if (set(lst[:M]) & set(gold)) else 0.0

def ceil_fr3(lst, gold, M):
    found = len(set(lst[:M]) & set(gold))
    return min(3, found) / len(gold)

for M in (10, 50, 100):
    for arm in ("CODE", "BM25", "RRF"):
        key = {"CODE": "code", "BM25": "bm25", "RRF": "rrf"}.get(arm, arm)
        cands = [k for k in r0.keys() if arm.lower() in k.lower()]
        print(f"M={M} arm={arm} candidate_keys={cands}")
        break
