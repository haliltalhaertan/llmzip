"""V52 static-storage external binding preflight V5.

Repairs what the independent audit of V4 found. V4 is
drafts/v52/static_storage_plan_prep_v4_2026_09_12 at 81928414eaeb0e442d0750a56fd268025bc05722;
its bytes are not rewritten, and neither are V3's at 3fab24bce46203348935492ba8276b9920aea898.

That audit returned REQUEST_CHANGES on two claims V4 listed as repaired, and this
session reproduced both before accepting them:
  - a lone UTF-16 surrogate in a locator escaped as UnicodeEncodeError, not
    PreflightError, because Path.resolve() raises a ValueError that the OSError-only
    except in safe_child did not catch;
  - the guard binding was opt-in and defaulted off, so guarding plan A and preflighting
    plan B was still accepted, and the contract digest was compared as a bare string
    that no file on disk had to match.
Also repaired: the array bound diverged from the parent guard in the opposite direction
to V3's, the read loop concatenated immutable bytes quadratically, fixtures were not
deduplicated by inode, and an empty physical-copy roster was accepted.

Preparation-only. Authenticates declarations and synthetic/source bytes. Authorizes no
storage measurement, model fitting, retrieval or Task4F1 access.

Carried from V4: AUD-002, AUD-003, AUD-005, AUD-006, AUD-010, AUD-011.
Repaired here: AUD-009 completed, AUD-007 made mandatory and actually authenticated,
AUD-004 aligned on both bounds, plus the four defects the V4 audit found new.

NOT repaired here, because they belong to the plan guard and the plan schema: AUD-001
(no external anchor for N_i) and AUD-008 (denominator rule yields a menu). This module
therefore still refuses to select a denominator; it reports states only. Those two are
closed separately by drafts/v52/static_storage_anchor_guard_2026_09_12, which must run
alongside this preflight; nothing here enforces that it did.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib, json, math, os, re, stat
from pathlib import Path

MAX_DECLARATION_BYTES = 1_048_576
MAX_ARTIFACT_BYTES = 64 * 1024 * 1024
MAX_TOTAL_ARTIFACT_BYTES = 256 * 1024 * 1024   # AUD-005 family: aggregate budget
MAX_ENTITIES = 1024          # parent guard's object bound
MAX_ARRAY_ENTRIES = 4096     # parent guard's array bound; V4 wrongly used 1024 for both
MAX_DEPTH = 24
FIXTURE_BINDING_SCHEMA = "v52.fixture-bindings"
PHYSICAL_BINDING_SCHEMA = "v52.physical-copy-bindings"
PHYSICAL_BINDING_VERSION = 4   # V4 added absence_basis at version 3; that collision is fixed here
FIXTURE_CONTENT_SCHEMA = "V52_SYNTHETIC_FIXTURE_BUNDLE_V3"
CONSUMER_SECTIONS = {"TRANSFORM": "transform", "ID_MAPPING": "id_mapping", "CORRUPT": "corruption"}


class PreflightError(ValueError):
    """Every refusal raised by this module. AUD-009: nothing else may escape."""


def need(c, m):
    if not c:
        raise PreflightError(m)


def fields(v, n, w):
    need(type(v) is dict and set(v) == set(n.split()), f"{w}: exact fields required: {n}")


def text(v, w):
    need(type(v) is str and bool(v.strip()) and len(v) <= 4096, f"{w}: nonblank bounded string required")


def integer(v, w, minimum=0, maximum=2**63 - 1):
    # type(v) is int excludes bool, which is a subclass of int.
    need(type(v) is int and minimum <= v <= maximum, f"{w}: integer in [{minimum},{maximum}] required")


def digest(v, w):
    need(type(v) is str and re.fullmatch(r"[0-9a-f]{64}", v) is not None, f"{w}: lowercase SHA256 required")


def exact_version(v, expected, w):
    """AUD-010: bare equality accepts True and 1.0. Require the int type as well."""
    integer(v, w, 1)
    need(v == expected, f"{w}: version {expected} required")


def _pairs(pairs):
    out = {}
    for k, v in pairs:
        need(k not in out, f"duplicate JSON key: {k}")
        out[k] = v
    return out


def _bounded(v, d=0):
    need(d <= MAX_DEPTH, "JSON nesting limit")
    if type(v) is dict:
        need(len(v) <= MAX_ENTITIES, "JSON object limit")
        for k, x in v.items():
            text(k, "JSON key")
            _bounded(x, d + 1)
    elif type(v) is list:
        need(len(v) <= MAX_ARRAY_ENTRIES, "JSON array limit")
        for x in v:
            _bounded(x, d + 1)
    elif type(v) is str:
        need(len(v) <= 4096, "JSON string limit")
    elif v is None or type(v) is bool:
        return
    elif type(v) in (int, float):
        need(math.isfinite(v) and abs(v) <= 2**63 - 1, "numeric limit")
    else:
        raise PreflightError("non-JSON value")


def decode_json(raw, where):
    try:
        v = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_pairs,
            parse_constant=lambda t: (_ for _ in ()).throw(PreflightError(f"{where}: nonfinite JSON constant {t}")),
        )
    except (UnicodeError, ValueError, RecursionError) as e:
        if isinstance(e, PreflightError):
            raise
        raise PreflightError(f"{where}: invalid JSON: {e}") from e
    _bounded(v)
    need(type(v) is dict, f"{where}: object required")
    return v


class _Budget:
    """AUD-005 family: bound the bytes retained across the whole preflight."""

    def __init__(self, limit=MAX_TOTAL_ARTIFACT_BYTES):
        self.limit = limit
        self.used = 0

    def charge(self, n, where):
        self.used += n
        need(self.used <= self.limit, f"{where}: aggregate artifact byte budget exceeded")


def read_bytes(path, limit, where, budget=None):
    """AUD-006: never block on a non-regular file.

    The handle is opened O_NOFOLLOW|O_NONBLOCK and fstat'ed, so the file that is
    actually read is the file that was checked, and a FIFO is refused rather than
    blocking. Every OSError and ValueError becomes a PreflightError.

    O_NOFOLLOW applies to the final component of the path as given. Artifact locators
    reach here already resolved by safe_child, which follows symlinks and then requires
    the result to stay under the binding directory, so a symlink to a regular file
    inside the directory is accepted by design. V4's docstring claimed this call never
    follows a symlink; that was false for artifacts and is corrected here.
    """
    try:
        fd = os.open(str(path), os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | getattr(os, "O_CLOEXEC", 0))
    except OSError as e:
        raise PreflightError(f"{where}: cannot open artifact: {e.__class__.__name__}") from e
    except ValueError as e:                                  # embedded NUL, etc.
        raise PreflightError(f"{where}: invalid path: {e}") from e
    try:
        st = os.fstat(fd)
        need(stat.S_ISREG(st.st_mode), f"{where}: artifact must be a regular file")
        need(st.st_size <= limit, f"{where}: file byte limit")
        chunks, total = [], 0
        while True:
            try:
                chunk = os.read(fd, 1 << 20)
            except OSError as e:
                raise PreflightError(f"{where}: read failed: {e.__class__.__name__}") from e
            if not chunk:
                break
            total += len(chunk)
            need(total <= limit, f"{where}: file byte limit")
            chunks.append(chunk)
        raw = b"".join(chunks)
    finally:
        os.close(fd)
    if budget is not None:
        budget.charge(len(raw), where)
    return raw


def authenticate(path, expected, where, artifact=False, budget=None):
    digest(expected, f"{where} expected SHA256")
    raw = read_bytes(path, MAX_ARTIFACT_BYTES if artifact else MAX_DECLARATION_BYTES, where, budget)
    need(hashlib.sha256(raw).hexdigest() == expected, f"{where}: SHA256 mismatch")
    return raw


def safe_child(base_dir, relative_path, where):
    text(relative_path, where)
    need("\x00" not in relative_path, f"{where}: path must not contain NUL")
    rel = Path(relative_path)
    need(not rel.is_absolute() and ".." not in rel.parts, f"{where}: path must stay below binding directory")
    need(rel.parts and rel.parts != (".",), f"{where}: path must name a file, not the directory itself")
    try:
        base = Path(base_dir).resolve()
        child = (base / rel).resolve()
    except (OSError, ValueError) as e:
        # ValueError covers UnicodeEncodeError from a lone surrogate, which realpath
        # raises while encoding for the filesystem. The V4 audit found this live.
        raise PreflightError(f"{where}: cannot resolve path: {e.__class__.__name__}") from e
    try:
        child.relative_to(base)
    except ValueError as e:
        raise PreflightError(f"{where}: path escapes binding directory") from e
    return child


def unique_index(rows, where, id_key="id", required=()):
    need(type(rows) is list, f"{where}: list required")
    out = {}
    for row in rows:
        need(type(row) is dict, f"{where}: object required")
        for key in (id_key,) + tuple(required):
            need(key in row, f"{where}: missing field {key}")       # AUD-003/009: never KeyError
        key = row[id_key]
        text(key, f"{where} {id_key}")
        need(key not in out, f"{where}: duplicate id {key}")
        out[key] = row
    return out


def validate_fixture_payload(p, artifact_length):
    fields(p, "schema transform id_mapping corruption", "fixture artifact")
    need(p["schema"] == FIXTURE_CONTENT_SCHEMA, "fixture artifact schema mismatch")
    fields(p["transform"], "input_utf8", "fixture transform")
    text(p["transform"]["input_utf8"], "transform input_utf8")
    fields(p["id_mapping"], "rows", "fixture id_mapping")
    rows = p["id_mapping"]["rows"]
    need(type(rows) is list and 2 <= len(rows) <= MAX_ENTITIES, "id_mapping rows: at least two rows required")
    ids, offsets = [], []
    for row in rows:
        fields(row, "logical_id offset payload_utf8", "id_mapping row")
        text(row["logical_id"], "id_mapping logical_id")
        integer(row["offset"], "id_mapping offset")
        text(row["payload_utf8"], "id_mapping payload_utf8")
        ids.append(row["logical_id"])
        offsets.append(row["offset"])
    need(len(ids) == len(set(ids)), "id_mapping logical_ids must be unique")
    need(len(offsets) == len(set(offsets)), "id_mapping offsets must be unique")
    fields(p["corruption"], "strategy byte_offset xor_mask", "fixture corruption")
    need(p["corruption"]["strategy"] == "XOR_SINGLE_BYTE", "corruption strategy")
    # AUD-002: an offset past the artifact makes the CORRUPT control a no-op.
    integer(p["corruption"]["byte_offset"], "corruption byte_offset", 0, max(artifact_length - 1, 0))
    integer(p["corruption"]["xor_mask"], "corruption xor_mask", 1, 255)


@dataclass(frozen=True)
class VerifiedFixture:
    fixture_id: str
    raw_bytes: bytes
    sha256: str
    byte_length: int

    def reverify(self):
        """AUD-001 closure caveat: frozen blocks rebinding only. Re-check on use."""
        need(hashlib.sha256(self.raw_bytes).hexdigest() == self.sha256,
             f"fixture {self.fixture_id}: authenticated bytes no longer match their digest")
        return self.raw_bytes


@dataclass(frozen=True)
class VerifiedPhysicalCopy:
    physical_copy_id: str
    raw_bytes: bytes
    sha256: str
    source_byte_length: int
    denominator_states: tuple

    def reverify(self):
        need(hashlib.sha256(self.raw_bytes).hexdigest() == self.sha256,
             f"physical copy {self.physical_copy_id}: authenticated bytes no longer match their digest")
        return self.raw_bytes


@dataclass(frozen=True)
class VerifiedBindings:
    plan_sha256: str
    contract_sha256: str
    fixture_bindings_sha256: str
    physical_bindings_sha256: str
    fixtures: tuple
    physical_copies: tuple


def _claim_inode(artifact, owner, seen_inodes, where):
    """AUD-011: one file on disk may back at most one declared artifact.

    V4 deduplicated physical copies only. The same argument applies to fixtures and to a
    fixture sharing a file with a physical copy, so one map covers all of them.
    """
    try:
        st = os.stat(str(artifact), follow_symlinks=False)
    except (OSError, ValueError) as e:
        raise PreflightError(f"{where}: cannot stat artifact: {e.__class__.__name__}") from e
    identity = (st.st_dev, st.st_ino)
    if identity in seen_inodes:
        raise PreflightError(
            f"{owner}: distinct declared artifacts must not resolve to one file "
            f"(already bound by {seen_inodes[identity]})")
    seen_inodes[identity] = owner


def verify_fixture_artifact(binding_dir, plan_fixture, binding, seen_inodes, budget):
    fields(binding, "fixture_id relative_path byte_length sha256 content_schema consumer_sections",
           "fixture binding")
    need(binding["fixture_id"] == plan_fixture["id"], "fixture id mismatch")
    integer(binding["byte_length"], "fixture byte_length", 1)
    digest(binding["sha256"], "fixture binding SHA256")
    digest(plan_fixture["sha256"], "plan fixture SHA256")
    need(binding["sha256"] == plan_fixture["sha256"], "fixture SHA disagrees with plan")
    need(binding["content_schema"] == FIXTURE_CONTENT_SCHEMA, "fixture content schema mismatch")
    fields(binding["consumer_sections"], "TRANSFORM ID_MAPPING CORRUPT", "fixture consumer_sections")
    need(binding["consumer_sections"] == CONSUMER_SECTIONS, "fixture consumer/subfixture mapping mismatch")
    artifact = safe_child(binding_dir, binding["relative_path"], "fixture relative_path")
    _claim_inode(artifact, f"fixture {plan_fixture['id']}", seen_inodes, "fixture relative_path")
    raw = read_bytes(artifact, MAX_ARTIFACT_BYTES, "fixture artifact", budget)
    need(len(raw) == binding["byte_length"], "fixture byte length mismatch")
    need(hashlib.sha256(raw).hexdigest() == binding["sha256"], "fixture artifact SHA mismatch")
    validate_fixture_payload(decode_json(raw, "fixture artifact"), len(raw))
    return VerifiedFixture(plan_fixture["id"], raw, binding["sha256"], len(raw))


def verify_physical_artifact(binding_dir, plan_copy, binding, populations, seen_inodes, budget):
    fields(binding, "physical_copy_id physical_locator source_raw_byte_length artifact_sha256 "
                    "sharing_denominator_rule absence_basis", "physical binding")
    need(binding["physical_copy_id"] == plan_copy["id"], "physical copy id mismatch")
    integer(binding["source_raw_byte_length"], "source raw byte length", 0)
    digest(binding["artifact_sha256"], "physical artifact SHA256")
    digest(plan_copy["artifact_sha256"], "plan physical copy SHA256")
    need(binding["artifact_sha256"] == plan_copy["artifact_sha256"], "physical binding SHA disagrees with plan")
    need(binding["sharing_denominator_rule"] == "POPULATION_COUNT", "unsupported sharing denominator rule")

    artifact = safe_child(binding_dir, binding["physical_locator"], "physical locator")

    # AUD-011: two declared artifacts must not resolve to one file on disk.
    _claim_inode(artifact, f"physical copy {plan_copy['id']}", seen_inodes, "physical locator")

    raw = read_bytes(artifact, MAX_ARTIFACT_BYTES, "physical artifact", budget)
    need(len(raw) == binding["source_raw_byte_length"], "physical source length mismatch")
    need(hashlib.sha256(raw).hexdigest() == binding["artifact_sha256"], "physical source SHA mismatch")

    # AUD-005: a zero-byte artifact needs stated evidence that no requirement exists.
    if len(raw) == 0:
        need(type(binding["absence_basis"]) is str and binding["absence_basis"].strip()
             and binding["absence_basis"] != "UNKNOWN",
             "zero-byte artifact requires a stated absence basis")
        text(binding["absence_basis"], "physical absence_basis")
    else:
        need(binding["absence_basis"] is None, "non-empty artifact must carry a null absence_basis")

    need(type(plan_copy["population_ids"]) is list, "plan copy population_ids: list required")
    states = []
    for pop_id in plan_copy["population_ids"]:
        text(pop_id, "population id")
        need(pop_id in populations, f"unknown population {pop_id}")
        count = populations[pop_id]["count"]
        integer(count, f"population {pop_id} count")
        states.append((pop_id, "EMPTY_NO_AMORTIZATION", None) if count == 0 else (pop_id, "POSITIVE", count))
    return VerifiedPhysicalCopy(plan_copy["id"], raw, binding["artifact_sha256"], len(raw), tuple(states))


def preflight(plan_path, expected_plan_sha256,
              contract_path, expected_contract_sha256,
              fixture_bindings_path, expected_fixture_bindings_sha256,
              physical_bindings_path, expected_physical_bindings_sha256,
              guarded_plan_sha256, guarded_contract_sha256):
    """Every argument is REQUIRED. AUD-007 was opt-in in V4 and defaulted off.

    `guarded_plan_sha256` and `guarded_contract_sha256` are what
    `measurement_plan_guard.load_plan` returned. There is no way to skip the comparison,
    so guarding plan A and preflighting plan B is a refusal rather than a silent
    divergence.

    `contract_path` is READ AND HASHED here, the way the parent guard reads it. V4 took
    the contract digest as a bare string that no file had to match, so its
    `VerifiedBindings.contract_sha256` recorded a declaration rather than an
    authentication. The chain enforced now is:

        bytes at contract_path  ==  expected_contract_sha256
                                ==  plan["contract_sha256"]
                                ==  guarded_contract_sha256

    and likewise the plan's own bytes against both the expected and the guarded digest.
    """
    budget = _Budget()
    digest(expected_contract_sha256, "expected contract SHA256")
    digest(guarded_plan_sha256, "guarded plan SHA256")
    digest(guarded_contract_sha256, "guarded contract SHA256")
    need(guarded_plan_sha256 == expected_plan_sha256,
         "guarded plan digest does not match the plan being preflighted")
    need(guarded_contract_sha256 == expected_contract_sha256,
         "guarded contract digest does not match the contract being preflighted")

    # The contract is authenticated from its own bytes, not asserted.
    authenticate(contract_path, expected_contract_sha256, "contract", budget=budget)

    plan = decode_json(authenticate(plan_path, expected_plan_sha256, "plan", budget=budget), "plan")
    need(plan.get("schema") == "v52.static-storage-plan", "schema-1 plan required")
    exact_version(plan.get("version"), 1, "plan version")
    # AUD-007: the plan must name the same contract the caller declared.
    need("contract_sha256" in plan, "plan: missing field contract_sha256")
    digest(plan["contract_sha256"], "plan contract_sha256")
    need(plan["contract_sha256"] == expected_contract_sha256,
         "plan contract digest does not match the expected contract")

    plan_fixtures = unique_index(plan.get("fixtures"), "plan fixtures", required=("sha256",))
    plan_copies = unique_index(plan.get("physical_copies"), "plan physical copies",
                               required=("artifact_sha256", "population_ids"))
    populations = unique_index(plan.get("populations"), "plan populations", required=("count",))
    need(plan_fixtures, "plan fixtures: at least one required")
    need(populations, "plan populations: at least one required")
    need(plan_copies, "plan physical copies: at least one required")

    fdoc = decode_json(authenticate(fixture_bindings_path, expected_fixture_bindings_sha256,
                                    "fixture bindings", budget=budget), "fixture bindings")
    fields(fdoc, "schema version fixtures", "fixture bindings")
    need(fdoc["schema"] == FIXTURE_BINDING_SCHEMA, "fixture bindings schema")
    exact_version(fdoc["version"], 3, "fixture bindings version")
    fixture_bindings = unique_index(fdoc["fixtures"], "fixture bindings", "fixture_id")
    need(set(fixture_bindings) == set(plan_fixtures), "fixture binding coverage must equal plan fixture roster")

    pdoc = decode_json(authenticate(physical_bindings_path, expected_physical_bindings_sha256,
                                    "physical bindings", budget=budget), "physical bindings")
    fields(pdoc, "schema version physical_copies", "physical bindings")
    need(pdoc["schema"] == PHYSICAL_BINDING_SCHEMA, "physical bindings schema")
    exact_version(pdoc["version"], PHYSICAL_BINDING_VERSION, "physical bindings version")
    physical_bindings = unique_index(pdoc["physical_copies"], "physical bindings", "physical_copy_id")
    need(set(physical_bindings) == set(plan_copies), "physical binding coverage must equal plan physical-copy roster")

    fdir = Path(fixture_bindings_path).resolve().parent
    pdir = Path(physical_bindings_path).resolve().parent
    seen_inodes = {}
    vf = tuple(verify_fixture_artifact(fdir, plan_fixtures[i], fixture_bindings[i],
                                       seen_inodes, budget)
               for i in plan_fixtures)
    vc = tuple(verify_physical_artifact(pdir, plan_copies[i], physical_bindings[i], populations,
                                        seen_inodes, budget)
               for i in plan_copies)
    return VerifiedBindings(expected_plan_sha256, expected_contract_sha256,
                            expected_fixture_bindings_sha256, expected_physical_bindings_sha256, vf, vc)
