"""V52 static-storage V10 integrated preflight (concurrency + denominator repair).

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

LongMemEval-only preparation gate. Repair candidate, not independently
audited, not frozen, no measurement authorization. No storage measurement,
retrieval, model fit, run authorization, seal, or Task4F1 outcome access.

Single public entrypoint: ``preflight_longmemeval_v10`` returning
``V10Context`` (paths/hashes only; every access revalidates from disk).
Ingredient layers (same directory, preserved for provenance):
``consumption_gate_v10.py`` (hardened loader: scoped importer, no
``sys.modules`` publication, process-global reentrant lock) and
``denominator_integrity_v10.py`` (unique-by-archive logical denominator
math). That denominator module's standalone ``V10Context`` wraps the frozen
V9 loader and is SUPERSEDED by this module: the integrated path below flows
the denominator logic through the hardened chain instead. Its pure helpers
are inlined here (self-contained gate, no sibling-import dependency);
behavioral equivalence with the candidate file is covered by the integrated
test module.

Hardening applied across ALL pinned loading paths (V8 chain, parent guard,
V7 anchor): transaction-local scoped ``__import__`` (no dependency name
published to ``sys.modules``; only the module's own unique private name is
visible transiently during its exec), whole-transaction ``_CHAIN_LOCK``,
exact-byte SHA256 auth
with a digest primitive captured at trusted import, and a frozen ``hashlib``
served to pinned code so ambient ``hashlib.sha256`` monkeypatching cannot
vouch for swapped bytes through the full chain. Trust assumption: this
module itself must be imported before any in-process attacker runs (same
assumption the pinned SHA constants already require); the existing gate
disclaims an arbitrary same-process code attacker beyond this primitive
capture (see disposition).

V9-compatible surface is preserved (``V9Context``,
``preflight_longmemeval_v9``, ``_fresh_v8``, ``_exec_exact``,
``_load_v8_exact``) so the frozen V9 suite and the implementation-independent
security regression suite run unmodified against this module.
"""
from __future__ import annotations

import builtins
import hashlib as _hashlib_module
import itertools
import os
from pathlib import Path
import stat
import sys
import threading
import types
from typing import NamedTuple

MAX_SOURCE_BYTES = 64 * 1024 * 1024

V8_RUNTIME_SHA256 = "a0f2432fcd381a2d58bc7837d01ef3ab74f2b61f95e1a307b93c987696486f2f"
V8_SNAPSHOT_SHA256 = "23296fa6b9b454f78798ddae0d94066fc43c43aec797cc2a432c9dd67693f20a"
V8_GATE_SHA256 = "68fbac5bc6b5cef7858a7d585b7be514a6b8fc5aadd12ad5cc25e1ac45b36d99"
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

# Process-global reentrant lock across whole load+consume transactions.
_CHAIN_LOCK = threading.RLock()

_REAL_IMPORT = builtins.__import__

# Trustworthy digest primitive, captured at trusted import before any
# in-process mutation can replace it. All authentication below uses this,
# never a dynamically resolved attribute.
_PRISTINE_SHA256 = _hashlib_module.sha256


def _frozen_hashlib_module():
    """Snapshot of ``hashlib`` with ``sha256`` pinned to the trusted capture."""
    mod = types.ModuleType("hashlib")
    mod.__dict__.update(vars(_hashlib_module))
    mod.__dict__["sha256"] = _PRISTINE_SHA256
    return mod


_FROZEN_HASHLIB = _frozen_hashlib_module()


class V10ValidationError(ValueError):
    """Any V10 refusal. Callers must stop preparation/measurement."""


def _need(c, m):
    if not c:
        raise V10ValidationError(m)


def _digest(value, where):
    _need(type(value) is str and len(value) == 64
          and all(c in "0123456789abcdef" for c in value),
          "%s: lowercase SHA256 required" % where)


def _discover_repo_root():
    env = os.environ.get("LLMZIP_REPO")
    if env:
        c = Path(env).resolve()
        if (c / "drafts/v52/static_storage_integration_v8_2026_09_13").is_dir():
            return c
    here = Path(__file__).resolve()
    for c in (here.parent, *here.parents):
        if (c / "drafts/v52/static_storage_integration_v8_2026_09_13").is_dir():
            return c
    return here.parent


_REPO_ROOT = _discover_repo_root()
_V8_DIR = _REPO_ROOT / "drafts/v52/static_storage_integration_v8_2026_09_13"
_V8_RUNTIME_PATH = _V8_DIR / "v8_runtime.py"
_V8_SNAPSHOT_PATH = _V8_DIR / "v8_snapshot.py"
_V8_GATE_PATH = _V8_DIR / "storage_semantic_gate_v8.py"
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
        raise V10ValidationError(f"{where}: cannot stat source: {exc.__class__.__name__}") from exc
    _need(stat.S_ISREG(pre.st_mode), f"{where}: source must be a regular file")
    _need(pre.st_size <= limit, f"{where}: source byte limit")
    try:
        fd = os.open(str(path), os.O_RDONLY | _O_NOFOLLOW | _O_NONBLOCK | _O_CLOEXEC | _O_BINARY)
    except (OSError, ValueError) as exc:
        raise V10ValidationError(f"{where}: cannot open source: {exc.__class__.__name__}") from exc
    try:
        post = os.fstat(fd)
        _need(stat.S_ISREG(post.st_mode), f"{where}: opened source not regular")
        _need((post.st_dev, post.st_ino) == (pre.st_dev, pre.st_ino), f"{where}: source identity changed")
        chunks, total = [], 0
        while True:
            try:
                chunk = os.read(fd, 1 << 20)
            except OSError as exc:
                raise V10ValidationError(f"{where}: source read failed: {exc.__class__.__name__}") from exc
            if not chunk:
                break
            total += len(chunk)
            _need(total <= limit, f"{where}: source byte limit")
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(fd)


def _scoped_importer(deps):
    def _scoped(name, globals=None, locals=None, fromlist=(), level=0):
        if level == 0 and name in deps:
            return deps[name]
        return _REAL_IMPORT(name, globals, locals, fromlist, level)

    return _scoped


def _exec_private(name, path, expected_sha256, dependencies=()):
    """Execute authenticated bytes with transaction-local dependency binding.

    Dependency names are never published to ``sys.modules``. The module
    itself is registered under its own unique per-transaction private name
    for the duration of the exec only (stdlib introspection such as
    ``dataclasses`` on Python 3.14 resolves ``sys.modules[cls.__module__]``;
    without self-registration, pinned V7/guard sources fail to execute).
    The name embeds a process-unique counter so concurrent transactions can
    never collide, and it is removed in ``finally``. Every pinned load
    additionally resolves ``hashlib`` to the frozen trusted capture, so
    ambient ``hashlib.sha256`` patching cannot vouch for swapped bytes
    inside pinned code either.
    """
    raw = _read_regular(path, MAX_SOURCE_BYTES, f"{name} source")
    _need(_PRISTINE_SHA256(raw).hexdigest() == expected_sha256, f"{name}: SHA256 mismatch")
    deps = dict(dependencies)
    deps.setdefault("hashlib", _FROZEN_HASHLIB)
    private = f"_v52_v10_{name}_{next(_COUNTER)}"
    mod = types.ModuleType(private)
    mod.__file__ = str(Path(path).resolve())
    mod.__package__ = ""
    shadow = dict(vars(builtins))
    shadow["__import__"] = _scoped_importer(deps)
    mod.__dict__["__builtins__"] = shadow
    leaked = set(sys.modules)
    sys.modules[private] = mod
    try:
        exec(compile(raw, mod.__file__, "exec", dont_inherit=True), mod.__dict__)
    except Exception as exc:
        raise V10ValidationError(f"{name}: exact source execution failed: {exc.__class__.__name__}: {exc}") from exc
    finally:
        sys.modules.pop(private, None)
        for key in set(sys.modules) - leaked:
            if key.startswith("_v52_v10_"):
                sys.modules.pop(key, None)
    return mod


# V9-compatible alias: byte-exact for dependency-free direct calls.
_exec_exact = _exec_private


def load_pinned_v8_chain():
    """Load the exact pinned V8 chain. Reentrant; serialized process-wide."""
    with _CHAIN_LOCK:
        rt = _exec_private("v8_runtime", _V8_RUNTIME_PATH, V8_RUNTIME_SHA256)
        snap = _exec_private("v8_snapshot", _V8_SNAPSHOT_PATH, V8_SNAPSHOT_SHA256, (("v8_runtime", rt),))
        gate = _exec_private(
            "storage_semantic_gate_v8", _V8_GATE_PATH, V8_GATE_SHA256,
            (("v8_runtime", rt), ("v8_snapshot", snap)),
        )
        return gate


_load_v8_exact = load_pinned_v8_chain


def _fresh_v8(plan_path, plan_sha, fixture_path, fixture_sha, physical_path, physical_sha):
    with _CHAIN_LOCK:
        gate = load_pinned_v8_chain()
        try:
            return gate._fresh_preflight(plan_path, plan_sha, fixture_path, fixture_sha, physical_path, physical_sha)
        except Exception as exc:
            raise V10ValidationError(f"pinned V8 fresh preflight refused: {exc.__class__.__name__}: {exc}") from exc


def load_longmemeval_anchor_map():
    """Frozen LongMemEval archive_id -> N_i map. No caller-supplied knobs."""
    with _CHAIN_LOCK:
        v7 = _exec_private("storage_semantic_gate_v7", _V7_GATE_PATH, V7_SOURCE_SHA256)
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


def _plan_maps_for(ctx):
    with _CHAIN_LOCK:
        guard = _exec_private("measurement_plan_guard", _PARENT_GUARD_PATH, PARENT_GUARD_SHA256)
        contract_raw = _read_regular(_CONTRACT_PATH, MAX_SOURCE_BYTES, "measurement contract source")
        _need(_PRISTINE_SHA256(contract_raw).hexdigest() == CONTRACT_SHA256,
              "measurement contract: SHA256 mismatch")
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


def _fresh_snapshot_for(ctx):
    return _fresh_v8(
        ctx.plan_path, ctx.expected_plan_sha256,
        ctx.fixture_bindings_path, ctx.expected_fixture_bindings_sha256,
        ctx.physical_bindings_path, ctx.expected_physical_bindings_sha256,
    )


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


class V9Context(NamedTuple):
    plan_path: str
    expected_plan_sha256: str
    fixture_bindings_path: str
    expected_fixture_bindings_sha256: str
    physical_bindings_path: str
    expected_physical_bindings_sha256: str

    def fresh_snapshot(self):
        return _fresh_v8(
            self.plan_path, self.expected_plan_sha256,
            self.fixture_bindings_path, self.expected_fixture_bindings_sha256,
            self.physical_bindings_path, self.expected_physical_bindings_sha256,
        )

    def authoritative_denominators(self):
        return self.fresh_snapshot().semantic_proof.denominators


class V10Context(V9Context):
    """Single integrated context: hardened fresh consumption + archive-identified rows.

    Carries paths/hashes only. Every method revalidates from disk; no
    snapshot is retained. Byte numerators are never deduplicated and no byte
    total is offered.
    """

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


def preflight_longmemeval_v9(plan_path, expected_plan_sha256,
                             fixture_bindings_path, expected_fixture_bindings_sha256,
                             physical_bindings_path, expected_physical_bindings_sha256):
    """V9-compatible validation: retain no snapshot, return fresh-consumption capability."""
    _fresh_v8(plan_path, expected_plan_sha256, fixture_bindings_path,
              expected_fixture_bindings_sha256, physical_bindings_path,
              expected_physical_bindings_sha256)
    return V9Context(str(Path(plan_path)), expected_plan_sha256,
                     str(Path(fixture_bindings_path)), expected_fixture_bindings_sha256,
                     str(Path(physical_bindings_path)), expected_physical_bindings_sha256)


def preflight_longmemeval_v10(plan_path, expected_plan_sha256,
                              fixture_bindings_path, expected_fixture_bindings_sha256,
                              physical_bindings_path, expected_physical_bindings_sha256):
    """Validate once through the hardened chain, retain no snapshot.

    Returns the single integrated fresh-consumption capability. Refusals
    raise V10ValidationError (a ValueError).
    """
    _digest(expected_plan_sha256, "expected plan SHA256")
    _digest(expected_fixture_bindings_sha256, "expected fixture bindings SHA256")
    _digest(expected_physical_bindings_sha256, "expected physical bindings SHA256")
    ctx = V10Context(str(Path(plan_path)), expected_plan_sha256,
                     str(Path(fixture_bindings_path)), expected_fixture_bindings_sha256,
                     str(Path(physical_bindings_path)), expected_physical_bindings_sha256)
    ctx.logical_denominator_rows()
    return V10Context(ctx.plan_path, ctx.expected_plan_sha256,
                      ctx.fixture_bindings_path, ctx.expected_fixture_bindings_sha256,
                      ctx.physical_bindings_path, ctx.expected_physical_bindings_sha256)
