#!/usr/bin/env python3
"""How much CPU is left on the table for the packed Hamming scorer?

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

At N~500 the real arithmetic is ~1 us of XOR; we measure ~17 us.  The gap is
numpy dispatch, not computation, so the only pure-numpy levers are (a) making
fewer calls and (b) doing more work per call.

  s1_4call    current best: xor -> count -> sum -> negate        (uint32)
  s2_3call    drop the negate; rank ascending on distance instead
  s3_2call    precomputed uint16 popcount table: xor -> gather+sum
  batch_*     all of an archive's queries in ONE set of calls, reported as
              time PER QUERY -- this is the benchmark-evaluation regime, not
              single-query latency, and the two must not be conflated

The float baseline is measured in BOTH regimes too (matvec and GEMM), because
batching a bit scorer and comparing it against an unbatched float one would
be a rigged comparison.

Every variant is asserted bit-identical to the frozen lib_b8 scorer.
"""
import glob
import json
import os
import pickle
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_hit10 as H  # noqa: E402

POP16 = np.array([bin(i).count("1") for i in range(1 << 16)], dtype=np.uint8)


def med(fn, reps):
    for _ in range(4):
        fn()
    ts = []
    for _ in range(reps):
        t = time.perf_counter()
        fn()
        ts.append(time.perf_counter() - t)
    return float(np.median(ts))


def bench(C, QC, reps=30):
    C = np.ascontiguousarray(np.asarray(C, dtype=np.float64))
    QC = np.ascontiguousarray(np.atleast_2d(np.asarray(QC, dtype=np.float64)))
    n, nq = C.shape[0], QC.shape[0]
    bits = C >= 0
    qbits = QC >= 0
    p8 = np.packbits(bits, axis=1, bitorder="big").astype(np.uint8)
    q8 = np.packbits(qbits, axis=1, bitorder="big").astype(np.uint8)
    p32 = np.ascontiguousarray(p8).view(np.uint32)          # n x 3
    q32 = np.ascontiguousarray(q8).view(np.uint32)          # nq x 3
    p16 = np.ascontiguousarray(p8).view(np.uint16)          # n x 6
    q16 = np.ascontiguousarray(q8).view(np.uint16)          # nq x 6
    q0_32, q0_16 = q32[0], q16[0]
    x = np.empty_like(p32)
    c = np.empty(p32.shape, dtype=np.uint8)
    o = np.empty(n, dtype=np.int64)
    x16 = np.empty_like(p16)
    cn = np.linalg.norm(C, axis=1)
    q0 = QC[0]
    ref = -np.count_nonzero(bits != qbits[0][None, :], axis=1).astype(np.int64)

    def s1_4call():
        np.bitwise_xor(p32, q0_32[None, :], out=x)
        np.bitwise_count(x, out=c)
        np.sum(c, axis=1, dtype=np.int64, out=o)
        np.negative(o, out=o)
        return o

    def s2_3call():                       # distance, ascending is better
        np.bitwise_xor(p32, q0_32[None, :], out=x)
        np.bitwise_count(x, out=c)
        return np.sum(c, axis=1, dtype=np.int64, out=o)

    def s3_2call():
        np.bitwise_xor(p16, q0_16[None, :], out=x16)
        return POP16[x16].sum(axis=1, dtype=np.int64)

    def f_matvec():
        return (C @ q0) / cn

    def b_packed():                       # all nq queries at once
        xx = np.bitwise_xor(p32[:, None, :], q32[None, :, :])
        return np.bitwise_count(xx).sum(axis=2, dtype=np.int16)

    def b_float():
        return (C @ QC.T) / cn[:, None]

    out = {"N": int(n), "n_queries": int(nq)}
    checks = {
        "s1_4call": np.array_equal(s1_4call().copy(), ref),
        "s2_3call": np.array_equal(-s2_3call().copy(), ref),
        "s3_2call": np.array_equal(-s3_2call(), ref),
        "batch_packed": np.array_equal(-b_packed()[:, 0].astype(np.int64), ref),
    }
    out["bit_identical"] = checks
    out["single_ms"] = {
        "float96_matvec": med(f_matvec, reps) * 1e3,
        "s1_4call": med(s1_4call, reps) * 1e3,
        "s2_3call": med(s2_3call, reps) * 1e3,
        "s3_2call": med(s3_2call, reps) * 1e3,
    }
    if nq > 1:
        bp = med(b_packed, max(5, reps // 6))
        bf = med(b_float, max(5, reps // 6))
        out["batch_ms_per_query"] = {"packed": bp / nq * 1e3,
                                     "float96": bf / nq * 1e3}
        out["batch_total_ms"] = {"packed": bp * 1e3, "float96": bf * 1e3}
    return out


def main():
    res = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "numpy": np.__version__, "cases": {}}

    # LME: one query per archive -> single-query regime only
    d = pickle.loads(open(sorted(glob.glob(H.LME_GLOB))[0], "rb").read())
    res["cases"]["lme_archive"] = bench(np.asarray(d["C"], float),
                                        np.asarray(d["qC"], float))
    # PerLTQA: many queries per archive -> both regimes
    arch = pickle.load(open(H.ARCH_PKL, "rb"))
    Q = pickle.load(open(H.Q_PKL, "rb"))
    from collections import defaultdict
    by = defaultdict(list)
    for qid, v in Q.items():
        by[v["char"]].append(qid)
    ch = sorted(by)[0]
    res["cases"]["perltqa_archive"] = bench(
        np.asarray(arch[ch]["C"], float),
        np.stack([np.asarray(Q[q]["qC"], float) for q in sorted(by[ch])]))
    del arch, Q
    # RealTalk: many queries per archive
    o = pickle.loads(open(sorted(glob.glob(H.RT_GLOB))[0], "rb").read())
    res["cases"]["realtalk_archive"] = bench(np.asarray(o["C"], float),
                                             np.asarray(o["QC"], float))

    for k, v in res["cases"].items():
        print(f"\n== {k}  N={v['N']:,}  sorgu={v['n_queries']} ==")
        print(f"  bit-aynı: {v['bit_identical']}")
        s = v["single_ms"]
        base = s["float96_matvec"]
        for a in ("float96_matvec", "s1_4call", "s2_3call", "s3_2call"):
            print(f"    {a:16s} {s[a]:8.4f} ms   {base/s[a]:5.2f}x float")
        if "batch_ms_per_query" in v:
            b = v["batch_ms_per_query"]
            print(f"    -- toplu (sorgu başına) --")
            print(f"    {'packed':16s} {b['packed']:8.4f} ms   "
                  f"{base/b['packed']:5.2f}x tek-sorgu float")
            print(f"    {'float96':16s} {b['float96']:8.4f} ms   "
                  f"packed/float = {b['packed']/b['float96']:.2f}x")
    with open("FASTER.json", "w") as f:
        json.dump(res, f, indent=2)
    print("\nwrote FASTER.json")


if __name__ == "__main__":
    main()
