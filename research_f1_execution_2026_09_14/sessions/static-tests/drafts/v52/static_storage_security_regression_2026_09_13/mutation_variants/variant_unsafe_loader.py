"""MUTATION VARIANT (deliberately broken). NOT a gate, NOT V10, NOT shippable.

Reproduces the auditor's unsafe-loader class against the exact V9 bytes: the
byte-exact loader is kept for direct calls, but whenever a caller supplies
dependency modules, ambient ``sys.modules`` entries are preferred over the
exact ones. On a clean interpreter this behaves identically to V9; when an
attacker (or stale import) plants ``v8_runtime`` / ``v8_snapshot``, the gate
executes the planted code with full trust.

The module mirrors V9's patchable shape (``_fresh_v8`` module global,
identical context ``_fields``) so the mock-based V9-era tests exercise it
exactly as they exercise V9.

Why the V9-era tests still pass on this variant:
- ``test_exact_loader_ignores_preloaded_same_name`` calls ``_exec_exact``
  with NO dependencies (a bare ``victim`` name), which stays byte-exact.
- The canonical tests run on a clean interpreter where the dependency names
  are absent from ``sys.modules``, so the ambient-preference branch never
  fires and hashes/behavior match V9 exactly.
- No V9-era test ever poisons ``sys.modules['v8_runtime']`` /
  ``sys.modules['v8_snapshot']`` and then runs the real chain end-to-end.
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
_V8_RUNTIME_PATH = _real._V8_RUNTIME_PATH
_V8_SNAPSHOT_PATH = _real._V8_SNAPSHOT_PATH
_V8_GATE_PATH = _real._V8_GATE_PATH
V8_RUNTIME_SHA256 = _real.V8_RUNTIME_SHA256
V8_SNAPSHOT_SHA256 = _real.V8_SNAPSHOT_SHA256
V8_GATE_SHA256 = _real.V8_GATE_SHA256


_exact_orig = _real._exec_exact


def _exec_exact(name, path, expected_sha256, dependencies=()):
    deps = tuple(dependencies)
    if deps and all(dep_name in sys.modules for dep_name, _ in deps):
        # UNSAFE: trust whatever the ambient interpreter already imported.
        deps = tuple((dep_name, sys.modules[dep_name]) for dep_name, _ in deps)
    return _exact_orig(name, path, expected_sha256, deps)


# Rebind inside the real module namespace: the whole pinned chain below this
# file resolves the loader through that namespace and honors the ambient
# preference above, while direct ``_exec_exact`` calls stay byte-exact.
_real._exec_exact = _exec_exact


def _load_v8_exact():
    return _real._load_v8_exact()


def _fresh_v8(plan_path, plan_sha, fixture_path, fixture_sha, physical_path,
              physical_sha):
    return _real._fresh_v8(plan_path, plan_sha, fixture_path, fixture_sha,
                           physical_path, physical_sha)


class V9Context(_real.V9Context):
    """Same fields; reruns through this module's patchable ``_fresh_v8``."""

    def fresh_snapshot(self):
        return _fresh_v8(
            self.plan_path, self.expected_plan_sha256,
            self.fixture_bindings_path, self.expected_fixture_bindings_sha256,
            self.physical_bindings_path, self.expected_physical_bindings_sha256,
        )


def preflight_longmemeval_v9(plan_path, expected_plan_sha256,
                             fixture_bindings_path,
                             expected_fixture_bindings_sha256,
                             physical_bindings_path,
                             expected_physical_bindings_sha256):
    _fresh_v8(plan_path, expected_plan_sha256, fixture_bindings_path,
              expected_fixture_bindings_sha256, physical_bindings_path,
              expected_physical_bindings_sha256)
    return V9Context(str(Path(plan_path)), expected_plan_sha256,
                     str(Path(fixture_bindings_path)),
                     expected_fixture_bindings_sha256,
                     str(Path(physical_bindings_path)),
                     expected_physical_bindings_sha256)


def _module_sha() -> str:  # debugging helper, not part of any contract
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
