from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parent
RUNNER = REPO / "task4f1_execution_candidate_v3_2026_09_01" / "v52_t4f1_beam_retrieval.py"
SPEC = importlib.util.spec_from_file_location("v52_t4f1_v3_auth_negative", RUNNER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load V3 runner")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

os.environ.pop(MODULE.AUTH_HMAC_ENV, None)
output_dir = HERE / "NEGATIVE_V3_STRUCTURAL_MUST_NOT_EXIST"
if output_dir.exists():
    raise RuntimeError("negative output path already exists")

try:
    MODULE.verify_run_authorization(
        HERE / "NEGATIVE_STRUCTURALLY_COMPLETE_AUTH.json",
        RUNNER,
        REPO / "task4f1_execution_candidate_v3_2026_09_01" / "CANDIDATE_EXECUTION_SEAL.json",
        REPO / "audit_v52_t4f0_restricted_refreeze_2026_08_31" / "estimand_primary_cohort.csv",
        output_dir,
    )
except RuntimeError as exc:
    if "HEAD RESEARCHER AUTHORITY KEY NOT SEALED" not in str(exc):
        raise
else:
    raise RuntimeError("structurally complete negative authorization was accepted")

if output_dir.exists():
    raise RuntimeError("authorization direct-call test created an output directory")

print("PASS: structurally complete V3 authorization blocked by unsealed authority commitment")
