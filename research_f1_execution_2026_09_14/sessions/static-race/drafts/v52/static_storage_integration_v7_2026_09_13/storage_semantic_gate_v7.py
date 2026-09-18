"""V52 static-storage V7 semantic-anchor integration.

Preparation-only. This module does not measure storage, fit models, score retrieval,
authorize runs, or access Task4F1 outcomes.

V7 closes four remaining semantic/binding holes after V6:
1) LongMemEval anchor columns are fixed in code (`question_id`, `N_archive`);
2) the anchor digest is fixed in code and cannot be supplied by the plan/caller;
3) the authoritative BEFORE population count must equal anchored N_i;
4) the public entry point itself loads the independently reviewed parent Plan object
   from pinned guard bytes, then derives the anchor and only then calls pinned V6.

This V7 entry point is LongMemEval-only. LoCoMo requires its own independently
reviewed anchor profile/parser rather than reusing this CSV contract by analogy.
"""
from __future__ import annotations

from dataclasses import dataclass
import csv
import hashlib
import io
import os
from pathlib import Path
import stat
import sys
import importlib

MAX_SOURCE_BYTES = 64 * 1024 * 1024
MAX_ROWS = 100_000

PARENT_GUARD_SHA256 = "19724919c9085e49a531e94bdb269cba96c81739f7d9449b717db982becde4c9"
CONTRACT_SHA256 = "e395451d026f176b875856244abe73b54a7d54cdf2649eec272f14cfc609c510"
V6_PREFLIGHT_SHA256 = "eb7165bcbe633c0a9d233e3b7167fb67590ca8b8db6076d6b205a6e1c7648b75"

LONGMEMEVAL_ANCHOR_SHA256 = "d4c9ce62b0f1b66611611bb014a887d2e7e5fcfaee0af94f53ffb70dc84d7d32"
LONGMEMEVAL_ID_COLUMN = "question_id"
LONGMEMEVAL_VALUE_COLUMN = "N_archive"
LONGMEMEVAL_EXPECTED_ROWS = 470
LONGMEMEVAL_SOURCE_IDENTITY = (
    "5ec3db60c03edde490374bf9cd7c3e56dd6bcd00:"
    "docs/v52/task4c2/V52_T4C2_feature_geometry.csv"
)

def _discover_repo_root():
    env = os.environ.get("LLMZIP_REPO")
    if env:
        candidate = Path(env).resolve()
        if (candidate / "drafts/v52/static_storage_contract_2026_09_12").is_dir():
            return candidate
    here = Path(__file__).resolve()
    for candidate in (here.parent, *here.parents):
        if (candidate / "drafts/v52/static_storage_contract_2026_09_12").is_dir():
            return candidate
    return here.parent


_REPO_ROOT = _discover_repo_root()
_PARENT_GUARD_PATH = _REPO_ROOT / "drafts/v52/static_storage_contract_2026_09_12/measurement_plan_guard.py"
_CONTRACT_PATH = _REPO_ROOT / "drafts/v52/static_storage_contract_2026_09_12/MEASUREMENT_CONTRACT_TR.md"
_V6_PATH = _REPO_ROOT / "drafts/v52/static_storage_integration_v6_2026_09_12/storage_adapter_preflight_v6.py"
_LONGMEMEVAL_ANCHOR_PATH = _REPO_ROOT / "docs/v52/task4c2/V52_T4C2_feature_geometry.csv"

_O_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
_O_NONBLOCK = getattr(os, "O_NONBLOCK", 0)
_O_CLOEXEC = getattr(os, "O_CLOEXEC", 0)
_O_BINARY = getattr(os, "O_BINARY", 0)


class V7ValidationError(ValueError):
    """Any V7 refusal. Callers must stop preparation/measurement."""


def _need(condition, message):
    if not condition:
        raise V7ValidationError(message)


def _digest(value, where):
    _need(
        type(value) is str
        and len(value) == 64
        and all(c in "0123456789abcdef" for c in value),
        f"{where}: lowercase SHA256 required",
    )


def _read_regular(path, limit, where):
    """Read one regular file without following a final-component symlink."""
    path = Path(path)
    try:
        pre = os.stat(str(path), follow_symlinks=False)
    except (OSError, ValueError) as exc:
        raise V7ValidationError(
            f"{where}: cannot stat source: {exc.__class__.__name__}"
        ) from exc
    _need(stat.S_ISREG(pre.st_mode), f"{where}: source must be a regular file")
    _need(pre.st_size <= limit, f"{where}: source byte limit")

    try:
        fd = os.open(
            str(path),
            os.O_RDONLY | _O_NOFOLLOW | _O_NONBLOCK | _O_CLOEXEC | _O_BINARY,
        )
    except (OSError, ValueError) as exc:
        raise V7ValidationError(
            f"{where}: cannot open source: {exc.__class__.__name__}"
        ) from exc
    try:
        post = os.fstat(fd)
        _need(stat.S_ISREG(post.st_mode), f"{where}: opened source is not regular")
        _need(
            (post.st_dev, post.st_ino) == (pre.st_dev, pre.st_ino),
            f"{where}: source changed identity between stat and open",
        )
        chunks = []
        total = 0
        while True:
            chunk = os.read(fd, 1 << 20)
            if not chunk:
                break
            total += len(chunk)
            _need(total <= limit, f"{where}: source byte limit")
            chunks.append(chunk)
        return b"".join(chunks)
    except OSError as exc:
        raise V7ValidationError(
            f"{where}: source read failed: {exc.__class__.__name__}"
        ) from exc
    finally:
        os.close(fd)


def _authenticate_fixed(path, expected_sha256, where, limit=MAX_SOURCE_BYTES):
    _digest(expected_sha256, f"{where} expected SHA256")
    raw = _read_regular(path, limit, where)
    actual = hashlib.sha256(raw).hexdigest()
    _need(actual == expected_sha256, f"{where}: SHA256 mismatch")
    return raw


def _import_pinned_module(module_name, module_path, expected_sha256):
    """Import one fixed repo module after authenticating its source file.

    V7 refuses a pre-existing module of the same name if it came from another path.
    The source is re-authenticated after import as well.
    """
    _authenticate_fixed(module_path, expected_sha256, f"{module_name} source")
    expected_path = Path(module_path).resolve()
    existing = sys.modules.get(module_name)
    if existing is not None:
        actual_file = getattr(existing, "__file__", None)
        _need(actual_file is not None, f"{module_name}: preloaded module has no file identity")
        _need(
            Path(actual_file).resolve() == expected_path,
            f"{module_name}: preloaded module came from an unexpected path",
        )
        _authenticate_fixed(expected_path, expected_sha256, f"{module_name} source post-import")
        return existing

    module_dir = str(expected_path.parent)
    inserted = False
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)
        inserted = True
    try:
        module = importlib.import_module(module_name)
    finally:
        if inserted:
            try:
                sys.path.remove(module_dir)
            except ValueError:
                pass

    actual_file = getattr(module, "__file__", None)
    _need(actual_file is not None, f"{module_name}: imported module has no file identity")
    _need(
        Path(actual_file).resolve() == expected_path,
        f"{module_name}: imported module path mismatch",
    )
    _authenticate_fixed(expected_path, expected_sha256, f"{module_name} source post-import")
    return module


@dataclass(frozen=True)
class LongMemEvalAnchor:
    sha256: str
    source_identity: str
    sizes: tuple

    def as_map(self):
        return dict(self.sizes)

    def reverify(self):
        raw = _authenticate_fixed(
            _LONGMEMEVAL_ANCHOR_PATH,
            LONGMEMEVAL_ANCHOR_SHA256,
            "LongMemEval anchor",
        )
        return hashlib.sha256(raw).hexdigest() == self.sha256


@dataclass(frozen=True)
class V7AnchorProof:
    anchor_sha256: str
    source_identity: str
    archive_ids: tuple
    authoritative_probe_ids: tuple
    denominators: tuple

    def denominator_map(self):
        return {
            copy_id: (population_id, d_k)
            for copy_id, population_id, d_k in self.denominators
        }


@dataclass(frozen=True)
class V7VerifiedContext:
    guarded_plan: object
    anchor: LongMemEvalAnchor
    anchor_proof: V7AnchorProof
    verified_bindings: object

    def reverify(self):
        raw = getattr(self.guarded_plan, "raw", None)
        plan_sha = getattr(self.guarded_plan, "sha256", None)
        _need(type(raw) is bytes, "guarded Plan raw bytes unavailable")
        _need(type(plan_sha) is str, "guarded Plan SHA256 unavailable")
        _need(hashlib.sha256(raw).hexdigest() == plan_sha, "guarded Plan bytes no longer match its digest")
        _need(
            getattr(self.guarded_plan, "contract_sha256", None) == CONTRACT_SHA256,
            "guarded Plan contract digest no longer matches V7",
        )
        _ = self.guarded_plan.data
        _need(self.anchor.reverify(), "LongMemEval anchor reverify failed")
        for fixture in self.verified_bindings.fixtures:
            fixture.reverify()
        for physical in self.verified_bindings.physical_copies:
            physical.reverify()
        return True


def _parse_longmemeval_anchor(raw):
    _need(type(raw) is bytes, "LongMemEval anchor must be bytes")
    actual = hashlib.sha256(raw).hexdigest()
    _need(
        actual == LONGMEMEVAL_ANCHOR_SHA256,
        "LongMemEval anchor bytes do not match the pinned digest",
    )
    try:
        text = raw.decode("utf-8")
    except UnicodeError as exc:
        raise V7ValidationError("LongMemEval anchor is not UTF-8") from exc

    reader = csv.reader(io.StringIO(text, newline=""))
    try:
        header = next(reader)
    except StopIteration as exc:
        raise V7ValidationError("LongMemEval anchor is empty") from exc

    _need(header and len(header) == len(set(header)), "LongMemEval anchor header must be unique")
    _need(LONGMEMEVAL_ID_COLUMN in header, "LongMemEval anchor missing question_id")
    _need(LONGMEMEVAL_VALUE_COLUMN in header, "LongMemEval anchor missing N_archive")
    id_idx = header.index(LONGMEMEVAL_ID_COLUMN)
    value_idx = header.index(LONGMEMEVAL_VALUE_COLUMN)

    rows = []
    seen = set()
    for line_no, row in enumerate(reader, start=2):
        _need(len(rows) < MAX_ROWS, "LongMemEval anchor row limit")
        _need(len(row) == len(header), f"LongMemEval anchor line {line_no}: column-count mismatch")
        archive_id = row[id_idx].strip()
        raw_n = row[value_idx].strip()
        _need(archive_id, f"LongMemEval anchor line {line_no}: blank question_id")
        _need(archive_id not in seen, f"LongMemEval anchor line {line_no}: duplicate question_id")
        _need(raw_n.isdecimal(), f"LongMemEval anchor line {line_no}: N_archive must be decimal")
        n_i = int(raw_n)
        _need(n_i >= 1, f"LongMemEval anchor line {line_no}: N_archive must be positive")
        seen.add(archive_id)
        rows.append((archive_id, n_i))

    _need(
        len(rows) == LONGMEMEVAL_EXPECTED_ROWS,
        f"LongMemEval anchor must contain exactly {LONGMEMEVAL_EXPECTED_ROWS} data rows",
    )
    return LongMemEvalAnchor(
        LONGMEMEVAL_ANCHOR_SHA256,
        LONGMEMEVAL_SOURCE_IDENTITY,
        tuple(rows),
    )


def load_longmemeval_anchor():
    raw = _authenticate_fixed(
        _LONGMEMEVAL_ANCHOR_PATH,
        LONGMEMEVAL_ANCHOR_SHA256,
        "LongMemEval anchor",
    )
    return _parse_longmemeval_anchor(raw)


def _verify_plan_data_against_anchor(plan_data, anchor):
    """Derive the only legal LongMemEval amortization denominators."""
    _need(type(plan_data) is dict, "guarded plan data must be an object")
    archives = plan_data.get("archives")
    probes = plan_data.get("probes")
    populations = plan_data.get("populations")
    copies = plan_data.get("physical_copies")
    _need(type(archives) is list, "plan archives must be a list")
    _need(type(probes) is list, "plan probes must be a list")
    _need(type(populations) is list, "plan populations must be a list")
    _need(type(copies) is list and copies, "plan physical_copies must be a non-empty list")

    expected_ids = tuple(aid for aid, _ in anchor.sizes)
    expected_map = anchor.as_map()
    actual_ids = []
    archive_map = {}
    for row in archives:
        _need(type(row) is dict and set(row) == {"id", "N_i"}, "plan archive exact fields required")
        aid = row["id"]
        n_i = row["N_i"]
        _need(type(aid) is str and aid, "plan archive id required")
        _need(type(n_i) is int and not isinstance(n_i, bool), f"archive {aid}: integer N_i required")
        _need(aid in expected_map, f"archive {aid}: not present in pinned LongMemEval anchor")
        _need(n_i == expected_map[aid], f"archive {aid}: N_i disagrees with pinned LongMemEval anchor")
        _need(aid not in archive_map, f"archive {aid}: duplicate plan archive")
        actual_ids.append(aid)
        archive_map[aid] = n_i
    _need(
        tuple(actual_ids) == expected_ids,
        "plan archive roster/order must exactly equal the pinned 470-row LongMemEval anchor",
    )

    probe_by_id = {}
    authoritative = {}
    for probe in probes:
        _need(type(probe) is dict, "probe object required")
        for key in ("id", "archive_id", "N", "q"):
            _need(key in probe, f"probe: missing field {key}")
        pid = probe["id"]
        aid = probe["archive_id"]
        _need(type(pid) is str and pid, "probe id required")
        _need(pid not in probe_by_id, f"duplicate probe id {pid}")
        _need(aid in archive_map, f"probe {pid}: unknown archive {aid}")
        _need(type(probe["N"]) is int and not isinstance(probe["N"], bool), f"probe {pid}: integer N required")
        _need(type(probe["q"]) is int and not isinstance(probe["q"], bool) and probe["q"] >= 1,
              f"probe {pid}: positive integer q required")
        probe_by_id[pid] = probe
        if probe["N"] == archive_map[aid] and probe["q"] == 1:
            _need(aid not in authoritative, f"archive {aid}: multiple authoritative (N_i,q=1) probes")
            authoritative[aid] = pid

    _need(
        set(authoritative) == set(archive_map),
        "every LongMemEval archive requires exactly one authoritative (N_i,q=1) probe",
    )

    population_by_id = {}
    for pop in populations:
        _need(type(pop) is dict, "population object required")
        for key in ("id", "archive_id", "probe_id", "phase", "count"):
            _need(key in pop, f"population: missing field {key}")
        pop_id = pop["id"]
        _need(type(pop_id) is str and pop_id, "population id required")
        _need(pop_id not in population_by_id, f"duplicate population id {pop_id}")
        _need(pop["archive_id"] in archive_map, f"population {pop_id}: unknown archive")
        _need(pop["probe_id"] in probe_by_id, f"population {pop_id}: unknown probe")
        _need(
            probe_by_id[pop["probe_id"]]["archive_id"] == pop["archive_id"],
            f"population {pop_id}: probe/archive mismatch",
        )
        _need(pop["phase"] in ("BEFORE", "AFTER"), f"population {pop_id}: invalid phase")
        _need(type(pop["count"]) is int and not isinstance(pop["count"], bool) and pop["count"] >= 0,
              f"population {pop_id}: nonnegative integer count required")
        population_by_id[pop_id] = pop

    denominators = []
    seen_copy_ids = set()
    for copy in copies:
        _need(type(copy) is dict, "physical copy object required")
        for key in ("id", "archive_id", "population_ids"):
            _need(key in copy, f"physical copy: missing field {key}")
        copy_id = copy["id"]
        aid = copy["archive_id"]
        _need(type(copy_id) is str and copy_id, "physical copy id required")
        _need(copy_id not in seen_copy_ids, f"duplicate physical copy id {copy_id}")
        seen_copy_ids.add(copy_id)
        _need(aid in archive_map, f"physical copy {copy_id}: unknown archive {aid}")
        pop_ids = copy["population_ids"]
        _need(type(pop_ids) is list, f"physical copy {copy_id}: population_ids list required")
        _need(len(pop_ids) == len(set(pop_ids)), f"physical copy {copy_id}: duplicate population id")

        auth_probe = authoritative[aid]
        eligible = []
        for pop_id in pop_ids:
            _need(pop_id in population_by_id, f"physical copy {copy_id}: unknown population {pop_id}")
            pop = population_by_id[pop_id]
            _need(pop["archive_id"] == aid, f"physical copy {copy_id}: cross-archive population")
            if pop["probe_id"] == auth_probe and pop["phase"] == "BEFORE":
                eligible.append(pop)

        _need(
            len(eligible) == 1,
            f"physical copy {copy_id}: exactly one authoritative q=1 BEFORE population required",
        )
        pop = eligible[0]
        anchored_n = expected_map[aid]
        _need(
            pop["count"] == anchored_n,
            f"physical copy {copy_id}: authoritative population count {pop['count']} "
            f"must equal pinned N_i {anchored_n}",
        )
        denominators.append((copy_id, pop["id"], anchored_n))

    return V7AnchorProof(
        anchor.sha256,
        anchor.source_identity,
        expected_ids,
        tuple((aid, authoritative[aid]) for aid in expected_ids),
        tuple(denominators),
    )


def _load_dependencies():
    guard = _import_pinned_module(
        "measurement_plan_guard",
        _PARENT_GUARD_PATH,
        PARENT_GUARD_SHA256,
    )
    v6 = _import_pinned_module(
        "storage_adapter_preflight_v6",
        _V6_PATH,
        V6_PREFLIGHT_SHA256,
    )
    _authenticate_fixed(_CONTRACT_PATH, CONTRACT_SHA256, "measurement contract")
    return guard, v6


def preflight_longmemeval_v7(
    plan_path,
    expected_plan_sha256,
    fixture_bindings_path,
    expected_fixture_bindings_sha256,
    physical_bindings_path,
    expected_physical_bindings_sha256,
):
    """Single V7 entry point. Returns preparation evidence, not authorization."""
    _digest(expected_plan_sha256, "expected plan SHA256")
    _digest(expected_fixture_bindings_sha256, "expected fixture bindings SHA256")
    _digest(expected_physical_bindings_sha256, "expected physical bindings SHA256")

    guard, v6 = _load_dependencies()

    try:
        guarded_plan = guard.load_plan(
            plan_path,
            expected_plan_sha256,
            _CONTRACT_PATH,
        )
    except (guard.PlanValidationError, OSError, ValueError) as exc:
        raise V7ValidationError(
            f"parent measurement-plan guard refused: {exc}"
        ) from exc
    _need(
        type(guarded_plan) is guard.Plan,
        "parent guard did not return its exact Plan type",
    )
    _need(
        guarded_plan.contract_sha256 == CONTRACT_SHA256,
        "guarded Plan contract digest disagrees with the pinned V7 contract",
    )

    anchor = load_longmemeval_anchor()
    proof = _verify_plan_data_against_anchor(guarded_plan.data, anchor)

    try:
        verified_bindings = v6.preflight(
            plan_path,
            guarded_plan.sha256,
            _CONTRACT_PATH,
            guarded_plan.contract_sha256,
            fixture_bindings_path,
            expected_fixture_bindings_sha256,
            physical_bindings_path,
            expected_physical_bindings_sha256,
            guarded_plan.sha256,
            guarded_plan.contract_sha256,
            proof.denominator_map(),
        )
    except (v6.PreflightError, OSError, ValueError) as exc:
        raise V7ValidationError(
            f"pinned V6 preflight refused: {exc}"
        ) from exc

    return V7VerifiedContext(
        guarded_plan,
        anchor,
        proof,
        verified_bindings,
    )
