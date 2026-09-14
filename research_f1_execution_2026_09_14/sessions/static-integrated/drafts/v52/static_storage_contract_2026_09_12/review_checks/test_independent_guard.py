"""Independent synthetic contract checks. No production data or worker fixture imports.

Run with the authorized interpreter and -B. Runtime files stay in review_checks.
The guard is loaded from one byte snapshot; its digest is printed for attribution.
Assertions describe required behavior, so unfinished implementations can fail.
"""

import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest


ROOT = Path(__file__).resolve().parent
NAMESPACE = ROOT.parent
GUARD_PATH = NAMESPACE / "measurement_plan_guard.py"
GUARD_BYTES = GUARD_PATH.read_bytes()
GUARD_SHA256 = hashlib.sha256(GUARD_BYTES).hexdigest()
guard = types.ModuleType("independent_review_guard_snapshot")
guard.__file__ = str(GUARD_PATH)
sys.modules[guard.__name__] = guard
exec(compile(GUARD_BYTES, str(GUARD_PATH), "exec"), guard.__dict__)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def independent_plan(contract):
    """Fictitious two-archive declaration with distinguishable weighting results."""
    data = {
        "schema": "v52.static-storage-plan", "version": 1, "status": "READY",
        "contract_sha256": sha(contract), "run_id": "independent-synthetic-only",
        "analysis_mode": "PREDECLARED", "parent_plan_sha256": None,
        "weighting": {"primary": "archive_weighted_mean_i(C_i/N_i)",
                      "secondary": "vector_weighted_sum_i(C_i)/sum_i(N_i)"},
        "archives": [{"id": "review-small", "N_i": 1}, {"id": "review-large", "N_i": 9}],
        "formats": [{"id": "review-format", "serialization": "review-fixed-record-v1",
                     "dtype": "uint8", "representation": "SURROGATE"}],
        "configurations": [{"id": "review-config", "format_ids": ["review-format"],
                            "item_ids": ["stored-optional", "unused-scratch"]}],
        "items": [
            {"id": "stored-optional", "role": "actually serialized optional toy record",
             "disposition": "INCLUDED", "reason": "actual serialized bytes still count",
             "cost_scope": "PER_VECTOR", "source_identity": "review-synthetic-literal-v1",
             "exclusion_basis": None},
            {"id": "unused-scratch", "role": "not-required unsaved scratch",
             "disposition": "EXCLUDED", "reason": "declared functions preserved without scratch",
             "cost_scope": "SHARED", "source_identity": "review-synthetic-literal-v1",
             "exclusion_basis": "NOT_REQUIRED"}],
        "fixtures": [{"id": "review-fixture", "kind": "SYNTHETIC",
                      "sha256": sha(b"id-A:toy-A;id-B:toy-B"),
                      "generator_identity": "review-literal-seedless-v1"}],
        "operations": [{"id": "review-transform", "kind": "TRANSFORM",
                        "implementation_identity": "review-identity-transform-v1"},
                       {"id": "review-id-map", "kind": "ID_MAPPING",
                        "implementation_identity": "review-fixed-toy-map-v1"}],
        "probes": [], "populations": [], "physical_copies": [], "controls": [],
    }
    for archive in data["archives"]:
        aid = archive["id"]
        for n, q in [(0, 1), (2, 3)]:
            pid = f"{aid}-{n}-{q}"
            data["probes"].append({"id": pid, "archive_id": aid, "N": n, "q": q,
                                   "fixture_id": "review-fixture"})
            for phase, size in [("BEFORE", n), ("AFTER", n + q)]:
                data["populations"].append({"id": f"{pid}-{phase}", "archive_id": aid,
                    "probe_id": pid, "phase": phase, "count": size,
                    "member_ids_sha256": sha(json.dumps(list(range(size))).encode())})
        data["physical_copies"].append({"id": f"copy-{aid}", "item_id": "stored-optional",
            "archive_id": aid, "config_id": "review-config", "format_id": "review-format",
            "artifact_identity": f"review-toy-source-{aid}", "artifact_sha256": sha(b"toy-only"),
            "population_ids": [p["id"] for p in data["populations"] if p["archive_id"] == aid]})
    for op in data["operations"]:
        states = [("BASELINE", [], "BASELINE")]
        for action in ["REMOVE", "RESTORE", "CORRUPT"]:
            states.extend(("PER_ITEM", [i["id"]], action) for i in data["items"])
            states.append(("FALLBACK_COMBINED", [i["id"] for i in data["items"]], action))
        for scope, items, action in states:
            data["controls"].append({"id": f"review-control-{len(data['controls'])}",
                "config_id": "review-config", "operation_id": op["id"], "scope": scope,
                "item_ids": items, "action": action, "expected_outcome": "MATCH",
                "reference_identity": "review-fixed-expected-function-v1",
                "applicability": "APPLICABLE", "na_reason": None})
    return data


def declaration_echo(request):
    """Envelope fixture only. Does NOT execute necessity ablations or retrieval."""
    return {"request": copy.deepcopy(request), "items": [
        {"item_id": i["id"], "disposition": i["disposition"], "format_id": request["format"]["id"],
         "physical_copy_ids": [c["id"] for c in request["physical_copies"] if c["item_id"] == i["id"]],
         "bytes_before": request["probe"]["N"] * 7 if i["disposition"] == "INCLUDED" else None,
         "bytes_after": (request["probe"]["N"] + request["probe"]["q"]) * 7
                        if i["disposition"] == "INCLUDED" else None} for i in request["items"]],
        "controls": [{"control_id": c["id"], "outcome": c["expected_outcome"],
                      "reference_identity": c["reference_identity"]} for c in request["controls"]]}


class IndependentGuardChecks(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="synthetic-review-", dir=ROOT)
        self.addCleanup(temp.cleanup)
        self.plan_path = Path(temp.name) / "toy-plan.json"
        self.contract_path = Path(temp.name) / "toy-contract.txt"
        self.contract = b"Independent synthetic boundary contract; no scientific approval.\n"
        self.contract_path.write_bytes(self.contract)
        self.data = independent_plan(self.contract)
        self.write_plan()

    def write_plan(self):
        raw = json.dumps(self.data, indent=2).encode()
        self.plan_path.write_bytes(raw)
        self.expected_sha256 = sha(raw)

    def load(self):
        return guard.load_plan(self.plan_path, self.expected_sha256, self.contract_path)

    def probe(self, request, callback=declaration_echo):
        return guard.guarded_probe(self.plan_path, self.expected_sha256, self.contract_path, request, callback)

    def finish(self, rows):
        return guard.finalize(self.plan_path, self.expected_sha256, self.contract_path, rows)

    def costs(self):
        return [{"archive_id": "review-small", "N_i": 1, "C_i": 10},
                {"archive_id": "review-large", "N_i": 9, "C_i": 270}]

    def claim(self, **kwargs):
        return guard.make_claim(self.load(), "review-config", "review-format", 7, self.costs(), **kwargs)

    def add_unknown(self, scope):
        self.data["status"] = "SCOPED_PARTIAL"
        self.data["items"].append({"id": "review-unknown", "role": "unresolved synthetic component",
            "disposition": "UNKNOWN", "reason": "independent deliberate missingness",
            "cost_scope": scope, "source_identity": "UNKNOWN", "exclusion_basis": None})
        self.data["configurations"][0]["item_ids"].append("review-unknown")
        self.write_plan()

    def test_known_inventory_lower_bound_never_becomes_full_headline(self):
        result = self.claim(lower_bound_verified=True)
        self.assertEqual(result["effective_total_status"], "LOWER_BOUND", result)
        self.assertIsNone(result["headline_full_total"])
        self.assertIn("LOWER_BOUND", result["sentence"])
        self.assertEqual(result["margin_status"], "LOWER_BOUND")
        self.assertEqual(result["cap_verdict"], "UNKNOWN")

    def test_known_inventory_lower_bound_threshold_edges(self):
        for margin in [0, 12, 12.25]:
            with self.subTest(margin=margin):
                result = guard.make_claim(self.load(), "review-config", "review-format", margin,
                                          self.costs(), lower_bound_verified=True)
                self.assertEqual(result["effective_total_status"], "LOWER_BOUND")
                self.assertIsNone(result["headline_full_total"])
                self.assertEqual(result["cap_verdict"], "EXCEEDS_12" if margin > 12 else "UNKNOWN")

    def test_corrupt_NA_requires_reason_and_is_not_unknown(self):
        c = next(c for c in self.data["controls"] if c["action"] == "CORRUPT")
        c.update(applicability="NA", expected_outcome="NA", na_reason="toy variant has no mutable state")
        self.write_plan()
        result = self.finish([self.probe(r) for r in guard.expected_requests(self.load())])
        self.assertEqual(result["status"], "COMPLETE")
        self.assertEqual(result["unknown_control_ids"], [])
        for reason in [None, "", "  ", "UNKNOWN"]:
            c["na_reason"] = reason
            self.write_plan()
            with self.subTest(reason=reason), self.assertRaises(guard.PlanValidationError):
                self.load()

    def test_external_dependency_loss_is_not_not_required(self):
        self.data["items"][1].update(exclusion_basis="EXTERNAL_BOUNDARY",
                                     reason="toy external dependency outside package")
        c = next(c for c in self.data["controls"] if c["action"] == "REMOVE"
                 and c["item_ids"] == ["unused-scratch"])
        c["expected_outcome"] = "FAILURE"
        self.write_plan()
        self.load()
        self.data["items"][1]["exclusion_basis"] = "NOT_REQUIRED"
        self.write_plan()
        with self.assertRaises(guard.PlanValidationError):
            self.load()

    def test_exploratory_rows_cannot_complete_original_plan(self):
        original_data = copy.deepcopy(self.data)
        original_hash = self.expected_sha256
        self.data.update(analysis_mode="EXPLORATORY", parent_plan_sha256=original_hash,
                         run_id="independent-separate-exploratory")
        self.write_plan()
        rows = [self.probe(r) for r in guard.expected_requests(self.load())]
        result = self.claim()
        self.assertEqual(result["analysis_mode"], "EXPLORATORY")
        self.assertIn(original_hash, result["sentence"])
        self.data = original_data
        self.write_plan()
        self.assertEqual(self.expected_sha256, original_hash)
        with self.assertRaises(guard.PlanValidationError):
            self.finish(rows)

    def test_ready_baseline_failure_rejected(self):
        next(c for c in self.data["controls"] if c["scope"] == "BASELINE")["expected_outcome"] = "FAILURE"
        self.write_plan()
        with self.assertRaises(guard.PlanValidationError):
            self.load()

    def test_ready_restore_failure_rejected(self):
        next(c for c in self.data["controls"] if c["action"] == "RESTORE")["expected_outcome"] = "FAILURE"
        self.write_plan()
        with self.assertRaises(guard.PlanValidationError):
            self.load()

    def test_not_required_removal_function_loss_rejected(self):
        next(c for c in self.data["controls"] if c["action"] == "REMOVE"
             and c["item_ids"] == ["unused-scratch"])["expected_outcome"] = "DIFFERENT"
        self.write_plan()
        with self.assertRaises(guard.PlanValidationError):
            self.load()

    def test_control_missing_rejected(self):
        self.data["controls"].pop()
        self.write_plan()
        with self.assertRaises(guard.PlanValidationError):
            self.load()

    def test_complete_panel_and_optional_serialized_bytes(self):
        rows = [self.probe(r) for r in guard.expected_requests(self.load())]
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]["items"][0]["bytes_after"], 7)
        self.assertEqual(self.finish(rows)["status"], "COMPLETE")
        for bad in [rows[:-1], rows + [rows[0]], [rows[0]] * 4, list(reversed(rows))]:
            with self.subTest(size=len(bad)), self.assertRaises(guard.PlanValidationError):
                self.finish(bad)

    def test_plan_and_contract_hashes_checked_before_callback(self):
        request = guard.expected_requests(self.load())[0]
        for path in [self.plan_path, self.contract_path]:
            with self.subTest(path=path.name):
                original = path.read_bytes()
                path.write_bytes(original + b" ")
                calls = []
                with self.assertRaises(guard.PlanValidationError):
                    self.probe(request, lambda r: calls.append(r))
                self.assertEqual(calls, [])
                path.write_bytes(original)

    def test_frozen_request_change_prevents_callback(self):
        request = guard.expected_requests(self.load())[0]
        request["probe"]["q"] = 77
        calls = []
        with self.assertRaises(guard.PlanValidationError):
            self.probe(request, lambda r: calls.append(r))
        self.assertEqual(calls, [])

    def test_fixed_weighting_and_full_population(self):
        result = self.claim()
        self.assertEqual(result["effective_primary"], 20)
        self.assertEqual(result["effective_secondary"], 28)
        with self.assertRaises(guard.PlanValidationError):
            guard.make_claim(self.load(), "review-config", "review-format", 7, self.costs()[:1])

    def test_per_vector_unknown_blocks_cap(self):
        self.add_unknown("PER_VECTOR")
        result = self.claim()
        self.assertEqual(result["cap_verdict"], "UNKNOWN")
        self.assertEqual(result["effective_total_status"], "UNKNOWN")
        self.assertIsNone(result["headline_full_total"])
        self.assertIn("review-unknown", result["sentence"])

    def test_shared_unknown_preserves_only_scoped_claim(self):
        self.add_unknown("SHARED")
        result = self.claim()
        self.assertEqual(result["status"], "PARTIAL")
        self.assertEqual(result["effective_total_status"], "UNKNOWN")
        self.assertIsNone(result["headline_full_total"])
        self.assertIn("review-unknown", result["sentence"])

    def test_unready_template_rejected_before_callback(self):
        template = NAMESPACE / "MEASUREMENT_PLAN.template.json"
        calls = []
        with self.assertRaises(guard.PlanValidationError):
            guard.guarded_probe(template, sha(template.read_bytes()), self.contract_path, {},
                                lambda r: calls.append(r))
        self.assertEqual(calls, [])


if __name__ == "__main__":
    print("INDEPENDENT SYNTHETIC REVIEW; guard snapshot SHA256=" + GUARD_SHA256, flush=True)
    unittest.main(verbosity=2)
