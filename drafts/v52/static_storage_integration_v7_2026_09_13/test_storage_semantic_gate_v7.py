import inspect
import unittest
from pathlib import Path

import storage_semantic_gate_v7 as v7


def tiny_anchor():
    return v7.LongMemEvalAnchor(
        "0" * 64,
        "synthetic-test-anchor",
        (("a", 10), ("b", 20)),
    )


def base_plan():
    return {
        "archives": [{"id": "a", "N_i": 10}, {"id": "b", "N_i": 20}],
        "probes": [
            {"id": "a_q1", "archive_id": "a", "N": 10, "q": 1},
            {"id": "a_q8", "archive_id": "a", "N": 10, "q": 8},
            {"id": "a_diag", "archive_id": "a", "N": 32, "q": 1},
            {"id": "b_q1", "archive_id": "b", "N": 20, "q": 1},
        ],
        "populations": [
            {"id": "pa1b", "archive_id": "a", "probe_id": "a_q1", "phase": "BEFORE", "count": 10},
            {"id": "pa1a", "archive_id": "a", "probe_id": "a_q1", "phase": "AFTER", "count": 11},
            {"id": "pa8b", "archive_id": "a", "probe_id": "a_q8", "phase": "BEFORE", "count": 10},
            {"id": "pa8a", "archive_id": "a", "probe_id": "a_q8", "phase": "AFTER", "count": 18},
            {"id": "padb", "archive_id": "a", "probe_id": "a_diag", "phase": "BEFORE", "count": 32},
            {"id": "pada", "archive_id": "a", "probe_id": "a_diag", "phase": "AFTER", "count": 33},
            {"id": "pb1b", "archive_id": "b", "probe_id": "b_q1", "phase": "BEFORE", "count": 20},
            {"id": "pb1a", "archive_id": "b", "probe_id": "b_q1", "phase": "AFTER", "count": 21},
        ],
        "physical_copies": [
            {"id": "ca", "archive_id": "a", "population_ids": ["pa1b", "pa1a", "pa8b", "pa8a", "padb", "pada"]},
            {"id": "cb", "archive_id": "b", "population_ids": ["pb1b", "pb1a"]},
        ],
    }


class V7SemanticTests(unittest.TestCase):
    def test_q8_at_Ni_is_not_authoritative(self):
        proof = v7._verify_plan_data_against_anchor(base_plan(), tiny_anchor())
        self.assertEqual(
            dict(proof.authoritative_probe_ids),
            {"a": "a_q1", "b": "b_q1"},
        )
        self.assertEqual(
            proof.denominator_map(),
            {"ca": ("pa1b", 10), "cb": ("pb1b", 20)},
        )

    def test_inflated_population_count_is_rejected(self):
        plan = base_plan()
        next(p for p in plan["populations"] if p["id"] == "pa1b")["count"] = 10**9
        with self.assertRaises(v7.V7ValidationError):
            v7._verify_plan_data_against_anchor(plan, tiny_anchor())

    def test_wrong_declared_Ni_is_rejected(self):
        plan = base_plan()
        plan["archives"][0]["N_i"] = 999
        with self.assertRaises(v7.V7ValidationError):
            v7._verify_plan_data_against_anchor(plan, tiny_anchor())

    def test_missing_authoritative_q1_is_rejected(self):
        plan = base_plan()
        plan["probes"] = [p for p in plan["probes"] if p["id"] != "a_q1"]
        with self.assertRaises(v7.V7ValidationError):
            v7._verify_plan_data_against_anchor(plan, tiny_anchor())

    def test_subset_archive_roster_is_rejected(self):
        plan = base_plan()
        plan["archives"] = [plan["archives"][0]]
        with self.assertRaises(v7.V7ValidationError):
            v7._verify_plan_data_against_anchor(plan, tiny_anchor())

    def test_public_entrypoint_has_no_anchor_or_guarded_digest_knobs(self):
        names = tuple(inspect.signature(v7.preflight_longmemeval_v7).parameters)
        self.assertEqual(
            names,
            (
                "plan_path",
                "expected_plan_sha256",
                "fixture_bindings_path",
                "expected_fixture_bindings_sha256",
                "physical_bindings_path",
                "expected_physical_bindings_sha256",
            ),
        )
        self.assertEqual(tuple(inspect.signature(v7.load_longmemeval_anchor).parameters), ())


@unittest.skipUnless(v7._LONGMEMEVAL_ANCHOR_PATH.exists(), "canonical repo checkout unavailable")
class V7CanonicalRepoTests(unittest.TestCase):
    def test_canonical_anchor_and_pinned_dependencies_load(self):
        anchor = v7.load_longmemeval_anchor()
        self.assertEqual(len(anchor.sizes), 470)
        self.assertEqual(anchor.sha256, v7.LONGMEMEVAL_ANCHOR_SHA256)
        guard, v6 = v7._load_dependencies()
        self.assertTrue(hasattr(guard, "load_plan"))
        self.assertTrue(hasattr(guard, "Plan"))
        self.assertTrue(hasattr(v6, "preflight"))

    def test_anchor_mutation_is_rejected_without_caller_digest_override(self):
        raw = v7._LONGMEMEVAL_ANCHOR_PATH.read_bytes()
        mutated = raw + b"\n"
        with self.assertRaises(v7.V7ValidationError):
            v7._parse_longmemeval_anchor(mutated)


if __name__ == "__main__":
    unittest.main()
