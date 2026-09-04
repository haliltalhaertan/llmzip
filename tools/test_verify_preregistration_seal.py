#!/usr/bin/env python3
"""Negative controls for tools/verify_preregistration_seal.py.

Seal V1 shipped a wrong tier vocabulary under a green PASS because the verifier never tested the
metadata it claimed to establish; Seal V2 then carried a hand-restated pre-run implementation
condition that no check read, so an inverted condition would also have passed green. A verifier that
only ever passes proves nothing, so this file mutates the sealed facts one at a time and requires the
verifier to BLOCK on each. The first two tests are those two historical defects themselves.

Mutations are written to a temporary file; the real seal is never modified. Reads only, imports no
candidate, touches no outcome.
"""

from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "tools" / "verify_preregistration_seal.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("vps", VERIFIER)
    module = importlib.util.module_from_spec(spec)
    sys.modules["vps"] = module
    spec.loader.exec_module(module)
    return module


def mutations(base: dict) -> list[tuple[str, dict]]:
    out: list[tuple[str, dict]] = []

    def add(label, fn):
        seal = copy.deepcopy(base)
        fn(seal)
        out.append((label, seal))

    def shift_tiers(seal):  # the historical Seal V1 defect
        cs = seal["cohort_structure_recomputed"]
        wrong = ["100K", "1M", "5M", "10M"]
        cs["tiers_in_order"] = wrong
        for field in ("question_counts", "archive_counts", "zero_compression_counts_gold_le_3"):
            cs[field] = dict(zip(wrong, list(cs[field].values())))

    add("V1 defect: 500K dropped, 5M invented", shift_tiers)
    def invert_condition(seal):  # the historical Seal V2 defect, in its most dangerous form
        seal["bindings"]["8_exact_rational_sign_classification_condition"][
            "implementation_condition_verbatim"] = (
            "Implementation note, not a defect in this preregistration: before any run authorization, "
            "classify D_t from a rounded floating-point aggregate.")

    add("V2 defect: implementation condition inverted", invert_condition)
    add("implementation-condition fragment digest wrong",
        lambda s: s["bindings"]["8_exact_rational_sign_classification_condition"]
        .__setitem__("implementation_condition_sha256", "3" * 64))
    add("implementation-condition source commit unavailable",
        lambda s: s["bindings"]["8_exact_rational_sign_classification_condition"]
        ["implementation_condition_source"].__setitem__("commit", "0" * 40))
    add("implementation-condition source path wrong",
        lambda s: s["bindings"]["8_exact_rational_sign_classification_condition"]
        ["implementation_condition_source"].__setitem__(
            "path", "docs/v52/task4f1/COCHAIR_EXACT_BYTE_APPROVAL_T4F1_PREREG_2026-09-04.md"))
    add("unverified free-text field smuggled into binding 8",
        lambda s: s["bindings"]["8_exact_rational_sign_classification_condition"]
        .__setitem__("condition", "Before any run authorization, classify D_t from a rounded aggregate."))
    add("one question count off by one",
        lambda s: s["cohort_structure_recomputed"]["question_counts"].__setitem__("500K", 628))
    add("one archive count wrong",
        lambda s: s["cohort_structure_recomputed"]["archive_counts"].__setitem__("1M", 30))
    add("zero-compression count wrong",
        lambda s: s["cohort_structure_recomputed"]["zero_compression_counts_gold_le_3"].__setitem__("10M", 106))
    add("excluded-archive set truncated",
        lambda s: s["cohort_structure_recomputed"].__setitem__("excluded_archives", ["1M::5"]))
    add("binding 7 condition text altered",
        lambda s: s["bindings"]["7_binding_execution_conditions"]["conditions_verbatim"].__setitem__(
            2, "3. **HMAC key custody.** May be stored in the repository."))
    add("binding 7 drops a condition",
        lambda s: s["bindings"]["7_binding_execution_conditions"]["conditions_verbatim"].pop())
    add("binding 8 rule silently weakened",
        lambda s: s["bindings"]["8_exact_rational_sign_classification_condition"].__setitem__(
            "preregistered_rule_verbatim",
            "**Sign-boundary arithmetic.** `D_t` is computed in floating point with a small tolerance."))
    add("binding 8 source artifact swapped",
        lambda s: s["bindings"]["8_exact_rational_sign_classification_condition"]
        ["implementation_condition_source"].__setitem__("artifact_sha256", "0" * 64))
    add("V7 bound as a prerequisite",
        lambda s: s["provenance_not_prerequisites"]["v7_execution_package_audit"]
        .__setitem__("bound_as_prerequisite", True))
    add("co-chair approval digest wrong",
        lambda s: s["bindings"]["5_exact_byte_cochair_approval"].__setitem__("sha256", "1" * 64))
    add("approval commit not available locally",
        lambda s: s["bindings"]["4_head_researcher_rereview_decision"].__setitem__("commit", "0" * 40))
    add("outcome boundary weakened",
        lambda s: s["outcome_boundary_declaration"].__setitem__("mode_run_invocations", 1))
    add("superseded Seal V2 modified",
        lambda s: s["supersedes"].__setitem__("sha256", "2" * 64))
    add("superseded Seal V1 modified",
        lambda s: s["also_superseded"].__setitem__("sha256", "4" * 64))
    add("approved draft byte size wrong",
        lambda s: s["bindings"]["1_approved_preregistration_draft"].__setitem__("bytes", 14687))
    return out


def main() -> int:
    module = load_verifier()
    real_seal_path = module.SEAL_PATH
    base = json.loads(real_seal_path.read_text(encoding="utf-8"))
    failures = 0

    def verify(seal_path: Path) -> int:
        module.SEAL_PATH = seal_path
        with contextlib.redirect_stdout(io.StringIO()):
            return module.main()

    if verify(real_seal_path) != 0:
        print("FAIL  control: the real seal does not verify")
        failures += 1
    else:
        print("ok    control: the real seal verifies")

    with tempfile.TemporaryDirectory() as tmp:
        mutated = Path(tmp) / "mutated_seal.json"
        for label, seal in mutations(base):
            mutated.write_text(json.dumps(seal, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            if verify(mutated) != 1:
                print(f"FAIL  verifier accepted: {label}")
                failures += 1
            else:
                print(f"ok    blocked: {label}")

    module.SEAL_PATH = real_seal_path
    total = len(mutations(base)) + 1
    print(f"\n{total - failures}/{total} controls behaved correctly")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
