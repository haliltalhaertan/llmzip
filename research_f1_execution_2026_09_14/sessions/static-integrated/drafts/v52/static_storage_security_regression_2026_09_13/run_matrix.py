"""Matrix runner: new suite x {V9, mutation variants, integrated V10} + old tests x targets.

Writes RECEIPT_V10.json next to this file (the V9-only RECEIPT.json from
the cherry-picked audit is left untouched). Exits 0 only if every outcome
matches its expectation. Any surprise is reported, not hidden.

Fail-closed rules (hardened for V10 integration):
- an expected-fail test must outcome EXACTLY "fail" (pass/error/skip/crash
  is a surprise, never silently reclassified);
- every expected new-suite test must run exactly once; unknown extra tests,
  missing tests, skips, errors, and unparsed output are surprises;
- a crashed child (timeout, nonzero return with empty outcomes, JSON that
  does not parse) is a surprise;
- the frozen old suite must be exactly its 7 tests, all "pass", on EVERY
  target; any fail/error/skip/missing/extra old-suite outcome is a surprise.
  (The old suite passing on a broken variant is the documented blindness,
  not a defect of the target; it is recorded, not gated.)

Original per-target expectations are preserved verbatim; the integrated V10
candidate expectation is added explicitly (no expected failures: all 7 new
tests, including the ambient-hashlib protection V9 lacks, must pass).

Usage: ``python3 run_matrix.py`` from this directory.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SUITE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SUITE_DIR.parents[2]
V10_GATE = str(REPO_ROOT / "drafts/v52/static_storage_integration_v10_2026_09_13"
               / "static_storage_preflight_v10.py")

TARGETS = {
    "v9": (str(REPO_ROOT / "drafts/v52/static_storage_integration_v9_2026_09_13"
               / "consumption_gate_v9.py"),
           "preflight_longmemeval_v9"),
    "variant-retained-snapshot": (
        str(SUITE_DIR / "mutation_variants/variant_retained_snapshot.py"),
        "preflight_longmemeval_v9"),
    "variant-unsafe-loader": (
        str(SUITE_DIR / "mutation_variants/variant_unsafe_loader.py"),
        "preflight_longmemeval_v9"),
    "integrated-v10": (V10_GATE, "preflight_longmemeval_v10"),
}

EXPECTED_V9_FAIL = {
    "test_ambient_hashlib_substitution_is_refused",
}

# Per-target expected failures. A variant MUST fail exactly the test(s) that
# target its sabotage class (proving suite sensitivity) plus the flaws it
# inherits from V9. Anything else failing — or an expected failure passing —
# is a recorded surprise, never silently reclassified.
TARGET_EXPECTED_FAIL = {
    "v9": {
        "test_ambient_hashlib_substitution_is_refused",
    },
    "variant-retained-snapshot": {
        "test_ambient_hashlib_substitution_is_refused",
        "test_consumption_revalidates_after_corruption",
    },
    "variant-unsafe-loader": {
        "test_ambient_hashlib_substitution_is_refused",
        "test_ambient_sysmodules_cannot_substitute_code",
    },
    "integrated-v10": set(),
}

# Full new-suite roster: acceptance tests plus the expected-fail protection.
# Any deviation in membership (missing, extra, skipped, unparsed) is a
# surprise; test names/shapes alone are not evidence.
NEW_SUITE_ACCEPTANCE = {
    "test_valid_plan_end_to_end",
    "test_consumption_revalidates_after_corruption",
    "test_ambient_sysmodules_cannot_substitute_code",
    "test_duplicate_physical_copy_rows_are_refused",
    "test_inflated_denominator_plan_is_refused",
    "test_concurrent_consumption_is_isolated",
}

# Frozen V9-era suite roster (5 unit + 2 canonical). Must hold exactly on
# every target; the variants passing it is the known blindness signal.
OLD_SUITE_EXPECTED = {
    "test_context_exposes_no_snapshot_field",
    "test_preflight_discards_validation_snapshot",
    "test_fresh_snapshot_reruns_each_access",
    "test_exact_loader_ignores_preloaded_same_name",
    "test_public_signature",
    "test_exact_v8_chain_loads",
    "test_v8_hashes_match",
}

TEST_HEADER = re.compile(r"^(test_\w+) \([\w.]+\)$")
RESULT_TAIL = re.compile(r"\.\.\. (ok|FAIL|ERROR|skipped.*)$")


def _sha(path: str) -> str:
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return "<unreadable>"


def run_new_suite(gate_path: str, preflight_fn: str) -> dict:
    env = dict(os.environ)
    env["GATE_UNDER_TEST_PATH"] = gate_path
    env["GATE_PREFLIGHT_FN"] = preflight_fn
    try:
        proc = subprocess.run(
            [sys.executable, "-B", "-m", "unittest", "-v",
             "test_security_regression"],
            cwd=str(SUITE_DIR), env=env, capture_output=True, text=True,
            timeout=600)
    except subprocess.TimeoutExpired as exc:
        return {"outcomes": {}, "returncode": "<timeout>", "crashed": True,
                "stdout": "", "stderr": str(exc)[:2000],
                "gate_sha256": _sha(gate_path)}
    outcomes: dict = {}
    counts: dict = {}
    pending: str | None = None
    for line in (proc.stderr + "\n" + proc.stdout).splitlines():
        stripped = line.strip()
        header = TEST_HEADER.match(stripped)
        if header:
            pending = header.group(1)
            counts[pending] = counts.get(pending, 0) + 1
            continue
        tail = RESULT_TAIL.search(stripped)
        if tail and pending is not None:
            result = tail.group(1)
            if result == "ok":
                outcome = "pass"
            elif result == "FAIL":
                outcome = "fail"
            elif result.startswith("skipped"):
                outcome = "skip: %s" % result
            else:
                outcome = result.lower()
            outcomes[pending] = outcome
            pending = None
    if pending is not None:
        outcomes[pending] = "unparsed (header without result)"
    return {"outcomes": outcomes, "returncode": proc.returncode,
            "run_counts": counts, "crashed": False,
            "stdout": proc.stdout, "stderr": proc.stderr,
            "gate_sha256": _sha(gate_path)}


def run_old_tests(gate_path: str) -> dict:
    try:
        proc = subprocess.run(
            [sys.executable, "-B", "run_old_tests_against_target.py",
             gate_path],
            cwd=str(SUITE_DIR), capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired as exc:
        return {"outcomes": {}, "returncode": "<timeout>", "crashed": True,
                "stdout": "", "stderr": str(exc)[:2000],
                "gate_sha256": _sha(gate_path)}
    try:
        full = json.loads(proc.stdout or "null")
        raw = full if isinstance(full, dict) else {}
    except json.JSONDecodeError:
        return {"outcomes": {}, "returncode": proc.returncode,
                "crashed": False, "unparsed": True,
                "stdout": proc.stdout, "stderr": proc.stderr,
                "gate_sha256": _sha(gate_path)}
    short = {}
    for test_id, outcome in raw.items():
        short[str(test_id).split(" ")[0]] = outcome
    return {"outcomes": short, "returncode": proc.returncode,
            "crashed": False, "unparsed": False,
            "stdout": proc.stdout, "stderr": proc.stderr,
            "gate_sha256": _sha(gate_path)}


def main() -> int:
    receipt: dict = {"targets": {}, "expectations": {
        "EXPECTED_V9_FAIL": sorted(EXPECTED_V9_FAIL),
        "TARGET_EXPECTED_FAIL": {
            k: sorted(v) for k, v in TARGET_EXPECTED_FAIL.items()},
        "NEW_SUITE_ACCEPTANCE": sorted(NEW_SUITE_ACCEPTANCE),
        "OLD_SUITE_EXPECTED": sorted(OLD_SUITE_EXPECTED)}}
    surprises = []
    for label, (gate_path, preflight_fn) in TARGETS.items():
        new = run_new_suite(gate_path, preflight_fn)
        old = run_old_tests(gate_path)
        receipt["targets"][label] = {
            "gate": gate_path,
            "preflight_fn": preflight_fn,
            "new_suite": new,
            "old_tests": old,
        }
        expected_fail = TARGET_EXPECTED_FAIL[label]
        expected_all = set(expected_fail) | NEW_SUITE_ACCEPTANCE | EXPECTED_V9_FAIL
        if new.get("crashed"):
            surprises.append(f"{label}: new-suite harness crashed")
        for name, outcome in new["outcomes"].items():
            if name in expected_fail:
                if outcome != "fail":
                    surprises.append(
                        f"{label}:{name} -> {outcome} (expected FAIL)")
            elif name in expected_all:
                if outcome != "pass":
                    surprises.append(
                        f"{label}:{name} -> {outcome} (expected pass)")
            else:
                surprises.append(f"{label}:{name} unexpected test ran")
        for name in sorted(expected_all - set(new["outcomes"])):
            surprises.append(f"{label}:{name} did not run")
        dupes = [n for n, c in new.get("run_counts", {}).items() if c != 1]
        for name in sorted(dupes):
            surprises.append(f"{label}:{name} ran {new['run_counts'][name]}x")
        if old.get("crashed") or old.get("unparsed"):
            surprises.append(f"{label}: old-suite harness crashed/unparsed")
        else:
            for name, outcome in old["outcomes"].items():
                if name not in OLD_SUITE_EXPECTED:
                    surprises.append(
                        f"{label}:old-suite unexpected test {name}")
                elif outcome != "pass":
                    surprises.append(
                        f"{label}:old-suite {name} -> {outcome} "
                        f"(expected pass; blindness signal if pass on "
                        f"variant, defect if not)")
            for name in sorted(OLD_SUITE_EXPECTED - set(old["outcomes"])):
                surprises.append(f"{label}:old-suite {name} did not run")
    receipt["surprises"] = surprises
    receipt["verdict"] = ("MATRIX-AS-EXPECTED" if not surprises
                          else "MATRIX-DEVIATION")
    (SUITE_DIR / "RECEIPT_V10.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    print(json.dumps({"targets": {t: {
        "new_outcomes": v["new_suite"]["outcomes"],
        "new_returncode": v["new_suite"]["returncode"],
        "old_outcomes": v["old_tests"]["outcomes"],
        "old_returncode": v["old_tests"]["returncode"],
        "gate_sha256": v["new_suite"]["gate_sha256"]}
        for t, v in receipt["targets"].items()},
        "surprises": surprises, "verdict": receipt["verdict"]},
        indent=2, sort_keys=True))
    print("verdict:", receipt["verdict"])
    return 0 if not surprises else 1


if __name__ == "__main__":
    raise SystemExit(main())
