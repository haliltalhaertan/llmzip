#!/usr/bin/env python3
"""Negative controls for tools/verify_preregistration_seal.py.

Three seal generations shipped defects under a green PASS: Seal V1's wrong tier vocabulary, Seal V2's
hand-restated pre-run implementation condition that no check read, and Seal V3's binding-8 metadata
which the field-set check did not reach. A verifier that only ever passes proves nothing, so this
file mutates the sealed facts one at a time and requires a BLOCK on each.

The suite has two layers, matching the verifier:

  * IDENTITY controls mutate the seal file or its sidecar on disk and exercise verify_identity, which
    answers "which seal is this?".
  * SEMANTIC controls mutate the parsed seal and exercise verify_semantics directly, so each one
    fails for its own specific reason rather than trivially because a mutated file has a different
    overall digest. Running them through production main() would make every semantic control pass on
    the identity check alone and prove nothing about the check it targets.

Mutations are written to a temporary directory; the real seal is never modified. Reads only, imports
no candidate, touches no outcome.
"""

from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import shutil
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


def semantic_mutations(base: dict) -> list[tuple[str, dict]]:
    out: list[tuple[str, dict]] = []

    def add(label, fn):
        seal = copy.deepcopy(base)
        fn(seal)
        out.append((label, seal))

    def b8(seal):
        return seal["bindings"]["8_exact_rational_sign_classification_condition"]

    def src8(seal):
        return b8(seal)["implementation_condition_source"]

    def shift_tiers(seal):  # the historical Seal V1 defect
        cs = seal["cohort_structure_recomputed"]
        wrong = ["100K", "1M", "5M", "10M"]
        cs["tiers_in_order"] = wrong
        for field in ("question_counts", "archive_counts", "zero_compression_counts_gold_le_3"):
            cs[field] = dict(zip(wrong, list(cs[field].values())))

    def invert_condition(seal):  # the historical Seal V2 defect, in its most dangerous form
        b8(seal)["implementation_condition_verbatim"] = (
            "Implementation note, not a defect in this preregistration: before any run authorization, "
            "classify D_t from a rounded floating-point aggregate.")

    add("V1 defect: 500K dropped, 5M invented", shift_tiers)
    add("V2 defect: implementation condition inverted", invert_condition)

    # binding 8 - the pre-run implementation condition and its source
    add("implementation-condition fragment digest wrong",
        lambda s: b8(s).__setitem__("implementation_condition_sha256", "3" * 64))
    add("implementation-condition source commit unavailable",
        lambda s: src8(s).__setitem__("commit", "0" * 40))
    add("implementation-condition source path wrong",
        lambda s: src8(s).__setitem__(
            "path", "docs/v52/task4f1/COCHAIR_EXACT_BYTE_APPROVAL_T4F1_PREREG_2026-09-04.md"))
    add("binding 8 source artifact swapped",
        lambda s: src8(s).__setitem__("artifact_sha256", "0" * 64))

    # binding 8 - the section 6 preregistered rule
    add("binding 8 rule silently weakened",
        lambda s: b8(s).__setitem__(
            "preregistered_rule_verbatim",
            "**Sign-boundary arithmetic.** `D_t` is computed in floating point with a small tolerance."))
    add("binding 8 rule replaced by a strict true substring",
        lambda s: b8(s).__setitem__("preregistered_rule_verbatim", "**Sign-boundary arithmetic.**"))

    # binding 8 - metadata, nested and not
    add("binding 8 owner changed", lambda s: b8(s).__setitem__("owner", "scientific track"))
    add("binding 8 type changed", lambda s: b8(s).__setitem__("type", "OPTIONAL SUGGESTION"))
    add("binding 8 not_a_scientific_amendment flipped",
        lambda s: b8(s).__setitem__("not_a_scientific_amendment", False))
    add("binding 8 no_restated_wording rewritten",
        lambda s: b8(s).__setitem__("no_restated_wording", "nothing here is checked"))
    add("nested extraction_rule changed",
        lambda s: src8(s).__setitem__("extraction_rule", "any paragraph you like"))
    add("nested extraction_rule reworded but keeps the marker",
        lambda s: src8(s).__setitem__(
            "extraction_rule",
            "any paragraph at all; marker: 'Implementation note, not a defect in this preregistration:'"))
    add("nested source branch changed", lambda s: src8(s).__setitem__("branch", "some/other-branch"))
    add("nested source 'what' rewritten", lambda s: src8(s).__setitem__("what", "an unrelated document"))
    add("unexpected nested source field inserted",
        lambda s: src8(s).__setitem__("override", "classify D_t from a rounded aggregate"))
    add("unverified free-text field smuggled into binding 8",
        lambda s: b8(s).__setitem__(
            "condition", "Before any run authorization, classify D_t from a rounded aggregate."))

    # binding 2 - the cohort structure
    add("one question count off by one",
        lambda s: s["cohort_structure_recomputed"]["question_counts"].__setitem__("500K", 628))
    add("one archive count wrong",
        lambda s: s["cohort_structure_recomputed"]["archive_counts"].__setitem__("1M", 30))
    add("zero-compression count wrong",
        lambda s: s["cohort_structure_recomputed"]["zero_compression_counts_gold_le_3"].__setitem__("10M", 106))
    add("excluded-archive set truncated",
        lambda s: s["cohort_structure_recomputed"].__setitem__("excluded_archives", ["1M::5"]))

    # binding 7 - the execution conditions
    add("binding 7 condition text altered",
        lambda s: s["bindings"]["7_binding_execution_conditions"]["conditions_verbatim"].__setitem__(
            2, "3. **HMAC key custody.** May be stored in the repository."))
    add("binding 7 drops a condition",
        lambda s: s["bindings"]["7_binding_execution_conditions"]["conditions_verbatim"].pop())

    # approvals, boundary, superseded seals, draft
    add("co-chair approval digest wrong",
        lambda s: s["bindings"]["5_exact_byte_cochair_approval"].__setitem__("sha256", "1" * 64))
    add("approval commit not available locally",
        lambda s: s["bindings"]["4_head_researcher_rereview_decision"].__setitem__("commit", "0" * 40))
    add("V7 bound as a prerequisite",
        lambda s: s["provenance_not_prerequisites"]["v7_execution_package_audit"]
        .__setitem__("bound_as_prerequisite", True))
    add("outcome boundary weakened",
        lambda s: s["outcome_boundary_declaration"].__setitem__("mode_run_invocations", 1))
    add("superseded Seal V2 modified", lambda s: s["supersedes"].__setitem__("sha256", "2" * 64))
    add("superseded Seal V1 modified", lambda s: s["also_superseded"].__setitem__("sha256", "4" * 64))
    add("approved draft byte size wrong",
        lambda s: s["bindings"]["1_approved_preregistration_draft"].__setitem__("bytes", 14687))
    return out


def identity_controls(module, seal_path: Path, tmp: Path) -> list[tuple[str, Path]]:
    """Each case is a directory holding a seal file and sidecar, one of them sabotaged."""
    sidecar_name = seal_path.name + ".sha256"
    cases: list[tuple[str, Path]] = []

    def case(label: str, mutate) -> None:
        directory = tmp / label.replace(" ", "_")
        directory.mkdir()
        target = directory / seal_path.name
        shutil.copy2(seal_path, target)
        shutil.copy2(seal_path.parent / sidecar_name, directory / sidecar_name)
        mutate(target, directory / sidecar_name)
        cases.append((label, target))

    def one_byte(target: Path, _sidecar: Path) -> None:
        data = bytearray(target.read_bytes())
        data[-2] = data[-2] ^ 0x20  # flip one bit of one byte
        target.write_bytes(bytes(data))

    case("one-byte Seal V3 mutation", one_byte)
    case("missing sidecar", lambda _t, sidecar: sidecar.unlink())
    case("wrong sidecar digest",
         lambda _t, sidecar: sidecar.write_text(f"{'5' * 64}  {seal_path.name}\n", encoding="utf-8"))
    case("wrong sidecar filename",
         lambda _t, sidecar: sidecar.write_text(
             f"{module.ACCEPTED_SEAL_SHA256}  SOME_OTHER_SEAL.json\n", encoding="utf-8"))
    return cases


def main() -> int:
    module = load_verifier()
    seal_path = module.SEAL_PATH
    base = json.loads(seal_path.read_text(encoding="utf-8"))
    failures = 0

    def report(ok: bool, line: str) -> None:
        nonlocal failures
        if not ok:
            failures += 1
        print(("ok    " if ok else "FAIL  ") + line)

    print("-- production control --")
    with contextlib.redirect_stdout(io.StringIO()):
        production_rc = module.main()
    report(production_rc == 0, "the real seal passes production verification (identity + semantics)")

    print("\n-- identity layer --")
    with tempfile.TemporaryDirectory() as tmp:
        report(module.verify_identity(seal_path) == [], "control: the real seal file establishes its identity")
        for label, path in identity_controls(module, seal_path, Path(tmp)):
            report(bool(module.verify_identity(path)), f"blocked: {label}")

    print("\n-- semantic layer --")
    report(module.verify_semantics(base) == [], "control: the real seal passes every semantic check")
    for label, seal in semantic_mutations(base):
        report(bool(module.verify_semantics(seal)), f"blocked: {label}")

    total = 1 + 1 + 4 + 1 + len(semantic_mutations(base))
    print(f"\n{total - failures}/{total} controls behaved correctly")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
