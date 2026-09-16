#!/usr/bin/env python3
"""Explaining the LoCoMo ANCHOR_MISMATCH: different metric, or different gold?

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

`LOCOMO.json` flagged that our frac@3 for `sym` is 23.7907 against the
historical gate's 23.6547 on what looked like an identical query set
(1,540 / 1,535 valid / 5 excluded / 10 archives).  Two candidate causes:

  A. the metric implementations differ
  B. the gold sets differ

`theory_benchmark_test_v1/locomo/run_locomo.py:189` settles B:

    ag = Q[qid]["ag"]        # "ag" = correct_evidence, the AUDITED gold

whereas our caches carry `raw_evidence` only.  Those are the 156 audit
corrections that are an open Head-Researcher obligation.

This script rules A out directly by porting the historical `exact_exp`
verbatim and running BOTH metrics over the SAME scores and the SAME (raw)
gold.  `exact_exp` averages P(gold_i in top k) over gold items;
`lib_b8.exact_frac` takes the expected fraction of gold retrieved.  By
linearity of expectation these should be identical -- if they are, the metric
is not the explanation and the gold convention is the whole story.
"""
import glob
import json
import os
import pickle
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_hit10 as H  # noqa: E402
sys.path.insert(0, os.path.join(H.SRC, "parallel_ideas_r1", "b8"))
import lib_b8 as B  # noqa: E402

TOPK = 3


def exact_exp(dvec, gold, k=TOPK):
    """VERBATIM from theory_benchmark_test_v1/locomo/run_locomo.py:75-90."""
    d = np.asarray(dvec)
    tot = 0.0
    for gg in np.asarray(gold).ravel():
        dg = d[int(gg)]
        s = int(np.count_nonzero(d < dg))
        t = int(np.count_nonzero(d == dg))
        if s >= k:
            p = 0.0
        elif s + t <= k:
            p = 1.0
        else:
            p = (k - s) / t
        tot += p
    return tot / len(np.asarray(gold).ravel())


def main():
    files = sorted(glob.glob(os.path.join(H.SRC, "regen", "locomo",
                                          "locomo_*.pkl")))
    assert len(files) == 10, len(files)
    hist, ours, worst = [], [], 0.0
    nq = 0
    for f in files:
        d = pickle.load(open(f, "rb"))
        C = np.asarray(d["C"], dtype=np.float64)
        QC = np.asarray(d["QC"], dtype=np.float64)
        i2r = d["id_to_row"]
        Cb = C >= 0
        for j, qa in enumerate(d["qas"]):
            rows = sorted({int(i2r[x]) for x in qa["raw_evidence"]
                           if x in i2r})
            if not rows:
                continue
            g = np.asarray(rows, dtype=int)
            qb = QC[j] >= 0
            # historical works on DISTANCE, lib_b8 on SCORE = -distance
            dist = np.count_nonzero(Cb != qb[None, :], axis=1)
            a = exact_exp(dist, g)
            b = B.exact_frac((-dist).astype(np.float64), g, True)
            hist.append(a)
            ours.append(b)
            worst = max(worst, abs(a - b))
            nq += 1

    out = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "n_queries": nq,
           "gold_used_here": "raw_evidence (the only gold in our caches)",
           "historical_metric_exact_exp_pct": float(np.mean(hist) * 100),
           "frozen_metric_exact_frac_pct": float(np.mean(ours) * 100),
           "max_per_query_abs_difference": float(worst),
           "historical_gate_value_pct": 23.654714666441054,
           "verdict": None}
    same = worst < 1e-12
    out["verdict"] = (
        "METRICS ARE IDENTICAL on the same gold; the anchor gap is entirely "
        "the gold convention (raw_evidence here vs correct_evidence = the 156 "
        "audited corrections at run_locomo.py:189). ANCHOR_MISMATCH explained."
        if same else
        "metrics differ; the gold convention is not the only cause")
    with open(os.path.join(HERE, "AUDIT_LOCOMO_ANCHOR.json"), "w") as fh:
        json.dump(out, fh, indent=2)

    print(f"sorgu: {nq}")
    print(f"  tarihsel exact_exp   {out['historical_metric_exact_exp_pct']:.9f}")
    print(f"  donmus  exact_frac   {out['frozen_metric_exact_frac_pct']:.9f}")
    print(f"  sorgu basina en buyuk fark: {worst:.3e}")
    print(f"  tarihsel cipa (denetlenmis gold ile): "
          f"{out['historical_gate_value_pct']:.9f}")
    print(f"\n{out['verdict']}")


if __name__ == "__main__":
    main()
