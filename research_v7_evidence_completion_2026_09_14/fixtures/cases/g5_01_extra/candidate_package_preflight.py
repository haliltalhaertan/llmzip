#!/usr/bin/env python3
"""No-outcome recursive byte, AST and single-source preflight for the Task 4F1 V7 candidate."""

from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AUTH_HMAC_ENV = "V52_T4F1_AUTH_HMAC_KEY_HEX"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()



V4_ACCEPTED_RUNNER_SHA256 = "f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8"

# The bound payload is exactly this set of functional files and nothing else.
# Narrative documentation is deliberately NOT bound: it lives in docs/ on the canonical
# branch, is labelled non-normative there, and therefore cannot state a requirement.
EXPECTED_BOUND_PAYLOAD = frozenset({
    "v52_t4f1_beam_retrieval.py",      # the single normative source of every execution value
    "DEPENDENCY_LOCK.txt",             # functional; the runner verifies its digest
    "RUN_AUTHORIZATION_TEMPLATE.json", # inert placeholder; cannot authorize
    "candidate_package_preflight.py",  # this checker
})


def bound_payload_is_functional_only() -> dict:
    """Establish the consistency property structurally rather than by scanning text.

    Two earlier packages tried to prove that restated values agreed, and a third attempt
    tried to prohibit value-shaped literals by pattern. Independent audit defeated the
    first two, and this package's own fixtures defeated the third: any pattern over prose
    loses to line wrapping, case, zero-width characters, markup or re-encoding.

    So no prose is bound. The claim becomes a set equality over file names, which no
    encoding trick can evade: the bound payload contains only the functional files above,
    so there is no bound document in which a requirement could be restated at all.
    """
    manifest = json.loads((ROOT / "PAYLOAD_HASHES.json").read_text(encoding="utf-8"))
    declared = {item["name"] for item in manifest["files"]}
    if declared != set(EXPECTED_BOUND_PAYLOAD):
        raise RuntimeError(
            "[BLOCKED - BOUND PAYLOAD IS NOT FUNCTIONAL-ONLY] "
            f"unexpected={sorted(declared - EXPECTED_BOUND_PAYLOAD)} "
            f"missing={sorted(EXPECTED_BOUND_PAYLOAD - declared)}"
        )

    runner_sha = sha256(ROOT / "v52_t4f1_beam_retrieval.py")
    if runner_sha != V4_ACCEPTED_RUNNER_SHA256:
        raise RuntimeError(f"[BLOCKED - RUNNER NOT BYTE-IDENTICAL TO ACCEPTED V4] {runner_sha}")

    seal = json.loads((ROOT / "CANDIDATE_EXECUTION_SEAL.json").read_text(encoding="utf-8"))
    if seal.get("status_at_audit_submission") != "PREPARED_NOT_INDEPENDENTLY_AUDITED":
        raise RuntimeError("[BLOCKED - SUBMISSION STATUS]")
    for forbidden in ("status", "acceptance_state", "accepted", "sealed"):
        if forbidden in seal:
            raise RuntimeError(f"[BLOCKED - SEAL CLAIMS POST-AUDIT STATE] {forbidden}")
    if "status" in manifest:
        raise RuntimeError("[BLOCKED - INVENTORY CARRIES A STATUS FIELD]")

    return {"bound_payload": sorted(declared), "narrative_documents_bound": 0,
            "runner_identical_to_accepted_v4": True}


def main() -> None:
    manifest_path = ROOT / "PAYLOAD_HASHES.json"
    seal_path = ROOT / "CANDIDATE_EXECUTION_SEAL.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    seal = json.loads(seal_path.read_text(encoding="utf-8"))
    if seal["schema"] != "V52_T4F1_EXECUTION_CANDIDATE_SEAL_V4":
        raise RuntimeError("candidate seal schema mismatch")
    if seal.get("status_at_audit_submission") != "PREPARED_NOT_INDEPENDENTLY_AUDITED":
        raise RuntimeError("candidate submission status must remain prepared")
    if seal["authorization"] != {
        "task_4f1_preregistration": "BLOCKED",
        "task_4f1_run": "BLOCKED",
        "retrieval_quality_outcome_access": "FORBIDDEN",
        "independent_execution_code_audit": "PENDING",
    }:
        raise RuntimeError("candidate authorization boundary mismatch")
    if sha256(manifest_path) != seal["payload_inventory"]["sha256"]:
        raise RuntimeError("payload inventory binding mismatch")
    declared = {item["name"] for item in manifest["files"]}
    actual = {path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*") if path.is_file()} - {
        "PAYLOAD_HASHES.json",
        "CANDIDATE_EXECUTION_SEAL.json",
    }
    if declared != actual:
        raise RuntimeError(f"payload closure mismatch declared={sorted(declared)} actual={sorted(actual)}")
    for item in manifest["files"]:
        path = ROOT / item["name"]
        if path.stat().st_size != item["bytes"] or sha256(path) != item["sha256"]:
            raise RuntimeError(f"payload mismatch {item['name']}")

    runner = ROOT / "v52_t4f1_beam_retrieval.py"
    tree = ast.parse(runner.read_text(encoding="utf-8"))
    functions = {node.name: node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    fit = functions["fit_archive_representation"]
    fit_args = [argument.arg for argument in fit.args.args]
    if fit_args != ["memory_texts"]:
        raise RuntimeError("fit function accepts non-archive payload")
    fit_source = ast.get_source_segment(runner.read_text(encoding="utf-8"), fit) or ""
    forbidden_fit_tokens = ("question", "gold", "rubric", "answer", "source_id", "ability", "difficulty")
    if any(token in fit_source.lower() for token in forbidden_fit_tokens):
        raise RuntimeError("forbidden token in archive fit")
    main_source = ast.get_source_segment(runner.read_text(encoding="utf-8"), functions["main"]) or ""
    if "verify_run_authorization" not in main_source:
        raise RuntimeError("run authorization guard missing")
    authorization_control = seal.get("authorization_control", {})
    if authorization_control.get("scheme") != "HMAC-SHA256":
        raise RuntimeError("authorization scheme mismatch")
    if authorization_control.get("key_environment_variable") != AUTH_HMAC_ENV:
        raise RuntimeError("authorization key environment binding mismatch")
    if authorization_control.get("key_commitment_sha256") != "PENDING_HEAD_RESEARCHER_PREREGISTRATION":
        raise RuntimeError("candidate must remain fail-closed before preregistration")
    gate_report = bound_payload_is_functional_only()
    template = json.loads((ROOT / "RUN_AUTHORIZATION_TEMPLATE.json").read_text(encoding="utf-8"))
    if template["status"] != "NOT_AUTHORIZED" or template["retrieval_quality_outcome_access"] != "FORBIDDEN":
        raise RuntimeError("authorization template is unsafe")
    if template.get("authorization_hmac_sha256") != "NOT_PRESENT_TEMPLATE_CANNOT_AUTHORIZE":
        raise RuntimeError("authorization template must not contain a signature")
    print("PASS: recursive payload closure, fail-closed HMAC authorization, script binding, and archive-fit AST boundary")
    print(
        "PASS: bound payload is functional-only - "
        f"{len(gate_report['bound_payload'])} files, "
        f"{gate_report['narrative_documents_bound']} narrative documents bound; "
        "runner byte-identical to the accepted V4 runner; "
        "candidate asserts no post-audit acceptance state"
    )
    print("BLOCKED: independent execution-code audit and Head Researcher authorization are still required")


if __name__ == "__main__":
    main()
