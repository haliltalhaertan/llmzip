#!/usr/bin/env python3
"""Two-layer negative controls for the final unchanged Seal V3 verifier.

Identity attacks are tested through the production identity layer. Semantic/source attacks bypass
identity deliberately and exercise the inner checks directly, so a changed temporary seal cannot
get a meaningless green test merely because its overall SHA256 changed.

Reads only. Does not import or execute an outcome-capable candidate.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "tools" / "verify_preregistration_seal_v3_final.py"
LEGACY_NEGATIVE_TESTS = ROOT / "tools" / "test_verify_preregistration_seal.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    final = load_module(FINAL, "v52_prereg_final_verifier")
    legacy_tests = load_module(LEGACY_NEGATIVE_TESTS, "v52_prereg_legacy_negative_tests")

    failures = 0
    identity_total = 0
    semantic_total = 0

    # ------------------------------------------------------------------
    # Layer A: production identity controls.
    # ------------------------------------------------------------------
    identity_total += 1
    if final.verify_identity():
        print("FAIL  identity control: real Seal V3 + real sidecar did not verify")
        failures += 1
    else:
        print("ok    identity: exact Seal V3 + exact sidecar")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        real_seal_bytes = final.SEAL_PATH.read_bytes()

        mutated_seal = tmp / final.ACCEPTED_SEAL_FILENAME
        mutated_seal.write_bytes(real_seal_bytes + b" ")
        identity_total += 1
        if not final.verify_identity(mutated_seal, final.SIDECAR_PATH):
            print("FAIL  identity accepted: one-byte Seal V3 mutation")
            failures += 1
        else:
            print("ok    identity blocked: one-byte Seal V3 mutation")

        missing_sidecar = tmp / "missing.sha256"
        identity_total += 1
        if not final.verify_identity(final.SEAL_PATH, missing_sidecar):
            print("FAIL  identity accepted: missing sidecar")
            failures += 1
        else:
            print("ok    identity blocked: missing sidecar")

        wrong_digest_sidecar = tmp / "wrong_digest.sha256"
        wrong_digest_sidecar.write_text(
            f"{'0' * 64}  {final.ACCEPTED_SEAL_FILENAME}\n", encoding="utf-8"
        )
        identity_total += 1
        if not final.verify_identity(final.SEAL_PATH, wrong_digest_sidecar):
            print("FAIL  identity accepted: wrong sidecar digest")
            failures += 1
        else:
            print("ok    identity blocked: wrong sidecar digest")

        wrong_filename_sidecar = tmp / "wrong_filename.sha256"
        wrong_filename_sidecar.write_text(
            f"{final.ACCEPTED_SEAL_SHA256}  WRONG_SEAL.json\n", encoding="utf-8"
        )
        identity_total += 1
        if not final.verify_identity(final.SEAL_PATH, wrong_filename_sidecar):
            print("FAIL  identity accepted: wrong sidecar filename")
            failures += 1
        else:
            print("ok    identity blocked: wrong sidecar filename")

    # ------------------------------------------------------------------
    # Layer B: semantic/source controls, intentionally without identity.
    # ------------------------------------------------------------------
    real_seal = json.loads(final.SEAL_PATH.read_text(encoding="utf-8"))
    semantic_total += 1
    semantic_fail = final.verify_content_sources(final.SEAL_PATH)
    if semantic_fail:
        print("FAIL  semantic control: unchanged Seal V3 did not verify")
        for item in semantic_fail:
            print(f"      {item}")
        failures += 1
    else:
        print("ok    semantic: unchanged Seal V3")

    mutations = list(legacy_tests.mutations(real_seal))

    # F2: a strict true substring used to pass the old membership check.
    weakened_rule = copy.deepcopy(real_seal)
    weakened_rule["bindings"]["8_exact_rational_sign_classification_condition"][
        "preregistered_rule_verbatim"
    ] = "**Sign-boundary arithmetic.**"
    mutations.append(("F2 strict true substring of §6 rule", weakened_rule))

    # F3: preserve the marker substring while materially changing the declared extraction rule.
    weakened_extraction_rule = copy.deepcopy(real_seal)
    weakened_extraction_rule["bindings"]["8_exact_rational_sign_classification_condition"][
        "implementation_condition_source"
    ]["extraction_rule"] = (
        "choose any paragraph provided it contains "
        "'Implementation note, not a defect in this preregistration:'"
    )
    mutations.append(("F3 changed extraction rule retaining marker", weakened_extraction_rule))

    with tempfile.TemporaryDirectory() as tmpdir:
        mutated_path = Path(tmpdir) / "mutated_seal.json"
        for label, mutated in mutations:
            mutated_path.write_text(
                json.dumps(mutated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            semantic_total += 1
            reasons = final.verify_content_sources(mutated_path)
            if not reasons:
                print(f"FAIL  semantic verifier accepted: {label}")
                failures += 1
            else:
                print(f"ok    semantic blocked: {label}")

    total = identity_total + semantic_total
    passed = total - failures
    print(f"\n{passed}/{total} two-layer controls behaved correctly")
    print(f"identity_controls={identity_total}")
    print(f"semantic_source_controls={semantic_total}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
