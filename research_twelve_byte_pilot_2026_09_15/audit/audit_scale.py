#!/usr/bin/env python3
"""Per-benchmark C5 under high reps, and the scale dependence of C4/C5.

At N~500 a single search takes ~10us.  How much of that is the Hamming /
inner-product kernel and how much is Python+SWIG per-call overhead?  If the
ratio moves with N, neither 3.4x nor 1.3x is a property of the kernels.
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


def mk_v1(docs):
    p32 = np.ascontiguousarray(docs).view(np.uint32)
    x = np.empty_like(p32)
    c = np.empty(p32.shape, dtype=np.uint8)
    o = np.empty(docs.shape[0], dtype=np.int64)

    def f(q):
        q32 = np.ascontiguousarray(q).view(np.uint32)
        np.bitwise_xor(p32, q32[None, :], out=x)
        np.bitwise_count(x, out=c)
        np.sum(c, axis=1, dtype=np.int64, out=o)
        t = np.argpartition(o, K)[:K]
        return o[t]
    return f


def blk(fn, order, reps):
    t0 = time.perf_counter()
    for i in range(reps):
        fn(order[i])
    return (time.perf_counter() - t0) / reps


def summ(v):
    a = np.asarray(v, float)
    return {"median": float(np.median(a)), "p25": float(np.percentile(a, 25)),
            "p75": float(np.percentile(a, 75)), "min": float(a.min()),
            "max": float(a.max()), "n": len(a)}


def part_a():
    """Per-benchmark C4/C5 at 1000 reps, random query order."""
    faiss.omp_set_num_threads(1)
    rng = np.random.default_rng(99)
    REPS, ROUNDS = 1000, 5
    per = {}
    for f in sorted(glob.glob(os.path.join(DATA, "*.npz"))):
        if f.endswith("_float.npz"):
            continue
        tag = os.path.basename(f)[:-4]
        bench = "lme" if tag.startswith("lme") else (
            "perltqa" if tag.startswith("pq") else "realtalk")
        z = np.load(f)
        docs, qs = z["docs"], z["queries"]
        nq = qs.shape[0]
        zf = np.load(os.path.join(DATA, tag + "_float.npz"))
        C = np.ascontiguousarray(zf["docs"])
        Qf = np.ascontiguousarray(zf["queries"])
        bi = faiss.IndexBinaryFlat(96)
        bi.add(docs)
        fi = faiss.IndexFlatIP(96)
        fi.add(C)
        v1 = mk_v1(docs)
        o = rng.integers(0, nq, REPS)
        for j in range(min(nq, 20)):
            bi.search(qs[j:j + 1], K)
            fi.search(Qf[j:j + 1], K)
            v1(qs[j])
        tb, tf, tn = [], [], []
        for _ in range(ROUNDS):
            tb.append(blk(lambda j: bi.search(qs[j:j + 1], K), o, REPS))
            tf.append(blk(lambda j: fi.search(Qf[j:j + 1], K), o, REPS))
            tn.append(blk(lambda j: v1(qs[j]), o, REPS))
        b, fl, nn = np.median(tb), np.median(tf), np.median(tn)
        d = per.setdefault(bench, {"c4": [], "c5": [], "bms": [], "fms": [],
                                   "N": []})
        d["c4"].append(nn / b)
        d["c5"].append(fl / b)
        d["bms"].append(b * 1e3)
        d["fms"].append(fl * 1e3)
        d["N"].append(docs.shape[0])
    out = {}
    allc4, allc5 = [], []
    for k, v in per.items():
        out[k] = {"archives": len(v["c4"]),
                  "N_median": float(np.median(v["N"])),
                  "C4_numpy_over_binary": summ(v["c4"]),
                  "C5_float_over_binary": summ(v["c5"]),
                  "binary_ms_median": float(np.median(v["bms"])),
                  "float_ms_median": float(np.median(v["fms"]))}
        allc4 += v["c4"]
        allc5 += v["c5"]
    out["overall"] = {"C4": summ(allc4), "C5": summ(allc5)}
    return out


def part_b():
    """Scale sweep on real codes, tiled with perturbation to reach large N."""
    faiss.omp_set_num_threads(1)
    rng = np.random.default_rng(7)
    z = np.load(os.path.join(DATA, "pq00.npz"))
    zf = np.load(os.path.join(DATA, "pq00_float.npz"))
    base_b, base_f = z["docs"], zf["docs"]
    qs, Qf = z["queries"], zf["queries"]
    rows = []
    for N in [64, 256, 1024, 4096, 16384, 65536, 262144, 1048576]:
        reps = 2000 if N <= 16384 else (400 if N <= 262144 else 120)
        r = int(np.ceil(N / base_b.shape[0]))
        db = np.ascontiguousarray(np.tile(base_b, (r, 1))[:N])
        # decorrelate the tiles so the distance distribution is not degenerate
        flip = rng.integers(0, 256, db.shape, dtype=np.uint8)
        mask = rng.random(db.shape) < 0.02
        db = np.ascontiguousarray(np.where(mask, db ^ flip, db))
        df = np.ascontiguousarray(np.tile(base_f, (r, 1))[:N]
                                  + rng.normal(0, .05, (N, 96)).astype(
                                      np.float32))
        bi = faiss.IndexBinaryFlat(96)
        bi.add(db)
        fi = faiss.IndexFlatIP(96)
        fi.add(df)
        v1 = mk_v1(db)
        o = rng.integers(0, qs.shape[0], reps)
        for j in range(10):
            bi.search(qs[j:j + 1], K)
            fi.search(Qf[j:j + 1], K)
            v1(qs[j])
        tb = min(blk(lambda j: bi.search(qs[j:j + 1], K), o, reps)
                 for _ in range(3))
        tf = min(blk(lambda j: fi.search(Qf[j:j + 1], K), o, reps)
                 for _ in range(3))
        tn = min(blk(lambda j: v1(qs[j]), o, reps) for _ in range(3))
        # batched faiss, 256 queries at once, per-query cost
        nb = min(256, qs.shape[0])
        t0 = time.perf_counter()
        for _ in range(5):
            bi.search(qs[:nb], K)
        tbatch = (time.perf_counter() - t0) / 5 / nb
        rows.append({"N": N, "binary_us": tb * 1e6, "float_us": tf * 1e6,
                     "numpy_us": tn * 1e6,
                     "binary_batched_us_per_q": tbatch * 1e6,
                     "C4_numpy_over_binary": tn / tb,
                     "C5_float_over_binary": tf / tb,
                     "binary_ns_per_doc": tb * 1e9 / N,
                     "float_ns_per_doc": tf * 1e9 / N})
    return rows


def main():
    out = {"per_benchmark_high_rep": part_a(), "scale_sweep": part_b()}
    print(json.dumps(out, indent=2))
    with open(os.path.join(HERE, "AUDIT_SCALE.json"), "w") as fh:
        json.dump(out, fh, indent=2)


if __name__ == "__main__":
    main()
