#!/usr/bin/env python3
"""No-outcome byte and AST preflight for the Task 4F1 implementation candidate."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    manifest_path = ROOT / "PAYLOAD_HASHES.json"
    seal_path = ROOT / "CANDIDATE_EXECUTION_SEAL.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    seal = json.loads(seal_path.read_text(encoding="utf-8"))
    if seal["status"] != "PREPARED_NOT_INDEPENDENTLY_AUDITED":
        raise RuntimeError("candidate status must remain prepared")
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
    actual = {path.name for path in ROOT.iterdir() if path.is_file()} - {
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
    template = json.loads((ROOT / "RUN_AUTHORIZATION_TEMPLATE.json").read_text(encoding="utf-8"))
    if template["status"] != "NOT_AUTHORIZED" or template["retrieval_quality_outcome_access"] != "FORBIDDEN":
        raise RuntimeError("authorization template is unsafe")
    print("PASS: candidate payload closure, blocked authorization, script binding, and archive-fit AST boundary")
    print("BLOCKED: independent execution-code audit and Head Researcher authorization are still required")


if __name__ == "__main__":
    main()
