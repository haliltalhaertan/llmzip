#!/usr/bin/env python3
"""Whole-benchmark storage / RAM / CPU accounting for all three corpora.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

`run_cost.py` timed ONE archive per corpus plus a synthetic scale-up.  This
does every archive of every benchmark and totals it, so the numbers describe
the actual workload rather than a sample of it.

Reported separately, never combined into one "compression ratio":

  STORAGE   bytes resident to hold one archive's index
  SCORE     CPU to score one query against a whole archive
  BUILD     the TF-IDF + SVD fit that produces the vectors (measured on
            LongMemEval, extrapolated per archive; identical for every arm)

Arms:
  float96      96 float64 per doc, centered cosine  (the reference)
  sign_naive   Hamming exactly as lib_b8 does it today -- compares against
               the FLOAT matrix, so it gets NO byte or speed benefit
  sign_packed  the 12-byte payload, XOR + popcount   (what the budget claims)
  sign80_pkt   10-byte payload, the deletion point that was free on LME
  dot_pm1      +-1 reconstruction against the float query (asymmetric)

Totals only; bytes-per-vector is never printed, because that is the quantity
that silently improves when the vector count is inflated.
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

POP8 = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)
HAS_BC = hasattr(np, "bitwise_count")
BUILD_SECONDS_PER_ARCHIVE = 4.85     # measured on LongMemEval, run_cost.py
ARMS = ["float96", "sign_naive", "sign_packed", "sign80_pkt", "dot_pm1"]


def popc(a):
    return np.bitwise_count(a) if HAS_BC else POP8[a]


def med_time(fn, reps=25):
    for _ in range(3):
        fn()
    ts = []
    for _ in range(reps):
        t = time.perf_counter()
        fn()
        ts.append(time.perf_counter() - t)
    return float(np.median(ts))


def one_archive(C, QC):
    C = np.ascontiguousarray(np.asarray(C, dtype=np.float64))
    QC = np.atleast_2d(np.asarray(QC, dtype=np.float64))
    q = np.ascontiguousarray(QC[0])
    N = C.shape[0]
    packed = np.packbits(C >= 0, axis=1, bitorder="big").astype(np.uint8)
    qpack = np.packbits((q >= 0)[None, :], axis=1,
                        bitorder="big").astype(np.uint8)[0]
    # 80-bit deletion point: keep the 80 highest-variance coordinates
    order = np.lexsort((np.arange(96), -np.var(C, axis=0, ddof=0)))
    keep = np.sort(order[:80])
    p80 = np.packbits(C[:, keep] >= 0, axis=1,
                      bitorder="big").astype(np.uint8)
    q80 = np.packbits((q[keep] >= 0)[None, :], axis=1,
                      bitorder="big").astype(np.uint8)[0]
    S = np.where(C >= 0, 1.0, -1.0)
    cn = np.linalg.norm(C, axis=1)
    ram = {"float96": int(C.nbytes + cn.nbytes),
           "sign_naive": int(C.nbytes),
           "sign_packed": int(packed.nbytes),
           "sign80_pkt": int(p80.nbytes),
           "dot_pm1": int(S.nbytes)}
    t = {
        "float96": med_time(lambda: (C @ q) / cn),
        "sign_naive": med_time(
            lambda: -np.count_nonzero((C >= 0) != (q >= 0)[None, :], axis=1)),
        "sign_packed": med_time(
            lambda: -(popc(np.bitwise_xor(packed, qpack[None, :]))
                      .sum(axis=1).astype(np.int64))),
        "sign80_pkt": med_time(
            lambda: -(popc(np.bitwise_xor(p80, q80[None, :]))
                      .sum(axis=1).astype(np.int64))),
        "dot_pm1": med_time(lambda: S @ q),
    }
    # correctness: packed Hamming must equal the frozen scorer
    ok = np.array_equal(
        -(popc(np.bitwise_xor(packed, qpack[None, :]))
          .sum(axis=1).astype(np.int64)),
        -np.count_nonzero((C >= 0) != (q >= 0)[None, :], axis=1))
    return N, ram, t, bool(ok)


def run(name, it, n_queries):
    ramsum = defaultdict(int)
    tsum = defaultdict(float)
    n_arch = 0
    ok_all = True
    for C, QC in it:
        N, ram, t, ok = one_archive(C, QC)
        ok_all &= ok
        n_arch += 1
        for a in ARMS:
            ramsum[a] += ram[a]
            tsum[a] += t[a]          # seconds per ONE query on this archive
    return {"n_archives": n_arch, "n_queries": n_queries,
            "packed_matches_frozen": ok_all,
            "total_index_bytes": {a: int(ramsum[a]) for a in ARMS},
            "mean_score_ms_per_query": {
                a: float(tsum[a] / n_arch * 1e3) for a in ARMS},
            "build_seconds_total": n_arch * BUILD_SECONDS_PER_ARCHIVE}


def it_perltqa():
    arch = pickle.load(open(H.ARCH_PKL, "rb"))
    Q = pickle.load(open(H.Q_PKL, "rb"))
    by = defaultdict(list)
    for qid, v in Q.items():
        by[v["char"]].append(qid)
    for ch in sorted(by):
        yield (np.asarray(arch[ch]["C"], float),
               np.stack([np.asarray(Q[q]["qC"], float) for q in by[ch]]))


def it_lme():
    for f in sorted(glob.glob(H.LME_GLOB)):
        d = pickle.loads(open(f, "rb").read())
        yield np.asarray(d["C"], float), np.asarray(d["qC"], float).reshape(1, -1)


def it_rt():
    for f in sorted(glob.glob(H.RT_GLOB)):
        o = pickle.loads(open(f, "rb").read())
        yield np.asarray(o["C"], float), np.asarray(o["QC"], float)


def main():
    res = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "numpy": np.__version__, "native_popcount": HAS_BC,
           "build_seconds_per_archive": BUILD_SECONDS_PER_ARCHIVE,
           "build_note": "measured on LongMemEval (TF-IDF 1.04 + SVD96 3.81); "
                         "identical for every arm; the frozen protocol refits "
                         "it per question",
           "benchmarks": {}}
    for name, it, nq in (("perltqa", it_perltqa, 8265),
                         ("lme", it_lme, 470),
                         ("realtalk", it_rt, 705)):
        print(f"=== {name} ===", flush=True)
        res["benchmarks"][name] = run(name, it(), nq)
        b = res["benchmarks"][name]
        print(f"  arşiv={b['n_archives']} sorgu={b['n_queries']} "
              f"eşleşme={b['packed_matches_frozen']}", flush=True)
        for a in ARMS:
            print(f"    {a:12s} index {b['total_index_bytes'][a]/1e6:9.2f} MB"
                  f"   score {b['mean_score_ms_per_query'][a]:7.4f} ms/soru",
                  flush=True)
        f = b["total_index_bytes"]["float96"]
        p = b["total_index_bytes"]["sign_packed"]
        tf = b["mean_score_ms_per_query"]["float96"]
        tp = b["mean_score_ms_per_query"]["sign_packed"]
        print(f"    -> packed vs float:  RAM {f/p:.1f}x az   "
              f"CPU {tf/tp:.2f}x   "
              f"| build toplam {b['build_seconds_total']/60:.1f} dk vs "
              f"score toplam {b['mean_score_ms_per_query']['sign_packed']*b['n_queries']/1000:.3f} sn",
              flush=True)
    with open("COSTFULL.json", "w") as fh:
        json.dump(res, fh, indent=2)
    print("\nwrote COSTFULL.json", flush=True)


if __name__ == "__main__":
    main()
