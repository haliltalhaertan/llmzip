#!/usr/bin/env python3
"""Outcome-free synthetic controls for the frozen Task 4F1 exact-rational analyzer."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "t4f1_exact_rational_outcome_analysis.py"


def load_module():
    spec = importlib.util.spec_from_file_location("t4f1_exact_analyzer", ANALYZER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load exact-rational analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def synthetic_cohort() -> dict:
    return {
        "q1": {
            "tier": "100K",
            "conversation_id": "synthetic",
            "archive_id": "100K::synthetic",
            "ability": "synthetic_ability",
            "gold": frozenset({"g1", "g2", "g3"}),
            "gold_count": 3,
        }
    }


def make_row(method: str, seed: str, trial: int, retrieved=None, distances=None) -> dict[str, str]:
    retrieved = retrieved or ["g1", "x", "y"]
    distances = distances or [1, 2, 3]
    hits = len(set(retrieved) & {"g1", "g2", "g3"})
    return {
        "audit_question_id": "q1",
        "tier": "100K",
        "conversation_id": "synthetic",
        "ability": "synthetic_ability",
        "method": method,
        "seed": seed,
        "trial": str(trial),
        "archive_units": "17",
        "gold_count": "3",
        "retrieved_top3_ids": json.dumps(retrieved, separators=(",", ":")),
        "top3_distances": json.dumps(distances, separators=(",", ":")),
        "fractional_source_evidence_recall_at_3": format(hits / 3, ".17g"),
        "any_at_3": str(int(hits > 0)),
        "all_at_3": str(int(hits == 3)),
    }


def synthetic_rows(a) -> list[dict[str, str]]:
    rows = []
    for method, seeds in a.METHOD_SEEDS.items():
        for seed in seeds:
            for trial in a.TRIALS:
                rows.append(make_row(method, seed, trial))
    return rows


def expect_raises(label: str, fn) -> bool:
    try:
        fn()
    except RuntimeError:
        print(f"ok   blocked: {label}")
        return True
    print(f"FAIL accepted: {label}")
    return False


def main() -> int:
    a = load_module()
    failures = 0
    total = 0

    cases = [
        ("full replication", {t: Fraction(1, 7) for t in a.TIERS}, "FULL_REPLICATION"),
        ("no replication including zero", {t: Fraction(0, 1) for t in a.TIERS}, "NO_REPLICATION"),
        ("heterogeneous", {"100K": Fraction(1), "500K": Fraction(0), "1M": Fraction(-1), "10M": Fraction(2)}, "HETEROGENEOUS_PARTIAL_REPLICATION"),
    ]
    for label, values, expected in cases:
        total += 1
        observed = a.classify_primary(values)
        if observed != expected:
            print(f"FAIL category {label}: {observed} != {expected}")
            failures += 1
        else:
            print(f"ok   category: {label}")

    total += 1
    simple = [
        {"delta": Fraction(1, 3)},
        {"delta": Fraction(-1, 6)},
    ]
    if a.d_contrast(simple) != Fraction(1, 12):
        print("FAIL exact mean arithmetic")
        failures += 1
    else:
        print("ok   exact mean arithmetic")

    total += 1
    denominator_records = [{"gold_count": 2}, {"gold_count": 3}]
    if a.denominator_bound(denominator_records) != 60:
        print("FAIL denominator bound")
        failures += 1
    else:
        print("ok   denominator bound")

    old_expected = a.EXPECTED_ELIGIBLE
    a.EXPECTED_ELIGIBLE = 1
    try:
        cohort = synthetic_cohort()
        rows = synthetic_rows(a)

        total += 1
        try:
            rep = a.validate_integrity_and_reduce(rows, cohort)
        except RuntimeError as exc:
            print(f"FAIL valid synthetic integrity fixture: {exc}")
            failures += 1
        else:
            expected_cells = sum(len(v) for v in a.METHOD_SEEDS.values())
            if len(rep) != expected_cells:
                print(f"FAIL synthetic representative count: {len(rep)}")
                failures += 1
            else:
                print("ok   valid synthetic 20-trial + signed-perm fixture")

        varied = copy.deepcopy(rows)
        target = next(
            row for row in varied
            if row["method"] == "HAAR96_SIGN" and row["seed"] == str(a.HAAR_SEEDS[0]) and row["trial"] == "7"
        )
        target.update(make_row("HAAR96_SIGN", str(a.HAAR_SEEDS[0]), 7, retrieved=["g2", "x", "y"]))
        total += 1
        if not expect_raises("nuisance trial variation", lambda: a.validate_integrity_and_reduce(varied, cohort)):
            failures += 1

        divergent = copy.deepcopy(rows)
        for row in divergent:
            if row["method"] == "SIGNED_PERM_CONTROL96" and row["seed"] == str(a.SIGNED_PERM_SEEDS[0]):
                trial = int(row["trial"])
                row.update(make_row("SIGNED_PERM_CONTROL96", str(a.SIGNED_PERM_SEEDS[0]), trial, retrieved=["g2", "x", "y"]))
        total += 1
        if not expect_raises("signed-permutation divergence", lambda: a.validate_integrity_and_reduce(divergent, cohort)):
            failures += 1

        total += 1
        cell = a.parse_cell(make_row("NATIVE_SIGN96", "", 0), cohort)
        if cell["fraction"] != Fraction(1, 3):
            print("FAIL discrete-ID exact fraction reconstruction")
            failures += 1
        else:
            print("ok   discrete-ID exact fraction reconstruction")

    finally:
        a.EXPECTED_ELIGIBLE = old_expected

    total += 1
    fake_strata = {
        "1": {"D": a.rational_payload(Fraction(-1, 10))},
        "2": None,
        "3": {"D": a.rational_payload(Fraction(1, 20))},
        "4-6": None,
        "7+": None,
    }
    flag = a.sensitivity_discordance(Fraction(1, 5), Fraction(1, 4), Fraction(-1, 8), fake_strata)
    if not flag["present"] or set(flag["components_with_sign_different_from_D_t"]) != {"D_t_norm_sensitivity", "gold_stratum_1"}:
        print(f"FAIL sensitivity discordance: {flag}")
        failures += 1
    else:
        print("ok   sensitivity discordance flag")

    print(f"\n{total - failures}/{total} outcome-free controls behaved correctly")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
