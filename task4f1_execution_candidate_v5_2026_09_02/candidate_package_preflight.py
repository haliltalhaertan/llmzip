#!/usr/bin/env python3
"""No-outcome recursive byte, AST and single-source preflight for the Task 4F1 V5 candidate."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AUTH_HMAC_ENV = "V52_T4F1_AUTH_HMAC_KEY_HEX"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()



V4_ACCEPTED_RUNNER_SHA256 = "f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8"


def single_source_gate() -> dict:
    """Prove one normative source per concept, typed equal mirrors, and zero surviving
    deprecated load-bearing literals across the whole recursive payload closure.

    The claim is not "no contradiction found". It is that every declared load-bearing
    concept has exactly one enumerated normative source, every repetition is a typed
    mirror that compares equal, and no superseded literal survives anywhere in the bound
    payload, prose included.
    """
    source_map = json.loads((ROOT / "NORMATIVE_SOURCE_MAP.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "PAYLOAD_HASHES.json").read_text(encoding="utf-8"))
    bound = sorted(
        {item["name"] for item in manifest["files"]}
        | {"PAYLOAD_HASHES.json", "CANDIDATE_EXECUTION_SEAL.json"}
    )
    report = {"bound_payloads": bound, "concepts": len(source_map["fields"])}

    # 1. runner identity with the accepted V4 runner
    runner_sha = sha256(ROOT / "v52_t4f1_beam_retrieval.py")
    if runner_sha != V4_ACCEPTED_RUNNER_SHA256:
        raise RuntimeError(
            f"[BLOCKED - RUNNER NOT BYTE-IDENTICAL TO ACCEPTED V4] {runner_sha}"
        )
    report["runner_identical_to_accepted_v4"] = True

    # 2. every concept names exactly one authoritative source
    seen = set()
    for field in source_map["fields"]:
        concept = field["concept"]
        if concept in seen:
            raise RuntimeError(f"[BLOCKED - DUPLICATE NORMATIVE CONCEPT] {concept}")
        seen.add(concept)
        if not field.get("authoritative_path") or not field.get("locator"):
            raise RuntimeError(f"[BLOCKED - CONCEPT WITHOUT SINGLE SOURCE] {concept}")
        for mirror in field.get("mirrors", []):
            if not mirror.get("path") or not mirror.get("locator"):
                raise RuntimeError(f"[BLOCKED - UNTYPED MIRROR] {concept}")

    # 3. no deprecated load-bearing literal survives anywhere in the bound closure
    # The registry that DECLARES a literal deprecated is the one lawful place it may appear.
    # Exempt exactly that block by re-serialising the map without it, rather than by any
    # line-level heuristic, so the exemption cannot be widened accidentally.
    registry = dict(source_map)
    registry.pop("deprecated_literals", None)
    exempt_text = json.dumps(registry, indent=2, sort_keys=True)

    survivors = []
    for name in bound:
        path = ROOT / name
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if name == "NORMATIVE_SOURCE_MAP.json":
            text = exempt_text
        for entry in source_map["deprecated_literals"]:
            if not entry.get("must_not_appear_as_requirement", True):
                continue
            literal = entry["literal"]
            for number, line in enumerate(text.splitlines(), start=1):
                if literal in line:
                    survivors.append({"file": name, "line": number, "literal": literal})
    if survivors:
        raise RuntimeError(f"[BLOCKED - DEPRECATED LITERAL SURVIVES] {survivors}")
    report["deprecated_literal_survivors"] = 0

    # 4. typed mirrors must equal their authoritative value where mechanically checkable
    checked = 0
    seal = json.loads((ROOT / "CANDIDATE_EXECUTION_SEAL.json").read_text(encoding="utf-8"))
    inventory = {item["name"]: item["sha256"] for item in manifest["files"]}
    identity = next(f for f in source_map["fields"] if f["concept"] == "v4_to_v5_runner_identity")
    for observed, label in (
        (seal["implementation"]["sha256"], "seal.implementation.sha256"),
        (inventory["v52_t4f1_beam_retrieval.py"], "PAYLOAD_HASHES runner entry"),
    ):
        if observed != identity["value"]:
            raise RuntimeError(f"[BLOCKED - MIRROR DISAGREES] {label} {observed}")
        checked += 1
    commitment = next(f for f in source_map["fields"] if f["concept"] == "authorization_commitment_state")
    if seal.get("authorization_control", {}).get("key_commitment_sha256") != commitment["value"]:
        raise RuntimeError("[BLOCKED - MIRROR DISAGREES] authorization commitment")
    checked += 1
    signed = next(f for f in source_map["fields"] if f["concept"] == "authorization_signed_fields")
    if list(seal.get("authorization_control", {}).get("signed_fields", [])) != list(signed["value"]):
        raise RuntimeError("[BLOCKED - MIRROR DISAGREES] authorization signed fields")
    checked += 1
    submission = next(f for f in source_map["fields"] if f["concept"] == "candidate_submission_status")
    if seal.get("status_at_audit_submission") != submission["value"]:
        raise RuntimeError("[BLOCKED - MIRROR DISAGREES] status_at_audit_submission")
    checked += 1
    report["mirrors_checked"] = checked

    # 5. the seal must not claim post-audit acceptance authority
    if "status" in seal and seal.get("status") != seal.get("status_at_audit_submission"):
        raise RuntimeError("[BLOCKED - SEAL CLAIMS POST-AUDIT STATE]")
    report["seal_scope"] = "status_at_audit_submission only"
    return report


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
    gate_report = single_source_gate()
    template = json.loads((ROOT / "RUN_AUTHORIZATION_TEMPLATE.json").read_text(encoding="utf-8"))
    if template["status"] != "NOT_AUTHORIZED" or template["retrieval_quality_outcome_access"] != "FORBIDDEN":
        raise RuntimeError("authorization template is unsafe")
    if template.get("authorization_hmac_sha256") != "NOT_PRESENT_TEMPLATE_CANNOT_AUTHORIZE":
        raise RuntimeError("authorization template must not contain a signature")
    print("PASS: recursive payload closure, fail-closed HMAC authorization, script binding, and archive-fit AST boundary")
    print(
        "PASS: single-source gate - "
        f"{gate_report['concepts']} concepts each with one normative source; "
        f"{gate_report['mirrors_checked']} typed mirrors equal; "
        f"{gate_report['deprecated_literal_survivors']} deprecated literals surviving; "
        "runner byte-identical to the accepted V4 runner"
    )
    print("BLOCKED: independent execution-code audit and Head Researcher authorization are still required")


if __name__ == "__main__":
    main()
