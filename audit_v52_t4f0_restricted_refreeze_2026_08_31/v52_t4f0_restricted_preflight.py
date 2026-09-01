#!/usr/bin/env python3
"""Pre-outcome verifier for the V52 Task 4F0 restricted refreeze candidate.

This verifier intentionally does not load a BEAM corpus, fit a representation,
rank a query, or calculate retrieval-quality metrics. It checks the immutable
candidate package and its outcome-independent cohort only.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


EXPECTED_COHORT_SHA256 = "9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a"
EXPECTED_AUDIT_INVENTORY_SHA256 = "3b3bb1a25cd9c8b7a56e1c29afbe8b3589f0c5c5f4705c000b7625da6f64fa65"
EXPECTED_PARENT_LLMZIP_COMMIT = "d3c7aa09c9553cd5ac100e668923abab602e4257"
EXPECTED_BEAM_COMMIT = "3e12035532eb85768f1a7cd779832b650c4b2ef9"
EXCLUDED_ARCHIVES = {"1M::5", "1M::26", "1M::33", "1M::34"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"BLOCKED: {message}")


def verify_audit_inventory(root: Path) -> None:
    inventory = root.parent / "audit_v52_t4f0_codex_2026_08_31" / "AUDIT_OUTPUT_HASHES.json"
    require(inventory.is_file(), f"missing accepted audit inventory: {inventory}")
    require(sha256(inventory) == EXPECTED_AUDIT_INVENTORY_SHA256, "audit inventory digest mismatch")
    payload = json.loads(inventory.read_text(encoding="utf-8"))
    require(payload.get("file_count_excluding_self") == 33, "accepted audit inventory file count changed")
    require(payload.get("scientific_native_vs_haar_outcome_inspected") is False, "audit outcome flag is not false")
    audit_root = inventory.parent
    for item in payload["files"]:
        path = audit_root / item["name"]
        require(path.is_file(), f"missing audit payload: {item['name']}")
        require(path.stat().st_size == item["bytes"], f"audit size mismatch: {item['name']}")
        require(sha256(path) == item["sha256"], f"audit hash mismatch: {item['name']}")


def verify_cohort(root: Path) -> None:
    cohort = root / "estimand_primary_cohort.csv"
    summary = root / "estimand_summary.json"
    require(sha256(cohort) == EXPECTED_COHORT_SHA256, "restricted cohort digest mismatch")
    rows = list(csv.DictReader(cohort.open(encoding="utf-8", newline="")))
    require(len(rows) == 2000, f"expected 2000 cohort records, got {len(rows)}")
    eligible = [row for row in rows if row["primary_evidence_cohort_eligible"] == "True"]
    require(len(eligible) == 1712, f"expected 1712 eligible questions, got {len(eligible)}")
    for row in eligible:
        archive = f"{row['tier']}::{row['conversation_id']}"
        require(archive not in EXCLUDED_ARCHIVES, f"excluded archive entered cohort: {archive}")
        require(row["ability"] != "abstention", f"abstention entered cohort: {row['audit_question_id']}")
        require(row["audit_category"] == "EXACT_SOURCE_IDS", f"non-exact row entered cohort: {row['audit_question_id']}")
        require(int(row["gold_source_unit_count"]) > 0, f"eligible row has empty gold set: {row['audit_question_id']}")
    summary_data = json.loads(summary.read_text(encoding="utf-8"))
    require(summary_data["primary_evidence_questions"] == 1712, "summary cohort count changed")
    require(summary_data["gold_cardinality"]["questions_with_more_than_3_gold_units"] == 587, "ALL@3 structural-zero count changed")
    require(summary_data["retrieval_quality_computed"] is False, "cohort summary reports retrieval quality")


def verify_local_inventory_and_seal(root: Path) -> None:
    inventory_path = root / "PAYLOAD_HASHES.json"
    seal_path = root / "CANDIDATE_SEAL.json"
    require(inventory_path.is_file(), "local payload inventory missing")
    require(seal_path.is_file(), "candidate seal missing")
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    names = {item["name"] for item in inventory["files"]}
    require(inventory["file_count_excluding_inventory"] == len(names), "local payload inventory count mismatch")
    for item in inventory["files"]:
        path = root / item["name"]
        require(path.is_file(), f"missing local payload: {item['name']}")
        require(path.stat().st_size == item["bytes"], f"local size mismatch: {item['name']}")
        require(sha256(path) == item["sha256"], f"local hash mismatch: {item['name']}")
    unexpected = {
        path.name for path in root.iterdir() if path.is_file()
    } - names - {"PAYLOAD_HASHES.json", "CANDIDATE_SEAL.json"}
    require(not unexpected, f"unbound local payloads: {sorted(unexpected)}")
    seal = json.loads(seal_path.read_text(encoding="utf-8"))
    require(seal["status"] == "PREPARED_NOT_INDEPENDENTLY_SEALED", "candidate seal status changed")
    require(seal["parent_llmzip_commit"] == EXPECTED_PARENT_LLMZIP_COMMIT, "parent commit binding changed")
    require(seal["pinned_beam_commit"] == EXPECTED_BEAM_COMMIT, "BEAM commit binding changed")
    require(seal["prompt"]["sha256"] == sha256(root / "REFREEZE_PROTOCOL.md"), "seal prompt binding mismatch")
    require(seal["cohort"]["sha256"] == EXPECTED_COHORT_SHA256, "seal cohort binding mismatch")
    require(seal["payload_inventory"]["sha256"] == sha256(inventory_path), "seal inventory binding mismatch")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    root = args.root.resolve()
    require((root / "REFREEZE_PROTOCOL.md").is_file(), "protocol missing")
    require((root / "DEPENDENCY_LOCK.txt").is_file(), "dependency lock missing")
    require((root / "excluded_archives.txt").read_text(encoding="utf-8").splitlines() == sorted(EXCLUDED_ARCHIVES), "excluded archive bytes/order changed")
    verify_audit_inventory(root)
    verify_cohort(root)
    verify_local_inventory_and_seal(root)
    print("PASS: exact audit inventory, local payload closure, restricted cohort, exclusion rule, and no-outcome declarations verified")
    print("BLOCKED: independent sign-off and raw-corpus representation self-tests are still required")


if __name__ == "__main__":
    main()
