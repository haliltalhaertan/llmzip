#!/usr/bin/env python3
"""Greedy-allocation replacement theory: exact finite verification (stdlib only).

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

SYNTHETIC toy PMFs only. NOT benchmark output.

Model M-IND: d independent coords, fixed full-precision query q, asymmetric
inner-product scoring s_hat = sum q_j x_hat_j, b_j in {0,1,2} with
conditional-mean decoders (0 -> 0; 1 -> E[X|sign]; 2 -> E[X|region] with
threshold t). Pairwise ORDER error: estimated tie counts 1/2, true ties
excluded from the denominator.

Two INDEPENDENT exact paths (cross-checked on every allocation):
  Path A: double loop over ordered doc pairs (A,B).
  Path B: per-coordinate gap-law convolution -> joint law of (M, Mhat).
Both use exact Fractions; no floating point in any computation.

Fail-closed: any mismatch -> FAIL + nonzero exit. A deliberately corrupted
score table is validated and must be REJECTED (fail-closed demonstration).
"""
from fractions import Fraction as F
from itertools import product
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json")
T = F(2)

CHECKS = []


def check(name, ok, detail):
    CHECKS.append({"name": name, "pass": bool(ok), "detail": detail})
    print(("PASS " if ok else "FAIL ") + name + " :: " + detail)


# ---------------------------------------------------------- model
# Main ranking-error instance G*: C1 sparse, C2 +-3/2, C3 +-1/10, q=(1,1,1).
C1 = [(-10, F(1, 20)), (-1, F(9, 20)), (1, F(9, 20)), (10, F(1, 20))]
C2 = [(-F(3, 2), F(1, 2)), (F(3, 2), F(1, 2))]
C3 = [(-F(1, 10), F(1, 2)), (F(1, 10), F(1, 2))]
PMFS = [C1, C2, C3]
Q = [F(1), F(1), F(1)]

# Separable-MSE instance: Q4 = quaternary (diminishing), S10 = sparse (increasing).
Q4 = [(-3, F(1, 4)), (-1, F(1, 4)), (1, F(1, 4)), (3, F(1, 4))]
S10 = C1


def levels(pmf, bits, t=T):
    if bits == 0:
        return {v: F(0) for (v, _) in pmf}
    if bits == 1:
        pos = [(v, p) for (v, p) in pmf if v > 0]
        neg = [(v, p) for (v, p) in pmf if v < 0]
        mp = sum(v * p for (v, p) in pos) / sum(p for (_, p) in pos)
        mn = sum(v * p for (v, p) in neg) / sum(p for (_, p) in neg)
        return {v: (mp if v > 0 else (mn if v < 0 else F(0))) for (v, _) in pmf}
    reg = {}
    for (v, _) in pmf:
        if v >= t:
            reg[v] = 'hp'
        elif v > 0:
            reg[v] = 'lp'
        elif v > -t:
            reg[v] = 'ln'
        else:
            reg[v] = 'hn'
    mass = {}
    for (v, p) in pmf:
        k = reg[v]
        mass.setdefault(k, [F(0), F(0)])
        mass[k][0] += v * p
        mass[k][1] += p
    mean = {k: (n / d if d else F(0)) for k, (n, d) in mass.items()}
    return {v: mean[reg[v]] for (v, _) in pmf}


def err_pathA(pmfs, q, alloc, t=T):
    """Ordered doc-pair double loop. Returns (num, den, value)."""
    supps = [[v for (v, _) in p] for p in pmfs]
    prob = [{v: p for (v, p) in pm} for pm in pmfs]
    lv = [levels(p, b, t) for (p, b) in zip(pmfs, alloc)]
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
            Mh = sum(q[j] * (lv[j][A[j]] - lv[j][B[j]]) for j in range(len(q)))
            if Mh == 0:
                num += w / 2
            elif (Mh > 0) != (M > 0):
                num += w
    return num, den, (num / den if den != 0 else None)


def err_pathB(pmfs, q, alloc, t=T):
    """Gap-law convolution. Returns (num, den, value)."""
    joint = {(F(0), F(0)): F(1)}
    for j, (pmf, b) in enumerate(zip(pmfs, alloc)):
        lv = levels(pmf, b, t)
        gap = {}
        for (a, pa) in pmf:
            for (b2, pb) in pmf:
                key = (q[j] * (a - b2), q[j] * (lv[a] - lv[b2]))
                gap[key] = gap.get(key, F(0)) + pa * pb
        new = {}
        for (M, Mh), m in joint.items():
            for (d, dh), md in gap.items():
                key = (M + d, Mh + dh)
                new[key] = new.get(key, F(0)) + m * md
        joint = new
    num = F(0)
    den = F(0)
    for (M, Mh), m in joint.items():
        if M == 0:
            continue
        den += m
        if Mh == 0:
            num += m / 2
        elif (Mh > 0) != (M > 0):
            num += m
    return num, den, (num / den if den != 0 else None)


def mse(pmf, bits, t=T):
    lv = levels(pmf, bits, t)
    return sum(p * (v - lv[v]) ** 2 for (v, p) in pmf)


def Stot(pmfs, qq, alloc, t=T):
    return sum(qj * qj * mse(p, b, t) for (p, qj, b) in zip(pmfs, qq, alloc))


def validate_scores(scores, tag):
    """Independent validator: recompute every allocation via Path B
    (gap convolution) and require exact string match. Fail-closed."""
    nodes = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 2, 0),
             (1, 1, 0), (0, 1, 1), (0, 1, 2), (0, 2, 1), (1, 0, 2),
             (1, 1, 1), (1, 2, 0), (2, 0, 1), (2, 1, 0)]
    for a in nodes:
        _, _, v = err_pathB(PMFS, Q, a)
        if scores.get(str(a)) != str(v):
            print("validator[%s]: MISMATCH at %s: got %s, want %s"
                  % (tag, a, scores.get(str(a)), v))
            return False
    return True


def greedy_P(pmfs, q, B, t=T):
    """Fixed-budget greedy by largest one-step P_err decrease.
    Returns (final, steps, all_strict) where steps = (from, pick, mv, all_mvs)."""
    G = [0] * len(pmfs)
    steps = []
    for _ in range(B):
        pG = err_pathA(pmfs, q, tuple(G), t)[2]
        cands = []
        for j in range(len(pmfs)):
            if G[j] < 2:
                G2 = list(G)
                G2[j] += 1
                cands.append((pG - err_pathA(pmfs, q, tuple(G2), t)[2], j))
        cands.sort(key=lambda x: -x[0])
        strict = len(cands) < 2 or cands[0][0] != cands[1][0]
        steps.append((tuple(G), cands[0][1], cands[0][0],
                      [(j, mv) for (mv, j) in cands], strict))
        G[cands[0][1]] += 1
    return tuple(G), steps


def main():
    out = {"labels": ["[LOCAL EXPLORATORY PILOT]", "[NOT PREREGISTERED]",
                      "[NOT FOR CITATION]", "[DISCLOSE-BEFORE-USE]"],
           "synthetic_note": "All distributions SYNTHETIC toy PMFs. NOT benchmark output.",
           "model": "M-IND: independent coords, fixed full-precision query, "
                    "asymmetric inner-product scoring, tie=1/2, true ties excluded."}

    # ================= PART 1: strict greedy failure on P_err =================
    nodes = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 2, 0),
             (1, 1, 0), (0, 1, 1), (0, 1, 2), (0, 2, 1), (1, 0, 2),
             (1, 1, 1), (1, 2, 0), (2, 0, 1), (2, 1, 0)]
    tab = {}
    agree = True
    for a in nodes:
        nA, dA, vA = err_pathA(PMFS, Q, a)
        nB, dB, vB = err_pathB(PMFS, Q, a)
        if not (nA == nB and dA == dB and vA == vB):
            agree = False
        tab[str(a)] = {"P_num": str(nA), "P_den": str(dA), "P_err": str(vA)}
    out["main_instance"] = {
        "desc": "C1={+-10 w.p.1/20, +-1 w.p.9/20} (sparse); C2={+-3/2}; "
                "C3={+-1/10}; q=(1,1,1); t=2. docs=16, ordered pairs=256.",
        "allocs": tab}
    check("G0_paths_agree_all_14_nodes", agree,
          "PathA (pair loop) == PathB (gap convolution) on all 14 allocations")

    def P(a):
        return F(tab[str(a)]["P_num"]) / F(tab[str(a)]["P_den"])

    # Exact headline values (hand-derived in REPORT.md).
    check("G1_denom_true_ties", F(tab["(0, 0, 0)"]["P_den"]) == F(359, 400),
          "denominator mass = 359/400 (true-tie mass 41/400)")
    check("G2_P000_is_half", P((0, 0, 0)) == F(1, 2), "P(0,0,0)=1/2, got %s" % P((0, 0, 0)))
    check("G3_P210_is_41_over_718", P((2, 1, 0)) == F(41, 718),
          "P(2,1,0)=41/718, got %s" % P((2, 1, 0)))
    check("G4_P111_is_117_over_718", P((1, 1, 1)) == F(117, 718),
          "P(1,1,1)=117/718, got %s" % P((1, 1, 1)))

    # Greedy trace with STRICT decisions (no tie artifact).
    G, steps = greedy_P(PMFS, Q, 3)
    out["greedy_trace"] = [
        {"from": str(fr), "pick": pk, "MV": str(mv),
         "contenders": [(j, str(m)) for (j, m) in allm], "strict": st}
        for (fr, pk, mv, allm, st) in steps]
    exp_picks = [1, 2, 0]
    exp_MVs = [F(163, 718), F(41, 718), F(19, 359)]
    ok_steps = ([pk for (_, pk, _, _, _) in steps] == exp_picks and
                [mv for (_, _, mv, _, _) in steps] == exp_MVs and
                all(st for (_, _, _, _, st) in steps) and G == (1, 1, 1))
    check("G5_greedy_path_strict_to_111", ok_steps,
          "picks [C2,C3,C1] MVs 163/718,41/718,19/359 all strict; final=(1,1,1)")

    # Global optimum over all 7 budget-3 allocations: unique (2,1,0).
    b3 = [a for a in product([0, 1, 2], repeat=3) if sum(a) == 3]
    b3v = {a: err_pathA(PMFS, Q, a)[2] for a in b3}
    bopt = min(b3v.values())
    opts = [a for (a, v) in b3v.items() if v == bopt]
    out["budget3_table"] = {str(a): str(v) for (a, v) in b3v.items()}
    check("G6_unique_global_opt_210", opts == [(2, 1, 0)] and bopt == F(41, 718),
          "opts=%s value=%s" % (opts, bopt))
    check("G7_greedy_strictly_suboptimal", b3v[G] - bopt == F(38, 359),
          "P(greedy)-P(opt)=117/718-41/718=38/359 > 0")

    # Secondary witness d=2: (Q4, S10), q=(3,2), B=3. Last step forced: disclosed.
    Q2 = [F(3), F(2)]
    PM2 = [Q4, S10]
    G2, steps2 = greedy_P(PM2, Q2, 3)
    b3b = [a for a in product([0, 1, 2], repeat=2) if sum(a) == 3]
    b3bv = {a: err_pathA(PM2, Q2, a)[2] for a in b3b}
    opt2 = min(b3bv.values())
    opts2 = [a for (a, v) in b3bv.items() if v == opt2]
    # cross-check secondary witness with path B as well
    agree2 = all(err_pathA(PM2, Q2, a)[2] == err_pathB(PM2, Q2, a)[2] for a in b3b)
    out["secondary_d2"] = {
        "desc": "Q4={+-3,+-1} uniform; S10 sparse as above; q=(3,2); t=2; B=3.",
        "greedy": str(G2),
        "steps": [{"from": str(fr), "pick": pk, "MV": str(mv), "strict": st}
                  for (fr, pk, mv, _, st) in steps2],
        "table": {str(a): str(v) for (a, v) in b3bv.items()}}
    check("G8_d2_witness_paths_agree", agree2, "PathA==PathB on d=2 witness")
    check("G9_d2_greedy_suboptimal", G2 == (2, 1) and opts2 == [(1, 2)] and
          b3bv[(2, 1)] == F(213, 1427) and opt2 == F(163, 1427),
          "greedy=(2,1) P=213/1427; opt=(1,2) P=163/1427; steps0-1 strict, step2 forced")

    # ================= PART 2: separable query-weighted MSE =================
    eQ = [mse(Q4, b) for b in (0, 1, 2)]
    eS = [mse(S10, b) for b in (0, 1, 2)]
    out["mse_gains"] = {"quat_e": [str(e) for e in eQ],
                        "sparse_e": [str(e) for e in eS],
                        "quat_gains": [str(eQ[0] - eQ[1]), str(eQ[1] - eQ[2])],
                        "sparse_gains": [str(eS[0] - eS[1]), str(eS[1] - eS[2])]}
    check("S1_quat_diminishing", eQ == [F(5), F(1), F(0)],
          "e=(5,1,0) gains 4>=1")
    check("S2_sparse_increasing_REALIZABLE", eS == [F(109, 10), F(729, 100), F(0)],
          "e=(109/10,729/100,0) gains 361/100 < 729/100: diminishing FAILS "
          "for a real conditional-mean quantizer")
    gA = (F(5), F(100))
    gB = (F(6), F(6))
    val = lambda ab: (gA[0] if ab[0] >= 1 else F(0)) + (gA[1] if ab[0] >= 2 else F(0)) + \
                     (gB[0] if ab[1] >= 1 else F(0)) + (gB[1] if ab[1] >= 2 else F(0))
    check("S3_abstract_separable_failure", val((0, 2)) == F(12) and val((2, 0)) == F(105),
          "abstract gains A=(5,100) B=(6,6): greedy step1 B(6>5), step2 B(6>5) "
          "-> (0,2)=12 < OPT (2,0)=105")
    PMQ = [Q4, S10]
    QQ = [F(1), F(1)]
    all2 = [a for a in product([0, 1, 2], repeat=2) if sum(a) == 2]
    Sv = {a: Stot(PMQ, QQ, a) for a in all2}
    out["realizable_S_failure"] = {str(a): str(v) for (a, v) in Sv.items()}
    sG = [0, 0]
    for _ in range(2):
        s0 = Stot(PMQ, QQ, tuple(sG))
        mv = []
        for j in (0, 1):
            if sG[j] < 2:
                G2x = list(sG)
                G2x[j] += 1
                mv.append((s0 - Stot(PMQ, QQ, tuple(G2x)), j))
        mv.sort(key=lambda x: -x[0])
        sG[mv[0][1]] += 1
    check("S4_realizable_S_greedy_fails_strict",
          tuple(sG) == (1, 1) and Sv[(1, 1)] == F(829, 100) and
          min(Sv.values()) == F(5) and Sv[(0, 2)] == F(5),
          "greedy: step0 Q(4>361/100 strict), step1 S(361/100>1 strict) -> "
          "(1,1)=829/100; OPT (0,2)=5")

    # ================= PART 3: shared-cost ledger =================
    L1 = levels(C1, 1)
    L2 = levels(C1, 2)
    lv1_vals = sorted(set(L1.values()), key=float)
    lv2_vals = sorted(set(L2.values()), key=float)
    out["decoder_ledger"] = {
        "C1_1bit_levels": [str(v) for v in lv1_vals],
        "C1_2bit_region_means": [str(v) for v in lv2_vals],
        "C2_C3_binary_exact_at_1bit": True,
        "alloc_(2,1,0)": {"payload_bits": 3, "thresholds": ["t_C1"],
                          "level_values": len(lv2_vals) + 1 + 1,
                          "index_map": "which coord upgraded (2-of-3 subset)"},
        "alloc_(1,1,1)": {"payload_bits": 3, "thresholds": [],
                          "level_values": 1 + 1 + 1,
                          "index_map": "none (uniform 1 bit)"}}
    check("C1_ledger_levels", lv1_vals == [F(-19, 10), F(19, 10)] and
          lv2_vals == [F(-10), F(-1), F(1), F(10)] and
          levels(C2, 1) == {-F(3, 2): -F(3, 2), F(3, 2): F(3, 2)},
          "1-bit C1 needs +-19/10 stored; 2-bit needs 4 region means + t")

    # ================= PART 4: fail-closed corruption test =================
    expected = {a: tab[a]["P_err"] for a in tab}
    corrupted = dict(expected)
    corrupted["(2, 1, 0)"] = "42/718"  # perturbed optimum entry
    rej = validate_scores(corrupted, "corrupted")
    acc = validate_scores(expected, "expected")
    check("C2_corrupt_table_rejected", rej is False,
          "perturbed P(2,1,0)=42/718 rejected by validator")
    check("C3_true_table_accepted", acc is True, "true table accepted")
    out["corruption_test"] = {"corrupted_rejected": rej is False,
                              "true_accepted": acc is True}

    out["model_spec"] = {
        "supports": [[[str(v), str(p)] for (v, p) in pmf] for pmf in PMFS],
        "query": [str(x) for x in Q],
        "threshold": str(T),
        "quat_support": [[str(v), str(p)] for (v, p) in Q4]}
    out["coverage"] = {
        "main_nodes_double_path": len(nodes),
        "main_ordered_pairs_per_alloc": 256,
        "budget3_allocs_enumerated": len(b3),
        "d2_witness_allocs": len(b3b),
        "S_allocs_enumerated": len(all2)}
    out["checks"] = CHECKS
    out["all_pass"] = all(c["pass"] for c in CHECKS)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    print("ALL_PASS =", out["all_pass"])
    print("wrote", OUT)
    if not out["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()