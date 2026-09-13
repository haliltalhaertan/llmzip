"""Integrated V10 tests: hardened chain + unique-by-archive denominator.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Scope: LongMemEval-only preparation checks. No storage measurement, no model
fit, no retrieval, no Task4F1 outcome access, no run authorization.

The acceptance test below runs the REAL integrated entrypoint
(``static_storage_preflight_v10.preflight_longmemeval_v10``) against REAL
temp plan/bindings files with DISTINCT duplicate physical copies per
archive. No stubs, no mocks on that path.
"""
import hashlib
import inspect
import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path

import static_storage_preflight_v10 as v10

_SUITE_DIR = Path(__file__).resolve().parent
_SEC_DIR = _SUITE_DIR.parent / "static_storage_security_regression_2026_09_13"
sys.path.insert(0, str(_SEC_DIR))

import e2e_fixtures  # noqa: E402

LABELS = ("[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] "
          "[NOT FOR CITATION] [DISCLOSE-BEFORE-USE]")


def _duplicate_copy_set(root, run_id):
    """Valid 470-archive set plus a SECOND distinct copy per archive.

    Same (archive, config, format, item) coverage the contract requires;
    distinct copy ids, distinct artifact identities, distinct artifact
    bytes. Digests re-issued from file bytes, exactly as a real caller
    must. No contract adaptation: the guard's copy inventory is keyed by
    (archive, config, format, item) and its comment explicitly permits
    distinct physical identities (``two actual file copies``).
    """
    fx = e2e_fixtures.build_valid_set(root, run_id)
    plan = json.loads(fx.plan_path.read_bytes().decode("utf-8"))
    aids = [(a["id"], a["N_i"]) for a in plan["archives"]]
    copies = plan["physical_copies"]
    by_id = {c["id"]: c for c in copies}
    assert len(copies) == 470, len(copies)
    new_copies = []
    phys_doc = json.loads(fx.physical_path.read_bytes().decode("utf-8"))
    new_rows = []
    for i, (aid, _n) in enumerate(aids):
        first = by_id["copy-%d" % i]
        assert first["archive_id"] == aid
        raw = ("physical-bytes-%s-%04d-B" % (run_id, i)).encode()
        (root / ("phys-%04d-b.bin" % i)).write_bytes(raw)
        second = dict(first)
        second["id"] = "copy-%d-b" % i
        second["artifact_identity"] = "phys-ident-%04d-b" % i
        second["artifact_sha256"] = hashlib.sha256(raw).hexdigest()
        new_copies.append(second)
        template = phys_doc["physical_copies"][i]
        assert template["physical_copy_id"] == "copy-%d" % i
        row = dict(template)
        row["physical_copy_id"] = "copy-%d-b" % i
        row["physical_locator"] = "phys-%04d-b.bin" % i
        row["source_raw_byte_length"] = len(raw)
        row["artifact_sha256"] = hashlib.sha256(raw).hexdigest()
        new_rows.append(row)
    plan["physical_copies"] = copies + new_copies
    plan_raw = json.dumps(plan, sort_keys=True).encode("utf-8")
    fx.plan_path.write_bytes(plan_raw)
    fx.plan_sha = hashlib.sha256(plan_raw).hexdigest()
    phys_doc["physical_copies"] = phys_doc["physical_copies"] + new_rows
    phys_raw = json.dumps(phys_doc, sort_keys=True).encode("utf-8")
    fx.physical_path.write_bytes(phys_raw)
    fx.physical_sha = hashlib.sha256(phys_raw).hexdigest()
    return fx


class AcceptanceDuplicateCopyE2E(unittest.TestCase):
    """Valid plan, DISTINCT duplicate copies, real entrypoint, no stubs."""

    def test_940_distinct_copies_yield_231606_unique_by_archive(self):
        with tempfile.TemporaryDirectory() as td:
            fx = _duplicate_copy_set(Path(td), "v10-int-dup-01")
            ctx = v10.preflight_longmemeval_v10(
                fx.plan_path, fx.plan_sha, fx.fixture_path,
                fx.fixture_sha, fx.physical_path, fx.physical_sha)
            rows = ctx.logical_denominator_rows()
            self.assertEqual(len(rows), 940)
            for row in rows:
                self.assertIs(type(row), v10.LogicalDenominatorRow)
                self.assertEqual(
                    row._fields,
                    ("archive_id", "physical_copy_id",
                     "population_id", "n_i"))
            self.assertEqual(len({r.physical_copy_id for r in rows}), 940)
            self.assertEqual(len({r.archive_id for r in rows}), 470)
            by_archive = {}
            for row in rows:
                by_archive.setdefault(row.archive_id, []).append(row)
            for aid, pair in by_archive.items():
                self.assertEqual(len(pair), 2, aid)
                self.assertNotEqual(
                    pair[0].physical_copy_id, pair[1].physical_copy_id)
                self.assertEqual(pair[0].n_i, pair[1].n_i)
            self.assertEqual(ctx.naive_copy_total_vectors(), 463212)
            self.assertEqual(ctx.logical_total_vectors(), 231606)
            text = v10.labeled_summary(
                logical_total=ctx.logical_total_vectors(),
                naive_total=ctx.naive_copy_total_vectors(),
                n_archives=470, n_copies=940)
            self.assertTrue(text.startswith(LABELS))
            self.assertIn("logical_total=231606", text)
            self.assertIn("naive_copy_total=463212", text)
            # Fresh revalidation: a second access reruns the chain.
            self.assertEqual(ctx.logical_total_vectors(), 231606)
            dense = ctx.authoritative_denominators()
            self.assertEqual(len(dense), 940)

    def test_single_copy_baseline_still_accepts(self):
        with tempfile.TemporaryDirectory() as td:
            fx = e2e_fixtures.build_valid_set(Path(td), "v10-int-base-01")
            ctx = v10.preflight_longmemeval_v10(
                fx.plan_path, fx.plan_sha, fx.fixture_path,
                fx.fixture_sha, fx.physical_path, fx.physical_sha)
            self.assertEqual(len(ctx.logical_denominator_rows()), 470)
            self.assertEqual(ctx.logical_total_vectors(), 231606)


class RevalidationTests(unittest.TestCase):
    def test_consumption_refuses_after_corruption_on_both_paths(self):
        with tempfile.TemporaryDirectory() as td:
            fx = e2e_fixtures.build_valid_set(Path(td), "v10-int-stale-01")
            ctx = v10.preflight_longmemeval_v10(
                fx.plan_path, fx.plan_sha, fx.fixture_path,
                fx.fixture_sha, fx.physical_path, fx.physical_sha)
            self.assertEqual(ctx.logical_total_vectors(), 231606)
            e2e_fixtures.corrupt_first_physical_artifact(fx)
            with self.assertRaises(ValueError):
                ctx.fresh_snapshot()
            with self.assertRaises(ValueError):
                ctx.authoritative_denominators()
            with self.assertRaises(ValueError):
                ctx.logical_denominator_rows()

    def test_context_carries_no_snapshot(self):
        ctx = v10.V10Context("p", "1" * 64, "f", "2" * 64, "b", "3" * 64)
        self.assertFalse(hasattr(ctx, "initial_snapshot"))
        self.assertEqual(ctx._fields,
                         ("plan_path", "expected_plan_sha256",
                          "fixture_bindings_path",
                          "expected_fixture_bindings_sha256",
                          "physical_bindings_path",
                          "expected_physical_bindings_sha256"))


class LoaderHardeningTests(unittest.TestCase):
    def test_no_sysmodules_publication(self):
        before = set(sys.modules)
        with tempfile.TemporaryDirectory() as td:
            fx = e2e_fixtures.build_valid_set(Path(td), "v10-int-hyg-01")
            ctx = v10.preflight_longmemeval_v10(
                fx.plan_path, fx.plan_sha, fx.fixture_path,
                fx.fixture_sha, fx.physical_path, fx.physical_sha)
            ctx.logical_denominator_rows()
            ctx.logical_total_vectors()
        after = set(sys.modules)
        self.assertEqual(after - before, set())
        self.assertNotIn("v8_runtime", sys.modules)
        self.assertNotIn("v8_snapshot", sys.modules)

class AmbientPoisonTests(unittest.TestCase):
    def test_planted_sysmodules_cannot_substitute_code(self):
        import importlib.util
        adv = _SEC_DIR / "adversarial"

        def _load(path, name):
            spec = importlib.util.spec_from_file_location(name, str(path))
            assert spec is not None and spec.loader is not None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module

        runtime = _load(adv / "malicious_v8_runtime.py", "mal_int_runtime")
        snapshot = _load(adv / "malicious_v8_snapshot.py", "mal_int_snapshot")
        planted = {"v8_runtime": runtime, "v8_snapshot": snapshot}
        saved = {k: sys.modules.get(k) for k in planted}
        sys.modules.update(planted)
        try:
            with tempfile.TemporaryDirectory() as td:
                fx = e2e_fixtures.build_valid_set(Path(td), "v10-int-poi-01")
                with self.assertRaises(ValueError):
                    v10.preflight_longmemeval_v10(
                        fx.plan_path, "0" * 64, fx.fixture_path,
                        "0" * 64, fx.physical_path, "0" * 64)
                ctx = v10.preflight_longmemeval_v10(
                    fx.plan_path, fx.plan_sha, fx.fixture_path,
                    fx.fixture_sha, fx.physical_path, fx.physical_sha)
                self.assertEqual(ctx.logical_total_vectors(), 231606)
        finally:
            for key, old in saved.items():
                if old is None:
                    sys.modules.pop(key, None)
                else:
                    sys.modules[key] = old

    def test_ambient_hashlib_substitution_is_refused(self):
        real_sha256 = hashlib.sha256
        with tempfile.TemporaryDirectory() as td:
            fx = e2e_fixtures.build_valid_set(Path(td), "v10-int-hash-01")
            tampered = e2e_fixtures.rewrite_plan_with_new_run_id(
                fx, "v10-int-hash-ATTACKER")
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
                    v10.preflight_longmemeval_v10(
                        fx.plan_path, fx.plan_sha, fx.fixture_path,
                        fx.fixture_sha, fx.physical_path, fx.physical_sha)
            finally:
                hashlib.sha256 = real_sha256


class DenominatorLogicTests(unittest.TestCase):
    def test_inconsistent_duplicates_reject_end_to_end(self):
        with tempfile.TemporaryDirectory() as td:
            fx = _duplicate_copy_set(Path(td), "v10-int-inc-01")
            plan = json.loads(fx.plan_path.read_bytes().decode("utf-8"))
            plan["physical_copies"][-1]["population_ids"] = ["pop-0-a"]
            raw = json.dumps(plan, sort_keys=True).encode("utf-8")
            fx.plan_path.write_bytes(raw)
            fx.plan_sha = hashlib.sha256(raw).hexdigest()
            with self.assertRaises(ValueError):
                v10.preflight_longmemeval_v10(
                    fx.plan_path, fx.plan_sha, fx.fixture_path,
                    fx.fixture_sha, fx.physical_path, fx.physical_sha)

    def test_pure_math_matches_candidate_module(self):
        import denominator_integrity_v10 as cand
        denominators = (("ca1", "pa1", 10), ("ca2", "pa1b", 10),
                        ("cb", "pb", 20))
        cmap, frozen = {"ca1": "a", "ca2": "a", "cb": "b"}, {"a": 10, "b": 20}
        mine = v10.enrich_denominator_rows(denominators, cmap, frozen)
        theirs = cand.enrich_denominator_rows(denominators, cmap, frozen)
        self.assertEqual(tuple(mine), tuple(theirs))
        self.assertEqual(v10.deduplicate_logical_total(mine),
                         cand.deduplicate_logical_total(theirs))
        self.assertEqual(v10.naive_copy_total(denominators),
                         cand.naive_copy_total(denominators))
        self.assertEqual(v10.ACCOUNTING_RULE, cand.ACCOUNTING_RULE)
        self.assertEqual(v10.REPORT_LABELS, cand.REPORT_LABELS)

    def test_no_byte_total_helpers(self):
        for name in ("total_bytes", "byte_total", "deduplicate_bytes",
                     "logical_byte_total", "bytes_per_vector"):
            self.assertFalse(hasattr(v10, name), name)

    def test_public_signature_and_labels(self):
        self.assertEqual(
            tuple(inspect.signature(v10.preflight_longmemeval_v10).parameters),
            ("plan_path", "expected_plan_sha256",
             "fixture_bindings_path", "expected_fixture_bindings_sha256",
             "physical_bindings_path", "expected_physical_bindings_sha256"))
        self.assertEqual(v10.REPORT_LABELS, LABELS)
        self.assertIn("unique-by-archive", v10.ACCOUNTING_RULE)


class ConcurrencySmokeTests(unittest.TestCase):
    def test_two_threads_share_no_state(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fx = e2e_fixtures.build_valid_set(root / "s", "v10-int-thr-00")
            oracle = v10.preflight_longmemeval_v10(
                fx.plan_path, fx.plan_sha, fx.fixture_path,
                fx.fixture_sha, fx.physical_path, fx.physical_sha)
            expect = oracle.logical_total_vectors()
            barrier = threading.Barrier(2)
            outcomes = {}

            def worker(tag):
                try:
                    barrier.wait(timeout=60)
                    wfx = e2e_fixtures.build_valid_set(root / tag, tag)
                    wctx = v10.preflight_longmemeval_v10(
                        wfx.plan_path, wfx.plan_sha, wfx.fixture_path,
                        wfx.fixture_sha, wfx.physical_path, wfx.physical_sha)
                    outcomes[tag] = wctx.logical_total_vectors() == expect
                except Exception as exc:  # noqa: BLE001
                    outcomes[tag] = "%s: %s" % (exc.__class__.__name__, exc)

            threads = [threading.Thread(target=worker, args=(t,))
                       for t in ("v10-int-thr-a", "v10-int-thr-b")]
            for th in threads:
                th.start()
            for th in threads:
                th.join(timeout=180)
            self.assertEqual(outcomes,
                             {"v10-int-thr-a": True, "v10-int-thr-b": True})


if __name__ == "__main__":
    unittest.main()
