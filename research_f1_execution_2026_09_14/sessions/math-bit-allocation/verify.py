#!/usr/bin/env python3
"""Bit-allocation toy checks: 96x1 vs 48x2 (and mixed) under model M-IND.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

SYNTHETIC distributions only. NOT benchmark output. Never present as benchmark output.
Stdlib only (fractions, itertools, json). Exact rational arithmetic throughout.

Model M-IND (see REPORT.md for full statement):
  - d independent coordinates; doc values from finite symmetric PMFs (exact Fractions).
  - Query FIXED at full precision (asymmetric scoring). Score estimate:
        s_hat(doc) = sum_j q_j * x_hat_j(doc_j)
    True score: s(doc) = sum_j q_j * x_j(doc_j).
  - Per-coordinate doc quantizer with b_j bits:
        0 bits: x_hat = 0 (coordinate dropped).
        1 bit : sign bit, threshold 0; level = E[X | sign region] (exact conditional mean).
        2 bits: sign + magnitude bit 1[|X| >= t]; level = E[X | region].
  - Pairwise ranking error for ordered doc pair (A=true-winner side, B=other side):
    ordered pair sampled from product law; M = s(A)-s(B), Mh = s_hat(A)-s_hat(B).
    Pairs with M == 0 are EXCLUDED (no true order). Else err = 1 if sign(Mh)!=sign(M),
    1/2 if Mh == 0 (random-tie-break expectation; mirrors frozen fractional protocol).
        P_err = sum(w*err) / sum(w[M != 0]).
  - MSE(doc) = sum_j E[(X_j - X_hat_j)^2] (unweighted) and query-weighted S(b).
  - Payload budget B = sum b_j (doc payload bits). Threshold values / shared metadata
    are charged SEPARATELY (see metadata_accounting()).

Setups:
  Setup A (LOSS regime + counterexample to 'always allocate to highest variance'):
    d=2, budget 2. H quaternary {+-3,+-1} (var 5), L binary {+-1/2} (var 1/4),
    q = (1/100, 1). Compare (1,1) spread vs (2,0) concentrate-on-H vs (0,2).
  Setup B (GAIN regime): d=3, budget 3. C1 quaternary (var 5), C2 {+-3/2} (var 9/4),
    C3 {+-1/10} (var 1/100), q=(1,1,1). Compare (1,1,1) vs (2,1,0).
"""

from fractions import Fraction as F
from itertools import product
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json")


# ---------------------------------------------------------------- pmfs
def pmf_quaternary():
    # values +-3, +-1 each w.p. 1/4. E[X^2] = (9+1+1+9)/4 = 5.
    return [(-3, F(1, 4)), (-1, F(1, 4)), (1, F(1, 4)), (3, F(1, 4))]


def pmf_binary(half):
    # values +-half w.p. 1/2. Var = half^2.
    h = F(half)
    return [(-h, F(1, 2)), (h, F(1, 2))]


# ---------------------------------------------------------------- quantizer
def quantize_levels(pmf, bits, t=F(2)):
    """Return dict value -> reconstruction level (exact Fraction)."""
    if bits == 0:
        return {v: F(0) for (v, _) in pmf}
    if bits == 1:
        pos = [(v, p) for (v, p) in pmf if v > 0]
        neg = [(v, p) for (v, p) in pmf if v < 0]
        zero = [(v, p) for (v, p) in pmf if v == 0]
        if not pos or not neg:
            raise ValueError("1-bit needs both signs in support")
        mp = sum(v * p for (v, p) in pos) / sum(p for (_, p) in pos)
        mn = sum(v * p for (v, p) in neg) / sum(p for (_, p) in neg)
        out = {}
        for (v, _) in pmf:
            out[v] = mp if v > 0 else mn
        for (v, _) in zero:
            out[v] = F(0)
        return out
    if bits == 2:
        # regions: {x<=-t}, {-t<x<0}, {0<x<t}, {x>=t}; level = conditional mean.
        out = {}
        for (v, _) in pmf:
            if v >= t:
                key = "hp"
            elif v > 0:
                key = "lp"
            elif v > -t:
                key = "ln"
            else:
                key = "hn"
            regs_key = key
            out[v] = regs_key
        # conditional means per region
        mass = {}
        for (v, p) in pmf:
            k = out[v]
            if k not in mass:
                mass[k] = [F(0), F(0)]
            mass[k][0] += v * p
            mass[k][1] += p
        mean = {k: (num / den if den != 0 else F(0)) for k, (num, den) in mass.items()}
        return {v: mean[out[v]] for (v, _) in pmf}
    raise ValueError("bits must be 0, 1 or 2")


# ---------------------------------------------------------------- metrics
def coord_mse(pmf, bits, t=F(2)):
    lv = quantize_levels(pmf, bits, t)
    return sum(p * (v - lv[v]) ** 2 for (v, p) in pmf)


def total_mse(pmfs, alloc, t=F(2)):
    return sum(coord_mse(p, b, t) for (p, b) in zip(pmfs, alloc))


def weighted_mse(pmfs, q, alloc, t=F(2)):
    # surrogate S(b) = sum_j q_j^2 e_j(b_j)
    return sum((qq ** 2) * coord_mse(p, b, t) for (p, qq, b) in zip(pmfs, q, alloc))


def pairwise_error(pmfs, q, alloc, t=F(2)):
    """Exact P_err by exhaustive enumeration. Returns (num, den, value)."""
    supps = [[v for (v, _) in p] for p in pmfs]
    prob = [{v: p for (v, p) in pm} for pm in pmfs]
    lvls = [quantize_levels(p, b, t) for (p, b) in zip(pmfs, alloc)]
    num = F(0)
    den = F(0)
    for A in product(*supps):
        wA = F(1)
        for j, a in enumerate(A):
            wA *= prob[j][a]
        for B in product(*supps):
            w = wA
            for j, b in enumerate(B):
                w *= prob[j][b]
            M = sum(qq * (a - b) for (qq, a, b) in zip(q, A, B))
            if M == 0:
                continue
            den += w
            Mh = sum(q[j] * (lvls[j][A[j]] - lvls[j][B[j]]) for j in range(len(q)))
            if Mh == 0:
                num += w / 2
            elif (Mh > 0) != (M > 0):
                num += w
    return num, den, (num / den if den != 0 else None)


def frac_str(x):
    return str(x) if x is None else "%s (%s)" % (x, float(x))


def main():
    checks = []
    out = {"labels": ["[LOCAL EXPLORATORY PILOT]", "[NOT PREREGISTERED]",
                       "[NOT FOR CITATION]", "[DISCLOSE-BEFORE-USE]"],
           "synthetic_note": "All distributions SYNTHETIC toy PMFs. NOT benchmark output.",
           "model": "M-IND: independent coords, fixed full-precision query, asymmetric "
                    "inner-product scoring, tie=1/2, true-ties excluded.",
           "setups": {}}

    # ================= Setup A =================
    H = pmf_quaternary()
    L = pmf_binary(F(1, 2))
    pmfsA = [H, L]
    qA = [F(1, 100), F(1)]
    resA = {}
    for alloc in [(1, 1), (2, 0), (0, 2), (1, 0), (0, 1), (0, 0), (2, 1), (1, 2)]:
        n, d, v = pairwise_error(pmfsA, qA, alloc)
        m = total_mse(pmfsA, alloc)
        s = weighted_mse(pmfsA, qA, alloc)
        resA[str(alloc)] = {"P_num": str(n), "P_den": str(d), "P_err": str(v),
                            "P_float": float(v), "MSE": str(m), "MSE_float": float(m),
                            "S_surrogate": str(s), "S_float": float(s)}
    out["setups"]["A_loss_regime"] = {
        "desc": "d=2,budget=2; H={+-3,+-1} var=5; L={+-1/2} var=1/4; q=(1/100,1).",
        "allocs": resA}

    def A(alloc):
        return resA[str(alloc)]

    # A1: MSE prefers concentration on high-variance coord.
    checks.append(("A1_MSE_prefers_2_0",
                   total_mse(pmfsA, (2, 0)) < total_mse(pmfsA, (1, 1)),
                   "MSE(2,0)=%s < MSE(1,1)=%s" % (A((2, 0))["MSE"], A((1, 1))["MSE"])))
    # A2: ranking prefers spread (1/14 via same-sign-conflation ties vs 2/7).
    p11 = F(resA["(1, 1)"]["P_num"]) / F(resA["(1, 1)"]["P_den"])
    p20 = F(resA["(2, 0)"]["P_num"]) / F(resA["(2, 0)"]["P_den"])
    checks.append(("A2_rank_prefers_1_1", p11 == F(1, 14) and p20 > p11,
                   "P(1,1)=%s vs P(2,0)=%s" % (A((1, 1))["P_err"], A((2, 0))["P_err"])))
    # A3: dropping the HIGH-variance coord beats upgrading it.
    checks.append(("A3_drop_H_beats_upgrade_H",
                   A((0, 2))["P_float"] < A((2, 0))["P_float"],
                   "P(0,2)=%s < P(2,0)=%s" % (A((0, 2))["P_err"], A((2, 0))["P_err"])))
    # A4: exact predicted value P(2,0) == 2/7.
    n, d, v = pairwise_error(pmfsA, qA, (2, 0))
    checks.append(("A4_P20_equals_2_over_7", v == F(2, 7), "P(2,0)=%s" % v))
    # A5: threshold robustness — any t in (1,3) keeps 2-bit lossless -> identical errors.
    robust = True
    for t in [F(3, 2), F(2), F(5, 2)]:
        _, _, v2 = pairwise_error(pmfsA, qA, (2, 0), t)
        _, _, w2 = pairwise_error(pmfsA, qA, (1, 1), t)
        if not (v2 == v and w2 == F(1, 14)):
            robust = False
    checks.append(("A5_threshold_robust_t_in_(1,3)", robust,
                   "t=3/2,2,5/2 all give P(2,0)=2/7, P(1,1)=1/14"))
    # A6: greedy-by-MV from zero does NOT fall into the variance trap.
    p00 = pairwise_error(pmfsA, qA, (0, 0))[2]
    p10 = pairwise_error(pmfsA, qA, (1, 0))[2]
    p01 = pairwise_error(pmfsA, qA, (0, 1))[2]
    mvH0 = p00 - p10
    mvL0 = p00 - p01
    checks.append(("A6_greedy_MV_picks_L_first", mvL0 > mvH0,
                   "MV_L(0,0)=%s > MV_H(0,0)=%s" % (mvL0, mvH0)))
    out["setups"]["A_loss_regime"]["greedy_MV_from_zero"] = {
        "P(0,0)": str(p00), "P(1,0)": str(p10), "P(0,1)": str(p01),
        "MV_H": str(mvH0), "MV_L": str(mvL0)}

    # ================= Setup B =================
    C1 = pmf_quaternary()            # var 5
    C2 = pmf_binary(F(3, 2))         # +-3/2, var 9/4
    C3 = pmf_binary(F(1, 10))        # +-1/10, var 1/100
    pmfsB = [C1, C2, C3]
    qB = [F(1), F(1), F(1)]
    resB = {}
    for alloc in [(1, 1, 1), (2, 1, 0), (2, 0, 1), (1, 2, 0), (0, 2, 1)]:
        n, d, v = pairwise_error(pmfsB, qB, alloc)
        m = total_mse(pmfsB, alloc)
        resB[str(alloc)] = {"P_num": str(n), "P_den": str(d), "P_err": str(v),
                            "P_float": float(v), "MSE": str(m), "MSE_float": float(m)}
    out["setups"]["B_gain_regime"] = {
        "desc": "d=3,budget=3; C1={+-3,+-1} var=5; C2={+-3/2} var=9/4; "
                "C3={+-1/10} var=1/100; q=(1,1,1).",
        "allocs": resB}
    # B1: exact predicted values P(1,1,1)=1/10, P(2,1,0)=1/30.
    nB, dB, vB = pairwise_error(pmfsB, qB, (1, 1, 1))
    nC, dC, vC = pairwise_error(pmfsB, qB, (2, 1, 0))
    checks.append(("B1_P111_equals_1_over_10", vB == F(1, 10), "P(1,1,1)=%s" % vB))
    checks.append(("B2_P210_equals_1_over_30", vC == F(1, 30), "P(2,1,0)=%s" % vC))
    # B3: concentration wins ranking here (gain regime).
    checks.append(("B3_concentration_wins_ranking", vC < vB,
                   "P(2,1,0)=%s < P(1,1,1)=%s" % (vC, vB)))

    # ================= metadata accounting (no fake 12-byte claim) =================
    out["metadata_accounting"] = {
        "rule": "Doc payload bits B=sum b_j. Every coord with b_j=2 needs one "
                "magnitude threshold t_j; every coded coord needs its index "
                "mapping. These live OUTSIDE the payload and must be reported.",
        "setupA_(1,1)": {"payload_bits": 2, "thresholds": 0, "shared_bits": 0},
        "setupA_(2,0)": {"payload_bits": 2, "thresholds": 1,
                         "shared_bits": "T (threshold precision, e.g. 8-bit log-quantized "
                                        "or 32-bit float) + index of upgraded coord"},
        "setupB_(1,1,1)": {"payload_bits": 3, "thresholds": 0, "shared_bits": 0},
        "setupB_(2,1,0)": {"payload_bits": 3, "thresholds": 1, "shared_bits": "T + index map"},
        "scale_note": "48x2-bit at 96 payload bits needs 48 thresholds (or 1 global t "
                      "plus the decision to share it); 96x1 needs 0. A '12-byte' claim "
                      "that omits this is incomplete accounting."
    }

    out["checks"] = [{"name": n, "pass": bool(ok), "detail": det}
                     for (n, ok, det) in checks]
    out["all_pass"] = all(bool(ok) for (_, ok, _) in checks)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    print("=== bit-allocation toy verification ===")
    for (n, ok, det) in checks:
        print(("PASS " if ok else "FAIL ") + n + " :: " + det)
    print("ALL_PASS =", out["all_pass"])
    print("wrote", OUT)
    if not out["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
