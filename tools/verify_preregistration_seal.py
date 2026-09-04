#!/usr/bin/env python3
"""Verify the sealed V52 Task 4F1 scientific preregistration (Seal V2).

Every binding is re-derived from source bytes rather than read back from the seal's own claims:

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
SEAL_PATH = ROOT / "docs" / "v52" / "task4f1" / "TASK4F1_PREREGISTRATION_SEAL_V2_2026-09-04.json"
TIER_ORDER = ["100K", "500K", "1M", "10M"]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_blob(commit: str, path: str) -> str | None:
    try:
        blob = subprocess.run(["git", "cat-file", "-p", f"{commit}:{path}"],
                              cwd=ROOT, check=True, capture_output=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return sha256_bytes(blob)


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


def main() -> int:
    seal = json.loads(SEAL_PATH.read_text(encoding="utf-8"))
    b = seal["bindings"]
    fail: list[str] = []

    if seal.get("schema") != "V52_T4F1_SCIENTIFIC_PREREGISTRATION_SEAL_V2":
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
        if sha256_bytes(s6.encode("utf-8")) != b8["source_section_sha256"]:
            fail.append("8 exact-rational condition: section 6 of the draft does not match the sealed section digest")
        if b8["preregistered_rule_verbatim"].strip() not in s6:
            fail.append("8 exact-rational condition: the preregistered rule is not present verbatim in section 6")
        if b8["origin_artifact"]["sha256"] != b["4_head_researcher_rereview_decision"]["sha256"]:
            fail.append("8 exact-rational condition: origin artifact digest does not match the HR re-review decision")

    # --- the seal may never become contingent on the execution track ------------------------
    v7 = seal["provenance_not_prerequisites"]["v7_execution_package_audit"]
    if v7.get("bound_as_prerequisite") is not False:
        fail.append("V7 is bound as a prerequisite; the sealing direction forbids this")

    # --- the superseded V1 artifact must stay byte-unchanged --------------------------------
    sup = seal["supersedes"]
    v1 = ROOT / sup["seal"]
    if not v1.is_file():
        fail.append("superseded Seal V1 is missing; it must be preserved as a historical artifact")
    elif sha256_file(v1) != sup["sha256"]:
        fail.append("superseded Seal V1 has been modified; it must be preserved byte-unchanged")

    # --- the boundary declaration must stay all zero / all false ----------------------------
    for key, value in seal["outcome_boundary_declaration"].items():
        if value not in (0, False):
            fail.append(f"outcome boundary violated: {key}={value}")

    if fail:
        print("PREREGISTRATION_SEAL: BLOCKED")
        for f in fail:
            print(f"- {f}")
        return 1
    print("PREREGISTRATION_SEAL: PASS")
    print(f"seal_id={seal['seal_id']}")
    print(f"approved_draft_sha256={b['1_approved_preregistration_draft']['sha256']}")
    print(f"tiers={seal['cohort_structure_recomputed']['tiers_in_order']} "
          f"n={list(seal['cohort_structure_recomputed']['question_counts'].values())}")
    print(f"supersedes={sup['sha256']} (Seal V1, BLOCKED, preserved unchanged)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
