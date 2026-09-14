"""Bounded declaration/coverage guard; no real runner or cost measurement integration.

Hashes establish byte identity, not authority. See PLAN_INTERFACE.md.
"""

import copy
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import re


SCHEMA = "v52.static-storage-plan"
VERSION = 1
MAX_BYTES = 1_048_576
MAX_ENTITIES = 1024
MAX_REQUESTS = 4096
MAX_DEPTH = 24
PRIMARY = "archive_weighted_mean_i(C_i/N_i)"
SECONDARY = "vector_weighted_sum_i(C_i)/sum_i(N_i)"
DISPOSITIONS = {"INCLUDED", "EXCLUDED", "UNKNOWN"}
ACTIONS = {"REMOVE", "RESTORE", "CORRUPT"}
OUTCOMES = {"MATCH", "DIFFERENT", "FAILURE", "UNKNOWN", "NA"}
DTYPES = {"uint8", "int8", "uint16", "int16", "uint32", "int32", "uint64",
          "int64", "float16", "float32", "float64", "bytes", "utf8", "mixed"}


class PlanValidationError(ValueError):
    """Fatal validation failure. Callers must stop this run."""


def _need(condition, message):
    if not condition:
        raise PlanValidationError(message)


def _fields(value, names, where):
    _need(type(value) is dict and set(value) == set(names.split()),
          f"{where}: exact fields required: {names}")


def _text(value, where):
    _need(type(value) is str and bool(value.strip()) and len(value) <= 4096,
          f"{where}: nonblank bounded string required")


def _integer(value, where, minimum=0):
    _need(type(value) is int and minimum <= value <= 2**63 - 1,
          f"{where}: integer >= {minimum} required")


def _digest(value, where):
    _need(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
          f"{where}: lowercase SHA256 required")


def _array(value, where, nonempty=True):
    _need(type(value) is list and (not nonempty or len(value) > 0)
          and len(value) <= MAX_ENTITIES, f"{where}: bounded array required")


def _unique(values, where):
    _need(len(values) == len(set(values)), f"{where}: duplicate identity")


def _refs(values, universe, where, nonempty=True):
    _array(values, where, nonempty)
    for value in values:
        _text(value, where)
        _need(value in universe, f"{where}: unknown reference {value}")
    _unique(values, where)


def _index(rows, where, nonempty=True):
    _array(rows, where, nonempty)
    ids = []
    for row in rows:
        _need(type(row) is dict and "id" in row, f"{where}: object/id required")
        _text(row["id"], where)
        _need(row["id"] != "UNKNOWN", f"{where}: unresolved identity")
        ids.append(row["id"])
    _unique(ids, where)
    return dict(zip(ids, rows))


def _bounded_json(value, depth=0):
    _need(depth <= MAX_DEPTH, "JSON nesting limit")
    if type(value) is dict:
        _need(len(value) <= MAX_ENTITIES, "JSON object limit")
        for key, child in value.items():
            _text(key, "JSON key")
            _bounded_json(child, depth + 1)
    elif type(value) is list:
        _need(len(value) <= MAX_REQUESTS, "JSON array limit")
        for child in value:
            _bounded_json(child, depth + 1)
    elif type(value) is str:
        _need(len(value) <= 4096, "JSON string limit")
    else:
        _need(value is None or type(value) in (bool, int, float), "non-JSON value")
        if type(value) in (int, float):
            _need(abs(value) <= 2**63 - 1 and math.isfinite(value), "numeric limit")


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        _need(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _decode(raw):
    try:
        result = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                            parse_constant=lambda _: (_ for _ in ()).throw(
                                PlanValidationError("nonfinite JSON")))
        _bounded_json(result)
        return result
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise PlanValidationError(f"invalid plan JSON: {exc}") from exc


def _read(path):
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    _need(len(raw) <= MAX_BYTES, "file byte limit")
    return raw


def _validate_data(data, contract_sha256):
    _fields(data, "schema version status contract_sha256 run_id weighting archives formats "
            "analysis_mode parent_plan_sha256 configurations probes items populations "
            "physical_copies fixtures operations controls", "plan")
    _need(data["schema"] == SCHEMA and type(data["version"]) is int
          and data["version"] == VERSION, "unsupported schema/version")
    _need(data["status"] in ("READY", "SCOPED_PARTIAL"), "plan NOT_READY")
    _digest(data["contract_sha256"], "contract_sha256")
    _need(data["contract_sha256"] == contract_sha256, "contract hash mismatch")
    _text(data["run_id"], "run_id")
    _need(data["run_id"] != "UNKNOWN", "unresolved run identity")
    _need(data["analysis_mode"] in ("PREDECLARED", "EXPLORATORY"), "analysis_mode required")
    if data["analysis_mode"] == "EXPLORATORY":
        _digest(data["parent_plan_sha256"], "exploratory parent plan SHA256")
    else:
        _need(data["parent_plan_sha256"] is None, "PREDECLARED parent must be null")
    _fields(data["weighting"], "primary secondary", "weighting")
    _need(data["weighting"] == {"primary": PRIMARY, "secondary": SECONDARY},
          "fixed primary/secondary weighting required")
    archives = _index(data["archives"], "archives")
    formats = _index(data["formats"], "formats")
    configs = _index(data["configurations"], "configurations")
    probes = _index(data["probes"], "probes")
    items = _index(data["items"], "items")
    populations = _index(data["populations"], "populations")
    copies = _index(data["physical_copies"], "physical_copies", False)
    fixtures = _index(data["fixtures"], "fixtures")
    operations = _index(data["operations"], "operations")
    controls = _index(data["controls"], "controls")
    for a in archives.values():
        _fields(a, "id N_i", "archive")
        _integer(a["N_i"], "N_i", 1)
    for f in formats.values():
        _fields(f, "id serialization dtype representation", "format")
        _text(f["serialization"], "serialization")
        _need(f["serialization"] != "UNKNOWN", "undeclared serialization")
        _need(f["dtype"] in DTYPES, "undeclared dtype")
        _need(f["representation"] in ("REAL", "SURROGATE", "EXPLICIT_CONVERSION"),
              "undeclared representation")
    for item in items.values():
        _fields(item, "id role disposition reason cost_scope source_identity exclusion_basis", "item")
        for key in ("role", "reason", "source_identity"):
            _text(item[key], key)
        _need(item["disposition"] in DISPOSITIONS, "invalid disposition")
        _need(item["cost_scope"] in ("PER_VECTOR", "SHARED", "UNKNOWN"), "invalid cost scope")
        if item["disposition"] == "EXCLUDED":
            _need(item["exclusion_basis"] in ("NOT_REQUIRED", "EXTERNAL_BOUNDARY"),
                  "excluded item requires explicit exclusion_basis")
        else:
            _need(item["exclusion_basis"] is None, "non-excluded exclusion_basis must be null")
        if item["disposition"] != "UNKNOWN":
            _need(item["cost_scope"] != "UNKNOWN" and item["source_identity"] != "UNKNOWN",
                  "known item requires known scope/source")
    for f in fixtures.values():
        _fields(f, "id kind sha256 generator_identity", "fixture")
        _need(f["kind"] == "SYNTHETIC", "only synthetic fixture declarations allowed")
        _digest(f["sha256"], "fixture SHA256")
        _text(f["generator_identity"], "fixture generator")
        _need(f["generator_identity"] != "UNKNOWN", "unknown fixture generator")
    for op in operations.values():
        _fields(op, "id kind implementation_identity", "operation")
        _need(op["kind"] in ("TRANSFORM", "ID_MAPPING"), "undeclared operation")
        _text(op["implementation_identity"], "implementation identity")
        _need(op["implementation_identity"] != "UNKNOWN", "unknown implementation")
    _need({op["kind"] for op in operations.values()} == {"TRANSFORM", "ID_MAPPING"},
          "transform and ID mapping operations required")
    used_items, used_formats = set(), set()
    for c in configs.values():
        _fields(c, "id format_ids item_ids", "configuration")
        _refs(c["format_ids"], formats, "config formats")
        _refs(c["item_ids"], items, "config items")
        used_items.update(c["item_ids"])
        used_formats.update(c["format_ids"])
    _need(used_items == set(items) and used_formats == set(formats), "unused item/format")
    for p in probes.values():
        _fields(p, "id archive_id N q fixture_id", "probe")
        _need(p["archive_id"] in archives and p["fixture_id"] in fixtures, "probe reference")
        _integer(p["N"], "N")
        _integer(p["q"], "q", 1)
        _integer(p["N"] + p["q"], "N+q")
    _need({p["archive_id"] for p in probes.values()} == set(archives), "archive omitted from panel")
    _need({p["fixture_id"] for p in probes.values()} == set(fixtures), "unused fixture")
    _unique([(p["archive_id"], p["N"], p["q"]) for p in probes.values()], "N/q panel")
    population_keys = []
    for pop in populations.values():
        _fields(pop, "id archive_id probe_id phase count member_ids_sha256", "population")
        _need(pop["probe_id"] in probes, "population probe reference")
        p = probes[pop["probe_id"]]
        _need(pop["archive_id"] == p["archive_id"], "population archive mismatch")
        _need(pop["phase"] in ("BEFORE", "AFTER"), "population phase")
        _integer(pop["count"], "population count")
        _need(pop["count"] == p["N"] + (p["q"] if pop["phase"] == "AFTER" else 0),
              "population count mismatch")
        _digest(pop["member_ids_sha256"], "population membership SHA256")
        population_keys.append((pop["probe_id"], pop["phase"]))
    _unique(population_keys, "snapshot populations")
    _need(set(population_keys) == {(p, phase) for p in probes for phase in ("BEFORE", "AFTER")},
          "complete snapshot populations required")
    copy_keys = set()
    for physical in copies.values():
        _fields(physical, "id item_id archive_id config_id format_id artifact_identity "
                "artifact_sha256 population_ids", "physical copy")
        _need(physical["config_id"] in configs and physical["archive_id"] in archives,
              "copy config/archive reference")
        c = configs[physical["config_id"]]
        _need(physical["item_id"] in c["item_ids"] and physical["format_id"] in c["format_ids"],
              "copy item/format reference")
        _need(items[physical["item_id"]]["disposition"] == "INCLUDED", "copy must be included")
        _text(physical["artifact_identity"], "physical artifact identity")
        _need(physical["artifact_identity"] != "UNKNOWN", "unknown physical identity")
        _digest(physical["artifact_sha256"], "artifact SHA256")
        _refs(physical["population_ids"], populations, "copy populations")
        expected = {pop["id"] for pop in populations.values()
                    if pop["archive_id"] == physical["archive_id"]}
        _need(set(physical["population_ids"]) == expected, "copy snapshot population mismatch")
        copy_keys.add((physical["archive_id"], physical["config_id"],
                       physical["format_id"], physical["item_id"]))
    expected_copies = {(a, c["id"], f, i) for a in archives for c in configs.values()
                       for f in c["format_ids"] for i in c["item_ids"]
                       if items[i]["disposition"] == "INCLUDED"}
    _need(copy_keys == expected_copies, "included physical copy inventory incomplete")
    # A physical identity cannot be renamed to count it twice. Equal hashes are
    # permitted for distinct physical identities (e.g. two actual file copies).
    _unique([c["artifact_identity"] for c in copies.values()], "physical artifact identities")
    control_keys = []
    for control in controls.values():
        _fields(control, "id config_id operation_id scope item_ids action expected_outcome "
                "reference_identity applicability na_reason", "control")
        _need(control["config_id"] in configs and control["operation_id"] in operations,
              "control reference")
        roster = configs[control["config_id"]]["item_ids"]
        _refs(control["item_ids"], roster, "control items", False)
        known = [i for i in roster if items[i]["disposition"] != "UNKNOWN"]
        scope, action = control["scope"], control["action"]
        _need(control["expected_outcome"] in OUTCOMES, "control expected outcome")
        _need(control["applicability"] in ("APPLICABLE", "NA"), "control applicability")
        if control["applicability"] == "NA":
            _need(action == "CORRUPT" and control["expected_outcome"] == "NA",
                  "NA allowed only for CORRUPT with NA outcome")
            _text(control["na_reason"], "NA reason")
            _need(control["na_reason"] != "UNKNOWN", "NA requires a known reason")
        else:
            _need(control["na_reason"] is None and control["expected_outcome"] != "NA",
                  "applicable control cannot have NA reason/outcome")
        if action in ("BASELINE", "RESTORE"):
            _need(control["expected_outcome"] in ("MATCH", "UNKNOWN"),
                  "baseline/restore must MATCH or remain UNKNOWN in SCOPED_PARTIAL")
        _text(control["reference_identity"], "control reference identity")
        _need(control["reference_identity"] != "UNKNOWN", "unknown control reference identity")
        if scope == "BASELINE":
            _need(action == "BASELINE" and not control["item_ids"], "baseline control")
        elif scope == "PER_ITEM":
            _need(action in ACTIONS and len(control["item_ids"]) == 1
                  and control["item_ids"][0] in known, "per-item control")
            item = items[control["item_ids"][0]]
            if action == "REMOVE" and item["exclusion_basis"] == "NOT_REQUIRED":
                _need(control["expected_outcome"] == "MATCH",
                      "excluded-as-NOT_REQUIRED removal must MATCH")
        else:
            _need(scope == "FALLBACK_COMBINED" and action in ACTIONS
                  and control["item_ids"] == known, "combined fallback roster")
        control_keys.append((control["config_id"], control["operation_id"], scope,
                             tuple(control["item_ids"]), action))
    _unique(control_keys, "control states")
    required_controls = set()
    for c in configs.values():
        known = [i for i in c["item_ids"] if items[i]["disposition"] != "UNKNOWN"]
        for op in operations:
            required_controls.add((c["id"], op, "BASELINE", (), "BASELINE"))
            for action in ACTIONS:
                required_controls.add((c["id"], op, "FALLBACK_COMBINED", tuple(known), action))
                for i in known:
                    required_controls.add((c["id"], op, "PER_ITEM", (i,), action))
    _need(set(control_keys) == required_controls, "necessity/control coverage incomplete")
    unknown = any(i["disposition"] == "UNKNOWN" for i in items.values()) or any(
        c["expected_outcome"] == "UNKNOWN" for c in controls.values())
    _need(not unknown or data["status"] == "SCOPED_PARTIAL", "UNKNOWN requires SCOPED_PARTIAL")
    count = len(probes) * sum(len(c["format_ids"]) for c in configs.values())
    _need(count <= MAX_REQUESTS, "request panel limit")


def _validate(data, contract_sha256):
    try:
        _validate_data(data, contract_sha256)
    except (TypeError, KeyError) as exc:
        raise PlanValidationError(f"invalid schema value/reference: {exc}") from exc


@dataclass(frozen=True)
class Plan:
    raw: bytes
    sha256: str
    contract_sha256: str

    @property
    def data(self):
        """Return a fresh copy; modifying it cannot modify the frozen bytes."""
        return _decode(self.raw)


def load_plan(path, expected_sha256, contract_path):
    """Authenticate no authority: compare external byte identity BEFORE parsing.

    Only plan bytes are read before the hash comparison. Contract bytes follow;
    no fixture, model, corpus, callback, or declared artifact path is opened.
    """
    _digest(expected_sha256, "external expected SHA256")
    raw = _read(path)
    _need(hashlib.sha256(raw).hexdigest() == expected_sha256, "plan hash mismatch")
    contract_hash = hashlib.sha256(_read(contract_path)).hexdigest()
    data = _decode(raw)
    _validate(data, contract_hash)
    return Plan(raw, expected_sha256, contract_hash)


def _checked_data(plan):
    _need(type(plan) is Plan and len(plan.raw) <= MAX_BYTES, "loaded Plan required")
    _need(hashlib.sha256(plan.raw).hexdigest() == plan.sha256, "snapshot hash mismatch")
    data = plan.data
    _validate(data, plan.contract_sha256)
    return data


def _requests(data):
    # Probe order, then declared configuration order, then format order.
    for probe in data["probes"]:
        archive = next(a for a in data["archives"] if a["id"] == probe["archive_id"])
        fixture = next(f for f in data["fixtures"] if f["id"] == probe["fixture_id"])
        for config in data["configurations"]:
            for format_id in config["format_ids"]:
                yield {
                    "run_id": data["run_id"], "archive": archive, "config_id": config["id"],
                    "analysis_mode": data["analysis_mode"], "parent_plan_sha256": data["parent_plan_sha256"],
                    "format": next(f for f in data["formats"] if f["id"] == format_id),
                    "probe": probe, "fixture": fixture,
                    "items": [next(i for i in data["items"] if i["id"] == item_id)
                              for item_id in config["item_ids"]],
                    "physical_copies": [c for c in data["physical_copies"]
                                        if c["archive_id"] == archive["id"]
                                        and c["config_id"] == config["id"]
                                        and c["format_id"] == format_id],
                    "populations": [p for p in data["populations"] if p["probe_id"] == probe["id"]],
                    "operations": data["operations"],
                    "controls": [c for c in data["controls"] if c["config_id"] == config["id"]],
                }


def expected_requests(plan):
    """Ordered complete panel; callers cannot choose an alternative subset."""
    return list(_requests(_checked_data(plan)))


def probe_key(request):
    return (request["archive"]["id"], request["config_id"],
            request["format"]["id"], request["probe"]["id"])


def _json_identity(value):
    _bounded_json(value)
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False,
                      separators=(",", ":"))


def _match_request(data, request):
    encoded = _json_identity(request)
    for expected in _requests(data):
        if encoded == _json_identity(expected):
            return expected
    raise PlanValidationError("request is not an exact frozen panel member")


def _observation(expected, observed):
    _bounded_json(observed)
    _fields(observed, "request items controls", "observation")
    _need(_json_identity(observed["request"]) == _json_identity(expected), "observed identity mismatch")
    _array(observed["items"], "observed items")
    _need(len(observed["items"]) == len(expected["items"]), "observed item coverage")
    for item, row in zip(expected["items"], observed["items"]):
        _fields(row, "item_id disposition format_id physical_copy_ids bytes_before bytes_after", "item observation")
        _need(row["item_id"] == item["id"] and row["disposition"] == item["disposition"]
              and row["format_id"] == expected["format"]["id"], "observed item/format/order mismatch")
        ids = [c["id"] for c in expected["physical_copies"] if c["item_id"] == item["id"]]
        _need(row["physical_copy_ids"] == ids, "observed physical copy mismatch")
        for field in ("bytes_before", "bytes_after"):
            if item["disposition"] == "INCLUDED":
                _integer(row[field], field)
            else:
                _need(row[field] is None, "excluded/UNKNOWN bytes must be null, not zero")
        if item["disposition"] == "INCLUDED" and item["cost_scope"] == "SHARED":
            _need(row["bytes_before"] == row["bytes_after"],
                  "frozen SHARED item size changed across probe")
    _array(observed["controls"], "observed controls")
    _need(len(observed["controls"]) == len(expected["controls"]), "observed control coverage")
    for control, row in zip(expected["controls"], observed["controls"]):
        _fields(row, "control_id outcome reference_identity", "control observation")
        _need(row == {"control_id": control["id"], "outcome": control["expected_outcome"],
                      "reference_identity": control["reference_identity"]}, "observed control mismatch")


def guarded_probe(plan_path, expected_sha256, contract_path, request, measure_callback):
    """Revalidate before callback; a validation/callback exception stops the call.

    A callback receives a detached exact request and returns the observation
    envelope documented in PLAN_INTERFACE.md. It is trusted Python, not JSON code.
    """
    plan = load_plan(plan_path, expected_sha256, contract_path)
    expected = _match_request(plan.data, request)
    _need(callable(measure_callback), "callable required")
    observed = measure_callback(copy.deepcopy(expected))
    # Also reject replacement during callback; this cannot undo callback I/O.
    load_plan(plan_path, expected_sha256, contract_path)
    _observation(expected, observed)
    return copy.deepcopy(observed)


def finalize(plan_path, expected_sha256, contract_path, observations):
    """Require exact ordered coverage; no missing, duplicate or exploratory rows.

    COMPLETE means declaration/coverage checks passed, not scientific validation.
    UNKNOWN declarations/control evidence force PARTIAL even with full coverage.
    """
    plan = load_plan(plan_path, expected_sha256, contract_path)
    data = plan.data
    _need(type(observations) is list and len(observations) <= MAX_REQUESTS,
          "bounded observation list required")
    expected = list(_requests(data))
    _need(len(observations) == len(expected), "incomplete/extra probe coverage")
    for request, observed in zip(expected, observations):
        _observation(request, observed)
    unknown_items = [i["id"] for i in data["items"] if i["disposition"] == "UNKNOWN"]
    unknown_controls = [c["id"] for c in data["controls"] if c["expected_outcome"] == "UNKNOWN"]
    return {"status": "PARTIAL" if data["status"] == "SCOPED_PARTIAL" else "COMPLETE",
            "plan_sha256": plan.sha256, "contract_sha256": plan.contract_sha256,
            "run_id": data["run_id"], "probe_keys": [list(probe_key(r)) for r in expected],
            "analysis_mode": data["analysis_mode"], "parent_plan_sha256": data["parent_plan_sha256"],
            "unknown_ids": unknown_items, "unknown_control_ids": unknown_controls,
            "primary_weighting": PRIMARY, "secondary_weighting": SECONDARY,
            "scope": "declaration and synthetic observation coverage only; no real runner integration"}


def _number(value, where):
    _need(type(value) in (int, float) and 0 <= value <= 2**63 - 1
          and math.isfinite(value), f"{where}: finite nonnegative number required")


def make_claim(plan, config_id, format_id, marginal_bytes_per_vector,
               archive_costs=None, *, lower_bound_verified=False):
    """Couple cost, verdict, UNKNOWN and labels. Does not verify supplied costs.

    archive_costs is the complete ordered [{archive_id, N_i, C_i}] roster for
    this config/format. A lower bound requires caller-verified allocation and
    deduplication. lower_bound_verified=True marks ALL supplied costs (including
    margin) as verified LOWER_BOUND, even with no UNKNOWN items. This helper
    never infers a general marginal law from probes.
    """
    data = _checked_data(plan)
    config = next((c for c in data["configurations"] if c["id"] == config_id), None)
    _need(config is not None and format_id in config["format_ids"], "claim config/format reference")
    _need(type(lower_bound_verified) is bool, "lower_bound_verified must be boolean")
    if marginal_bytes_per_vector is not None:
        _number(marginal_bytes_per_vector, "margin")
    items = [i for i in data["items"] if i["id"] in config["item_ids"]]
    unknown = [i["id"] for i in items if i["disposition"] == "UNKNOWN"]
    unknown_controls = [c["id"] for c in data["controls"] if c["config_id"] == config_id
                        and c["expected_outcome"] == "UNKNOWN"]
    vector_unknown = any(i["disposition"] == "UNKNOWN" and i["cost_scope"] != "SHARED" for i in items)
    partial = data["status"] == "SCOPED_PARTIAL"
    unresolved = bool(unknown or unknown_controls or partial)
    primary = secondary = None
    if archive_costs is not None:
        _array(archive_costs, "archive costs")
        _need(len(archive_costs) == len(data["archives"]), "full archive roster required")
        costs, counts = [], []
        for a, row in zip(data["archives"], archive_costs):
            _fields(row, "archive_id N_i C_i", "archive cost")
            _integer(row["N_i"], "cost N_i", 1)
            _need(row["archive_id"] == a["id"] and row["N_i"] == a["N_i"], "archive cost identity/order mismatch")
            _number(row["C_i"], "C_i")
            costs.append(row["C_i"])
            counts.append(row["N_i"])
        primary = sum(c / n for c, n in zip(costs, counts)) / len(counts)
        secondary = sum(costs) / sum(counts)
        _number(primary, "primary aggregate")
        _number(secondary, "secondary aggregate")
    total_status = "UNKNOWN" if primary is None else (
        "LOWER_BOUND" if lower_bound_verified else "UNKNOWN" if unresolved else "FULL")
    if total_status == "UNKNOWN":
        primary = secondary = None
    margin_status = "UNKNOWN" if marginal_bytes_per_vector is None else (
        "LOWER_BOUND" if lower_bound_verified else
        "UNKNOWN" if vector_unknown else "DECLARED_MARGIN")
    verdict = "UNKNOWN"
    if margin_status != "UNKNOWN":
        if marginal_bytes_per_vector > 12:
            verdict = "EXCEEDS_12"
        elif margin_status == "DECLARED_MARGIN" and not vector_unknown and not unknown_controls:
            verdict = "WITHIN_12_FOR_DECLARED_MARGIN"
    result = {
        "plan_sha256": plan.sha256, "contract_sha256": plan.contract_sha256,
        "run_id": data["run_id"], "config_id": config_id, "format_id": format_id,
        "analysis_mode": data["analysis_mode"], "parent_plan_sha256": data["parent_plan_sha256"],
        "status": "PARTIAL" if unresolved or total_status != "FULL" or margin_status != "DECLARED_MARGIN"
                  else "COMPLETE_DECLARATION",
        "marginal_bytes_per_vector": marginal_bytes_per_vector, "margin_status": margin_status,
        "cap_verdict": verdict, "unknown_ids": unknown, "unknown_control_ids": unknown_controls,
        "effective_total_status": total_status,
        "lower_bound_label": "VERIFIED_SUBTOTAL_ONLY_NOT_FULL_TOTAL" if total_status == "LOWER_BOUND"
                             or margin_status == "LOWER_BOUND" else "NO_LOWER_BOUND_CLAIM",
        "primary_weighting": PRIMARY, "secondary_weighting": SECONDARY,
        "effective_primary": primary, "effective_secondary": secondary,
        "headline_full_total": primary if total_status == "FULL" else None,
    }
    result["sentence"] = (
        f"analysis_mode={data['analysis_mode']}, parent_plan_sha256={data['parent_plan_sha256']}; "
        f"margin={marginal_bytes_per_vector} B/vector ({margin_status}); cap={verdict}; "
        f"UNKNOWN items={unknown}, controls={unknown_controls}; effective_total={total_status}; "
        f"{result['lower_bound_label']}; archive-weighted={primary}, vector-weighted={secondary}; "
        f"status={result['status']}; declared scope only, no general eligibility or real runner proof."
    )
    return result
