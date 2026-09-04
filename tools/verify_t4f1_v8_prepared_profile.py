#!/usr/bin/env python3
"""Outcome-free verifier for the exact Task 4F1 V8 prepared execution profile.

V8 intentionally makes no generalized claim about future resealed mutations. This tool verifies
only the exact submitted profile bytes and their reference to the already-accepted runner.
It never imports or executes the runner and never reads retrieval-quality outcomes.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = ROOT / "task4f1_execution_profile_v8_2026_09_04"
SEAL = PROFILE_DIR / "CANDIDATE_EXECUTION_SEAL.json"
SIDECAR = PROFILE_DIR / "CANDIDATE_EXECUTION_SEAL.json.sha256"
RUNNER = ROOT / "task4f1_execution_candidate_v4_2026_09_01" / "v52_t4f1_beam_retrieval.py"

ACCEPTED_PROFILE_SHA256 = "d6c6f700a77607e12cddd0a99d83374172c2c1cd4e75fcc3ac1fd99b68b4f30b"
ACCEPTED_RUNNER_SHA256 = "f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8"
PROFILE_FILENAME = "CANDIDATE_EXECUTION_SEAL.json"
EXPECTED_PROFILE_FILES = {PROFILE_FILENAME, PROFILE_FILENAME + ".sha256"}
EXPECTED_TOP_FIELDS = {"authorization", "authorization_control", "implementation", "schema"}
EXPECTED_AUTH_FIELDS = {"task_4f1_run"}
EXPECTED_CONTROL_FIELDS = {
    "key_commitment_sha256", "key_environment_variable", "scheme", "signed_fields"
}
EXPECTED_IMPLEMENTATION_FIELDS = {"sha256"}
EXPECTED_SIGNED_FIELDS = [
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
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_sidecar(path: Path) -> tuple[str, str] | None:
    try:
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except (OSError, UnicodeError):
        return None
    if len(lines) != 1:
        return None
    parts = lines[0].split()
    if len(parts) != 2:
        return None
    digest, filename = parts
    if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
        return None
    return digest, filename


def verify_semantics(profile: dict) -> list[str]:
    fail: list[str] = []
    if set(profile) != EXPECTED_TOP_FIELDS:
        fail.append("unexpected top-level profile field set")
    if profile.get("schema") != "V52_T4F1_EXECUTION_CANDIDATE_SEAL_V4":
        fail.append("wrong execution-seal schema")

    auth = profile.get("authorization")
    if not isinstance(auth, dict) or set(auth) != EXPECTED_AUTH_FIELDS:
        fail.append("unexpected authorization field set")
    elif auth.get("task_4f1_run") != "BLOCKED":
        fail.append("prepared profile must keep Task 4F1 run BLOCKED")

    control = profile.get("authorization_control")
    if not isinstance(control, dict) or set(control) != EXPECTED_CONTROL_FIELDS:
        fail.append("unexpected authorization-control field set")
    else:
        if control.get("scheme") != "HMAC-SHA256":
            fail.append("wrong authorization scheme")
        if control.get("key_environment_variable") != "V52_T4F1_AUTH_HMAC_KEY_HEX":
            fail.append("wrong HMAC environment variable")
        if control.get("signed_fields") != EXPECTED_SIGNED_FIELDS:
            fail.append("authorization signed-field contract changed")
        if control.get("key_commitment_sha256") != "PENDING_HEAD_RESEARCHER_PREREGISTRATION":
            fail.append("prepared profile must not contain a production key commitment")

    impl = profile.get("implementation")
    if not isinstance(impl, dict) or set(impl) != EXPECTED_IMPLEMENTATION_FIELDS:
        fail.append("unexpected implementation field set")
    elif impl.get("sha256") != ACCEPTED_RUNNER_SHA256:
        fail.append("profile does not bind the accepted V4 runner")
    return fail


def main() -> int:
    fail: list[str] = []

    if not PROFILE_DIR.is_dir():
        fail.append("V8 profile directory missing")
    else:
        actual_files = {p.name for p in PROFILE_DIR.iterdir() if p.is_file()}
        if actual_files != EXPECTED_PROFILE_FILES:
            fail.append(
                f"V8 profile closure mismatch: actual={sorted(actual_files)} "
                f"expected={sorted(EXPECTED_PROFILE_FILES)}"
            )

    if not SEAL.is_file():
        fail.append("V8 prepared seal missing")
    else:
        actual_profile_sha = sha256(SEAL)
        if actual_profile_sha != ACCEPTED_PROFILE_SHA256:
            fail.append(
                f"V8 prepared profile identity mismatch: {actual_profile_sha} != {ACCEPTED_PROFILE_SHA256}"
            )
        try:
            profile = json.loads(SEAL.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            fail.append(f"V8 prepared profile unreadable: {exc}")
        else:
            fail.extend(verify_semantics(profile))

    sidecar = parse_sidecar(SIDECAR)
    if sidecar is None:
        fail.append("V8 profile sidecar missing or malformed")
    else:
        declared_sha, declared_name = sidecar
        if declared_sha != ACCEPTED_PROFILE_SHA256:
            fail.append("V8 profile sidecar digest mismatch")
        if declared_name != PROFILE_FILENAME:
            fail.append("V8 profile sidecar filename mismatch")

    if not RUNNER.is_file():
        fail.append("accepted V4 runner missing")
    elif sha256(RUNNER) != ACCEPTED_RUNNER_SHA256:
        fail.append("accepted V4 runner byte identity mismatch")

    if fail:
        print("T4F1_V8_PREPARED_PROFILE: BLOCKED")
        for item in fail:
            print(f"- {item}")
        return 1

    print("T4F1_V8_PREPARED_PROFILE: PASS")
    print(f"profile_sha256={ACCEPTED_PROFILE_SHA256}")
    print(f"runner_sha256={ACCEPTED_RUNNER_SHA256}")
    print("normative_execution_code_authorities=1")
    print("task_4f1_run=BLOCKED")
    print("production_key_commitment=ABSENT")
    print("outcome_access=FORBIDDEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
