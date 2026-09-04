#!/usr/bin/env python3
"""Head-Researcher-only pre-run authorization release attestation for Task 4F1.

This tool is PREPARED code only; running it with a production authorization is itself a load-bearing
pre-run act and must not occur until all preceding gates are accepted. It verifies the HMAC using the
single-use secret held in V52_T4F1_AUTH_HMAC_KEY_HEX, then writes a NON-SECRET attestation binding
the exact authorization SHA. The secret is never printed or persisted.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROVENANCE_PATH = ROOT / "tools" / "t4f1_verify_post_run_provenance.py"


def load_provenance():
    spec = importlib.util.spec_from_file_location("t4f1_post_run_provenance", PROVENANCE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load provenance module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", type=Path, required=True)
    parser.add_argument("--prereg-seal", type=Path, required=True)
    parser.add_argument("--execution-seal", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--attestation-output", type=Path, required=True)
    args = parser.parse_args()

    if args.attestation_output.exists():
        raise RuntimeError(f"[BLOCKED - REFUSE ATTESTATION OVERWRITE] {args.attestation_output}")
    if args.output_dir.exists():
        raise RuntimeError(f"[BLOCKED - PRODUCTION OUTPUT NAMESPACE ALREADY EXISTS] {args.output_dir}")

    p = load_provenance()
    cohort_sha = p.sha256_file(args.cohort) if args.cohort.is_file() else ""
    if cohort_sha != p.EXPECTED_COHORT_SHA256:
        raise RuntimeError("[BLOCKED - COHORT SHA256]")
    prereg_sha = p.sha256_file(args.prereg_seal) if args.prereg_seal.is_file() else ""
    if prereg_sha != p.EXPECTED_PREREG_SEAL_SHA256:
        raise RuntimeError("[BLOCKED - PREREGISTRATION SEAL SHA256]")

    _, execution_seal_sha, commitment = p.verify_execution_seal_public(args.execution_seal)
    authorization, authorization_sha = p.verify_authorization_public(
        args.authorization, execution_seal_sha, cohort_sha, args.output_dir
    )

    secret_hex = os.environ.get(p.AUTH_HMAC_ENV)
    if secret_hex is None:
        raise RuntimeError("[BLOCKED - HEAD RESEARCHER AUTHORITY KEY MISSING]")
    try:
        secret = bytes.fromhex(secret_hex)
    except ValueError as exc:
        raise RuntimeError("[BLOCKED - HEAD RESEARCHER AUTHORITY KEY FORMAT]") from exc
    if len(secret) != 32:
        raise RuntimeError("[BLOCKED - HEAD RESEARCHER AUTHORITY KEY LENGTH]")
    if hashlib.sha256(secret).hexdigest() != commitment:
        raise RuntimeError("[BLOCKED - HEAD RESEARCHER AUTHORITY KEY COMMITMENT MISMATCH]")

    signed_payload = {field: authorization[field] for field in p.AUTH_SIGNED_FIELDS}
    expected_hmac = hmac.new(secret, p.canonical_json_bytes(signed_payload), hashlib.sha256).hexdigest()
    observed_hmac = authorization["authorization_hmac_sha256"]
    if not hmac.compare_digest(observed_hmac, expected_hmac):
        raise RuntimeError("[BLOCKED - AUTHORIZATION HMAC]")

    attestation = {
        "schema": p.AUTH_RELEASE_SCHEMA,
        "status": "AUTHORIZATION_VERIFIED_AND_RELEASED_FOR_SINGLE_USE",
        "runner_sha256": p.ACCEPTED_RUNNER_SHA256,
        "execution_candidate_seal_sha256": execution_seal_sha,
        "cohort_sha256": cohort_sha,
        "preregistration_seal_sha256": prereg_sha,
        "run_authorization_sha256": authorization_sha,
        "output_namespace_basename": args.output_dir.name,
        "authorization_id": authorization["authorization_id"],
        "authorization_nonce": authorization["authorization_nonce"],
        "hmac_verified_by_head_researcher": True,
        "hmac_key_disclosed_or_persisted": False,
        "single_use": True,
    }
    if set(attestation) != p.AUTH_RELEASE_FIELDS:
        raise RuntimeError("[BLOCKED - INTERNAL ATTESTATION FIELD SET]")

    args.attestation_output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.attestation_output.with_name(args.attestation_output.name + ".tmp")
    if temporary.exists():
        temporary.unlink()
    temporary.write_bytes(p.canonical_json_bytes(attestation))
    temporary.replace(args.attestation_output)

    print("T4F1_AUTHORIZATION_RELEASE_ATTESTATION: PASS")
    print(f"attestation={args.attestation_output}")
    print(f"attestation_sha256={sha256_file(args.attestation_output)}")
    print(f"run_authorization_sha256={authorization_sha}")
    print("hmac_verified=True")
    print("hmac_key_disclosed_or_persisted=False")
    print("task_run_invoked=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
