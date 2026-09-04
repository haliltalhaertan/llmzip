#!/usr/bin/env python3
"""Verify the sealed V52 Task 4F1 scientific preregistration (Seal V3).

Every binding is re-derived from source bytes rather than read back from the seal's own claims:

  * identity       before anything is read out of the seal, the file itself must hash to the pinned
                   accepted Seal V3 digest AND carry a sidecar that names the accepted filename and
                   declares that same digest - the verifier establishes which seal it is checking;
  * bindings 1-3   digests, and the draft's byte size, recomputed from the working tree;
  * binding 2      the cohort structure is RECOMPUTED from the sealed CSV and compared field by
                   field, and the tier set is required to be exactly {100K, 500K, 1M, 10M};
  * bindings 4-6   read out of the named commits and hashed; a commit that is not fetched is a
                   failure, not a soft pass, because an approval that cannot be checked is not
                   verified;
  * binding 7      section 8 is re-extracted from the approved draft, hashed, and its four numbered
                   conditions re-parsed and compared for exact equality;
  * binding 8      section 6 is re-extracted and hashed, the preregistered rule must appear in it
                   verbatim, and its origin artifact must be the same bytes as binding 4.

It also refuses a seal that binds the V7 execution track as a prerequisite, that weakens its
outcome-boundary declaration, or whose superseded V1 artifact has been edited.

This checker imports and executes no outcome-capable candidate and reads no retrieval-quality
outcome.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEAL_PATH = ROOT / "docs" / "v52" / "task4f1" / "TASK4F1_PREREGISTRATION_SEAL_V3_2026-09-04.json"
IMPL_NOTE_MARKER = "Implementation note, not a defect in this preregistration:"
RULE_MARKER = "**Sign-boundary arithmetic.**"
# The accepted Seal V3 identity. Pinned here so the verifier establishes WHICH seal it is checking
# before it checks anything inside it; the sidecar is cross-checked but is never the sole authority.
ACCEPTED_SEAL_SHA256 = "e906c6d2b68b103c6c21906cbdf44acba10e31b7e5e17ffd2c7d1bbfb7a95cf4"
ACCEPTED_SEAL_FILENAME = "TASK4F1_PREREGISTRATION_SEAL_V3_2026-09-04.json"
BINDING_8_FIELDS = frozenset({
    "type", "implementation_condition_source", "implementation_condition_verbatim",
    "implementation_condition_sha256", "preregistered_rule_source", "source_section_sha256",
    "preregistered_rule_verbatim", "owner", "not_a_scientific_amendment", "no_restated_wording",
})
BINDING_8_SOURCE_FIELDS = frozenset({
    "what", "branch", "commit", "path", "artifact_sha256", "extraction_rule",
})
# Descriptive binding-8 metadata carries no value that can be re-derived from another artifact, so
# it is pinned here by digest instead. Pinning the digest rather than the prose keeps the schema
# short and still makes any edit - a flipped "owner", a reworded claim - a BLOCKED.
BINDING_8_PINNED_SHA256 = {
    "type": "99abc8cd71e8112ed23c9ab7740ce0f8757b5607214cc7faa3673a3115d9e1f6",
    "owner": "8e5c51ad33dd035668a2d90a89df736f72ef3534f9e63a3f7c5e6d7007b7f604",
    "no_restated_wording": "0470e3134fd1437af00c2b5d254208b50e56256f9b152f8faf314ff81ef8a762",
    "preregistered_rule_source": "b43590c8a4ffffe5a210fe912c42ee53803f0a160a3dd3d58b9bfccfbc056367",
}
BINDING_8_SOURCE_PINNED_SHA256 = {
    "what": "674fc0c6f5cef2f1450355ad4f768f6850fedbff78b75b248bc45b4b3e050ec5",
    "extraction_rule": "900ef76ce074270f5e2e64aa220dca174971459df111940f35b55420501d6515",
}
TIER_ORDER = ["100K", "500K", "1M", "10M"]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def blob(commit: str, path: str) -> bytes | None:
    try:
        return subprocess.run(["git", "cat-file", "-p", f"{commit}:{path}"],
                              cwd=ROOT, check=True, capture_output=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def sha256_blob(commit: str, path: str) -> str | None:
    data = blob(commit, path)
    return None if data is None else sha256_bytes(data)


def paragraph_starting(text: str, marker: str) -> str | None:
    """The single paragraph of `text` that begins with `marker`, verbatim."""
    for para in text.split("\n\n"):
        if para.lstrip().startswith(marker):
            return para.strip()
    return None


def implementation_note(hr_text: str) -> str | None:
    """The authoritative A2 implementation-note paragraph, re-extracted from the HR re-review bytes."""
    return paragraph_starting(hr_text, IMPL_NOTE_MARKER)


def section(text: str, number: int) -> str:
    out, on = [], False
    for line in text.split("\n"):
        if line.startswith(f"## {number}."):
            on = True
        elif on and line.startswith("## "):
            break
        if on:
            out.append(line)
    return "\n".join(out).rstrip() + "\n"


def numbered_items(section_text: str) -> list[str]:
    items: list[str] = []
    for line in section_text.split("\n"):
        if re.match(r"^\d+\.\s", line):
            items.append(line.strip())
        elif items and line.startswith("   ") and line.strip():
            items[-1] += " " + line.strip()
    return items


def recompute_cohort(path: Path) -> dict:
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    eligible = [r for r in rows if r["primary_evidence_cohort_eligible"].strip().lower() == "true"]
    archive = lambda r: f"{r['tier']}::{r['conversation_id']}"
    tiers = sorted({r["tier"] for r in eligible},
                   key=lambda t: TIER_ORDER.index(t) if t in TIER_ORDER else 99)
    per = {t: [r for r in eligible if r["tier"] == t] for t in tiers}
    return {
        "tiers_in_order": tiers,
        "question_counts": {t: len(rs) for t, rs in per.items()},
        "archive_counts": {t: len({archive(r) for r in rs}) for t, rs in per.items()},
        "zero_compression_counts_gold_le_3":
            {t: sum(1 for r in rs if int(r["gold_source_unit_count"]) <= 3) for t, rs in per.items()},
        "eligible_questions": len(eligible),
        "eligible_archives": len({archive(r) for r in eligible}),
        "excluded_archives": sorted({archive(r) for r in rows} - {archive(r) for r in eligible}),
    }


def verify_identity(seal_path: Path) -> list[str]:
    """Establish WHICH seal this is, before trusting anything written inside it.

    All four must hold: the file hashes to the accepted Seal V3 digest; a sidecar exists beside it;
    the sidecar names exactly the accepted filename; and the sidecar declares that same digest. The
    pinned constant is the authority - the sidecar is a mutable file and is cross-checked, never
    trusted alone.
    """
    fail: list[str] = []
    if not seal_path.is_file():
        return [f"identity: seal file is missing at {seal_path}"]

    actual = sha256_file(seal_path)
    if actual != ACCEPTED_SEAL_SHA256:
        fail.append(f"identity: this is not the accepted Seal V3 - file hashes to {actual}, "
                    f"accepted is {ACCEPTED_SEAL_SHA256}")

    sidecar = seal_path.with_suffix(seal_path.suffix + ".sha256")
    if not sidecar.is_file():
        fail.append(f"identity: the seal sidecar {sidecar.name} is missing")
        return fail
    parts = sidecar.read_text(encoding="utf-8").split()
    if len(parts) != 2:
        fail.append("identity: the seal sidecar is not a single '<digest>  <filename>' line")
        return fail
    declared_digest, declared_name = parts
    if declared_name != ACCEPTED_SEAL_FILENAME:
        fail.append(f"identity: the sidecar names {declared_name!r}, expected {ACCEPTED_SEAL_FILENAME!r}")
    if declared_digest != ACCEPTED_SEAL_SHA256:
        fail.append(f"identity: the sidecar declares {declared_digest}, expected {ACCEPTED_SEAL_SHA256}")
    return fail


def verify_semantics(seal: dict) -> list[str]:
    """Check what the seal binds. Assumes identity has already been established."""
    b = seal["bindings"]
    fail: list[str] = []

    if seal.get("schema") != "V52_T4F1_SCIENTIFIC_PREREGISTRATION_SEAL_V3":
        fail.append("unexpected seal schema")

    # --- bindings 1-3: working-tree bytes -------------------------------------------------
    draft_rel = b["1_approved_preregistration_draft"]["path"]
    for label, rel, expected in (
        ("1 approved draft", draft_rel, b["1_approved_preregistration_draft"]["sha256"]),
        ("2 sealed 4F0 cohort", b["2_sealed_4f0_restricted_cohort"]["path"],
         b["2_sealed_4f0_restricted_cohort"]["sha256"]),
        ("3 accepted runner", b["3_accepted_runner"]["path_in_current_candidate"],
         b["3_accepted_runner"]["sha256"]),
    ):
        path = ROOT / rel
        if not path.is_file():
            fail.append(f"{label}: missing {rel}")
        elif sha256_file(path) != expected:
            fail.append(f"{label}: SHA256 mismatch ({sha256_file(path)})")

    draft_path = ROOT / draft_rel
    if draft_path.is_file():
        if draft_path.stat().st_size != b["1_approved_preregistration_draft"]["bytes"]:
            fail.append("1 approved draft: byte size mismatch")
    v4 = ROOT / b["3_accepted_runner"]["byte_identical_to"]
    if not v4.is_file() or sha256_file(v4) != b["3_accepted_runner"]["sha256"]:
        fail.append("3 accepted runner: not byte-identical to the accepted V4 runner")

    # --- binding 2: the structure is recomputed, never trusted -----------------------------
    cohort_path = ROOT / b["2_sealed_4f0_restricted_cohort"]["path"]
    if cohort_path.is_file():
        actual = recompute_cohort(cohort_path)
        declared = seal["cohort_structure_recomputed"]
        if actual["tiers_in_order"] != TIER_ORDER:
            fail.append(f"2 cohort: tier set is {actual['tiers_in_order']}, required {TIER_ORDER}")
        if b["2_sealed_4f0_restricted_cohort"].get("required_tier_set") != TIER_ORDER:
            fail.append("2 cohort: binding does not require the exact tier set")
        for field, value in actual.items():
            if declared.get(field) != value:
                fail.append(f"2 cohort: {field} disagrees with the cohort bytes "
                            f"(seal {declared.get(field)} vs recomputed {value})")

    # --- bindings 4-6: approval artifacts in their own commits -----------------------------
    for key, label in (
        ("4_head_researcher_rereview_decision", "4 HR re-review decision"),
        ("5_exact_byte_cochair_approval", "5 exact-byte co-chair approval"),
        ("6_head_researcher_authorization_schema_ratification", "6 HR authorization-schema ratification"),
    ):
        item = b[key]
        actual = sha256_blob(item["commit"], item["path"])
        if actual is None:
            fail.append(f"{label}: commit {item['commit'][:8]} not available locally "
                        f"(git fetch origin {item['branch']}) - an approval that cannot be checked is not verified")
        elif actual != item["sha256"]:
            fail.append(f"{label}: SHA256 mismatch ({actual})")

    # --- bindings 7-8: conditions checked against the draft's own bytes ---------------------
    if draft_path.is_file():
        draft_text = draft_path.read_text(encoding="utf-8")
        s8, s6 = section(draft_text, 8), section(draft_text, 6)

        b7 = b["7_binding_execution_conditions"]
        if sha256_bytes(s8.encode("utf-8")) != b7["source_section_sha256"]:
            fail.append("7 execution conditions: section 8 of the draft does not match the sealed section digest")
        items = numbered_items(s8)
        if len(items) != 4:
            fail.append(f"7 execution conditions: section 8 yields {len(items)} numbered conditions, expected 4")
        if items != b7["conditions_verbatim"]:
            fail.append("7 execution conditions: bound text differs from section 8 of the approved draft")

        b8 = b["8_exact_rational_sign_classification_condition"]
        if set(b8) != set(BINDING_8_FIELDS):
            unexpected = sorted(set(b8) - BINDING_8_FIELDS)
            missing = sorted(BINDING_8_FIELDS - set(b8))
            fail.append(f"8 exact-rational condition: field set is not the verified set "
                        f"(unexpected {unexpected}, missing {missing}); an unverified field here is the "
                        f"escape that blocked Seal V2")
        for field, expected in BINDING_8_PINNED_SHA256.items():
            value = b8.get(field)
            if not isinstance(value, str) or sha256_bytes(value.encode("utf-8")) != expected:
                fail.append(f"8 exact-rational condition: pinned metadata field {field!r} was altered")
        if b8.get("not_a_scientific_amendment") is not True:
            fail.append("8 exact-rational condition: not_a_scientific_amendment must be true")
        if sha256_bytes(s6.encode("utf-8")) != b8.get("source_section_sha256"):
            fail.append("8 exact-rational condition: section 6 of the draft does not match the sealed section digest")
        authoritative_rule = paragraph_starting(s6, RULE_MARKER)
        if authoritative_rule is None:
            fail.append("8 exact-rational condition: the sign-boundary paragraph is absent from section 6")
        elif b8.get("preregistered_rule_verbatim") != authoritative_rule:
            fail.append("8 exact-rational condition: the bound preregistered rule is not the complete "
                        "section 6 paragraph (substring or altered text is not enough)")

        # The pre-run implementation condition is re-extracted from its authoritative HR bytes.
        src8 = b8.get("implementation_condition_source", {})
        if set(src8) != set(BINDING_8_SOURCE_FIELDS):
            unexpected = sorted(set(src8) - BINDING_8_SOURCE_FIELDS)
            missing = sorted(BINDING_8_SOURCE_FIELDS - set(src8))
            fail.append(f"8 exact-rational condition: source field set is not the verified set "
                        f"(unexpected {unexpected}, missing {missing})")
        for field, expected in BINDING_8_SOURCE_PINNED_SHA256.items():
            value = src8.get(field)
            if not isinstance(value, str) or sha256_bytes(value.encode("utf-8")) != expected:
                fail.append(f"8 exact-rational condition: pinned source field {field!r} was altered")
        # The source location is not restated: it must be the same branch, commit and path as the
        # approval bound at binding 4.
        b4 = b["4_head_researcher_rereview_decision"]
        for field in ("branch", "commit", "path"):
            if src8.get(field) != b4[field]:
                fail.append(f"8 exact-rational condition: source {field} does not match the HR re-review "
                            f"decision bound at binding 4")
        # The declared extraction rule must be the rule this verifier actually applies.
        if repr(IMPL_NOTE_MARKER) not in str(src8.get("extraction_rule", "")):
            fail.append("8 exact-rational condition: the declared extraction rule is not the marker the "
                        "verifier applies")
        if src8.get("artifact_sha256") != b4["sha256"]:
            fail.append("8 exact-rational condition: source artifact digest does not match the HR re-review decision")
        hr = blob(src8.get("commit", ""), src8.get("path", ""))
        if hr is None:
            fail.append(f"8 exact-rational condition: HR source commit {str(src8.get('commit'))[:8]} not available "
                        f"locally (git fetch origin {src8.get('branch')}) - an unreadable source is not verified")
        elif sha256_bytes(hr) != src8.get("artifact_sha256"):
            fail.append("8 exact-rational condition: HR source bytes do not hash to the declared artifact digest")
        else:
            extracted = implementation_note(hr.decode("utf-8"))
            if extracted is None:
                fail.append("8 exact-rational condition: the implementation note is absent from the HR source bytes")
            else:
                if b8.get("implementation_condition_verbatim") != extracted:
                    fail.append("8 exact-rational condition: the bound implementation condition is not the "
                                "verbatim text of the HR implementation note")
                if b8.get("implementation_condition_sha256") != sha256_bytes(extracted.encode("utf-8")):
                    fail.append("8 exact-rational condition: implementation-condition fragment digest mismatch")

    # --- the seal may never become contingent on the execution track ------------------------
    v7 = seal["provenance_not_prerequisites"]["v7_execution_package_audit"]
    if v7.get("bound_as_prerequisite") is not False:
        fail.append("V7 is bound as a prerequisite; the sealing direction forbids this")

    # --- every superseded seal must stay byte-unchanged -------------------------------------
    for key, label in (("supersedes", "Seal V2"), ("also_superseded", "Seal V1")):
        entry = seal[key]
        path = ROOT / entry["seal"]
        if not path.is_file():
            fail.append(f"superseded {label} is missing; it must be preserved as a historical artifact")
        elif sha256_file(path) != entry["sha256"]:
            fail.append(f"superseded {label} has been modified; it must be preserved byte-unchanged")

    # --- the boundary declaration must stay all zero / all false ----------------------------
    for key, value in seal["outcome_boundary_declaration"].items():
        if value not in (0, False):
            fail.append(f"outcome boundary violated: {key}={value}")

    return fail


def main() -> int:
    identity = verify_identity(SEAL_PATH)
    seal = json.loads(SEAL_PATH.read_text(encoding="utf-8")) if SEAL_PATH.is_file() else {}
    fail = identity + (verify_semantics(seal) if seal else [])
    if fail:
        print("PREREGISTRATION_SEAL: BLOCKED")
        for f in fail:
            print(f"- {f}")
        return 1
    b = seal["bindings"]
    sup = seal["supersedes"]
    print("PREREGISTRATION_SEAL: PASS")
    print(f"identity=sha256 {ACCEPTED_SEAL_SHA256} (pinned constant and sidecar agree)")
    print(f"seal_id={seal['seal_id']}")
    print(f"approved_draft_sha256={b['1_approved_preregistration_draft']['sha256']}")
    print(f"tiers={seal['cohort_structure_recomputed']['tiers_in_order']} "
          f"n={list(seal['cohort_structure_recomputed']['question_counts'].values())}")
    print(f"supersedes={sup['sha256']} (Seal V2, BLOCKED) and {seal['also_superseded']['sha256']} "
          f"(Seal V1, BLOCKED); both preserved unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
