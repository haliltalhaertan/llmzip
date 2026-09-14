"""Parameterizable gate loader for the V52 static-storage security regression suite.

The suite never imports a gate by repository path directly. Every test goes
through :func:`load_gate`, which loads one gate module file chosen at runtime:

- ``GATE_UNDER_TEST_PATH``: filesystem path of the gate module to test.
  Default: the frozen V9 ``consumption_gate_v9.py`` (read-only; never edited).
- ``GATE_PREFLIGHT_FN``: public entrypoint name. Default
  ``preflight_longmemeval_v9``. A V10 candidate that renames the entrypoint
  can be tested without touching the suite by exporting this variable.

Consumption contract assumed (same shape V7/V8/V9 document):
- ``preflight(plan_path, plan_sha, fixture_path, fixture_sha, physical_path,
  physical_sha)`` returns a context; every refusal raises ``ValueError``.
- The context exposes ``fresh_snapshot()`` and ``authoritative_denominators()``.
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_GATE_PATH = (
    REPO_ROOT
    / "drafts/v52/static_storage_integration_v9_2026_09_13/consumption_gate_v9.py"
)
DEFAULT_PREFLIGHT_FN = "preflight_longmemeval_v9"


def gate_path() -> Path:
    return Path(os.environ.get("GATE_UNDER_TEST_PATH", str(DEFAULT_GATE_PATH)))


def preflight_fn_name() -> str:
    return os.environ.get("GATE_PREFLIGHT_FN", DEFAULT_PREFLIGHT_FN)


def load_gate(path: str | Path | None = None, fn: str | None = None):
    """Import the gate file under a unique module name and bind its entrypoint."""
    resolved = Path(path or gate_path())
    if not resolved.is_file():
        raise FileNotFoundError(f"gate under test not found: {resolved}")
    entry = fn or preflight_fn_name()
    tag = hashlib.sha256(str(resolved).encode()).hexdigest()[:12]
    name = f"gate_under_test_{tag}"
    spec = importlib.util.spec_from_file_location(name, str(resolved))
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load gate module from {resolved}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, entry):
        raise AttributeError(f"gate {resolved} has no entrypoint {entry!r}")
    module.preflight = getattr(module, entry)
    return module


def preflight(gate, plan_path, plan_sha, fixture_path, fixture_sha,
              physical_path, physical_sha):
    return gate.preflight(
        str(plan_path), plan_sha, str(fixture_path), fixture_sha,
        str(physical_path), physical_sha)


def denominators(ctx):
    return ctx.authoritative_denominators()


def fresh_denominators(ctx):
    return ctx.fresh_snapshot().semantic_proof.denominators
