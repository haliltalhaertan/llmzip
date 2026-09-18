#!/usr/bin/env python3
"""Exhaustive small-case verification for ranking-stability theorems (T1-T6).

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Stdlib only. Deterministic (no RNG; full enumeration).
Protocol under test: docs/query as b-bit sign vectors, Hamming distances,
top-K ranking, per-gold (S,T) profile, f(S,T) = expected fractional recall
under uniform random tie-break (frozen-tie expectation identity, MATH-1).

Writes results.json next to this script (or argv[1]).
"""
import itertools
import json
import sys
from fractions import Fraction


def popcount(x):
    return bin(x).count("1")


def dists(docs, q, b, sub):
    """Full + subset + removed Hamming distances. sub = retained bitmask."""
    full_mask = (1 << b) - 1
    rem = full_mask ^ sub
    d, ds, dr = [], [], []
    for doc in docs:
        x = doc ^ q
        d.append(popcount(x))
        ds.append(popcount(x & sub))
        dr.append(popcount(x & rem))
    return d, ds, dr


def ST(d, g):
    dg = d[g]
    S = sum(1 for v in d if v < dg)
    T = sum(1 for v in d if v == dg)
    return S, T


def f_of_ST(S, T, K):
    if S >= K:
        return Fraction(0)
    if S + T <= K:
        return Fraction(1)
    return Fraction(K - S, T)


def pess_of_ST(S, T, K):
    return Fraction(1 if S + T <= K else 0)


def opt_of_ST(S, T, K):
    return Fraction(1 if S < K else 0)


def topk_set(d, K):
    order = sorted(range(len(d)), key=lambda i: (d[i], i))
    return set(order[:K])


def configs(b, n):
    return itertools.product(range(1 << b), repeat=n + 1)  # (*docs, q)


def submasks(b):
    return [s for s in range(1 << b) if popcount(s) < b]  # proper subsets, r>=1


def gold_sets(n):
    out = [[i] for i in range(n)]
    out.append(list(range(n)))
    return out


def check_T1_T2_T3_T4(b, n, K, res):
    r = res  # dict accumulator
    for cfg in configs(b, n):
        docs, q = cfg[:-1], cfg[-1]
        for sub in submasks(b):
            rr = b - popcount(sub)
            d, ds, dr = dists(docs, q, b, sub)
            # ---- T1: perturbation bound + corollary + tightness ----
            r["T1_checks"] += 1
            for i in range(n):
                for j in range(n):
                    assert abs((d[i] - d[j]) - (ds[i] - ds[j])) == abs(dr[i] - dr[j])
                    assert abs(dr[i] - dr[j]) <= rr
                    if d[j] - d[i] > rr:
                        assert ds[j] > ds[i], "T1 corollary violated"
                    if abs(dr[i] - dr[j]) == rr and rr > 0:
                        r["T1_tight_hits"] += 1
            # ---- T2: gap>r => top-K set preserved (both boundaries strict) ----
            srt = sorted(d)
            Gamma = srt[K] - srt[K - 1] if K < n else None
            if Gamma is not None:
                r["T2_applicable"] += 1
                if Gamma > rr:
                    r["T2_premise_hits"] += 1
                    assert topk_set(d, K) == topk_set(ds, K), "T2 set invariance violated"
                    ss = sorted(ds)
                    assert ss[K] - ss[K - 1] > 0, "T2 subset-boundary strictness violated"
                elif Gamma == rr:
                    ss = sorted(ds)
                    if ss[K] == ss[K - 1]:
                        r["T2_sharp_instances"] += 1
                        if r["T2_sharp_example"] is None:
                            r["T2_sharp_example"] = {
                                "b": b, "n": n, "K": K, "docs": list(docs),
                                "q": q, "sub": sub, "d": d, "ds": ds,
                            }
            # ---- T3/T4 per gold-set ----
            for G in gold_sets(n):
                m = len(G)
                for g in G:
                    S, T = ST(d, g)
                    Sp, Tp = ST(ds, g)
                    fp = f_of_ST(Sp, Tp, K)
                    H = sum(1 for v in d if v <= d[g] + rr)  # deep-free radius count
                    L = sum(1 for v in d if v < d[g] - rr)  # deep-buried strict count
                    r["T3_checks"] += 1
                    if H <= K:
                        r["T3_free_hits"] += 1
                        assert fp == 1, "T3 deep-free survival violated"
                    if L >= K:
                        r["T3_buried_hits"] += 1
                        assert fp == 0, "T3 deep-buried persistence violated"
                # T4 sandwich on this question
                Ef = sum(f_of_ST(*ST(d, g), K) for g in G) / m
                Es = sum(f_of_ST(*ST(ds, g), K) for g in G) / m
                lo = sum(1 for g in G
                         if sum(1 for v in d if v <= d[g] + rr) <= K) / m
                hi = sum(1 for g in G
                         if sum(1 for v in d if v < d[g] - rr) < K) / m
                r["T4_checks"] += 1
                assert lo - 1e-12 <= Es <= hi + 1e-12, "T4 sandwich violated"
                assert float(Ef) - float(Es) <= (float(Ef) - lo) + 1e-12
                if lo == 0:
                    r["T4_vacuous_lo"] += 1
                if abs(float(Es) - lo) < 1e-12:
                    r["T4_lo_attained"] += 1
                if abs(float(Es) - hi) < 1e-12:
                    r["T4_hi_attained"] += 1


def check_T5(res):
    """Brute-force permutation check of hypergeometric tie math."""
    for T in range(1, 6):
        for K in range(1, 4):
            for S in range(0, K + 1):
                t = K - S
                if t < 0 or t > T:
                    continue
                perms = list(itertools.permutations(range(T)))
                res["T5_perm_count"] += len(perms)
                # single distinguished gold (doc 0): inclusion freq == t/T
                if T > 0:
                    hits = sum(1 for p in perms if 0 in p[:t]) if t > 0 \
                        else 0
                    res["T5_checks"] += 1
                    assert Fraction(hits, len(perms)) == Fraction(t, T), \
                        f"T5 single-gold freq violated T={T} K={K} S={S}"
                # multi-gold: c golds among T, #picked distribution == Hypergeometric
                for c in range(1, T + 1):
                    from math import comb
                    dist = {}
                    for p in perms:
                        picked = sum(1 for x in p[:t] if x < c) if t > 0 else 0
                        dist[picked] = dist.get(picked, 0) + 1
                    res["T5_checks"] += 1
                    for v, cnt in dist.items():
                        expect = Fraction(comb(c, v) * comb(T - c, t - v), comb(T, t)) \
                            if 0 <= v <= c and 0 <= t - v <= T - c else Fraction(0)
                        assert Fraction(cnt, len(perms)) == expect, \
                            f"T5 hypergeometric violated T={T} c={c} t={t} v={v}"
                    # variance formula spot: E[V]=t*c/T, Var=t*(c/T)*(1-c/T)*(T-t)/(T-1) (T>1)
                    mean = sum(Fraction(v) * Fraction(cnt, len(perms))
                               for v, cnt in dist.items())
                    assert mean == Fraction(t * c, T)


def specific_witnesses(res):
    """Named 96-bit-liftable witnesses: T6 impossibility + r=1 opt boundary."""
    # W1 (r=1): full E=1, subset E=1/2, pess 1->0, opt stays 1. K=1.
    b, K, sub = 2, 1, 0b01  # retain bit0, remove bit1
    docs, q = (0b00, 0b10), 0b00
    d, ds, _ = dists(docs, q, b, sub)
    g = 0
    S, T = ST(d, g)
    Sp, Tp = ST(ds, g)
    assert (S, T) == (0, 1) and f_of_ST(S, T, K) == 1
    assert (Sp, Tp) == (0, 2) and f_of_ST(Sp, Tp, K) == Fraction(1, 2)
    assert pess_of_ST(S, T, K) == 1 and pess_of_ST(Sp, Tp, K) == 0
    assert opt_of_ST(S, T, K) == 1 and opt_of_ST(Sp, Tp, K) == 1
    res["W1"] = {"docs": list(docs), "q": q, "b": b, "K": K, "sub": sub,
                 "full_f": "1", "sub_f": "1/2", "pess": "1->0", "opt": "1->1"}
    # W2 (r=2): optimistic recall killed 1->0. K=3, n=4 (triplicated intruder).
    b, K, sub = 3, 3, 0b001
    docs, q = (0b001, 0b110, 0b110, 0b110), 0b000
    d, ds, _ = dists(docs, q, b, sub)
    assert d == [1, 2, 2, 2] and ds == [1, 0, 0, 0]
    S, T = ST(d, 0)
    Sp, Tp = ST(ds, 0)
    assert f_of_ST(S, T, K) == 1 and opt_of_ST(S, T, K) == 1
    assert f_of_ST(Sp, Tp, K) == 0 and opt_of_ST(Sp, Tp, K) == 0
    res["W2"] = {"docs": list(docs), "q": q, "b": b, "K": K, "sub": sub,
                 "d": d, "ds": ds, "opt": "1->0"}
    # W3: reversibility != retrieval. Signed permutation (bit swap) preserves
    # all distances exactly; subset projection does not. Exhaustively implied
    # by T1 (perm: r=0 -> exact equality); here one concrete line:
    docs, q = (0b01, 0b10), 0b00
    d, _, _ = dists(docs, q, 2, 0b11)
    swapped = tuple(v ^ 0b11 for v in docs)  # swap bit values globally
    d2, _, _ = dists(swapped, q ^ 0b11, 2, 0b11)
    assert sorted(d) == sorted(d2)
    res["W3"] = {"note": "global bit-complement (reversible) preserves distance multiset; projection need not"}


def main():
    res = {
        "labels": ["[LOCAL EXPLORATORY PILOT]", "[NOT PREREGISTERED]",
                   "[NOT FOR CITATION]", "[DISCLOSE-BEFORE-USE]"],
        "ranges": {
            "A": "b=3, n=3, K in {1,2}: all 8^4=4096 (docs,q) x 7 proper subsets",
            "B": "b=3, n=2, K=1: all 8^3=512 (docs,q) x 7 proper subsets",
            "C": "b=4, n=2, K=1: all 16^3=4096 (docs,q) x 15 proper subsets",
            "gold_sets": "all singletons + full set per config",
            "T5": "T=1..5, K=1..3, all S<=K, all c=1..T, full permutation enum",
        },
        "T1_checks": 0, "T1_tight_hits": 0,
        "T2_applicable": 0, "T2_premise_hits": 0, "T2_sharp_instances": 0,
        "T2_sharp_example": None,
        "T3_checks": 0, "T3_free_hits": 0, "T3_buried_hits": 0,
        "T4_checks": 0, "T4_vacuous_lo": 0,
        "T4_lo_attained": 0, "T4_hi_attained": 0,
        "T5_checks": 0, "T5_perm_count": 0,
    }
    check_T1_T2_T3_T4(3, 3, 1, res)
    check_T1_T2_T3_T4(3, 3, 2, res)
    check_T1_T2_T3_T4(3, 2, 1, res)
    check_T1_T2_T3_T4(4, 2, 1, res)
    # CORRECTED r=1 boundary (original "opt preserved" conjecture FALSIFIED by
    # this sweep on the first run): restricted entry -- no doc strictly behind
    # gold in full code can become strictly closer in subset code. Tied docs
    # CAN (asymmetric tie-break on the removed bit), so opt may still break.
    opt_kills_r1 = 0
    opt_cases_r1 = 0
    opt_kill_example = None
    entry_violations = 0
    for (b, n, K) in [(3, 3, 1), (3, 3, 2), (3, 2, 1), (4, 2, 1)]:
        for cfg in configs(b, n):
            docs, q = cfg[:-1], cfg[-1]
            for sub in submasks(b):
                if b - popcount(sub) != 1:
                    continue
                d, ds, _ = dists(docs, q, b, sub)
                for g in range(n):
                    Sp, _ = ST(ds, g)
                    # restricted entry: every new strictly-closer doc was tied-or-ahead
                    for i in range(n):
                        if ds[i] < ds[g] and not (d[i] <= d[g]):
                            entry_violations += 1
                    assert entry_violations == 0, "r=1 restricted-entry violated"
                    if opt_of_ST(*ST(d, g), K) == 1:
                        opt_cases_r1 += 1
                        if opt_of_ST(Sp, ST(ds, g)[1], K) != 1:
                            opt_kills_r1 += 1
                            if opt_kill_example is None:
                                opt_kill_example = {
                                    "b": b, "n": n, "K": K, "docs": list(docs),
                                    "q": q, "sub": sub, "gold": g,
                                    "d": d, "ds": ds,
                                }
    assert opt_kills_r1 > 0, "expected r=1 opt-kill counterexample to exist"
    res["opt_r1_cases"] = opt_cases_r1
    res["opt_r1_kills"] = opt_kills_r1
    res["opt_r1_kill_example"] = opt_kill_example
    # Minimal hand-checkable r=1 opt-kill (C1): tie broken asymmetrically.
    b, K, sub = 2, 1, 0b01
    docs, q = (0b01, 0b10), 0b00
    d, ds, _ = dists(docs, q, b, sub)
    assert d == [1, 1] and ds == [1, 0]
    assert opt_of_ST(*ST(d, 0), K) == 1 and opt_of_ST(*ST(ds, 0), K) == 0
    res["C1"] = {"docs": list(docs), "q": q, "b": b, "K": K, "sub": sub,
                 "d": d, "ds": ds, "opt": "1->0 via tied-doc entry"}
    check_T5(res)
    specific_witnesses(res)
    res["verdict"] = ("ALL THEOREM CHECKS PASSED: T1 bound+corollary, T2 set "
                      "invariance under gap>r, T3 deep-free/buried, T4 sandwich, "
                      "T5 hypergeometric, W1/W2/C1 impossibility witnesses, "
                      "r=1 restricted-entry (opt CAN break via tied docs).")
    out = sys.argv[1] if len(sys.argv) > 1 else "results.json"
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2, default=str)
    print(f"T1_checks={res['T1_checks']} tight_hits={res['T1_tight_hits']}")
    print(f"T2_applicable={res['T2_applicable']} premise_hits={res['T2_premise_hits']} "
          f"sharp_instances={res['T2_sharp_instances']}")
    print(f"T2_sharp_example={res['T2_sharp_example']}")
    print(f"T3_checks={res['T3_checks']} free_hits={res['T3_free_hits']} "
          f"buried_hits={res['T3_buried_hits']}")
    print(f"T4_checks={res['T4_checks']} vacuous_lo={res['T4_vacuous_lo']} "
          f"lo_attained={res['T4_lo_attained']} hi_attained={res['T4_hi_attained']}")
    print(f"T5_checks={res['T5_checks']} perm_count={res['T5_perm_count']}")
    print(f"opt_r1: cases={res['opt_r1_cases']} kills={res['opt_r1_kills']}")
    print(f"W1={res['W1']}")
    print(f"W2={res['W2']}")
    print("DONE " + res["verdict"])
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
