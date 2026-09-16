#!/usr/bin/env python3
"""Same stored bits, a better query: does per-coordinate scaling of the query help?

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

An external reviewer reports that keeping the query numeric AND balancing its
per-coordinate scales lifts retrieval on all three benchmarks, without
touching a single stored document bit: LME 86.08 -> 88.51, PerLTQA 75.76 ->
80.00, RealTalk 46.68 -> 49.65.  That is a strong claim -- 12 bytes per
document unchanged, only the query side and the scorer move -- so it is
measured here rather than accepted.

The document side is FROZEN throughout: `sign(C)` packed, exactly what
production stores.  Only the query representation changes:

  sym         query binarised too, Hamming            production baseline
  asym        float query, cosine vs +-1 code         lib_b8.cosine_from_code
  qscale      float query divided by the per-coordinate std, cosine vs +-1
  qscale_dot  same, without the cosine denominators   (ranking check)

The extra state is one float array of 96 per archive -- `st["std"]`, which
`lib_b8.fit_archive` already computes for the `float_std` arm, so nothing new
has to be fitted.  It is NOT free: it must be counted, and the count is
reported below.

Why this could work at all: L2 row normalisation makes every DOCUMENT unit
length; it says nothing about the spread of any one COORDINATE across
documents.  A value of 0.10 can be ordinary on one axis and extreme on
another, and the sign code discards exactly that distinction.  The document
cannot carry it back -- one bit is one bit -- but the query can weight each
axis by how much that axis actually varies.
"""
import glob
import json
import os
import pickle
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_hit10 as H  # noqa: E402
sys.path.insert(0, os.path.join(H.SRC, "parallel_ideas_r1", "b8"))
import lib_b8 as B  # noqa: E402

ARMS = ["sym", "asym", "qscale", "qscale_dot", "float_std"]
KS = (1, 3, 10)


def arm_scores(C, st, R, packed, q):
    qb = (np.asarray(q, dtype=np.float64) >= 0)
    sym = (-np.count_nonzero(
        np.unpackbits(packed, axis=1, bitorder="big")[:, :96].astype(bool)
        != qb[None, :], axis=1)).astype(np.float64)
    std = np.asarray(st["std"], dtype=np.float64)
    qs = np.asarray(q, dtype=np.float64).reshape(-1) / std
    rn = np.linalg.norm(R, axis=1)
    qn = float(np.linalg.norm(qs))
    with np.errstate(divide="ignore", invalid="ignore"):
        qscale = (R @ qs) / (rn * qn) if qn > 0 else np.full(R.shape[0], -np.inf)
    return {
        "sym": sym,
        "asym": B.cosine_from_code(R, q),
        "qscale": np.nan_to_num(qscale, nan=-np.inf, posinf=-np.inf,
                                neginf=-np.inf),
        "qscale_dot": R @ qs,
        "float_std": B.float_std_scores(C, q, st["std"]),
    }


def score_archive(C, queries, golds, acc, bytes_acc):
    C = np.asarray(C, dtype=np.float64)
    n = C.shape[0]
    st = B.fit_archive(C)
    packed = np.packbits((C >= 0), axis=1, bitorder="big").astype(np.uint8)
    assert packed.shape == (n, 12)
    R = np.where(np.unpackbits(packed, axis=1,
                               bitorder="big")[:, :96].astype(bool), 1.0, -1.0)
    bytes_acc["doc_bits"] += int(packed.nbytes)
    bytes_acc["std_array"] += int(np.asarray(st["std"],
                                             dtype=np.float32).nbytes)
    bytes_acc["float64_docs"] += int(C.nbytes)
    for j, qv in enumerate(queries):
        q = np.asarray(qv, dtype=np.float64).reshape(-1)
        g = np.asarray(golds[j]).ravel().astype(int)
        sc = arm_scores(C, st, R, packed, q)
        # frozen self-check: sym must reproduce lib_b8's own sym path at k=3
        ref = B.exact_frac(sc["sym"], g, True)
        mine = H.frac_at_k(sc["sym"], g, 3)
        if abs(ref - mine) > 1e-12:
            raise AssertionError("sym self-check failed")
        for a in ARMS:
            for k in KS:
                acc[(a, k)].append(H.hit_at_k(sc[a], g, k))


def main():
    res = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "document_side": "UNCHANGED -- packed sign(C), 12 B/doc",
           "extra_state": "one float32 array of 96 per archive (st['std']), "
                          "already fitted by lib_b8 for the float_std arm",
           "benchmarks": {}}
    for name in ("perltqa", "lme", "realtalk"):
        acc = {(a, k): [] for a in ARMS for k in KS}
        ba = defaultdict(int)
        if name == "lme":
            for f in sorted(glob.glob(H.LME_GLOB)):
                d = pickle.loads(open(f, "rb").read())
                score_archive(d["C"], [np.asarray(d["qC"], float).reshape(-1)],
                              [np.asarray(d["gold"]).ravel().astype(int)],
                              acc, ba)
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
                    score_archive(o["C"], qs, gs, acc, ba)
        else:
            arch = pickle.load(open(H.ARCH_PKL, "rb"))
            Q = pickle.load(open(H.Q_PKL, "rb"))
            by = defaultdict(list)
            for qid, v in Q.items():
                by[v["char"]].append(qid)
            for ch in sorted(by):
                ids = sorted(by[ch])
                score_archive(arch[ch]["C"],
                              [np.asarray(Q[q]["qC"], float) for q in ids],
                              [np.asarray(Q[q]["gold"]).ravel().astype(int)
                               for q in ids], acc, ba)
            del arch, Q
        n = len(acc[("sym", 10)])
        res["benchmarks"][name] = {
            "n_queries": n,
            "hit_percent": {f"{a}_hit{k}": float(np.mean(acc[(a, k)]) * 100)
                            for a in ARMS for k in KS},
            "index_bytes": dict(ba),
            "std_overhead_pct_of_doc_bits": float(
                ba["std_array"] / ba["doc_bits"] * 100)}
        # paired CI for the headline contrast
        d = (np.asarray(acc[("qscale", 10)]) - np.asarray(acc[("sym", 10)]))
        rng = np.random.default_rng(20260916)
        boot = d[rng.integers(0, n, size=(20000, n))].mean(axis=1) * 100
        res["benchmarks"][name]["qscale_minus_sym_hit10"] = {
            "delta_pp": float(d.mean() * 100),
            "ci95": [float(np.percentile(boot, 2.5)),
                     float(np.percentile(boot, 97.5))],
            "queries_up": int(np.count_nonzero(d > 0)),
            "queries_down": int(np.count_nonzero(d < 0))}
        v = res["benchmarks"][name]
        c = v["qscale_minus_sym_hit10"]
        print(f"\n=== {name}  n={n} ===")
        print(f"  {'kol':>12s}{'hit@1':>9s}{'hit@3':>9s}{'hit@10':>9s}")
        for a in ARMS:
            print(f"  {a:>12s}" + "".join(
                f"{v['hit_percent'][f'{a}_hit{k}']:9.2f}" for k in KS))
        sig = "ANLAMLI" if (c["ci95"][0] > 0 or c["ci95"][1] < 0) else "ns"
        print(f"  qscale - sym : {c['delta_pp']:+.2f} pp  "
              f"[{c['ci95'][0]:+.2f}, {c['ci95'][1]:+.2f}]  {sig}   "
              f"(yukari {c['queries_up']}, asagi {c['queries_down']})")
        print(f"  std dizisi maliyeti: "
              f"{v['std_overhead_pct_of_doc_bits']:.1f}% of doc bits "
              f"({ba['std_array']/1e6:.3f} MB / {ba['doc_bits']/1e6:.3f} MB)",
              flush=True)

    with open(os.path.join(HERE, "QSCALE.json"), "w") as fh:
        json.dump(res, fh, indent=2)
    print("\nwrote QSCALE.json")


if __name__ == "__main__":
    main()
