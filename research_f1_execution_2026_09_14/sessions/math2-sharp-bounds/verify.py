#!/usr/bin/env python3
"""Sharp full-distance-profile-only deletion bounds: exact finite verification.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Stdlib only. Deterministic (full enumeration, no RNG). Exact integer/Fraction
arithmetic throughout. Fail-closed: any violated assertion exits nonzero; a
deliberately false ("broken") variant is included and must be REJECTED for the
run to count as passed.

Protocol under test (frozen llmzip sign/Hamming top-K):
  docs/query are b-bit vectors; full Hamming distances d_i; a FIXED retained
  subset S (|S|=s, r=b-s removed) scores by retained distances e_i; ranking is
  by (e_i) with uniform-random tie breaking; per-gold expected fractional
  inclusion f(S,T) with S=#{e<e_g}, T=#{e==e_g} (gold included):
    f = 0 if S>=K; 1 if S+T<=K; (K-S)/T otherwise.  (MATH-1 identity, reused.)

Writes results.json next to this script (or argv[1]).
"""
import itertools
import json
import sys
from fractions import Fraction


def f_of_ST(S, T, K):
    if S >= K:
        return Fraction(0)
    if S + T <= K:
        return Fraction(1)
    return Fraction(K - S, T)


def interval(L_r_s, d):
    """Retained-distance interval [L,U] for full distance d given (r, s)."""
    r, s = L_r_s
    return (max(0, d - r), min(s, d))


def popcount(x):
    return bin(x).count("1")


def construct_realization(b, s, d_prof, e_prof):
    """Canonical construction for Theorem R: q=0, S=low s bits.

    doc_i = (low part of weight e_i) | (high part of weight f_i=d_i-e_i).
    Returns (q, S_mask, docs) or raises AssertionError if infeasible.
    """
    r = b - s
    assert len(d_prof) == len(e_prof)
    q = 0
    S_mask = (1 << s) - 1 if s > 0 else 0
    docs = []
    for d, e in zip(d_prof, e_prof):
        f = d - e
        assert 0 <= e <= s, (e, s)
        assert 0 <= f <= r, (f, r)
        assert 0 <= d <= b
        lo = (1 << e) - 1 if e > 0 else 0
        hi = (((1 << f) - 1) << s) if f > 0 else 0
        docs.append(lo | hi)
    # self-check the realization (fail-closed)
    for doc, d, e in zip(docs, d_prof, e_prof):
        x = doc ^ q
        assert popcount(x) == d, (b, s, doc, d)
        assert popcount(x & S_mask) == e, (b, s, doc, e)
    return q, S_mask, docs


def ST_of(e_prof, g):
    eg = e_prof[g]
    S = sum(1 for i, v in enumerate(e_prof) if i != g and v < eg)
    T = 1 + sum(1 for i, v in enumerate(e_prof) if i != g and v == eg)
    return S, T


def H_old(d_prof, g, r):
    return sum(1 for d in d_prof if d <= d_prof[g] + r)


def L_old(d_prof, g, r):
    return sum(1 for d in d_prof if d < d_prof[g] - r)


def corner_extrema(d_prof, g, r, s, K):
    """Theorem P formulas. Returns (fmin, fmax) via opposite corners."""
    n = len(d_prof)
    L = [interval((r, s), d) for d in d_prof]
    Lo = [a for a, _ in L]
    Up = [b_ for _, b_ in L]
    # min corner: gold at U, competitors at L
    e_lo = list(Lo)
    e_lo[g] = Up[g]
    S1, T1 = ST_of(e_lo, g)
    # max corner: gold at L, competitors at U
    e_hi = list(Up)
    e_hi[g] = Lo[g]
    S2, T2 = ST_of(e_hi, g)
    return f_of_ST(S1, T1, K), f_of_ST(S2, T2, K)


def brute_extrema(d_prof, g, r, s, K):
    """Exact min/max of f over the full interval product (independent oracle)."""
    L = [interval((r, s), d) for d in d_prof]
    ranges = [range(a, b_ + 1) for a, b_ in L]
    vals = set()
    for e in itertools.product(*ranges):
        S, T = ST_of(list(e), g)
        vals.add(f_of_ST(S, T, K))
    return min(vals), max(vals)


def check_realizability(res):
    """Theorem R: every interval-profile choice is jointly realizable."""
    total = 0
    for b in range(0, 4):
        for s in range(0, b + 1):
            r = b - s
            for n in range(1, 5):
                for d_prof in itertools.product(range(b + 1), repeat=n):
                    ivs = [interval((r, s), d) for d in d_prof]
                    ranges = [range(a, b_ + 1) for a, b_ in ivs]
                    for e_prof in itertools.product(*ranges):
                        construct_realization(b, s, d_prof, e_prof)
                        total += 1
    res["realizability_pairs_checked"] = total


def check_pergold(K, res, bmax=3, nmax=4, key="pergold_checks_K3"):
    """Theorem P: corner formulas equal brute-force extrema; dominate T3/T4."""
    n_checked = 0
    n_loose_old_lo = 0  # old lower indicator 0
    strict_lo = None    # old 0 but new min > 0
    strict_hi = None    # old 1 but new max < 1
    for b in range(0, bmax + 1):
        for s in range(0, b + 1):
            r = b - s
            for n in range(1, nmax + 1):
                for d_prof in itertools.product(range(b + 1), repeat=n):
                    for g in range(n):
                        cf = corner_extrema(d_prof, g, r, s, K)
                        bf = brute_extrema(d_prof, g, r, s, K)
                        assert cf == bf, ("corner!=brute", b, s, d_prof, g, cf, bf)
                        fmin, fmax = cf
                        # dominance over old T3/T4 indicators
                        old_lo = Fraction(1 if H_old(d_prof, g, r) <= K else 0)
                        old_hi = Fraction(1 if L_old(d_prof, g, r) < K else 0)
                        assert fmin >= old_lo, ("new-lo<old-lo", d_prof, g)
                        assert fmax <= old_hi, ("new-hi>old-hi", d_prof, g)
                        n_checked += 1
                        if old_lo == 0:
                            n_loose_old_lo += 1
                            # genuine-deletion witness only (skip degenerate b=0 / s=0 / r=0)
                            if fmin > 0 and strict_lo is None and b >= 2 and s >= 1 and r >= 1:
                                strict_lo = {
                                    "b": b, "s": s, "r": r, "K": K,
                                    "d": list(d_prof), "g": g,
                                    "old_lo": "0", "new_min": str(fmin),
                                }
                        if old_hi == 1 and fmax < 1 and strict_hi is None and b >= 2 and s >= 1 and r >= 1:
                            strict_hi = {
                                "b": b, "s": s, "r": r, "K": K,
                                "d": list(d_prof), "g": g,
                                "old_hi": "1", "new_max": str(fmax),
                            }
    assert strict_lo is not None, "no strict lower-improvement witness found"
    assert strict_hi is not None, "no strict upper-improvement witness found"
    res[key] = n_checked
    res[key + "_old_lo_vacuous"] = n_loose_old_lo
    res[key + "_strict_lo"] = strict_lo
    res[key + "_strict_hi"] = strict_hi


def check_monotonicity(K, res):
    """Lemma M deltas: single-competitor moves change f in the right direction."""
    n = 0
    for S in range(0, K + 3):
        for T in range(1, K + 4):
            base = f_of_ST(S, T, K)
            # behind -> tied: (S, T+1)
            assert f_of_ST(S, T + 1, K) <= base, (S, T)
            # tied -> ahead: (S+1, T-1) when T >= 2
            if T >= 2:
                assert f_of_ST(S + 1, T - 1, K) <= base, (S, T)
            # behind -> ahead: (S+1, T)
            assert f_of_ST(S + 1, T, K) <= base, (S, T)
            # reverse moves increase f: tied->behind (S,T-1), ahead->tied (S-1,T+1)
            if T >= 2:
                assert f_of_ST(S, T - 1, K) >= base, (S, T)
            if S >= 1:
                assert f_of_ST(S - 1, T + 1, K) >= base, (S, T)
            n += 1
    res["monotonicity_cells"] = n


def joint_best(d_prof, golds, r, s, K):
    """Exact best jointly-attained mean inclusion over the interval product."""
    L = [interval((r, s), d) for d in d_prof]
    ranges = [range(a, b_ + 1) for a, b_ in L]
    best = Fraction(-1)
    for e in itertools.product(*ranges):
        tot = sum(
            f_of_ST(*ST_of(list(e), g), K) for g in golds
        )
        avg = tot / len(golds)
        if avg > best:
            best = avg
    return best


def check_showcase(K, res):
    """Hand-designed strictly-improved nonzero witnesses (K=3, genuine deletion)."""
    # LO: b=4,s=2,r=2, d=(4,0,4,4,4), gold 0 pinned at e=2; one pinned ahead,
    # three pinned tied -> min corner S'=1,T'=4, f=1/2; old T4 lower indicator 0.
    b, s, r = 4, 2, 2
    d_lo = (4, 0, 4, 4, 4)
    fmin, fmax = corner_extrema(d_lo, 0, r, s, K)
    assert (fmin, fmax) == (Fraction(1, 2), Fraction(1, 2)), (fmin, fmax)
    assert H_old(d_lo, 0, r) == 5 > K
    construct_realization(b, s, d_lo, (2, 0, 2, 2, 2))
    # HI: b=4,s=2,r=2, d=(4,0,0,2,2), gold 0 pinned at e=2; max corner S'=2,T'=3,
    # f=1/3; old T4 upper indicator 1 (only 2 docs strictly within r below).
    d_hi = (4, 0, 0, 2, 2)
    fmin2, fmax2 = corner_extrema(d_hi, 0, r, s, K)
    assert (fmin2, fmax2) == (Fraction(0), Fraction(1, 3)), (fmin2, fmax2)
    assert L_old(d_hi, 0, r) == 2 < K
    construct_realization(b, s, d_hi, (2, 0, 0, 2, 2))
    res["showcase"] = {
        "lo": {"d": list(d_lo), "old_lo": "0", "new": "1/2"},
        "hi": {"d": list(d_hi), "old_hi": "1", "new": "1/3"},
    }


def check_joint(K, res):
    """Theorem J: per-gold-average need not be jointly attainable (witness)."""
    # witness: b=4,s=2,r=2, d=(2,2,0,0), golds={0,1}, K=3
    b, s, r = 4, 2, 2
    d_prof = (2, 2, 0, 0)
    golds = [0, 1]
    permax = []
    for g in golds:
        _, fmax = corner_extrema(d_prof, g, r, s, K)
        permax.append(fmax)
    avgmax = sum(permax) / len(golds)
    best = joint_best(d_prof, golds, r, s, K)
    assert avgmax == Fraction(1), avgmax
    assert best == Fraction(3, 4), best
    assert best < avgmax, "witness must show a strict joint gap"
    # computable envelope gap: uniform golds-at-L corner is jointly feasible
    L = [interval((r, s), d) for d in d_prof]
    e_uni = [(a if i in golds else b_) for i, (a, b_) in enumerate(L)]
    uni = sum(f_of_ST(*ST_of(e_uni, g), K) for g in golds) / len(golds)
    gamma = avgmax - uni
    assert Fraction(0) <= avgmax - best <= gamma, (avgmax, best, gamma)
    # single gold is always jointly sharp (no conflict possible)
    for g in golds:
        assert joint_best(d_prof, [g], r, s, K) == permax[golds.index(g)]
    res["joint_witness"] = {
        "b": b, "s": s, "r": r, "K": K, "d": list(d_prof), "golds": golds,
        "avg_of_pergold_max": str(avgmax),
        "best_joint": str(best),
        "uniform_golds_at_L": str(uni),
        "gamma_envelope_gap": str(gamma),
    }


def broken_variant_must_fail():
    """Deliberately FALSE claim: avg-of-per-gold-max is always jointly attainable.

    Returns True iff the checker correctly REJECTS it (fail-closed demo).
    """
    b, s, r, K = 4, 2, 2, 3
    d_prof = (2, 2, 0, 0)
    golds = [0, 1]
    permax = [corner_extrema(d_prof, g, r, s, K)[1] for g in golds]
    avgmax = sum(permax) / len(golds)
    best = joint_best(d_prof, golds, r, s, K)
    try:
        assert best == avgmax, "BROKEN claim: joint attains avg-of-max"
    except AssertionError:
        return True
    return False


def edge_cases(res):
    """s=0 and r=0 degeneracies: intervals force unique profiles; corners agree."""
    out = {}
    # s=0 (all deleted): e identically 0
    b, s, r, K = 3, 0, 3, 3
    d_prof = (0, 1, 2, 3)
    L = [interval((r, s), d) for d in d_prof]
    assert all(iv == (0, 0) for iv in L), L
    e = [0, 0, 0, 0]
    construct_realization(b, s, d_prof, e)
    out["s0_intervals"] = [list(iv) for iv in L]
    out["s0_f_gold0"] = str(f_of_ST(*ST_of(e, 0), K))
    # r=0 (nothing deleted): e == d forced
    b, s, r = 3, 3, 0
    L = [interval((r, s), d) for d in d_prof]
    assert all(iv == (d, d) for iv, d in zip(L, d_prof)), L
    construct_realization(b, s, d_prof, list(d_prof))
    out["r0_intervals"] = [list(iv) for iv in L]
    # b=0 degenerate (s=r=0)
    construct_realization(0, 0, (0,), (0,))
    out["b0_ok"] = True
    res["edge_cases"] = out


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "results.json"
    res = {"K": 3, "banner": "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] "
                             "[NOT FOR CITATION] [DISCLOSE-BEFORE-USE]"}
    check_realizability(res)
    check_pergold(3, res)
    check_pergold(1, res, bmax=2, nmax=3, key="pergold_checks_K1")  # spot check
    # re-run K=3 counts label fix: check_pergold overwrote; restore by rerun order
    check_monotonicity(3, res)
    check_showcase(3, res)
    check_joint(3, res)
    edge_cases(res)
    rejected = broken_variant_must_fail()
    res["broken_variant_rejected"] = rejected
    assert rejected, "checker failed to reject the deliberately false variant"
    with open(out_path, "w") as fh:
        json.dump(res, fh, indent=2)
    print("realizability_pairs=%d" % res["realizability_pairs_checked"])
    print("K3_checks=%d strict_lo=%s strict_hi=%s" % (
        res["pergold_checks_K3"], res["pergold_checks_K3_strict_lo"],
        res["pergold_checks_K3_strict_hi"]))
    print("K1_spot=%d" % res["pergold_checks_K1"])
    print("mono_cells=%d joint=%s" % (
        res["monotonicity_cells"], res["joint_witness"]))
    print("edge=%s broken_rejected=%s" % (res["edge_cases"], rejected))
    print("DONE ALL SHARP-BOUND CHECKS PASSED (K=3 full + K=1 spot)")


if __name__ == "__main__":
    main()
