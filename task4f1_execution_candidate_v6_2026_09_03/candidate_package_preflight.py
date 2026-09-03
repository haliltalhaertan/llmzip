#!/usr/bin/env python3
"""No-outcome recursive byte, AST and single-source preflight for the Task 4F1 V6 candidate."""

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

# Token shapes that carry load-bearing values in this package. The sweep is what makes the
# gate's claim provable: it does not ask "are the declared mirrors equal?", it asks
# "does every value-shaped token in the closure belong to a declared concept and sit only
# where that concept permits?".
# Lookarounds stop a 64-hex digest also matching as its own 40-hex prefix.
TOKEN_PATTERNS = (
    re.compile(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])"),   # sha256 digests
    re.compile(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])"),   # git commit / blob sha1
    re.compile(r"v52_t4f[0-9][a-z0-9_]*"),                  # V52 identifiers
)


def json_token_paths(value, patterns, prefix="") -> dict:
    """Map each discovered token to the set of JSON key paths carrying it.

    Exemptions are scoped to key paths rather than whole files, so declaring the seal's
    provenance block exempt cannot silently excuse a normative literal elsewhere in it.
    """
    out: dict[str, set[str]] = {}
    if isinstance(value, dict):
        for key, sub in value.items():
            for token, paths in json_token_paths(sub, patterns, f"{prefix}.{key}" if prefix else key).items():
                out.setdefault(token, set()).update(paths)
    elif isinstance(value, list):
        for item in value:
            for token, paths in json_token_paths(item, patterns, f"{prefix}[]").items():
                out.setdefault(token, set()).update(paths)
    elif isinstance(value, str):
        text = normalise(value)
        for pattern in patterns:
            for token in pattern.findall(text):
                out.setdefault(token, set()).add(prefix)
    return out


def normalise(text: str) -> str:
    """Fold case and strip every whitespace character.

    V5's scan compared raw text line by line, so the same digest wrapped across two lines
    or written in uppercase slipped past it. Both defeats disappear once the haystack and
    the needle are normalised the same way.
    """
    return re.sub(r"\s+", "", text).casefold()


def single_source_gate() -> dict:
    """Sweep the bound closure and hold every discovered value-shaped token to account.

    The claim is: every load-bearing concept has exactly one enumerated normative source;
    every occurrence of its value elsewhere is a declared, typed mirror; no superseded
    literal survives anywhere; and no value-shaped token exists that no concept claims.
    """
    source_map = json.loads((ROOT / "NORMATIVE_SOURCE_MAP.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "PAYLOAD_HASHES.json").read_text(encoding="utf-8"))
    bound = sorted(
        {item["name"] for item in manifest["files"]}
        | {"PAYLOAD_HASHES.json", "CANDIDATE_EXECUTION_SEAL.json"}
    )
    report = {"bound_payloads": bound, "concepts": len(source_map["fields"])}

    runner_sha = sha256(ROOT / "v52_t4f1_beam_retrieval.py")
    if runner_sha != V4_ACCEPTED_RUNNER_SHA256:
        raise RuntimeError(f"[BLOCKED - RUNNER NOT BYTE-IDENTICAL TO ACCEPTED V4] {runner_sha}")
    report["runner_identical_to_accepted_v4"] = True

    # --- structural rules on the map itself -------------------------------------------
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
        for path in [field["authoritative_path"], *(m["path"] for m in field.get("mirrors", []))]:
            if path.startswith("EXTERNAL:"):
                continue
            if not (ROOT / path).exists() and not (ROOT.parent / path).exists():
                raise RuntimeError(f"[BLOCKED - UNRESOLVABLE DECLARED PATH] {concept} -> {path}")

    # --- build the attribution table ---------------------------------------------------
    # token -> (concept, permitted paths). Tokens come from declared scannable literals.
    attribution: dict[str, tuple[str, set[str]]] = {}
    for field in source_map["fields"]:
        permitted = {field["authoritative_path"], *(m["path"] for m in field.get("mirrors", []))}
        for literal in field.get("scannable_literals", []):
            key = normalise(literal)
            if key in attribution and attribution[key][0] != field["concept"]:
                raise RuntimeError(
                    f"[BLOCKED - LITERAL CLAIMED BY TWO CONCEPTS] {literal}"
                )
            attribution[key] = (field["concept"], permitted)
    deprecated = {normalise(e["literal"]): e for e in source_map["deprecated_literals"]}

    # --- sweep every bound payload ------------------------------------------------------
    # The map's "fields" and "deprecated_literals" blocks ARE the declaration site: a concept's
    # value and a deprecated literal must appear there and nowhere else. Exempt exactly those two
    # blocks by re-serialising the map without them, so the rest of the map -- its prose, rules and
    # exempt-class declarations -- is still swept under the ordinary rules and the exemption cannot
    # be widened by editing text around a literal.
    registry = dict(source_map)
    registry.pop("deprecated_literals", None)
    registry.pop("fields", None)
    exempt_text = json.dumps(registry, indent=2, sort_keys=True)

    exempt_classes = source_map.get("non_normative_token_classes", [])

    def exempted(name: str, token: str, key_paths: set[str]) -> bool:
        for cls in exempt_classes:
            if name not in cls.get("files", []):
                continue
            if cls.get("token_allowlist") and token in {normalise(t) for t in cls["token_allowlist"]}:
                return True
            prefixes = cls.get("json_key_prefixes")
            if prefixes and key_paths and all(
                any(kp == pre or kp.startswith(pre) for pre in prefixes) for kp in key_paths
            ):
                return True
        return False

    undeclared_location = []
    unattributed = []
    deprecated_survivors = []
    swept = 0
    for name in bound:
        path = ROOT / name
        try:
            raw = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        text = exempt_text if name == "NORMATIVE_SOURCE_MAP.json" else raw
        haystack = normalise(text)
        swept += 1

        for key, entry in deprecated.items():
            if entry.get("must_not_appear_as_requirement", True) and key in haystack:
                deprecated_survivors.append({"file": name, "literal": entry["literal"]})

        key_paths: dict[str, set[str]] = {}
        if name.endswith(".json"):
            try:
                key_paths = json_token_paths(json.loads(text), TOKEN_PATTERNS)
            except json.JSONDecodeError:
                key_paths = {}

        found = set()
        for pattern in TOKEN_PATTERNS:
            found.update(pattern.findall(haystack))
        for token in sorted(found):
            if token in deprecated:
                continue
            if exempted(name, token, key_paths.get(token, set())):
                continue
            if token not in attribution:
                unattributed.append({"file": name, "token": token})
                continue
            concept, permitted = attribution[token]
            if name not in permitted:
                undeclared_location.append({"file": name, "token": token, "concept": concept})

    if deprecated_survivors:
        raise RuntimeError(f"[BLOCKED - DEPRECATED LITERAL SURVIVES] {deprecated_survivors}")
    if unattributed:
        raise RuntimeError(f"[BLOCKED - UNATTRIBUTED LOAD-BEARING TOKEN] {unattributed}")
    if undeclared_location:
        raise RuntimeError(f"[BLOCKED - UNDECLARED REPETITION] {undeclared_location}")
    report.update(
        payloads_swept=swept,
        tracked_literals=len(attribution),
        deprecated_literal_survivors=0,
        unattributed_tokens=0,
        undeclared_repetitions=0,
    )

    # --- attestation and submission-status semantics -------------------------------------
    seal = json.loads((ROOT / "CANDIDATE_EXECUTION_SEAL.json").read_text(encoding="utf-8"))
    submission = next(f for f in source_map["fields"] if f["concept"] == "candidate_submission_status")
    if seal.get("status_at_audit_submission") != submission["value"]:
        raise RuntimeError("[BLOCKED - MIRROR DISAGREES] status_at_audit_submission")
    if "status" in seal and seal.get("status") != seal.get("status_at_audit_submission"):
        raise RuntimeError("[BLOCKED - SEAL CLAIMS POST-AUDIT STATE]")
    if "status" in manifest:
        raise RuntimeError("[BLOCKED - INVENTORY CARRIES A SECOND STATUS FIELD]")
    acceptance = next(f for f in source_map["fields"] if f["concept"] == "post_audit_acceptance_state")
    attestation = ROOT.parent / acceptance["authoritative_path"]
    if not attestation.is_file():
        raise RuntimeError(f"[BLOCKED - ATTESTATION PATH NOT RESOLVABLE] {acceptance['authoritative_path']}")
    record = json.loads(attestation.read_text(encoding="utf-8"))
    if record.get("acceptance_state") != acceptance["value"]:
        raise RuntimeError("[BLOCKED - ATTESTATION DISAGREES WITH DECLARED STATE]")
    report["attestation"] = acceptance["authoritative_path"]
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
        f"{gate_report['payloads_swept']} payloads swept for value-shaped tokens; "
        f"{gate_report['tracked_literals']} tracked literals; "
        f"{gate_report['unattributed_tokens']} unattributed; "
        f"{gate_report['undeclared_repetitions']} undeclared repetitions; "
        f"{gate_report['deprecated_literal_survivors']} deprecated literals surviving; "
        "runner byte-identical to the accepted V4 runner"
    )
    print("BLOCKED: independent execution-code audit and Head Researcher authorization are still required")


if __name__ == "__main__":
    main()
