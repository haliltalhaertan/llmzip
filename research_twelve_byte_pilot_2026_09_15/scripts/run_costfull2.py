#!/usr/bin/env python3
"""Re-run the whole-benchmark cost accounting with the optimized scorer.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

Correction to run_fasthamming.py: its fast variants padded 96 bits to 128 and
viewed the rows as 2 x uint64.  That is 16 B/doc, not 12 -- it bought speed
with a 33 % RAM increase and did not say so.  96 bits is exactly 3 x uint32,
so the same element-count reduction (12 -> 3 per row) is available with NO
padding at all.  This script uses the uint32 layout and keeps the padded
uint64 one only as a labelled comparison, so the trade is visible.

Every variant is asserted bit-identical to the frozen `lib_b8` Hamming
scorer on EVERY archive of EVERY benchmark, not on a sample.  Quality is
therefore unchanged by construction; only CPU and RAM move.

Arms, all at their true stored width:
  float96       96 float64                        768 B/doc
  sign_v0       12 B, uint8 xor/popcount          the previously measured path
  sign_u32      12 B, 3 x uint32, preallocated    <- no padding
  sign_u64pad   16 B, 2 x uint64, preallocated    labelled: +33 % RAM
  sign80_u32    10 B stored, padded to 12 to view as 3 x uint32
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

HAS_BC = hasattr(np, "bitwise_count")
POP8 = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)
BUILD_S = 4.85


def popc(a):
    return np.bitwise_count(a) if HAS_BC else POP8[a]


def med(fn, reps=25):
    for _ in range(3):
        fn()
    ts = []
    for _ in range(reps):
        t = time.perf_counter()
        fn()
        ts.append(time.perf_counter() - t)
    return float(np.median(ts))


def make_scorers(C, q):
    C = np.ascontiguousarray(np.asarray(C, dtype=np.float64))
    n = C.shape[0]
    bits = C >= 0
    qb = np.asarray(q, dtype=np.float64) >= 0
    p8 = np.packbits(bits, axis=1, bitorder="big").astype(np.uint8)
    q8 = np.packbits(qb[None, :], axis=1, bitorder="big").astype(np.uint8)[0]
    # ---- uint32: 96 bits == 3 words exactly, no padding ----
    p32 = np.ascontiguousarray(p8).view(np.uint32)                 # n x 3
    q32 = np.ascontiguousarray(q8).view(np.uint32)                 # 3
    x32 = np.empty_like(p32)
    c32 = np.empty(p32.shape, dtype=np.uint8)
    o32 = np.empty(n, dtype=np.int64)
    # ---- uint64: needs 16 B rows, i.e. +33 % RAM ----
    pad = np.zeros((n, 16), dtype=np.uint8)
    pad[:, :12] = p8
    p64 = np.ascontiguousarray(pad).view(np.uint64)                # n x 2
    qpad = np.zeros(16, dtype=np.uint8)
    qpad[:12] = q8
    q64 = qpad.view(np.uint64)
    x64 = np.empty_like(p64)
    c64 = np.empty(p64.shape, dtype=np.uint8)
    o64 = np.empty(n, dtype=np.int64)
    # ---- 80-bit deletion point: 10 B stored, viewed as 3 x uint32 ----
    order = np.lexsort((np.arange(96), -np.var(C, axis=0, ddof=0)))
    keep = np.sort(order[:80])
    s80 = np.packbits(bits[:, keep], axis=1, bitorder="big").astype(np.uint8)
    v80 = np.zeros((n, 12), dtype=np.uint8)
    v80[:, :10] = s80
    v80 = np.ascontiguousarray(v80).view(np.uint32)
    t80 = np.zeros(12, dtype=np.uint8)
    t80[:10] = np.packbits(qb[keep][None, :], axis=1,
                           bitorder="big").astype(np.uint8)[0]
    t80 = t80.view(np.uint32)
    x80 = np.empty_like(v80)
    c80 = np.empty(v80.shape, dtype=np.uint8)
    o80 = np.empty(n, dtype=np.int64)
    cn = np.linalg.norm(C, axis=1)

    def f_float():
        return (C @ q) / cn

    def f_v0():
        return -(popc(np.bitwise_xor(p8, q8[None, :]))
                 .sum(axis=1).astype(np.int64))

    def _packed(p, qq, xb, cb, ob):
        np.bitwise_xor(p, qq[None, :], out=xb)
        if HAS_BC:
            np.bitwise_count(xb, out=cb)
        else:
            cb[:] = popc(xb.view(np.uint8)).reshape(
                xb.shape[0], -1)[:, :xb.shape[1]]
        np.sum(cb, axis=1, dtype=np.int64, out=ob)
        np.negative(ob, out=ob)
        return ob

    def f_u32():
        return _packed(p32, q32, x32, c32, o32)

    def f_u64():
        return _packed(p64, q64, x64, c64, o64)

    def f_80():
        return _packed(v80, t80, x80, c80, o80)

    ram = {"float96": int(C.nbytes + cn.nbytes),
           "sign_v0": int(p8.nbytes),
           "sign_u32": int(p32.nbytes),
           "sign_u64pad": int(p64.nbytes),
           "sign80_u32": int(s80.nbytes)}
    ref = -np.count_nonzero(bits != qb[None, :], axis=1).astype(np.int64)
    ok = all(np.array_equal(np.asarray(f()).astype(np.int64), ref)
             for f in (f_v0, f_u32, f_u64))
    return ({"float96": f_float, "sign_v0": f_v0, "sign_u32": f_u32,
             "sign_u64pad": f_u64, "sign80_u32": f_80}, ram, ok)


ARMS = ["float96", "sign_v0", "sign_u32", "sign_u64pad", "sign80_u32"]


def run(it, nq):
    ramsum = defaultdict(int)
    tsum = defaultdict(float)
    n_arch = 0
    ok_all = True
    for C, QC in it:
        q = np.atleast_2d(np.asarray(QC, float))[0]
        fns, ram, ok = make_scorers(C, q)
        ok_all &= ok
        n_arch += 1
        for a in ARMS:
            ramsum[a] += ram[a]
            tsum[a] += med(fns[a])
    return {"n_archives": n_arch, "n_queries": nq,
            "bit_identical_every_archive": bool(ok_all),
            "total_index_bytes": {a: int(ramsum[a]) for a in ARMS},
            "mean_score_ms": {a: float(tsum[a] / n_arch * 1e3)
                              for a in ARMS},
            "build_seconds_total": n_arch * BUILD_S}


def it_perltqa():
    arch = pickle.load(open(H.ARCH_PKL, "rb"))
    Q = pickle.load(open(H.Q_PKL, "rb"))
    by = defaultdict(list)
    for qid, v in Q.items():
        by[v["char"]].append(qid)
    for ch in sorted(by):
        yield (np.asarray(arch[ch]["C"], float),
               np.asarray(Q[by[ch][0]]["qC"], float))


def it_lme():
    for f in sorted(glob.glob(H.LME_GLOB)):
        d = pickle.loads(open(f, "rb").read())
        yield np.asarray(d["C"], float), np.asarray(d["qC"], float)


def it_rt():
    for f in sorted(glob.glob(H.RT_GLOB)):
        o = pickle.loads(open(f, "rb").read())
        yield np.asarray(o["C"], float), np.asarray(o["QC"], float)[0]


def main():
    res = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "numpy": np.__version__, "native_popcount": HAS_BC,
           "note": "uint32 layout is exactly 12 B/doc, no padding; the "
                   "uint64 layout needs 16 B/doc (+33 % RAM) and is kept "
                   "only as a labelled comparison",
           "benchmarks": {}}
    for name, it, nq in (("perltqa", it_perltqa, 8265),
                         ("lme", it_lme, 470),
                         ("realtalk", it_rt, 705)):
        print(f"=== {name} ===", flush=True)
        b = run(it(), nq)
        res["benchmarks"][name] = b
        print(f"  arşiv={b['n_archives']}  "
              f"her arşivde bit-aynı={b['bit_identical_every_archive']}",
              flush=True)
        for a in ARMS:
            print(f"    {a:12s} {b['total_index_bytes'][a]/1e6:8.2f} MB "
                  f"{b['mean_score_ms'][a]:8.4f} ms")
        f = b["total_index_bytes"]["float96"]
        tf = b["mean_score_ms"]["float96"]
        for a in ("sign_v0", "sign_u32", "sign_u64pad", "sign80_u32"):
            print(f"    -> {a:12s} RAM {f/b['total_index_bytes'][a]:5.1f}x  "
                  f"CPU {tf/b['mean_score_ms'][a]:5.2f}x")
    with open("COSTFULL2.json", "w") as fh:
        json.dump(res, fh, indent=2)
    print("\nwrote COSTFULL2.json", flush=True)


if __name__ == "__main__":
    main()
