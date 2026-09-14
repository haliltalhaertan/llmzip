"""Tests for the archive-anchor guard.

The central case is the exploit the independent audit demonstrated: a plan whose
declared archive sizes are inflated passes the structural guard and deflates the
published headline. It must now be refused.

Synthetic data plus one committed metric table's archive-cardinality column. No corpus,
query, gold, outcome, model fit, seal or run.
"""
import hashlib, subprocess, unittest
from archive_anchor_guard import (AnchorValidationError, load_anchor, verify_archive_sizes,
                                  classify_probes, verify_full_size_coverage,
                                  authoritative_denominators, verify_plan_against_anchor)

ANCHOR_CSV = b"question_id,N_archive\na1,10\na2,20\n"
ANCHOR_SHA = hashlib.sha256(ANCHOR_CSV).hexdigest()


def anchor():
    return load_anchor(ANCHOR_CSV, ANCHOR_SHA, "toy-anchor.csv", "question_id", "N_archive")


def plan(n1=10, n2=20, probes=None, populations=None, copies=None):
    probes = probes if probes is not None else [
        {"id": "pr1", "archive_id": "a1", "N": n1, "q": 1, "fixture_id": "fx1"},
        {"id": "pr2", "archive_id": "a2", "N": n2, "q": 1, "fixture_id": "fx1"}]
    populations = populations if populations is not None else [
        {"id": "po1b", "archive_id": "a1", "probe_id": "pr1", "phase": "BEFORE", "count": n1},
        {"id": "po1a", "archive_id": "a1", "probe_id": "pr1", "phase": "AFTER", "count": n1 + 1},
        {"id": "po2b", "archive_id": "a2", "probe_id": "pr2", "phase": "BEFORE", "count": n2},
        {"id": "po2a", "archive_id": "a2", "probe_id": "pr2", "phase": "AFTER", "count": n2 + 1}]
    copies = copies if copies is not None else [
        {"id": "pc1", "population_ids": ["po1b", "po1a"]},
        {"id": "pc2", "population_ids": ["po2b", "po2a"]}]
    return {"archives": [{"id": "a1", "N_i": n1}, {"id": "a2", "N_i": n2}],
            "probes": probes, "populations": populations, "physical_copies": copies}


class AnchorTests(unittest.TestCase):

    # --- the anchor source itself -------------------------------------------------
    def test_anchor_loads_and_reads(self):
        a = anchor()
        self.assertEqual(a.as_map(), {"a1": 10, "a2": 20})
        self.assertTrue(a.reverify(ANCHOR_CSV))

    def test_anchor_digest_mismatch_refused(self):
        with self.assertRaises(AnchorValidationError) as cm:
            load_anchor(ANCHOR_CSV, "0" * 64, "toy", "question_id", "N_archive")
        self.assertIn("SHA256 mismatch", str(cm.exception))

    def test_anchor_reverify_catches_a_swap(self):
        a = anchor()
        with self.assertRaises(AnchorValidationError):
            a.reverify(b"question_id,N_archive\na1,999999\n")

    def test_anchor_rejects_duplicate_archive_id(self):
        raw = b"question_id,N_archive\na1,10\na1,20\n"
        with self.assertRaises(AnchorValidationError) as cm:
            load_anchor(raw, hashlib.sha256(raw).hexdigest(), "toy", "question_id", "N_archive")
        self.assertIn("duplicate archive id", str(cm.exception))

    def test_anchor_rejects_non_integer_and_zero_and_negative(self):
        for body in (b"a1,ten\n", b"a1,1.0\n", b"a1,0\n", b"a1,-3\n", b"a1, \n"):
            raw = b"question_id,N_archive\n" + body
            with self.assertRaises(AnchorValidationError):
                load_anchor(raw, hashlib.sha256(raw).hexdigest(), "toy", "question_id", "N_archive")

    def test_anchor_rejects_missing_column_and_empty_table(self):
        for raw in (b"qid,N\na1,10\n", b"question_id,N_archive\n"):
            with self.assertRaises(AnchorValidationError):
                load_anchor(raw, hashlib.sha256(raw).hexdigest(), "toy", "question_id", "N_archive")

    # --- AUD-001: the exploit ------------------------------------------------------
    def test_honest_plan_passes(self):
        ids, roles, full, dens = verify_plan_against_anchor(plan(), anchor())
        self.assertEqual(ids, ("a1", "a2"))
        self.assertEqual(roles, {"pr1": "FULL_SIZE", "pr2": "FULL_SIZE"})
        self.assertEqual(full, {"a1": "pr1", "a2": "pr2"})
        self.assertEqual(dens, {"pc1": ("po1b", 10), "pc2": ("po2b", 20)})

    def test_inflated_N_i_is_refused(self):
        """The audit's exploit: raise N_i and the headline mean_i(C_i/N_i) collapses."""
        with self.assertRaises(AnchorValidationError) as cm:
            verify_archive_sizes(plan(n1=10**9), anchor())
        self.assertIn("disagrees with the frozen anchor", str(cm.exception))

    def test_deflated_N_i_is_refused_too(self):
        with self.assertRaises(AnchorValidationError):
            verify_archive_sizes(plan(n1=1), anchor())

    def test_unanchored_archive_is_refused(self):
        p = plan()
        p["archives"].append({"id": "ghost", "N_i": 10**9})
        with self.assertRaises(AnchorValidationError) as cm:
            verify_archive_sizes(p, anchor())
        self.assertIn("not present in the frozen anchor", str(cm.exception))

    def test_N_i_of_wrong_type_is_refused(self):
        for bad in (True, 10.0, "10", None):
            p = plan()
            p["archives"][0]["N_i"] = bad
            with self.assertRaises(AnchorValidationError):
                verify_archive_sizes(p, anchor())

    # --- AUD-001 second path: probe N no longer free ------------------------------
    def test_probe_at_a_size_that_is_not_the_archive_is_diagnostic(self):
        p = plan()
        p["probes"].append({"id": "pr_stair", "archive_id": "a1", "N": 1024, "q": 1, "fixture_id": "fx1"})
        roles = classify_probes(p)
        self.assertEqual(roles["pr_stair"], "DIAGNOSTIC")
        self.assertEqual(roles["pr1"], "FULL_SIZE")

    def test_archive_without_a_full_size_probe_is_refused(self):
        p = plan()
        p["probes"][0]["N"] = 1024          # a1 now has only a staircase point
        roles = classify_probes(p)
        with self.assertRaises(AnchorValidationError) as cm:
            verify_full_size_coverage(p, roles)
        self.assertIn("exactly one full-size probe", str(cm.exception))

    def test_two_full_size_probes_for_one_archive_are_refused(self):
        p = plan()
        p["probes"].append({"id": "pr1b", "archive_id": "a1", "N": 10, "q": 8, "fixture_id": "fx1"})
        roles = classify_probes(p)
        with self.assertRaises(AnchorValidationError):
            verify_full_size_coverage(p, roles)

    # --- AUD-008: one denominator, not a menu -------------------------------------
    def test_diagnostic_population_cannot_become_a_denominator(self):
        """The audit's menu case: a copy bound to a 10^9 staircase population."""
        p = plan()
        p["probes"].append({"id": "prX", "archive_id": "a1", "N": 10**9, "q": 1, "fixture_id": "fx1"})
        p["populations"].append({"id": "poX", "archive_id": "a1", "probe_id": "prX",
                                 "phase": "BEFORE", "count": 10**9})
        p["physical_copies"][0]["population_ids"].append("poX")
        roles = classify_probes(p)
        self.assertEqual(roles["prX"], "DIAGNOSTIC")
        dens = authoritative_denominators(p, roles)
        self.assertEqual(dens["pc1"], ("po1b", 10))      # the 10^9 candidate is not eligible

    def test_copy_with_no_full_size_before_population_is_refused(self):
        p = plan()
        p["physical_copies"][0]["population_ids"] = ["po1a"]      # AFTER only
        roles = classify_probes(p)
        with self.assertRaises(AnchorValidationError) as cm:
            authoritative_denominators(p, roles)
        self.assertIn("exactly one full-size BEFORE population", str(cm.exception))

    def test_copy_with_two_full_size_before_populations_is_refused(self):
        p = plan()
        p["populations"].append({"id": "po1b2", "archive_id": "a1", "probe_id": "pr1",
                                 "phase": "BEFORE", "count": 10})
        p["physical_copies"][0]["population_ids"].append("po1b2")
        roles = classify_probes(p)
        with self.assertRaises(AnchorValidationError):
            authoritative_denominators(p, roles)

    def test_zero_denominator_is_refused(self):
        p = plan()
        p["populations"][0]["count"] = 0
        roles = classify_probes(p)
        with self.assertRaises(AnchorValidationError) as cm:
            authoritative_denominators(p, roles)
        self.assertIn("positive integer", str(cm.exception))

    def test_unknown_population_reference_is_refused(self):
        p = plan()
        p["physical_copies"][0]["population_ids"].append("nope")
        roles = classify_probes(p)
        with self.assertRaises(AnchorValidationError):
            authoritative_denominators(p, roles)

    # --- malformed input must be an AnchorValidationError, never something else ----
    def test_malformed_plans_raise_only_anchor_errors(self):
        bad = [{}, {"archives": []}, {"archives": [{"id": "a1"}]},
               {"archives": [{"id": "a1", "N_i": 10}], "probes": []},
               {"archives": [{"id": "a1", "N_i": 10}], "probes": [{"id": "p"}]}]
        for p in bad:
            with self.assertRaises(AnchorValidationError):
                try:
                    verify_plan_against_anchor(p, anchor())
                except AnchorValidationError:
                    raise
                except Exception as e:          # noqa: BLE001 - the point of the test
                    self.fail(f"non-anchor exception {type(e).__name__} for {p}")

    # --- the real frozen table ------------------------------------------------------
    def test_real_committed_anchor_table_loads(self):
        """The committed metric table, read by digest. Archive cardinality only."""
        raw = subprocess.run(
            ["git", "-C", "/home/user/llmzip", "show",
             "origin/main:docs/v52/task4c2/V52_T4C2_feature_geometry.csv"],
            capture_output=True, check=True).stdout
        a = load_anchor(raw, hashlib.sha256(raw).hexdigest(),
                        "docs/v52/task4c2/V52_T4C2_feature_geometry.csv",
                        "question_id", "N_archive")
        sizes = a.as_map()
        self.assertEqual(len(sizes), 470)
        self.assertTrue(all(isinstance(v, int) and v >= 1 for v in sizes.values()))
        # a plan declaring the true size for one real archive passes; inflating it fails
        aid, n = a.sizes[0]
        self.assertTrue(verify_archive_sizes({"archives": [{"id": aid, "N_i": n}]}, a))
        with self.assertRaises(AnchorValidationError):
            verify_archive_sizes({"archives": [{"id": aid, "N_i": n * 1000}]}, a)


if __name__ == "__main__":
    unittest.main()
