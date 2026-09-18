"""Round-2 stats audit: LoCoMo rerank +1.07 under multiple-comparison correction (task B/C).

READ-ONLY on sources; writes only to this stats dir.
Claim: DECISION_TESTS.md T2 "LoCoMo +1.07pp [+0.44,+1.72] SIG PASS (disputed gold)".
Checks:
  (1) count tested contrasts in T2 (methods x datasets) -> Bonferroni/Sidak thresholds;
  (2) recompute the LoCoMo qscale96_bm25-vs-BM25 contrast from the stored CSV with the
      project's own paired archive-clustered bootstrap at 95% AND at Bonferroni level;
  (3) archive-level fragility: per-archive sign of the effect over LoCoMo's 10 clusters;
  (4) enumerate all SIG claims in REPORT.md/DECISION_TESTS.md/FINAL_STATE.md vs corrected alpha.
"""
import csv, json
from collections import defaultdict
import numpy as np

CSV = ("/mnt/c/Users/MDP/dev/llmzip-work/incoming_20260916b/extracted/"
       "LLMZIP_FIKIR1_METIN_YENIDEN_SIRALAMA_2026-09-16/LLMZIP_FIKIR1_2026-09-16/"
       "results/text_rerank_per_query.csv")
PKG = "/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10/research_top10_comparison_2026_09_16"
OUT = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/stats/rerank_recompute.json"
out = {}


def boot(diff, clusters, reps=20000, seed=20260916, level=0.95):
    rng = np.random.default_rng(seed)
    cl = list(clusters.values())
    res = np.empty(reps)
    for t in range(reps):
        pick = rng.integers(0, len(cl), len(cl))
        res[t] = diff[np.concatenate([cl[j] for j in pick])].mean()
    a = (1 - level) / 2 * 100
    lo, hi = np.percentile(res, [a, 100 - a])
    return float(100 * diff.mean()), float(100 * lo), float(100 * hi), bool(lo > 0 or hi < 0)


rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
per, arch = defaultdict(dict), {}
for r in rows:
    per[(r["dataset"], r["method"])][r["qid"]] = float(r["fr3"])
    arch[(r["dataset"], r["qid"])] = r["archive"]

datasets = sorted({k[0] for k in per})
# (1) contrast count: every *_bm25 reranked arm vs BM25_full, per dataset
n_contrasts = 0
contrast_list = []
for ds in datasets:
    ms = sorted({k[1] for k in per if k[0] == ds})
    nbm = sum(1 for m in ms if m.endswith("_bm25"))
    n_contrasts += nbm
    contrast_list.append({"dataset": ds, "reranked_arms": nbm, "methods": ms})
out["contrast_inventory"] = contrast_list
out["T2_total_contrasts"] = n_contrasts
m = n_contrasts
out["bonferroni_alpha"] = 0.05 / m
out["bonferroni_level"] = 1 - 0.05 / m
out["sidak_level"] = (1 - 0.05) ** (1 / m)

# (2) LoCoMo qscale recompute
ds = "LoCoMo"
qids = sorted(per[(ds, "BM25_full")].keys())
clusters = defaultdict(list)
for i, q in enumerate(qids):
    clusters[arch[(ds, q)]].append(i)
clusters = {k: np.array(v) for k, v in clusters.items()}
base = np.array([per[(ds, "BM25_full")][q] for q in qids])
out["LoCoMo_n_queries"] = len(qids)
out["LoCoMo_n_clusters"] = len(clusters)
out["LoCoMo_cluster_sizes"] = sorted([len(v) for v in clusters.values()])
loco = {}
for meth in ("qscale96_bm25", "float_raw32_bm25", "float_std32_bm25",
              "hamming96_bm25", "asym96_bm25"):
    d = np.array([per[(ds, meth)][q] for q in qids]) - base
    e95, lo95, hi95, s95 = boot(d, clusters, level=0.95)
    eB, loB, hiB, sB = boot(d, clusters, level=out["bonferroni_level"])
    loco[meth] = {"est_pp": round(e95, 3),
                  "CI95": [round(lo95, 3), round(hi95, 3)], "sig95": s95,
                  "CI_bonf": [round(loB, 3), round(hiB, 3)],
                  "sig_bonf": sB,
                  "passes_C3_gate_bonf": bool(e95 >= 1.0 and sB)}
out["LoCoMo_contrasts"] = loco

# (3) per-archive sign of qscale effect (10 clusters)
arch_effect = {}
for a, idx in clusters.items():
    b = base[idx]
    q = np.array([per[(ds, "qscale96_bm25")][qids[i]] for i in idx])
    arch_effect[a] = {"n": len(idx), "diff_pp": round(100 * float((q - b).mean()), 2)}
out["LoCoMo_qscale_per_archive_effect"] = arch_effect
out["LoCoMo_archives_favoring_code"] = sum(1 for v in arch_effect.values() if v["diff_pp"] > 0)

# all-dataset reranked contrasts at both levels (for the correction table)
allc = {}
for ds in datasets:
    qids2 = sorted(per[(ds, "BM25_full")].keys())
    cl2 = defaultdict(list)
    for i, q in enumerate(qids2):
        cl2[arch[(ds, q)]].append(i)
    cl2 = {k: np.array(v) for k, v in cl2.items()}
    b2 = np.array([per[(ds, "BM25_full")][q] for q in qids2])
    for meth in sorted({k[1] for k in per if k[0] == ds}):
        if not meth.endswith("_bm25"):
            continue
        d = np.array([per[(ds, meth)][q] for q in qids2]) - b2
        e, lo, hi, s = boot(d, cl2, level=0.95)
        _, loB, hiB, sB = boot(d, cl2, level=out["bonferroni_level"])
        allc[(ds, meth)] = {"est": round(e, 2), "sig95": s, "sig_bonf": sB}
out["all_contrasts_sig95_vs_bonf"] = [
    {"ds": k[0], "arm": k[1], **v} for k, v in sorted(allc.items())]
out["n_sig95"] = sum(1 for v in allc.values() if v["sig95"])
out["n_sig_bonf"] = sum(1 for v in allc.values() if v["sig_bonf"])
json.dump(out, open(OUT, "w"), indent=1)
print(json.dumps(out, indent=1)[:4000])
print("n_sig95 =", out["n_sig95"], " n_sig_bonf =", out["n_sig_bonf"])
