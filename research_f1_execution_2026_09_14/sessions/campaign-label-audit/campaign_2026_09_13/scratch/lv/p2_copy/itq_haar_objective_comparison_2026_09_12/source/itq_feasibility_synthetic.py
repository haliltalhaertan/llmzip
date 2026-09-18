"""Task 3 only: finite synthetic ITQ optimization and rotation-stability diagnostic.

Run with the locked interpreter and -B. Writes only a fresh task3/ output tree.
No corpus, saved representation, query distances, retrieval code, G3 or other
repository module is imported. No statistical equivalence test is performed.
"""
from __future__ import annotations

import os
for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS",
             "OMP_THREAD_LIMIT"):
    os.environ[_key] = "1"

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import platform
import sys
import time

import numpy as np
import scipy
from scipy.linalg import qr, svd
from scipy.optimize import linear_sum_assignment
from threadpoolctl import threadpool_info, threadpool_limits

BASE_COMMIT = "ae9175676b840ae6a80a31eba9836187dc1b7491"
DIM = 96
DATA_SEEDS = ((100, 5212100), (250, 5212250), (500, 5212500), (1000, 5213000))
INIT_SEEDS = (7312001, 7312002, 7312003, 7312004, 7312005,
              7312006, 7312007, 7312008, 7312009, 7312010,
              7312011, 7312012, 7312013, 7312014, 7312015,
              7312016, 7312017, 7312018, 7312019, 7312020)
NULL_SEEDS = (8312001, 8312002, 8312003, 8312004, 8312005,
              8312006, 8312007, 8312008, 8312009, 8312010,
              8312011, 8312012, 8312013, 8312014, 8312015,
              8312016, 8312017, 8312018, 8312019, 8312020)
ROTATED_HETEROGENEITY_SEED = 9312001
CONTROL_SEED = 9312099
MAX_ITERATIONS = 250
RELATIVE_TOLERANCE = 1e-8
REQUIRED_STABLE_STEPS = 5
MONOTONIC_TOLERANCE = 128 * np.finfo(np.float64).eps
ORTHOGONAL_TOLERANCE = 1e-10
DISTRIBUTIONS = ("gaussian", "heterogeneous", "rotated_heterogeneous")
ROOT = Path(__file__).resolve().parent
TASK3 = ROOT / "task3"
TASK_FILE_SHA256 = "d10e6bc47f0c418f44d0d66c11d93a7da682bb266729a32d92b81f8986e7776f"
METHOD_REVIEW_SHA256 = "bd0a704eb011a7d43dda50e022120b5aa76e557d4a9e4db62ab6f7f95169224b"
LIMITATIONS = [
    "One generated data realization per n, paired across distributions; twenty initializations per fixed matrix.",
    "This measures conditional optimizer variability, not sampling stability across independent datasets.",
    "The 190 pairwise distances share twenty fits and are dependent; the Haar pairs are also dependent.",
    "The same initial and null rotations are reused across panels; panels are not independent replications.",
    "Distribution differences are descriptive only: no p-values, significance, equivalence margin, or power claim.",
    "This finite panel cannot determine a universal minimum n, equivalence, or statistical indistinguishability.",
    "Objective convergence under the declared rule does not imply a unique/stable rotation or a global optimum.",
    "An isotropic Gaussian population has no preferred orientation; different fits alone do not establish failure.",
    "Training quantization error is measured; no held-out loss, real representation or retrieval outcome is measured.",
    "No preregistration arm selection, seal, main ledger/state update, or G3 modification is authorized here.",
]


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def matrix_identity(matrix):
    a = np.ascontiguousarray(matrix)
    return {"shape": list(a.shape), "dtype": a.dtype.str, "order": "C",
            "sha256_raw_c_bytes": sha(a.tobytes(order="C")), "bytes": a.nbytes}


def write_json(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write("\n")


def sign_code(projected):
    return np.where(projected >= 0, 1, -1).astype(np.int8)


def objective(projected, code=None):
    if code is None:
        code = sign_code(projected)
    residual = projected - code
    return float(np.sum(residual * residual, dtype=np.float64) / projected.size)


def haar(seed, dimension=DIM):
    raw = np.random.default_rng(seed).standard_normal((dimension, dimension))
    q, r = qr(raw, mode="economic", check_finite=False)
    return np.ascontiguousarray(q * np.where(np.diag(r) >= 0, 1.0, -1.0))


def rotation_distances(first, second):
    """Only bit-column permutations and signs are removed, never arbitrary O(d)."""
    cross = first.T @ second
    rows, columns = linear_sum_assignment(-np.abs(cross))
    signs = np.where(cross[rows, columns] >= 0, 1.0, -1.0)
    aligned = np.empty_like(second)
    aligned[:, rows] = second[:, columns] * signs
    raw = float(np.linalg.norm(first - second, ord="fro"))
    sp = float(np.linalg.norm(first - aligned, ord="fro"))
    d = first.shape[1]
    return {"raw_frobenius": raw, "raw_normalized": raw / np.sqrt(d),
            "signed_permutation_frobenius": sp, "signed_permutation_normalized": sp / np.sqrt(d)}


def orthogonal_error(rotation):
    residual = rotation.T @ rotation - np.eye(rotation.shape[1])
    return float(np.linalg.norm(residual, ord="fro"))


def fit_itq(data, initial):
    """Minimize ||B-YR||_F^2 via sign>=0 and R=U Vh for svd(Y.T B).

    Traces contain both half-step objectives, scaled by n*d; this scale does
    not change the optimizer. No determinant correction (optimization is O(d)).
    """
    started = time.perf_counter()
    require(data.ndim == 2 and data.shape[1] == initial.shape[0] == initial.shape[1], "shape mismatch")
    require(data.dtype == np.float64 and np.isfinite(data).all(), "finite float64 data required")
    rotation = initial.copy()
    require(orthogonal_error(rotation) < ORTHOGONAL_TOLERANCE, "initial rotation is not orthogonal")
    projection = data @ rotation
    code = sign_code(projection)
    current = objective(projection, code)
    initial_objective = current
    history = []
    stable = 0
    positive_increases = 0
    largest_increase = 0.0
    zero_projections = int(np.count_nonzero(projection == 0))
    reason = "iteration_cap"
    for iteration in range(1, MAX_ITERATIONS + 1):
        u, singular_values, vh = svd(data.T @ code, full_matrices=False,
                                     check_finite=False, lapack_driver="gesdd")
        new_rotation = u @ vh
        projection = data @ new_rotation
        fixed_code_objective = objective(projection, code)
        new_code = sign_code(projection)
        next_objective = objective(projection, new_code)
        scale = max(1.0, abs(current), abs(fixed_code_objective))
        half_increase = max(fixed_code_objective - current, next_objective - fixed_code_objective)
        require(half_increase <= MONOTONIC_TOLERANCE * scale, "ITQ half-step objective increased beyond tolerance")
        positive_increases += int(half_increase > 0)
        largest_increase = max(largest_increase, half_increase)
        relative = abs(current - next_objective) / max(abs(current), np.finfo(np.float64).eps)
        stable = stable + 1 if relative <= RELATIVE_TOLERANCE else 0
        history.append({"iteration": iteration, "objective_before": current,
                        "objective_after_procrustes_fixed_B": fixed_code_objective,
                        "objective_after_sign": next_objective, "relative_change": relative,
                        "stable_steps": stable,
                        "binary_entries_changed": int(np.count_nonzero(new_code != code)),
                        "cross_min_singular_value": float(singular_values[-1])})
        zero_projections += int(np.count_nonzero(projection == 0))
        rotation, code, current = new_rotation, new_code, next_objective
        if stable >= REQUIRED_STABLE_STEPS:
            reason = "relative_objective_stable_5"
            break
    error = orthogonal_error(rotation)
    require(error < ORTHOGONAL_TOLERANCE, "final rotation is not orthogonal")
    return rotation, {
        "iterations": len(history), "converged": reason == "relative_objective_stable_5",
        "stop_reason": reason, "cap_hit": len(history) == MAX_ITERATIONS,
        "initial_objective_mean": initial_objective, "final_objective_mean": current,
        "initial_objective_sum": initial_objective * data.size,
        "final_objective_sum": current * data.size,
        "relative_training_objective_reduction": (initial_objective - current) / max(abs(initial_objective), np.finfo(float).eps),
        "orthogonality_frobenius_error": error, "monotonicity_violations": 0,
        "positive_half_step_increases_within_tolerance": positive_increases,
        "largest_positive_half_step_increase": largest_increase,
        "exact_zero_projection_entries_over_observed_steps": zero_projections,
        "elapsed_seconds": time.perf_counter() - started,
        "initial_rotation": matrix_identity(initial), "final_rotation": matrix_identity(rotation),
        "final_binary_codes": matrix_identity(code), "history": history,
    }


def descriptive(values):
    a = np.asarray(values, dtype=np.float64)
    require(a.size > 0 and np.isfinite(a).all(), "finite descriptive input required")
    quantiles = np.quantile(a, [0.05, 0.25, 0.5, 0.75, 0.95], method="linear")
    return {"count": int(a.size), "min": float(a.min()), "max": float(a.max()),
            "mean": float(a.mean()), "sample_sd_descriptive_only": float(a.std(ddof=1)) if a.size > 1 else None,
            **dict(zip(("p05", "p25", "median", "p75", "p95"), map(float, quantiles)))}


def pairwise(rotations, seeds, group, n=None, distribution=None):
    return [{"group": group, "n": n, "distribution": distribution, "seed_i": seeds[i], "seed_j": seeds[j],
             **rotation_distances(rotations[i], rotations[j])}
            for i in range(len(rotations)) for j in range(i + 1, len(rotations))]


def controls():
    started = time.perf_counter()
    rotation = haar(CONTROL_SEED)
    permutation = np.arange(DIM - 1, -1, -1)
    signs = np.where(np.arange(DIM) % 2, -1.0, 1.0)
    same_bits = rotation[:, permutation] * signs
    equivalent = rotation_distances(rotation, same_bits)
    require(equivalent["signed_permutation_normalized"] < 1e-12, "signed permutation zero-distance control failed")
    require(equivalent["raw_normalized"] > 0.5, "raw metric control is not discriminating")
    other = haar(CONTROL_SEED + 1)
    different = rotation_distances(rotation, other)
    require(different["signed_permutation_normalized"] > 0.1, "arbitrary orthogonal alignment incorrectly removed")
    # Independent exhaustive signed-permutation oracle in three dimensions.
    a, b = haar(CONTROL_SEED + 2, 3), haar(CONTROL_SEED + 3, 3)
    brute = min(np.linalg.norm(a - b[:, perm] * np.asarray(s), "fro")
                for perm in itertools.permutations(range(3))
                for s in itertools.product((-1.0, 1.0), repeat=3))
    assigned = rotation_distances(a, b)["signed_permutation_frobenius"]
    require(abs(brute - assigned) < 1e-12, "assignment differs from exhaustive symmetry oracle")
    require(sign_code(np.array([[0.0, -0.0, 1.0, -1.0]])).tolist() == [[1, 1, 1, -1]], "sign tie convention changed")
    y = np.random.default_rng(CONTROL_SEED + 4).normal(size=(128, DIM))
    y -= y.mean(axis=0)
    fitted, info = fit_itq(y, rotation)
    require(info["final_objective_mean"] < info["initial_objective_mean"] - 1e-3, "objective reduction control failed")
    code = sign_code(y @ rotation)
    u, s, vh = svd(y.T @ code, full_matrices=False, check_finite=False)
    theoretical = (float(np.sum(y * y)) + float(np.sum(code.astype(float) ** 2)) - 2 * float(s.sum())) / y.size
    actual = objective(y @ (u @ vh), code)
    require(abs(actual - theoretical) < 1e-12, "Procrustes objective identity failed")
    wrong = objective(y @ (-u @ vh), code)
    require(wrong > actual + 0.1, "wrong Procrustes sign is not discriminated")
    return {"status": "PASS", "seed": CONTROL_SEED, "signed_permutation_equivalent": equivalent,
            "unrelated_Haar_control": different, "assignment_vs_exhaustive_3d_abs_error": abs(brute - assigned),
            "sign_zero_rule": "+0.0 and -0.0 map to +1", "procrustes_closed_form_abs_error": abs(actual - theoretical),
            "wrong_sign_objective_excess": wrong - actual,
            "nonincreasing_objective_control": {k: v for k, v in info.items() if k != "history"},
            "elapsed_seconds": time.perf_counter() - started}


def environment():
    require(platform.python_version() == "3.13.15" and np.__version__ == "2.3.5" and scipy.__version__ == "1.17.0",
            "exact Python/NumPy/SciPy lock required")
    require(sys.dont_write_bytecode, "use -B")
    pools = threadpool_info()
    require(all(p["num_threads"] == 1 for p in pools), "numerical thread pools must be one")
    return {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
            "executable": sys.executable, "platform": platform.platform(), "thread_pools": pools,
            "thread_environment": {k: os.environ[k] for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                                                             "NUMEXPR_NUM_THREADS", "OMP_THREAD_LIMIT")}}


def render_report(results):
    lines = ["# Task 3 — finite synthetic ITQ diagnostic", "",
             "Base: `" + BASE_COMMIT + "`. This report changes no preregistration, root report, ledger, or G3 artifact.", "",
             "20 fixed initializations per fixed matrix; d=96. All three distributions were selected before execution.",
             "ITQ uses sign>=0 and alternating orthogonal Procrustes. Cap=250; relative tolerance=1e-8; stable steps=5.",
             "Objectives are training mean squared quantization residuals per matrix entry (sum/(n*d)).", "",
             "| Distribution | n | Converged / 20 | Iterations min/median/max | Initial → final objective mean | Fit SP median | Haar–Haar SP median |", 
             "|---|---:|---:|---|---|---:|---:|"]
    null = results["haar_null"]["distance_summary"]["signed_permutation_normalized"]["median"]
    for p in results["panels"]:
        it = p["iterations"]
        lines.append(f"| {p['distribution']} | {p['n']} | {p['converged_count']} | {it['min']:.0f}/{it['median']:.1f}/{it['max']:.0f} | "
                     f"{p['initial_objective']['mean']:.6f} → {p['final_objective']['mean']:.6f} | "
                     f"{p['distance_summary']['signed_permutation_normalized']['median']:.6f} | {null:.6f} |")
    lines += ["", "Distances divide Frobenius norm by sqrt(96); CSV also retains unnormalized and raw values.",
              "Signed-permutation alignment maximizes abs(R1.T@R2) using linear_sum_assignment. No principal angles or arbitrary orthogonal alignment.",
              "The Haar null is one separate, fixed 20-rotation panel reused at every n/distribution, with 190 dependent pairs.",
              "Each ITQ panel likewise has 190 dependent fit pairs; quantiles and differences are descriptive, not a hypothesis test.", "",
              "## Data and provenance", "",
              "For each n a literal-seeded standard Gaussian matrix is generated. Coordinate means are subtracted.",
              "Heterogeneous population variances are geomspace(16,1/16,96), divided by their arithmetic mean (variance ratio 256).",
              "This is fixed population-energy scaling, not sample whitening or per-row normalization. The rotated variant is the same centered heterogeneous matrix right-multiplied by one literal-seeded Haar matrix.",
              "Each panel has one data realization, not twenty independently generated data samples. Initialization and null seeds are separate fixed panels.",
              "PLAN.json was written before controls/fits and pins source bytes, seeds, dtype, shape and stopping rules.",
              "RESULTS.json carries matrix hashes and per-fit metadata; fits.csv, objective_history.csv and pairwise_distances.csv retain the individual observations.",
              "Run with the locked interpreter: `python -B itq_feasibility_synthetic.py --output task3/review-new` (fresh directory).", "",
              "## Limits", ""] + ["- " + x for x in LIMITATIONS]
    lines += ["", f"Elapsed wall time: {results['elapsed_seconds']:.3f} seconds; fitting subtotal: {results['fit_elapsed_seconds_sum']:.3f} seconds.",
              "Controls: signed-permutation zero distance, raw-distance discrimination, unrelated-Haar nonzero distance, exhaustive 3-D assignment oracle, exact-zero sign convention, nonincreasing objective, Procrustes closed-form optimum and wrong-sign negative.",
              "These measurements supply a finite feasibility/stability description. They do not determine at what n ITQ becomes statistically indistinguishable from random rotation.", ""]
    return "\n".join(lines)


def run(output):
    started = time.perf_counter()
    env = environment()
    out = Path(output)
    out = (ROOT / out).resolve() if not out.is_absolute() else out.resolve()
    require(out == TASK3 or TASK3 in out.parents, "output must be task3 or a child of task3")
    out.mkdir(parents=True, exist_ok=False)
    source_hash = sha(Path(__file__).read_bytes())
    plan = {"status": "PREDECLARED_BEFORE_COMPUTATION_NOT_A_SEAL", "created_utc": datetime.now(timezone.utc).isoformat(),
            "base_commit": BASE_COMMIT, "source_sha256": source_hash,
            "task_file_sha256": TASK_FILE_SHA256, "methodological_review_sha256": METHOD_REVIEW_SHA256,
            "dimension": DIM, "dtype": "<f8", "data_seeds": DATA_SEEDS, "initialization_seeds": INIT_SEEDS,
            "haar_null_seeds": NULL_SEEDS, "rotated_heterogeneity_seed": ROTATED_HETEROGENEITY_SEED,
            "control_seed": CONTROL_SEED, "distributions": DISTRIBUTIONS,
            "max_iterations": MAX_ITERATIONS, "relative_tolerance": RELATIVE_TOLERANCE,
            "consecutive_stable_steps": REQUIRED_STABLE_STEPS,
            "relative_denominator": "max(abs(previous mean objective), float64 epsilon)",
            "monotonicity_tolerance": MONOTONIC_TOLERANCE, "orthogonality_frobenius_tolerance": ORTHOGONAL_TOLERANCE,
            "variance_profile": "geomspace(16,1/16,96) / mean(geomspace(16,1/16,96))",
            "centering": "subtract each generated matrix's coordinate sample means; no row normalization or whitening",
            "paired_data": "same underlying Gaussian realization per n across distributions; rotated heterogeneous uses same matrix and spectrum",
            "sampling_replications_per_panel": 1, "limitations": LIMITATIONS}
    write_json(out / "PLAN.json", plan)
    write_json(out / "ENVIRONMENT.json", env)
    control = controls()
    write_json(out / "CONTROL_RESULTS.json", control)
    print("CONTROLS PASS; declared panel and stopping rule unchanged", flush=True)
    initial = [haar(seed) for seed in INIT_SEEDS]
    null = [haar(seed) for seed in NULL_SEEDS]
    rotation = haar(ROTATED_HETEROGENEITY_SEED)
    pairs = pairwise(null, NULL_SEEDS, "haar_null_shared")
    metrics = ("raw_frobenius", "raw_normalized", "signed_permutation_frobenius", "signed_permutation_normalized")
    null_summary = {m: descriptive([p[m] for p in pairs]) for m in metrics}
    fit_fields = ["distribution", "n", "data_seed", "initialization_seed", "iterations", "converged", "stop_reason", "cap_hit",
                  "initial_objective_mean", "final_objective_mean", "initial_objective_sum", "final_objective_sum",
                  "relative_training_objective_reduction", "orthogonality_frobenius_error", "monotonicity_violations",
                  "positive_half_step_increases_within_tolerance", "largest_positive_half_step_increase",
                  "exact_zero_projection_entries_over_observed_steps", "elapsed_seconds",
                  "data_sha256", "initial_rotation_sha256", "final_rotation_sha256", "final_binary_codes_sha256"]
    trace_fields = ["distribution", "n", "data_seed", "initialization_seed", "iteration", "objective_before",
                    "objective_after_procrustes_fixed_B", "objective_after_sign", "relative_change", "stable_steps",
                    "binary_entries_changed", "cross_min_singular_value"]
    fits, panels = [], []
    with (out / "fits.csv").open("x", encoding="utf-8", newline="") as fh, \
         (out / "objective_history.csv").open("x", encoding="utf-8", newline="") as th:
        fw = csv.DictWriter(fh, fieldnames=fit_fields, lineterminator="\n"); fw.writeheader()
        tw = csv.DictWriter(th, fieldnames=trace_fields, lineterminator="\n"); tw.writeheader()
        for n, data_seed in DATA_SEEDS:
            z = np.random.default_rng(data_seed).standard_normal((n, DIM))
            variances = np.geomspace(16.0, 1.0 / 16, DIM); variances /= variances.mean()
            gaussian = z - z.mean(axis=0)
            heterogeneous = z * np.sqrt(variances)
            heterogeneous -= heterogeneous.mean(axis=0)
            datasets = (gaussian, heterogeneous, heterogeneous @ rotation)
            for distribution, y in zip(DISTRIBUTIONS, datasets):
                y = np.ascontiguousarray(y, dtype=np.float64)
                y.flags.writeable = False
                identity = matrix_identity(y)
                panel_fits, fitted = [], []
                for seed, start_rotation in zip(INIT_SEEDS, initial):
                    r, info = fit_itq(y, start_rotation)
                    key = {"distribution": distribution, "n": n, "data_seed": data_seed, "initialization_seed": seed}
                    tw.writerows(dict(key, **h) for h in info.pop("history"))
                    info.update(key, data=identity)
                    row = {k: info[k] for k in fit_fields if k in info}
                    row.update(data_sha256=identity["sha256_raw_c_bytes"],
                               initial_rotation_sha256=info["initial_rotation"]["sha256_raw_c_bytes"],
                               final_rotation_sha256=info["final_rotation"]["sha256_raw_c_bytes"],
                               final_binary_codes_sha256=info["final_binary_codes"]["sha256_raw_c_bytes"])
                    fw.writerow(row); fh.flush(); th.flush()
                    fits.append(info); panel_fits.append(info); fitted.append(r)
                    print(f"FIT {distribution} n={n} seed={seed}: iterations={info['iterations']} {info['stop_reason']}", flush=True)
                pp = pairwise(fitted, INIT_SEEDS, "itq_fit", n, distribution)
                pairs.extend(pp)
                dist_summary = {m: descriptive([p[m] for p in pp]) for m in metrics}
                null_objectives = [{"seed": seed, "objective_mean": objective(y @ r)} for seed, r in zip(NULL_SEEDS, null)]
                panels.append({"n": n, "distribution": distribution, "data_seed": data_seed, "data": identity,
                               "sample_mean_max_abs": float(np.abs(y.mean(axis=0)).max()),
                               "sample_covariance_rank": int(np.linalg.matrix_rank(y)),
                               "sample_coordinate_variance_min": float(np.var(y, axis=0).min()),
                               "sample_coordinate_variance_max": float(np.var(y, axis=0).max()),
                               "converged_count": sum(f["converged"] for f in panel_fits),
                               "cap_hit_count": sum(f["cap_hit"] for f in panel_fits),
                               "iterations": descriptive([f["iterations"] for f in panel_fits]),
                               "initial_objective": descriptive([f["initial_objective_mean"] for f in panel_fits]),
                               "final_objective": descriptive([f["final_objective_mean"] for f in panel_fits]),
                               "haar_null_objective": descriptive([x["objective_mean"] for x in null_objectives]),
                               "haar_null_objectives_per_rotation": null_objectives,
                               "distance_summary": dist_summary,
                               "SP_median_minus_haar_null_median_descriptive": dist_summary["signed_permutation_normalized"]["median"] - null_summary["signed_permutation_normalized"]["median"],
                               "elapsed_fit_seconds": sum(f["elapsed_seconds"] for f in panel_fits)})
                require(matrix_identity(y) == identity, "data matrix mutated during fitting")
    with (out / "pairwise_distances.csv").open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(pairs[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(pairs)
    require(sha(Path(__file__).read_bytes()) == source_hash, "source changed during diagnostic")
    results = {"status": "COMPLETED_SYNTHETIC_DIAGNOSTIC_NOT_ACCEPTANCE", "base_commit": BASE_COMMIT,
               "source_sha256": source_hash, "plan_sha256": sha((out / "PLAN.json").read_bytes()),
               "created_utc": datetime.now(timezone.utc).isoformat(), "dimension": DIM, "fit_count": len(fits),
               "converged_count": sum(f["converged"] for f in fits), "cap_hit_count": sum(f["cap_hit"] for f in fits),
               "rotated_heterogeneity_matrix": matrix_identity(rotation),
               "haar_null": {"seeds": NULL_SEEDS, "rotation_identities": [matrix_identity(r) for r in null],
                             "pair_count": 190, "reuse": "one shared panel, not fresh independent null per condition",
                             "distance_summary": null_summary},
               "panels": panels, "fits": fits, "limitations": LIMITATIONS,
               "minimum_n_or_equivalence_decision": "NOT_IDENTIFIABLE_FROM_THIS_FINITE_PANEL",
               "controls_status": control["status"], "elapsed_seconds": time.perf_counter() - started,
               "fit_elapsed_seconds_sum": sum(f["elapsed_seconds"] for f in fits)}
    write_json(out / "RESULTS.json", results)
    with (out / "README.md").open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(render_report(results))
    hashes = {p.name: {"sha256": sha(p.read_bytes()), "bytes": p.stat().st_size}
              for p in sorted(out.iterdir()) if p.is_file()}
    source_relative = os.path.relpath(Path(__file__).resolve(), out).replace("\\", "/")
    hashes[source_relative] = {"sha256": source_hash, "bytes": Path(__file__).stat().st_size}
    write_json(out / "HASHES.json", {"self_excluded": True, "files": hashes})
    print(f"COMPLETE fits={len(fits)} converged={results['converged_count']} cap_hit={results['cap_hit_count']} elapsed={results['elapsed_seconds']:.3f}s", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="task3")
    args = parser.parse_args()
    with threadpool_limits(limits=1):
        run(args.output)


if __name__ == "__main__":
    main()
