"""04_retrieval probe P2: paired archive-clustered bootstrap CIs for _rrf60 contrasts.
Same contract as decision_tests.py boot(): paired per-query diff, resample clusters
with replacement, 20000 reps, seed 20260916, 95% pct CI, excludes_zero flag.
Own code; reads only stored CSV.
"""
import csv, json
import numpy as np
from collections import defaultdict

CSV = ("/mnt/c/Users/MDP/dev/llmzip-work/incoming_20260916b/extracted/"
       "LLMZIP_FIKIR1_METIN_YENIDEN_SIRALAMA_2026-09-16/LLMZIP_FIKIR1_2026-09-16/"
       "results/text_rerank_per_query.csv")
DT = json.load(open("/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/04_retrieval/DECISION_TESTS.orig.json"))

rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
per = defaultdict(dict); arch = {}
for r in rows:
    per[(r["dataset"], r["method"])][r["qid"]] = float(r["fr3"])
    arch[(r["dataset"], r["qid"])] = r["archive"]

def boot(diff, clusters, reps=20000, seed=20260916):
    rng = np.random.default_rng(seed)
    cl = list(clusters.values())
    out = np.empty(reps)
    for t in range(reps):
        pick = rng.integers(0, len(cl), len(cl))
        out[t] = diff[np.concatenate([cl[j] for j in pick])].mean()
    lo, hi = np.percentile(out, [2.5, 97.5])
    return float(100*diff.mean()), float(100*lo), float(100*hi), bool(lo > 0 or hi < 0)

out = {}
for ds in sorted({k[0] for k in per}):
    methods = sorted({k[1] for k in per if k[0] == ds})
    qids = sorted(per[(ds, "BM25_full")].keys())
    clusters = defaultdict(list)
    for i, q in enumerate(qids):
        clusters[arch[(ds, q)]].append(i)
    clusters = {k: np.array(v) for k, v in clusters.items()}
    base = np.array([per[(ds, "BM25_full")][q] for q in qids])
    res = {"n_queries": len(qids), "n_clusters": len(clusters)}
    # reproduce stored _bm25 contrasts as calibration
    print(f"== {ds} n={len(qids)} clusters={len(clusters)} ==")
    for m in sorted(methods):
        if not (m.endswith("_bm25") or m.endswith("_rrf60")):
            continue
        d = np.array([per[(ds, m)][q] for q in qids]) - base
        est, lo, hi, sig = boot(d, clusters)
        gate = bool(est >= 1.0 and sig)
        res[m] = {"est": est, "lo": lo, "hi": hi, "sig": sig, "C3": gate}
        if m.endswith("_bm25"):
            s = DT["T2_rerank"][ds]["contrasts_vs_BM25_alone"][m]
            match = (abs(est-s["vs_BM25_alone_pp"])<1e-9 and abs(lo-s["ci_lo"])<1e-9
                     and abs(hi-s["ci_hi"])<1e-9)
            print(f"  {m:22s} {est:+7.3f} [{lo:+7.3f},{hi:+7.3f}] {'SIG' if sig else 'ns '} C3={'PASS' if gate else 'FAIL'}  repro_match={match}")
        else:
            print(f"  {m:22s} {est:+7.3f} [{lo:+7.3f},{hi:+7.3f}] {'SIG' if sig else 'ns '} C3={'PASS' if gate else 'FAIL'}  (NEW: omitted by pilot gate)")
    out[ds] = res
json.dump(out, open("/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/04_retrieval/rrf60_ci.json", "w"), indent=1)
print("WROTE rrf60_ci.json")
# inversion under rrf60: does first-stage order survive RRF fusion?
print("\n--- first-stage order under _rrf60 (from stored levels) ---")
for ds, v in DT["T2_rerank"].items():
    lv = v["levels_fr3"]
    stages = [m for m in lv if "_" not in m or (not m.endswith("_bm25") and not m.endswith("_rrf60"))]
    base_order = sorted(stages, key=lambda m: -lv[m])
    rrf = {m: lv[m + "_rrf60"] for m in base_order if m + "_rrf60" in lv}
    seq = [rrf[m] for m in base_order]
    inv = sum(1 for i in range(len(seq)) for j in range(i+1, len(seq)) if seq[i] < seq[j])
    print(f"  {ds}: base_order={[(m, round(lv[m],2)) for m in base_order]}")
    print(f"         after_rrf60={[(m, round(rrf[m],2)) for m in base_order]} inv={inv}/10")
