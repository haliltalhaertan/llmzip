#!/usr/bin/env python3
"""Freeze an outcome-independent restricted evidence cohort from audit semantics."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import Counter
from pathlib import Path


BAD_ARCHIVES = {"1M::5", "1M::26", "1M::33", "1M::34"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    questions = list(csv.DictReader((args.audit_results / "question_census.csv").open(encoding="utf-8")))
    joins = {
        row["audit_question_id"]: row
        for row in csv.DictReader((args.audit_results / "source_id_join.csv").open(encoding="utf-8"))
    }

    rows: list[dict[str, object]] = []
    for question in questions:
        archive_id = f"{question['tier']}::{question['conversation_id']}"
        if archive_id in BAD_ARCHIVES:
            eligible = False
            reason = "EXCLUDE_ARCHIVE_DUPLICATE_DIVERGENT_MESSAGE_IDS"
        elif question["category"] == "EXACT_SOURCE_IDS":
            eligible = True
            reason = "ELIGIBLE_EXACT_SOURCE_IDS_UNIQUE_ARCHIVE"
        else:
            eligible = False
            reason = f"EXCLUDE_{question['category']}"
        join = joins.get(question["audit_question_id"])
        gold_count = int(question["unique_source_id_count"]) if eligible else 0
        rows.append(
            {
                "audit_question_id": question["audit_question_id"],
                "tier": question["tier"],
                "conversation_id": question["conversation_id"],
                "ability": question["ability"],
                "audit_category": question["category"],
                "primary_evidence_cohort_eligible": eligible,
                "eligibility_reason": reason,
                "gold_source_unit_count": gold_count,
                "all_at_3_structurally_possible": eligible and gold_count <= 3,
                "gold_source_ids": join["unique_source_ids"] if eligible and join else "[]",
            }
        )

    eligible_rows = [row for row in rows if row["primary_evidence_cohort_eligible"]]
    gold_counts = [int(row["gold_source_unit_count"]) for row in eligible_rows]
    tier_ability = Counter((str(row["tier"]), str(row["ability"])) for row in eligible_rows)
    exclusions = Counter(str(row["eligibility_reason"]) for row in rows if not row["primary_evidence_cohort_eligible"])
    answerable_total = sum(row["ability"] != "abstention" for row in rows)
    clean_archive_answerable = sum(
        row["ability"] != "abstention"
        and f"{row['tier']}::{row['conversation_id']}" not in BAD_ARCHIVES
        for row in rows
    )
    summary = {
        "primary_cohort_rule": (
            "Include only non-abstention questions classified EXACT_SOURCE_IDS whose entire "
            "conversation archive has unique (tier, conversation_id, raw_message_id) keys."
        ),
        "primary_evidence_questions": len(eligible_rows),
        "total_questions": len(rows),
        "answerable_questions": answerable_total,
        "clean_archive_answerable_questions": clean_archive_answerable,
        "coverage_of_all_answerable": len(eligible_rows) / answerable_total,
        "coverage_of_clean_archive_answerable": len(eligible_rows) / clean_archive_answerable,
        "excluded_archive_ids": sorted(BAD_ARCHIVES),
        "excluded_archive_count": len(BAD_ARCHIVES),
        "exclusion_reason_counts": dict(sorted(exclusions.items())),
        "eligible_by_tier_ability": {
            f"{tier}.{ability}": count for (tier, ability), count in sorted(tier_ability.items())
        },
        "gold_cardinality": {
            "min": min(gold_counts),
            "median": statistics.median(gold_counts),
            "mean": statistics.mean(gold_counts),
            "max": max(gold_counts),
            "distribution": dict(sorted(Counter(gold_counts).items())),
            "questions_with_more_than_3_gold_units": sum(value > 3 for value in gold_counts),
        },
        "estimand_identifiability": {
            "Fractional Source Evidence R@3": "IDENTIFIABLE_ON_PRIMARY_RESTRICTED_COHORT",
            "ANY@3": "IDENTIFIABLE_ON_PRIMARY_RESTRICTED_COHORT",
            "ALL@3": (
                "IDENTIFIABLE_ON_PRIMARY_RESTRICTED_COHORT; questions with >3 gold units "
                "are structurally zero unless a separately preregistered cardinality restriction is used"
            ),
        },
        "retrieval_quality_computed": False,
    }
    with (args.output / "estimand_primary_cohort.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (args.output / "estimand_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
