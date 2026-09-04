#!/usr/bin/env python3
"""Cryptographic/provenance gate for authorized Task 4F1 post-run analysis.

This module parses no retrieval ranking or metric value. It verifies only file identities, the
runner-produced post-run manifest, the production execution seal, and the HMAC-signed run
authorization. It is designed to run immediately before the exact-rational outcome analyzer.

The HMAC secret is read only from V52_T4F1_AUTH_HMAC_KEY_HEX and is never printed or persisted.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Any

ACCEPTED_RUNNER_SHA256 = "f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8"
EXPECTED_COHORT_SHA256 = "9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a"
EXPECTED_PREREG_SEAL_SHA256 = "e906c6d2b68b103c6c21906cbdf44acba10e31b7e5e17ffd2c7d1bbfb7a95cf4"
EXPECTED_ARCHIVES = 96
EXPECTED_QUESTIONS = 1712
EXPECTED_TRIAL_ROWS = 547840
AUTH_SCHEMA = "V52_T4F1_RUN_AUTHORIZATION_V4"
AUTH_HMAC_ENV = "V52_T4F1_AUTH_HMAC_KEY_HEX"
AUTH_SIGNED_FIELDS = (
    "schema",
    "status",
    "retrieval_quality_outcome_access",
    "execution_script_sha256",
    "execution_candidate_seal_sha256",
    "cohort_sha256",
    "required_archive_count",
    "output_namespace_basename",
    "preregistration_seal_sha256",
    "authorization_id",
    "authorization_nonce",
)
EXPECTED_MANIFEST_OUTPUTS = {
    "V52_T4F1_question_seed_level.csv",
    "V52_T4F1_question_level.csv",
    "V52_T4F1_aggregate.csv",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def require_hex64(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
        raise RuntimeError(f"[BLOCKED - INVALID {label}]" )
    return value


def load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"[BLOCKED - MISSING {label}] {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"[BLOCKED - MALFORMED {label}] {path}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"[BLOCKED - NON-OBJECT {label}] {path}")
    return value


def verify_execution_seal(path: Path) -> tuple[dict[str, Any], str, bytes]:
    seal = load_json(path, "EXECUTION SEAL")
    if seal.get("schema") != "V52_T4F1_EXECUTION_CANDIDATE_SEAL_V4":
        raise RuntimeError("[BLOCKED - EXECUTION SEAL SCHEMA]")
    if seal.get("implementation", {}).get("sha256") != ACCEPTED_RUNNER_SHA256:
        raise RuntimeError("[BLOCKED - EXECUTION SEAL RUNNER BINDING]")
    if seal.get("authorization", {}).get("task_4f1_run") != "BLOCKED":
        raise RuntimeError("[BLOCKED - EXECUTION SEAL RUN BOUNDARY]")
    control = seal.get("authorization_control", {})
    if (
        control.get("scheme") != "HMAC-SHA256"
        or control.get("key_environment_variable") != AUTH_HMAC_ENV
        or tuple(control.get("signed_fields", ())) != AUTH_SIGNED_FIELDS
    ):
        raise RuntimeError("[BLOCKED - EXECUTION SEAL AUTH CONTROL]")
    commitment = require_hex64(control.get("key_commitment_sha256"), "KEY COMMITMENT")
    secret_hex = os.environ.get(AUTH_HMAC_ENV)
    if secret_hex is None:
        raise RuntimeError("[BLOCKED - HEAD RESEARCHER AUTHORITY KEY MISSING]")
    try:
        secret = bytes.fromhex(secret_hex)
    except ValueError as exc:
        raise RuntimeError("[BLOCKED - HEAD RESEARCHER AUTHORITY KEY FORMAT]") from exc
    if len(secret) != 32 or hashlib.sha256(secret).hexdigest() != commitment:
        raise RuntimeError("[BLOCKED - HEAD RESEARCHER AUTHORITY KEY MISMATCH]")
    return seal, sha256_file(path), secret


def verify_authorization(
    path: Path,
    execution_seal_sha256: str,
    cohort_sha256: str,
    output_dir: Path,
    secret: bytes,
) -> tuple[dict[str, Any], str]:
    authorization = load_json(path, "RUN AUTHORIZATION")
    exact_keys = set(AUTH_SIGNED_FIELDS) | {"authorization_hmac_sha256"}
    if set(authorization) != exact_keys:
        raise RuntimeError("[BLOCKED - AUTHORIZATION FIELD SET]")
    expected = {
        "schema": AUTH_SCHEMA,
        "status": "AUTHORIZED_FOR_TASK_4F1_EXECUTION",
        "retrieval_quality_outcome_access": "AUTHORIZED",
        "execution_script_sha256": ACCEPTED_RUNNER_SHA256,
        "execution_candidate_seal_sha256": execution_seal_sha256,
        "cohort_sha256": cohort_sha256,
        "required_archive_count": EXPECTED_ARCHIVES,
        "output_namespace_basename": output_dir.name,
        "preregistration_seal_sha256": EXPECTED_PREREG_SEAL_SHA256,
    }
    mismatches = {
        key: {"expected": value, "observed": authorization.get(key)}
        for key, value in expected.items()
        if authorization.get(key) != value
    }
    if mismatches:
        raise RuntimeError("[BLOCKED - AUTHORIZATION BINDING] " + json.dumps(mismatches, sort_keys=True))
    require_hex64(authorization.get("authorization_nonce"), "AUTHORIZATION NONCE")
    auth_id = authorization.get("authorization_id")
    if not isinstance(auth_id, str) or not auth_id.startswith("V52-T4F1-"):
        raise RuntimeError("[BLOCKED - AUTHORIZATION ID]")
    signed_payload = {field: authorization[field] for field in AUTH_SIGNED_FIELDS}
    expected_hmac = hmac.new(secret, canonical_json_bytes(signed_payload), hashlib.sha256).hexdigest()
    observed_hmac = authorization.get("authorization_hmac_sha256")
    if not isinstance(observed_hmac, str) or not hmac.compare_digest(observed_hmac, expected_hmac):
        raise RuntimeError("[BLOCKED - AUTHORIZATION HMAC]")
    return authorization, sha256_file(path)


def verify_post_run_manifest(
    results_dir: Path,
    authorization_sha256: str,
    execution_seal_sha256: str,
    cohort_sha256: str,
) -> tuple[dict[str, Any], str]:
    manifest_path = results_dir / "V52_T4F1_POST_RUN_MANIFEST.json"
    manifest = load_json(manifest_path, "POST-RUN MANIFEST")
    expected = {
        "schema": "V52_T4F1_POST_RUN_MANIFEST_V4",
        "status": "COMPLETE_PENDING_INDEPENDENT_RESULT_AUDIT",
        "script_sha256": ACCEPTED_RUNNER_SHA256,
        "cohort_sha256": cohort_sha256,
        "run_authorization_sha256": authorization_sha256,
        "execution_candidate_seal_sha256": execution_seal_sha256,
        "question_denominator": EXPECTED_QUESTIONS,
        "archive_count": EXPECTED_ARCHIVES,
        "trial_rows": EXPECTED_TRIAL_ROWS,
        "console_outcomes_emitted": False,
        "interpretation_authorized": False,
    }
    mismatches = {
        key: {"expected": value, "observed": manifest.get(key)}
        for key, value in expected.items()
        if manifest.get(key) != value
    }
    if mismatches:
        raise RuntimeError("[BLOCKED - POST-RUN MANIFEST BINDING] " + json.dumps(mismatches, sort_keys=True))

    evidence = manifest.get("archive_evidence")
    if not isinstance(evidence, list) or len(evidence) != EXPECTED_ARCHIVES:
        raise RuntimeError("[BLOCKED - ARCHIVE EVIDENCE COUNT]")
    seen = set()
    for item in evidence:
        if not isinstance(item, dict) or set(item) != {"archive_id", "csv_sha256", "meta_sha256"}:
            raise RuntimeError("[BLOCKED - ARCHIVE EVIDENCE SCHEMA]")
        archive_id = item["archive_id"]
        if not isinstance(archive_id, str) or archive_id in seen:
            raise RuntimeError("[BLOCKED - ARCHIVE EVIDENCE ID]")
        seen.add(archive_id)
        safe = archive_id.replace("::", "__")
        csv_path = results_dir / "archives" / f"{safe}.csv"
        meta_path = results_dir / "archives" / f"{safe}.meta.json"
        if not csv_path.is_file() or sha256_file(csv_path) != item.get("csv_sha256"):
            raise RuntimeError(f"[BLOCKED - ARCHIVE CSV MANIFEST HASH] {archive_id}")
        if not meta_path.is_file() or sha256_file(meta_path) != item.get("meta_sha256"):
            raise RuntimeError(f"[BLOCKED - ARCHIVE META MANIFEST HASH] {archive_id}")

    outputs = manifest.get("outputs")
    if not isinstance(outputs, list) or len(outputs) != len(EXPECTED_MANIFEST_OUTPUTS):
        raise RuntimeError("[BLOCKED - POST-RUN OUTPUT MANIFEST COUNT]")
    names = set()
    for item in outputs:
        if not isinstance(item, dict) or set(item) != {"name", "bytes", "sha256"}:
            raise RuntimeError("[BLOCKED - POST-RUN OUTPUT MANIFEST SCHEMA]")
        name = item["name"]
        names.add(name)
        path = results_dir / name
        if not path.is_file() or path.stat().st_size != item["bytes"] or sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"[BLOCKED - POST-RUN OUTPUT HASH] {name}")
    if names != EXPECTED_MANIFEST_OUTPUTS:
        raise RuntimeError(f"[BLOCKED - POST-RUN OUTPUT NAMES] {sorted(names)}")
    return manifest, sha256_file(manifest_path)


def verify(
    cohort_path: Path,
    prereg_seal_path: Path,
    execution_seal_path: Path,
    authorization_path: Path,
    results_dir: Path,
) -> dict[str, Any]:
    cohort_sha = sha256_file(cohort_path) if cohort_path.is_file() else ""
    if cohort_sha != EXPECTED_COHORT_SHA256:
        raise RuntimeError("[BLOCKED - COHORT SHA256]")
    prereg_sha = sha256_file(prereg_seal_path) if prereg_seal_path.is_file() else ""
    if prereg_sha != EXPECTED_PREREG_SEAL_SHA256:
        raise RuntimeError("[BLOCKED - PREREGISTRATION SEAL SHA256]")
    _, execution_seal_sha, secret = verify_execution_seal(execution_seal_path)
    _, authorization_sha = verify_authorization(
        authorization_path, execution_seal_sha, cohort_sha, results_dir, secret
    )
    _, manifest_sha = verify_post_run_manifest(
        results_dir, authorization_sha, execution_seal_sha, cohort_sha
    )
    return {
        "status": "PASS",
        "runner_sha256": ACCEPTED_RUNNER_SHA256,
        "cohort_sha256": cohort_sha,
        "preregistration_seal_sha256": prereg_sha,
        "execution_candidate_seal_sha256": execution_seal_sha,
        "run_authorization_sha256": authorization_sha,
        "post_run_manifest_sha256": manifest_sha,
        "hmac_verified": True,
        "retrieval_quality_values_parsed_by_this_gate": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", type=Path, required=True)
    parser.add_argument("--prereg-seal", type=Path, required=True)
    parser.add_argument("--execution-seal", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()
    report = verify(
        args.cohort, args.prereg_seal, args.execution_seal, args.authorization, args.results_dir
    )
    print("T4F1_POST_RUN_PROVENANCE: PASS")
    for key, value in report.items():
        if key != "status":
            print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
