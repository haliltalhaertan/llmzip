#!/usr/bin/env python3
"""Independent BEAM corpus/evidence audit with no retrieval-quality computation."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


TIERS = ("100K", "500K", "1M", "10M")
EXPECTED_ABILITIES = (
    "abstention",
    "contradiction_resolution",
    "event_ordering",
    "information_extraction",
    "instruction_following",
    "knowledge_update",
    "multi_session_reasoning",
    "preference_following",
    "summarization",
    "temporal_reasoning",
)
EXACT = "EXACT_SOURCE_IDS"
COARSE = "COARSE_SOURCE"
ABSTAIN = "ABSTENTION_NO_POSITIVE_EVIDENCE"
AMBIGUOUS = "SOURCE_AMBIGUOUS_OR_MISSING"
MALFORMED = "MALFORMED_CONTRADICTORY"


def sha256_file(path: Path, chunk: int = 8 << 20) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(chunk), b""):
            digest.update(block)
    return digest.hexdigest()


def iter_messages(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        if {"role", "id", "content"}.issubset(value):
            yield value
            return
        for child in value.values():
            yield from iter_messages(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_messages(child)


def flatten_source_ids(value: Any) -> list[int]:
    found: list[int] = []

    def walk(node: Any) -> None:
        if isinstance(node, bool):
            raise TypeError("boolean source ID")
        if isinstance(node, int):
            found.append(node)
        elif isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, dict):
            for item in node.values():
                walk(item)
        else:
            raise TypeError(f"unsupported source ID node {type(node).__name__}")

    walk(value)
    return found


def nonempty(value: Any) -> bool:
    return value not in (None, "", [], {})


def classify_question(
    ability: str, question: dict[str, Any], message_id_counts: Counter[int]
) -> tuple[str, dict[str, Any]]:
    has_source_field = "source_chat_ids" in question
    source_value = question.get("source_chat_ids")
    details: dict[str, Any] = {
        "raw_source_ids": [],
        "unique_source_ids": [],
        "matched_source_ids": [],
        "unmatched_source_ids": [],
        "ambiguous_source_ids": [],
        "duplicate_source_refs": [],
        "source_parse_error": "",
    }

    if ability == "abstention":
        if has_source_field and nonempty(source_value):
            try:
                details["raw_source_ids"] = flatten_source_ids(source_value)
            except Exception as exc:  # the contradiction already controls the class
                details["source_parse_error"] = str(exc)
            return MALFORMED, details
        return ABSTAIN, details

    if not has_source_field:
        coarse = nonempty(question.get("conversation_reference")) or nonempty(
            question.get("conversation_references")
        )
        return (COARSE if coarse else AMBIGUOUS), details

    try:
        raw_ids = flatten_source_ids(source_value)
    except Exception as exc:
        details["source_parse_error"] = str(exc)
        return MALFORMED, details
    if not raw_ids:
        return AMBIGUOUS, details

    unique_ids = list(dict.fromkeys(raw_ids))
    raw_counts = Counter(raw_ids)
    details["raw_source_ids"] = raw_ids
    details["unique_source_ids"] = unique_ids
    details["duplicate_source_refs"] = sorted(
        source_id for source_id, count in raw_counts.items() if count > 1
    )
    details["matched_source_ids"] = sorted(
        source_id for source_id in unique_ids if message_id_counts[source_id] == 1
    )
    details["unmatched_source_ids"] = sorted(
        source_id for source_id in unique_ids if message_id_counts[source_id] == 0
    )
    details["ambiguous_source_ids"] = sorted(
        source_id for source_id in unique_ids if message_id_counts[source_id] > 1
    )
    if details["unmatched_source_ids"] or details["ambiguous_source_ids"]:
        return AMBIGUOUS, details
    return EXACT, details


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    inventory_rows: list[dict[str, Any]] = []
    taxonomy_counter: Counter[tuple[str, str, str]] = Counter()
    question_rows: list[dict[str, Any]] = []
    join_rows: list[dict[str, Any]] = []
    all_message_locations: defaultdict[int, list[str]] = defaultdict(list)
    composite_memory_keys: Counter[str] = Counter()
    raw_conversation_ids: set[str] = set()
    composite_conversation_ids: set[str] = set()
    tier_message_counts: defaultdict[str, list[int]] = defaultdict(list)
    source_shapes: Counter[str] = Counter()
    schema_keys: Counter[tuple[str, str]] = Counter()

    for tier in TIERS:
        tier_root = args.corpus / "chats" / tier
        conversation_dirs = sorted(
            (path for path in tier_root.iterdir() if path.is_dir()),
            key=lambda path: (not path.name.isdigit(), int(path.name) if path.name.isdigit() else path.name),
        )
        for conversation_dir in conversation_dirs:
            conversation_id = conversation_dir.name
            raw_conversation_ids.add(conversation_id)
            composite_conversation_ids.add(f"{tier}::{conversation_id}")
            chat_path = conversation_dir / "chat.json"
            question_path = conversation_dir / "probing_questions" / "probing_questions.json"
            if not chat_path.is_file() or not question_path.is_file():
                raise FileNotFoundError(f"incomplete conversation directory: {conversation_dir}")

            chat = json.loads(chat_path.read_text(encoding="utf-8"))
            messages = list(iter_messages(chat))
            message_id_counts: Counter[int] = Counter()
            malformed_message_ids = 0
            malformed_message_texts = 0
            role_counts: Counter[str] = Counter()
            for ordinal, message in enumerate(messages):
                source_id = message.get("id")
                role = message.get("role")
                content = message.get("content")
                role_counts[str(role)] += 1
                if isinstance(source_id, bool) or not isinstance(source_id, int):
                    malformed_message_ids += 1
                    continue
                if role not in {"user", "assistant"} or not isinstance(content, str):
                    malformed_message_texts += 1
                message_id_counts[source_id] += 1
                location = f"{tier}::{conversation_id}::msg:{source_id}"
                all_message_locations[source_id].append(location)
                composite_memory_keys[location] += 1
            duplicate_raw_ids = sorted(
                source_id for source_id, count in message_id_counts.items() if count > 1
            )
            tier_message_counts[tier].append(len(messages))

            question_data = json.loads(question_path.read_text(encoding="utf-8"))
            if not isinstance(question_data, dict):
                raise TypeError(f"question file is not an object: {question_path}")
            question_count = 0
            for ability, questions in question_data.items():
                if not isinstance(questions, list):
                    raise TypeError(f"ability value is not a list: {question_path}: {ability}")
                for index, question in enumerate(questions):
                    if not isinstance(question, dict):
                        raise TypeError(f"question is not an object: {question_path}: {ability}[{index}]")
                    question_count += 1
                    audit_question_id = f"{tier}::{conversation_id}::{ability}::{index + 1}"
                    for key in question:
                        schema_keys[(ability, key)] += 1
                    source_value = question.get("source_chat_ids")
                    if "source_chat_ids" not in question:
                        source_shape = "ABSENT"
                    elif isinstance(source_value, list):
                        source_shape = "LIST"
                    elif isinstance(source_value, dict):
                        source_shape = "DICT"
                    elif source_value is None:
                        source_shape = "NULL"
                    else:
                        source_shape = type(source_value).__name__.upper()
                    source_shapes[source_shape] += 1

                    category, details = classify_question(ability, question, message_id_counts)
                    taxonomy_counter[(tier, ability, category)] += 1
                    question_row = {
                        "audit_question_id": audit_question_id,
                        "tier": tier,
                        "conversation_id": conversation_id,
                        "ability": ability,
                        "category": category,
                        "source_shape": source_shape,
                        "source_field_present": "source_chat_ids" in question,
                        "conversation_reference_present": nonempty(question.get("conversation_reference")),
                        "conversation_references_present": nonempty(question.get("conversation_references")),
                        "raw_source_ref_count": len(details["raw_source_ids"]),
                        "unique_source_id_count": len(details["unique_source_ids"]),
                        "matched_source_id_count": len(details["matched_source_ids"]),
                        "unmatched_source_id_count": len(details["unmatched_source_ids"]),
                        "ambiguous_source_id_count": len(details["ambiguous_source_ids"]),
                        "duplicate_source_ref_id_count": len(details["duplicate_source_refs"]),
                        "source_parse_error": details["source_parse_error"],
                    }
                    question_rows.append(question_row)
                    if "source_chat_ids" in question and nonempty(source_value):
                        join_rows.append(
                            {
                                **question_row,
                                "raw_source_ids": json.dumps(details["raw_source_ids"]),
                                "unique_source_ids": json.dumps(details["unique_source_ids"]),
                                "matched_source_ids": json.dumps(details["matched_source_ids"]),
                                "unmatched_source_ids": json.dumps(details["unmatched_source_ids"]),
                                "ambiguous_source_ids": json.dumps(details["ambiguous_source_ids"]),
                                "duplicate_source_refs": json.dumps(details["duplicate_source_refs"]),
                            }
                        )

            inventory_rows.append(
                {
                    "tier": tier,
                    "conversation_id": conversation_id,
                    "chat_path": chat_path.relative_to(args.corpus).as_posix(),
                    "chat_bytes": chat_path.stat().st_size,
                    "chat_sha256": sha256_file(chat_path),
                    "question_path": question_path.relative_to(args.corpus).as_posix(),
                    "question_bytes": question_path.stat().st_size,
                    "question_sha256": sha256_file(question_path),
                    "raw_message_units": len(messages),
                    "user_messages": role_counts["user"],
                    "assistant_messages": role_counts["assistant"],
                    "other_role_messages": len(messages) - role_counts["user"] - role_counts["assistant"],
                    "unique_local_message_ids": len(message_id_counts),
                    "duplicate_local_message_id_values": len(duplicate_raw_ids),
                    "malformed_message_ids": malformed_message_ids,
                    "malformed_message_texts": malformed_message_texts,
                    "probing_questions": question_count,
                }
            )

    taxonomy_rows = [
        {"tier": tier, "ability": ability, "category": category, "count": count}
        for (tier, ability, category), count in sorted(taxonomy_counter.items())
    ]
    tier_summaries: dict[str, Any] = {}
    for tier in TIERS:
        tier_inventory = [row for row in inventory_rows if row["tier"] == tier]
        counts = tier_message_counts[tier]
        category_counts = Counter(
            row["category"] for row in question_rows if row["tier"] == tier
        )
        ability_counts = Counter(row["ability"] for row in question_rows if row["tier"] == tier)
        tier_summaries[tier] = {
            "conversations": len(tier_inventory),
            "probing_questions": sum(row["probing_questions"] for row in tier_inventory),
            "raw_message_units": sum(counts),
            "messages_per_conversation": {
                "min": min(counts),
                "median": statistics.median(counts),
                "mean": statistics.mean(counts),
                "max": max(counts),
            },
            "chat_bytes": sum(row["chat_bytes"] for row in tier_inventory),
            "question_bytes": sum(row["question_bytes"] for row in tier_inventory),
            "category_counts": dict(sorted(category_counts.items())),
            "ability_counts": dict(sorted(ability_counts.items())),
            "duplicate_local_message_id_values": sum(
                row["duplicate_local_message_id_values"] for row in tier_inventory
            ),
            "malformed_message_ids": sum(row["malformed_message_ids"] for row in tier_inventory),
            "malformed_message_texts": sum(row["malformed_message_texts"] for row in tier_inventory),
            "binary96_code_bytes": 12 * sum(counts),
        }

    global_id_collision_values = {
        source_id: locations
        for source_id, locations in all_message_locations.items()
        if len(locations) > 1
    }
    duplicate_memory_keys = {
        key: count for key, count in composite_memory_keys.items() if count > 1
    }
    overall_counts = [row["raw_message_units"] for row in inventory_rows]
    category_counts = Counter(row["category"] for row in question_rows)
    exact_join_rows = [row for row in join_rows if row["category"] == EXACT]
    summary = {
        "task": "V52 TASK 4F0 - CODEX INDEPENDENT AUDIT",
        "scientific_native_vs_haar_outcome_inspected": False,
        "tiers": tier_summaries,
        "overall": {
            "conversations": len(inventory_rows),
            "unique_raw_conversation_ids": len(raw_conversation_ids),
            "unique_composite_conversation_ids": len(composite_conversation_ids),
            "probing_questions": len(question_rows),
            "raw_message_units": sum(overall_counts),
            "messages_per_conversation": {
                "min": min(overall_counts),
                "median": statistics.median(overall_counts),
                "mean": statistics.mean(overall_counts),
                "max": max(overall_counts),
            },
            "chat_bytes": sum(row["chat_bytes"] for row in inventory_rows),
            "question_bytes": sum(row["question_bytes"] for row in inventory_rows),
            "category_counts": dict(sorted(category_counts.items())),
            "exact_source_questions": category_counts[EXACT],
            "exact_source_id_count_unique_per_question_sum": sum(
                row["unique_source_id_count"] for row in exact_join_rows
            ),
            "matched_source_ids": sum(row["matched_source_id_count"] for row in join_rows),
            "unmatched_source_ids": sum(row["unmatched_source_id_count"] for row in join_rows),
            "ambiguous_source_ids": sum(row["ambiguous_source_id_count"] for row in join_rows),
            "duplicate_source_reference_id_occurrences": sum(
                row["raw_source_ref_count"] - row["unique_source_id_count"] for row in join_rows
            ),
            "duplicate_memory_unit_keys": len(duplicate_memory_keys),
            "unique_raw_message_id_values": len(all_message_locations),
            "raw_message_id_values_colliding_across_conversations": len(global_id_collision_values),
            "binary96_code_bytes": 12 * sum(overall_counts),
        },
        "source_shapes": dict(sorted(source_shapes.items())),
        "expected_abilities_present": sorted({row["ability"] for row in question_rows})
        == sorted(EXPECTED_ABILITIES),
        "duplicate_memory_keys": duplicate_memory_keys,
        "affected_question_ids": {
            "unmatched_source_ids": [
                row["audit_question_id"] for row in join_rows if row["unmatched_source_id_count"]
            ],
            "ambiguous_source_ids": [
                row["audit_question_id"] for row in join_rows if row["ambiguous_source_id_count"]
            ],
            "malformed_or_contradictory": [
                row["audit_question_id"] for row in question_rows if row["category"] == MALFORMED
            ],
            "source_ambiguous_or_missing": [
                row["audit_question_id"] for row in question_rows if row["category"] == AMBIGUOUS
            ],
        },
        "schema_key_counts": {
            f"{ability}.{key}": count for (ability, key), count in sorted(schema_keys.items())
        },
    }

    (args.output / "corpus_audit_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    write_csv(
        args.output / "conversation_inventory.csv",
        inventory_rows,
        list(inventory_rows[0]),
    )
    write_csv(
        args.output / "question_taxonomy_counts.csv",
        taxonomy_rows,
        ["tier", "ability", "category", "count"],
    )
    write_csv(
        args.output / "question_census.csv",
        question_rows,
        list(question_rows[0]),
    )
    write_csv(
        args.output / "source_id_join.csv",
        join_rows,
        list(join_rows[0]),
    )
    collision_rows = [
        {
            "raw_message_id": source_id,
            "occurrence_count": len(locations),
            "sample_locations": json.dumps(locations[:20]),
        }
        for source_id, locations in sorted(global_id_collision_values.items())
    ]
    write_csv(
        args.output / "global_raw_id_collisions.csv",
        collision_rows,
        ["raw_message_id", "occurrence_count", "sample_locations"],
    )
    print(json.dumps(summary["overall"], indent=2))


if __name__ == "__main__":
    main()
