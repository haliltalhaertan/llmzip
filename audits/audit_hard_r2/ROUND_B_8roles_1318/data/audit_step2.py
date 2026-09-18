#!/usr/bin/env python3
"""DATA audit step2: LME + LoCoMo inventory, dup/empty/unanswerable, LoCoMo 1531v1535."""
import json, os, glob, pickle, csv
from collections import Counter, defaultdict

OUT = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/data"
W = "/mnt/c/Users/MDP/dev/llmzip-work"
def jdump(o, fn):
    json.dump(o, open(os.path.join(OUT, fn), "w"), indent=1, default=str)

# ---- LME: baseline per_query_top10 + regen caches ----
import subprocess
# per_query_top10 structure: check one row
row = json.loads(open(f"{W}/top10_comparison_r1/baseline/per_query_top10.jsonl").readline())
print("baseline row keys:", list(row.keys()))
print("sample:", json.dumps(row, default=str)[:800])
# count by benchmark
cnt = Counter(); Ns = {}
lme_gold_sizes = Counter(); lme_oor = 0; lme_N = {}
for line in open(f"{W}/top10_comparison_r1/baseline/per_query_top10.jsonl"):
    r = json.loads(line)
    cnt[r["benchmark"]] += 1
print("baseline counts:", dict(cnt))
# LME rows detail (first LME row)
for line in open(f"{W}/top10_comparison_r1/baseline/per_query_top10.jsonl"):
    r = json.loads(line)
    if r["benchmark"] == "lme":
        print("LME sample:", json.dumps(r, default=str)[:1000]); break
# LME gold-size hist + N dist + oor
for line in open(f"{W}/top10_comparison_r1/baseline/per_query_top10.jsonl"):
    r = json.loads(line)
    if r["benchmark"] != "LME": continue
    lme_gold_sizes[len(r["gold"])] += 1
    N = r["N"]; lme_N[r["archive_id"]] = N
    for g in r["gold"]:
        if not (0 <= int(g) < N): lme_oor += 1
print("LME n_arch:", len(lme_N), "N min/max/total:", min(lme_N.values()), max(lme_N.values()), sum(lme_N.values()))
print("LME gold-size hist:", dict(sorted(lme_gold_sizes.items())))
print("LME oor:", lme_oor)
# LME dup doc texts? need cache texts — check one cache
cf = sorted(glob.glob(f"{W}/regen/lme/cache_repr/*.pkl"))[:3]
print("LME cache files:", len(glob.glob(f"{W}/regen/lme/cache_repr/*.pkl")))
c = pickle.load(open(cf[0], "rb"))
print("LME cache keys:", list(c.keys())[:20])
jdump({"n_arch": len(lme_N), "N": lme_N, "gold_sizes": dict(lme_gold_sizes), "oor": lme_oor, "cache_keys": list(c.keys())[:30]}, "audit_lme_gold.json")

# ---- LoCoMo ----
# HIZ adapter file
ad = json.load(open(f"{W}/incoming_20260916b/extracted/LLMZIP_HIZ_GENELLEME_2026-09-16/LLMZIP_HIZ_GENELLEME_2026-09-16/results/locomo_adapter_before_scores.json"))
print("HIZ adapter type:", type(ad), "len:" if hasattr(ad, "__len__") else "", len(ad) if hasattr(ad, "__len__") else "")
if isinstance(ad, dict): print("HIZ adapter keys:", list(ad.keys())[:20])
if isinstance(ad, list): print("HIZ adapter[0]:", json.dumps(ad[0], default=str)[:800])
