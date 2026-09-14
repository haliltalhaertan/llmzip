#!/usr/bin/env python3
"""Independent checker for sharp full-profile deletion bounds.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Independently written: no imports from verify.py. Different canonical
construction (retained set = HIGH s bits, docs filled from the top), own
interval/corner/brute-force routines, different enumeration order. Stdlib only,
exact Fractions, fail-closed (nonzero exit on any violation). Also rejects the
same deliberately false variant (avg-of-per-gold-max jointly attainable).
"""
import itertools
import sys
from fractions import Fraction


def frac_f(S, T, K):
    if S >= K:
        return Fraction(0)
    if S + T <= K:
        return Fraction(1)
    return Fraction(K - S, T)


def ends(d, r, s):
    return (max(0, d - r), min(s, d))


def build(b, s, dprof, eprof):
    """Realize via q=0 and S = high s bits; fail-closed self-check."""
    r = b - s
    Smask = ((1 << s) - 1) << r if s > 0 else 0
    full = (1 << b) - 1 if b > 0 else 0
    docs = []
    for d, e in zip(dprof, eprof):
        f = d - e
        assert 0 <= e <= s and 0 <= f <= r and 0 <= d <= b
        hi = (((1 << e) - 1) << r) if e > 0 else 0
        lo = ((1 << f) - 1) if f > 0 else 0
        docs.append(hi | lo)
    for doc, d, e in zip(docs, dprof, eprof):
        assert bin(doc).count("1") == d, (doc, d)
        assert bin(doc & Smask).count("1") == e, (doc, e)
        assert bin(doc & (full ^ Smask)).count("1") == d - e
    return docs


def st_of(eprof, g):
    eg = eprof[g]
    S = sum(1 for i, v in enumerate(eprof) if i != g and v < eg)
    T = 1 + sum(1 for i, v in enumerate(eprof) if i != g and v == eg)
    return S, T


def main():
    K = 3
    n_real = 0
    # 1. realizability, reversed enumeration order, b<=3
    for b in (3, 2, 1, 0):
        for n in (4, 3, 2, 1):
            for s in range(b, -1, -1):
                r = b - s
                for dprof in itertools.product(range(b + 1), repeat=n):
                    spans = [ends(d, r, s) for d in dprof]
                    for eprof in itertools.product(
                            *(range(a, c + 1) for a, c in spans)):
                        build(b, s, dprof, eprof)
                        n_real += 1
    # 2. corner == brute force per gold, b<=2
    n_gold = 0
    for b in (2, 1, 0):
        for n in (3, 2, 1):
            for s in range(0, b + 1):
                r = b - s
                for dprof in itertools.product(range(b + 1), repeat=n):
                    spans = [ends(d, r, s) for d in dprof]
                    box = [range(a, c + 1) for a, c in spans]
                    for g in range(n):
                        vals = set()
                        for e in itertools.product(*box):
                            vals.add(frac_f(*st_of(e, g), K))
                        lo = [a for a, _ in spans]
                        hi = [c for _, c in spans]
                        e_min = list(lo)
                        e_min[g] = hi[g]
                        e_max = list(hi)
                        e_max[g] = lo[g]
                        cmin = frac_f(*st_of(e_min, g), K)
                        cmax = frac_f(*st_of(e_max, g), K)
                        assert cmin == min(vals), (dprof, g, cmin, min(vals))
                        assert cmax == max(vals), (dprof, g, cmax, max(vals))
                        n_gold += 1
    # 3. joint-conflict witness re-derived (b=4 outside scope above on purpose)
    b, s, r, dprof, golds = 4, 2, 2, (2, 2, 0, 0), (0, 1)
    spans = [ends(d, r, s) for d in dprof]
    box = [range(a, c + 1) for a, c in spans]
    permax = []
    for g in golds:
        hi = [c for _, c in spans]
        lo = [a for a, _ in spans]
        e = list(hi)
        e[g] = lo[g]
        permax.append(frac_f(*st_of(e, g), K))
    avg = sum(permax) / len(golds)
    best = max(
        sum(frac_f(*st_of(e, g), K) for g in golds) / len(golds)
        for e in itertools.product(*box)
    )
    assert avg == Fraction(1) and best == Fraction(3, 4) and best < avg
    build(b, s, dprof, (0, 2, 0, 0))  # one attaining codebook exists
    # 4. showcase re-derived
    assert frac_f(*st_of((2, 0, 2, 2, 2), 0), K) == Fraction(1, 2)
    assert frac_f(*st_of((2, 0, 0, 2, 2), 0), K) == Fraction(1, 3)
    # 5. broken variant must be rejected
    try:
        assert best == avg, "BROKEN: joint attains avg-of-max"
        print("INDEPENDENT CHECKER FAILED TO REJECT BROKEN VARIANT")
        return 1
    except AssertionError:
        pass
    print("independent: realizability=%d goldcells=%d joint=(avg=1,best=3/4) "
          "showcase=(1/2,1/3) broken_rejected=True" % (n_real, n_gold))
    print("INDEPENDENT ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
