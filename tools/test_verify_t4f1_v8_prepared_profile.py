#!/usr/bin/env python3
"""Outcome-free negative controls for the V8 prepared-profile verifier."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "tools" / "verify_t4f1_v8_prepared_profile.py"


def load_module():
    spec = importlib.util.spec_from_file_location("v8_profile_verifier", VERIFIER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load V8 profile verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    v = load_module()
    base = json.loads(v.SEAL.read_text(encoding="utf-8"))
    failures = 0
    total = 0

    def expect_pass(label: str, profile: dict) -> None:
        nonlocal failures, total
        total += 1
        reasons = v.verify_semantics(profile)
        if reasons:
            print(f"FAIL expected pass: {label}: {reasons}")
            failures += 1
        else:
            print(f"ok   pass: {label}")

    def expect_block(label: str, mutate) -> None:
        nonlocal failures, total
        total += 1
        profile = copy.deepcopy(base)
        mutate(profile)
        reasons = v.verify_semantics(profile)
        if not reasons:
            print(f"FAIL accepted mutation: {label}")
            failures += 1
        else:
            print(f"ok   blocked: {label}")

    expect_pass("unchanged prepared profile semantics", base)
    expect_block("extra top-level field", lambda p: p.__setitem__("note", "prose"))
    expect_block("run status changed", lambda p: p["authorization"].__setitem__("task_4f1_run", "AUTHORIZED"))
    expect_block("authorization extra field", lambda p: p["authorization"].__setitem__("outcome", "AUTHORIZED"))
    expect_block("production-looking key commitment inserted", lambda p: p["authorization_control"].__setitem__("key_commitment_sha256", "0" * 64))
    expect_block("HMAC scheme changed", lambda p: p["authorization_control"].__setitem__("scheme", "NONE"))
    expect_block("signed field removed", lambda p: p["authorization_control"]["signed_fields"].pop())
    expect_block("runner hash changed", lambda p: p["implementation"].__setitem__("sha256", "0" * 64))
    expect_block("implementation extra field", lambda p: p["implementation"].__setitem__("path", "other.py"))
    expect_block("schema changed", lambda p: p.__setitem__("schema", "V8"))

    total += 1
    parsed = v.parse_sidecar(v.SIDECAR)
    if parsed != (v.ACCEPTED_PROFILE_SHA256, v.PROFILE_FILENAME):
        print(f"FAIL sidecar parse: {parsed}")
        failures += 1
    else:
        print("ok   pass: exact sidecar")

    total += 1
    if v.sha256(v.SEAL) != v.ACCEPTED_PROFILE_SHA256:
        print("FAIL prepared profile identity")
        failures += 1
    else:
        print("ok   pass: exact prepared profile identity")

    total += 1
    if not v.RUNNER.is_file() or v.sha256(v.RUNNER) != v.ACCEPTED_RUNNER_SHA256:
        print("FAIL accepted V4 runner identity")
        failures += 1
    else:
        print("ok   pass: accepted V4 runner identity")

    print(f"\n{total - failures}/{total} controls behaved correctly")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
