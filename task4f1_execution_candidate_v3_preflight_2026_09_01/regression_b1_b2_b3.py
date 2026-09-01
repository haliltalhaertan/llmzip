from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parent
RUNNER = REPO / "task4f1_execution_candidate_v3_2026_09_01" / "v52_t4f1_beam_retrieval.py"
SPEC = importlib.util.spec_from_file_location("v52_t4f1_v3_regression", RUNNER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load V3 runner")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

PROVENANCE = {
    "script_sha256": "1" * 64,
    "cohort_sha256": "2" * 64,
    "run_authorization_sha256": "3" * 64,
    "execution_candidate_seal_sha256": "4" * 64,
}
ELIGIBLE = [{
    "audit_question_id": "100K::synthetic::fact::1",
    "tier": "100K",
    "conversation_id": "synthetic",
    "ability": "fact",
    "gold_source_unit_count": "4",
    "gold_source_ids_parsed": ["1", "2", "3", "4"],
}]


def rows(
    *,
    retrieved_override: list[str] | None = None,
    fractional_override: str | None = None,
    signed_top3_divergence: bool = False,
    signed_distance_divergence: bool = False,
    trial_distance_divergence: bool = False,
) -> list[dict[str, Any]]:
    methods = {
        "NATIVE_SIGN96": [None],
        "SIGNED_PERM_CONTROL96": list(MODULE.SIGNED_PERM_SEEDS),
        "HAAR96_SIGN": list(MODULE.HAAR_SEEDS),
        "ITQ96_CENTERED": list(MODULE.ITQ_SEEDS),
    }
    output: list[dict[str, Any]] = []
    for method, seeds in methods.items():
        for seed in seeds:
            for trial in MODULE.NUISANCE_TRIALS:
                retrieved = list(retrieved_override or ["1", "2", "3"])
                distances = [0, 1, 2]
                if signed_top3_divergence and method == "SIGNED_PERM_CONTROL96":
                    retrieved = ["3", "2", "1"]
                if signed_distance_divergence and method == "SIGNED_PERM_CONTROL96":
                    distances = [0, 1, 3]
                if trial_distance_divergence and method == "HAAR96_SIGN" and seed == MODULE.HAAR_SEEDS[0] and trial == 1:
                    distances = [0, 1, 3]
                output.append({
                    "audit_question_id": "100K::synthetic::fact::1",
                    "tier": "100K",
                    "conversation_id": "synthetic",
                    "ability": "fact",
                    "method": method,
                    "seed": "" if seed is None else seed,
                    "trial": trial,
                    "archive_units": 128,
                    "gold_count": 4,
                    "retrieved_top3_ids": json.dumps(retrieved, separators=(",", ":")),
                    "top3_distances": json.dumps(distances, separators=(",", ":")),
                    "fractional_source_evidence_recall_at_3": fractional_override or ".75",
                    "any_at_3": 1,
                    "all_at_3": 0,
                })
    return output


def checkpoint(root: Path, trial_rows: list[dict[str, Any]]) -> None:
    metadata = {
        "schema": "V52_T4F1_ARCHIVE_RESULT_META_V3",
        "archive_id": "100K::synthetic",
        "eligible_questions": 1,
        "archive_units": 128,
        "trial_rows": 320,
        "signed_control_question_seed_checks": 5,
        "continuous_max_abs_dot_diff": 0.0,
        "continuous_max_abs_norm_diff": 0.0,
        "outcomes_printed_to_console": False,
        "provenance": dict(PROVENANCE),
    }
    MODULE.write_archive_result(root, "100K::synthetic", trial_rows, metadata)


def expect_block(call: Any, token: str) -> str:
    try:
        call()
    except RuntimeError as exc:
        message = str(exc)
        if token not in message:
            raise RuntimeError(f"expected blocker {token!r}, observed {message!r}") from exc
        return message
    raise RuntimeError(f"expected blocker {token!r}, but call succeeded")


original_eligible = MODULE.EXPECTED_ELIGIBLE
original_archives = MODULE.EXPECTED_ARCHIVES
MODULE.EXPECTED_ELIGIBLE = 1
MODULE.EXPECTED_ARCHIVES = 1
results: dict[str, Any] = {}
try:
    with tempfile.TemporaryDirectory(prefix="v3_baseline_", dir=HERE) as name:
        root = Path(name)
        checkpoint(root, rows())
        MODULE.finalize_results(root, ELIGIBLE, PROVENANCE)
        results["baseline_valid_synthetic_finalization"] = all((root / filename).is_file() for filename in (
            "V52_T4F1_question_seed_level.csv",
            "V52_T4F1_question_level.csv",
            "V52_T4F1_aggregate.csv",
            "V52_T4F1_POST_RUN_MANIFEST.json",
        ))

    with tempfile.TemporaryDirectory(prefix="v3_b1_destination_", dir=HERE) as name:
        root = Path(name)
        checkpoint(root, rows())
        sentinel_path = root / "V52_T4F1_question_seed_level.csv"
        sentinel = b"PREEXISTING_SYNTHETIC_RESULT_MUST_NOT_CHANGE\n"
        sentinel_path.write_bytes(sentinel)
        expect_block(lambda: MODULE.finalize_results(root, ELIGIBLE, PROVENANCE), "REFUSE FINALIZATION OVERWRITE")
        results["B1_existing_destination_blocked_unchanged"] = sentinel_path.read_bytes() == sentinel

    with tempfile.TemporaryDirectory(prefix="v3_b1_temp_", dir=HERE) as name:
        root = Path(name)
        checkpoint(root, rows())
        temp_path = root / "V52_T4F1_question_level.csv.tmp"
        sentinel = b"CRASH_LEFT_TEMP_MUST_NOT_CHANGE\n"
        temp_path.write_bytes(sentinel)
        expect_block(lambda: MODULE.finalize_results(root, ELIGIBLE, PROVENANCE), "REFUSE FINALIZATION OVERWRITE")
        results["B1_existing_temp_blocked_unchanged"] = temp_path.read_bytes() == sentinel

    with tempfile.TemporaryDirectory(prefix="v3_b2_gold_", dir=HERE) as name:
        root = Path(name)
        checkpoint(root, rows(retrieved_override=["9", "8", "7"]))
        expect_block(lambda: MODULE.finalize_results(root, ELIGIBLE, PROVENANCE), "METRIC GOLD RECOMPUTATION MISMATCH")
        results["B2_non_gold_retrieval_with_fake_metrics_blocked"] = True

    with tempfile.TemporaryDirectory(prefix="v3_b2_metric_", dir=HERE) as name:
        root = Path(name)
        checkpoint(root, rows(fractional_override=".5"))
        expect_block(lambda: MODULE.finalize_results(root, ELIGIBLE, PROVENANCE), "METRIC GOLD RECOMPUTATION MISMATCH")
        results["B2_wrong_stored_metric_blocked"] = True

    with tempfile.TemporaryDirectory(prefix="v3_b3_top3_", dir=HERE) as name:
        root = Path(name)
        checkpoint(root, rows(signed_top3_divergence=True))
        expect_block(lambda: MODULE.finalize_results(root, ELIGIBLE, PROVENANCE), "SIGNED CONTROL EXACT TOP3 OR DISTANCE MISMATCH")
        results["B3_signed_top3_divergence_blocked"] = True

    with tempfile.TemporaryDirectory(prefix="v3_b3_distance_", dir=HERE) as name:
        root = Path(name)
        checkpoint(root, rows(signed_distance_divergence=True))
        expect_block(lambda: MODULE.finalize_results(root, ELIGIBLE, PROVENANCE), "SIGNED CONTROL EXACT TOP3 OR DISTANCE MISMATCH")
        results["B3_signed_distance_divergence_blocked"] = True

    with tempfile.TemporaryDirectory(prefix="v3_trial_distance_", dir=HERE) as name:
        root = Path(name)
        checkpoint(root, rows(trial_distance_divergence=True))
        expect_block(lambda: MODULE.finalize_results(root, ELIGIBLE, PROVENANCE), "TRIAL-VARYING TOP3 OR DISTANCE")
        results["trial_distance_divergence_blocked"] = True
finally:
    MODULE.EXPECTED_ELIGIBLE = original_eligible
    MODULE.EXPECTED_ARCHIVES = original_archives

if not all(results.values()):
    raise RuntimeError(f"V3 regression failure: {results}")

evidence = {
    "schema": "V52_T4F1_V3_B1_B2_B3_REGRESSION_V1",
    "status": "PASS",
    "synthetic_only": True,
    "retrieval_quality_computed": False,
    "cli_mode_run_invocation_count": 0,
    "cli_mode_finalize_invocation_count": 0,
    "results": results,
}
MODULE.write_json(HERE / "B1_B2_B3_REGRESSION.json", evidence)
print("PASS: V3 synthetic B1/B2/B3 regression suite")
