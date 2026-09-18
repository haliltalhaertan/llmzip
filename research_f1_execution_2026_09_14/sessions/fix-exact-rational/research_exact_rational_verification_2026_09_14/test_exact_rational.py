# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""Adversarial synthetic tests for binding 8 (exact-rational sign classification).

SYNTHETIC INPUTS ONLY — every value below is authored in this file. No real corpus,
query, gold label, embedding, HMAC key, or authorization is used or needed: the vendored
module is imported by path and only its pure functions (sign, mean_fraction, d_contrast,
denominator_bound, classify_primary, rational_payload, summarize_subset,
sensitivity_discordance, parse_cell) are called. The module's main() entry point, which
demands the sealed cohort + 96 archive CSVs, is NEVER invoked (fail-closed; see PROVENANCE.md).

Oracle: fractions.Fraction expectations written by hand in this file. The implementation is
never its own oracle: each case asserts an independently computed Fraction/sign/category,
AND (for discriminating cases) asserts that a deliberately float-based classifier gets it
WRONG. If the float control ever agrees everywhere, the suite exits nonzero as "too weak".

Run:  python3 test_exact_rational.py
Writes: evidence/results.json   Exit 0 = all exact checks pass AND float control fails >=3.
"""
from __future__ import annotations

import datetime
import hashlib
import importlib.util
import json
import platform
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ANALYZER = HERE / "vendored" / "t4f1_exact_rational_outcome_analysis.py"
RESULTS = HERE / "evidence" / "results.json"
TIERS = ("100K", "500K", "1M", "10M")


def load_module():
    spec = importlib.util.spec_from_file_location("vendored_exact_rational", ANALYZER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load vendored analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# ---- Deliberately FLOAT-based negative control (the violation model) ----
def float_sign(x: Fraction) -> int:
    f = float(x)
    return 1 if f > 0 else (-1 if f < 0 else 0)


def float_classify(primary: dict) -> str:
    signs = [float_sign(primary[t]) for t in TIERS]
    if all(s > 0 for s in signs):
        return "FULL_REPLICATION"
    if all(s <= 0 for s in signs):
        return "NO_REPLICATION"
    return "HETEROGENEOUS_PARTIAL_REPLICATION"


def float_mean_naive_fold(values: list) -> float:
    # Naive hand-rolled float accumulator (acc += float(v) left to right) — the pattern a
    # float-based D_t aggregator would use. NOTE: builtin sum() is NOT used here because on
    # modern CPython it applies compensated summation that masks order effects (VERIFIED on
    # Python 3.14.4: builtin sum gives 0.0333... for all three orders below, while the naive
    # fold gives 0.0 for order A and 0.0333... for orders B/C).
    acc = 0.0
    for v in values:
        acc += float(v)
    return acc / len(values)


def main() -> int:
    a = load_module()
    cases: list = []
    failures = 0

    def check(label: str, observed, expected, discriminating: bool = False,
              float_observed=None, float_should_differ: bool = False) -> None:
        nonlocal failures
        ok = observed == expected
        entry = {"label": label, "expected": str(expected), "observed": str(observed),
                 "pass": bool(ok)}
        if float_observed is not None:
            entry["float_control_observed"] = str(float_observed)
        if ok:
            print(f"ok   {label}: {observed}")
        else:
            print(f"FAIL {label}: observed={observed} expected={expected}")
            failures += 1
        if float_should_differ:
            entry["float_control_differs"] = (float_observed != expected)
            if float_observed == expected:
                print(f"FAIL {label}: float control AGREED ({float_observed}) — test too weak")
                failures += 1
            else:
                print(f"ok   {label}: float control wrong as required ({float_observed})")
        cases.append(entry)

    tiny_pos = Fraction(1, 10 ** 400)   # float() == 0.0  (VERIFIED below)
    tiny_neg = Fraction(-1, 10 ** 400)  # float() == -0.0 (== 0.0)
    assert float(tiny_pos) == 0.0, "pilot assumption broken: tiny_pos not 0.0 in float"
    assert float(tiny_neg) == 0.0, "pilot assumption broken: tiny_neg not 0.0 in float"
    assert float(Fraction(2, 10 ** 400)) == 0.0, "pilot assumption broken"
    print("ok   pilot assumption: float(1e-400-class rationals) == 0.0")

    # T1 — tiny positive must stay positive (would-be violation: rounded to 0.0 -> tie)
    p1 = {t: tiny_pos for t in TIERS}
    check("T1 tiny-positive D_t all tiers -> FULL_REPLICATION",
          a.classify_primary(p1), "FULL_REPLICATION",
          float_observed=float_classify(p1), float_should_differ=True)
    check("T1b sign(tiny_pos) == +1", a.sign(tiny_pos), 1,
          float_observed=float_sign(tiny_pos), float_should_differ=True)

    # T2 — tiny negative must stay negative
    p2 = {t: tiny_neg for t in TIERS}
    check("T2 tiny-negative D_t all tiers -> NO_REPLICATION",
          a.classify_primary(p2), "NO_REPLICATION")
    check("T2b sign(tiny_neg) == -1", a.sign(tiny_neg), -1)

    # T3 — exact tie is a tie, never nudged; zero joins the <= 0 side
    check("T3a sign(0) == 0", a.sign(Fraction(0, 1)), 0)
    p3 = {"100K": Fraction(1, 7), "500K": Fraction(0, 1),
          "1M": Fraction(-1, 7), "10M": Fraction(2, 11)}
    check("T3b mixed profile incl. exact zero -> HETEROGENEOUS_PARTIAL_REPLICATION",
          a.classify_primary(p3), "HETEROGENEOUS_PARTIAL_REPLICATION")
    check("T3c all-zero tiers -> NO_REPLICATION (zero is not positive)",
          a.classify_primary({t: Fraction(0, 1) for t in TIERS}), "NO_REPLICATION")
    check("T3d three positives + one exact zero -> HETEROGENEOUS (zero flips Full)",
          a.classify_primary({"100K": Fraction(1, 3), "500K": Fraction(1, 5),
                              "1M": Fraction(1, 7), "10M": Fraction(0, 1)}),
          "HETEROGENEOUS_PARTIAL_REPLICATION")
    check("T3e canceling pair mean is exactly 0",
          a.d_contrast([{"delta": Fraction(1, 3)}, {"delta": Fraction(-1, 3)}]),
          Fraction(0, 1))

    # T4 — tiers differing only below float64 resolution: float sees equality, exact does not
    d_a, d_b = tiny_pos, 2 * tiny_pos
    check("T4a exact rationals below float resolution are distinguished",
          (d_b - d_a) > 0 and a.sign(d_b - d_a) == 1, True)
    check("T4b float cannot distinguish them (hazard is real)",
          float(d_a) == float(d_b), True)
    p4 = {"100K": d_a, "500K": d_b, "1M": Fraction(1, 9), "10M": Fraction(1, 9)}
    check("T4c sub-float-resolution positives -> FULL_REPLICATION",
          a.classify_primary(p4), "FULL_REPLICATION",
          float_observed=float_classify(p4), float_should_differ=True)

    # T5/T6 — summation ORDER changes the float result but not the exact result
    vals = [Fraction(1, 10), Fraction(10 ** 16), Fraction(-10 ** 16)]
    orders = [list(vals), list(reversed(vals)), [vals[1], vals[2], vals[0]]]
    exact_means = [a.mean_fraction(o) for o in orders]
    check("T5a exact mean order-invariant == 1/30",
          all(m == Fraction(1, 30) for m in exact_means), True)
    float_means = [float_mean_naive_fold(o) for o in orders]
    check("T5b float mean differs by order (hazard is real)",
          len(set(float_means)) > 1, True)
    print(f"     float order means: {float_means}  exact: {exact_means[0]}")
    check("T5c exact sign of order-sensitive mean == +1",
          a.sign(exact_means[0]), 1)
    big_cancel = [Fraction(10 ** 16), Fraction(1, 3), Fraction(-10 ** 16)]
    check("T5d cancellation order-invariant == 1/9",
          a.mean_fraction(big_cancel) == a.mean_fraction(list(reversed(big_cancel))) == Fraction(1, 9),
          True)

    # T7 — replication-category boundaries at ordinary magnitudes (prereg §6)
    check("T7a all-positive -> FULL_REPLICATION",
          a.classify_primary({t: Fraction(1, 7) for t in TIERS}), "FULL_REPLICATION")
    check("T7b all-non-positive (zeros + negatives) -> NO_REPLICATION",
          a.classify_primary({"100K": Fraction(0, 1), "500K": Fraction(-1, 5),
                              "1M": Fraction(-2, 3), "10M": Fraction(0, 1)}),
          "NO_REPLICATION")
    check("T7c mixed signs -> HETEROGENEOUS_PARTIAL_REPLICATION",
          a.classify_primary({"100K": Fraction(1, 1), "500K": Fraction(0, 1),
                              "1M": Fraction(-1, 1), "10M": Fraction(2, 1)}),
          "HETEROGENEOUS_PARTIAL_REPLICATION")
    check("T7d single negative among positives -> HETEROGENEOUS",
          a.classify_primary({"100K": Fraction(1, 3), "500K": Fraction(1, 3),
                              "1M": Fraction(-1, 10 ** 30), "10M": Fraction(1, 3)}),
          "HETEROGENEOUS_PARTIAL_REPLICATION")

    # T8 — denominator bound 5*n*lcm(gold) holds on a synthetic tier-like set
    recs = [{"gold_count": 3, "delta": Fraction(1, 3)},
            {"gold_count": 4, "delta": Fraction(-1, 4)},
            {"gold_count": 6, "delta": Fraction(1, 6)}]
    d8 = a.d_contrast(recs)  # (1/3 - 1/4 + 1/6)/3 = 1/12 by hand
    check("T8a hand-computed exact mean == 1/12", d8, Fraction(1, 12))
    bound8 = a.denominator_bound(recs)  # 5*3*lcm(3,4,6) = 180 by hand
    check("T8b hand-computed bound == 180", bound8, 180)
    check("T8c denominator divides bound (prereg divisibility rule)",
          bound8 % d8.denominator == 0, True)

    # T9 — inputs reconstructed from discrete IDs, never from the float aggregate
    cohort = {"q1": {"tier": "100K", "conversation_id": "syn",
                     "archive_id": "100K::syn", "ability": "syn_ab",
                     "gold": frozenset({"g1", "g2", "g3"}), "gold_count": 3}}
    row = {"audit_question_id": "q1", "tier": "100K", "conversation_id": "syn",
           "ability": "syn_ab", "method": "NATIVE_SIGN96", "seed": "", "trial": "0",
           "archive_units": "17", "gold_count": "3",
           "retrieved_top3_ids": '["g1","x","y"]', "top3_distances": "[1,2,3]",
           "fractional_source_evidence_recall_at_3": format(1 / 3, ".17g"),
           "any_at_3": "1", "all_at_3": "0"}
    cell = a.parse_cell(row, cohort)
    check("T9a fraction from discrete IDs == 1/3 exactly", cell["fraction"], Fraction(1, 3))
    check("T9b no float-derived value leaks into exact fraction",
          isinstance(cell["fraction"], Fraction), True)

    # T10 — display rounding must not touch the sign
    pay = a.rational_payload(tiny_pos)
    check("T10a payload sign of tiny positive == +1", pay["sign"], 1)
    check("T10b display decimal is all zeros yet sign stays +1 (display-only)",
          pay["decimal_18"] == "0.000000000000000000" and pay["sign"] == 1, True)

    # T11 — W/T/L counts use exact zero: tiny positive is a WIN, not a tie
    wtl = a.summarize_subset([{"delta": tiny_pos}, {"delta": Fraction(0, 1)},
                              {"delta": Fraction(-1, 7)}])
    check("T11a exact W/T/L == 1/1/1", (wtl["W"], wtl["T"], wtl["L"]), (1, 1, 1))
    float_wins = sum(1 for v in (tiny_pos, Fraction(0, 1), Fraction(-1, 7)) if float(v) > 0)
    check("T11b float W-count misses the tiny win (hazard is real)", float_wins == 0, True)
    check("T11c tie-excluded W/(W+L) == 1/2 exactly",
          Fraction(wtl["W_over_W_plus_L"]["numerator"],
                   wtl["W_over_W_plus_L"]["denominator"]), Fraction(1, 2))

    # T12 — basic exact mean sanity (independent hand computation)
    check("T12 mean(1/3, -1/6) == 1/12",
          a.d_contrast([{"delta": Fraction(1, 3)}, {"delta": Fraction(-1, 6)}]),
          Fraction(1, 12))

    discriminating = [c for c in cases
                      if c.get("float_control_observed") is not None
                      and c.get("float_control_differs")]
    total = len(cases)
    passed = sum(1 for c in cases if c["pass"])
    print(f"\n{passed}/{total} exact checks passed; "
          f"{len(discriminating)} cases expose the float control")

    payload = {
        "pilot": "LOCAL EXPLORATORY PILOT, NOT PREREGISTERED, NOT FOR CITATION",
        "status": "PREPARED, NOT ACCEPTED",
        "inputs": "synthetic only; authored in test_exact_rational.py; no real data",
        "module": str(ANALYZER),
        "module_sha256": hashlib.sha256(ANALYZER.read_bytes()).hexdigest(),
        "python": platform.python_version(),
        "run_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "summary": {"total": total, "passed": passed,
                    "float_control_exposed": len(discriminating)},
        "cases": cases,
    }
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    RESULTS.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"results -> {RESULTS}")

    if failures:
        print(f"RESULT: FAIL ({failures} failing checks)")
        return 1
    if len(discriminating) < 3:
        print("RESULT: TESTS TOO WEAK — float control exposed < 3 cases, fix the suite")
        return 2
    print("RESULT: PASS — exact behaviour confirmed, float control exposed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
