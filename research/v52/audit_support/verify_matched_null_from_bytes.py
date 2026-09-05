#!/usr/bin/env python3
"""Verify everything about the matched random-partition null stage (410bcf5)
that is checkable from committed repository bytes alone.

Scope statement, stated up front because it is the point of this script:

  CHECKABLE (this script)      : partition derivation from the declared RNG
                                 rule, per-seed rho/Delta arithmetic, the
                                 aggregates and dispersion, seed CSV against
                                 summary JSON, and the provenance manifest
                                 against both summaries.
  NOT CHECKABLE (any script)   : the per-seed retrieval numbers themselves
                                 (spectral_R3, random_R3) and the frozen
                                 Full-Haar denominator. No per-question output
                                 was committed for this stage, so those values
                                 enter the chain as declarations and cannot be
                                 reconstructed without re-running the stage
                                 against the pinned corpora.

A PASS from this script is therefore an internal-consistency result, not an
audit. It cannot detect an error upstream of the seed-level numbers.

Run from the repository root:
    python3 research/v52/audit_support/verify_matched_null_from_bytes.py
Exit code 0 = all checkable layers consistent, 1 = at least one discrepancy.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / "research" / "v52"
TOL = 1e-12

MANIFEST = R / "V52_MATCHED_RANDOM_PARTITION_NULL_PROVENANCE_MANIFEST_2026-09-04.json"
BENCHMARKS = {
    "locomo": ("locomo_random_partition_outputs", "locomo_result"),
    "longmemeval": ("longmemeval_random_partition_outputs", "longmemeval_result"),
}
SEED_COLS = ("spectral_R3", "random_R3", "rho_spec", "rho_rand", "Delta")


def mean(v):
    return sum(v) / len(v)


def sample_sd(v):
    m = mean(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))


def population_sd(v):
    m = mean(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / len(v))


def check_partitions(summary: dict) -> list[str]:
    """S32 = sort(default_rng(seed).permutation(96)[:32]); T64 = complement."""
    errs: list[str] = []
    for p in summary["partitions"]:
        seed = p["seed"]
        perm = np.random.default_rng(seed).permutation(96)
        s32 = sorted(perm[:32].tolist())
        t64 = sorted(set(range(96)) - set(s32))
        if s32 != p["S32"]:
            errs.append(f"seed {seed}: S32 does not match the declared rule")
        if t64 != p["T64"]:
            errs.append(f"seed {seed}: T64 does not match the declared rule")
        if set(p["S32"]) & set(p["T64"]):
            errs.append(f"seed {seed}: S32 and T64 are not disjoint")
        if sorted(p["S32"] + p["T64"]) != list(range(96)):
            errs.append(f"seed {seed}: S32 union T64 is not 0..95")
        if len(p["S32"]) != 32 or len(p["T64"]) != 64:
            errs.append(f"seed {seed}: partition sizes are not 32/64")
    return errs


def check_per_seed_arithmetic(primary: dict) -> list[str]:
    """rho = (native - arm) / (native - full_haar); Delta = rho_rand - rho_spec."""
    errs: list[str] = []
    native = primary["native_R3"]
    L = native - primary["frozen_full_haar_R3"]
    for row in primary["seed_rows"]:
        expected = {
            "rho_spec": (native - row["spectral_R3"]) / L,
            "rho_rand": (native - row["random_R3"]) / L,
        }
        expected["Delta"] = expected["rho_rand"] - expected["rho_spec"]
        for name, exp in expected.items():
            if abs(row[name] - exp) > TOL:
                errs.append(
                    f"seed {row['seed']} {name}: declared {row[name]!r}, recomputed {exp!r}"
                )
    return errs


def check_aggregates(primary: dict) -> list[str]:
    errs: list[str] = []
    cols = {k: [r[k] for r in primary["seed_rows"]] for k in SEED_COLS}
    headline = {
        "spectral_mean_R3": "spectral_R3",
        "random_mean_R3": "random_R3",
        "rho_spec": "rho_spec",
        "rho_rand": "rho_rand",
        "Delta": "Delta",
    }
    for declared, src in headline.items():
        exp = mean(cols[src])
        if abs(primary[declared] - exp) > TOL:
            errs.append(f"{declared}: declared {primary[declared]!r}, recomputed {exp!r}")
    for k, values in cols.items():
        d = primary["dispersion"][k]
        for name, exp in (
            ("mean", mean(values)),
            ("sample_sd", sample_sd(values)),
            ("population_sd", population_sd(values)),
            ("min", min(values)),
            ("max", max(values)),
        ):
            if abs(d[name] - exp) > TOL:
                errs.append(f"dispersion.{k}.{name}: declared {d[name]!r}, recomputed {exp!r}")
    if "L_full" in primary:
        exp = primary["native_R3"] - primary["frozen_full_haar_R3"]
        if abs(primary["L_full"] - exp) > TOL:
            errs.append(f"L_full: declared {primary['L_full']!r}, recomputed {exp!r}")
    return errs


def check_csv_against_json(csv_path: Path, primary: dict) -> list[str]:
    errs: list[str] = []
    with csv_path.open() as fh:
        rows = list(csv.DictReader(fh))
    declared = primary["seed_rows"]
    if len(rows) != len(declared):
        return [f"row count {len(rows)} does not match summary {len(declared)}"]
    for c, r in zip(rows, declared):
        if int(c["seed"]) != r["seed"]:
            errs.append(f"seed order: csv {c['seed']}, summary {r['seed']}")
            continue
        for k in SEED_COLS:
            if abs(float(c[k]) - r[k]) > TOL:
                errs.append(f"seed {r['seed']} {k}: csv {c[k]}, summary {r[k]!r}")
    return errs


def check_manifest(manifest: dict, key: str, summary: dict) -> list[str]:
    errs: list[str] = []
    declared = manifest[key]
    primary = summary["primary"]
    for f in (
        "native_R3",
        "frozen_full_haar_R3",
        "spectral_mean_R3",
        "random_mean_R3",
        "rho_spec",
        "rho_rand",
        "Delta",
        "regime",
    ):
        if declared[f] != primary[f]:
            errs.append(f"{key}.{f}: manifest {declared[f]!r}, summary {primary[f]!r}")
    spread = primary["dispersion"]["Delta"]
    for mf, sf in (("Delta_sample_sd", "sample_sd"), ("Delta_min", "min"), ("Delta_max", "max")):
        if declared[mf] != spread[sf]:
            errs.append(f"{key}.{mf}: manifest {declared[mf]!r}, summary {spread[sf]!r}")
    if declared["native_reproduction_error"] != summary["controls"]["absolute_reproduction_error"]:
        errs.append(f"{key}.native_reproduction_error disagrees with the summary controls block")
    return errs


def main() -> int:
    manifest = json.loads(MANIFEST.read_text())
    report: dict[str, dict] = {}
    failed = False

    for bench, (outdir, manifest_key) in BENCHMARKS.items():
        base = R / outdir
        summary = json.loads((base / f"{bench}_random_partition_summary.json").read_text())
        primary = summary["primary"]
        seed_csv = base / f"{bench}_random_partition_seed_results.csv"

        checks = {
            "A_partition_derivation": check_partitions(summary),
            "B_per_seed_arithmetic": check_per_seed_arithmetic(primary),
            "C_aggregates_and_dispersion": check_aggregates(primary),
            "D_seed_csv_vs_summary_json": check_csv_against_json(seed_csv, primary),
            "E_manifest_vs_summary": check_manifest(manifest, manifest_key, summary),
        }
        result = {k: ("PASS" if not v else v) for k, v in checks.items()}
        result["n_seeds"] = len(primary["seed_rows"])
        result["not_checkable_from_bytes"] = [
            "per-seed spectral_R3 and random_R3 (no per-question output committed)",
            "frozen_full_haar_R3 (inherited denominator, sampling uncertainty unquantified)",
        ]
        report[bench] = result
        failed |= any(v for v in checks.values())

    report["_scope"] = (
        "Internal consistency of committed bytes only. This is NOT an independent "
        "audit and cannot detect an error upstream of the seed-level retrieval numbers."
    )
    print(json.dumps(report, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
