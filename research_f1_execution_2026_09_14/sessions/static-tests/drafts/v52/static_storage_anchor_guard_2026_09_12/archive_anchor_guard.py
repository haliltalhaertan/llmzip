"""V52 static-storage archive-anchor guard.

Closes the two scientific findings of the independent V3 audit
(audit/v52-static-storage-plan-prep-v3-independent-2026-09-12 @ b06247df):

  AUD-001  the plan's archive sizes N_i, and therefore the headline aggregate
           mean_i(C_i/N_i) and every amortization denominator, are internally
           consistent but externally unanchored. Nothing tied N_i to a frozen
           source, and nothing tied a probe's N to its archive's N_i, so an
           inflated declaration deflated the published figure with both guards
           passing.

  AUD-008  sharing_denominator_rule = POPULATION_COUNT emitted one candidate per
           bound population - None, 1, 10^9, 4 for a single artifact - with no
           selection rule. Choosing the largest was the dilution AUD-001 warns of.

This module is ADDITIVE. measurement_plan_guard.py is not modified and its bytes are
not rewritten. It runs AFTER that guard has validated the plan's structure, and it
requires no change to the schema-1 plan: the roles it needs are DERIVED from values the
schema already carries, so no new declared field can be mis-declared.

Preparation-only. Authorizes no measurement, model fitting, retrieval or Task4F1 access.
"""
from __future__ import annotations
from dataclasses import dataclass
import csv
import hashlib
import io
import re

MAX_ANCHOR_BYTES = 8 * 1024 * 1024
MAX_ANCHOR_ROWS = 100_000


class AnchorValidationError(ValueError):
    """Fatal anchor failure. Callers must stop this run."""


def _need(condition, message):
    if not condition:
        raise AnchorValidationError(message)


def _digest(value, where):
    _need(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
          f"{where}: lowercase SHA256 required")


@dataclass(frozen=True)
class ArchiveAnchor:
    """A frozen, digest-bound source of true archive sizes."""
    source_identity: str
    sha256: str
    id_column: str
    value_column: str
    sizes: tuple          # ((archive_id, N), ...) in file order

    def as_map(self):
        return dict(self.sizes)

    def reverify(self, raw_bytes):
        _need(hashlib.sha256(raw_bytes).hexdigest() == self.sha256,
              f"{self.source_identity}: anchor bytes no longer match their digest")
        return True


def load_anchor(raw_bytes, expected_sha256, source_identity, id_column, value_column):
    """Authenticate a frozen archive-size table and read it.

    Takes BYTES, not a path: the caller authenticates what it read, and this module
    never reopens a locator after hashing it. Refuses a duplicate archive id, a
    non-integer or non-positive size, and an empty table.
    """
    _need(type(raw_bytes) is bytes, "anchor source must be bytes")
    _need(len(raw_bytes) <= MAX_ANCHOR_BYTES, "anchor source byte limit")
    _digest(expected_sha256, "expected anchor SHA256")
    actual = hashlib.sha256(raw_bytes).hexdigest()
    _need(actual == expected_sha256,
          f"{source_identity}: anchor SHA256 mismatch (declared {expected_sha256}, actual {actual})")
    _need(type(source_identity) is str and source_identity.strip(), "anchor source identity required")
    for name in (id_column, value_column):
        _need(type(name) is str and name.strip(), "anchor column names required")
    _need(id_column != value_column, "anchor id and value columns must differ")

    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeError as e:
        raise AnchorValidationError(f"{source_identity}: anchor source is not UTF-8: {e}") from e
    reader = csv.DictReader(io.StringIO(text, newline=""))
    _need(reader.fieldnames is not None, f"{source_identity}: anchor source has no header")
    _need(id_column in reader.fieldnames, f"{source_identity}: missing id column {id_column}")
    _need(value_column in reader.fieldnames, f"{source_identity}: missing value column {value_column}")

    rows, seen = [], set()
    for i, row in enumerate(reader, start=2):
        _need(len(rows) < MAX_ANCHOR_ROWS, f"{source_identity}: anchor row limit")
        key = row.get(id_column)
        raw_value = row.get(value_column)
        _need(type(key) is str and key.strip(), f"{source_identity} line {i}: blank archive id")
        _need(key not in seen, f"{source_identity} line {i}: duplicate archive id {key}")
        _need(type(raw_value) is str and re.fullmatch(r"[0-9]+", raw_value.strip()) is not None,
              f"{source_identity} line {i}: archive size must be a non-negative decimal integer")
        value = int(raw_value.strip())
        _need(value >= 1, f"{source_identity} line {i}: archive size must be at least 1")
        seen.add(key)
        rows.append((key, value))
    _need(rows, f"{source_identity}: anchor source carries no rows")
    return ArchiveAnchor(source_identity, expected_sha256, id_column, value_column, tuple(rows))


def verify_archive_sizes(plan_data, anchor):
    """AUD-001: every declared N_i must equal the frozen source, with no archive unanchored.

    `plan_data` is the already-structurally-validated schema-1 plan mapping.
    """
    archives = plan_data.get("archives")
    _need(type(archives) is list and archives, "plan archives: non-empty list required")
    sizes = anchor.as_map()
    checked = []
    for a in archives:
        _need(type(a) is dict and "id" in a and "N_i" in a, "plan archive: id and N_i required")
        aid = a["id"]
        _need(type(aid) is str and aid.strip(), "plan archive id required")
        _need(aid in sizes,
              f"archive {aid} is not present in the frozen anchor {anchor.source_identity}; "
              f"an unanchored archive size may not be used")
        _need(type(a["N_i"]) is int and a["N_i"] == sizes[aid],
              f"archive {aid}: declared N_i {a['N_i']!r} disagrees with the frozen anchor "
              f"value {sizes[aid]}")
        checked.append(aid)
    _need(len(set(checked)) == len(checked), "plan archives: duplicate archive id")
    return tuple(checked)


def classify_probes(plan_data):
    """Derive each probe's role rather than letting the plan declare it.

    FULL_SIZE  -- N equals the archive's anchored N_i. This is the add-one estimand at
                  the real archive, and the only probe whose populations describe the
                  real sharing group.
    DIAGNOSTIC -- any other N. The staircase points exist to expose block and header
                  steps in the serializer; they describe no real archive and may not
                  contribute an amortization denominator.

    Returns {probe_id: role}.
    """
    archives = {a["id"]: a["N_i"] for a in plan_data["archives"]}
    probes = plan_data.get("probes")
    _need(type(probes) is list and probes, "plan probes: non-empty list required")
    roles = {}
    for p in probes:
        for key in ("id", "archive_id", "N"):
            _need(type(p) is dict and key in p, f"plan probe: missing field {key}")
        _need(p["archive_id"] in archives, f"probe {p['id']}: unknown archive {p['archive_id']}")
        _need(type(p["N"]) is int, f"probe {p['id']}: N must be an int")
        _need(p["id"] not in roles, f"duplicate probe id {p['id']}")
        roles[p["id"]] = "FULL_SIZE" if p["N"] == archives[p["archive_id"]] else "DIAGNOSTIC"
    return roles


def verify_full_size_coverage(plan_data, roles):
    """The declared panel is `(N_i, q=1)` for every archive. Enforce it.

    Exactly one FULL_SIZE probe per archive, so the authoritative denominator is unique
    by construction rather than by the caller's choice.
    """
    per_archive = {}
    for p in plan_data["probes"]:
        if roles[p["id"]] == "FULL_SIZE":
            per_archive.setdefault(p["archive_id"], []).append(p["id"])
    for a in plan_data["archives"]:
        got = per_archive.get(a["id"], [])
        _need(len(got) == 1,
              f"archive {a['id']}: exactly one full-size probe required, found {len(got)}")
    return {aid: ids[0] for aid, ids in per_archive.items()}


def authoritative_denominators(plan_data, roles):
    """AUD-008: return ONE denominator per physical copy, or refuse.

    The denominator is the BEFORE population of the archive's full-size probe: the
    number of vectors that actually share the copy in the real archive. Diagnostic
    populations and AFTER populations are not eligible, so the largest-candidate
    selection that AUD-001 warns about cannot be made.
    """
    populations = {}
    for pop in plan_data.get("populations", []):
        for key in ("id", "probe_id", "phase", "count"):
            _need(type(pop) is dict and key in pop, f"plan population: missing field {key}")
        _need(pop["id"] not in populations, f"duplicate population id {pop['id']}")
        populations[pop["id"]] = pop

    out = {}
    for copy in plan_data.get("physical_copies", []):
        for key in ("id", "population_ids"):
            _need(type(copy) is dict and key in copy, f"plan physical copy: missing field {key}")
        pop_ids = copy["population_ids"]
        _need(type(pop_ids) is list, f"physical copy {copy['id']}: population_ids must be a list")
        eligible = []
        for pid in pop_ids:
            _need(pid in populations, f"physical copy {copy['id']}: unknown population {pid}")
            pop = populations[pid]
            _need(pop["probe_id"] in roles, f"population {pid}: unknown probe {pop['probe_id']}")
            if roles[pop["probe_id"]] == "FULL_SIZE" and pop["phase"] == "BEFORE":
                eligible.append(pop)
        _need(len(eligible) == 1,
              f"physical copy {copy['id']}: exactly one full-size BEFORE population required "
              f"as the amortization denominator, found {len(eligible)}")
        count = eligible[0]["count"]
        _need(type(count) is int and count >= 1,
              f"physical copy {copy['id']}: amortization denominator must be a positive integer, "
              f"got {count!r}")
        out[copy["id"]] = (eligible[0]["id"], count)
    return out


def verify_plan_against_anchor(plan_data, anchor):
    """The whole check, in the order a caller should run it.

    Returns (archive_ids, probe_roles, full_size_probe_per_archive, denominators).
    Every return value is derived from the anchored sizes; none of it is declared.
    """
    archive_ids = verify_archive_sizes(plan_data, anchor)
    roles = classify_probes(plan_data)
    full_size = verify_full_size_coverage(plan_data, roles)
    denominators = authoritative_denominators(plan_data, roles)
    return archive_ids, roles, full_size, denominators
