"""V10 denominator-integrity tests: duplicate-copy regression + adversarial coverage.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Scope: LongMemEval-only preparation checks. No storage measurement, no model
fit, no retrieval, no Task4F1 outcome access, no run authorization.

The V10 implementation under test lives in this same additive directory as
``denominator_integrity_v10.py`` and is imported lazily so the pre-fix failure
mode (missing/unsigned repair layer) is an ordinary test failure, not a
collection error: the V9 defect-demonstration test below still runs.
"""
import inspect
import sys
import unittest
from pathlib import Path

_V10_DIR = Path(__file__).resolve().parent
_V9_DIR = _V10_DIR.parent / "static_storage_integration_v9_2026_09_13"
sys.path.insert(0, str(_V9_DIR))

import consumption_gate_v9 as v9  # noqa: E402

LABELS = ("[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] "
          "[NOT FOR CITATION] [DISCLOSE-BEFORE-USE]")


def _v10():
    import denominator_integrity_v10 as v10
    return v10


def _repo_root():
    here = Path(__file__).resolve()
    for candidate in (here.parent, *here.parents):
        if (candidate / "drafts/v52/static_storage_contract_2026_09_12").is_dir():
            return candidate
    return None


def _anchor_csv():
    root = _repo_root()
    return None if root is None else root / "docs/v52/task4c2/V52_T4C2_feature_geometry.csv"


class V9DefectDemonstration(unittest.TestCase):
    """Regression demonstration through the V9 PUBLIC consumption surface.

    Two legitimate physical copies of one archive each carry the same frozen
    N_i through ``V9Context.authoritative_denominators()``. The returned rows
    carry no archive identity, so a consumer summing the d column counts one
    logical archive twice.
    """

    def test_naive_sum_over_v9_public_rows_double_counts_duplicate_copies(self):
        class _Proof:
            denominators = (("ca1", "pa1", 10), ("ca2", "pa1b", 10))

        class _Snap:
            semantic_proof = _Proof()

        old = v9._fresh_v8
        v9._fresh_v8 = lambda *args: _Snap()  # noqa: E731
        try:
            rows = v9.V9Context(
                "p", "1" * 64, "f", "2" * 64, "b", "3" * 64
            ).authoritative_denominators()
        finally:
            v9._fresh_v8 = old
        self.assertEqual(tuple(rows), (("ca1", "pa1", 10), ("ca2", "pa1b", 10)))
        for row in rows:
            self.assertEqual(len(row), 3)
            self.assertNotIn("a", tuple(row[:2]))
        naive = sum(d for _, _, d in rows)
        self.assertEqual(naive, 20)
        # Byte-numerator consequence for one representation billed per vector:
        # 120 bytes over the naive denominator appears as 6 B/vector, while
        # the single logical archive (N=10) truly costs 12 B/vector.
        self.assertEqual(120 / naive, 6)
        self.assertEqual(120 / 10, 12)


class DuplicateCopyRegression(unittest.TestCase):
    """Two physical copies of one archive must yield one logical N_i."""

    def test_two_copies_one_archive_dedup_to_single_N(self):
        v10 = _v10()
        denominators = (("ca1", "pa1", 10), ("ca2", "pa1b", 10))
        rows = v10.enrich_denominator_rows(
            denominators, {"ca1": "a", "ca2": "a"}, {"a": 10})
        self.assertEqual(rows, (
            v10.LogicalDenominatorRow("a", "ca1", "pa1", 10),
            v10.LogicalDenominatorRow("a", "ca2", "pa1b", 10),
        ))
        for row in rows:
            self.assertEqual(row.archive_id, "a")
        self.assertEqual(v10.naive_copy_total(denominators), 20)
        self.assertEqual(v10.deduplicate_logical_total(rows), 10)


class InconsistentDuplicateTests(unittest.TestCase):
    def test_conflicting_duplicate_counts_reject(self):
        v10 = _v10()
        with self.assertRaises(v10.V10ValidationError):
            v10.enrich_denominator_rows(
                (("ca1", "pa1", 10), ("ca2", "pa1b", 999)),
                {"ca1": "a", "ca2": "a"}, {"a": 10})

    def test_agreeing_duplicates_against_wrong_frozen_N_reject(self):
        v10 = _v10()
        with self.assertRaises(v10.V10ValidationError):
            v10.enrich_denominator_rows(
                (("ca1", "pa1", 11), ("ca2", "pa1b", 11)),
                {"ca1": "a", "ca2": "a"}, {"a": 10})

    def test_enriched_rows_with_conflicting_N_per_archive_reject(self):
        v10 = _v10()
        rows = (v10.LogicalDenominatorRow("a", "ca1", "pa1", 10),
                v10.LogicalDenominatorRow("a", "ca2", "pa1b", 999))
        with self.assertRaises(v10.V10ValidationError):
            v10.deduplicate_logical_total(rows)


class UnknownArchiveTests(unittest.TestCase):
    def test_copy_with_no_archive_binding_rejects(self):
        v10 = _v10()
        with self.assertRaises(v10.V10ValidationError):
            v10.enrich_denominator_rows(
                (("ghost", "p", 10),), {"ca1": "a"}, {"a": 10})

    def test_copy_bound_to_archive_outside_frozen_roster_rejects(self):
        v10 = _v10()
        with self.assertRaises(v10.V10ValidationError):
            v10.enrich_denominator_rows(
                (("ca1", "pa1", 10),), {"ca1": "zzz"}, {"a": 10})


class OrdinaryOneCopyTests(unittest.TestCase):
    def test_one_copy_per_archive_naive_equals_logical(self):
        v10 = _v10()
        denominators = (("ca", "pa", 10), ("cb", "pb", 20))
        rows = v10.enrich_denominator_rows(
            denominators, {"ca": "a", "cb": "b"}, {"a": 10, "b": 20})
        self.assertEqual(v10.naive_copy_total(denominators), 30)
        self.assertEqual(v10.deduplicate_logical_total(rows), 30)


@unittest.skipUnless(
    _anchor_csv() is not None and _anchor_csv().exists(),
    "canonical repo checkout unavailable")
class Canonical470Tests(unittest.TestCase):
    def test_doubled_copy_rows_still_yield_231606(self):
        v10 = _v10()
        frozen = v10.load_longmemeval_anchor_map()
        self.assertEqual(len(frozen), 470)
        self.assertEqual(sum(frozen.values()), 231606)
        denominators, copy_to_archive = [], {}
        for aid, n_i in frozen.items():
            for tag in ("x", "y"):
                cid = "copy-%s-%s" % (aid, tag)
                copy_to_archive[cid] = aid
                denominators.append((cid, "pop-%s" % aid, n_i))
        denominators = tuple(denominators)
        self.assertEqual(len(denominators), 940)
        rows = v10.enrich_denominator_rows(denominators, copy_to_archive, frozen)
        self.assertEqual(v10.naive_copy_total(denominators), 463212)
        self.assertEqual(v10.deduplicate_logical_total(rows), 231606)


class NumeratorBytesNotDedupedTests(unittest.TestCase):
    def test_no_byte_total_helper_and_rows_carry_no_numerator(self):
        v10 = _v10()
        for name in ("total_bytes", "byte_total", "deduplicate_bytes",
                     "logical_byte_total", "bytes_per_vector"):
            self.assertFalse(hasattr(v10, name), name)
        rows = v10.enrich_denominator_rows(
            (("ca1", "pa1", 10), ("ca2", "pa1b", 10)),
            {"ca1": "a", "ca2": "a"}, {"a": 10})
        for row in rows:
            self.assertEqual(row._fields,
                             ("archive_id", "physical_copy_id",
                              "population_id", "n_i"))


class LabelsAndScopeTests(unittest.TestCase):
    def test_report_labels_exact(self):
        v10 = _v10()
        self.assertEqual(v10.REPORT_LABELS, LABELS)

    def test_labeled_summary_carries_labels_and_scope(self):
        v10 = _v10()
        text = v10.labeled_summary(logical_total=10, naive_total=20,
                                   n_archives=1, n_copies=2)
        self.assertTrue(text.startswith(LABELS))
        self.assertIn("LongMemEval", text)
        self.assertIn("logical_total=10", text)
        self.assertIn("naive_copy_total=20", text)

    def test_accounting_rule_states_archive_uniqueness(self):
        v10 = _v10()
        rule = v10.ACCOUNTING_RULE
        self.assertIn("unique-by-archive", rule)
        self.assertIn("numerator", rule.lower())


class PublicSignatureTests(unittest.TestCase):
    def test_preflight_signature_mirrors_v9(self):
        v10 = _v10()
        self.assertEqual(
            tuple(inspect.signature(v10.preflight_longmemeval_v10).parameters),
            ("plan_path", "expected_plan_sha256",
             "fixture_bindings_path", "expected_fixture_bindings_sha256",
             "physical_bindings_path", "expected_physical_bindings_sha256"))

    def test_anchor_loader_takes_no_caller_knobs(self):
        v10 = _v10()
        self.assertEqual(
            tuple(inspect.signature(v10.load_longmemeval_anchor_map).parameters),
            ())


class ContextPathTests(unittest.TestCase):
    """End-to-end through the public V10Context methods (seams stubbed)."""

    def _ctx(self, v10, denominators, copy_to_archive, frozen):
        class _Proof:
            pass
        _Proof.denominators = denominators

        class _Snap:
            semantic_proof = _Proof()

        ctx = v10.V10Context("p", "1" * 64, "f", "2" * 64, "b", "3" * 64)
        v10._fresh_snapshot_for = lambda _c: _Snap()  # noqa: SLF001
        v10._plan_maps_for = lambda _c: (copy_to_archive, frozen)  # noqa: SLF001
        return ctx

    def test_context_logical_total_dedups_while_naive_double_counts(self):
        v10 = _v10()
        old_fresh, old_maps = v10._fresh_snapshot_for, v10._plan_maps_for  # noqa: SLF001
        try:
            ctx = self._ctx(v10, (("ca1", "pa1", 10), ("ca2", "pa1b", 10)),
                            {"ca1": "a", "ca2": "a"}, {"a": 10})
            rows = ctx.logical_denominator_rows()
            self.assertTrue(all(r.archive_id == "a" for r in rows))
            self.assertEqual(ctx.naive_copy_total_vectors(), 20)
            self.assertEqual(ctx.logical_total_vectors(), 10)
        finally:
            v10._fresh_snapshot_for, v10._plan_maps_for = old_fresh, old_maps  # noqa: SLF001

    def test_context_inconsistent_duplicates_reject(self):
        v10 = _v10()
        old_fresh, old_maps = v10._fresh_snapshot_for, v10._plan_maps_for  # noqa: SLF001
        try:
            ctx = self._ctx(v10, (("ca1", "pa1", 10), ("ca2", "pa1b", 999)),
                            {"ca1": "a", "ca2": "a"}, {"a": 10})
            with self.assertRaises(v10.V10ValidationError):
                ctx.logical_denominator_rows()
        finally:
            v10._fresh_snapshot_for, v10._plan_maps_for = old_fresh, old_maps  # noqa: SLF001

    def test_context_exposes_no_snapshot_field(self):
        v10 = _v10()
        ctx = v10.V10Context("p", "1" * 64, "f", "2" * 64, "b", "3" * 64)
        self.assertFalse(hasattr(ctx, "initial_snapshot"))
        self.assertEqual(ctx._fields,
                         ("plan_path", "expected_plan_sha256",
                          "fixture_bindings_path",
                          "expected_fixture_bindings_sha256",
                          "physical_bindings_path",
                          "expected_physical_bindings_sha256"))


if __name__ == "__main__":
    unittest.main()
