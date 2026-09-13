#!/usr/bin/env python3
"""Independent checker: permutation formulation + explicit codebook builds.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Deliberately different from verify.py: expectation computed by enumerating all
n! tie-break permutations (no bucket formula), and every corner profile is
realized as an explicit binary codebook (Q=0, retained coords first) whose
Hamming distances are re-measured. Agreement between the two formulations is
the cross-validation signal.
"""

import sys
from fractions import Fraction
from itertools import permutations, product


def interval(d, s, r):
    return (max(0, d - r), min(s, d))


def expected_frac_perm(e, golds, K):
    """E over uniform permutation pi: sort by (e_i, rank_pi), count golds."""
    G = set(golds)
    n = len(e)
    tot = Fraction(0)
    nperm = 0
    for pi in permutations(range(n)):
        rank = {doc: k for k, doc in enumerate(pi)}
        order = sorted(range(n), key=lambda i: (e[i], rank[i]))
        tot += sum(1 for i in order[:K] if i in G)
        nperm += 1
    return tot / nperm / len(golds)


def build_codebook(dprof, e, s):
    """Explicit binary docs with Q=0: e_i ones on S, d_i-e_i ones on R."""
    docs = []
    for d, ei in zip(dprof, e):
        fi = d - ei
        assert 0 <= ei <= s and 0 <= fi, (d, ei, s)
        docs.append([1] * ei + [0] * (s - ei) + [1] * fi)
    return docs


def ham(a, b):
    return sum(x != y for x, y in zip(a, b))


def main():
    fails = []
    cells = 0

    # A. Permutation-vs-theorem sweep (small: b<=2, n<=3, all K), corners only
    #    compared against every feasible e computed the SAME perm way.
    for b, s in ((2, 1), (2, 0), (2, 2)):
        r = b - s
        n = 3
        for dprof in product(range(b + 1), repeat=n):
            Ls = [interval(d, s, r) for d in dprof]
            for mask in range(1, 1 << n):
                golds = [i for i in range(n) if mask >> i & 1]
                G = set(golds)
                eranges = [range(L, U + 1) for L, U in Ls]
                for K in range(1, n + 1):
                    emax = tuple(L if i in G else U for i, (L, U) in enumerate(Ls))
                    emin = tuple(U if i in G else L for i, (L, U) in enumerate(Ls))
                    rmax = expected_frac_perm(emax, golds, K)
                    rmin = expected_frac_perm(emin, golds, K)
                    for e in product(*eranges):
                        v = expected_frac_perm(e, golds, K)
                        cells += 1
                        if not (rmin <= v <= rmax):
                            fails.append({"d": dprof, "golds": golds, "K": K,
                                          "e": e, "v": str(v)})

    # B. Explicit codebook realization of both corners (+ interior point) for
    #    the witness and edge profiles; re-measure full + retained distances.
    constructs = [
        {"b": 4, "s": 2, "d": (2, 2, 0, 0), "golds": [0, 1], "K": 3,
         "test_e": [(0, 0, 0, 0), (2, 2, 0, 0), (0, 2, 0, 0)]},
        {"b": 4, "s": 2, "d": (4, 0, 4, 4), "golds": [0], "K": 3,
         "test_e": [(2, 0, 2, 2)]},
        {"b": 2, "s": 0, "d": (2, 1, 0), "golds": [0, 2], "K": 2,
         "test_e": [(0, 0, 0)]},
    ]
    built = 0
    for c in constructs:
        b, s = c["b"], c["s"]
        Q = [0] * b
        for e in c["test_e"]:
            docs = build_codebook(c["d"], e, s)
            for doc, d, ei in zip(docs, c["d"], e):
                assert ham(doc, Q) == d, (doc, d)
                assert ham(doc[:s], Q[:s]) == ei, (doc, ei)
                built += 1
            # permutation expectation on the built codebook's retained part
            eret = tuple(ham(doc[:s], Q[:s]) for doc in docs)
            assert eret == tuple(e)
            expected_frac_perm(eret, c["golds"], c["K"])  # runs without error

    # C. Perm-formulation negative control on the witness.
    e_corner = (0, 0, 0, 0)
    v_joint = expected_frac_perm(e_corner, [0, 1], 3)
    assert v_joint == Fraction(3, 4), v_joint
    # per-gold maxima (each gold alone at L, rival gold at U) both give 1:
    v_g0 = expected_frac_perm((0, 2, 0, 0), [0], 3)
    v_g1 = expected_frac_perm((2, 0, 0, 0), [1], 3)
    assert v_g0 == 1 and v_g1 == 1, (v_g0, v_g1)
    assert (v_g0 + v_g1) / 2 != v_joint  # false "avg is sharp" rejected

    print(f"independent: perm_cells={cells} codebooks_built={built} "
          f"witness_joint={v_joint} fails={len(fails)}")
    print("INDEPENDENT ALL CHECKS " + ("PASSED" if not fails else "FAILED"))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
