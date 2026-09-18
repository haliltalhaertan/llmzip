"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
01_metrics probe P3 — second-dataset (PerLTQA) + T2 join recompute from stored CSV.
Own CSV parse, own micro-mean levels, own small cluster bootstrap
(seed 777, 2000 reps) for ONE focal contrast per dataset; cluster-unit inventory.
Reads (READ ONLY): incoming.../results/text_rerank_per_query.csv,
 published coordinator/DECISION_TESTS.json (copied orig) for comparison only.
"""
import csv
import json
import os
from collections import defaultdict

import numpy as np

RER = ("/mnt/c/Users/MDP/dev/llmzip-work/incoming_20260916b/extracted/"
       "LLMZIP_FIKIR1_METIN_YENIDEN_SIRALAMA_2026-09-16/"
       "LLMZIP_FIKIR1_2026-09-16/results/text_rerank_per_query.csv")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "out", "p3_t2_second_dataset.json")
DEC = json.load(open(os.path.join(HERE, "..", "orig", "DECISION_TESTS.json"),
                     encoding="utf-8"))
res = {"datasets": {}}

rows = list(csv.DictReader(open(RER, encoding="utf-8")))
res["rowcount"] = len(rows)
per = defaultdict(dict)
arch = {}
for r in rows:
    ds, m, q = r["dataset"], r["method"], r["qid"]
    per[(ds, m)][q] = float(r["fr3"])
    arch[(ds, q)] = r["archive"]

FOCAL = {"PerLTQA": "qscale96_bm25", "LoCoMo": "qscale96_bm25", "LME": "qscale96_bm25"}


def boot(diff, clusters, reps=2000, seed=777):
    rng = np.random.default_rng(seed)
    cl = list(clusters.values())
    out = np.empty(reps)
    for t in range(reps):
        pick = rng.integers(0, len(cl), len(cl))
        out[t] = diff[np.concatenate([cl[j] for j in pick])].mean()
    lo, hi = np.percentile(out, [2.5, 97.5])
    return float(100 * diff.mean()), float(100 * lo), float(100 * hi)


for ds in sorted({k[0] for k in per}):
    methods = sorted({k[1] for k in per if k[0] == ds})
    qids = sorted(per[(ds, "BM25_full")].keys())
    clusters = defaultdict(list)
    for i, q in enumerate(qids):
        clusters[arch[(ds, q)]].append(i)
    clusters = {k: np.array(v) for k, v in clusters.items()}
    base = np.array([per[(ds, "BM25_full")][q] for q in qids])
    m = FOCAL[ds]
    d = np.array([per[(ds, m)][q] for q in qids]) - base
    est, lo, hi = boot(d, clusters)
    pub = DEC["T2_rerank"][ds]["contrasts_vs_BM25_alone"][m]
    lvl_mine = 100 * np.mean([per[(ds, m)][q] for q in qids])
    lvl_pub = DEC["T2_rerank"][ds]["levels_fr3"][m]
    sizes = sorted(len(v) for v in clusters.values())
    res["datasets"][ds] = {
        "n_queries": len(qids),
        "n_clusters": len(clusters),
        "cluster_size_min_med_max": [sizes[0], sizes[len(sizes) // 2], sizes[-1]],
        "cluster_unit": ("query==archive (LME single-session rows: clustering is a no-op)"
                         if len(clusters) == len(qids) else "archive"),
        "focal": m,
        "level_mine": lvl_mine, "level_pub": lvl_pub,
        "level_diff_pp": lvl_mine - lvl_pub,
        "est_mine": est, "est_pub": pub["vs_BM25_alone_pp"],
        "est_diff_pp": est - pub["vs_BM25_alone_pp"],
        "ci_mine_2k_s777": [lo, hi],
        "ci_pub_20k_s20260916": [pub["ci_lo"], pub["ci_hi"]],
        "sig_agrees": bool((lo > 0 or hi < 0) == pub["excludes_zero"]),
        "c3_agrees": bool((est >= 1.0 and (lo > 0 or hi < 0)) == pub["passes_C3_gate"]),
    }

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1))
