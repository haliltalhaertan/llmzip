#!/usr/bin/env python3
"""Cluster bootstrap for the qscale gain -- correcting my own repeated error.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

`run_qscale.py` reported the qscale-minus-sym contrast with an i.i.d.
query-level bootstrap.  That is wrong wherever queries share an archive:
PerLTQA has 8,265 queries drawn from 30 archives and RealTalk 705 from 10, so
the effective sample size is the ARCHIVE count, not the query count.  An
independent auditor flagged exactly this error in this session's earlier faiss
work; `run_hit10.bootstrap_ci` has used a cluster bootstrap all along.
Repeating it after being corrected is worse than making it once, so this
recomputes every interval the honest way.

LongMemEval is unaffected in principle -- one query per archive, so query and
cluster coincide -- and is recomputed anyway as a control: its two intervals
should agree.

Both intervals are printed side by side so the size of the error is visible
rather than quietly fixed.
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

B_REPS = 20000
SEED = 20260916
K = 10
CONTRASTS = [("qscale", "sym"), ("qscale", "float_std"), ("asym", "sym")]


def arm_scores(C, st, R, packed, q):
    qb = (np.asarray(q, dtype=np.float64) >= 0)
    sym = (-np.count_nonzero(
        np.unpackbits(packed, axis=1, bitorder="big")[:, :96].astype(bool)
        != qb[None, :], axis=1)).astype(np.float64)
    std = np.asarray(st["std"], dtype=np.float64)
    qs = np.asarray(q, dtype=np.float64).reshape(-1) / std
    return {"sym": sym, "asym": B.cosine_from_code(R, q),
            "qscale": R @ qs,
            "float_std": B.float_std_scores(C, q, st["std"])}


def collect(name):
    hits = defaultdict(list)
    cluster = []

    def do(C, queries, golds, tag):
        C = np.asarray(C, dtype=np.float64)
        st = B.fit_archive(C)
        packed = np.packbits((C >= 0), axis=1, bitorder="big").astype(np.uint8)
        R = np.where(np.unpackbits(packed, axis=1,
                                   bitorder="big")[:, :96].astype(bool),
                     1.0, -1.0)
        for j, qv in enumerate(queries):
            q = np.asarray(qv, dtype=np.float64).reshape(-1)
            g = np.asarray(golds[j]).ravel().astype(int)
            sc = arm_scores(C, st, R, packed, q)
            for a, s in sc.items():
                hits[a].append(H.hit_at_k(s, g, K))
            cluster.append(tag)

    if name == "lme":
        for f in sorted(glob.glob(H.LME_GLOB)):
            d = pickle.loads(open(f, "rb").read())
            do(d["C"], [np.asarray(d["qC"], float).reshape(-1)],
               [np.asarray(d["gold"]).ravel().astype(int)],
               os.path.basename(f))
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
                do(o["C"], qs, gs, os.path.basename(f))
    else:
        arch = pickle.load(open(H.ARCH_PKL, "rb"))
        Q = pickle.load(open(H.Q_PKL, "rb"))
        by = defaultdict(list)
        for qid, v in Q.items():
            by[v["char"]].append(qid)
        for ch in sorted(by):
            ids = sorted(by[ch])
            do(arch[ch]["C"], [np.asarray(Q[q]["qC"], float) for q in ids],
               [np.asarray(Q[q]["gold"]).ravel().astype(int) for q in ids], ch)
        del arch, Q
    return {a: np.asarray(v, float) for a, v in hits.items()}, np.asarray(cluster)


def boot_query(d, rng):
    n = len(d)
    return d[rng.integers(0, n, size=(B_REPS, n))].mean(axis=1) * 100


def boot_cluster(d, cluster, rng):
    keys = np.unique(cluster)
    groups = [np.nonzero(cluster == k)[0] for k in keys]
    sums = np.array([d[g].sum() for g in groups])
    cnts = np.array([len(g) for g in groups], dtype=float)
    idx = rng.integers(0, len(keys), size=(B_REPS, len(keys)))
    return (sums[idx].sum(axis=1) / cnts[idx].sum(axis=1)) * 100


def main():
    out = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "k": K, "bootstrap": B_REPS,
           "why": ("run_qscale.py used a query-level bootstrap where queries "
                   "share archives; the cluster bootstrap over archives is "
                   "the correct one and is what run_hit10.py has always used"),
           "benchmarks": {}}
    rng = np.random.default_rng(SEED)
    for name in ("perltqa", "lme", "realtalk"):
        hits, cluster = collect(name)
        nq, nc = len(cluster), len(np.unique(cluster))
        rec = {"n_queries": nq, "n_archives": nc,
               "levels_pct": {a: float(v.mean() * 100) for a, v in hits.items()},
               "contrasts": {}}
        print(f"\n=== {name}  {nq} sorgu / {nc} arsiv ===")
        print(f"  {'kontrast':>22s}{'fark':>9s}{'SORGU bootstrap':>22s}"
              f"{'KUME bootstrap':>22s}{'anlamli':>9s}")
        for a, b in CONTRASTS:
            d = hits[a] - hits[b]
            bq, bc = boot_query(d, rng), boot_cluster(d, cluster, rng)
            qlo, qhi = np.percentile(bq, [2.5, 97.5])
            clo, chi = np.percentile(bc, [2.5, 97.5])
            sig = "EVET" if (clo > 0 or chi < 0) else "hayir"
            rec["contrasts"][f"{a}-{b}"] = {
                "delta_pp": float(d.mean() * 100),
                "ci95_query_level_WRONG_when_clustered": [float(qlo), float(qhi)],
                "ci95_cluster_level": [float(clo), float(chi)],
                "significant_cluster": sig == "EVET",
                "width_ratio_cluster_over_query": float(
                    (chi - clo) / (qhi - qlo)) if qhi > qlo else None}
            print(f"  {a+' - '+b:>22s}{d.mean()*100:+9.2f}"
                  f"{f'[{qlo:+.2f}, {qhi:+.2f}]':>22s}"
                  f"{f'[{clo:+.2f}, {chi:+.2f}]':>22s}{sig:>9s}")
        out["benchmarks"][name] = rec

    with open(os.path.join(HERE, "QSCALE_CI.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print("\nwrote QSCALE_CI.json")


if __name__ == "__main__":
    main()
