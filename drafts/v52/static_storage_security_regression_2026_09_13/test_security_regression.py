"""V52 static-storage implementation-independent security regression suite.

Every test runs the REAL public entrypoint of the gate under test
(``GATE_UNDER_TEST_PATH``) against REALISTIC temp plan/bindings files built
from the pinned anchor and contract. No test greps source text; each attack
input is executed and the gate must refuse it (``ValueError``) or, for the
one documented exception, the suite records the acceptance as failure.

Expectation labels (also mirrored in ``run_matrix.py`` and the audit report):
- ``[V10-ACCEPTANCE]``: must pass on V9 and on any V10 candidate.
- ``[EXPECTED-V9-FAIL]``: demonstrates a protection V9 lacks; fails on V9
  (and on the mutation variants, which inherit the flaw) and must pass on V10.

Run: ``python3 -B -m unittest -v test_security_regression`` from this
directory. Point at another candidate without editing anything::

    GATE_UNDER_TEST_PATH=/path/to/candidate_gate.py \\
    GATE_PREFLIGHT_FN=preflight_longmemeval_v10 \\
    python3 -B -m unittest -v test_security_regression
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path

import gate_adapter
from gate_adapter import denominators, fresh_denominators, preflight
import e2e_fixtures

SUITE_DIR = Path(__file__).resolve().parent
ADVERSARIAL_DIR = SUITE_DIR / "adversarial"

GATE = gate_adapter.load_gate()

# Tests V9 is expected to FAIL (protections absent in V9, required of V10).
EXPECTED_V9_FAIL = {
    "test_ambient_hashlib_substitution_is_refused",
}

# Tests that must pass on V9 and on V10.
V10_ACCEPTANCE = {
    "test_valid_plan_end_to_end",
    "test_consumption_revalidates_after_corruption",
    "test_ambient_sysmodules_cannot_substitute_code",
    "test_duplicate_physical_copy_rows_are_refused",
    "test_inflated_denominator_plan_is_refused",
    "test_concurrent_consumption_is_isolated",
}


def load_module_from(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SecurityRegression(unittest.TestCase):
    maxDiff = 4096

    def test_valid_plan_end_to_end(self):
        """[V10-ACCEPTANCE] Real entrypoint accepts a realistic valid set."""
        with tempfile.TemporaryDirectory() as td:
            fx = e2e_fixtures.build_valid_set(Path(td), "regen-accept-01")
            ctx = preflight(GATE, fx.plan_path, fx.plan_sha, fx.fixture_path,
                            fx.fixture_sha, fx.physical_path, fx.physical_sha)
            dense = denominators(ctx)
            fresh = fresh_denominators(ctx)
            self.assertEqual(len(dense), 470)
            self.assertEqual(tuple(dense), tuple(fresh))
            first = dense[0]
            self.assertEqual(len(first), 3)
            copy_id, pop_id, count = first
            self.assertTrue(copy_id.startswith("copy-"))
            self.assertTrue(pop_id.startswith("pop-"))
            self.assertIs(type(count), int)
            self.assertEqual(
                {c for c, _p, _d in dense},
                {f"copy-{i}" for i in range(470)},
                "denominator roster must equal the physical-copy roster",
            )

    def test_consumption_revalidates_after_corruption(self):
        """[V10-ACCEPTANCE] No validated snapshot may survive file corruption.

        After an artifact is rewritten, BOTH the fresh path and the
        authoritative-denominator path must refuse. A gate that serves a
        retained snapshot from either path fails here.
        """
        with tempfile.TemporaryDirectory() as td:
            fx = e2e_fixtures.build_valid_set(Path(td), "regen-stale-01")
            ctx = preflight(GATE, fx.plan_path, fx.plan_sha, fx.fixture_path,
                            fx.fixture_sha, fx.physical_path, fx.physical_sha)
            before = denominators(ctx)
            self.assertEqual(len(before), 470)
            e2e_fixtures.corrupt_first_physical_artifact(fx)
            with self.assertRaises(ValueError):
                ctx.fresh_snapshot()
            with self.assertRaises(ValueError):
                denominators(ctx)

    def test_ambient_sysmodules_cannot_substitute_code(self):
        """[V10-ACCEPTANCE] Planted v8_runtime/v8_snapshot must be inert.

        Explicit malicious modules (see adversarial/) are planted in
        ``sys.modules`` under the exact dependency names. The gate must still
        refuse garbage input AND still accept a valid set with correct
        denominators; executing the planted code in either direction fails.
        """
        runtime = load_module_from(
            ADVERSARIAL_DIR / "malicious_v8_runtime.py",
            "malicious_v8_runtime_case")
        snapshot = load_module_from(
            ADVERSARIAL_DIR / "malicious_v8_snapshot.py",
            "malicious_v8_snapshot_case")
        planted = {"v8_runtime": runtime, "v8_snapshot": snapshot}
        saved = {k: sys.modules.get(k) for k in planted}
        sys.modules.update(planted)
        try:
            with tempfile.TemporaryDirectory() as td:
                fx = e2e_fixtures.build_valid_set(Path(td), "regen-poison-01")
                # Garbage input must be refused even with malicious deps bound.
                with self.assertRaises(ValueError):
                    preflight(GATE, fx.plan_path, "0" * 64, fx.fixture_path,
                              "0" * 64, fx.physical_path, "0" * 64)
                # A valid set must still verify with TRUE denominators.
                ctx = preflight(GATE, fx.plan_path, fx.plan_sha,
                                fx.fixture_path, fx.fixture_sha,
                                fx.physical_path, fx.physical_sha)
                dense = denominators(ctx)
                self.assertEqual(len(dense), 470)
                for _c, _p, d in dense:
                    self.assertLess(d, 10 ** 9)
        finally:
            for key, old in saved.items():
                if old is None:
                    sys.modules.pop(key, None)
                else:
                    sys.modules[key] = old

    def test_ambient_hashlib_substitution_is_refused(self):
        """[EXPECTED-V9-FAIL] Ambient hashlib must not vouch for swapped bytes.

        A tampered-but-content-valid plan is presented with the ORIGINAL
        digest while ambient ``hashlib.sha256`` is patched to vouch for the
        tampered bytes. A gate that resolves its trust root dynamically
        accepts the swap; a gate that captured pristine references refuses.
        """
        real_sha256 = hashlib.sha256
        with tempfile.TemporaryDirectory() as td:
            fx = e2e_fixtures.build_valid_set(Path(td), "regen-hash-01")
            tampered = e2e_fixtures.rewrite_plan_with_new_run_id(
                fx, "regen-hash-ATTACKER")
            fx.plan_path.write_bytes(tampered)
            self.assertNotEqual(real_sha256(tampered).hexdigest(),
                                fx.plan_sha)

            class VouchingHash:
                def __init__(self, data=b""):
                    self._data = bytes(data)

                def update(self, more):
                    self._data += bytes(more)

                def hexdigest(self):
                    if self._data == tampered:
                        return fx.plan_sha
                    return real_sha256(self._data).hexdigest()

                def digest(self):
                    return bytes.fromhex(self.hexdigest())

            hashlib.sha256 = VouchingHash
            try:
                with self.assertRaises(ValueError):
                    preflight(GATE, fx.plan_path, fx.plan_sha,
                              fx.fixture_path, fx.fixture_sha,
                              fx.physical_path, fx.physical_sha)
            finally:
                hashlib.sha256 = real_sha256

    def test_duplicate_physical_copy_rows_are_refused(self):
        """[V10-ACCEPTANCE] A repeated physical_copy_id must not double-count.

        The bindings digest is re-issued for the duplicated document, so only
        the roster-uniqueness layer can refuse it.
        """
        with tempfile.TemporaryDirectory() as td:
            fx = e2e_fixtures.build_valid_set(Path(td), "regen-dup-01")
            e2e_fixtures.rewrite_physical_bindings_with_duplicate(fx)
            with self.assertRaises(ValueError):
                preflight(GATE, fx.plan_path, fx.plan_sha, fx.fixture_path,
                          fx.fixture_sha, fx.physical_path, fx.physical_sha)

    def test_inflated_denominator_plan_is_refused(self):
        """[V10-ACCEPTANCE] Guard-shaped but anchor-violating N must refuse.

        Probe N and BEFORE/AFTER counts are raised together (guard stays
        satisfied); the pinned anchor no longer authorizes the denominator.
        """
        with tempfile.TemporaryDirectory() as td:
            fx = e2e_fixtures.build_valid_set(Path(td), "regen-dilute-01")
            e2e_fixtures.rewrite_plan_with_inflated_denominator(fx)
            with self.assertRaises(ValueError):
                preflight(GATE, fx.plan_path, fx.plan_sha, fx.fixture_path,
                          fx.fixture_sha, fx.physical_path, fx.physical_sha)

    def test_concurrent_consumption_is_isolated(self):
        """[V10-ACCEPTANCE] Barrier-started threads must not cross-bind.

        Two threads consume valid sets (distinct run_ids/dirs, denominators
        must match a single-threaded oracle); two consume corrupted sets and
        must both refuse. Any input or module cross-talk fails this test.
        """
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            oracle_fx = e2e_fixtures.build_valid_set(root / "oracle",
                                                     "regen-conc-oracle")
            oracle_ctx = preflight(
                GATE, oracle_fx.plan_path, oracle_fx.plan_sha,
                oracle_fx.fixture_path, oracle_fx.fixture_sha,
                oracle_fx.physical_path, oracle_fx.physical_sha)
            oracle = tuple(denominators(oracle_ctx))
            self.assertEqual(len(oracle), 470)

            barrier = threading.Barrier(4)
            outcomes: dict = {}

            def valid_worker(tag):
                try:
                    barrier.wait(timeout=60)
                    fx = e2e_fixtures.build_valid_set(root / tag, tag)
                    ctx = preflight(GATE, fx.plan_path, fx.plan_sha,
                                    fx.fixture_path, fx.fixture_sha,
                                    fx.physical_path, fx.physical_sha)
                    outcomes[tag] = ("ok", tuple(denominators(ctx))
                                     == oracle)
                except Exception as exc:  # noqa: BLE001
                    outcomes[tag] = ("error",
                                     f"{exc.__class__.__name__}: {exc}")

            def invalid_worker(tag):
                try:
                    barrier.wait(timeout=60)
                    fx = e2e_fixtures.build_valid_set(root / tag, tag)
                    e2e_fixtures.corrupt_first_physical_artifact(fx)
                    try:
                        preflight(GATE, fx.plan_path, fx.plan_sha,
                                  fx.fixture_path, fx.fixture_sha,
                                  fx.physical_path, fx.physical_sha)
                    except ValueError:
                        outcomes[tag] = ("refused", True)
                    else:
                        outcomes[tag] = ("accepted", False)
                except Exception as exc:  # noqa: BLE001
                    outcomes[tag] = ("error",
                                     f"{exc.__class__.__name__}: {exc}")

            threads = [
                threading.Thread(target=valid_worker,
                                 args=("regen-conc-a",)),
                threading.Thread(target=valid_worker,
                                 args=("regen-conc-b",)),
                threading.Thread(target=invalid_worker,
                                 args=("regen-conc-c",)),
                threading.Thread(target=invalid_worker,
                                 args=("regen-conc-d",)),
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=180)
            self.assertEqual(len(outcomes), 4, outcomes)
            for tag in ("regen-conc-a", "regen-conc-b"):
                self.assertEqual(outcomes[tag], ("ok", True), tag)
            for tag in ("regen-conc-c", "regen-conc-d"):
                self.assertEqual(outcomes[tag], ("refused", True), tag)


if __name__ == "__main__":
    unittest.main()

