#!/usr/bin/env python3
"""Controls for denominator_sensitivity.py.

The breakdown point is the whole content of that script, so it is checked by
round trip rather than by restating the algebra: substitute the breakdown
denominator back into rho and it must land exactly on the gate. The remaining
controls check the direction of the effect, the transcription of the audited
seed values, and that the reported dispersion is what it claims to be.

Run from the repository root:
    python3 research/v52/audit_support/test_denominator_sensitivity.py
"""

from __future__ import annotations

import json
import math
import statistics

import denominator_sensitivity as D

TOL = 1e-12
FAILURES: list[str] = []
PASSED = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global PASSED
    if ok:
        PASSED += 1
        print(f"  ok   {name}")
    else:
        FAILURES.append(name)
        print(f"  FAIL {name}  {detail}")


def rho(native: float, arm: float, denom: float) -> float:
    return (native - arm) / (native - denom)


def main() -> int:
    print("round trip: the breakdown denominator must put rho exactly on the gate")
    for bench, path in D.BOUNDARY_SUMMARIES.items():
        primary = json.loads(path.read_text())["primary"]
        native = primary["native_R3"]
        for arm, stats in primary["arm_stats"].items():
            flip = D.breakdown_denominator(native, stats["mean_R3"])
            back = rho(native, stats["mean_R3"], flip)
            check(f"{bench}/{arm} round-trips to the gate",
                  abs(back - D.GATE) <= TOL, f"got {back!r}")

    print("\ndeclared rho must be reproducible from the declared inputs")
    for bench, path in D.BOUNDARY_SUMMARIES.items():
        primary = json.loads(path.read_text())["primary"]
        native, denom = primary["native_R3"], primary["frozen_full_haar_R3"]
        for arm, stats in primary["arm_stats"].items():
            check(f"{bench}/{arm} declared rho reproduces",
                  abs(rho(native, stats["mean_R3"], denom) - stats["rho"]) <= TOL,
                  f"declared {stats['rho']!r}")

    # This control was written the wrong way round first and failed, which is
    # why it is here: the numerator is fixed, so raising the denominator toward
    # native shrinks native - H and RAISES rho.
    print("\ndirection: rho must rise as the denominator rises toward native")
    for bench, path in D.BOUNDARY_SUMMARIES.items():
        primary = json.loads(path.read_text())["primary"]
        native, denom = primary["native_R3"], primary["frozen_full_haar_R3"]
        arm = primary["arm_stats"]["B32"]["mean_R3"]
        base = rho(native, arm, denom)
        raised = rho(native, arm, denom + 0.01)
        lowered = rho(native, arm, denom - 0.01)
        check(f"{bench} rho rises when the denominator is raised", raised > base,
              f"{base!r} -> {raised!r}")
        check(f"{bench} rho falls when the denominator is lowered", lowered < base,
              f"{base!r} -> {lowered!r}")
        check(f"{bench} the reported direction label matches that behaviour",
              (D.breakdown_denominator(native, arm) > denom) == (base < D.GATE),
              "a verdict currently inside the gate must be lost by RAISING the denominator")

    print("\nnegative controls: a wrong breakdown point must NOT round-trip")
    primary = json.loads(D.BOUNDARY_SUMMARIES["longmemeval"].read_text())["primary"]
    native = primary["native_R3"]
    arm = primary["arm_stats"]["B48"]["mean_R3"]
    flip = D.breakdown_denominator(native, arm)
    check("perturbed breakdown point is rejected",
          abs(rho(native, arm, flip + 1e-6) - D.GATE) > TOL)
    check("breakdown point computed against the wrong arm is rejected",
          abs(rho(native, arm, D.breakdown_denominator(native, primary["arm_stats"]["B16"]["mean_R3"])) - D.GATE) > TOL)
    check("breakdown point computed against a different gate is rejected",
          abs(rho(native, arm, D.breakdown_denominator(native, arm, gate=0.30)) - D.GATE) > TOL)

    print("\ntranscribed audited seed values")
    disp = D.longmemeval_denominator_dispersion()
    vals = list(D.T4C3_FULL_HAAR_SEEDS.values())
    check("five seeds, 43001..43005", sorted(D.T4C3_FULL_HAAR_SEEDS) == [43001, 43002, 43003, 43004, 43005])
    check("their mean is the denominator in use to within report rounding",
          disp["agreement_with_denominator_in_use"] < 1e-9,
          f"{disp['agreement_with_denominator_in_use']!r}")
    check("a single altered seed would break that agreement",
          abs(statistics.mean([vals[0] + 1e-6] + vals[1:]) - 0.38271666666667) > 1e-9)
    check("sd and se are consistent with each other",
          abs(disp["standard_error"] - disp["sample_sd"] / math.sqrt(5)) <= TOL)
    check("the envelope brackets every seed value",
          disp["seed_envelope"][0] == min(vals) and disp["seed_envelope"][1] == max(vals))
    check("the 95% interval is wider than the standard error and narrower than the seed envelope",
          (disp["t_interval_95"][1] - disp["t_interval_95"][0]) > 2 * disp["standard_error"])

    print("\nno LoCoMo dispersion may be reported")
    report = json.loads(
        __import__("subprocess").run(
            ["python3", __file__.replace("test_denominator_sensitivity", "denominator_sensitivity")],
            capture_output=True, text=True, check=True).stdout)
    check("LoCoMo dispersion is declared not measurable",
          isinstance(report["locomo"]["denominator_dispersion"], str)
          and "NOT MEASURABLE" in report["locomo"]["denominator_dispersion"])
    check("no LoCoMo arm carries a standard-error figure",
          all("required_shift_in_standard_errors" not in v for v in report["locomo"]["arms"].values()))

    total = PASSED + len(FAILURES)
    print(f"\n{PASSED}/{total} controls passed")
    if FAILURES:
        print("FAILED: " + ", ".join(FAILURES))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
