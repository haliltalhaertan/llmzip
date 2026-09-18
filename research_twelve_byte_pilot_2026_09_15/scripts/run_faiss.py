#!/usr/bin/env python3
"""Does a compiled SIMD binary index beat numpy on the 12-byte codes?

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

Runs in `venv_faiss`, a SEPARATE environment.  The frozen venv that
reproduces the production pipeline was not touched -- numpy there is still
2.3.5 -- because this session measured that the sign code is numerically
fragile, so a dependency change is a scientific risk, not just an ops one.
The only bridge between the two environments is the exported .npy files.

The comparison is end-to-end "give me the top 10", not "give me every
distance".  numpy computes all N distances then argpartitions; faiss walks a
heap and never materialises the full vector.  That is faiss doing the right
operation rather than the same one, and it is the operation a retrieval
system actually needs -- so the honest baseline is the whole numpy pipeline,
including the partition.

Correctness is asserted against `*_refdist.npy`, the distances produced by
the frozen `lib_b8` scorer, before any timing is reported.
"""
import glob
import json
import os
import sys
import time

import faiss
import numpy as np

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "faissdata")
K = 10
TAGS = ["lme", "realtalk", "perltqa", "synth100000", "synth1000000"]


def med(fn, reps):
    for _ in range(3):
        fn()
    ts = []
    for _ in range(reps):
        t = time.perf_counter()
        fn()
        ts.append(time.perf_counter() - t)
    return float(np.median(ts))


def numpy_top10(p32, q32, x, c, o):
    np.bitwise_xor(p32, q32[None, :], out=x)
    np.bitwise_count(x, out=c)
    np.sum(c, axis=1, dtype=np.int64, out=o)
    idx = np.argpartition(o, K)[:K]
    return o[idx[np.argsort(o[idx], kind="stable")]]


def run_tag(tag):
    docs = np.load(f"{DATA}/{tag}_docs.npy")
    qs = np.load(f"{DATA}/{tag}_queries.npy")
    ref = np.load(f"{DATA}/{tag}_refdist.npy").astype(np.int64)
    n, nq = docs.shape[0], qs.shape[0]
    out = {"N": int(n), "n_queries": int(nq)}

    # ---------- faiss binary index ----------
    idx = faiss.IndexBinaryFlat(96)
    t0 = time.perf_counter()
    idx.add(docs)
    out["build_index_ms"] = (time.perf_counter() - t0) * 1e3
    out["index_bytes"] = int(docs.nbytes)

    q1 = np.ascontiguousarray(qs[0:1])
    D1, I1 = idx.search(q1, K)
    # ---------- correctness against the frozen scorer ----------
    ref_top = np.sort(ref)[:K]
    out["faiss_matches_frozen_top10"] = bool(
        np.array_equal(np.sort(D1[0]).astype(np.int64), ref_top))
    # full-vector check where it is cheap
    if n <= 100_000:
        idx_all = faiss.IndexBinaryFlat(96)
        idx_all.add(docs)
        Dall, _ = idx_all.search(q1, n)
        out["faiss_matches_frozen_all"] = bool(
            np.array_equal(np.sort(Dall[0]).astype(np.int64), np.sort(ref)))
    else:
        out["faiss_matches_frozen_all"] = None

    # ---------- numpy end-to-end top-10 ----------
    p32 = np.ascontiguousarray(docs).view(np.uint32)
    q32 = np.ascontiguousarray(qs).view(np.uint32)
    x = np.empty_like(p32)
    c = np.empty(p32.shape, dtype=np.uint8)
    o = np.empty(n, dtype=np.int64)
    np_top = numpy_top10(p32, q32[0], x, c, o)
    out["numpy_matches_frozen_top10"] = bool(
        np.array_equal(np_top, ref_top))

    reps = 40 if n <= 100_000 else 6
    faiss.omp_set_num_threads(1)
    out["single_ms"] = {
        "faiss_1thread": med(lambda: idx.search(q1, K), reps) * 1e3,
        "numpy_1thread": med(
            lambda: numpy_top10(p32, q32[0], x, c, o), reps) * 1e3,
    }
    faiss.omp_set_num_threads(20)
    out["single_ms"]["faiss_20thread"] = med(
        lambda: idx.search(q1, K), reps) * 1e3

    # ---------- float32 reference, same top-10 operation ----------
    fl = np.load(f"{DATA}/{tag}_float.npy")
    fl = np.ascontiguousarray(fl / np.linalg.norm(fl, axis=1, keepdims=True))
    fidx = faiss.IndexFlatIP(96)
    fidx.add(fl)
    # TIMING ONLY: the float query vector was not exported, so this row
    # measures the cost of the same top-K operation on a 384 B/doc index.
    # It is not a quality comparison and must never be read as one.
    rq = np.random.default_rng(0).normal(size=(1, 96)).astype(np.float32)
    qf = np.ascontiguousarray(rq / np.linalg.norm(rq))
    faiss.omp_set_num_threads(1)
    out["single_ms"]["faiss_float32_1thread"] = med(
        lambda: fidx.search(qf, K), reps) * 1e3
    out["float_index_bytes"] = int(fl.nbytes)

    # ---------- batched ----------
    if nq > 1:
        faiss.omp_set_num_threads(1)
        bf = med(lambda: idx.search(qs, K), max(5, reps // 5))
        out["batch_ms_per_query_faiss_1thread"] = bf / nq * 1e3
        faiss.omp_set_num_threads(20)
        bf20 = med(lambda: idx.search(qs, K), max(5, reps // 5))
        out["batch_ms_per_query_faiss_20thread"] = bf20 / nq * 1e3
    return out


def main():
    res = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "faiss": faiss.__version__, "numpy": np.__version__,
           "isolation": "venv_faiss; the frozen venv (numpy 2.3.5) was not "
                        "modified and has no faiss",
           "operation": f"end-to-end top-{K}",
           "tags": {}}
    for tag in TAGS:
        if not os.path.exists(f"{DATA}/{tag}_docs.npy"):
            continue
        r = run_tag(tag)
        res["tags"][tag] = r
        s = r["single_ms"]
        print(f"\n== {tag}  N={r['N']:,} sorgu={r['n_queries']} ==")
        print(f"  bit-aynı: top10={r['faiss_matches_frozen_top10']}  "
              f"tamvektör={r['faiss_matches_frozen_all']}  "
              f"numpy={r['numpy_matches_frozen_top10']}")
        print(f"  numpy  1thr   {s['numpy_1thread']:9.4f} ms")
        print(f"  faiss  1thr   {s['faiss_1thread']:9.4f} ms   "
              f"{s['numpy_1thread']/s['faiss_1thread']:6.2f}x numpy")
        print(f"  faiss 20thr   {s['faiss_20thread']:9.4f} ms   "
              f"{s['numpy_1thread']/s['faiss_20thread']:6.2f}x numpy")
        print(f"  faiss float32 {s['faiss_float32_1thread']:9.4f} ms   "
              f"(indeks {r['float_index_bytes']/1e6:.1f} MB vs "
              f"{r['index_bytes']/1e6:.3f} MB)")
        if "batch_ms_per_query_faiss_1thread" in r:
            print(f"  toplu/sorgu   "
                  f"1thr {r['batch_ms_per_query_faiss_1thread']:.4f} ms   "
                  f"20thr {r['batch_ms_per_query_faiss_20thread']:.4f} ms")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "FAISS.json"), "w") as f:
        json.dump(res, f, indent=2)
    print("\nwrote FAISS.json")


if __name__ == "__main__":
    main()
