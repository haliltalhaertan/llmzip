#!/usr/bin/env python3
"""Cost the Full-Haar denominator uncertainty, so far as committed bytes allow.

The boundary-localization auditor named the inherited Full-Haar denominator as
"the single largest un-costed source of uncertainty in the line". This script
costs it on the side where a source exists, and bounds its consequence on the
side where none does.

  LongMemEval: the denominator IS traceable. audit_v52_t4c3/AUDIT_REPORT.md on
               canonical main - an independent audit accepted 2026-08-28 -
               commits the five per-seed full-Haar values (rotation seeds
               43001..43005, block_size 96) whose mean is the denominator in
               use. Their dispersion is therefore measurable from bytes.
  LoCoMo:      no per-seed source is committed anywhere. Its denominator's
               dispersion is NOT measurable and this script does not invent one.

For both benchmarks the script computes the breakdown point of every verdict:
the denominator value at which rho = (native - arm) / (native - full_haar)
would cross the preregistered 0.25 sufficiency gate. That converts an
unquantified uncertainty into a bounded consequence, which is a weaker but
honest substitute for measuring it.

Run from the repository root:
    python3 research/v52/audit_support/denominator_sensitivity.py
"""

from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / "research" / "v52"
GATE = 0.25
T_975_DF4 = 2.776  # two-sided 95% Student t critical value at 4 degrees of freedom

# Transcribed from audit_v52_t4c3/AUDIT_REPORT.md (sha256
# 8f6b31050c6e211b7c34ba8214405cff91251d33bd590be97c996ce17f2be238), section
# "Full-Haar seed-specific Fractional R@3 values". Percentages there, fractions
# here. Nine decimal places is the precision that report publishes.
T4C3_FULL_HAAR_SEEDS = {
    43001: 0.361395390,
    43002: 0.391393617,
    43003: 0.379320922,
    43004: 0.380195035,
    43005: 0.401278369,
}
T4C3_REPORT_SHA256 = "8f6b31050c6e211b7c34ba8214405cff91251d33bd590be97c996ce17f2be238"

BOUNDARY_SUMMARIES = {
    "locomo": R / "locomo_boundary_outputs" / "locomo_boundary_summary.json",
    "longmemeval": R / "longmemeval_boundary_outputs" / "longmemeval_boundary_summary.json",
}


def breakdown_denominator(native: float, arm: float, gate: float = GATE) -> float:
    """The full-Haar value H at which rho = (native - arm) / (native - H) = gate.

    The numerator is fixed, so rho RISES as H rises toward native (the gap
    native - H shrinks) and falls as H moves away from it. A breakdown point
    ABOVE the denominator in use therefore means the verdict is lost only if
    the true denominator is HIGHER than the recorded one, and a breakdown point
    below it means the verdict is lost only if the true denominator is LOWER.
    """
    return native - (native - arm) / gate


def longmemeval_denominator_dispersion() -> dict:
    values = list(T4C3_FULL_HAAR_SEEDS.values())
    n = len(values)
    mean = statistics.mean(values)
    sd = statistics.stdev(values)
    se = sd / math.sqrt(n)
    return {
        "source": "audit_v52_t4c3/AUDIT_REPORT.md (independent audit, accepted 2026-08-28)",
        "source_sha256": T4C3_REPORT_SHA256,
        "rotation_seeds": sorted(T4C3_FULL_HAAR_SEEDS),
        "n": n,
        "mean_of_published_seed_values": mean,
        "denominator_in_use": 0.38271666666667,
        "agreement_with_denominator_in_use": abs(mean - 0.38271666666667),
        "agreement_note": (
            "the residual is the rounding of the audit report's nine published "
            "decimal places, not a disagreement about the value"
        ),
        "sample_sd": sd,
        "standard_error": se,
        "relative_standard_error_pct": se / mean * 100.0,
        "seed_envelope": [min(values), max(values)],
        "t_interval_95": [mean - T_975_DF4 * se, mean + T_975_DF4 * se],
    }


def analyse(bench: str, path: Path, dispersion: dict | None) -> dict:
    primary = json.loads(path.read_text())["primary"]
    native = primary["native_R3"]
    denom = primary["frozen_full_haar_R3"]
    arms = {}
    for arm, stats in primary["arm_stats"].items():
        rho = stats["rho"]
        flip = breakdown_denominator(native, stats["mean_R3"])
        shift = flip - denom
        entry = {
            "rho": rho,
            "verdict": "SUFFICIENT (rho <= 0.25)" if rho <= GATE else "not sufficient",
            "denominator_at_which_verdict_flips": flip,
            "required_shift": shift,
            "required_shift_pct_of_denominator": shift / denom * 100.0,
            "direction": "lost only if the true denominator is HIGHER than recorded" if shift > 0
                         else "lost only if the true denominator is LOWER than recorded",
        }
        if dispersion is not None:
            se = dispersion["standard_error"]
            entry["required_shift_in_standard_errors"] = abs(shift) / se
            lo, hi = dispersion["t_interval_95"]
            entry["flip_inside_95_interval"] = lo <= flip <= hi
        arms[arm] = entry

    tightest = min(arms, key=lambda a: abs(arms[a]["required_shift_pct_of_denominator"]))
    return {
        "native_R3": native,
        "denominator_in_use": denom,
        "denominator_dispersion": dispersion if dispersion else "NOT MEASURABLE - no per-seed source is committed",
        "arms": arms,
        "tightest_verdict": tightest,
        "tightest_required_shift_pct": arms[tightest]["required_shift_pct_of_denominator"],
    }


def main() -> int:
    dispersion = longmemeval_denominator_dispersion()
    report = {
        "locomo": analyse("locomo", BOUNDARY_SUMMARIES["locomo"], None),
        "longmemeval": analyse("longmemeval", BOUNDARY_SUMMARIES["longmemeval"], dispersion),
        "_scope": (
            "Arithmetic on committed declared numbers and on one independently "
            "audited artifact. No corpus was read, no seed was drawn, no "
            "retrieval was computed. This does not measure the LoCoMo "
            "denominator's dispersion and does not transfer the LongMemEval "
            "figure to it."
        ),
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
