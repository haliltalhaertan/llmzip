#!/usr/bin/env python3
"""Scrutinising the faiss result: is it the same retrieval, or just the same distances?

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

The first faiss benchmark compared sorted DISTANCE MULTISETS and found them
identical.  That is not enough.  Hamming distance over 96 bits produces heavy
ties, and the two systems break them differently:

    frozen metric : uniform at random within an equal-distance bucket
    faiss         : deterministic, by ascending internal index

So the distances can agree exactly while the returned DOCUMENTS differ, which
is precisely the failure mode the exact-SVD experiment hit earlier today.
This script measures whether that actually changes the reported number.

Checks, over 90 archives / 9020 queries, not one archive each:

  1. distance agreement, every query, full top-10 (and full vector where cheap)
  2. how often a tie straddles the k=10 boundary at all
  3. what fraction of a top-10 is forced (d < d10) vs decided by tie-breaking
  4. hit@10 under the frozen expected-value convention vs faiss's determinism
  5. timing with DISTINCT queries cycled, 1 thread, median and IQR across
     archives -- the earlier run repeated one query 40 times into a warm cache
"""
import glob
import json
import os
import time

import faiss
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "faissdeep")
K = 10


def hit_expected(dist, gold, k=K):
    """Frozen convention: P(>=1 gold in top k) under uniform tie-breaking."""
    gs = set(int(x) for x in gold)
    order = np.sort(dist)
    if len(dist) <= k:
        return 1.0 if gs else 0.0
    dk = order[k - 1]
    inside = np.nonzero(dist < dk)[0]
    if any(int(i) in gs for i in inside):
        return 1.0
    bucket = np.nonzero(dist == dk)[0]
    gb = sum(1 for i in bucket if int(i) in gs)
    slots = k - len(inside)
    b = len(bucket)
    if gb == 0:
        return 0.0
    if slots > b - gb:
        return 1.0
    num = den = 1.0
    for i in range(slots):
        num *= (b - gb - i)
        den *= (b - i)
    return 1.0 - num / den


def tie_facts(dist, k=K):
    order = np.sort(dist)
    if len(dist) <= k:
        return 0, 0, k
    dk = order[k - 1]
    n_lt = int(np.count_nonzero(dist < dk))
    bucket = int(np.count_nonzero(dist == dk))
    slots = k - n_lt
    return n_lt, bucket, slots


def main():
    # NOTE (audit fix): the *_float.npz companions were written AFTER the
    # first run of this script, so a bare "*.npz" glob now matches 180
    # files and dies on the first float archive with KeyError: refdist.
    # The published FAISS_DEEP.json is the 90-archive run; this exclusion
    # restores that set so the result can be reproduced.
    files = sorted(f for f in glob.glob(os.path.join(DATA, "*.npz"))
                   if not f.endswith("_float.npz"))
    assert len(files) == 90, f"expected 90 code archives, found {len(files)}"
    faiss.omp_set_num_threads(1)
    agg = {"queries": 0, "dist_mismatch": 0, "full_vec_checked": 0,
           "full_vec_mismatch": 0, "tie_straddles": 0,
           "forced_frac": [], "hit_frozen": [], "hit_faiss": [],
           "hit_differs": 0, "speedups": [], "per_bench": {}}
    per = {}
    for f in files:
        tag = os.path.basename(f)[:-4]
        bench = "lme" if tag.startswith("lme") else (
            "perltqa" if tag.startswith("pq") else "realtalk")
        z = np.load(f, allow_pickle=True)
        docs, qs, ref = z["docs"], z["queries"], z["refdist"]
        golds = z["gold"]
        n, nq = docs.shape[0], qs.shape[0]
        idx = faiss.IndexBinaryFlat(96)
        idx.add(docs)
        D, I = idx.search(qs, K)
        p = per.setdefault(bench, {"q": 0, "dmis": 0, "straddle": 0,
                                   "hf": [], "hx": [], "diff": 0,
                                   "forced": [], "sp": []})
        for j in range(nq):
            d = ref[j].astype(np.int64)
            top = np.sort(d)[:K]
            if not np.array_equal(np.sort(D[j]).astype(np.int64), top):
                agg["dist_mismatch"] += 1
                p["dmis"] += 1
            n_lt, bucket, slots = tie_facts(d)
            if bucket > slots:
                agg["tie_straddles"] += 1
                p["straddle"] += 1
            forced = min(n_lt, K) / K
            agg["forced_frac"].append(forced)
            p["forced"].append(forced)
            g = set(int(x) for x in np.asarray(golds[j]).ravel())
            hf = hit_expected(d, g)
            hx = 1.0 if (set(int(i) for i in I[j]) & g) else 0.0
            agg["hit_frozen"].append(hf)
            agg["hit_faiss"].append(hx)
            p["hf"].append(hf)
            p["hx"].append(hx)
            if abs(hf - hx) > 1e-9:
                agg["hit_differs"] += 1
                p["diff"] += 1
            agg["queries"] += 1
            p["q"] += 1
        if n <= 20000:
            Dall, _ = idx.search(qs[:1], n)
            agg["full_vec_checked"] += 1
            if not np.array_equal(np.sort(Dall[0]).astype(np.int64),
                                  np.sort(ref[0].astype(np.int64))):
                agg["full_vec_mismatch"] += 1
        # ---- timing with DISTINCT queries, no repeated-query cache effect ----
        p32 = np.ascontiguousarray(docs).view(np.uint32)
        q32 = np.ascontiguousarray(qs).view(np.uint32)
        x = np.empty_like(p32)
        c = np.empty(p32.shape, dtype=np.uint8)
        o = np.empty(n, dtype=np.int64)

        def np_one(j):
            np.bitwise_xor(p32, q32[j][None, :], out=x)
            np.bitwise_count(x, out=c)
            np.sum(c, axis=1, dtype=np.int64, out=o)
            t = np.argpartition(o, K)[:K]
            return o[t]

        reps = min(nq, 60)
        for j in range(min(nq, 5)):
            np_one(j)
            idx.search(qs[j:j + 1], K)
        t0 = time.perf_counter()
        for j in range(reps):
            np_one(j % nq)
        tn = (time.perf_counter() - t0) / reps
        t0 = time.perf_counter()
        for j in range(reps):
            idx.search(qs[(j % nq):(j % nq) + 1], K)
        tf = (time.perf_counter() - t0) / reps
        agg["speedups"].append(tn / tf)
        p["sp"].append(tn / tf)

    def summ(v):
        a = np.asarray(v, dtype=float)
        return {"mean": float(a.mean()), "median": float(np.median(a)),
                "p25": float(np.percentile(a, 25)),
                "p75": float(np.percentile(a, 75))}

    out = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "faiss": faiss.__version__, "numpy": np.__version__,
           "n_archives": len(files), "n_queries": agg["queries"],
           "distance_mismatches": agg["dist_mismatch"],
           "full_vector_checked": agg["full_vec_checked"],
           "full_vector_mismatches": agg["full_vec_mismatch"],
           "tie_straddles_k10": agg["tie_straddles"],
           "tie_straddle_rate": agg["tie_straddles"] / agg["queries"],
           "forced_fraction_of_top10": summ(agg["forced_frac"]),
           "hit10_frozen_expected_pct": float(
               np.mean(agg["hit_frozen"]) * 100),
           "hit10_faiss_deterministic_pct": float(
               np.mean(agg["hit_faiss"]) * 100),
           "queries_where_hit_differs": agg["hit_differs"],
           "speedup_over_numpy": summ(agg["speedups"]),
           "per_benchmark": {}}
    d = np.asarray(agg["hit_faiss"]) - np.asarray(agg["hit_frozen"])
    se = d.std(ddof=1) / np.sqrt(len(d))
    out["hit10_delta_pp"] = {
        "point": float(d.mean() * 100),
        "ci95": [float((d.mean() - 1.96 * se) * 100),
                 float((d.mean() + 1.96 * se) * 100)]}
    for b, v in per.items():
        dd = np.asarray(v["hx"]) - np.asarray(v["hf"])
        s2 = dd.std(ddof=1) / np.sqrt(len(dd)) if len(dd) > 1 else 0.0
        out["per_benchmark"][b] = {
            "archives": len(v["sp"]), "queries": v["q"],
            "distance_mismatches": v["dmis"],
            "tie_straddle_rate": v["straddle"] / v["q"],
            "forced_fraction_median": float(np.median(v["forced"])),
            "hit10_frozen_pct": float(np.mean(v["hf"]) * 100),
            "hit10_faiss_pct": float(np.mean(v["hx"]) * 100),
            "hit10_delta_pp": float(dd.mean() * 100),
            "hit10_delta_ci95": [float((dd.mean() - 1.96 * s2) * 100),
                                 float((dd.mean() + 1.96 * s2) * 100)],
            "queries_where_hit_differs": v["diff"],
            "speedup_median": float(np.median(v["sp"])),
            "speedup_p25_p75": [float(np.percentile(v["sp"], 25)),
                                float(np.percentile(v["sp"], 75))]}
    with open(os.path.join(HERE, "FAISS_DEEP.json"), "w") as fh:
        json.dump(out, fh, indent=2)

    print(f"arşiv={out['n_archives']}  sorgu={out['n_queries']}")
    print(f"\n1. MESAFE UYUMU")
    print(f"   uyuşmayan sorgu : {out['distance_mismatches']}"
          f"/{out['n_queries']}")
    print(f"   tam vektör      : {out['full_vector_mismatches']}"
          f"/{out['full_vector_checked']} uyuşmazlık")
    print(f"\n2. BERABERLİK ilk-10 sınırını kesiyor mu")
    print(f"   oran            : {out['tie_straddle_rate']*100:.1f}% "
          f"({out['tie_straddles_k10']} sorgu)")
    fr = out["forced_fraction_of_top10"]
    print(f"   ilk-10'un zorunlu kısmı: medyan {fr['median']*100:.0f}%  "
          f"(p25 {fr['p25']*100:.0f}% – p75 {fr['p75']*100:.0f}%)")
    print(f"\n3. RAPOR EDİLEN SAYI DEĞİŞİYOR MU")
    print(f"   hit@10 donmuş (beklenen değer) : "
          f"{out['hit10_frozen_expected_pct']:.2f}%")
    print(f"   hit@10 faiss  (deterministik)  : "
          f"{out['hit10_faiss_deterministic_pct']:.2f}%")
    hd = out["hit10_delta_pp"]
    sig = "*ANLAMLI" if (hd["ci95"][0] > 0 or hd["ci95"][1] < 0) else "ns"
    print(f"   fark : {hd['point']:+.2f} pp  "
          f"[{hd['ci95'][0]:.2f}, {hd['ci95'][1]:.2f}]  {sig}")
    print(f"   farklı çıkan sorgu: {out['queries_where_hit_differs']}"
          f"/{out['n_queries']}")
    sp = out["speedup_over_numpy"]
    print(f"\n4. HIZ (farklı sorgular, 1 thread, 90 arşiv)")
    print(f"   medyan {sp['median']:.2f}x  "
          f"(p25 {sp['p25']:.2f}x – p75 {sp['p75']:.2f}x)")
    print(f"\n5. BENCHMARK BAZINDA")
    for b, v in out["per_benchmark"].items():
        print(f"   {b:9s} n={v['queries']:5d}  "
              f"beraberlik={v['tie_straddle_rate']*100:5.1f}%  "
              f"hit@10 {v['hit10_frozen_pct']:.2f} -> "
              f"{v['hit10_faiss_pct']:.2f}  "
              f"({v['hit10_delta_pp']:+.2f} pp)  hız {v['speedup_median']:.2f}x")
    print("\nwrote FAISS_DEEP.json")


if __name__ == "__main__":
    main()
