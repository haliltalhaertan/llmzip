"""Run the FROZEN V9-era test file against an arbitrary gate module.

Usage: ``python3 run_old_tests_against_target.py <gate_path>``.
Prints JSON ``{test_id: outcome}`` where outcome is pass/fail/error/skip.

The old test file does ``import consumption_gate_v9``; that name is
pre-seeded with the target module so the unmodified frozen tests exercise the
target. Frozen files are never edited or copied.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
V9_DIR = (REPO_ROOT / "drafts/v52/static_storage_integration_v9_2026_09_13")
OLD_TEST = V9_DIR / "test_consumption_gate_v9.py"


def load_gate_as_consumption_gate_v9(gate_path: str):
    digest = hashlib.sha256(gate_path.encode()).hexdigest()[:12]
    spec = importlib.util.spec_from_file_location(
        f"consumption_gate_v9_target_{digest}", gate_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["consumption_gate_v9"] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    gate_path = sys.argv[1]
    load_gate_as_consumption_gate_v9(gate_path)
    spec = importlib.util.spec_from_file_location(
        "test_consumption_gate_v9_frozen", str(OLD_TEST))
    assert spec is not None and spec.loader is not None
    test_mod = importlib.util.module_from_spec(spec)
    sys.modules["test_consumption_gate_v9_frozen"] = test_mod
    spec.loader.exec_module(test_mod)
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_mod)
    results: dict = {}

    class Collector(unittest.TestResult):
        def addSuccess(self, test):
            results[str(test)] = "pass"
            super().addSuccess(test)

        def addFailure(self, test, err):
            results[str(test)] = "fail"
            super().addFailure(test, err)

        def addError(self, test, err):
            results[str(test)] = "error"
            super().addError(test, err)

        def addSkip(self, test, reason):
            results[str(test)] = f"skip: {reason}"
            super().addSkip(test, reason)

    runner = unittest.TextTestRunner(resultclass=Collector, stream=open(
        "/dev/null", "w"), verbosity=0)
    runner.run(suite)
    print(json.dumps(results, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
