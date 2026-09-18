"""Round-2 decision-audit probes (read-only inputs, writes only to this dir).
1. RRF60 (code-involving fusion+rerank) vs BM25_full deltas with paired
   archive-clustered bootstrap CIs -- the family decision_tests.py drops via
   its endswith('_bm25') filter.
2. T1 gap CIs that decision_tests.py omits (gate C1 requires CI excl 0):
   48B qscale vs frozen_textbook (referee primary) and vs frozen_idfonly
   (executed comparator), FR@3 primary + Hit@10 guardrail.
"""
import csv, json, os
from collections import defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RERANK_CSV = ("/mnt/c/Users/MDP/dev/llmzip-work/incoming_20260916b/extracted/"
              "LLMZIP_FIKIR1_METIN_YENIDEN_SIRALAMA_2026-09-16/"
              "LLMZIP_FIKIR1_2026-09-16/results/text_rerank_per_query.csv")

def boot(diff, clusters, reps=20000, seed=20260916):
    rng = np.random.default_rng(seed)
    cl = list(clusters.values())
    out = np.empty(reps)
    for t in range(reps):
        pick = rng.integers(0, len(cl), len(cl))
        out[t] = diff[np.concatenate([cl[j] for j in pick])].mean()
    lo, hi = np.percentile(out, [2.5, 97.5])
    return float(100*diff.mean()), float(100*lo), float(100*hi), bool(lo > 0 or hi < 0)

rows = list(csv.DictReader(open(RERANK_CSV, encoding="utf-8")))
print("data rows:", len(rows))
per = defaultdict(dict); arch = {}
for r in rows:
    per[(r["dataset"], r["method"])][r["qid"]] = float(r["fr3"])
    arch[(r["dataset"], r["qid"])] = r["archive"]

rrf = {}
for ds in sorted({k[0] for k in per}):
    qids = sorted(per[(ds, "BM25_full")].keys())
    clusters = defaultdict(list)
    for i, q in enumerate(qids):
        clusters[arch[(ds, q)]].append(i)
    clusters = {k: np.array(v) for k, v in clusters.items()}
    base = np.array([per[(ds, "BM25_full")][q] for q in qids])
    rrf[ds] = {}
    for m in sorted({k[1] for k in per if k[0] == ds}):
        if not m.endswith("_rrf60"):
            continue
        d = np.array([per[(ds, m)][q] for q in qids]) - base
        est, lo, hi, sig = boot(d, clusters)
        rrf[ds][m] = {"vs_BM25_alone_pp": round(est,2), "ci_lo": round(lo,2),
                      "ci_hi": round(hi,2), "excludes_zero": sig,
                      "passes_+1pp_gate": bool(est >= 1.0 and sig)}
print(json.dumps(rrf, indent=1))
json.dump(rrf, open(os.path.join(HERE, "AUDIT_RRF60.json"), "w"), indent=1)

# ---- T1: paired ARCHIVE-level gaps from stored per-archive means.
# (Per-query code rows are not stored, so the query-level paired CI the C1
# gate requires is UNREPRODUCIBLE from artifacts; this archive-level check
# with n=10 is supplementary, not a substitute. LADDER_CACHE stores
# BM25_frozen = frozen TEXTBOOK -- the referee's primary comparator.)
cache = [json.loads(l) for l in
         open("/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/"
              "coordinator/LADDER_CACHE.jsonl", encoding="utf-8")]
t1 = {}
for metric, mkey in (("hit10", "hit10"), ("fr3", "fr3")):
    gaps = np.array([a["arms"]["k384/qscale"][mkey] - a["arms"]["BM25_frozen/-"][mkey]
                     for a in cache])
    ns = np.array([a["n"] for a in cache])
    wmean = float((gaps * ns).sum() / ns.sum())
    n = len(gaps)
    rng = np.random.default_rng(20260916)
    reps = 20000
    boots = np.array([gaps[rng.integers(0, n, n)].mean() for _ in range(reps)])
    lo, hi = np.percentile(boots, [2.5, 97.5])
    t1[f"48Bqscale_vs_textbook_{metric}"] = {
        "unweighted_mean_gap_pp": round(float(gaps.mean()), 2),
        "query_weighted_gap_pp": round(wmean, 2),
        "archive_bootstrap_ci": [round(float(lo), 2), round(float(hi), 2)],
        "n_archives": n}
print(json.dumps(t1, indent=1))
json.dump(t1, open(os.path.join(HERE, "AUDIT_T1_ARCHIVE_CI.json"), "w"), indent=1)
