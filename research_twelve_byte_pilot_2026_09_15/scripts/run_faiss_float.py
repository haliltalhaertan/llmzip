#!/usr/bin/env python3
"""Corrected binary-vs-float timing: does the 12-byte code actually win on CPU?

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

The first pass claimed the binary index beats float32 by 1.3x-7.3x.  That
number is withdrawn: it timed ONE archive per corpus and called search with
the SAME query dozens of times into a warm cache, and the companion binary
speedup measured that way (4.25x-5.67x) fell to 3.39x once distinct queries
across 90 archives were used.  This re-measures the float comparison under
the corrected protocol.

Protocol, identical for both indexes:
  * 90 real archives (50 LME, 30 PerLTQA, 10 RealTalk)
  * DISTINCT queries cycled, never the same query twice in a row
  * the archive's own real float32 vectors, not +-1 stand-ins
  * 1 thread (faiss defaults to 20, which this session measured to be 12x
    SLOWER for a single query on a small archive)
  * warm-up excluded, median across archives, quartiles reported

Both indexes answer the same question -- top-10 by their own metric -- so
this is a cost comparison at equal output shape, NOT a quality comparison.
Binary ranks by Hamming, float by inner product; they return different
documents by design.  Nothing here says which retrieves better.
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


def main():
    faiss.omp_set_num_threads(1)
    rows = []
    for f in sorted(glob.glob(os.path.join(DATA, "*_float.npz"))):
        tag = os.path.basename(f)[:-10]
        bench = "lme" if tag.startswith("lme") else (
            "perltqa" if tag.startswith("pq") else "realtalk")
        zf = np.load(f)
        C = np.ascontiguousarray(zf["docs"])
        Qf = np.ascontiguousarray(zf["queries"])
        zb = np.load(os.path.join(DATA, tag + ".npz"), allow_pickle=True)
        docs, qs = zb["docs"], zb["queries"]
        n, nq = C.shape[0], Qf.shape[0]
        assert docs.shape[0] == n and qs.shape[0] == nq

        bi = faiss.IndexBinaryFlat(96)
        bi.add(docs)
        fi = faiss.IndexFlatIP(96)
        fi.add(C)

        reps = min(nq, 60)
        for j in range(min(nq, 5)):          # warm-up, not timed
            bi.search(qs[j:j + 1], K)
            fi.search(Qf[j:j + 1], K)
        t0 = time.perf_counter()
        for j in range(reps):
            bi.search(qs[(j % nq):(j % nq) + 1], K)
        tb = (time.perf_counter() - t0) / reps
        t0 = time.perf_counter()
        for j in range(reps):
            fi.search(Qf[(j % nq):(j % nq) + 1], K)
        tf = (time.perf_counter() - t0) / reps

        rows.append({"tag": tag, "bench": bench, "N": int(n),
                     "binary_ms": tb * 1e3, "float32_ms": tf * 1e3,
                     "speedup": tf / tb,
                     "binary_bytes": int(docs.nbytes),
                     "float32_bytes": int(C.nbytes)})

    def summ(v):
        a = np.asarray(v, float)
        return {"median": float(np.median(a)),
                "p25": float(np.percentile(a, 25)),
                "p75": float(np.percentile(a, 75)),
                "min": float(a.min()), "max": float(a.max())}

    out = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "faiss": faiss.__version__, "threads": 1,
           "withdrawn": "the earlier 1.3x-7.3x binary-vs-float figure, which "
                        "used one archive per corpus and a repeated query",
           "not_a_quality_comparison": True,
           "n_archives": len(rows),
           "overall_speedup": summ([r["speedup"] for r in rows]),
           "ram_ratio": float(sum(r["float32_bytes"] for r in rows)
                              / sum(r["binary_bytes"] for r in rows)),
           "per_benchmark": {}, "rows": rows}
    for b in ("lme", "perltqa", "realtalk"):
        sub = [r for r in rows if r["bench"] == b]
        if sub:
            out["per_benchmark"][b] = {
                "archives": len(sub),
                "N_median": float(np.median([r["N"] for r in sub])),
                "binary_ms_median": float(np.median(
                    [r["binary_ms"] for r in sub])),
                "float32_ms_median": float(np.median(
                    [r["float32_ms"] for r in sub])),
                "speedup": summ([r["speedup"] for r in sub])}
    with open(os.path.join(HERE, "FAISS_FLOAT.json"), "w") as fh:
        json.dump(out, fh, indent=2)

    s = out["overall_speedup"]
    print(f"90 arşiv · 1 thread · farklı sorgular\n")
    print(f"binary (12 B/belge) vs float32 (384 B/belge), aynı işlem top-{K}")
    print(f"  hız   : medyan {s['median']:.2f}x  "
          f"(p25 {s['p25']:.2f} – p75 {s['p75']:.2f}, "
          f"min {s['min']:.2f}, max {s['max']:.2f})")
    print(f"  RAM   : {out['ram_ratio']:.1f}x az\n")
    for b, v in out["per_benchmark"].items():
        print(f"  {b:9s} N~{v['N_median']:.0f}  "
              f"binary {v['binary_ms_median']:.4f} ms  "
              f"float32 {v['float32_ms_median']:.4f} ms  "
              f"-> {v['speedup']['median']:.2f}x "
              f"({v['speedup']['p25']:.2f}–{v['speedup']['p75']:.2f})")
    print("\nwrote FAISS_FLOAT.json")


if __name__ == "__main__":
    main()
