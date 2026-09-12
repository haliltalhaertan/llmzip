"""V52 static-storage external binding preflight.

Preparation-only validator for schema-1 plans plus two hash-bound companion records.
It does not measure storage, fit models, read corpora, score retrieval, seal, or authorize runs.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

MAX_BYTES = 1_048_576
FIXTURE_BINDING_SCHEMA = "v52.fixture-bindings"
PHYSICAL_BINDING_SCHEMA = "v52.physical-copy-bindings"
FIXTURE_CONTENT_SCHEMA = "V52_SYNTHETIC_FIXTURE_BUNDLE_V1"
OPERATION_SECTIONS = {
    "TRANSFORM": "transform",
    "ID_MAPPING": "id_mapping",
    "CORRUPT": "corruption",
}


class PreflightError(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise PreflightError(message)


def fields(value, names, where):
    need(type(value) is dict and set(value) == set(names.split()),
         f"{where}: exact fields required: {names}")


def text(value, where):
    need(type(value) is str and bool(value.strip()) and len(value) <= 4096,
         f"{where}: nonblank bounded string required")


def integer(value, where, minimum=0):
    need(type(value) is int and minimum <= value <= 2**63 - 1,
         f"{where}: integer >= {minimum} required")


def digest(value, where):
    need(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value),
         f"{where}: lowercase SHA256 required")


def read_bytes(path):
    p = Path(path)
    with p.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    need(len(raw) <= MAX_BYTES, f"{p}: file byte limit")
    return raw


def authenticate(path, expected_sha256, where):
    digest(expected_sha256, f"{where} expected SHA256")
    raw = read_bytes(path)
    actual = hashlib.sha256(raw).hexdigest()
    need(actual == expected_sha256, f"{where}: SHA256 mismatch")
    return raw


def decode_json(raw, where):
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise PreflightError(f"{where}: invalid JSON: {exc}") from exc
    need(type(value) is dict, f"{where}: object required")
    return value


def safe_child(base_dir, relative_path, where):
    text(relative_path, where)
    rel = Path(relative_path)
    need(not rel.is_absolute() and ".." not in rel.parts,
         f"{where}: path must stay below binding directory")
    base = Path(base_dir).resolve()
    child = (base / rel).resolve()
    try:
        child.relative_to(base)
    except ValueError as exc:
        raise PreflightError(f"{where}: path escapes binding directory") from exc
    return child


def unique_index(rows, where):
    need(type(rows) is list, f"{where}: list required")
    out = {}
    for row in rows:
        need(type(row) is dict and "id" in row, f"{where}: id required")
        text(row["id"], f"{where} id")
        need(row["id"] not in out, f"{where}: duplicate id {row['id']}")
        out[row["id"]] = row
    return out


def verify_fixture_artifact(binding_dir, plan_fixture, binding):
    fields(binding,
           "fixture_id relative_path byte_length sha256 content_schema operation_sections",
           "fixture binding")
    need(binding["fixture_id"] == plan_fixture["id"], "fixture id mismatch")
    integer(binding["byte_length"], "fixture byte_length", 1)
    digest(binding["sha256"], "fixture binding SHA256")
    need(binding["sha256"] == plan_fixture["sha256"], "fixture SHA disagrees with plan")
    need(binding["content_schema"] == FIXTURE_CONTENT_SCHEMA, "fixture content schema mismatch")
    need(binding["operation_sections"] == OPERATION_SECTIONS,
         "fixture operation/subfixture mapping mismatch")

    artifact = safe_child(binding_dir, binding["relative_path"], "fixture relative_path")
    raw = read_bytes(artifact)
    need(len(raw) == binding["byte_length"], "fixture byte length mismatch")
    need(hashlib.sha256(raw).hexdigest() == binding["sha256"], "fixture artifact SHA mismatch")
    payload = decode_json(raw, "fixture artifact")
    fields(payload, "schema transform id_mapping corruption", "fixture artifact")
    need(payload["schema"] == FIXTURE_CONTENT_SCHEMA, "fixture artifact schema mismatch")
    need(type(payload["transform"]) is dict, "fixture transform section required")
    need(type(payload["id_mapping"]) is dict, "fixture id_mapping section required")
    need(type(payload["corruption"]) is dict, "fixture corruption section required")
    return {
        "fixture_id": plan_fixture["id"],
        "artifact_path": str(artifact),
        "byte_length": len(raw),
        "sha256": binding["sha256"],
        "operation_sections": dict(OPERATION_SECTIONS),
    }


def verify_physical_artifact(binding_dir, plan_copy, binding, populations):
    fields(binding,
           "physical_copy_id physical_locator source_raw_byte_length artifact_sha256 "
           "sharing_denominator_rule",
           "physical binding")
    need(binding["physical_copy_id"] == plan_copy["id"], "physical copy id mismatch")
    integer(binding["source_raw_byte_length"], "source raw byte length", 0)
    digest(binding["artifact_sha256"], "physical artifact SHA256")
    need(binding["artifact_sha256"] == plan_copy["artifact_sha256"],
         "physical binding SHA disagrees with plan")
    need(binding["sharing_denominator_rule"] == "POPULATION_COUNT",
         "unsupported sharing denominator rule")

    artifact = safe_child(binding_dir, binding["physical_locator"], "physical locator")
    raw = read_bytes(artifact)
    need(len(raw) == binding["source_raw_byte_length"], "physical source length mismatch")
    need(hashlib.sha256(raw).hexdigest() == binding["artifact_sha256"],
         "physical source SHA mismatch")

    dmap = {}
    for pop_id in plan_copy["population_ids"]:
        need(pop_id in populations, f"unknown population {pop_id}")
        count = populations[pop_id]["count"]
        integer(count, f"population {pop_id} count")
        dmap[pop_id] = count
    return {
        "physical_copy_id": plan_copy["id"],
        "artifact_path": str(artifact),
        "source_raw_byte_length": len(raw),
        "artifact_sha256": binding["artifact_sha256"],
        "D_k_by_population": dmap,
    }


def preflight(plan_path, expected_plan_sha256,
              fixture_bindings_path, expected_fixture_bindings_sha256,
              physical_bindings_path, expected_physical_bindings_sha256):
    plan_raw = authenticate(plan_path, expected_plan_sha256, "plan")
    fixture_raw = authenticate(fixture_bindings_path, expected_fixture_bindings_sha256,
                               "fixture bindings")
    physical_raw = authenticate(physical_bindings_path, expected_physical_bindings_sha256,
                                "physical bindings")

    plan = decode_json(plan_raw, "plan")
    need(plan.get("schema") == "v52.static-storage-plan" and plan.get("version") == 1,
         "schema-1 plan required")
    plan_fixtures = unique_index(plan.get("fixtures"), "plan fixtures")
    plan_copies = unique_index(plan.get("physical_copies"), "plan physical copies")
    populations = unique_index(plan.get("populations"), "plan populations")

    fdoc = decode_json(fixture_raw, "fixture bindings")
    fields(fdoc, "schema version fixtures", "fixture bindings")
    need(fdoc["schema"] == FIXTURE_BINDING_SCHEMA and fdoc["version"] == 1,
         "fixture bindings schema/version")
    fixture_bindings = {}
    for row in fdoc["fixtures"]:
        need(type(row) is dict and "fixture_id" in row, "fixture binding id required")
        fid = row["fixture_id"]
        text(fid, "fixture binding id")
        need(fid not in fixture_bindings, "duplicate fixture binding")
        fixture_bindings[fid] = row
    need(set(fixture_bindings) == set(plan_fixtures),
         "fixture binding coverage must equal plan fixture roster")

    pdoc = decode_json(physical_raw, "physical bindings")
    fields(pdoc, "schema version physical_copies", "physical bindings")
    need(pdoc["schema"] == PHYSICAL_BINDING_SCHEMA and pdoc["version"] == 1,
         "physical bindings schema/version")
    physical_bindings = {}
    for row in pdoc["physical_copies"]:
        need(type(row) is dict and "physical_copy_id" in row, "physical binding id required")
        cid = row["physical_copy_id"]
        text(cid, "physical binding id")
        need(cid not in physical_bindings, "duplicate physical binding")
        physical_bindings[cid] = row
    need(set(physical_bindings) == set(plan_copies),
         "physical binding coverage must equal plan physical-copy roster")

    verified_fixtures = [
        verify_fixture_artifact(Path(fixture_bindings_path).resolve().parent,
                                plan_fixtures[fid], fixture_bindings[fid])
        for fid in plan_fixtures
    ]
    verified_copies = [
        verify_physical_artifact(Path(physical_bindings_path).resolve().parent,
                                 plan_copies[cid], physical_bindings[cid], populations)
        for cid in plan_copies
    ]

    return {
        "status": "PASS_PRECALL_EXTERNAL_BINDINGS",
        "plan_sha256": expected_plan_sha256,
        "fixture_bindings_sha256": expected_fixture_bindings_sha256,
        "physical_bindings_sha256": expected_physical_bindings_sha256,
        "verified_fixture_count": len(verified_fixtures),
        "verified_physical_copy_count": len(verified_copies),
        "fixtures": verified_fixtures,
        "physical_copies": verified_copies,
        "scope": "external binding preflight only; no storage measurement or run authorization",
    }
