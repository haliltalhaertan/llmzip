#!/usr/bin/env python3
"""Fail-closed authorization verification on invalid fixtures only.

Calls the runner's authorization verifier directly with the HMAC key environment
variable ABSENT, using the inert in-package template and fully synthetic fixtures.
No valid authorization is constructed: no HMAC key exists in this process, the seal
commitment is the literal PENDING_HEAD_RESEARCHER_PREREGISTRATION, and no signature
is ever computed. Never calls the archive-processing or finalization entry points.
"""
import hashlib, importlib.util, json, os, sys, tempfile
from pathlib import Path

AUTH_ENV = "V52_T4F1_AUTH_HMAC_KEY_HEX"
assert AUTH_ENV not in os.environ, "refusing to proceed: HMAC key environment is set"

V5 = Path(sys.argv[1]).resolve()
COHORT = Path(sys.argv[2]).resolve()
SCRATCH = Path(sys.argv[3]).resolve()
SCRATCH.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("t4f1_runner_under_audit",
                                              V5 / "v52_t4f1_beam_retrieval.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["t4f1_runner_under_audit"] = mod
spec.loader.exec_module(mod)          # module import only; __name__ != "__main__"

verifier = getattr(mod, "verify_run_authorization")
seal_path = V5 / "CANDIDATE_EXECUTION_SEAL.json"
script_path = V5 / "v52_t4f1_beam_retrieval.py"

results = []


def attempt(label, auth_doc_or_path, out_name):
    out_dir = SCRATCH / out_name
    if isinstance(auth_doc_or_path, Path):
        auth_path = auth_doc_or_path
    else:
        auth_path = SCRATCH / (out_name + "_auth.json")
        auth_path.write_text(json.dumps(auth_doc_or_path, indent=2, sort_keys=True), encoding="utf-8")
    created_before = out_dir.exists()
    try:
        verifier(auth_path, script_path, seal_path, COHORT, out_dir)
        outcome, message = "ACCEPTED", ""
    except BaseException as exc:                     # noqa: BLE001 - record any refusal
        outcome, message = "REFUSED", f"{type(exc).__name__}: {exc}"
    results.append({
        "fixture": label,
        "outcome": outcome,
        "message": message[:300],
        "output_directory_created": out_dir.exists() and not created_before,
        "hmac_env_present_during_call": AUTH_ENV in os.environ,
    })


# 1. the inert in-package template, unmodified
attempt("in-package RUN_AUTHORIZATION_TEMPLATE.json (inert, unsigned)",
        V5 / "RUN_AUTHORIZATION_TEMPLATE.json", "f_template")

# 2. fully synthetic: every field structurally present, signature absent
synth = {
    "schema": "V52_T4F1_RUN_AUTHORIZATION_V4",
    "status": "AUTHORIZED_FOR_TASK_4F1_EXECUTION",
    "retrieval_quality_outcome_access": "GRANTED",
    "execution_script_sha256": hashlib.sha256(script_path.read_bytes()).hexdigest(),
    "execution_candidate_seal_sha256": hashlib.sha256(seal_path.read_bytes()).hexdigest(),
    "cohort_sha256": hashlib.sha256(COHORT.read_bytes()).hexdigest(),
    "required_archive_count": 96,
    "output_namespace_basename": "synthetic_audit_fixture_never_run",
    "preregistration_seal_sha256": "00" * 32,
    "authorization_id": "SYNTHETIC-AUDIT-FIXTURE",
    "authorization_nonce": "11" * 32,
}
attempt("synthetic authorization, all fields, NO signature field", dict(synth), "f_nosig")

# 3. fully synthetic with a structurally-shaped but arbitrary (invalid) signature
bad = dict(synth); bad["authorization_hmac_sha256"] = "de" * 32
attempt("synthetic authorization with an arbitrary invalid HMAC", bad, "f_badsig")

# 4. same, with the wrong schema label (superseded V3)
wrong = dict(bad); wrong["schema"] = "V52_T4F1_RUN_AUTHORIZATION_V3"
attempt("synthetic authorization carrying the superseded V3 schema label", wrong, "f_v3schema")

print(json.dumps({
    "hmac_key_environment_variable": AUTH_ENV,
    "hmac_env_set_at_any_point": False,
    "valid_production_authorization_constructed": False,
    "seal_key_commitment": json.loads(seal_path.read_text(encoding="utf-8"))
        ["authorization_control"]["key_commitment_sha256"],
    "entry_points_called": ["verify_run_authorization"],
    "entry_points_never_called": ["run_archives", "evaluate_archive", "finalize_results"],
    "fixtures": results,
    "all_fixtures_refused": all(r["outcome"] == "REFUSED" for r in results),
    "no_output_directory_created": not any(r["output_directory_created"] for r in results),
}, indent=2))
