"""Replay only existing synthetic Haar objectives; never fit ITQ or load corpora.

python -B replay_objectives.py --output replay
All data/rotation seeds come from the pinned historical PLAN. Historical fitted
objectives are cited, not recomputed. A fresh output directory is required.
"""
import os
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
            "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS",
            "OMP_THREAD_LIMIT"):
    os.environ[key] = "1"
import argparse
import csv
import hashlib
import json
from pathlib import Path
import platform
import sys
from datetime import datetime, timezone
import numpy as np
import scipy
from scipy.linalg import qr
from threadpoolctl import threadpool_limits, threadpool_info

ROOT = Path(__file__).resolve().parent
SOURCE_COMMIT = "4001fc9d8ea2c932042de7823713c6efce8e56d0"
PINS = {
    "itq_feasibility_synthetic.py": "18ddc99dfe57e93f949ea55b2e1c9cae402c9204d1db99bb82d0a2014a30973d",
    "PLAN.json": "e56ea0d6858e06211fa9eb82d6d255724a3d0e23016b77d28f8d8ff10923c53f",
    "RESULTS.json": "0c2cf96553dbf448d22def0538c8993ada038d1fdac52665f759c08e5a304214",
}

def require(ok, reason):
    if not ok:
        raise RuntimeError(reason)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def write_json(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write("\n")

def identity(a):
    a = np.ascontiguousarray(a)
    return {"shape": list(a.shape), "dtype": a.dtype.str, "order": "C",
            "sha256_raw_c_bytes": digest(a.tobytes()), "bytes": a.nbytes}

def rotation(seed, d):
    q, r = qr(np.random.default_rng(seed).standard_normal((d, d)),
              mode="economic", check_finite=False)
    return np.ascontiguousarray(q * np.where(np.diag(r) >= 0, 1.0, -1.0))

def objective(projected):
    # Independent equivalent expression, rather than calling the producer.
    return float(np.mean((np.abs(projected) - 1.0) ** 2, dtype=np.float64))

def summary(values):
    return {"count": len(values), "mean": float(np.mean(values)),
            "min": float(np.min(values)), "max": float(np.max(values)),
            "sample_sd_descriptive_only": float(np.std(values, ddof=1))}

def run(output):
    for name, expected in PINS.items():
        require(digest((ROOT / "source" / name).read_bytes()) == expected,
                "source hash mismatch: " + name)
    plan = json.loads((ROOT / "source/PLAN.json").read_bytes())
    prior = json.loads((ROOT / "source/RESULTS.json").read_bytes())
    require(plan["source_sha256"] == prior["source_sha256"] == PINS["itq_feasibility_synthetic.py"], "source cross-link")
    require(prior["plan_sha256"] == PINS["PLAN.json"], "plan cross-link")
    d = plan["dimension"]
    require(d == 96 and plan["dtype"] == "<f8", "dimension/dtype")
    require(plan["distributions"] == ["gaussian", "heterogeneous", "rotated_heterogeneous"], "distribution identity")
    out = (ROOT / output).resolve()
    require(ROOT in out.parents, "output must be a fresh child of this package")
    out.mkdir(parents=True, exist_ok=False)
    write_json(out / "PLAN.json", {
        "status": "POST_HOC_VERIFICATION_OF_PREVIOUSLY_KNOWN_RESULTS_NOT_PREREGISTRATION_OR_SEAL",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_commit": SOURCE_COMMIT, "source_pins": PINS,
        "replay_source_sha256": digest(Path(__file__).read_bytes()),
        "data_seeds": plan["data_seeds"], "initialization_seeds": plan["initialization_seeds"],
        "haar_null_seeds": plan["haar_null_seeds"],
        "objective": "mean((abs(Y @ R)-1)**2), per matrix entry; sign convention >=0",
        "replay_criterion": "exact equality of all 480 stored initial/null objectives and input/rotation raw identities",
        "new_data_or_seeds": False, "fit_itq": False,
        "historical_final_objectives": "read from pinned RESULTS, not refitted",
        "limitations": ["training quantization only", "one realization per n",
                        "shared seed panels; no statistical test or arm decision", "no held-out or retrieval measurement"]})
    write_json(out / "ENVIRONMENT.json", {"python": sys.version, "platform": platform.platform(),
        "numpy": np.__version__, "scipy": scipy.__version__, "threadpools": threadpool_info()})
    require(objective(np.zeros((2, 3))) == 1.0, "zero control")
    require(objective(np.array([[-1., 1., -1.]])) == 0.0, "binary control")
    probe = np.array([[0., 0.5, -2.], [3., -0.25, 1.]])
    expected = sum((abs(float(x))-1)**2 for x in probe.flat) / probe.size
    require(objective(probe) == expected, "scalar oracle")
    require(objective(probe) == objective(probe[:, [2, 0, 1]] * [-1., 1., -1.]), "signed-permutation control")
    wrong_sign = float(np.mean((probe + np.where(probe >= 0, 1., -1.))**2))
    require(wrong_sign != expected, "wrong-sign negative control")
    initials = {s: rotation(s, d) for s in plan["initialization_seeds"]}
    nulls = {s: rotation(s, d) for s in plan["haar_null_seeds"]}
    for r, expected_identity in zip(nulls.values(), prior["haar_null"]["rotation_identities"]):
        require(identity(r) == expected_identity, "null rotation identity")
    orientation = rotation(plan["rotated_heterogeneity_seed"], d)
    require(identity(orientation) == prior["rotated_heterogeneity_matrix"], "orientation identity")
    require(prior["haar_null"]["seeds"] == plan["haar_null_seeds"], "null seed identity")
    panels = {(p["n"], p["distribution"]): p for p in prior["panels"]}
    fits = {(f["n"], f["distribution"], f["initialization_seed"]): f for f in prior["fits"]}
    rows, comparisons, verified_panels = [], [], []
    for n, seed in plan["data_seeds"]:
        z = np.random.default_rng(seed).standard_normal((n, d))
        variances = np.geomspace(16., 1./16, d)
        variances /= variances.mean()
        gaussian = z - z.mean(axis=0)
        heterogeneous = z * np.sqrt(variances)
        heterogeneous -= heterogeneous.mean(axis=0)
        for distribution, y in zip(plan["distributions"], (gaussian, heterogeneous, heterogeneous @ orientation)):
            y = np.ascontiguousarray(y, dtype=np.float64)
            p = panels[n, distribution]
            require(identity(y) == p["data"], "regenerated data identity")
            verified_panels.append({"n": n, "distribution": distribution, "data": identity(y)})
            stored_nulls = {v["seed"]: v["objective_mean"] for v in p["haar_null_objectives_per_rotation"]}
            initial_values, null_values, final_values = [], [], []
            for group, rotations, target in (("initial_haar", initials, initial_values), ("null_haar", nulls, null_values)):
                for rotation_seed, r in rotations.items():
                    if group == "initial_haar":
                        f = fits[n, distribution, rotation_seed]
                        require(identity(r) == f["initial_rotation"] and identity(y) == f["data"], "fit source identities")
                        stored = f["initial_objective_mean"]
                        final_values.append(f["final_objective_mean"])
                    else:
                        stored = stored_nulls[rotation_seed]
                    value = objective(y @ r)
                    require(value == stored, f"objective replay mismatch: {n}/{distribution}/{rotation_seed}")
                    target.append(value)
                    rows.append({"n": n, "distribution": distribution, "rotation_group": group,
                        "rotation_seed": rotation_seed, "objective_mean": value,
                        "stored_objective_mean": stored, "exact_match": True})
            for values, key in ((initial_values, "initial_objective"), (null_values, "haar_null_objective"), (final_values, "final_objective")):
                require(summary(values)["mean"] == p[key]["mean"], "stored summary replay")
            comparisons.append({"n": n, "distribution": distribution,
                "initial_haar": summary(initial_values), "null_haar": summary(null_values),
                "historical_itq_fitted": summary(final_values),
                "relative_reduction_vs_null_mean": 1.0 - np.mean(final_values)/np.mean(null_values),
                "largest_fitted_less_than_smallest_null": max(final_values) < min(null_values)})
    require(len(rows) == 480 and len(comparisons) == 12 and len(fits) == 240, "complete historical panel")
    with (out / "objectives.csv").open("x", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    write_json(out / "RESULTS.json", {"status": "PASS_EXACT_HISTORICAL_HAAR_OBJECTIVE_REPLAY",
        "controls": "PASS: zero/binary/scalar-oracle/signed-permutation/wrong-sign-negative",
        "replayed_objectives": len(rows), "verified_data_panels": verified_panels,
        "new_itq_fits": 0, "historical_fitted_objectives_cited": 240,
        "source_commit": SOURCE_COMMIT, "source_pins": PINS, "comparisons": comparisons})
    for p in comparisons:
        print(f"{p['distribution']:24} n={p['n']:4} Haar={p['null_haar']['mean']:.9f} ITQ={p['historical_itq_fitted']['mean']:.9f} reduction={p['relative_reduction_vs_null_mean']:.6%}")
    print("PASS: 480 exact objective replays; 12 exact input identities; no ITQ refit")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="replay")
    with threadpool_limits(limits=1):
        run(parser.parse_args().output)
