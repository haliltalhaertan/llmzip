"""Account for one actual NumPy ITQ rotation; float32 is an explicit conversion.

Run with the locked Python and -B. The existing main source/PLAN are never edited.
Use --output task3/state-review for a fresh supplementary reproduction directory.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import time


ROOT = Path(__file__).resolve().parent.parent
TASK3 = ROOT / "task3"
MAIN_SOURCE = ROOT / "itq_feasibility_synthetic.py"
DATA_SEED = 5212100
INITIALIZATION_SEED = 7312001
N = 100
D = 96


def load_itq():
    spec = importlib.util.spec_from_file_location("pure_synthetic_itq_task3", MAIN_SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(output):
    started = time.perf_counter()
    m = load_itq()  # Establishes thread environment before numerical imports.
    out = (ROOT / output).resolve()
    m.require(out == TASK3 or TASK3 in out.parents, "output must stay inside task3")
    source_hash = m.sha(Path(__file__).read_bytes())
    results = json.loads((TASK3 / "RESULTS.json").read_text(encoding="utf-8"))
    plan = json.loads((TASK3 / "PLAN.json").read_text(encoding="utf-8"))
    main_hash = m.sha(MAIN_SOURCE.read_bytes())
    m.require(main_hash == plan["source_sha256"] == results["source_sha256"], "main source identity mismatch")
    m.require(m.sha((TASK3 / "PLAN.json").read_bytes()) == results["plan_sha256"], "main PLAN identity mismatch")
    expected = [f for f in results["fits"] if
                (f["distribution"], f["n"], f["data_seed"], f["initialization_seed"]) ==
                ("gaussian", N, DATA_SEED, INITIALIZATION_SEED)]
    m.require(len(expected) == 1, "must identify exactly one existing declared fit")
    expected = expected[0]
    with m.threadpool_limits(limits=1):
        env = m.environment()
        y = m.np.random.default_rng(DATA_SEED).standard_normal((N, D))
        y -= y.mean(axis=0)
        start = m.haar(INITIALIZATION_SEED, D)
        m.require(m.matrix_identity(y) == expected["data"], "input data hash/dtype/shape mismatch")
        rotation, fit = m.fit_itq(y, start)
        for field in ("initial_rotation", "final_rotation", "final_binary_codes", "iterations", "converged",
                      "initial_objective_mean", "final_objective_mean"):
            m.require(fit[field] == expected[field], "existing fit identity mismatch: " + field)
        m.require(rotation.dtype == m.np.float64 and rotation.nbytes == 73728, "unexpected actual fitted rotation storage")
        converted = rotation.astype(m.np.float32)
        max_abs_cast_delta = float(m.np.max(m.np.abs(rotation - converted.astype(m.np.float64))))
        m.require(converted.nbytes == 36864, "unexpected converted rotation storage")
        m.require(max_abs_cast_delta > 0, "conversion unexpectedly exact; report must not claim this is the same matrix")
        out.mkdir(parents=True, exist_ok=True)
        binaries = out / "actual_binary_artifacts"
        m.require(not (out / "FITTED_STATE.json").exists(), "receipt already exists; use a fresh output")
        binaries.mkdir(exist_ok=False)
        artifacts = {}
        for label, matrix, filename in (
            ("actual_numpy_fitted_float64", rotation, "R_fitted_float64.npy"),
            ("explicit_float32_conversion", converted, "R_converted_float32.npy"),
        ):
            path = binaries / filename
            with path.open("xb") as handle:
                m.np.save(handle, matrix, allow_pickle=False)
            loaded = m.np.load(path, allow_pickle=False)
            m.require(m.matrix_identity(loaded) == m.matrix_identity(matrix), "npy roundtrip identity mismatch")
            raw = path.read_bytes()
            artifacts[label] = {
                "path_relative_to_receipt": path.relative_to(out).as_posix(),
                "matrix": m.matrix_identity(matrix), "raw_nbytes": matrix.nbytes,
                "npy_bytes": len(raw), "npy_sha256": m.sha(raw),
                "npy_header_and_framing_bytes": len(raw) - matrix.nbytes,
                "allow_pickle": False, "npy_roundtrip_identity": "PASS",
            }
    m.require(m.sha(Path(__file__).read_bytes()) == source_hash, "supplement source changed during run")
    receipt = {
        "status": "PASS_ACTUAL_NUMPY_FITTED_STATE_ACCOUNTING",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "supplement_source_sha256": source_hash, "main_source_sha256": main_hash,
        "main_plan_sha256": m.sha((TASK3 / "PLAN.json").read_bytes()),
        "existing_results_sha256": m.sha((TASK3 / "RESULTS.json").read_bytes()),
        "base_commit": m.BASE_COMMIT, "environment": env,
        "distribution": "gaussian", "n": N, "dimension": D,
        "data_seed": DATA_SEED, "initialization_seed": INITIALIZATION_SEED,
        "input_data": m.matrix_identity(y), "initial_rotation": fit["initial_rotation"],
        "existing_fit_data_rotation_codes_objective_stopping_identity": "EXACT_MATCH",
        "fit": {k: v for k, v in fit.items() if k != "history"},
        "artifacts": artifacts, "float32_conversion_max_abs_delta": max_abs_cast_delta,
        "limitations": [
            "Actual state is the float64 R fitted by this NumPy/SciPy synthetic implementation, not a Faiss ITQ fit.",
            "Float32 state is explicitly converted from that fitted R; it has different dtype, bytes and numerical values.",
            "Float32 conversion was not refitted; no code-stability, quantization-loss or retrieval claim is made for it.",
            "This accounts for the learned rotation array and its npy container only, not a complete deployment/index footprint.",
            "No real matrix, corpus, query-distance or retrieval code is accessed; the original 240-fit panel is not rerun.",
        ],
        "elapsed_seconds": time.perf_counter() - started,
    }
    m.write_json(out / "FITTED_STATE.json", receipt)
    print(json.dumps({"status": receipt["status"], "artifacts": artifacts,
                      "float32_conversion_max_abs_delta": max_abs_cast_delta,
                      "elapsed_seconds": receipt["elapsed_seconds"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="task3")
    run(parser.parse_args().output)
