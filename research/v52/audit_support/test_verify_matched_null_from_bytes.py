#!/usr/bin/env python3
"""Negative controls for verify_matched_null_from_bytes.py.

Every check in the verifier must be able to FAIL. A verifier that passes on
mutated bytes proves nothing, and this line has already produced one such
verifier. Each control below perturbs exactly one thing and asserts the
corresponding check reports it.

Run from the repository root:
    python3 research/v52/audit_support/test_verify_matched_null_from_bytes.py
"""

from __future__ import annotations

import copy
import csv
import json
import tempfile
from pathlib import Path

import verify_matched_null_from_bytes as V

R = V.R
FAILURES: list[str] = []
PASSED = 0


def control(name: str, errs: list[str]) -> None:
    global PASSED
    if errs:
        PASSED += 1
        print(f"  ok   {name}  ->  caught: {errs[0]}")
    else:
        FAILURES.append(name)
        print(f"  FAIL {name}  ->  ESCAPED (mutation not detected)")


def load(bench: str) -> dict:
    return json.loads(
        (R / f"{bench}_random_partition_outputs" / f"{bench}_random_partition_summary.json").read_text()
    )


def main() -> int:
    manifest = json.loads(V.MANIFEST.read_text())

    for bench, (_outdir, key) in V.BENCHMARKS.items():
        print(f"\n{bench}:")
        base = load(bench)

        # --- baseline: unmutated bytes must pass every check ---
        control_baseline = [
            ("A", V.check_partitions(base)),
            ("B", V.check_per_seed_arithmetic(base["primary"])),
            ("C", V.check_aggregates(base["primary"])),
            ("E", V.check_manifest(manifest, key, base)),
        ]
        for label, errs in control_baseline:
            if errs:
                FAILURES.append(f"{bench} baseline {label}")
                print(f"  FAIL baseline {label} -> unmutated bytes reported {errs[0]}")
            else:
                print(f"  ok   baseline {label} -> clean")

        # --- A: partition mutations ---
        s = copy.deepcopy(base)
        s["partitions"][0]["S32"][0] = (s["partitions"][0]["S32"][0] + 1) % 96
        control(f"{bench} A/swapped-index", V.check_partitions(s))

        s = copy.deepcopy(base)
        s["partitions"][0]["S32"] = sorted(range(32))
        s["partitions"][0]["T64"] = sorted(range(32, 96))
        control(f"{bench} A/trivial-leading-32", V.check_partitions(s))

        s = copy.deepcopy(base)
        s["partitions"][0]["T64"].append(s["partitions"][0]["S32"][0])
        control(f"{bench} A/overlapping-partition", V.check_partitions(s))

        s = copy.deepcopy(base)
        s["partitions"][0]["S32"] = s["partitions"][0]["S32"][:31]
        control(f"{bench} A/wrong-size", V.check_partitions(s))

        # --- B: per-seed arithmetic mutations ---
        s = copy.deepcopy(base)
        s["primary"]["seed_rows"][0]["Delta"] += 1e-9
        control(f"{bench} B/Delta-perturbed-1e-9", V.check_per_seed_arithmetic(s["primary"]))

        s = copy.deepcopy(base)
        s["primary"]["seed_rows"][0]["rho_spec"], s["primary"]["seed_rows"][0]["rho_rand"] = (
            s["primary"]["seed_rows"][0]["rho_rand"],
            s["primary"]["seed_rows"][0]["rho_spec"],
        )
        control(f"{bench} B/rho-arms-swapped", V.check_per_seed_arithmetic(s["primary"]))

        s = copy.deepcopy(base)
        s["primary"]["frozen_full_haar_R3"] *= 1.01
        control(f"{bench} B/denominator-shifted", V.check_per_seed_arithmetic(s["primary"]))

        # --- C: aggregate mutations ---
        s = copy.deepcopy(base)
        s["primary"]["Delta"] += 1e-9
        control(f"{bench} C/headline-Delta-perturbed", V.check_aggregates(s["primary"]))

        s = copy.deepcopy(base)
        s["primary"]["dispersion"]["Delta"]["sample_sd"] = s["primary"]["dispersion"]["Delta"][
            "population_sd"
        ]
        control(f"{bench} C/sample-sd-replaced-by-population-sd", V.check_aggregates(s["primary"]))

        s = copy.deepcopy(base)
        s["primary"]["dispersion"]["Delta"]["min"] = s["primary"]["dispersion"]["Delta"]["max"]
        control(f"{bench} C/min-replaced-by-max", V.check_aggregates(s["primary"]))

        s = copy.deepcopy(base)
        s["primary"]["seed_rows"] = s["primary"]["seed_rows"][:-1]
        control(f"{bench} C/one-seed-dropped", V.check_aggregates(s["primary"]))

        # --- D: csv/json divergence ---
        rows = copy.deepcopy(base["primary"]["seed_rows"])
        rows[0]["spectral_R3"] += 1e-9
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "seed.csv"
            with p.open("w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=["seed", *V.SEED_COLS])
                w.writeheader()
                for r in rows:
                    w.writerow({k: r[k] for k in ("seed", *V.SEED_COLS)})
            control(
                f"{bench} D/csv-value-perturbed",
                V.check_csv_against_json(p, base["primary"]),
            )

            p2 = Path(td) / "short.csv"
            with p2.open("w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=["seed", *V.SEED_COLS])
                w.writeheader()
                for r in rows[:-1]:
                    w.writerow({k: r[k] for k in ("seed", *V.SEED_COLS)})
            control(f"{bench} D/csv-row-missing", V.check_csv_against_json(p2, base["primary"]))

        # --- E: manifest divergence ---
        m = copy.deepcopy(manifest)
        m[key]["Delta"] += 1e-9
        control(f"{bench} E/manifest-Delta-drift", V.check_manifest(m, key, base))

        m = copy.deepcopy(manifest)
        m[key]["regime"] = "[NO EFFECT]"
        control(f"{bench} E/manifest-regime-relabelled", V.check_manifest(m, key, base))

        m = copy.deepcopy(manifest)
        m[key]["native_reproduction_error"] = 0.01
        control(f"{bench} E/manifest-reproduction-error", V.check_manifest(m, key, base))

    total = PASSED + len(FAILURES)
    print(f"\n{PASSED}/{total} negative controls caught their mutation")
    if FAILURES:
        print("ESCAPED: " + ", ".join(FAILURES))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
