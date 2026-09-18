"""MUTATION VARIANT (deliberately broken). NOT a gate, NOT V10, NOT shippable.

Reproduces the auditor's retained-snapshot class against the exact V9 bytes:
``preflight`` validates once, stashes that validated snapshot in a module
global, and ``authoritative_denominators()`` serves the STASH without
re-reading a single file. ``fresh_snapshot()`` still re-runs, so the stale
and fresh paths silently diverge after any on-disk change.

The module mirrors V9's patchable shape (``_fresh_v8`` module global,
identical ``_fields``) so the mock-based V9-era tests exercise it exactly as
they exercise V9.

Why the V9-era tests still pass on this variant:
- ``test_context_exposes_no_snapshot_field``: no new NamedTuple field exists;
  ``_fields`` is unchanged and there is no ``initial_snapshot`` attribute.
- ``test_preflight_discards_validation_snapshot``: validation calls the
  (mocked) ``_fresh_v8`` exactly once; the return value is stashed, not
  embedded in the context tuple.
- ``test_fresh_snapshot_reruns_each_access``: ``fresh_snapshot`` delegates to
  the (mocked) ``_fresh_v8`` on every access.
- ``test_exact_loader_ignores_preloaded_same_name``: the loader is untouched.
- No V9-era test ever calls ``authoritative_denominators()`` at all.
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

_V9_PATH = (
    Path(__file__).resolve().parents[2]
    / "static_storage_integration_v9_2026_09_13/consumption_gate_v9.py"
)

_spec = importlib.util.spec_from_file_location(
    "consumption_gate_v9_real", str(_V9_PATH))
assert _spec is not None and _spec.loader is not None
_real = importlib.util.module_from_spec(_spec)
sys.modules["consumption_gate_v9_real"] = _real
_spec.loader.exec_module(_real)

V9ValidationError = _real.V9ValidationError
_exec_exact = _real._exec_exact
_load_v8_exact = _real._load_v8_exact
_V8_RUNTIME_PATH = _real._V8_RUNTIME_PATH
_V8_SNAPSHOT_PATH = _real._V8_SNAPSHOT_PATH
_V8_GATE_PATH = _real._V8_GATE_PATH
V8_RUNTIME_SHA256 = _real.V8_RUNTIME_SHA256
V8_SNAPSHOT_SHA256 = _real.V8_SNAPSHOT_SHA256
V8_GATE_SHA256 = _real.V8_GATE_SHA256

_fresh_v8 = _real._fresh_v8

_STASH: dict = {}


class V9Context(_real.V9Context):
    """Same fields; only the denominator path is rotted to serve the stash."""

    def fresh_snapshot(self):
        return _fresh_v8(
            self.plan_path, self.expected_plan_sha256,
            self.fixture_bindings_path, self.expected_fixture_bindings_sha256,
            self.physical_bindings_path, self.expected_physical_bindings_sha256,
        )

    def authoritative_denominators(self):
        return _STASH["snapshot"].semantic_proof.denominators


def preflight_longmemeval_v9(plan_path, expected_plan_sha256,
                             fixture_bindings_path,
                             expected_fixture_bindings_sha256,
                             physical_bindings_path,
                             expected_physical_bindings_sha256):
    snap = _fresh_v8(plan_path, expected_plan_sha256, fixture_bindings_path,
                     expected_fixture_bindings_sha256, physical_bindings_path,
                     expected_physical_bindings_sha256)
    _STASH["snapshot"] = snap
    return V9Context(str(Path(plan_path)), expected_plan_sha256,
                     str(Path(fixture_bindings_path)),
                     expected_fixture_bindings_sha256,
                     str(Path(physical_bindings_path)),
                     expected_physical_bindings_sha256)


def _module_sha() -> str:  # debugging helper, not part of any contract
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
