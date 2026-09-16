#!/usr/bin/env python3
"""Keeping the scaled-query quality without paying a dense float matvec.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

`run_qscale.py` found a real, significant quality gain (+2.4 to +4.2 pp on
three benchmarks) from scaling the query per coordinate, with the stored
document bits untouched.  `run_qscale_cost.py` then showed the catch: the
scorer is no longer XOR/popcount.  It is fast only when the +-1 matrix is
materialised at 768 B/doc, which gives the memory back.

The score is s_i = sum_j r_ij w_j with r = +-1 and w = q / std.  Ranking by it
is the same as ranking by the bit-vector dot product, since
sum_j r_ij w_j = 2 * (b_i . w) - sum(w) and the second term is constant per
query.  Three ways to get it cheaply from 12 bytes:

  lut8      12 byte-wide tables of 256 partial sums, gathered and added.
            Table build is 12*256 work per QUERY, so it amortises only when
            there are many documents per query.
  lut4      24 nibble tables of 16 entries; smaller tables, more gathers.
  rerank_M  score everything with the production popcount kernel, keep the
            top M, and apply the scaled scorer to those M only.

rerank is the one with a quality knob, so its cost AND its quality are both
measured here at several M.  Its ceiling is whatever the Hamming stage puts
inside the top M: a gold that Hamming buries at rank 150 cannot be recovered
by reranking 100.  That ceiling is exactly what the sweep exposes.

Baselines timed alongside: the production `sym`, the dense `qscale`, and
float64, so every number is comparable to run_qscale_cost.py.
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

MS = (10, 20, 50, 100, 200)
REPS = 120
K = 10


def build_lut8(w):
    """T[c, byte] = sum of w over the bits set in that byte of chunk c."""
    T = np.zeros((12, 256), dtype=np.float64)
    for c in range(12):
        seg = w[c * 8:(c + 1) * 8]
        for b in range(256):
            m = 0.0
            for k in range(8):
                if b & (1 << (7 - k)):
                    m += seg[k]
            T[c, b] = m
    return T


def build_lut8_fast(w):
    """same table, vectorised: 256 x 8 bit pattern matrix times the segment."""
    pat = ((np.arange(256)[:, None] >> np.arange(7, -1, -1)) & 1).astype(
        np.float64)                                    # 256 x 8
    return (pat @ w.reshape(12, 8).T).T                # 12 x 256


def build_lut4(w):
    pat = ((np.arange(16)[:, None] >> np.arange(3, -1, -1)) & 1).astype(
        np.float64)                                    # 16 x 4
    return (pat @ w.reshape(24, 4).T).T                # 24 x 16


def med(fn, reps=REPS):
    for _ in range(5):
        fn()
    ts = []
    for _ in range(reps):
        t = time.perf_counter()
        fn()
        ts.append(time.perf_counter() - t)
    return float(np.median(ts))


def bench_archive(C, queries, golds, acc, tm):
    C = np.ascontiguousarray(np.asarray(C, dtype=np.float64))
    n = C.shape[0]
    st = B.fit_archive(C)
    std = np.asarray(st["std"], dtype=np.float64)
    bits = C >= 0
    p8 = np.ascontiguousarray(
        np.packbits(bits, axis=1, bitorder="big").astype(np.uint8))
    p32 = np.ascontiguousarray(p8).view(np.uint32)
    hi = np.ascontiguousarray(p8 >> 4)
    lo = np.ascontiguousarray(p8 & 0x0F)
    nib = np.ascontiguousarray(np.empty((n, 24), dtype=np.uint8))
    nib[:, 0::2] = hi
    nib[:, 1::2] = lo
    R = np.where(bits, 1.0, -1.0)
    x = np.empty_like(p32)
    cc = np.empty(p32.shape, dtype=np.uint8)
    o = np.empty(n, dtype=np.int64)
    cols8 = np.arange(12)
    cols4 = np.arange(24)

    # ---------------- quality ----------------
    for j, qv in enumerate(queries):
        q = np.asarray(qv, dtype=np.float64).reshape(-1)
        g = np.asarray(golds[j]).ravel().astype(int)
        w = q / std
        qb = (q >= 0)
        ham = (-np.count_nonzero(bits != qb[None, :], axis=1)).astype(
            np.float64)
        full = R @ w
        acc[("sym", 0)].append(H.hit_at_k(ham, g, K))
        acc[("qscale_full", 0)].append(H.hit_at_k(full, g, K))
        for M in MS:
            m = min(M, n)
            cand = np.argpartition(-ham, m - 1)[:m]
            # ties at the M-th place: take them all, so the stage is honest
            thr = ham[cand].min()
            cand = np.nonzero(ham >= thr)[0]
            sc = np.full(n, -np.inf)
            sc[cand] = full[cand]
            acc[("rerank", M)].append(H.hit_at_k(sc, g, K))

    # ---------------- cost, on the archive's first query ----------------
    q = np.asarray(queries[0], dtype=np.float64).reshape(-1)
    w = q / std
    qb32 = np.ascontiguousarray(
        np.packbits((q >= 0)[None, :], axis=1,
                    bitorder="big").astype(np.uint8)[0]).view(np.uint32)

    def f_sym():
        np.bitwise_xor(p32, qb32[None, :], out=x)
        np.bitwise_count(x, out=cc)
        return np.sum(cc, axis=1, dtype=np.int64, out=o)

    def f_qscale():
        return R @ w

    def f_lut8():
        T = build_lut8_fast(w)
        return T[cols8[None, :], p8].sum(axis=1)

    def f_lut4():
        T = build_lut4(w)
        return T[cols4[None, :], nib].sum(axis=1)

    def f_rerank(M):
        def g():
            np.bitwise_xor(p32, qb32[None, :], out=x)
            np.bitwise_count(x, out=cc)
            np.sum(cc, axis=1, dtype=np.int64, out=o)
            m = min(M, n)
            cand = np.argpartition(o, m - 1)[:m]
            return R[cand] @ w
        return g

    ref = R @ w
    tm["lut8_ok"].append(bool(np.allclose(f_lut8() * 2.0 - w.sum(), ref,
                                          rtol=0, atol=1e-8)))
    tm["lut4_ok"].append(bool(np.allclose(f_lut4() * 2.0 - w.sum(), ref,
                                          rtol=0, atol=1e-8)))
    tm["sym"].append(med(f_sym))
    tm["qscale"].append(med(f_qscale))
    tm["lut8"].append(med(f_lut8))
    tm["lut4"].append(med(f_lut4))
    for M in MS:
        tm[f"rerank{M}"].append(med(f_rerank(M)))
    tm["N"].append(n)


def main():
    which = sys.argv[1:] or ["perltqa", "lme", "realtalk"]
    res = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "k": K, "benchmarks": {}}
    for name in which:
        acc = defaultdict(list)
        tm = defaultdict(list)
        if name == "lme":
            for f in sorted(glob.glob(H.LME_GLOB)):
                d = pickle.loads(open(f, "rb").read())
                bench_archive(d["C"], [np.asarray(d["qC"], float).reshape(-1)],
                              [np.asarray(d["gold"]).ravel().astype(int)],
                              acc, tm)
        elif name == "realtalk":
            excluded = set(json.load(open(H.EXCL_RT))["excluded_ids"])
            for f in sorted(glob.glob(H.RT_GLOB)):
                o = pickle.loads(open(f, "rb").read())
                qc = np.asarray(o["QC"], float)
                qs, gs = [], []
                for qi, qid in enumerate(o["qids"]):
                    gold = [int(x) for x in o["gold_rows"][qi]]
                    if gold and qid not in excluded:
                        qs.append(qc[qi])
                        gs.append(np.asarray(gold))
                if qs:
                    bench_archive(o["C"], qs, gs, acc, tm)
        else:
            arch = pickle.load(open(H.ARCH_PKL, "rb"))
            Q = pickle.load(open(H.Q_PKL, "rb"))
            by = defaultdict(list)
            for qid, v in Q.items():
                by[v["char"]].append(qid)
            for ch in sorted(by):
                ids = sorted(by[ch])
                bench_archive(arch[ch]["C"],
                              [np.asarray(Q[q]["qC"], float) for q in ids],
                              [np.asarray(Q[q]["gold"]).ravel().astype(int)
                               for q in ids], acc, tm)
            del arch, Q

        q = {"sym": float(np.mean(acc[("sym", 0)]) * 100),
             "qscale_full": float(np.mean(acc[("qscale_full", 0)]) * 100)}
        for M in MS:
            q[f"rerank{M}"] = float(np.mean(acc[("rerank", M)]) * 100)
        ms = {k: float(np.mean(v) * 1e6) for k, v in tm.items()
              if k not in ("N", "lut8_ok", "lut4_ok")}
        res["benchmarks"][name] = {
            "n_queries": len(acc[("sym", 0)]),
            "n_archives": len(tm["N"]),
            "mean_N": float(np.mean(tm["N"])),
            "identity_lut8_ok": all(tm["lut8_ok"]),
            "identity_lut4_ok": all(tm["lut4_ok"]),
            "hit10_percent": q, "mean_us": ms}
        v = res["benchmarks"][name]
        print(f"\n=== {name}  n={v['n_queries']}  N~{v['mean_N']:.0f} ===")
        print(f"  LUT kimlikleri: lut8={v['identity_lut8_ok']} "
              f"lut4={v['identity_lut4_ok']}")
        print(f"  {'kol':>14s}{'hit@10':>9s}{'us':>10s}{'sym-e gore':>12s}")
        for k in ["sym", "qscale", "lut8", "lut4"] + [f"rerank{M}" for M in MS]:
            qq = (q.get("qscale_full") if k == "qscale"
                  else q.get(k, q.get("sym") if k in ("lut8", "lut4") else None))
            qs_ = f"{qq:9.2f}" if qq is not None else f"{'-':>9s}"
            print(f"  {k:>14s}{qs_}{ms[k]:10.2f}{ms[k]/ms['sym']:11.2f}x")
        print(flush=True)

    with open(os.path.join(HERE, "QSCALE_FAST.json"), "w") as fh:
        json.dump(res, fh, indent=2)
    print("wrote QSCALE_FAST.json")


if __name__ == "__main__":
    main()
