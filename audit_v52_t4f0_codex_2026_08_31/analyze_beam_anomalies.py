#!/usr/bin/env python3
"""Characterize duplicate message IDs and non-exact source annotations."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


def iter_messages_with_path(value: Any, path: tuple[Any, ...] = ()) -> Iterable[tuple[tuple[Any, ...], dict[str, Any]]]:
    if isinstance(value, dict):
        if {"role", "id", "content"}.issubset(value):
            yield path, value
            return
        for key, child in value.items():
            yield from iter_messages_with_path(child, path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_messages_with_path(child, path + (index,))


def payload_sha256(message: dict[str, Any]) -> str:
    payload = json.dumps(
        {"role": message.get("role"), "content": message.get("content")},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--audit-results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    question_rows = list(csv.DictReader((args.audit_results / "question_census.csv").open(encoding="utf-8")))
    join_rows = list(csv.DictReader((args.audit_results / "source_id_join.csv").open(encoding="utf-8")))
    duplicate_conversations = sorted(
        {
            (row["tier"], row["conversation_id"])
            for row in question_rows
            if int(row["ambiguous_source_id_count"]) > 0
        }
    )

    duplicate_rows: list[dict[str, Any]] = []
    duplicate_lookup: dict[tuple[str, str, int], dict[str, Any]] = {}
    for tier, conversation_id in duplicate_conversations:
        chat_path = args.corpus / "chats" / tier / conversation_id / "chat.json"
        chat = json.loads(chat_path.read_text(encoding="utf-8"))
        by_id: defaultdict[int, list[tuple[tuple[Any, ...], dict[str, Any]]]] = defaultdict(list)
        for path, message in iter_messages_with_path(chat):
            source_id = message.get("id")
            if isinstance(source_id, int) and not isinstance(source_id, bool):
                by_id[source_id].append((path, message))
        for source_id, occurrences in sorted(by_id.items()):
            if len(occurrences) < 2:
                continue
            hashes = [payload_sha256(message) for _, message in occurrences]
            roles = [message.get("role") for _, message in occurrences]
            contents = [message.get("content") for _, message in occurrences]
            row = {
                "tier": tier,
                "conversation_id": conversation_id,
                "message_id": source_id,
                "occurrence_count": len(occurrences),
                "distinct_role_content_payloads": len(set(hashes)),
                "identical_role_content": len(set(hashes)) == 1,
                "roles": json.dumps(roles),
                "payload_sha256s": json.dumps(hashes),
                "json_paths": json.dumps([list(path) for path, _ in occurrences]),
                "content_lengths": json.dumps([len(content) if isinstance(content, str) else None for content in contents]),
                "first_content_sha256": hashlib.sha256(
                    (contents[0] if isinstance(contents[0], str) else repr(contents[0])).encode("utf-8")
                ).hexdigest(),
            }
            duplicate_rows.append(row)
            duplicate_lookup[(tier, conversation_id, source_id)] = row

    question_anomaly_rows: list[dict[str, Any]] = []
    for row in question_rows:
        if row["category"] in {"EXACT_SOURCE_IDS", "ABSTENTION_NO_POSITIVE_EVIDENCE"}:
            continue
        question_file = (
            args.corpus
            / "chats"
            / row["tier"]
            / row["conversation_id"]
            / "probing_questions"
            / "probing_questions.json"
        )
        question_data = json.loads(question_file.read_text(encoding="utf-8"))
        question = question_data[row["ability"]][int(row["audit_question_id"].rsplit("::", 1)[1]) - 1]
        join = next((item for item in join_rows if item["audit_question_id"] == row["audit_question_id"]), None)
        ambiguous_ids = json.loads(join["ambiguous_source_ids"]) if join else []
        ambiguous_payload_identity = [
            duplicate_lookup[(row["tier"], row["conversation_id"], source_id)]["identical_role_content"]
            for source_id in ambiguous_ids
        ]
        question_anomaly_rows.append(
            {
                "audit_question_id": row["audit_question_id"],
                "tier": row["tier"],
                "conversation_id": row["conversation_id"],
                "ability": row["ability"],
                "category": row["category"],
                "source_shape": row["source_shape"],
                "source_chat_ids_json": json.dumps(question.get("source_chat_ids"), ensure_ascii=False),
                "conversation_reference_json": json.dumps(question.get("conversation_reference"), ensure_ascii=False),
                "conversation_references_json": json.dumps(question.get("conversation_references"), ensure_ascii=False),
                "ambiguous_source_ids": json.dumps(ambiguous_ids),
                "all_ambiguous_occurrences_text_identical": (
                    bool(ambiguous_ids) and all(ambiguous_payload_identity)
                ),
                "source_parse_error": row["source_parse_error"],
                "public_annotation_keys": json.dumps(sorted(question)),
            }
        )

    duplicate_fieldnames = list(duplicate_rows[0])
    with (args.output / "duplicate_message_ids.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=duplicate_fieldnames)
        writer.writeheader()
        writer.writerows(duplicate_rows)
    anomaly_fieldnames = list(question_anomaly_rows[0])
    with (args.output / "question_annotation_anomalies.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=anomaly_fieldnames)
        writer.writeheader()
        writer.writerows(question_anomaly_rows)

    summary = {
        "duplicate_conversations": [f"{tier}::{conversation_id}" for tier, conversation_id in duplicate_conversations],
        "duplicate_message_id_values": len(duplicate_rows),
        "duplicate_occurrences_beyond_first": sum(int(row["occurrence_count"]) - 1 for row in duplicate_rows),
        "identical_duplicate_id_values": sum(row["identical_role_content"] for row in duplicate_rows),
        "divergent_duplicate_id_values": sum(not row["identical_role_content"] for row in duplicate_rows),
        "max_occurrences_for_one_id": max(int(row["occurrence_count"]) for row in duplicate_rows),
        "affected_source_questions": sum(int(row["ambiguous_source_id_count"]) > 0 for row in question_rows),
        "affected_source_questions_all_duplicate_payloads_identical": sum(
            row["all_ambiguous_occurrences_text_identical"] for row in question_anomaly_rows
        ),
        "nonexact_question_category_counts": dict(
            Counter(row["category"] for row in question_anomaly_rows)
        ),
        "retrieval_quality_computed": False,
    }
    (args.output / "anomaly_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
