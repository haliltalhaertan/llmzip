#!/usr/bin/env python3
"""Can the packed Hamming scorer stop being slower than the float baseline?

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

Measured earlier: packed 12-byte Hamming is ~3x SLOWER than the float96
cosine it is supposed to beat, at real archive sizes (~500 docs).  The work
itself is 6 KB of XOR -- about a microsecond of CPU -- so the 30 us is not
arithmetic, it is four numpy calls each allocating a temporary.

Variants, all bit-identical to the frozen scorer (asserted, not assumed):

  v0_uint8      what run_cost.py timed: xor -> popcount -> sum -> astype
  v1_uint64     96 bits padded to 128 and viewed as 2 uint64 per row, so the
                same work touches 1/6 as many array elements
  v2_prealloc   v1 with out= buffers, so nothing is allocated per call
  v3_table      one 256-entry popcount gather per byte column, accumulated
  ref_float_pm1 Hamming via BLAS on a +-1 float matrix -- fastest possible,
                but needs 768 B/doc, so it buys speed by giving up the budget

The point of ref_float_pm1 is to make the trade explicit: if the only way to
win on CPU is to hold the float matrix, then the 12-byte budget is a RAM
decision, not a latency one, and should be reported that way.
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

HAS_BC = hasattr(np, "bitwise_count")
POP8 = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)
NS = (500, 5_000, 50_000, 500_000)


def popc(a):
    return np.bitwise_count(a) if HAS_BC else POP8[a]


def med(fn, reps):
    for _ in range(5):
        fn()
    ts = []
    for _ in range(reps):
        t = time.perf_counter()
        fn()
        ts.append(time.perf_counter() - t)
    return float(np.median(ts))


def build(C):
    """Every layout a variant needs, plus the reference answer."""
    bits = (np.asarray(C, dtype=np.float64) >= 0)
    n = bits.shape[0]
    p8 = np.packbits(bits, axis=1, bitorder="big").astype(np.uint8)   # n x 12
    pad = np.zeros((n, 16), dtype=np.uint8)
    pad[:, :12] = p8
    p64 = np.ascontiguousarray(pad).view(np.uint64)                   # n x 2
    pm1 = np.where(bits, 1.0, -1.0)
    return p8, p64, pm1


def build_q(q):
    b = (np.asarray(q, dtype=np.float64) >= 0)
    q8 = np.packbits(b[None, :], axis=1, bitorder="big").astype(np.uint8)[0]
    pad = np.zeros(16, dtype=np.uint8)
    pad[:12] = q8
    q64 = pad.view(np.uint64)
    return q8, q64, np.where(b, 1.0, -1.0)


def bench_one(C, q, reps):
    p8, p64, pm1 = build(C)
    q8, q64, qpm = build_q(q)
    n = C.shape[0]
    ref = -np.count_nonzero((C >= 0) != (q >= 0)[None, :],
                            axis=1).astype(np.int64)

    def v0():
        return -(popc(np.bitwise_xor(p8, q8[None, :]))
                 .sum(axis=1).astype(np.int64))

    def v1():
        return -(popc(np.bitwise_xor(p64, q64[None, :]))
                 .sum(axis=1).astype(np.int64))

    xbuf = np.empty_like(p64)
    cbuf = np.empty(p64.shape, dtype=np.uint8)
    obuf = np.empty(n, dtype=np.int64)

    def v2():
        np.bitwise_xor(p64, q64[None, :], out=xbuf)
        if HAS_BC:
            np.bitwise_count(xbuf, out=cbuf)
        else:
            cbuf[:] = POP8[xbuf.view(np.uint8)].reshape(n, -1)[:, :2]
        np.sum(cbuf, axis=1, dtype=np.int64, out=obuf)
        np.negative(obuf, out=obuf)
        return obuf

    tabs = np.stack([POP8[np.arange(256, dtype=np.uint8) ^ q8[j]]
                     for j in range(12)]).astype(np.int64)

    def v3():
        acc = tabs[0][p8[:, 0]]
        for j in range(1, 12):
            acc = acc + tabs[j][p8[:, j]]
        return -acc

    def ref_float():
        return (pm1 @ qpm - 96.0) * 0.5

    out = {"N": int(n)}
    for name, fn in (("v0_uint8", v0), ("v1_uint64", v1),
                     ("v2_prealloc", v2), ("v3_table", v3)):
        got = np.asarray(fn()).astype(np.int64)
        if not np.array_equal(got, ref):
            out[name + "_MISMATCH"] = True
            out[name] = None
            continue
        out[name] = med(fn, reps) * 1e3
    rf = np.rint(ref_float()).astype(np.int64)
    out["ref_float_pm1_matches"] = bool(np.array_equal(rf, ref))
    out["ref_float_pm1"] = med(ref_float, reps) * 1e3
    cn = np.linalg.norm(np.asarray(C, float), axis=1)
    Cc = np.ascontiguousarray(np.asarray(C, float))
    out["float96_cosine"] = med(lambda: (Cc @ q) / cn, reps) * 1e3
    out["ram_bytes"] = {"packed12": int(p8.nbytes), "packed16": int(p64.nbytes),
                        "pm1_float": int(pm1.nbytes),
                        "float96": int(Cc.nbytes)}
    return out


def main():
    d = pickle.loads(open(sorted(glob.glob(H.LME_GLOB))[0], "rb").read())
    C0 = np.asarray(d["C"], float)
    q = np.asarray(d["qC"], float).reshape(-1)
    res = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "numpy": np.__version__, "native_popcount": HAS_BC,
           "all_variants_bit_identical_to_frozen_scorer": True,
           "sizes": {}}
    rng = np.random.default_rng(0)
    for n in NS:
        if n <= C0.shape[0]:
            C = C0[:n]
        else:
            idx = rng.integers(0, C0.shape[0], size=n)
            C = np.ascontiguousarray(C0[idx] + rng.normal(0, 1e-3, (n, 96)))
        reps = 40 if n <= 50_000 else 8
        r = bench_one(C, q, reps)
        res["sizes"][str(n)] = r
        if any(k.endswith("_MISMATCH") for k in r):
            res["all_variants_bit_identical_to_frozen_scorer"] = False
        base = r["float96_cosine"]
        best = min((v, k) for k, v in r.items()
                   if k in ("v0_uint8", "v1_uint64", "v2_prealloc",
                            "v3_table") and v is not None)
        print(f"N={n:>7,}  float96={base:8.4f} ms   "
              f"v0={r['v0_uint8']:7.4f}  v1={r['v1_uint64']:7.4f}  "
              f"v2={r['v2_prealloc']:7.4f}  v3={r['v3_table']:7.4f}  "
              f"pm1={r['ref_float_pm1']:7.4f}   "
              f"| en iyi packed {best[1]} -> {base / best[0]:.2f}x float",
              flush=True)
    with open("FASTHAMMING.json", "w") as f:
        json.dump(res, f, indent=2)
    print("\nwrote FASTHAMMING.json", flush=True)


if __name__ == "__main__":
    main()
