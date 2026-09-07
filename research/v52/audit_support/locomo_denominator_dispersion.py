#!/usr/bin/env python3
"""Cost the LoCoMo Full-Haar denominator uncertainty from committed bytes, now that a panel exists.

Context. The boundary-localization auditor named the inherited Full-Haar denominator the largest
un-costed uncertainty in the line. L-051 costed it on LongMemEval (a five-seed panel is committed in
audit_v52_t4c3) and could only BOUND the consequence on LoCoMo, because no LoCoMo per-seed panel
was committed anywhere. The coordinate-scale stage (2026-09-07) ran a fresh ten-seed full-Haar arm
(FULLHAAR_FRESH, seeds 59001..59010) on the same frozen LoCoMo pipeline and persisted per-question
rows. That panel measures the dispersion of a full-Haar seed-mean on LoCoMo for the first time.

What this script does, from bytes only:
  1. re-derives the ten FULLHAAR_FRESH seed means from the committed per-question CSV (no summary
     value is trusted);
  2. computes their sample sd and the standard error of a FIVE-seed mean (the inherited denominator
     0.13770827054136 was a five-seed mean), and of the ten-seed mean;
  3. re-derives every boundary-localization arm's breakdown denominator from the committed
     locomo_boundary_summary.json (rho = (native - arm) / (native - H) crosses the 0.25 gate);
  4. expresses each breakdown shift in units of that measured dispersion and states whether it lies
     outside a 95% Student-t interval around the inherited denominator.

What it does NOT do: replace any frozen denominator, re-run anything, draw a seed, or transfer the
LongMemEval dispersion. The fresh panel and the inherited five seeds are independent draws under
the same pipeline, not a re-measurement of the same numbers; that is stated, not hidden.

Run from the repository root:
    python3 research/v52/audit_support/locomo_denominator_dispersion.py
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / "research" / "v52"
GATE = 0.25
T_975 = {4: 2.776, 9: 2.262}          # two-sided 95% Student-t critical values (df = n - 1)
INHERITED_FULL_HAAR = 0.13770827054136 # frozen LoCoMo denominator (five-seed mean), unchanged
INHERITED_N = 5
PER_QUESTION = R / "locomo_scale_outputs" / "locomo_scale_per_question.csv.gz"
BOUNDARY_SUMMARY = R / "locomo_boundary_outputs" / "locomo_boundary_summary.json"


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fresh_panel_from_rows(path: Path) -> dict[int, float]:
    """Seed means of FULLHAAR_FRESH re-derived from per-question rows; nothing read from a summary."""
    acc: dict[int, list[float]] = defaultdict(list)
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["arm"] == "FULLHAAR_FRESH":
                acc[int(row["rotation_seed"])].append(float(row["fractional_R3"]))
    if sorted(acc) != list(range(59001, 59011)):
        raise RuntimeError(f"unexpected seed panel {sorted(acc)}")
    counts = {len(v) for v in acc.values()}
    if counts != {1535}:
        raise RuntimeError(f"seed coverage failure {counts}")
    return {s: statistics.fmean(v) for s, v in sorted(acc.items())}


def breakdown_denominator(native: float, arm: float, gate: float = GATE) -> float:
    """H* such that (native - arm) / (native - H*) = gate. The numerator is fixed, so rho RISES as H
    rises toward native (directional control below)."""
    return native - (native - arm) / gate


def rho(native: float, arm: float, full: float) -> float:
    return (native - arm) / (native - full)


def analyse(panel: dict[int, float], boundary: dict) -> dict:
    vals = list(panel.values())
    sd = statistics.stdev(vals)
    se5 = sd / math.sqrt(INHERITED_N)
    se10 = sd / math.sqrt(len(vals))
    half5 = T_975[INHERITED_N - 1] * se5
    interval5 = (INHERITED_FULL_HAAR - half5, INHERITED_FULL_HAAR + half5)
    native = float(boundary["primary"]["native_R3"])
    if abs(float(boundary["primary"]["frozen_full_haar_R3"]) - INHERITED_FULL_HAAR) != 0.0:
        raise RuntimeError("boundary summary carries a different frozen denominator")
    arms = {}
    for name, st in boundary["primary"]["arm_stats"].items():
        arm = float(st["mean_R3"])
        r = rho(native, arm, INHERITED_FULL_HAAR)
        h = breakdown_denominator(native, arm)
        shift = h - INHERITED_FULL_HAAR
        arms[name] = {
            "arm_mean_R3": arm,
            "rho_recorded": float(st["rho"]),
            "rho_rederived": r,
            "verdict": "sufficient" if r <= GATE else "not sufficient",
            "breakdown_denominator": h,
            "shift_needed_abs": shift,
            "shift_needed_pct": 100.0 * shift / INHERITED_FULL_HAAR,
            "shift_in_se5": shift / se5,
            "shift_in_sd": shift / sd,
            "breakdown_outside_95pct_interval": not (interval5[0] <= h <= interval5[1]),
        }
        if abs(r - float(st["rho"])) > 1e-9:
            raise RuntimeError(f"rho mismatch for {name}")
    return {
        "fresh_panel": {"seeds": list(panel), "seed_means": vals, "mean": statistics.fmean(vals),
                        "sample_sd": sd, "se_of_ten_seed_mean": se10,
                        "se_of_five_seed_mean": se5, "sd_pct_of_inherited": 100.0 * sd / INHERITED_FULL_HAAR,
                        "se5_pct_of_inherited": 100.0 * se5 / INHERITED_FULL_HAAR,
                        "fresh_mean_minus_inherited": statistics.fmean(vals) - INHERITED_FULL_HAAR,
                        "fresh_mean_minus_inherited_in_sd": (statistics.fmean(vals) - INHERITED_FULL_HAAR) / sd},
        "inherited_denominator": INHERITED_FULL_HAAR,
        "interval_95_around_inherited_as_five_seed_mean": list(interval5),
        "gate": GATE,
        "arms": arms,
        "tightest_arm": min(arms, key=lambda a: abs(arms[a]["shift_in_se5"])),
    }


def directional_control() -> None:
    """rho must RISE as the denominator rises toward native (the L-051 tooling error, kept as a check)."""
    n, a = 0.5, 0.4
    if not rho(n, a, 0.30) < rho(n, a, 0.35) < rho(n, a, 0.39):
        raise RuntimeError("directional control failed: rho does not rise with H")


def main() -> int:
    directional_control()
    panel = fresh_panel_from_rows(PER_QUESTION)
    boundary = json.loads(BOUNDARY_SUMMARY.read_text(encoding="utf-8"))
    out = analyse(panel, boundary)
    out["sources"] = {
        "per_question_csv": str(PER_QUESTION.relative_to(ROOT)), "per_question_sha256": sha256_file(PER_QUESTION),
        "boundary_summary": str(BOUNDARY_SUMMARY.relative_to(ROOT)), "boundary_summary_sha256": sha256_file(BOUNDARY_SUMMARY),
    }
    evidence = Path(__file__).with_name("locomo_denominator_dispersion_evidence.json")
    evidence.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    fp = out["fresh_panel"]
    print(f"fresh panel: mean {fp['mean']:.9f} sd {fp['sample_sd']:.6f} se5 {fp['se_of_five_seed_mean']:.6f} "
          f"({fp['se5_pct_of_inherited']:.2f}% of inherited) | fresh-inherited {fp['fresh_mean_minus_inherited']:+.6f} "
          f"= {fp['fresh_mean_minus_inherited_in_sd']:+.2f} sd")
    print(f"95% t-interval around inherited (as a 5-seed mean): [{out['interval_95_around_inherited_as_five_seed_mean'][0]:.6f}, "
          f"{out['interval_95_around_inherited_as_five_seed_mean'][1]:.6f}]")
    for a, d in out["arms"].items():
        print(f"{a:9s} rho {d['rho_rederived']:.4f} {d['verdict']:15s} shift {d['shift_needed_pct']:+8.2f}% "
              f"= {d['shift_in_se5']:+7.2f} se5 = {d['shift_in_sd']:+6.2f} sd | outside interval: {d['breakdown_outside_95pct_interval']}")
    print("tightest:", out["tightest_arm"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
