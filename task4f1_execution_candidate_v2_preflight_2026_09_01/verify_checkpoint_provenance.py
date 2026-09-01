from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "task4f1_execution_candidate_v2_2026_09_01" / "v52_t4f1_beam_retrieval.py"
FIXTURE = Path(__file__).resolve().parent / "checkpoint_fixture"
SPEC = importlib.util.spec_from_file_location("v52_t4f1_v2_checkpoint_probe", RUNNER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load V2 runner")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

EXPECTED = {
    "script_sha256": "1" * 64,
    "cohort_sha256": "2" * 64,
    "run_authorization_sha256": "3" * 64,
    "execution_candidate_seal_sha256": "4" * 64,
}

if not MODULE.verify_existing_archive(FIXTURE, "100K::synthetic", 1, EXPECTED):
    raise RuntimeError("matching provenance was not accepted")

MISMATCH = dict(EXPECTED)
MISMATCH["run_authorization_sha256"] = "5" * 64
try:
    MODULE.verify_existing_archive(FIXTURE, "100K::synthetic", 1, MISMATCH)
except RuntimeError as exc:
    if "ARCHIVE CHECKPOINT MISMATCH" not in str(exc):
        raise
else:
    raise RuntimeError("mismatched provenance was accepted")

print("PASS: matching synthetic checkpoint provenance accepted; changed authorization hash rejected")
