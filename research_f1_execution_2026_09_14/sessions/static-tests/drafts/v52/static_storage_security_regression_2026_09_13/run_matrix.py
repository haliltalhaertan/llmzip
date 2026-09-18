"""Matrix runner: new suite x {V9, mutation variants} + old tests x targets.

Writes RECEIPT.json next to this file. Exits 0 only if every outcome matches
its expectation (V10-ACCEPTANCE passes; EXPECTED-V9-FAIL fails on V9 and on
the variants that inherit the flaw). Any surprise is reported, not hidden.

Usage: ``python3 run_matrix.py`` from this directory.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

SUITE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SUITE_DIR.parents[2]

TARGETS = {
    "v9": str(REPO_ROOT / "drafts/v52/static_storage_integration_v9_2026_09_13"
               / "consumption_gate_v9.py"),
    "variant-retained-snapshot": str(
        SUITE_DIR / "mutation_variants/variant_retained_snapshot.py"),
    "variant-unsafe-loader": str(
        SUITE_DIR / "mutation_variants/variant_unsafe_loader.py"),
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
}

TEST_HEADER = re.compile(r"^(test_\w+) \([\w.]+\)$")
RESULT_TAIL = re.compile(r"\.\.\. (ok|FAIL|ERROR|skipped.*)$")


def run_new_suite(gate_path: str) -> dict:
    env = dict(os.environ)
    env["GATE_UNDER_TEST_PATH"] = gate_path
    proc = subprocess.run(
        [sys.executable, "-B", "-m", "unittest", "-v",
         "test_security_regression"],
        cwd=str(SUITE_DIR), env=env, capture_output=True, text=True,
        timeout=600)
    outcomes: dict = {}
    pending: str | None = None
    for line in (proc.stderr + "\n" + proc.stdout).splitlines():
        stripped = line.strip()
        header = TEST_HEADER.match(stripped)
        if header:
            pending = header.group(1)
            continue
        tail = RESULT_TAIL.search(stripped)
        if tail and pending is not None:
            result = tail.group(1)
            outcomes[pending] = ("pass" if result == "ok"
                                 else "fail" if result == "FAIL" else result)
            pending = None
    tail = (proc.stderr.strip().splitlines() or ["<no stderr>"])[-5:]
    return {"outcomes": outcomes, "returncode": proc.returncode,
            "tail": tail}


def run_old_tests(gate_path: str) -> dict:
    proc = subprocess.run(
        [sys.executable, "-B", "run_old_tests_against_target.py", gate_path],
        cwd=str(SUITE_DIR), capture_output=True, text=True, timeout=600)
    try:
        return {"outcomes": json.loads(proc.stdout or "{}"),
                "returncode": proc.returncode,
                "stderr_tail": proc.stderr.strip().splitlines()[-3:]}
    except json.JSONDecodeError:
        return {"outcomes": {}, "returncode": proc.returncode,
                "stderr_tail": (proc.stdout + proc.stderr)[-2000:]}


def main() -> int:
    receipt: dict = {"targets": {}, "expectations": {
        "EXPECTED_V9_FAIL": sorted(EXPECTED_V9_FAIL),
        "TARGET_EXPECTED_FAIL": {
            k: sorted(v) for k, v in TARGET_EXPECTED_FAIL.items()}}}
    surprises = []
    for label, gate_path in TARGETS.items():
        new = run_new_suite(gate_path)
        old = run_old_tests(gate_path)
        receipt["targets"][label] = {
            "gate": gate_path,
            "new_suite": new,
            "old_tests": old,
        }
        expected_fail = TARGET_EXPECTED_FAIL[label]
        for name, outcome in new["outcomes"].items():
            if name in expected_fail:
                if outcome == "pass":
                    surprises.append(f"{label}:{name} unexpectedly passed")
            elif outcome != "pass":
                surprises.append(f"{label}:{name} -> {outcome} (expected pass)")
        missing = set(expected_fail) - set(new["outcomes"])
        for name in sorted(missing):
            surprises.append(f"{label}:{name} did not run")
    receipt["surprises"] = surprises
    receipt["verdict"] = ("MATRIX-AS-EXPECTED" if not surprises
                          else "MATRIX-DEVIATION")
    (SUITE_DIR / "RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    print("verdict:", receipt["verdict"])
    return 0 if not surprises else 1


if __name__ == "__main__":
    raise SystemExit(main())
