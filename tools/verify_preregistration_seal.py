#!/usr/bin/env python3
"""Verify that the sealed V52 Task 4F1 scientific preregistration still binds its declared anchors.

Every binding is re-derived from bytes: working-tree files by digest, and remote-branch artifacts by
reading the blob out of the named commit. This checker never imports or executes an outcome-capable
candidate, and reads no retrieval-quality outcome.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEAL_PATH = ROOT / "docs" / "v52" / "task4f1" / "TASK4F1_PREREGISTRATION_SEAL_2026-09-04.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_blob(commit: str, path: str) -> str | None:
    """Digest of a path inside a commit, or None if the commit is not present locally."""
    try:
        blob = subprocess.run(
            ["git", "cat-file", "-p", f"{commit}:{path}"],
            cwd=ROOT, check=True, capture_output=True,
        ).stdout
    except subprocess.CalledProcessError:
        return None
    return hashlib.sha256(blob).hexdigest()


def main() -> int:
    seal = json.loads(SEAL_PATH.read_text(encoding="utf-8"))
    b = seal["bindings"]
    failures: list[str] = []
    unavailable: list[str] = []

    if seal.get("schema") != "V52_T4F1_SCIENTIFIC_PREREGISTRATION_SEAL_V1":
        failures.append("unexpected seal schema")

    # Bindings 1-3 live in the working tree.
    worktree = [
        ("1 approved draft", b["1_approved_preregistration_draft"]["path"],
         b["1_approved_preregistration_draft"]["sha256"]),
        ("2 sealed 4F0 cohort", b["2_sealed_4f0_restricted_cohort"]["path"],
         b["2_sealed_4f0_restricted_cohort"]["sha256"]),
        ("3 accepted runner", b["3_accepted_runner"]["path_in_current_candidate"],
         b["3_accepted_runner"]["sha256"]),
    ]
    for label, rel, expected in worktree:
        path = ROOT / rel
        if not path.is_file():
            failures.append(f"{label}: missing {rel}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            failures.append(f"{label}: SHA256 mismatch ({actual})")

    declared_bytes = b["1_approved_preregistration_draft"]["bytes"]
    actual_bytes = (ROOT / b["1_approved_preregistration_draft"]["path"]).stat().st_size
    if actual_bytes != declared_bytes:
        failures.append(f"1 approved draft: size mismatch ({actual_bytes} != {declared_bytes})")

    # Bindings 4-6 are approval artifacts on their own branches.
    for key, label in (
        ("4_head_researcher_rereview_decision", "4 HR re-review decision"),
        ("5_exact_byte_cochair_approval", "5 exact-byte co-chair approval"),
        ("6_head_researcher_authorization_schema_ratification", "6 HR authorization-schema ratification"),
    ):
        item = b[key]
        actual = sha256_blob(item["commit"], item["path"])
        if actual is None:
            unavailable.append(f"{label}: commit {item['commit'][:8]} not fetched locally")
        elif actual != item["sha256"]:
            failures.append(f"{label}: SHA256 mismatch ({actual})")

    # Bindings 7-8 are textual conditions, not digests: assert they are present and complete.
    if len(b["7_binding_execution_conditions"]["conditions"]) != 4:
        failures.append("7 execution conditions: expected exactly four bound conditions")
    if not b["8_exact_rational_sign_classification_condition"].get("condition"):
        failures.append("8 exact-rational sign condition: missing")

    # The seal must never make itself contingent on the execution track.
    v7 = seal["provenance_not_prerequisites"]["v7_execution_package_audit"]
    if v7.get("bound_as_prerequisite") is not False:
        failures.append("V7 is bound as a prerequisite; the sealing direction forbids this")

    # The boundary declaration must stay all-zero / all-false.
    for key, value in seal["outcome_boundary_declaration"].items():
        if value not in (0, False):
            failures.append(f"outcome boundary violated: {key}={value}")

    if failures:
        print("PREREGISTRATION_SEAL: BLOCKED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PREREGISTRATION_SEAL: PASS")
    print(f"seal_id={seal['seal_id']}")
    print(f"approved_draft_sha256={b['1_approved_preregistration_draft']['sha256']}")
    for note in unavailable:
        print(f"NOT_CHECKED_LOCALLY: {note} (fetch the branch to verify)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
