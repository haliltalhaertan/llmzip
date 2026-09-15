#!/usr/bin/env python3
"""Full hit@k curve for the frozen r1 arms: how many candidates buy 90/95%?

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

Same re-read as run_hit10.py -- encoding and all six scoring functions are
imported unchanged from the frozen lib_b8.  Only the metric reduction is new.

Per query and arm we store four integers that determine hit@k for EVERY k:

  lo   docs ranked strictly above the first tied bucket that contains a gold
  hi   docs ranked at or above that bucket        (hi = lo + bsz)
  gb   golds inside that bucket
  bsz  size of that bucket

    hit@k = 0                                    k <= lo
          = 1 - C(bsz-gb, k-lo) / C(bsz, k-lo)   lo < k < hi
          = 1                                    k >= hi

which is the same uniform-random-within-tie convention lib_b8.exact_frac uses.
Self-check: the curve is re-evaluated at k in {1,3,5,10,20} and must match
run_hit10.py's independently computed hit_at_k to 1e-12.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_hit10 as H  # noqa: E402  (loaders + frozen arm wiring)

ARMS = H.ARMS
CHECK_KS = (1, 3, 5, 10, 20)
TARGETS = (0.80, 0.90, 0.95, 0.99)


def bucket_facts(scores, gold):
    """(lo, hi, gb, bsz) for the first tied bucket containing a gold doc."""
    s = np.asarray(scores, dtype=np.float64)
    s = np.where(np.isfinite(s), s, -np.inf)
    g = np.asarray(gold).ravel().astype(int)
    order_key = -s
    levels, counts = np.unique(order_key, return_counts=True)  # ascending -s
    cum = np.cumsum(counts)
    # bucket index of every gold doc
    gb_idx = np.searchsorted(levels, order_key[g])
    b = int(gb_idx.min())
    lo = int(cum[b - 1]) if b > 0 else 0
    hi = int(cum[b])
    bsz = hi - lo
    gb = int(np.count_nonzero(gb_idx == b))
    return lo, hi, gb, bsz


def hit_from_facts(lo, hi, gb, bsz, k):
    if k <= lo:
        return 0.0
    if k >= hi:
        return 1.0
    take = k - lo
    if take > bsz - gb:
        return 1.0
    return 1.0 - math.comb(bsz - gb, take) / math.comb(bsz, take)


def collect(bench_rows_fn):
    """bench_rows_fn yields (C, queries, golds) archive tuples."""
    facts = {a: [] for a in ARMS}
    pool_n = []
    for C, queries, golds in bench_rows_fn():
        C = np.asarray(C, dtype=np.float64)
        n = C.shape[0]
        st = H.B.fit_archive(C)
        p_b8 = H.B.encode_docs(C, st)
        p_s96 = np.packbits((C >= 0), axis=1, bitorder="big").astype(np.uint8)
        s96 = np.where(np.unpackbits(p_s96, axis=1,
                                     bitorder="big")[:, :96].astype(bool),
                       1.0, -1.0)
        for j, qv in enumerate(queries):
            q = np.asarray(qv, dtype=np.float64).reshape(-1)
            g = np.asarray(golds[j]).ravel().astype(int)
            sc = H.arm_scores(C, st, p_b8, p_s96, s96, q)
            pool_n.append(n)
            for a in ARMS:
                f = bucket_facts(sc[a], g)
                # self-check against the independent implementation
                for k in CHECK_KS:
                    ref = H.hit_at_k(sc[a], g, k)
                    mine = hit_from_facts(*f, k)
                    if abs(ref - mine) > 1e-12:
                        raise AssertionError(
                            f"curve != hit_at_k arm={a} k={k}: {mine} {ref}")
                facts[a].append(f)
    return facts, np.asarray(pool_n)


def curve(facts_arm, ks):
    out = np.empty(len(ks))
    for i, k in enumerate(ks):
        out[i] = np.mean([hit_from_facts(lo, hi, gb, bsz, k)
                          for (lo, hi, gb, bsz) in facts_arm])
    return out


def k_for(facts_arm, target, kmax):
    lo, hi = 1, int(kmax)
    if np.mean([hit_from_facts(*f, hi) for f in facts_arm]) < target:
        return None
    while lo < hi:
        mid = (lo + hi) // 2
        if np.mean([hit_from_facts(*f, mid) for f in facts_arm]) >= target:
            hi = mid
        else:
            lo = mid + 1
    return int(lo)


def perltqa_iter():
    import pickle
    from collections import defaultdict
    arch = pickle.load(open(H.ARCH_PKL, "rb"))
    q_all = pickle.load(open(H.Q_PKL, "rb"))
    by_char = defaultdict(list)
    for qid, q in q_all.items():
        by_char[q["char"]].append(qid)
    for char in sorted(by_char):
        ql = sorted(by_char[char])
        yield (np.asarray(arch[char]["C"], dtype=np.float64),
               [np.asarray(q_all[q]["qC"], dtype=np.float64) for q in ql],
               [np.asarray(q_all[q]["gold"]).ravel().astype(int) for q in ql])


def lme_iter():
    import glob
    import pickle
    for f in sorted(glob.glob(H.LME_GLOB)):
        d = pickle.loads(open(f, "rb").read())
        yield (np.asarray(d["C"], float),
               [np.asarray(d["qC"], float).reshape(-1)],
               [np.asarray(d["gold"]).ravel().astype(int)])


def realtalk_iter():
    import glob
    import pickle
    excluded = set(json.load(open(H.EXCL_RT))["excluded_ids"])
    for f in sorted(glob.glob(H.RT_GLOB)):
        o = pickle.loads(open(f, "rb").read())
        qc_all = np.asarray(o["QC"], float)
        qs, gs = [], []
        for qi, qid in enumerate(o["qids"]):
            gold = [int(x) for x in o["gold_rows"][qi]]
            if not gold or qid in excluded:
                continue
            qs.append(qc_all[qi])
            gs.append(np.asarray(gold))
        if qs:
            yield np.asarray(o["C"], float), qs, gs


def main():
    summary = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                          "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
               "what_this_is": "full hit@k curve over the frozen r1 arms",
               "self_check": "curve == run_hit10.hit_at_k at k in "
                             + str(CHECK_KS),
               "targets": list(TARGETS), "benchmarks": {}}
    for name, it in (("perltqa", perltqa_iter), ("lme", lme_iter),
                     ("realtalk", realtalk_iter)):
        print(f"=== {name} ===", flush=True)
        facts, pool_n = collect(it)
        kmax = int(pool_n.max())
        ks = sorted(set([1, 2, 3, 5, 10, 20, 30, 50, 75, 100, 150, 200, 300,
                         400, 500, 750, 1000] + [kmax]))
        ks = [k for k in ks if k <= kmax]
        b = {"n": len(pool_n), "pool_mean": float(pool_n.mean()),
             "pool_median": float(np.median(pool_n)),
             "pool_max": kmax, "ks": ks, "hit_curve_percent": {},
             "k_needed": {}, "k_needed_as_pool_fraction": {}}
        for a in ARMS:
            b["hit_curve_percent"][a] = [float(x * 100.0)
                                         for x in curve(facts[a], ks)]
            b["k_needed"][a] = {}
            b["k_needed_as_pool_fraction"][a] = {}
            for t in TARGETS:
                kk = k_for(facts[a], t, kmax)
                b["k_needed"][a][str(t)] = kk
                b["k_needed_as_pool_fraction"][a][str(t)] = (
                    None if kk is None else float(kk) / float(pool_n.mean()))
            print(f"  {a:10s} k@90%={b['k_needed'][a]['0.9']} "
                  f"k@95%={b['k_needed'][a]['0.95']} "
                  f"k@99%={b['k_needed'][a]['0.99']} "
                  f"(pool mean {pool_n.mean():.0f})", flush=True)
        summary["benchmarks"][name] = b
    with open("KSWEEP.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("wrote KSWEEP.json", flush=True)


if __name__ == "__main__":
    main()
