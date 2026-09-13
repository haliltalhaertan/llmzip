"""V52 static-storage V10 denominator-integrity repair. Preparation-only, LongMemEval-only.

Repair candidate / not independently audited / not frozen / no measurement
authorization. This module does not measure storage, fit models, score
retrieval, authorize runs, or access Task4F1 outcomes.

V9 returns authoritative denominator rows per physical copy as
``(physical_copy_id, population_id, d_k)`` triples with no archive identity.
The plan contract requires physical copies per archive/config/format/item, so
two legitimate physical copies of one archive each carry the same frozen N_i
and a consumer summing the d column counts one logical archive twice
(LongMemEval: 470 logical archives, total N=231606; doubled copy rows naive
sum to 463212, making 12 B/vector for one representation appear as 6).

V10 is additive: it does not modify V7/V8/V9. It executes the pinned V9
consumption chain exactly, resolves each copy row to its archive through the
pinned plan data, cross-checks every copy against the pinned LongMemEval
anchor, and exposes archive-identified rows plus a logical total deduplicated
by archive_id.
"""

from __future__ import annotations

import hashlib
import itertools
import os
from pathlib import Path
import stat
import sys
import types
from typing import NamedTuple

MAX_SOURCE_BYTES = 64 * 1024 * 1024

V9_GATE_SHA256 = "a5c98065c66df4c3ccb114f61d4e4f30f73b99a3a7d6443cddd3e0b092e66dc6"
PARENT_GUARD_SHA256 = "19724919c9085e49a531e94bdb269cba96c81739f7d9449b717db982becde4c9"
CONTRACT_SHA256 = "e395451d026f176b875856244abe73b54a7d54cdf2649eec272f14cfc609c510"
V7_SOURCE_SHA256 = "f7c6749f4648e6fc0f4034dca1823bfe03a2f70429533407217d43cfbbdff4e5"
LONGMEMEVAL_ANCHOR_SHA256 = "d4c9ce62b0f1b66611611bb014a887d2e7e5fcfaee0af94f53ffb70dc84d7d32"
LONGMEMEVAL_EXPECTED_ARCHIVES = 470
LONGMEMEVAL_EXPECTED_TOTAL_N = 231606

REPORT_LABELS = ("[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] "
                 "[NOT FOR CITATION] [DISCLOSE-BEFORE-USE]")

ACCOUNTING_RULE = (
    "V10 accounting rule (LongMemEval-only): the authoritative TOTAL logical "
    "vector denominator is unique-by-archive -- exactly one frozen N_i per "
    "archive_id, summed once. Every physical-copy denominator row must equal "
    "the frozen N_i of its archive; copies of one archive that disagree with "
    "each other or with the frozen N_i reject. Byte numerators are NOT "
    "deduplicated: per-copy/per-representation byte counts remain per-copy, "
    "and V10 offers no byte total, so a one-representation numerator divided "
    "by the logical denominator stays valid while dividing it by a naive "
    "per-copy sum is refused as a labeled error source. Only the logical "
    "vector denominator is unique-by-archive."
)

_O_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
_O_NONBLOCK = getattr(os, "O_NONBLOCK", 0)
_O_CLOEXEC = getattr(os, "O_CLOEXEC", 0)
_O_BINARY = getattr(os, "O_BINARY", 0)
_COUNTER = itertools.count()


class V10ValidationError(ValueError):
    """Any V10 refusal. Callers must stop preparation/measurement."""


def _need(condition, message):
    if not condition:
        raise V10ValidationError(message)


def _digest(value, where):
    _need(type(value) is str and len(value) == 64
          and all(c in "0123456789abcdef" for c in value),
          "%s: lowercase SHA256 required" % where)


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
_V9_GATE_PATH = (_REPO_ROOT
                 / "drafts/v52/static_storage_integration_v9_2026_09_13/consumption_gate_v9.py")
_PARENT_GUARD_PATH = (_REPO_ROOT
                      / "drafts/v52/static_storage_contract_2026_09_12/measurement_plan_guard.py")
_CONTRACT_PATH = (_REPO_ROOT
                  / "drafts/v52/static_storage_contract_2026_09_12/MEASUREMENT_CONTRACT_TR.md")
_V7_GATE_PATH = (_REPO_ROOT
                 / "drafts/v52/static_storage_integration_v7_2026_09_13/storage_semantic_gate_v7.py")


def _read_regular(path, limit, where):
    path = Path(path)
    try:
        pre = os.stat(str(path), follow_symlinks=False)
    except (OSError, ValueError) as exc:
        raise V10ValidationError(
            "%s: cannot stat source: %s" % (where, exc.__class__.__name__)) from exc
    _need(stat.S_ISREG(pre.st_mode), "%s: source must be a regular file" % where)
    _need(pre.st_size <= limit, "%s: source byte limit" % where)
    try:
        fd = os.open(str(path),
                     os.O_RDONLY | _O_NOFOLLOW | _O_NONBLOCK | _O_CLOEXEC | _O_BINARY)
    except (OSError, ValueError) as exc:
        raise V10ValidationError(
            "%s: cannot open source: %s" % (where, exc.__class__.__name__)) from exc
    try:
        post = os.fstat(fd)
        _need(stat.S_ISREG(post.st_mode), "%s: opened source not regular" % where)
        _need((post.st_dev, post.st_ino) == (pre.st_dev, pre.st_ino),
              "%s: source identity changed" % where)
        chunks, total = [], 0
        while True:
            try:
                chunk = os.read(fd, 1 << 20)
            except OSError as exc:
                raise V10ValidationError(
                    "%s: source read failed: %s" % (where, exc.__class__.__name__)) from exc
            if not chunk:
                break
            total += len(chunk)
            _need(total <= limit, "%s: source byte limit" % where)
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(fd)


def _exec_exact(name, path, expected_sha256):
    raw = _read_regular(path, MAX_SOURCE_BYTES, "%s source" % name)
    _need(hashlib.sha256(raw).hexdigest() == expected_sha256,
          "%s: SHA256 mismatch" % name)
    private = "_v52_v10_%s_%d" % (name, next(_COUNTER))
    mod = types.ModuleType(private)
    mod.__file__ = str(Path(path).resolve())
    mod.__package__ = ""
    restore = sys.modules.get(private)
    sys.modules[private] = mod
    try:
        exec(compile(raw, mod.__file__, "exec", dont_inherit=True), mod.__dict__)
    except Exception as exc:
        raise V10ValidationError(
            "%s: exact source execution failed: %s: %s"
            % (name, exc.__class__.__name__, exc)) from exc
    finally:
        if restore is None:
            sys.modules.pop(private, None)
        else:
            sys.modules[private] = restore
    return mod


def _load_v9_exact():
    return _exec_exact("consumption_gate_v9", _V9_GATE_PATH, V9_GATE_SHA256)


def _load_guard_exact():
    return _exec_exact("measurement_plan_guard", _PARENT_GUARD_PATH, PARENT_GUARD_SHA256)


def _load_v7_exact():
    return _exec_exact("storage_semantic_gate_v7", _V7_GATE_PATH, V7_SOURCE_SHA256)


class LogicalDenominatorRow(NamedTuple):
    archive_id: str
    physical_copy_id: str
    population_id: str
    n_i: int


def _check_denominator_shape(denominators, where):
    _need(type(denominators) in (tuple, list) and len(denominators) > 0,
          "%s: non-empty denominator row sequence required" % where)
    clean = []
    for row in denominators:
        _need(type(row) in (tuple, list) and len(row) == 3,
              "%s: (physical_copy_id, population_id, d_k) triple required" % where)
        copy_id, pop_id, d_k = row
        _need(type(copy_id) is str and copy_id.strip(),
              "%s: nonblank physical copy id required" % where)
        _need(type(pop_id) is str and pop_id.strip(),
              "%s: nonblank population id required" % where)
        _need(type(d_k) is int and not isinstance(d_k, bool) and d_k >= 1,
              "%s: positive integer d_k required" % where)
        clean.append((copy_id, pop_id, d_k))
    return tuple(clean)


def enrich_denominator_rows(denominators, copy_to_archive, frozen_n):
    """Attach archive identity to each per-copy row; reject disagreement.

    Every row's d_k must equal the frozen N_i of its archive. Unknown copies,
    copies bound outside the frozen roster, and inconsistent duplicates all
    reject with V10ValidationError -- never silently deduplicated.
    """
    rows = _check_denominator_shape(denominators, "denominators")
    _need(type(copy_to_archive) is dict and copy_to_archive,
          "copy_to_archive map required")
    _need(type(frozen_n) is dict and frozen_n, "frozen archive N_i map required")
    enriched = []
    for copy_id, pop_id, d_k in rows:
        _need(copy_id in copy_to_archive,
              "physical copy %s: unknown archive binding" % copy_id)
        archive_id = copy_to_archive[copy_id]
        _need(archive_id in frozen_n,
              "physical copy %s: archive %s outside frozen roster"
              % (copy_id, archive_id))
        _need(d_k == frozen_n[archive_id],
              "physical copy %s: d_k %d disagrees with frozen N_i %d "
              "for archive %s" % (copy_id, d_k, frozen_n[archive_id], archive_id))
        enriched.append(LogicalDenominatorRow(archive_id, copy_id, pop_id, d_k))
    return tuple(enriched)


def deduplicate_logical_total(logical_rows):
    """Authoritative TOTAL logical vector denominator, unique-by-archive."""
    _need(type(logical_rows) in (tuple, list) and len(logical_rows) > 0,
          "non-empty logical row sequence required")
    per_archive = {}
    for row in logical_rows:
        _need(type(row) is LogicalDenominatorRow,
              "LogicalDenominatorRow required")
        _need(type(row.archive_id) is str and row.archive_id.strip(),
              "nonblank archive_id required")
        _need(type(row.n_i) is int and not isinstance(row.n_i, bool)
              and row.n_i >= 1, "positive integer n_i required")
        if row.archive_id in per_archive:
            _need(per_archive[row.archive_id] == row.n_i,
                  "archive %s: conflicting N_i %d vs %d"
                  % (row.archive_id, per_archive[row.archive_id], row.n_i))
        else:
            per_archive[row.archive_id] = row.n_i
    return sum(per_archive.values())


def naive_copy_total(denominators):
    """Per-copy sum over raw rows. Defect demonstrator only, not authoritative."""
    return sum(d_k for _, _, d_k in _check_denominator_shape(denominators, "denominators"))


def labeled_summary(*, logical_total, naive_total, n_archives, n_copies):
    """One-line labeled report. LongMemEval-only, exploratory, not for citation."""
    for name, value in (("logical_total", logical_total), ("naive_total", naive_total),
                        ("n_archives", n_archives), ("n_copies", n_copies)):
        _need(type(value) is int and not isinstance(value, bool) and value >= 0,
              "%s: nonnegative integer required" % name)
    return ("%s LongMemEval logical denominator: logical_total=%d "
            "(unique-by-archive over %d archives); naive_copy_total=%d "
            "(per-copy sum over %d copies, double-counts duplicates, not authoritative)"
            % (REPORT_LABELS, logical_total, n_archives, naive_total, n_copies))


def load_longmemeval_anchor_map():
    """Frozen LongMemEval archive_id -> N_i map. No caller-supplied knobs."""
    v7 = _load_v7_exact()
    try:
        anchor = v7.load_longmemeval_anchor()
    except Exception as exc:
        raise V10ValidationError(
            "pinned V7 LongMemEval anchor refused: %s: %s"
            % (exc.__class__.__name__, exc)) from exc
    frozen = dict(anchor.sizes)
    _need(len(frozen) == LONGMEMEVAL_EXPECTED_ARCHIVES,
          "LongMemEval anchor must contain exactly %d archives"
          % LONGMEMEVAL_EXPECTED_ARCHIVES)
    return frozen


def _fresh_snapshot_for(ctx):
    v9 = _load_v9_exact()
    try:
        return v9.V9Context(ctx.plan_path, ctx.expected_plan_sha256,
                            ctx.fixture_bindings_path,
                            ctx.expected_fixture_bindings_sha256,
                            ctx.physical_bindings_path,
                            ctx.expected_physical_bindings_sha256).fresh_snapshot()
    except Exception as exc:
        raise V10ValidationError(
            "pinned V9 fresh consumption refused: %s: %s"
            % (exc.__class__.__name__, exc)) from exc


def _plan_maps_for(ctx):
    guard = _load_guard_exact()
    try:
        plan = guard.load_plan(ctx.plan_path, ctx.expected_plan_sha256, _CONTRACT_PATH)
    except Exception as exc:
        raise V10ValidationError(
            "pinned parent guard refused: %s: %s"
            % (exc.__class__.__name__, exc)) from exc
    data = plan.data
    try:
        copy_to_archive = {c["id"]: c["archive_id"] for c in data["physical_copies"]}
        declared = {a["id"]: a["N_i"] for a in data["archives"]}
    except (TypeError, KeyError) as exc:
        raise V10ValidationError("plan data shape: %s" % exc) from exc
    frozen = load_longmemeval_anchor_map()
    _need(set(declared) == set(frozen),
          "plan archive roster must equal the frozen LongMemEval roster")
    for aid, n_i in declared.items():
        _need(n_i == frozen[aid],
              "archive %s: declared N_i disagrees with frozen anchor" % aid)
    return copy_to_archive, frozen


class V10Context(NamedTuple):
    plan_path: str
    expected_plan_sha256: str
    fixture_bindings_path: str
    expected_fixture_bindings_sha256: str
    physical_bindings_path: str
    expected_physical_bindings_sha256: str

    def fresh_snapshot(self):
        return _fresh_snapshot_for(self)

    def logical_denominator_rows(self):
        snapshot = _fresh_snapshot_for(self)
        copy_to_archive, frozen = _plan_maps_for(self)
        return enrich_denominator_rows(
            snapshot.semantic_proof.denominators, copy_to_archive, frozen)

    def naive_copy_total_vectors(self):
        snapshot = _fresh_snapshot_for(self)
        return naive_copy_total(snapshot.semantic_proof.denominators)

    def logical_total_vectors(self):
        return deduplicate_logical_total(self.logical_denominator_rows())


def preflight_longmemeval_v10(plan_path, expected_plan_sha256,
                              fixture_bindings_path, expected_fixture_bindings_sha256,
                              physical_bindings_path, expected_physical_bindings_sha256):
    """Validate once, retain no snapshot, return only a fresh-consumption capability."""
    ctx = V10Context(str(Path(plan_path)), expected_plan_sha256,
                     str(Path(fixture_bindings_path)), expected_fixture_bindings_sha256,
                     str(Path(physical_bindings_path)), expected_physical_bindings_sha256)
    _digest(expected_plan_sha256, "expected plan SHA256")
    _digest(expected_fixture_bindings_sha256, "expected fixture bindings SHA256")
    _digest(expected_physical_bindings_sha256, "expected physical bindings SHA256")
    ctx.logical_denominator_rows()
    return V10Context(ctx.plan_path, ctx.expected_plan_sha256,
                      ctx.fixture_bindings_path, ctx.expected_fixture_bindings_sha256,
                      ctx.physical_bindings_path, ctx.expected_physical_bindings_sha256)
