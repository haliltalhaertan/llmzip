#!/usr/bin/env python3
"""INDEPENDENT AUDIT of C4 (faiss vs numpy) and C5 (binary vs float32).

Attacks: W1 (reps=min(nq,60) -> 1 call on 50 archives), W2 (index-order query
access), and the unexamined question of whether the numpy baseline is actually
the best numpy implementation.
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
POP8 = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)


# ------------------------------------------------------------ numpy kernels
def mk_v1(docs):
    """The baseline used in run_faiss_deep.py: uint32 view."""
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


def mk_v2(docs):
    """uint8 lanes, uint16 accumulator."""
    p = np.ascontiguousarray(docs)
    x = np.empty_like(p)
    o = np.empty(docs.shape[0], dtype=np.uint16)

    def f(q):
        np.bitwise_xor(p, q[None, :], out=x)
        np.bitwise_count(x, out=x)
        np.sum(x, axis=1, dtype=np.uint16, out=o)
        t = np.argpartition(o, K)[:K]
        return o[t]
    return f


def mk_v3(docs):
    """256-entry popcount LUT."""
    p = np.ascontiguousarray(docs)
    x = np.empty_like(p)
    o = np.empty(docs.shape[0], dtype=np.uint16)

    def f(q):
        np.bitwise_xor(p, q[None, :], out=x)
        np.take(POP8, x, out=x)
        np.sum(x, axis=1, dtype=np.uint16, out=o)
        t = np.argpartition(o, K)[:K]
        return o[t]
    return f


def mk_v4(docs):
    """12 bytes padded to 16 -> two uint64 lanes.  Padding XORs to 0."""
    n = docs.shape[0]
    pad = np.zeros((n, 16), dtype=np.uint8)
    pad[:, :12] = docs
    p64 = np.ascontiguousarray(pad).view(np.uint64)
    x = np.empty_like(p64)
    c = np.empty(p64.shape, dtype=np.uint8)
    o = np.empty(n, dtype=np.int64)
    qbuf = np.zeros(16, dtype=np.uint8)

    def f(q):
        qbuf[:12] = q
        q64 = qbuf.view(np.uint64)
        np.bitwise_xor(p64, q64[None, :], out=x)
        np.bitwise_count(x, out=c)
        np.sum(c, axis=1, dtype=np.int64, out=o)
        t = np.argpartition(o, K)[:K]
        return o[t]
    return f


def mk_v4_fair(docs):
    """v4 but returning SORTED distances AND labels, matching faiss output."""
    n = docs.shape[0]
    pad = np.zeros((n, 16), dtype=np.uint8)
    pad[:, :12] = docs
    p64 = np.ascontiguousarray(pad).view(np.uint64)
    x = np.empty_like(p64)
    c = np.empty(p64.shape, dtype=np.uint8)
    o = np.empty(n, dtype=np.int64)
    qbuf = np.zeros(16, dtype=np.uint8)

    def f(q):
        qbuf[:12] = q
        q64 = qbuf.view(np.uint64)
        np.bitwise_xor(p64, q64[None, :], out=x)
        np.bitwise_count(x, out=c)
        np.sum(c, axis=1, dtype=np.int64, out=o)
        t = np.argpartition(o, K)[:K]
        s = np.argsort(o[t], kind="stable")
        return o[t[s]], t[s]
    return f


KERNELS = {"v1_uint32_baseline": mk_v1, "v2_uint8": mk_v2,
           "v3_lut": mk_v3, "v4_uint64pad": mk_v4,
           "v4_fair_sorted_labels": mk_v4_fair}


def time_block(fn, order, reps):
    t0 = time.perf_counter()
    for i in range(reps):
        fn(order[i])
    return (time.perf_counter() - t0) / reps


def archives():
    for f in sorted(glob.glob(os.path.join(DATA, "*.npz"))):
        if f.endswith("_float.npz"):
            continue
        t = os.path.basename(f)[:-4]
        b = "lme" if t.startswith("lme") else (
            "perltqa" if t.startswith("pq") else "realtalk")
        yield t, f, b


def summ(v):
    a = np.asarray(v, float)
    return {"median": float(np.median(a)), "p25": float(np.percentile(a, 25)),
            "p75": float(np.percentile(a, 75)), "min": float(a.min()),
            "max": float(a.max())}


def main():
    faiss.omp_set_num_threads(1)
    rng = np.random.default_rng(4242)
    REPS = 1000
    ROUNDS = 5

    res = {"reps_per_block": REPS, "rounds": ROUNDS,
           "faiss": faiss.__version__, "numpy": np.__version__}
    sp = {k: {"idx": [], "rnd": []} for k in KERNELS}
    float_sp = {"idx": [], "rnd": []}
    orig_protocol_runs = []

    for tag, f, bench in archives():
        z = np.load(f, allow_pickle=True)
        docs, qs = z["docs"], z["queries"]
        n, nq = docs.shape[0], qs.shape[0]
        zf = np.load(os.path.join(DATA, tag + "_float.npz"))
        C = np.ascontiguousarray(zf["docs"])
        Qf = np.ascontiguousarray(zf["queries"])

        bi = faiss.IndexBinaryFlat(96)
        bi.add(docs)
        fi = faiss.IndexFlatIP(96)
        fi.add(C)

        ord_idx = np.arange(REPS) % nq
        ord_rnd = rng.integers(0, nq, REPS)

        kern = {k: mk(docs) for k, mk in KERNELS.items()}

        def fa(j):
            return bi.search(qs[j:j + 1], K)

        def ff(j):
            return fi.search(Qf[j:j + 1], K)

        # correctness of every kernel before it is timed
        for k, fn in kern.items():
            r = fn(qs[0])
            dd = r[0] if isinstance(r, tuple) else r
            assert np.array_equal(np.sort(np.asarray(dd).astype(np.int64)),
                                  np.sort(z["refdist"][0])[:K]), (tag, k)

        # warm-up
        for j in range(min(nq, 20)):
            fa(j)
            ff(j)
            for fn in kern.values():
                fn(qs[j])

        tf_i = tf_r = tfl_i = tfl_r = []
        acc = {k: {"idx": [], "rnd": []} for k in KERNELS}
        accf = {"idx": [], "rnd": []}
        accb = {"idx": [], "rnd": []}
        for _ in range(ROUNDS):
            accb["idx"].append(time_block(fa, ord_idx, REPS))
            accb["rnd"].append(time_block(fa, ord_rnd, REPS))
            accf["idx"].append(time_block(ff, ord_idx, REPS))
            accf["rnd"].append(time_block(ff, ord_rnd, REPS))
            for k, fn in kern.items():
                g = (lambda fn: lambda j: fn(qs[j]))(fn)
                acc[k]["idx"].append(time_block(g, ord_idx, REPS))
                acc[k]["rnd"].append(time_block(g, ord_rnd, REPS))
        tb_i, tb_r = np.median(accb["idx"]), np.median(accb["rnd"])
        tfl_i, tfl_r = np.median(accf["idx"]), np.median(accf["rnd"])
        for k in KERNELS:
            sp[k]["idx"].append(np.median(acc[k]["idx"]) / tb_i)
            sp[k]["rnd"].append(np.median(acc[k]["rnd"]) / tb_r)
        float_sp["idx"].append(tfl_i / tb_i)
        float_sp["rnd"].append(tfl_r / tb_r)

        # ---- W1: replicate the ORIGINAL protocol (reps=min(nq,60)) 25x
        v1 = kern["v1_uint32_baseline"]
        reps0 = min(nq, 60)
        runs = []
        for _ in range(25):
            for j in range(min(nq, 5)):
                v1(qs[j])
                fa(j)
            t0 = time.perf_counter()
            for j in range(reps0):
                v1(qs[j % nq])
            tn = (time.perf_counter() - t0) / reps0
            t0 = time.perf_counter()
            for j in range(reps0):
                fa(j % nq)
            tfa = (time.perf_counter() - t0) / reps0
            runs.append(tn / tfa)
        orig_protocol_runs.append({"tag": tag, "bench": bench, "nq": nq,
                                   "runs": runs})

    res["C4_speedup_vs_faiss_binary"] = {
        k: {"index_order": summ(sp[k]["idx"]),
            "random_order": summ(sp[k]["rnd"])} for k in KERNELS}
    res["C5_float32_over_binary"] = {
        "index_order": summ(float_sp["idx"]),
        "random_order": summ(float_sp["rnd"])}

    # W1 analysis
    per_arch_spread = []
    medians_of_runs = []
    for r in orig_protocol_runs:
        a = np.asarray(r["runs"])
        per_arch_spread.append({
            "tag": r["tag"], "nq": r["nq"],
            "cv": float(a.std(ddof=1) / a.mean()),
            "min": float(a.min()), "max": float(a.max()),
            "ratio_max_min": float(a.max() / a.min())})
        medians_of_runs.append(a)
    M = np.asarray(medians_of_runs)          # (90, 25)
    # what median-across-archives would the original protocol have reported?
    reported = np.median(M, axis=0)          # 25 independent replications
    lme_mask = np.array([r["nq"] == 1 for r in orig_protocol_runs])
    res["W1_original_protocol_instability"] = {
        "replications": 25,
        "reported_overall_median_across_replications": {
            "mean": float(reported.mean()), "sd": float(reported.std(ddof=1)),
            "min": float(reported.min()), "max": float(reported.max()),
            "range": float(reported.max() - reported.min())},
        "published_value": 3.3874372216220046,
        "per_archive_cv_median_nq_eq_1": float(np.median(
            [s["cv"] for s, m in zip(per_arch_spread, lme_mask) if m])),
        "per_archive_cv_median_nq_gt_1": float(np.median(
            [s["cv"] for s, m in zip(per_arch_spread, lme_mask) if not m])),
        "per_archive_maxmin_median_nq_eq_1": float(np.median(
            [s["ratio_max_min"] for s, m in zip(per_arch_spread, lme_mask)
             if m])),
        "per_archive_maxmin_median_nq_gt_1": float(np.median(
            [s["ratio_max_min"] for s, m in zip(per_arch_spread, lme_mask)
             if not m])),
    }
    print(json.dumps(res, indent=2))
    with open(os.path.join(HERE, "AUDIT_TIMING.json"), "w") as fh:
        json.dump(res, fh, indent=2)


if __name__ == "__main__":
    main()
