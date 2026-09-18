#!/usr/bin/env python3
"""Exact-rational Task 4F1 outcome analysis, frozen before outcome access.

This program is intentionally separate from the accepted retrieval runner. It never uses the
runner's floating aggregate as the authoritative sign-classification input. Instead it reconstructs
per-question hit counts from discrete retrieved IDs plus the sealed cohort gold IDs and computes all
D_t signs with fractions.Fraction.

It also re-checks the two invalidating integrity identities before assigning a replication category:
20 nuisance trials must be identical, and SIGNED_PERM_CONTROL96 must exactly reproduce Native's
ordered top-three IDs and exact Hamming distances for every question/seed/trial.

Creating or reviewing this file accesses no retrieval-quality outcome. Running it on production
Task 4F1 output is forbidden until a valid production authorization exists.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

EXPECTED_COHORT_SHA256 = "9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a"
EXPECTED_ELIGIBLE = 1712
EXPECTED_ARCHIVES = 96
TIERS = ("100K", "500K", "1M", "10M")
TIER_DENOMINATORS = {"100K": 355, "500K": 629, "1M": 553, "10M": 175}
TIER_ARCHIVE_COUNTS = {"100K": 20, "500K": 35, "1M": 31, "10M": 10}
CEILING_FREE_DENOMINATORS = {"100K": 259, "500K": 461, "1M": 300, "10M": 105}
HAAR_SEEDS = (43001, 43002, 43003, 43004, 43005)
SIGNED_PERM_SEEDS = HAAR_SEEDS
ITQ_SEEDS = (101, 202, 303, 404, 505)
TRIALS = tuple(range(20))
METHOD_SEEDS = {
    "NATIVE_SIGN96": ("",),
    "SIGNED_PERM_CONTROL96": tuple(str(x) for x in SIGNED_PERM_SEEDS),
    "HAAR96_SIGN": tuple(str(x) for x in HAAR_SEEDS),
    "ITQ96_CENTERED": tuple(str(x) for x in ITQ_SEEDS),
}
TRIAL_FIELDS = (
    "audit_question_id",
    "tier",
    "conversation_id",
    "ability",
    "method",
    "seed",
    "trial",
    "archive_units",
    "gold_count",
    "retrieved_top3_ids",
    "top3_distances",
    "fractional_source_evidence_recall_at_3",
    "any_at_3",
    "all_at_3",
)
EXPECTED_ROWS_PER_QUESTION = len(TRIALS) * sum(len(v) for v in METHOD_SEEDS.values())
EXPECTED_TRIAL_ROWS = EXPECTED_ELIGIBLE * EXPECTED_ROWS_PER_QUESTION


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def rational_payload(value: Fraction) -> dict[str, Any]:
    with localcontext() as ctx:
        ctx.prec = 60
        decimal = Decimal(value.numerator) / Decimal(value.denominator)
        decimal_text = format(decimal, ".18f")
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "decimal_18": decimal_text,
        "sign": 1 if value > 0 else (-1 if value < 0 else 0),
    }


def mean_fraction(values: Iterable[Fraction]) -> Fraction:
    values = list(values)
    if not values:
        raise ValueError("mean of empty exact-rational set")
    return sum(values, Fraction(0, 1)) / len(values)


def sign(value: Fraction) -> int:
    return 1 if value > 0 else (-1 if value < 0 else 0)


def classify_primary(primary: dict[str, Fraction]) -> str:
    signs = [sign(primary[tier]) for tier in TIERS]
    if all(value > 0 for value in signs):
        return "FULL_REPLICATION"
    if all(value <= 0 for value in signs):
        return "NO_REPLICATION"
    return "HETEROGENEOUS_PARTIAL_REPLICATION"


def gold_bucket(count: int) -> str:
    if count <= 0:
        raise ValueError("gold count must be positive")
    if count <= 3:
        return str(count)
    if count <= 6:
        return "4-6"
    return "7+"


def load_cohort(path: Path) -> dict[str, dict[str, Any]]:
    if sha256_file(path) != EXPECTED_COHORT_SHA256:
        raise RuntimeError("[BLOCKED - COHORT SHA256 MISMATCH]")
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    eligible: dict[str, dict[str, Any]] = {}
    for row in rows:
        if row["primary_evidence_cohort_eligible"].strip().lower() != "true":
            continue
        qid = row["audit_question_id"]
        if qid in eligible:
            raise RuntimeError(f"[BLOCKED - DUPLICATE COHORT QUESTION] {qid}")
        gold = json.loads(row["gold_source_ids"])
        if not isinstance(gold, list) or not gold:
            raise RuntimeError(f"[BLOCKED - INVALID GOLD IDS] {qid}")
        gold_strings = tuple(str(x) for x in gold)
        if len(set(gold_strings)) != len(gold_strings):
            raise RuntimeError(f"[BLOCKED - DUPLICATE GOLD IDS] {qid}")
        if len(gold_strings) != int(row["gold_source_unit_count"]):
            raise RuntimeError(f"[BLOCKED - GOLD COUNT MISMATCH] {qid}")
        eligible[qid] = {
            "tier": row["tier"],
            "conversation_id": row["conversation_id"],
            "archive_id": f"{row['tier']}::{row['conversation_id']}",
            "ability": row["ability"],
            "gold": frozenset(gold_strings),
            "gold_count": len(gold_strings),
        }
    if len(eligible) != EXPECTED_ELIGIBLE:
        raise RuntimeError(f"[BLOCKED - ELIGIBLE QUESTION COUNT] {len(eligible)}")

    question_counts = defaultdict(int)
    archive_sets: dict[str, set[str]] = defaultdict(set)
    ceiling_free = defaultdict(int)
    for item in eligible.values():
        question_counts[item["tier"]] += 1
        archive_sets[item["tier"]].add(item["archive_id"])
        if item["gold_count"] <= 3:
            ceiling_free[item["tier"]] += 1
    archive_counts = {tier: len(archive_sets[tier]) for tier in TIERS}
    if dict(question_counts) != TIER_DENOMINATORS:
        raise RuntimeError(f"[BLOCKED - TIER DENOMINATORS] {dict(question_counts)}")
    if archive_counts != TIER_ARCHIVE_COUNTS:
        raise RuntimeError(f"[BLOCKED - TIER ARCHIVE COUNTS] {archive_counts}")
    if dict(ceiling_free) != CEILING_FREE_DENOMINATORS:
        raise RuntimeError(f"[BLOCKED - CEILING-FREE DENOMINATORS] {dict(ceiling_free)}")
    if sum(archive_counts.values()) != EXPECTED_ARCHIVES:
        raise RuntimeError(f"[BLOCKED - ARCHIVE COUNT] {sum(archive_counts.values())}")
    return eligible


def read_trial_rows(results_dir: Path) -> tuple[list[dict[str, str]], dict[str, Any]]:
    archive_dir = results_dir / "archives"
    if not archive_dir.is_dir():
        raise RuntimeError("[BLOCKED - ARCHIVE RESULT DIRECTORY MISSING]")
    paths = sorted(archive_dir.glob("*.csv"))
    if len(paths) != EXPECTED_ARCHIVES:
        raise RuntimeError(f"[BLOCKED - ARCHIVE CSV COUNT] {len(paths)} != {EXPECTED_ARCHIVES}")
    rows: list[dict[str, str]] = []
    manifest: dict[str, Any] = {}
    observed_archives = set()
    for path in paths:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != TRIAL_FIELDS:
                raise RuntimeError(f"[BLOCKED - TRIAL CSV SCHEMA] {path.name}")
            file_rows = list(reader)
        if not file_rows:
            raise RuntimeError(f"[BLOCKED - EMPTY ARCHIVE CSV] {path.name}")
        archive_ids = {f"{row['tier']}::{row['conversation_id']}" for row in file_rows}
        if len(archive_ids) != 1:
            raise RuntimeError(f"[BLOCKED - MIXED ARCHIVE CSV] {path.name}")
        archive_id = next(iter(archive_ids))
        if archive_id in observed_archives:
            raise RuntimeError(f"[BLOCKED - DUPLICATE ARCHIVE CSV] {archive_id}")
        observed_archives.add(archive_id)
        expected_name = archive_id.replace("::", "__") + ".csv"
        if path.name != expected_name:
            raise RuntimeError(f"[BLOCKED - ARCHIVE CSV NAME] {path.name} != {expected_name}")
        manifest[path.name] = {
            "archive_id": archive_id,
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "row_count": len(file_rows),
        }
        rows.extend(file_rows)
    if len(observed_archives) != EXPECTED_ARCHIVES:
        raise RuntimeError("[BLOCKED - ARCHIVE CSV COVERAGE]")
    if len(rows) != EXPECTED_TRIAL_ROWS:
        raise RuntimeError(f"[BLOCKED - TRIAL ROW COUNT] {len(rows)} != {EXPECTED_TRIAL_ROWS}")
    return rows, {
        "archive_csv_count": len(paths),
        "trial_row_count": len(rows),
        "archive_csv_manifest": manifest,
    }


def parse_cell(row: dict[str, str], cohort: dict[str, dict[str, Any]]) -> dict[str, Any]:
    qid = row["audit_question_id"]
    if qid not in cohort:
        raise RuntimeError(f"[BLOCKED - UNKNOWN QUESTION] {qid}")
    frozen = cohort[qid]
    if row["tier"] != frozen["tier"] or row["conversation_id"] != frozen["conversation_id"]:
        raise RuntimeError(f"[BLOCKED - QUESTION LOCATION MISMATCH] {qid}")
    if row["ability"] != frozen["ability"]:
        raise RuntimeError(f"[BLOCKED - ABILITY MISMATCH] {qid}")
    if row["method"] not in METHOD_SEEDS or row["seed"] not in METHOD_SEEDS[row["method"]]:
        raise RuntimeError(f"[BLOCKED - METHOD/SEED] {qid} {row['method']} {row['seed']}")
    try:
        trial = int(row["trial"])
        reported_gold_count = int(row["gold_count"])
        retrieved_raw = json.loads(row["retrieved_top3_ids"])
        distances_raw = json.loads(row["top3_distances"])
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"[BLOCKED - MALFORMED TRIAL CELL] {qid}") from exc
    if trial not in TRIALS:
        raise RuntimeError(f"[BLOCKED - TRIAL INDEX] {qid} {trial}")
    if reported_gold_count != frozen["gold_count"]:
        raise RuntimeError(f"[BLOCKED - REPORTED GOLD COUNT] {qid}")
    if not isinstance(retrieved_raw, list) or len(retrieved_raw) != 3:
        raise RuntimeError(f"[BLOCKED - TOP3 IDS] {qid}")
    retrieved = tuple(str(x) for x in retrieved_raw)
    if len(set(retrieved)) != 3:
        raise RuntimeError(f"[BLOCKED - DUPLICATE TOP3 IDS] {qid}")
    if not isinstance(distances_raw, list) or len(distances_raw) != 3:
        raise RuntimeError(f"[BLOCKED - TOP3 DISTANCES] {qid}")
    try:
        distances = tuple(int(x) for x in distances_raw)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"[BLOCKED - TOP3 DISTANCE FORMAT] {qid}") from exc
    if any(value < 0 for value in distances):
        raise RuntimeError(f"[BLOCKED - NEGATIVE HAMMING DISTANCE] {qid}")

    hits = len(set(retrieved) & set(frozen["gold"]))
    frac = Fraction(hits, frozen["gold_count"])
    any_at_3 = int(hits > 0)
    all_at_3 = int(set(frozen["gold"]).issubset(set(retrieved)))
    try:
        reported_any = int(row["any_at_3"])
        reported_all = int(row["all_at_3"])
    except ValueError as exc:
        raise RuntimeError(f"[BLOCKED - BINARY METRIC FORMAT] {qid}") from exc
    if reported_any != any_at_3 or reported_all != all_at_3:
        raise RuntimeError(f"[BLOCKED - BINARY METRIC RECOMPUTATION] {qid}")

    # Convenience float is integrity-checked but is never used below for exact classification.
    try:
        reported_float = float(row["fractional_source_evidence_recall_at_3"])
    except ValueError as exc:
        raise RuntimeError(f"[BLOCKED - FRACTIONAL METRIC FORMAT] {qid}") from exc
    if reported_float != hits / frozen["gold_count"]:
        raise RuntimeError(f"[BLOCKED - FRACTIONAL METRIC RECOMPUTATION] {qid}")

    # Trial is the only CSV field allowed to vary across the 20 nuisance repetitions.
    row_identity = tuple((field, row[field]) for field in TRIAL_FIELDS if field != "trial")
    return {
        "qid": qid,
        "tier": frozen["tier"],
        "archive_id": frozen["archive_id"],
        "ability": frozen["ability"],
        "gold_count": frozen["gold_count"],
        "method": row["method"],
        "seed": row["seed"],
        "trial": trial,
        "row_identity": row_identity,
        "retrieved": retrieved,
        "distances": distances,
        "hits": hits,
        "fraction": frac,
        "any": Fraction(any_at_3, 1),
        "all": Fraction(all_at_3, 1),
    }


def validate_integrity_and_reduce(
    rows: list[dict[str, str]], cohort: dict[str, dict[str, Any]]
) -> dict[tuple[str, str, str], dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    seen_row_keys = set()
    for raw in rows:
        cell = parse_cell(raw, cohort)
        row_key = (cell["qid"], cell["method"], cell["seed"], cell["trial"])
        if row_key in seen_row_keys:
            raise RuntimeError(f"[INVALIDATION - DUPLICATE RESULT CELL] {row_key}")
        seen_row_keys.add(row_key)
        grouped[(cell["qid"], cell["method"], cell["seed"])].append(cell)

    expected_cells = EXPECTED_ELIGIBLE * sum(len(v) for v in METHOD_SEEDS.values())
    if len(grouped) != expected_cells:
        raise RuntimeError(f"[INVALIDATION - RESULT CELL COVERAGE] {len(grouped)} != {expected_cells}")

    representative: dict[tuple[str, str, str], dict[str, Any]] = {}
    for key, values in grouped.items():
        values = sorted(values, key=lambda x: x["trial"])
        if tuple(v["trial"] for v in values) != TRIALS:
            raise RuntimeError(f"[INVALIDATION - NUISANCE TRIAL COVERAGE] {key}")
        identity = values[0]["row_identity"]
        for item in values[1:]:
            if item["row_identity"] != identity:
                raise RuntimeError(f"[INVALIDATION - NUISANCE TRIAL VARIATION] {key}")
        representative[key] = values[0]

    # Signed-permutation control is an exact retrieval identity, not a result.
    for qid in cohort:
        native_rows = grouped[(qid, "NATIVE_SIGN96", "")]
        native_by_trial = {item["trial"]: item for item in native_rows}
        for seed in map(str, SIGNED_PERM_SEEDS):
            for item in grouped[(qid, "SIGNED_PERM_CONTROL96", seed)]:
                native = native_by_trial[item["trial"]]
                if item["retrieved"] != native["retrieved"] or item["distances"] != native["distances"]:
                    raise RuntimeError(
                        f"[INVALIDATION - SIGNED PERM CONTROL DIVERGENCE] {qid} seed={seed} trial={item['trial']}"
                    )
    return representative


def question_records(
    representative: dict[tuple[str, str, str], dict[str, Any]],
    cohort: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for qid, frozen in cohort.items():
        native = representative[(qid, "NATIVE_SIGN96", "")]
        haar = [representative[(qid, "HAAR96_SIGN", str(seed))] for seed in HAAR_SEEDS]
        itq = [representative[(qid, "ITQ96_CENTERED", str(seed))] for seed in ITQ_SEEDS]
        native_frac = native["fraction"]
        haar_fracs = [x["fraction"] for x in haar]
        delta = native_frac - mean_fraction(haar_fracs)
        ceiling = Fraction(1, 1) if frozen["gold_count"] <= 3 else Fraction(3, frozen["gold_count"])
        out.append({
            "qid": qid,
            "tier": frozen["tier"],
            "archive_id": frozen["archive_id"],
            "ability": frozen["ability"],
            "gold_count": frozen["gold_count"],
            "gold_bucket": gold_bucket(frozen["gold_count"]),
            "native_frac": native_frac,
            "haar_fracs": tuple(haar_fracs),
            "haar_mean": mean_fraction(haar_fracs),
            "delta": delta,
            "delta_norm": delta / ceiling,
            "native_any": native["any"],
            "haar_any_mean": mean_fraction(x["any"] for x in haar),
            "native_all": native["all"],
            "haar_all_mean": mean_fraction(x["all"] for x in haar),
            "itq_mean": mean_fraction(x["fraction"] for x in itq),
        })
    return out


def exact_contrast(records: list[dict[str, Any]], key_left: str, key_right: str) -> Fraction:
    return mean_fraction(row[key_left] - row[key_right] for row in records)


def d_contrast(records: list[dict[str, Any]]) -> Fraction:
    return mean_fraction(row["delta"] for row in records)


def summarize_subset(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not records:
        return None
    d = d_contrast(records)
    wins = sum(row["delta"] > 0 for row in records)
    ties = sum(row["delta"] == 0 for row in records)
    losses = len(records) - wins - ties
    wl = Fraction(wins, wins + losses) if wins + losses else None
    return {
        "n": len(records),
        "D": rational_payload(d),
        "W": wins,
        "T": ties,
        "L": losses,
        "W_over_W_plus_L": rational_payload(wl) if wl is not None else None,
    }


def denominator_bound(records: list[dict[str, Any]]) -> int:
    lcm_gold = 1
    for row in records:
        lcm_gold = math.lcm(lcm_gold, row["gold_count"])
    return 5 * len(records) * lcm_gold


def sensitivity_discordance(
    primary: Fraction,
    ceiling_free: Fraction,
    d_norm: Fraction,
    gold_strata: dict[str, dict[str, Any] | None],
) -> dict[str, Any]:
    primary_sign = sign(primary)
    flagged: list[str] = []
    if sign(ceiling_free) != primary_sign:
        flagged.append("D_t_gold_le_3")
    if sign(d_norm) != primary_sign:
        flagged.append("D_t_norm_sensitivity")
    for bucket, summary in gold_strata.items():
        if summary is not None and summary["D"]["sign"] != primary_sign:
            flagged.append(f"gold_stratum_{bucket}")
    return {
        "present": bool(flagged),
        "components_with_sign_different_from_D_t": flagged,
        "effect_on_global_category": "NONE; sensitivity flags never override or veto the D_t category",
    }


def build_report(records: list[dict[str, Any]], input_manifest: dict[str, Any]) -> dict[str, Any]:
    tier_report: dict[str, Any] = {}
    primary: dict[str, Fraction] = {}
    for tier in TIERS:
        subset = [r for r in records if r["tier"] == tier]
        if len(subset) != TIER_DENOMINATORS[tier]:
            raise RuntimeError(f"[BLOCKED - ANALYSIS TIER DENOMINATOR] {tier}")
        d = d_contrast(subset)
        primary[tier] = d
        bound = denominator_bound(subset)
        if bound % d.denominator != 0:
            raise RuntimeError(f"[BLOCKED - EXACT-RATIONAL DENOMINATOR RULE] {tier}")

        ceiling_free_records = [r for r in subset if r["gold_count"] <= 3]
        if len(ceiling_free_records) != CEILING_FREE_DENOMINATORS[tier]:
            raise RuntimeError(f"[BLOCKED - ANALYSIS CEILING-FREE DENOMINATOR] {tier}")
        ceiling_free_d = d_contrast(ceiling_free_records)
        d_norm = mean_fraction(r["delta_norm"] for r in subset)

        per_seed = {}
        per_seed_values = []
        for index, seed in enumerate(HAAR_SEEDS):
            value = mean_fraction(r["native_frac"] - r["haar_fracs"][index] for r in subset)
            per_seed[str(seed)] = rational_payload(value)
            per_seed_values.append(value)

        archives = sorted({r["archive_id"] for r in subset})
        if len(archives) != TIER_ARCHIVE_COUNTS[tier]:
            raise RuntimeError(f"[BLOCKED - ANALYSIS TIER ARCHIVE COUNT] {tier}")
        loo_values = []
        for archive in archives:
            kept = [r for r in subset if r["archive_id"] != archive]
            loo_values.append((archive, d_contrast(kept)))
        loo_min_archive, loo_min = min(loo_values, key=lambda x: x[1])
        loo_max_archive, loo_max = max(loo_values, key=lambda x: x[1])

        gold_strata = {
            bucket: summarize_subset([r for r in subset if r["gold_bucket"] == bucket])
            for bucket in ("1", "2", "3", "4-6", "7+")
        }
        ability_values = sorted({r["ability"] for r in subset})
        ability_strata = {
            ability: summarize_subset([r for r in subset if r["ability"] == ability])
            for ability in ability_values
        }

        tier_report[tier] = {
            "n": len(subset),
            "D_t": rational_payload(d),
            "D_t_descriptor": "tier-local direction reversal" if d < 0 else ("tier-local null" if d == 0 else "positive"),
            "exact_rational_denominator_bound": bound,
            "exact_rational_denominator_divides_bound": True,
            "D_t_gold_le_3": rational_payload(ceiling_free_d),
            "D_t_norm_sensitivity": rational_payload(d_norm),
            "sensitivity_discordance_flag": sensitivity_discordance(d, ceiling_free_d, d_norm, gold_strata),
            "ANY_at_3_contrast": rational_payload(exact_contrast(subset, "native_any", "haar_any_mean")),
            "ALL_at_3_contrast": rational_payload(exact_contrast(subset, "native_all", "haar_all_mean")),
            "ITQ96_CENTERED_mean_descriptive": rational_payload(mean_fraction(r["itq_mean"] for r in subset)),
            "W_T_L": summarize_subset(subset),
            "gold_cardinality_strata": gold_strata,
            "ability_strata": ability_strata,
            "haar_seed_delta_sensitivity": {
                "per_seed": per_seed,
                "min": rational_payload(min(per_seed_values)),
                "max": rational_payload(max(per_seed_values)),
                "semantics": "fixed enumerated comparator sensitivity; not a sampling distribution",
            },
            "leave_one_archive_out_D_t": {
                "archive_count": len(archives),
                "min": {"omitted_archive": loo_min_archive, "D": rational_payload(loo_min)},
                "max": {"omitted_archive": loo_max_archive, "D": rational_payload(loo_max)},
                "semantics": "descriptive min-max only; not a CI or SE",
            },
        }

    category = classify_primary(primary)
    signs = {tier: sign(primary[tier]) for tier in TIERS}
    return {
        "schema": "V52_T4F1_EXACT_RATIONAL_OUTCOME_ANALYSIS_V1",
        "integrity": {
            "status": "PASS",
            "nuisance_trials_exact_identity": True,
            "signed_perm_control_exact_identity": True,
            "authoritative_sign_arithmetic": "fractions.Fraction from discrete hit counts; runner float aggregates not used",
        },
        "input_evidence": {
            "cohort_sha256": EXPECTED_COHORT_SHA256,
            **input_manifest,
        },
        "global_category": category,
        "global_category_source": "D_t signs only; sensitivity flags never override or veto",
        "primary_tier_signs": signs,
        "tiers": tier_report,
        "pooled_secondary_D": rational_payload(d_contrast(records)),
        "fixed_denominators": TIER_DENOMINATORS,
        "ceiling_free_denominators": CEILING_FREE_DENOMINATORS,
        "interpretation_boundary": {
            "population_inference": False,
            "p_values": False,
            "confidence_intervals_over_questions": False,
            "causal_context_length_effect": False,
            "degradation_law": False,
            "extrapolation_beyond_10M": False,
            "ALL_at_3_cross_tier_scale_claim": False,
        },
    }


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.output.exists():
        raise RuntimeError(f"[BLOCKED - REFUSE OUTPUT OVERWRITE] {args.output}")

    cohort = load_cohort(args.cohort)
    rows, input_manifest = read_trial_rows(args.results_dir)
    representative = validate_integrity_and_reduce(rows, cohort)
    records = question_records(representative, cohort)
    report = build_report(records, input_manifest)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(args.output.name + ".tmp")
    if temporary.exists():
        temporary.unlink()
    temporary.write_bytes(canonical_json_bytes(report))
    temporary.replace(args.output)
    print("T4F1_EXACT_RATIONAL_ANALYSIS: PASS")
    print(f"output={args.output}")
    print(f"output_sha256={sha256_file(args.output)}")
    print(f"global_category={report['global_category']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
