#!/usr/bin/env python3
"""Exact joint multi-gold bounds — primary checker (bucket formulation).

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Checks the joint corner theorem over bounded exhaustive sweeps using the
tie-bucket expectation formula. The differently formulated checker lives in
check_independent.py (permutation-enumeration formulation + explicit binary
codebook construction). Both must agree.
"""

import json
import sys
from fractions import Fraction
from itertools import product


def interval(d, s, r):
    return (max(0, d - r), min(s, d))


def expected_frac_bucket(e, golds, K):
    """Expected fraction of designated golds in topK (uniform tie-break).

    Bucket law: bucket j (gold count g, size t, S docs strictly ahead):
    full take g if S+t<=K, else (K-S)*g/t. Exact Fraction arithmetic.
    """
    G = set(golds)
    m = len(golds)
    assert m >= 1
    buckets = {}
    for i, v in enumerate(e):
        b = buckets.setdefault(v, [0, 0])
        b[0 if i in G else 1] += 1
    total = Fraction(0)
    S = 0
    for v in sorted(buckets):
        g, c = buckets[v]
        t = g + c
        if S >= K:
            break
        if S + t <= K:
            total += g
        else:
            total += Fraction((K - S) * g, t)
        S += t
    return total / m


def expected_weight_bucket(e, golds, weights, K):
    """Expected total gold weight in topK (unnormalized)."""
    G = set(golds)
    buckets = {}
    for i, v in enumerate(e):
        b = buckets.setdefault(v, [Fraction(0), 0])
        if i in G:
            b[0] += weights[i]
        b[1] += 1
    total = Fraction(0)
    S = 0
    for v in sorted(buckets):
        W, t = buckets[v]
        if S >= K:
            break
        if S + t <= K:
            total += W
        else:
            total += Fraction(K - S) * W / t
        S += t
    return total


def corners(dprof, golds, s, r):
    G = set(golds)
    emax, emin = [], []
    for i, d in enumerate(dprof):
        L, U = interval(d, s, r)
        if i in G:
            emax.append(L)
            emin.append(U)
        else:
            emax.append(U)
            emin.append(L)
    return tuple(emax), tuple(emin)


def feasible_set(dprof, s, r):
    ranges = [range(*((lambda LU: (LU[0], LU[1] + 1))(interval(d, s, r))))
              for d in dprof]
    yield from product(*ranges)


def per_gold_max(dprof, g, s, r, K):
    """Single-gold sharp max (Theorem P): gold at L, every rival at U."""
    n = len(dprof)
    Lg, _ = interval(dprof[g], s, r)
    S = sum(1 for i in range(n) if i != g and interval(dprof[i], s, r)[1] < Lg)
    T = 1 + sum(1 for i in range(n) if i != g and interval(dprof[i], s, r)[1] == Lg)
    if S >= K:
        return Fraction(0)
    if S + T <= K:
        return Fraction(1)
    return Fraction(K - S, T)


def main(out_path):
    res = {"cells": 0, "violations": [], "witnesses": {}, "edge": {}}

    # ---- Sweep A: b=2, n=3, all profiles, all nonempty gold sets, all K ----
    b, s = 2, 1
    r = b - s
    n = 3
    for dprof in product(range(b + 1), repeat=n):
        for mask in range(1, 1 << n):
            golds = [i for i in range(n) if mask >> i & 1]
            for K in range(1, n + 1):
                emax, emin = corners(dprof, golds, s, r)
                rmax = expected_frac_bucket(emax, golds, K)
                rmin = expected_frac_bucket(emin, golds, K)
                for e in feasible_set(dprof, s, r):
                    v = expected_frac_bucket(e, golds, K)
                    res["cells"] += 1
                    if not (rmin <= v <= rmax):
                        res["violations"].append(
                            {"d": dprof, "golds": golds, "K": K,
                             "e": e, "v": str(v),
                             "min": str(rmin), "max": str(rmax)})
    res["sweep_A"] = {"b": b, "s": s, "n": n, "cells": res["cells"]}

    # ---- Sweep B: b=3, n=3, s=2, all profiles x gold sets, K=3 + K=1 ----
    b, s = 3, 2
    r = b - s
    cells_b = 0
    for dprof in product(range(b + 1), repeat=n):
        for mask in range(1, 1 << n):
            golds = [i for i in range(n) if mask >> i & 1]
            for K in (1, 3):
                emax, emin = corners(dprof, golds, s, r)
                rmax = expected_frac_bucket(emax, golds, K)
                rmin = expected_frac_bucket(emin, golds, K)
                for e in feasible_set(dprof, s, r):
                    v = expected_frac_bucket(e, golds, K)
                    cells_b += 1
                    if not (rmin <= v <= rmax):
                        res["violations"].append(
                            {"sweep": "B", "d": dprof, "golds": golds,
                             "K": K, "e": e, "v": str(v),
                             "min": str(rmin), "max": str(rmax)})
    res["sweep_B"] = {"b": b, "s": s, "n": n, "cells": cells_b}

    # ---- Sweep C: targeted n=4 cases incl. the prior witness profile ----
    cases_c = [
        {"b": 4, "s": 2, "d": (2, 2, 0, 0), "golds": [0, 1], "K": 3},
        {"b": 4, "s": 2, "d": (2, 2, 0, 0), "golds": [0, 1, 2], "K": 3},
        {"b": 4, "s": 2, "d": (2, 2, 0, 0), "golds": [0, 1, 2, 3], "K": 4},
        {"b": 4, "s": 2, "d": (4, 0, 4, 4), "golds": [0], "K": 3},
        {"b": 3, "s": 1, "d": (3, 3, 0, 0), "golds": [0, 1], "K": 2},
        {"b": 2, "s": 2, "d": (2, 1, 0, 2), "golds": [1, 3], "K": 1},
        {"b": 2, "s": 0, "d": (2, 1, 0, 2), "golds": [0, 2], "K": 3},
        {"b": 2, "s": 2, "d": (2, 1, 0, 2), "golds": [0, 2], "K": 4},
    ]
    cells_c = 0
    for c in cases_c:
        s, r = c["s"], c["b"] - c["s"]
        emax, emin = corners(c["d"], c["golds"], s, r)
        rmax = expected_frac_bucket(emax, c["golds"], c["K"])
        rmin = expected_frac_bucket(emin, c["golds"], c["K"])
        for e in feasible_set(c["d"], s, r):
            v = expected_frac_bucket(e, c["golds"], c["K"])
            cells_c += 1
            if not (rmin <= v <= rmax):
                res["violations"].append(
                    {"sweep": "C", "case": c, "e": e, "v": str(v),
                     "min": str(rmin), "max": str(rmax)})
    res["sweep_C"] = {"cells": cells_c}

    # ---- Prior witness: d=(2,2,0,0), b=4, s=2, K=3, golds={0,1} ----
    dprof, s, r, K, golds = (2, 2, 0, 0), 2, 2, 3, [0, 1]
    emax, emin = corners(dprof, golds, s, r)
    joint_max = expected_frac_bucket(emax, golds, K)
    joint_min = expected_frac_bucket(emin, golds, K)
    avg_indiv_max = sum(per_gold_max(dprof, g, s, r, K) for g in golds) / len(golds)
    baseline = expected_frac_bucket(dprof, golds, K)  # r=0-style: e=d profile
    res["witnesses"]["prior_example"] = {
        "d": list(dprof), "s": s, "K": K, "golds": golds,
        "emax": list(emax), "emin": list(emin),
        "joint_max": str(joint_max), "joint_min": str(joint_min),
        "avg_individual_max": str(avg_indiv_max),
        "baseline_original": str(baseline),
        "recall_change_interval": [str(joint_min - baseline),
                                   str(joint_max - baseline)],
    }
    assert joint_max == Fraction(3, 4), joint_max
    assert avg_indiv_max == Fraction(1), avg_indiv_max
    assert joint_min == Fraction(1, 2), joint_min
    assert baseline == Fraction(1, 2), baseline

    # ---- FALSE VARIANT (negative control): avg-of-individual-maxima sharp ----
    # Deliberately false universal claim; the checker must REJECT it here.
    false_claim_holds = (avg_indiv_max == joint_max)
    res["negative_control"] = {
        "claim": "avg of per-gold maxima is always jointly attainable",
        "verdict": "REJECTED" if not false_claim_holds else "HELD (BAD)",
    }
    assert not false_claim_holds, "negative control failed to reject!"

    # ---- Weighted counterexample: n=2, m=2, K=1, weights 1 vs 2 ----
    e_corner, w = (0, 0), {0: Fraction(1), 1: Fraction(2)}
    w_corner = expected_weight_bucket(e_corner, [0, 1], w, 1)
    w_alt = expected_weight_bucket((1, 0), [0, 1], w, 1)
    res["witnesses"]["weighted_counterexample"] = {
        "n": 2, "m": 2, "K": 1, "weights": {"0": "1", "1": "2"},
        "corner_all_golds_at_L": str(w_corner),
        "deviation_e10": str(w_alt),
        "corner_optimal": bool(w_corner >= w_alt),
    }
    assert w_corner == Fraction(3, 2), w_corner
    assert w_alt == Fraction(2), w_alt
    assert w_alt > w_corner  # corner theorem FAILS for weighted objective

    # ---- Edge cases ----
    res["edge"]["K_equals_n"] = str(expected_frac_bucket((2, 2, 0, 0), [0, 1], 4))
    assert expected_frac_bucket((2, 2, 0, 0), [0, 1], 4) == Fraction(1)
    res["edge"]["all_gold"] = str(expected_frac_bucket((1, 0, 2), [0, 1, 2], 2))
    assert expected_frac_bucket((1, 0, 2), [0, 1, 2], 2) == Fraction(2, 3)
    res["edge"]["s_zero_singleton"] = str(expected_frac_bucket((0, 0, 0, 0), [0, 2], 3))
    assert expected_frac_bucket((0, 0, 0, 0), [0, 2], 3) == Fraction(3, 4)

    res["total_cells"] = res["cells"] + cells_b + cells_c
    res["status"] = "PASS" if not res["violations"] else "FAIL"
    with open(out_path, "w") as f:
        json.dump(res, f, indent=2)
    print(f"cells={res['total_cells']} violations={len(res['violations'])} "
          f"joint_max={joint_max} avg_indiv={avg_indiv_max} "
          f"weighted_corner={w_corner} weighted_alt={w_alt} "
          f"negative_control={res['negative_control']['verdict']}")
    print("DONE PRIMARY CHECKS " + res["status"])
    return 0 if not res["violations"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "results.json"))
