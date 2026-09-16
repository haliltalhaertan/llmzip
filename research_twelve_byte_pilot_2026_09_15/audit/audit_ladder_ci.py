#!/usr/bin/env python3
"""Paired confidence intervals for every rung of the pipeline ladder.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

`run_ladder.py` reports a hit@10 for each stage of the text-to-bit chain, but
240 queries cannot resolve a 2 pp unpaired difference -- the unpaired SE alone
is about 2.3 pp.  Every rung scores the SAME queries, so the differences are
paired and the paired interval is far tighter.  This computes it, and without
it none of the step deltas may be read as real.

Reported for each consecutive step and for the two that matter end to end:
  * the paired mean difference
  * a BCa-free percentile bootstrap CI over queries (LongMemEval has one
    query per archive, so query and cluster coincide here -- no cluster
    bootstrap is needed, unlike the multi-query benchmarks)
  * how many queries move each way, since a mean of a 0/1 variable hides that
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
B = 20000
SEED = 20260916
RUNGS = ["S1_Z", "S2_svd", "S3_norm", "S4_center", "S5_sign_fq", "S6_sign"]
PAIRS = [("S1_Z", "S2_svd"), ("S2_svd", "S3_norm"), ("S3_norm", "S4_center"),
         ("S4_center", "S5_sign_fq"), ("S5_sign_fq", "S6_sign"),
         ("S1_Z", "S6_sign"), ("S4_center", "S6_sign")]


def ci(d, rng):
    n = len(d)
    idx = rng.integers(0, n, size=(B, n))
    boot = d[idx].mean(axis=1) * 100
    return float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))


def main():
    src = json.load(open(os.path.join(HERE, "LADDER.json")))
    pq = src.get("per_query_hit10")
    if pq is None:
        print("LADDER.json has no per_query_hit10; rerun run_ladder.py")
        return 1
    V = {r: np.asarray(pq[r], dtype=float) for r in RUNGS}
    n = len(V["S6_sign"])
    rng = np.random.default_rng(SEED)

    out = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "benchmark": "lme", "n_queries": n, "bootstrap": B,
           "note": ("one query per archive on LongMemEval, so query-level "
                    "and cluster-level bootstrap coincide"),
           "levels_pct": {r: float(V[r].mean() * 100) for r in RUNGS},
           "steps": {}}
    print(f"n = {n} sorgu,  {B} bootstrap\n")
    print(f"  {'adim':>22s}{'fark':>9s}{'%95 aralik':>20s}"
          f"{'anlamli':>10s}{'yukari':>8s}{'asagi':>7s}")
    for a, b in PAIRS:
        d = V[b] - V[a]
        lo, hi = ci(d, rng)
        sig = "EVET" if (lo > 0 or hi < 0) else "hayir"
        up = int(np.count_nonzero(d > 0))
        dn = int(np.count_nonzero(d < 0))
        out["steps"][f"{a}->{b}"] = {
            "delta_pp": float(d.mean() * 100), "ci95": [lo, hi],
            "significant": sig == "EVET",
            "queries_up": up, "queries_down": dn,
            "queries_unchanged": int(n - up - dn)}
        print(f"  {a+' -> '+b:>22s}{d.mean()*100:+9.2f}"
              f"{f'[{lo:+.2f}, {hi:+.2f}]':>20s}{sig:>10s}{up:>8d}{dn:>7d}")

    with open(os.path.join(HERE, "LADDER_CI.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print("\nwrote LADDER_CI.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
