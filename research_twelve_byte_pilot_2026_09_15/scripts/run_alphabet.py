#!/usr/bin/env python3
"""Same 96-bit budget, different alphabet: is binary the constraint?

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

"Binary is tying our hands."  The number BASE is not a constraint -- 96 bits
is 2^96 distinguishable states however you write it.  The real question is
how to SPEND those 96 bits: many coordinates at one bit each, or fewer
coordinates at more levels each?

Budget held fixed at 96 bits per document.  For an alphabet of L levels each
coordinate costs log2(L) bits, so the number of coordinates is
floor(96 / log2(L)):

    L=2    96 coordinates x 1 bit      <- the production code
    L=3    60 coordinates x 1.585      ternary
    L=4    48 coordinates x 2 bits
    L=8    32 coordinates x 3 bits
    L=16   24 coordinates x 4 bits
    L=256  12 coordinates x 8 bits

Coordinates are taken in the frozen variance order, so every arm keeps the
most informative axes it can afford.  Quantisation is by per-coordinate
QUANTILES, which makes the levels equiprobable and so extracts the maximum
entropy the alphabet allows; reconstruction is the conditional MEAN of each
level, which is the MSE-optimal value to put back.  Neither choice favours
binary.

Two scorers, because this session found the query side is where binarisation
actually costs:
    float_query  cosine(float q, reconstruction)   -- query kept exact
    quant_query  cosine(quantised q, reconstruction) -- both sides quantised

A query is ONE vector, never stored in bulk, so keeping it exact costs no
index memory at all.
"""
import glob
import json
import math
import os
import pickle
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_hit10 as H  # noqa: E402

BUDGET_BITS = 96
LEVELS = (2, 3, 4, 8, 16, 256)
KS = (1, 3, 10)


def n_coords(L):
    return int(math.floor(BUDGET_BITS / math.log2(L)))


def quantise(C, L, keep):
    """Per-coordinate quantile bins + conditional-mean reconstruction.

    Returns (recon, edges, centres) so the query can use the same bins.
    """
    X = C[:, keep]
    edges, centres = [], []
    R = np.empty_like(X)
    for j in range(X.shape[1]):
        col = X[:, j]
        qs = np.quantile(col, np.linspace(0, 1, L + 1)[1:-1])
        idx = np.searchsorted(qs, col, side="right")
        cen = np.zeros(L)
        for b in range(L):
            m = idx == b
            cen[b] = col[m].mean() if m.any() else 0.0
        R[:, j] = cen[idx]
        edges.append(qs)
        centres.append(cen)
    return R, edges, centres


def quantise_query(q, keep, edges, centres):
    out = np.empty(len(keep))
    for j, c in enumerate(keep):
        b = int(np.searchsorted(edges[j], q[c], side="right"))
        out[j] = centres[j][b]
    return out


def cos(R, q):
    rn = np.linalg.norm(R, axis=1)
    qn = float(np.linalg.norm(q))
    if qn == 0 or not np.isfinite(qn):
        return np.full(R.shape[0], -np.inf)
    with np.errstate(divide="ignore", invalid="ignore"):
        s = (R @ q) / (rn * qn)
    return np.nan_to_num(s, nan=-np.inf, posinf=-np.inf, neginf=-np.inf)


def one_archive(C, queries, golds, acc):
    C = np.asarray(C, dtype=np.float64)
    var = C.var(axis=0)
    order = np.lexsort((np.arange(C.shape[1]), -var))   # frozen tie rule
    for L in LEVELS:
        m = n_coords(L)
        keep = np.sort(order[:m])
        R, edges, centres = quantise(C, L, keep)
        for j, qv in enumerate(queries):
            q = np.asarray(qv, dtype=np.float64).reshape(-1)
            g = np.asarray(golds[j]).ravel().astype(int)
            for mode, qq in (("float_query", q[keep]),
                             ("quant_query",
                              quantise_query(q, keep, edges, centres))):
                sc = cos(R, qq)
                for k in KS:
                    acc[(L, mode, k)].append(H.hit_at_k(sc, g, k))


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    res = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "budget_bits": BUDGET_BITS,
           "coords_per_alphabet": {str(L): n_coords(L) for L in LEVELS},
           "quantiser": "per-coordinate quantile bins, conditional-mean "
                        "reconstruction (equiprobable levels, MSE-optimal "
                        "centres)",
           "benchmarks": {}}
    jobs = []
    if which in ("all", "lme"):
        jobs.append(("lme", H.run_lme))
    if which in ("all", "perltqa"):
        jobs.append(("perltqa", H.run_perltqa))
    if which in ("all", "realtalk"):
        jobs.append(("realtalk", H.run_realtalk))

    for name, _ in jobs:
        acc = {(L, m, k): [] for L in LEVELS
               for m in ("float_query", "quant_query") for k in KS}
        if name == "lme":
            for f in sorted(glob.glob(H.LME_GLOB)):
                d = pickle.loads(open(f, "rb").read())
                one_archive(
                    d["C"], [np.asarray(d["qC"], float).reshape(-1)],
                    [np.asarray(d["gold"]).ravel().astype(int)], acc)
        elif name == "realtalk":
            # same exclusion list run_hit10.run_realtalk applies
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
                    one_archive(o["C"], qs, gs, acc)
                print(f"  realtalk {os.path.basename(f)} n={len(qs)}",
                      flush=True)
        else:
            arch = pickle.load(open(H.ARCH_PKL, "rb"))
            Q = pickle.load(open(H.Q_PKL, "rb"))
            from collections import defaultdict
            by = defaultdict(list)
            for qid, v in Q.items():
                by[v["char"]].append(qid)
            for ch in sorted(by):
                ids = sorted(by[ch])
                one_archive(
                    arch[ch]["C"],
                    [np.asarray(Q[q]["qC"], float) for q in ids],
                    [np.asarray(Q[q]["gold"]).ravel().astype(int)
                     for q in ids],
                    acc)
                print(f"  perltqa {ch} n={len(ids)}", flush=True)
            del arch, Q
        res["benchmarks"][name] = {
            f"L{L}_{m}_hit{k}": float(np.mean(acc[(L, m, k)]) * 100)
            for L in LEVELS for m in ("float_query", "quant_query") for k in KS}
        b = res["benchmarks"][name]
        print(f"\n=== {name} ===")
        print(f"  {'alfabe':>8s}{'koord':>7s}"
              f"{'hit@10 float-q':>16s}{'hit@10 quant-q':>16s}")
        for L in LEVELS:
            print(f"  {L:>8d}{n_coords(L):>7d}"
                  f"{b[f'L{L}_float_query_hit10']:>16.2f}"
                  f"{b[f'L{L}_quant_query_hit10']:>16.2f}", flush=True)

    with open(os.path.join(HERE, f"ALPHABET_{which}.json"), "w") as fh:
        json.dump(res, fh, indent=2)
    print(f"\nwrote ALPHABET_{which}.json")


if __name__ == "__main__":
    main()
