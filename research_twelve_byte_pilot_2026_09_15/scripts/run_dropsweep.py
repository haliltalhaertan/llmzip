#!/usr/bin/env python3
"""How many of the 96 sign bits can be DELETED before retrieval degrades?

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

Compression of the 12-byte payload is dead (measured: 95.7 of 96 bits are
real information, best lossless gain 11% on one benchmark and negative on
another).  Deletion is the remaining lever, and it already worked once:
dropping the 8 lowest-variance coordinates (sign88, 11 bytes) cost nothing
measurable on any of the three benchmarks.

This sweeps the retained-coordinate budget with the FROZEN selection rule
(`lib_b8.select_axes`: descending population variance, ties -> lower index),
so b=88 must reproduce the already-measured sign88 arm and b=96 must
reproduce the production `sym` arm.  Those two are the fidelity checks.

Two scorers, because they are genuinely different objects and this session
already showed they disagree by benchmark:

  hamming   -#mismatches over retained sign bits        (query signs only)
  dot       sum over retained of sign(doc_j) * query_j  (float query;
            rank-identical to lib_b8's cosine-from-code, whose norm is the
            constant sqrt(b))

Ties use the same uniform-random-within-bucket convention as lib_b8.
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
import run_ksweep as KS  # noqa: E402

BUDGETS = [96, 88, 80, 72, 64, 56, 48, 40, 32, 24, 16]
SCORERS = ["hamming", "dot"]
KS_REPORT = (1, 3, 10)


def archive_scores(C, QC):
    """-> {(scorer, b): [N, nq] score matrix}, frozen variance ordering."""
    C = np.asarray(C, dtype=np.float64)
    QC = np.atleast_2d(np.asarray(QC, dtype=np.float64))
    order, _ = KS.H.B.select_axes(C)          # frozen rule, lib_b8
    Co = C[:, order]
    Qo = QC[:, order]
    D = (Co >= 0)
    Qs = (Qo >= 0)
    S = np.where(D, 1.0, -1.0)
    out = {}
    for b in BUDGETS:
        Db = D[:, :b].astype(np.float64)
        Qb = Qs[:, :b].astype(np.float64)
        agree = Db @ Qb.T + (1.0 - Db) @ (1.0 - Qb).T
        out[("hamming", b)] = agree - b            # = -mismatches
        out[("dot", b)] = S[:, :b] @ Qo[:, :b].T
    return out


def main():
    res = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "selection_rule": "lib_b8.select_axes, descending population "
                             "variance, ties -> lower coordinate index",
           "fidelity": "hamming@96 == production sym; dot@88 == sign88",
           "budgets_bits": BUDGETS,
           "bytes": {str(b): int(np.ceil(b / 8)) for b in BUDGETS},
           "scorers": SCORERS, "benchmarks": {}}

    def run(name, iterator):
        facts = {(s, b): [] for s in SCORERS for b in BUDGETS}
        pools = []
        for C, QC, golds in iterator:
            sc = archive_scores(C, QC)
            for j, g in enumerate(golds):
                g = np.asarray(g).ravel().astype(int)
                pools.append(C.shape[0])
                for s in SCORERS:
                    for b in BUDGETS:
                        facts[(s, b)].append(
                            KS.bucket_facts(sc[(s, b)][:, j], g))
        out = {"n": len(pools), "pool_mean": float(np.mean(pools)),
               "hit_percent": {}, "k90": {}}
        for s in SCORERS:
            out["hit_percent"][s] = {}
            out["k90"][s] = {}
            for b in BUDGETS:
                ff = facts[(s, b)]
                out["hit_percent"][s][str(b)] = {
                    str(k): float(np.mean([KS.hit_from_facts(*f, k)
                                           for f in ff]) * 100.0)
                    for k in KS_REPORT}
                kmax = int(max(pools))
                lo, hi = 1, kmax
                if np.mean([KS.hit_from_facts(*f, kmax) for f in ff]) < 0.90:
                    out["k90"][s][str(b)] = None
                else:
                    while lo < hi:
                        mid = (lo + hi) // 2
                        if np.mean([KS.hit_from_facts(*f, mid)
                                    for f in ff]) >= 0.90:
                            hi = mid
                        else:
                            lo = mid + 1
                    out["k90"][s][str(b)] = int(lo)
        # paired deltas vs the 96-bit production point, same scorer
        out["delta_vs_96_pp"] = {}
        for s in SCORERS:
            base = facts[(s, 96)]
            out["delta_vs_96_pp"][s] = {}
            for b in BUDGETS:
                d = np.array([KS.hit_from_facts(*f, 10)
                              - KS.hit_from_facts(*bf, 10)
                              for f, bf in zip(facts[(s, b)], base)])
                se = d.std(ddof=1) / np.sqrt(len(d)) if len(d) > 1 else 0.0
                out["delta_vs_96_pp"][s][str(b)] = {
                    "point": float(d.mean() * 100.0),
                    "ci95": [float((d.mean() - 1.96 * se) * 100.0),
                             float((d.mean() + 1.96 * se) * 100.0)]}
        return out

    def it_perltqa():
        arch = pickle.load(open(H.ARCH_PKL, "rb"))
        Q = pickle.load(open(H.Q_PKL, "rb"))
        by = defaultdict(list)
        for qid, q in Q.items():
            by[q["char"]].append(qid)
        for char in sorted(by):
            ql = sorted(by[char])
            yield (np.asarray(arch[char]["C"], dtype=np.float64),
                   np.stack([np.asarray(Q[q]["qC"], dtype=np.float64)
                             for q in ql]),
                   [np.asarray(Q[q]["gold"]).ravel().astype(int) for q in ql])

    def it_lme():
        for f in sorted(glob.glob(H.LME_GLOB)):
            d = pickle.loads(open(f, "rb").read())
            yield (np.asarray(d["C"], float),
                   np.asarray(d["qC"], float).reshape(1, -1),
                   [np.asarray(d["gold"]).ravel().astype(int)])

    def it_rt():
        excl = set(json.load(open(H.EXCL_RT))["excluded_ids"])
        for f in sorted(glob.glob(H.RT_GLOB)):
            o = pickle.loads(open(f, "rb").read())
            QC = np.asarray(o["QC"], float)
            qs, gs = [], []
            for qi, qid in enumerate(o["qids"]):
                gold = [int(x) for x in o["gold_rows"][qi]]
                if not gold or qid in excl:
                    continue
                qs.append(QC[qi])
                gs.append(np.asarray(gold))
            if qs:
                yield np.asarray(o["C"], float), np.stack(qs), gs

    for name, it in (("perltqa", it_perltqa), ("lme", it_lme),
                     ("realtalk", it_rt)):
        print(f"=== {name} ===", flush=True)
        res["benchmarks"][name] = run(name, it())
        hp = res["benchmarks"][name]["hit_percent"]
        for s in SCORERS:
            print("  " + s.ljust(8) + "  ".join(
                f"{b}b:{hp[s][str(b)]['10']:.1f}" for b in BUDGETS),
                flush=True)
    with open("DROPSWEEP.json", "w") as f:
        json.dump(res, f, indent=2)
    print("wrote DROPSWEEP.json", flush=True)


if __name__ == "__main__":
    main()
