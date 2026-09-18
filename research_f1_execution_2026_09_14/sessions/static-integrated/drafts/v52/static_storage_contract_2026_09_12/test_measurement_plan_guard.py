"""Temporary synthetic declarations only; never open a real archive/model."""

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import measurement_plan_guard as guard


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def toy_plan(contract_bytes):
    """These identities are fictitious and do not populate the shipped template."""
    data = {
        "schema": guard.SCHEMA, "version": 1, "status": "READY",
        "contract_sha256": digest(contract_bytes), "run_id": "toy-run-only",
        "analysis_mode": "PREDECLARED", "parent_plan_sha256": None,
        "weighting": {"primary": guard.PRIMARY, "secondary": guard.SECONDARY},
        "archives": [{"id": "toy-a", "N_i": 2}, {"id": "toy-b", "N_i": 8}],
        "formats": [{"id": "toy-u8", "serialization": "toy-raw-v1", "dtype": "uint8",
                     "representation": "SURROGATE"}],
        "configurations": [{"id": "toy-config", "format_ids": ["toy-u8"],
                            "item_ids": ["toy-codes", "toy-cache"]}],
        "probes": [], "populations": [], "physical_copies": [],
        "items": [
            {"id": "toy-codes", "role": "serialized code payload", "disposition": "INCLUDED",
             "reason": "physically stored even if a control can bypass it", "cost_scope": "PER_VECTOR",
             "source_identity": "toy-generator-v1", "exclusion_basis": None},
            {"id": "toy-cache", "role": "unsaved training scratch", "disposition": "EXCLUDED",
             "reason": "absent from the declared persistent package", "cost_scope": "SHARED",
             "source_identity": "toy-generator-v1", "exclusion_basis": "NOT_REQUIRED"}],
        "fixtures": [{"id": "toy-fixture", "kind": "SYNTHETIC",
                      "sha256": digest(b"fake-id-1:fake-payload-1"),
                      "generator_identity": "toy-literal-fixture-v1"}],
        "operations": [
            {"id": "toy-transform", "kind": "TRANSFORM", "implementation_identity": "toy-identity-v1"},
            {"id": "toy-map", "kind": "ID_MAPPING", "implementation_identity": "fake-preassigned-map-v1"}],
        "controls": [],
    }
    for archive in data["archives"]:
        for n, q in ((0, 1), (3, 2)):
            probe_id = f"{archive['id']}-n{n}-q{q}"
            data["probes"].append({"id": probe_id, "archive_id": archive["id"],
                                   "N": n, "q": q, "fixture_id": "toy-fixture"})
            for phase, count in (("BEFORE", n), ("AFTER", n + q)):
                data["populations"].append({
                    "id": f"{probe_id}-{phase}", "archive_id": archive["id"],
                    "probe_id": probe_id, "phase": phase, "count": count,
                    "member_ids_sha256": digest(json.dumps(list(range(count))).encode())})
        data["physical_copies"].append({
            "id": f"copy-{archive['id']}", "item_id": "toy-codes", "archive_id": archive["id"],
            "config_id": "toy-config", "format_id": "toy-u8",
            "artifact_identity": f"temp-toy-source-{archive['id']}", "artifact_sha256": digest(b"toy"),
            "population_ids": [p["id"] for p in data["populations"] if p["archive_id"] == archive["id"]]})
    for op in data["operations"]:
        states = [("BASELINE", [], "BASELINE")]
        for action in sorted(guard.ACTIONS):
            states.extend(("PER_ITEM", [i["id"]], action) for i in data["items"])
            states.append(("FALLBACK_COMBINED", [i["id"] for i in data["items"]], action))
        for scope, ids, action in states:
            data["controls"].append({
                "id": f"control-{len(data['controls'])}", "config_id": "toy-config",
                "operation_id": op["id"], "scope": scope, "item_ids": ids, "action": action,
                "expected_outcome": "MATCH", "reference_identity": "toy-reference-output-v1",
                "applicability": "APPLICABLE", "na_reason": None})
    return data


def toy_callback(request):
    """Echo dummy proves guard sequencing, NOT execution of ablation/projector."""
    return {
        "request": copy.deepcopy(request),
        "items": [{"item_id": i["id"], "disposition": i["disposition"],
                   "format_id": request["format"]["id"],
                   "physical_copy_ids": [c["id"] for c in request["physical_copies"] if c["item_id"] == i["id"]],
                   "bytes_before": request["probe"]["N"] * 8 if i["disposition"] == "INCLUDED" else None,
                   "bytes_after": (request["probe"]["N"] + request["probe"]["q"]) * 8
                                  if i["disposition"] == "INCLUDED" else None}
                  for i in request["items"]],
        "controls": [{"control_id": c["id"], "outcome": c["expected_outcome"],
                      "reference_identity": c["reference_identity"]} for c in request["controls"]],
    }


class PlanGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.plan_path = self.root / "toy-plan.json"
        self.contract_path = self.root / "toy-contract.txt"
        self.contract_bytes = b"Synthetic storage contract for guard tests only.\r\n"
        self.contract_path.write_bytes(self.contract_bytes)
        self.data = toy_plan(self.contract_bytes)
        self.write_plan()

    def write_plan(self):
        raw = json.dumps(self.data, indent=2).encode("utf-8")
        self.plan_path.write_bytes(raw)
        self.expected_hash = digest(raw)

    def load(self):
        return guard.load_plan(self.plan_path, self.expected_hash, self.contract_path)

    def run_probe(self, request, callback=toy_callback):
        return guard.guarded_probe(self.plan_path, self.expected_hash, self.contract_path, request, callback)

    def finish(self, observations):
        return guard.finalize(self.plan_path, self.expected_hash, self.contract_path, observations)

    def observations(self):
        return [self.run_probe(r) for r in guard.expected_requests(self.load())]

    def add_unknown(self, scope="SHARED"):
        self.data["status"] = "SCOPED_PARTIAL"
        self.data["items"].append({"id": "toy-unresolved", "role": "unavailable source",
                                   "disposition": "UNKNOWN", "reason": "source not available; never zero",
                                   "cost_scope": scope, "source_identity": "UNKNOWN", "exclusion_basis": None})
        self.data["configurations"][0]["item_ids"].append("toy-unresolved")
        self.write_plan()

    def costs(self):
        return [{"archive_id": "toy-a", "N_i": 2, "C_i": 20},
                {"archive_id": "toy-b", "N_i": 8, "C_i": 160}]

    def claim(self, **kwargs):
        return guard.make_claim(self.load(), "toy-config", "toy-u8", 8, self.costs(), **kwargs)

    def test_complete_ordered_panel_and_zero_N(self):
        requests = guard.expected_requests(self.load())
        self.assertEqual([r["probe"]["N"] for r in requests], [0, 3, 0, 3])
        self.assertEqual(len(requests), 4)
        result = self.finish(self.observations())
        self.assertEqual(result["status"], "COMPLETE")
        self.assertEqual(result["primary_weighting"], guard.PRIMARY)

    def test_hash_checked_before_contract_read_or_json_decode_or_callback(self):
        self.plan_path.write_bytes(b"not JSON")
        self.contract_path.unlink()
        callback = Mock()
        with patch.object(guard, "_decode", side_effect=AssertionError("must not parse")):
            with self.assertRaisesRegex(guard.PlanValidationError, "plan hash mismatch"):
                self.run_probe({}, callback)
        callback.assert_not_called()

    def test_raw_whitespace_and_line_endings_are_identity(self):
        request = guard.expected_requests(self.load())[0]
        for raw in (self.plan_path.read_bytes() + b"\n", self.plan_path.read_bytes().replace(b"\n", b"\r\n")):
            with self.subTest(raw_length=len(raw)):
                self.plan_path.write_bytes(raw)
                callback = Mock()
                with self.assertRaisesRegex(guard.PlanValidationError, "hash mismatch"):
                    self.run_probe(request, callback)
                callback.assert_not_called()

    def test_contract_revalidated_before_callback(self):
        request = guard.expected_requests(self.load())[0]
        self.contract_path.write_bytes(self.contract_bytes + b"changed")
        callback = Mock()
        with self.assertRaisesRegex(guard.PlanValidationError, "contract hash mismatch"):
            self.run_probe(request, callback)
        callback.assert_not_called()

    def test_changed_request_identity_never_calls_callback(self):
        original = guard.expected_requests(self.load())[0]
        changes = [("probe", "N", 99), ("probe", "q", 7), ("probe", "id", "extra-probe"),
                   ("archive", "id", "other-archive"), ("archive", "N_i", 493),
                   ("format", "dtype", "float64"), ("format", "serialization", "compressed"),
                   ("format", "representation", "REAL"), ("fixture", "sha256", "0" * 64)]
        for section, field, value in changes:
            with self.subTest(section=section, field=field):
                request = copy.deepcopy(original)
                request[section][field] = value
                callback = Mock()
                with self.assertRaises(guard.PlanValidationError):
                    self.run_probe(request, callback)
                callback.assert_not_called()
        for field, value in (("config_id", "other"), ("items", []), ("controls", []),
                             ("physical_copies", []), ("populations", []), ("operations", [])):
            request = copy.deepcopy(original)
            request[field] = value
            callback = Mock()
            with self.assertRaises(guard.PlanValidationError):
                self.run_probe(request, callback)
            callback.assert_not_called()

    def test_validly_rehashed_changed_plan_rejects_old_request(self):
        request = guard.expected_requests(self.load())[0]
        self.data["archives"][0]["N_i"] = 3
        self.write_plan()
        callback = Mock()
        with self.assertRaisesRegex(guard.PlanValidationError, "exact frozen"):
            self.run_probe(request, callback)
        callback.assert_not_called()

    def test_invalid_plan_shapes_and_semantics_fail_before_callback(self):
        original = copy.deepcopy(self.data)
        mutators = {
            "missing reason": lambda d: d["items"][0].pop("reason"),
            "blank reason": lambda d: d["items"][1].update(reason="  "),
            "bad disposition": lambda d: d["items"][0].update(disposition="OPTIONAL"),
            "zero Ni": lambda d: d["archives"][0].update(N_i=0),
            "bool Ni": lambda d: d["archives"][0].update(N_i=True),
            "negative N": lambda d: d["probes"][0].update(N=-1),
            "zero q": lambda d: d["probes"][0].update(q=0),
            "float q": lambda d: d["probes"][0].update(q=1.0),
            "duplicate archive": lambda d: d["archives"].append(copy.deepcopy(d["archives"][0])),
            "empty archives": lambda d: d.update(archives=[]),
            "unknown archive ref": lambda d: d["probes"][0].update(archive_id="missing"),
            "unknown format ref": lambda d: d["configurations"][0].update(format_ids=["missing"]),
            "unknown dtype": lambda d: d["formats"][0].update(dtype="UNKNOWN"),
            "wrong population": lambda d: d["populations"][0].update(count=493),
            "missing snapshot": lambda d: d["populations"].pop(),
            "missing physical copy": lambda d: d["physical_copies"].pop(),
            "duplicate physical identity": lambda d: d["physical_copies"][1].update(
                artifact_identity=d["physical_copies"][0]["artifact_identity"]),
            "missing control": lambda d: d["controls"].pop(),
            "duplicate control": lambda d: d["controls"].append(copy.deepcopy(d["controls"][0])),
            "real fixture": lambda d: d["fixtures"][0].update(kind="REAL_CORPUS"),
            "search operation": lambda d: d["operations"][1].update(kind="SEARCH_DISTANCE"),
            "invalid weight": lambda d: d["weighting"].update(primary=guard.SECONDARY),
            "bad schema": lambda d: d.update(schema="other"),
            "bad version": lambda d: d.update(version=True),
            "unknown field": lambda d: d.update(execute="do something"),
        }
        for name, mutate in mutators.items():
            with self.subTest(name=name):
                self.data = copy.deepcopy(original)
                mutate(self.data)
                self.write_plan()
                callback = Mock()
                with self.assertRaises(guard.PlanValidationError):
                    self.run_probe({}, callback)
                callback.assert_not_called()

    def test_plan_tampered_after_load_and_during_callback(self):
        request = guard.expected_requests(self.load())[0]
        raw = self.plan_path.read_bytes()
        self.plan_path.write_bytes(raw + b" ")
        callback = Mock()
        with self.assertRaises(guard.PlanValidationError):
            self.run_probe(request, callback)
        callback.assert_not_called()
        self.plan_path.write_bytes(raw)

        def replacing_callback(r):
            self.plan_path.write_bytes(raw + b" ")
            return toy_callback(r)

        with self.assertRaises(guard.PlanValidationError):
            self.run_probe(request, replacing_callback)

    def test_callback_mutation_cannot_change_expected_identity(self):
        request = guard.expected_requests(self.load())[0]

        def mutate(r):
            r["probe"]["q"] = 17
            return toy_callback(r)

        with self.assertRaisesRegex(guard.PlanValidationError, "observed identity"):
            self.run_probe(request, mutate)
        self.assertEqual(request["probe"]["q"], 1)

    def test_postflight_identity_item_control_and_byte_rejections(self):
        request = guard.expected_requests(self.load())[0]
        mutators = [lambda o: o["request"]["archive"].update(id="other"),
                    lambda o: o["request"]["probe"].update(q=3),
                    lambda o: o["request"]["format"].update(dtype="float64"),
                    lambda o: o["items"].pop(),
                    lambda o: o["items"].append(copy.deepcopy(o["items"][0])),
                    lambda o: o["items"].__setitem__(1, copy.deepcopy(o["items"][0])),
                    lambda o: o["items"][0].update(format_id="other"),
                    lambda o: o["items"][0].update(physical_copy_ids=[]),
                    lambda o: o["items"][0].update(bytes_before=-1),
                    lambda o: o["items"][0].update(bytes_before=True),
                    lambda o: o["items"][1].update(bytes_before=0),
                    lambda o: o["controls"].pop(),
                    lambda o: o["controls"][0].update(outcome="DIFFERENT"),
                    lambda o: o.update(exploratory_rows=[])]
        for i, mutate in enumerate(mutators):
            with self.subTest(mutation=i):
                def callback(r):
                    result = toy_callback(r)
                    mutate(result)
                    return result
                with self.assertRaises(guard.PlanValidationError):
                    self.run_probe(request, callback)

    def test_missing_duplicate_extra_and_reordered_coverage_never_complete(self):
        rows = self.observations()
        for invalid in ([], rows[:-1], rows + [rows[0]], [rows[0]] * len(rows),
                        [rows[1], rows[0], *rows[2:]]):
            with self.subTest(length=len(invalid)):
                with self.assertRaises(guard.PlanValidationError):
                    self.finish(invalid)

    def test_frozen_shared_equal_sizes_accepted_by_probe_and_finalize(self):
        self.data["items"][0].update(cost_scope="SHARED", role="frozen synthetic model state")
        self.write_plan()

        def callback(request):
            result = toy_callback(request)
            result["items"][0].update(bytes_before=32, bytes_after=32)
            return result

        rows = [self.run_probe(r, callback) for r in guard.expected_requests(self.load())]
        self.assertEqual(self.finish(rows)["status"], "COMPLETE")

    def test_frozen_shared_growth_and_shrink_rejected_by_probe_and_finalize(self):
        self.data["items"][0].update(cost_scope="SHARED", role="frozen synthetic model state")
        self.write_plan()
        requests = guard.expected_requests(self.load())
        for after in (33, 31):
            with self.subTest(bytes_after=after):
                rows = [toy_callback(r) for r in requests]
                for row in rows:
                    row["items"][0].update(bytes_before=32, bytes_after=32)
                rows[0]["items"][0]["bytes_after"] = after
                with self.assertRaisesRegex(guard.PlanValidationError, "frozen SHARED"):
                    self.run_probe(requests[0], lambda _: copy.deepcopy(rows[0]))
                with self.assertRaisesRegex(guard.PlanValidationError, "frozen SHARED"):
                    self.finish(rows)

    def test_per_vector_sizes_can_change_without_frozen_shared_rule(self):
        for after in (33, 31):
            with self.subTest(bytes_after=after):
                def callback(request):
                    result = toy_callback(request)
                    result["items"][0].update(bytes_before=32, bytes_after=after)
                    return result

                rows = [self.run_probe(r, callback) for r in guard.expected_requests(self.load())]
                self.assertEqual(self.finish(rows)["status"], "COMPLETE")

    def test_finalize_revalidates_observations_and_contract(self):
        rows = self.observations()
        rows[0]["items"][0]["bytes_after"] = -1
        with self.assertRaises(guard.PlanValidationError):
            self.finish(rows)
        self.contract_path.write_bytes(b"changed after probes")
        with self.assertRaises(guard.PlanValidationError):
            self.finish(rows)

    def test_unknown_shared_is_partial_and_caption_carries_unknown(self):
        self.add_unknown("SHARED")
        result = self.finish(self.observations())
        self.assertEqual(result["status"], "PARTIAL")
        self.assertEqual(result["unknown_ids"], ["toy-unresolved"])
        claim = self.claim(lower_bound_verified=True)
        self.assertEqual(claim["cap_verdict"], "UNKNOWN")
        self.assertEqual(claim["effective_total_status"], "LOWER_BOUND")
        self.assertIsNone(claim["headline_full_total"])
        for token in ("toy-unresolved", "margin=8", "cap=", "LOWER_BOUND", "NOT_FULL_TOTAL", "PARTIAL"):
            self.assertIn(token, claim["sentence"])
        unverified = self.claim()
        self.assertEqual(unverified["cap_verdict"], "WITHIN_12_FOR_DECLARED_MARGIN")
        self.assertEqual(unverified["effective_total_status"], "UNKNOWN")
        self.assertIsNone(unverified["effective_primary"])

    def test_unknown_per_vector_or_scope_blocks_definitive_cap(self):
        for scope in ("PER_VECTOR", "UNKNOWN"):
            with self.subTest(scope=scope):
                self.data = toy_plan(self.contract_bytes)
                self.add_unknown(scope)
                for lower_bound in (False, True):
                    claim = self.claim(lower_bound_verified=lower_bound)
                    self.assertEqual(claim["cap_verdict"], "UNKNOWN")
                    self.assertIsNone(claim["headline_full_total"])
                over = guard.make_claim(self.load(), "toy-config", "toy-u8", 13,
                                        lower_bound_verified=True)
                self.assertEqual(over["cap_verdict"], "EXCEEDS_12")

    def test_known_roster_lower_bound_never_promoted_to_full_or_within_cap(self):
        for margin in (0, 8, 12, 13):
            with self.subTest(margin=margin):
                claim = guard.make_claim(self.load(), "toy-config", "toy-u8", margin,
                                         self.costs(), lower_bound_verified=True)
                self.assertEqual(claim["unknown_ids"], [])
                self.assertEqual(claim["effective_total_status"], "LOWER_BOUND")
                self.assertEqual(claim["margin_status"], "LOWER_BOUND")
                self.assertEqual(claim["status"], "PARTIAL")
                self.assertIsNone(claim["headline_full_total"])
                self.assertIn("NOT_FULL_TOTAL", claim["sentence"])
                self.assertEqual(claim["cap_verdict"], "EXCEEDS_12" if margin > 12 else "UNKNOWN")

    def test_baseline_and_restore_failure_or_difference_cannot_be_ready(self):
        original = copy.deepcopy(self.data)
        for action in ("BASELINE", "RESTORE"):
            for outcome in ("FAILURE", "DIFFERENT", "UNKNOWN"):
                with self.subTest(action=action, outcome=outcome):
                    self.data = copy.deepcopy(original)
                    c = next(c for c in self.data["controls"] if c["action"] == action)
                    c["expected_outcome"] = outcome
                    self.write_plan()
                    callback = Mock()
                    with self.assertRaises(guard.PlanValidationError):
                        self.run_probe({}, callback)
                    callback.assert_not_called()

    def test_NA_corrupt_is_explicit_and_does_not_mean_UNKNOWN(self):
        c = next(c for c in self.data["controls"] if c["action"] == "CORRUPT")
        c.update(applicability="NA", expected_outcome="NA", na_reason="no mutable bytes in this synthetic state")
        self.write_plan()
        self.assertEqual(self.finish(self.observations())["status"], "COMPLETE")
        self.assertEqual(self.claim()["unknown_control_ids"], [])
        for reason in (None, "", "  ", "UNKNOWN"):
            c["na_reason"] = reason
            self.write_plan()
            with self.assertRaises(guard.PlanValidationError):
                self.load()

    def test_NA_baseline_restore_remove_and_inconsistent_applicability_rejected(self):
        original = copy.deepcopy(self.data)
        for action in ("BASELINE", "RESTORE", "REMOVE"):
            with self.subTest(action=action):
                self.data = copy.deepcopy(original)
                c = next(c for c in self.data["controls"] if c["action"] == action)
                c.update(applicability="NA", expected_outcome="NA", na_reason="test-only reason")
                self.write_plan()
                with self.assertRaises(guard.PlanValidationError):
                    self.load()
        self.data = copy.deepcopy(original)
        self.data["controls"][0]["expected_outcome"] = "NA"
        self.write_plan()
        with self.assertRaises(guard.PlanValidationError):
            self.load()

    def test_not_required_exclusion_remove_matches_external_boundary_can_fail(self):
        c = next(c for c in self.data["controls"]
                 if c["action"] == "REMOVE" and c["item_ids"] == ["toy-cache"])
        c["expected_outcome"] = "FAILURE"
        self.write_plan()
        with self.assertRaisesRegex(guard.PlanValidationError, "NOT_REQUIRED"):
            self.load()
        self.data["items"][1].update(exclusion_basis="EXTERNAL_BOUNDARY",
                                     reason="required external synthetic runtime; outside package boundary")
        self.write_plan()
        self.assertEqual(self.finish(self.observations())["status"], "COMPLETE")
        self.data["items"][1]["exclusion_basis"] = None
        self.write_plan()
        with self.assertRaises(guard.PlanValidationError):
            self.load()

    def test_exploratory_label_parent_and_request_membership(self):
        previous_request = guard.expected_requests(self.load())[0]
        parent_hash = self.expected_hash
        self.data.update(analysis_mode="EXPLORATORY", parent_plan_sha256=parent_hash,
                         run_id="toy-exploratory-run")
        self.write_plan()
        callback = Mock()
        with self.assertRaises(guard.PlanValidationError):
            self.run_probe(previous_request, callback)
        callback.assert_not_called()
        result = self.finish(self.observations())
        self.assertEqual(result["analysis_mode"], "EXPLORATORY")
        self.assertEqual(result["parent_plan_sha256"], parent_hash)
        claim = self.claim()
        self.assertEqual(claim["analysis_mode"], "EXPLORATORY")
        self.assertEqual(claim["parent_plan_sha256"], parent_hash)
        self.assertIn("EXPLORATORY", claim["sentence"])
        self.assertIn(parent_hash, claim["sentence"])

    def test_analysis_mode_and_parent_binding_required(self):
        for mode, parent in (("EXPLORATORY", None), ("EXPLORATORY", "UNKNOWN"),
                             ("PREDECLARED", "0" * 64), ("OTHER", None)):
            with self.subTest(mode=mode, parent=parent):
                self.data.update(analysis_mode=mode, parent_plan_sha256=parent)
                self.write_plan()
                callback = Mock()
                with self.assertRaises(guard.PlanValidationError):
                    self.run_probe({}, callback)
                callback.assert_not_called()

    def test_unknown_cannot_claim_ready_or_zero_bytes(self):
        self.add_unknown()
        request = guard.expected_requests(self.load())[0]

        def callback(r):
            result = toy_callback(r)
            result["items"][-1]["bytes_before"] = 0
            return result

        with self.assertRaises(guard.PlanValidationError):
            self.run_probe(request, callback)
        self.data["status"] = "READY"
        self.write_plan()
        with self.assertRaisesRegex(guard.PlanValidationError, "UNKNOWN requires"):
            self.load()

    def test_unknown_control_forces_partial_and_blocks_within_cap(self):
        self.data["status"] = "SCOPED_PARTIAL"
        self.data["controls"][0]["expected_outcome"] = "UNKNOWN"
        self.write_plan()
        self.assertEqual(self.finish(self.observations())["status"], "PARTIAL")
        self.assertEqual(self.claim()["cap_verdict"], "UNKNOWN")
        self.assertIn("control-0", self.claim()["sentence"])

    def test_archive_weight_fixed_and_no_subset_switching(self):
        claim = self.claim()
        self.assertEqual(claim["effective_primary"], 15)
        self.assertEqual(claim["effective_secondary"], 18)
        self.assertEqual(claim["headline_full_total"], 15)
        for rows in (self.costs()[:1], list(reversed(self.costs())), self.costs() + self.costs(),
                     [self.costs()[0], self.costs()[0]]):
            with self.assertRaises(guard.PlanValidationError):
                guard.make_claim(self.load(), "toy-config", "toy-u8", 8, rows)
        rows = self.costs()
        rows[0]["N_i"] = 493
        with self.assertRaises(guard.PlanValidationError):
            guard.make_claim(self.load(), "toy-config", "toy-u8", 8, rows)

    def test_claim_rejects_nonfinite_negative_bool_and_unknown_identity(self):
        for value in (float("nan"), float("inf"), -1, True):
            with self.assertRaises(guard.PlanValidationError):
                guard.make_claim(self.load(), "toy-config", "toy-u8", value)
        with self.assertRaises(guard.PlanValidationError):
            guard.make_claim(self.load(), "other", "toy-u8", 8)
        self.assertEqual(guard.make_claim(self.load(), "toy-config", "toy-u8", None)["cap_verdict"], "UNKNOWN")

    def test_declared_optional_stored_bytes_are_not_excluded_by_match_controls(self):
        rows = self.observations()
        self.assertTrue(all(c["outcome"] == "MATCH" for c in rows[0]["controls"]))
        self.assertEqual(rows[0]["items"][0]["bytes_after"], 8)
        self.assertEqual(rows[0]["items"][0]["disposition"], "INCLUDED")

    def test_template_is_not_executable_even_with_matching_hash(self):
        template = Path(__file__).with_name("MEASUREMENT_PLAN.template.json")
        raw = template.read_bytes()
        callback = Mock()
        with self.assertRaisesRegex(guard.PlanValidationError, "NOT_READY"):
            guard.guarded_probe(template, digest(raw), self.contract_path, {}, callback)
        callback.assert_not_called()
        self.data = json.loads(raw)
        self.data["status"] = "READY"
        self.data["contract_sha256"] = digest(self.contract_bytes)
        self.data["run_id"] = "toy-not-enough"
        self.write_plan()
        with self.assertRaises(guard.PlanValidationError):
            self.load()

    def test_duplicate_json_keys_nonfinite_and_size_limits(self):
        for raw in (b'{"schema":1,"schema":2}', b'{"x":NaN}', b" " * (guard.MAX_BYTES + 1),
                    ("[" * 40 + "0" + "]" * 40).encode()):
            self.plan_path.write_bytes(raw)
            self.expected_hash = digest(raw)
            with self.assertRaises(guard.PlanValidationError):
                self.load()

    def test_snapshot_data_is_detached_and_callback_error_propagates(self):
        plan = self.load()
        plan.data["archives"][0]["N_i"] = 493
        self.assertEqual(plan.data["archives"][0]["N_i"], 2)
        callback = Mock(side_effect=RuntimeError("dummy I/O failed"))
        with self.assertRaisesRegex(RuntimeError, "dummy I/O failed"):
            self.run_probe(guard.expected_requests(plan)[0], callback)
        callback.assert_called_once()


if __name__ == "__main__":
    unittest.main(verbosity=2)
