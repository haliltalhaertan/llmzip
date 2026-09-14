"""V52 static-storage V10 hardened consumption gate.

Preparation-only, LongMemEval-only. Additive repair layer over frozen V9
(b300cbf): V9 is not modified. V10 reimplements the pinned V8 loading
transaction with the race class removed.

V9 defect: authenticated source bytes are executed while dependency modules
are published under shared ``sys.modules`` names (``v8_runtime``,
``v8_snapshot``). Two concurrent transactions interleave across that global
namespace, so one chain can bind an ambient or foreign module and silently
bypass rejection controls.

V10 invariant: a loading transaction shares no mutable global namespace
state. Dependencies are bound through a transaction-local importer and
nothing is published to ``sys.modules``; a process-global reentrant lock
additionally serializes whole transactions (load plus consumption) so nested
V10 loads on one thread cannot deadlock and concurrent loads cannot overlap.

Preserved: exact-byte SHA256 authentication, O_NOFOLLOW regular-file reads,
pycache avoidance (compile+exec only, never the import system as authority).
"""
from __future__ import annotations

import builtins
import hashlib
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

_O_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
_O_NONBLOCK = getattr(os, "O_NONBLOCK", 0)
_O_CLOEXEC = getattr(os, "O_CLOEXEC", 0)
_O_BINARY = getattr(os, "O_BINARY", 0)
_COUNTER = itertools.count()

# Process-global reentrant lock: held across the entire loading transaction
# (every pinned exec, dependency wiring, and the consuming fresh-preflight
# call). Reentrant so a V10 entry called from inside a V10 transaction on the
# same thread does not deadlock.
_CHAIN_LOCK = threading.RLock()

_REAL_IMPORT = builtins.__import__


class V10ValidationError(ValueError):
    pass


def _need(c, m):
    if not c:
        raise V10ValidationError(m)


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

    Publishes nothing to ``sys.modules``: ``import <dep>`` inside the
    authenticated bytes resolves through a scoped ``__import__`` that serves
    only this transaction's dependency map and delegates everything else to
    the real importer. Concurrent transactions therefore cannot observe or
    perturb each other through the module namespace.
    """
    raw = _read_regular(path, MAX_SOURCE_BYTES, f"{name} source")
    _need(hashlib.sha256(raw).hexdigest() == expected_sha256, f"{name}: SHA256 mismatch")
    deps = dict(dependencies)
    private = f"_v52_v10_{name}_{next(_COUNTER)}"
    mod = types.ModuleType(private)
    mod.__file__ = str(Path(path).resolve())
    mod.__package__ = ""
    shadow = dict(vars(builtins))
    shadow["__import__"] = _scoped_importer(deps)
    mod.__dict__["__builtins__"] = shadow
    leaked = set(sys.modules)
    try:
        exec(compile(raw, mod.__file__, "exec", dont_inherit=True), mod.__dict__)
    except Exception as exc:
        raise V10ValidationError(f"{name}: exact source execution failed: {exc.__class__.__name__}: {exc}") from exc
    finally:
        for key in set(sys.modules) - leaked:
            if key.startswith("_v52_v10_"):
                sys.modules.pop(key, None)
    return mod


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


def _fresh_v8(plan_path, plan_sha, fixture_path, fixture_sha, physical_path, physical_sha):
    with _CHAIN_LOCK:
        gate = load_pinned_v8_chain()
        try:
            return gate._fresh_preflight(plan_path, plan_sha, fixture_path, fixture_sha, physical_path, physical_sha)
        except Exception as exc:
            raise V10ValidationError(f"pinned V8 fresh preflight refused: {exc.__class__.__name__}: {exc}") from exc


class V10Context(NamedTuple):
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


def preflight_longmemeval_v10(plan_path, expected_plan_sha256,
                              fixture_bindings_path, expected_fixture_bindings_sha256,
                              physical_bindings_path, expected_physical_bindings_sha256):
    """Validate once, retain no snapshot, return only a fresh-consumption capability."""
    _fresh_v8(plan_path, expected_plan_sha256, fixture_bindings_path,
              expected_fixture_bindings_sha256, physical_bindings_path,
              expected_physical_bindings_sha256)
    return V10Context(str(Path(plan_path)), expected_plan_sha256,
                      str(Path(fixture_bindings_path)), expected_fixture_bindings_sha256,
                      str(Path(physical_bindings_path)), expected_physical_bindings_sha256)
