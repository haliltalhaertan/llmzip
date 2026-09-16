#!/usr/bin/env python3
"""What the scaled-query win costs in CPU and RAM.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

`run_qscale.py` established a real, significant quality gain on all three
benchmarks from scaling the query per coordinate, with the stored document
bits untouched.  That result is incomplete until its cost is on the table,
because the new scorer is NOT the XOR/popcount path:

    sym      3 x uint32 XOR + popcount + sum        the production kernel
    qscale   R @ (q / std), a dense +-1 matvec      96 float ops per document

qscale and qscale_dot ranked identically in the quality run (all +-1 rows
share a norm, so the cosine denominators cannot change the order), so the
cheapest correct form is the plain dot product, and that is what is timed.

One arithmetic identity is worth exploiting and is measured as `qscale_bits`:
for a +-1 row, sum_j r_j w_j = 2 * (sum of w over set bits) - sum(w).  So the
score can be read straight off the packed bits without materialising the
+-1 matrix -- it saves the 768 B/doc reconstruction, though not the per-
coordinate float work.

RAM is reported as the honest total: packed bits PLUS the 96-float scale
array per archive, against the float64 documents it replaces.
"""
import glob
import json
import os
import pickle
import sys
import time
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_hit10 as H  # noqa: E402
sys.path.insert(0, os.path.join(H.SRC, "parallel_ideas_r1", "b8"))
import lib_b8 as B  # noqa: E402

REPS = 200


def med(fn, reps=REPS):
    for _ in range(5):
        fn()
    ts = []
    for _ in range(reps):
        t = time.perf_counter()
        fn()
        ts.append(time.perf_counter() - t)
    return float(np.median(ts))


def bench(C, q):
    C = np.ascontiguousarray(np.asarray(C, dtype=np.float64))
    n = C.shape[0]
    st = B.fit_archive(C)
    std = np.asarray(st["std"], dtype=np.float64)
    bits = C >= 0
    p8 = np.packbits(bits, axis=1, bitorder="big").astype(np.uint8)
    p32 = np.ascontiguousarray(p8).view(np.uint32)
    q = np.asarray(q, dtype=np.float64).reshape(-1)
    qb = np.packbits((q >= 0)[None, :], axis=1,
                     bitorder="big").astype(np.uint8)[0]
    q32 = np.ascontiguousarray(qb).view(np.uint32)
    R = np.where(bits, 1.0, -1.0)
    w = q / std
    wsum = float(w.sum())
    x = np.empty_like(p32)
    c = np.empty(p32.shape, dtype=np.uint8)
    o = np.empty(n, dtype=np.int64)
    cn = np.linalg.norm(C, axis=1)

    def f_sym():
        np.bitwise_xor(p32, q32[None, :], out=x)
        np.bitwise_count(x, out=c)
        return np.sum(c, axis=1, dtype=np.int64, out=o)

    def f_qscale():
        return R @ w

    def f_qscale_bits():
        # 2 * (sum of w over set bits) - sum(w), straight off the bit matrix
        return 2.0 * (bits @ w) - wsum

    def f_float():
        return (C @ q) / cn

    ref = R @ w
    ok_bits = bool(np.allclose(f_qscale_bits(), ref, rtol=0, atol=1e-9))
    return {
        "N": int(n),
        "qscale_bits_matches_qscale": ok_bits,
        "ms": {"sym": med(f_sym) * 1e3,
               "qscale": med(f_qscale) * 1e3,
               "qscale_bits": med(f_qscale_bits) * 1e3,
               "float64": med(f_float) * 1e3},
        "bytes": {"packed_bits": int(p8.nbytes),
                  "std_array_f32": int(np.asarray(std, np.float32).nbytes),
                  "pm1_matrix": int(R.nbytes),
                  "float64_docs": int(C.nbytes)},
    }


def main():
    res = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "benchmarks": {}}
    for name in ("perltqa", "lme", "realtalk"):
        rows = []
        if name == "lme":
            for f in sorted(glob.glob(H.LME_GLOB)):
                d = pickle.loads(open(f, "rb").read())
                rows.append(bench(d["C"], np.asarray(d["qC"], float)))
        elif name == "realtalk":
            for f in sorted(glob.glob(H.RT_GLOB)):
                o = pickle.loads(open(f, "rb").read())
                rows.append(bench(o["C"], np.asarray(o["QC"], float)[0]))
        else:
            arch = pickle.load(open(H.ARCH_PKL, "rb"))
            Q = pickle.load(open(H.Q_PKL, "rb"))
            by = defaultdict(list)
            for qid, v in Q.items():
                by[v["char"]].append(qid)
            for ch in sorted(by):
                rows.append(bench(arch[ch]["C"],
                                  np.asarray(Q[by[ch][0]]["qC"], float)))
            del arch, Q
        tb = defaultdict(int)
        for r in rows:
            for k, v in r["bytes"].items():
                tb[k] += v
        ms = {k: float(np.mean([r["ms"][k] for r in rows]))
              for k in rows[0]["ms"]}
        idx_new = tb["packed_bits"] + tb["std_array_f32"]
        res["benchmarks"][name] = {
            "n_archives": len(rows),
            "identity_holds_every_archive": all(
                r["qscale_bits_matches_qscale"] for r in rows),
            "mean_ms": ms,
            "total_index_bytes": dict(tb),
            "index_bits_plus_std_MB": idx_new / 1e6,
            "ram_ratio_vs_float64": tb["float64_docs"] / idx_new,
            "cpu_ratio_qscale_bits_over_sym": ms["qscale_bits"] / ms["sym"],
            "cpu_ratio_qscale_bits_over_float64": ms["qscale_bits"] / ms["float64"]}
        v = res["benchmarks"][name]
        print(f"\n=== {name}  {v['n_archives']} arsiv ===")
        print(f"  kimlik her arsivde tuttu: {v['identity_holds_every_archive']}")
        for k in ("sym", "qscale", "qscale_bits", "float64"):
            print(f"    {k:14s} {ms[k]*1e3:8.2f} us")
        print(f"  qscale_bits / sym      : "
              f"{v['cpu_ratio_qscale_bits_over_sym']:.2f}x yavas")
        print(f"  qscale_bits / float64  : "
              f"{v['cpu_ratio_qscale_bits_over_float64']:.2f}x")
        print(f"  RAM: {v['index_bits_plus_std_MB']:.3f} MB "
              f"(bit + std) vs {tb['float64_docs']/1e6:.2f} MB float64 "
              f"-> {v['ram_ratio_vs_float64']:.1f}x", flush=True)

    with open(os.path.join(HERE, "QSCALE_COST.json"), "w") as fh:
        json.dump(res, fh, indent=2)
    print("\nwrote QSCALE_COST.json")


if __name__ == "__main__":
    main()
