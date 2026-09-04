#!/usr/bin/env python3
"""Outcome-free synthetic controls for Task 4F1 post-run provenance/HMAC gate."""

from __future__ import annotations

import copy
import hashlib
import hmac
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "tools" / "t4f1_verify_post_run_provenance.py"


def load_module():
    spec = importlib.util.spec_from_file_location("t4f1_provenance_gate", GATE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load provenance gate")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def expect_block(label: str, fn) -> bool:
    try:
        fn()
    except RuntimeError:
        print(f"ok   blocked: {label}")
        return True
    print(f"FAIL accepted: {label}")
    return False


def build_fixture(g, root: Path):
    cohort = root / "cohort.csv"
    prereg = root / "prereg.json"
    execution_seal = root / "execution_seal.json"
    authorization = root / "authorization.json"
    results = root / "results"
    archives = results / "archives"
    archives.mkdir(parents=True)
    cohort.write_bytes(b"synthetic cohort\n")
    prereg.write_bytes(b"synthetic prereg seal\n")

    g.EXPECTED_COHORT_SHA256 = g.sha256_file(cohort)
    g.EXPECTED_PREREG_SEAL_SHA256 = g.sha256_file(prereg)
    g.ACCEPTED_RUNNER_SHA256 = "a" * 64
    g.EXPECTED_ARCHIVES = 2
    g.EXPECTED_QUESTIONS = 1
    g.EXPECTED_TRIAL_ROWS = 1

    secret = bytes(range(32))
    os.environ[g.AUTH_HMAC_ENV] = secret.hex()
    commitment = hashlib.sha256(secret).hexdigest()
    seal = {
        "schema": "V52_T4F1_EXECUTION_CANDIDATE_SEAL_V4",
        "implementation": {"sha256": g.ACCEPTED_RUNNER_SHA256},
        "authorization": {"task_4f1_run": "BLOCKED"},
        "authorization_control": {
            "scheme": "HMAC-SHA256",
            "key_environment_variable": g.AUTH_HMAC_ENV,
            "signed_fields": list(g.AUTH_SIGNED_FIELDS),
            "key_commitment_sha256": commitment,
        },
    }
    write_json(execution_seal, seal)
    seal_sha = g.sha256_file(execution_seal)

    auth = {
        "schema": g.AUTH_SCHEMA,
        "status": "AUTHORIZED_FOR_TASK_4F1_EXECUTION",
        "retrieval_quality_outcome_access": "AUTHORIZED",
        "execution_script_sha256": g.ACCEPTED_RUNNER_SHA256,
        "execution_candidate_seal_sha256": seal_sha,
        "cohort_sha256": g.EXPECTED_COHORT_SHA256,
        "required_archive_count": g.EXPECTED_ARCHIVES,
        "output_namespace_basename": results.name,
        "preregistration_seal_sha256": g.EXPECTED_PREREG_SEAL_SHA256,
        "authorization_id": "V52-T4F1-SYNTHETIC",
        "authorization_nonce": "b" * 64,
    }
    signed = {field: auth[field] for field in g.AUTH_SIGNED_FIELDS}
    auth["authorization_hmac_sha256"] = hmac.new(secret, g.canonical_json_bytes(signed), hashlib.sha256).hexdigest()
    write_json(authorization, auth)
    auth_sha = g.sha256_file(authorization)

    evidence = []
    for archive_id in ("100K::synthetic-a", "100K::synthetic-b"):
        safe = archive_id.replace("::", "__")
        csv_path = archives / f"{safe}.csv"
        meta_path = archives / f"{safe}.meta.json"
        csv_path.write_bytes(f"synthetic csv {archive_id}\n".encode())
        meta_path.write_bytes(f"synthetic meta {archive_id}\n".encode())
        evidence.append({
            "archive_id": archive_id,
            "csv_sha256": g.sha256_file(csv_path),
            "meta_sha256": g.sha256_file(meta_path),
        })

    outputs = []
    for name in sorted(g.EXPECTED_MANIFEST_OUTPUTS):
        path = results / name
        path.write_bytes(f"synthetic output {name}\n".encode())
        outputs.append({"name": name, "bytes": path.stat().st_size, "sha256": g.sha256_file(path)})

    manifest = {
        "schema": "V52_T4F1_POST_RUN_MANIFEST_V4",
        "status": "COMPLETE_PENDING_INDEPENDENT_RESULT_AUDIT",
        "script_sha256": g.ACCEPTED_RUNNER_SHA256,
        "cohort_sha256": g.EXPECTED_COHORT_SHA256,
        "run_authorization_sha256": auth_sha,
        "execution_candidate_seal_sha256": seal_sha,
        "question_denominator": g.EXPECTED_QUESTIONS,
        "archive_count": g.EXPECTED_ARCHIVES,
        "trial_rows": g.EXPECTED_TRIAL_ROWS,
        "archive_evidence": evidence,
        "outputs": outputs,
        "console_outcomes_emitted": False,
        "interpretation_authorized": False,
    }
    write_json(results / "V52_T4F1_POST_RUN_MANIFEST.json", manifest)
    return cohort, prereg, execution_seal, authorization, results


def main() -> int:
    g = load_module()
    failures = 0
    total = 0
    old_env = os.environ.get(g.AUTH_HMAC_ENV)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cohort, prereg, seal, auth, results = build_fixture(g, root)

            total += 1
            try:
                report = g.verify(cohort, prereg, seal, auth, results)
            except RuntimeError as exc:
                print(f"FAIL valid synthetic provenance chain: {exc}")
                failures += 1
            else:
                if report.get("hmac_verified") is not True:
                    print("FAIL synthetic provenance did not verify HMAC")
                    failures += 1
                else:
                    print("ok   pass: valid synthetic HMAC/provenance chain")

            auth_original = auth.read_bytes()
            auth_obj = json.loads(auth_original)
            auth_obj["authorization_hmac_sha256"] = "0" * 64
            write_json(auth, auth_obj)
            total += 1
            if not expect_block("authorization HMAC changed", lambda: g.verify(cohort, prereg, seal, auth, results)):
                failures += 1
            auth.write_bytes(auth_original)

            manifest_path = results / "V52_T4F1_POST_RUN_MANIFEST.json"
            manifest_original = manifest_path.read_bytes()
            manifest_obj = json.loads(manifest_original)
            manifest_obj["script_sha256"] = "c" * 64
            write_json(manifest_path, manifest_obj)
            total += 1
            if not expect_block("manifest runner binding changed", lambda: g.verify(cohort, prereg, seal, auth, results)):
                failures += 1
            manifest_path.write_bytes(manifest_original)

            output_path = results / "V52_T4F1_aggregate.csv"
            output_original = output_path.read_bytes()
            output_path.write_bytes(output_original + b"tamper")
            total += 1
            if not expect_block("manifest-bound output tampered", lambda: g.verify(cohort, prereg, seal, auth, results)):
                failures += 1
            output_path.write_bytes(output_original)

            meta_path = results / "archives" / "100K__synthetic-a.meta.json"
            meta_original = meta_path.read_bytes()
            meta_path.write_bytes(meta_original + b"tamper")
            total += 1
            if not expect_block("archive metadata tampered", lambda: g.verify(cohort, prereg, seal, auth, results)):
                failures += 1
            meta_path.write_bytes(meta_original)

            saved_key = os.environ.pop(g.AUTH_HMAC_ENV)
            total += 1
            if not expect_block("HMAC key missing", lambda: g.verify(cohort, prereg, seal, auth, results)):
                failures += 1
            os.environ[g.AUTH_HMAC_ENV] = saved_key

    finally:
        if old_env is None:
            os.environ.pop(g.AUTH_HMAC_ENV, None)
        else:
            os.environ[g.AUTH_HMAC_ENV] = old_env

    print(f"\n{total - failures}/{total} outcome-free provenance controls behaved correctly")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
