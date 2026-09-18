# Auditor's own T2 recomputation. Reads ONLY the incoming CSV (read-only).
# No coordinator code imported. Own bootstrap implementation.
import csv, json, sys
import numpy as np

CSV = "/mnt/c/Users/MDP/dev/llmzip-work/incoming_20260916b/extracted/LLMZIP_FIKIR1_METIN_YENIDEN_SIRALAMA_2026-09-16/LLMZIP_FIKIR1_2026-09-16/results/text_rerank_per_query.csv"
COORD = "/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10/research_top10_comparison_2026_09_16/coordinator/DECISION_TESTS.json"

def load():
    per = {}   # (ds,method,qid) -> fr3
    arch = {}  # (ds,qid) -> archive
    n = 0
    with open(CSV, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            per[(r["dataset"], r["method"], r["qid"])] = float(r["fr3"])
            arch[(r["dataset"], r["qid"])] = r["archive"]
            n += 1
    return per, arch, n

def cluster_boot(diff, cl_idx, cl_sizes, reps, seed):
    # diff: per-query diff vector; resample clusters with replacement, micro-mean
    rng = np.random.default_rng(seed)
    sums = np.array([diff[idx].sum() for idx in cl_idx])
    cnts = np.array(cl_sizes, dtype=float)
    picks = rng.integers(0, len(cl_idx), size=(reps, len(cl_idx)))
    est = sums[picks].sum(axis=1) / cnts[picks].sum(axis=1)
    lo, hi = np.percentile(est, [2.5, 97.5])
    return float(100*diff.mean()), float(100*lo), float(100*hi), est

def main():
    per, arch, nrows = load()
    coord = json.load(open(COORD, encoding="utf-8"))["T2_rerank"]
    print(f"rows={nrows} (claim 164256)")
    out = {"nrows": nrows, "datasets": {}}
    for ds in sorted({k[0] for k in per}):
        methods = sorted({k[1] for k in per if k[0] == ds})
        qids = sorted({k[2] for k in per if k[0] == ds and k[1] == "BM25_full"})
        base = np.array([per[(ds, "BM25_full", q)] for q in qids])
        # cluster index
        cl = {}
        for i, q in enumerate(qids):
            cl.setdefault(arch[(ds, q)], []).append(i)
        cl_idx = [np.array(v) for v in cl.values()]
        cnts = [len(v) for v in cl.values()]
        levels = {m: 100*float(np.mean([per[(ds, m, q)] for q in qids]))
                  for m in methods if sum(1 for q in qids if (ds, m, q) in per) >= len(qids)}
        # focal + full contrasts with alternate seed 777, 20000 reps
        contrasts = {}
        for m in methods:
            if not m.endswith("_bm25"):
                continue
            if sum(1 for q in qids if (ds, m, q) in per) < len(qids):
                continue
            d = np.array([per[(ds, m, q)] for q in qids]) - base
            est, lo, hi, _ = cluster_boot(d, cl_idx, cnts, 20000, 777)
            contrasts[m] = {"est": est, "lo": lo, "hi": hi}
        # multi-seed distribution for focal qscale96_bm25: 5 seeds x 2000 reps
        focal = {}
        m = "qscale96_bm25"
        if m in contrasts:
            d = np.array([per[(ds, m, q)] for q in qids]) - base
            for s in [11, 22, 33, 44, 55]:
                est, lo, hi, _ = cluster_boot(d, cl_idx, cnts, 2000, s)
                focal[s] = {"est": est, "lo": lo, "hi": hi}
        # inversion count (own recompute from levels)
        pairs = sorted([(b, levels[b], a, levels[a]) for a in methods
                        if a.endswith("_bm25") and a[:-5] in levels
                        for b in [a[:-5]]], key=lambda x: -x[1])
        inv = sum(1 for i in range(len(pairs)) for j in range(i+1, len(pairs)) if pairs[i][3] < pairs[j][3])
        out["datasets"][ds] = {"nq": len(qids), "ncl": len(cl), "levels": levels,
                               "contrasts": contrasts, "focal_multiseed": focal,
                               "inversions": inv, "npairs": len(pairs)*(len(pairs)-1)//2,
                               "order": [(a, b, d) for a, b, _, d in pairs]}
        print(f"\n{ds}: nq={len(qids)} ncl={len(cl)} inv={inv}/{len(pairs)*(len(pairs)-1)//2}")
        for mm in ["qscale96_bm25", "float_raw32_bm25", "float_std32_bm25", "asym96_bm25", "hamming96_bm25"]:
            if mm in contrasts:
                c = contrasts[mm]; cc = coord[ds]["contrasts_vs_BM25_alone"][mm]
                print(f"  {mm}: audit {c['est']:+.4f} [{c['lo']:+.4f},{c['hi']:+.4f}] vs coord {cc['vs_BM25_alone_pp']:+.4f} [{cc['ci_lo']:+.4f},{cc['ci_hi']:+.4f}]")
        for lv in ["BM25_full", "qscale96", "float_raw32", "float_std32", "qscale96_bm25", "float_raw32_bm25", "float_std32_bm25"]:
            if lv in levels:
                cl2 = coord[ds]["levels_fr3"].get(lv, float("nan"))
                print(f"  lvl {lv}: audit {levels[lv]:.6f} vs coord {cl2:.6f} diff={levels[lv]-cl2:+.6f}")
        if focal:
            print(f"  focal {m} multiseed(2000r): " + "; ".join(f"s{s}:{v['est']:+.3f}[{v['lo']:+.3f},{v['hi']:+.3f}]" for s, v in focal.items()))
    json.dump(out, open("audit_t2_out.json", "w", encoding="utf-8"), indent=1)
    print("\nWROTE audit_t2_out.json")

if __name__ == "__main__":
    main()
