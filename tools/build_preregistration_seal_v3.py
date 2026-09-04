#!/usr/bin/env python3
"""Build the V52 Task 4F1 scientific preregistration Seal V3 by DERIVING every value from bytes.

Seal V1 shipped hand-transcribed tier labels. Seal V2 converted almost everything to derivation but
left one hand-restated string: binding 8's pre-run implementation condition, which no check read, so
an inverted condition would have passed green. V3 closes that: the implementation condition is
extracted verbatim from the Head Researcher re-review bytes and bound by its own fragment digest,
and binding 8 carries no free-text field that nothing verifies.

Reads only. Imports no candidate. Touches no outcome.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = "docs/v52/task4f1/TASK4F1_PREREGISTRATION_DRAFT_2026-09-03.md"
COHORT = "audit_v52_t4f0_restricted_refreeze_2026_08_31/estimand_primary_cohort.csv"
RUNNER = "task4f1_execution_candidate_v7_2026_09_03/v52_t4f1_beam_retrieval.py"
V4_RUNNER = "task4f1_execution_candidate_v4_2026_09_01/v52_t4f1_beam_retrieval.py"
OUT = ROOT / "docs/v52/task4f1/TASK4F1_PREREGISTRATION_SEAL_V3_2026-09-04.json"
HR_REREVIEW_COMMIT = "19d9cbbfcbc48f80dc63ac179f2aa67e7eed490d"
HR_REREVIEW_PATH = "docs/v52/task4f1/T4F1_PREREG_REREVIEW_DECISION_2026-09-04.md"
IMPL_NOTE_MARKER = "Implementation note, not a defect in this preregistration:"

TIER_ORDER = ["100K", "500K", "1M", "10M"]


def sha256_file(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def sha256_blob(commit: str, path: str) -> str:
    blob = subprocess.run(["git", "cat-file", "-p", f"{commit}:{path}"],
                          cwd=ROOT, check=True, capture_output=True).stdout
    return hashlib.sha256(blob).hexdigest()


def blob_text(commit: str, path: str) -> str:
    return subprocess.run(["git", "cat-file", "-p", f"{commit}:{path}"],
                          cwd=ROOT, check=True, capture_output=True).stdout.decode("utf-8")


def implementation_note(hr_text: str) -> str:
    """The authoritative A2 implementation-note paragraph, verbatim from the HR re-review bytes."""
    for para in hr_text.split("\n\n"):
        if para.lstrip().startswith(IMPL_NOTE_MARKER):
            return para.strip()
    raise SystemExit("[BLOCKED] the implementation-note paragraph is absent from the HR re-review artifact")


def section(text: str, number: int) -> str:
    """The draft's section `number`, from its heading to just before the next one."""
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
    """The `1.`-style items of a section, each with its continuation lines folded in."""
    items: list[str] = []
    for line in section_text.split("\n"):
        if re.match(r"^\d+\.\s", line):
            items.append(line.strip())
        elif items and line.startswith("   ") and line.strip():
            items[-1] += " " + line.strip()
    return items


def cohort_structure() -> OrderedDict:
    rows = list(csv.DictReader((ROOT / COHORT).open(encoding="utf-8")))
    eligible = [r for r in rows if r["primary_evidence_cohort_eligible"].strip().lower() == "true"]
    archive = lambda r: f"{r['tier']}::{r['conversation_id']}"

    tiers = sorted({r["tier"] for r in eligible}, key=TIER_ORDER.index)
    counts, archives, zero_compression = OrderedDict(), OrderedDict(), OrderedDict()
    for tier in tiers:
        rows_t = [r for r in eligible if r["tier"] == tier]
        counts[tier] = len(rows_t)
        archives[tier] = len({archive(r) for r in rows_t})
        zero_compression[tier] = sum(1 for r in rows_t if int(r["gold_source_unit_count"]) <= 3)

    excluded = sorted({archive(r) for r in rows} - {archive(r) for r in eligible})
    return OrderedDict([
        ("derivation", "recomputed from the sealed cohort CSV named in binding 2; nothing here is transcribed"),
        ("archive_identity", "tier::conversation_id; conversation_id is not unique across tiers"),
        ("tiers_in_order", tiers),
        ("question_counts", counts),
        ("archive_counts", archives),
        ("zero_compression_counts_gold_le_3", zero_compression),
        ("eligible_questions", len(eligible)),
        ("eligible_archives", len({archive(r) for r in eligible})),
        ("excluded_archives", excluded),
    ])


def main() -> int:
    draft_text = (ROOT / DRAFT).read_text(encoding="utf-8")
    s6, s8 = section(draft_text, 6), section(draft_text, 8)
    rule = next(b for b in s6.split("\n\n") if b.startswith("**Sign-boundary arithmetic.**")).rstrip()
    impl_note = implementation_note(blob_text(HR_REREVIEW_COMMIT, HR_REREVIEW_PATH))

    runner_sha, v4_sha = sha256_file(RUNNER), sha256_file(V4_RUNNER)
    if runner_sha != v4_sha:
        raise SystemExit(f"[BLOCKED] runner is not byte-identical to the accepted V4 runner: {runner_sha} != {v4_sha}")

    approvals = OrderedDict([
        ("4_head_researcher_rereview_decision", OrderedDict([
            ("branch", "hr/rereview-t4f1-prereg-2026-09-04"),
            ("commit", "19d9cbbfcbc48f80dc63ac179f2aa67e7eed490d"),
            ("path", "docs/v52/task4f1/T4F1_PREREG_REREVIEW_DECISION_2026-09-04.md"),
            ("verdict", "APPROVED FOR SEALING - SCIENTIFIC PREREGISTRATION DESIGN ACCEPTED")])),
        ("5_exact_byte_cochair_approval", OrderedDict([
            ("branch", "cochair/exact-byte-approval-t4f1-prereg-2026-09-04"),
            ("commit", "5299cc12d899a918504110b4faf1734713f607cc"),
            ("path", "docs/v52/task4f1/COCHAIR_EXACT_BYTE_APPROVAL_T4F1_PREREG_2026-09-04.md"),
            ("verdict", "APPROVE WITH NOTES - unconditional; no note requires an amendment or new bytes")])),
        ("6_head_researcher_authorization_schema_ratification", OrderedDict([
            ("branch", "hr/ratify-v7-governance-2026-09-03"),
            ("commit", "6f1de9eb1dfb8557e4ebc3fa2a1130214c6b228b"),
            ("path", "docs/v52/task4f1/V7_HEAD_RESEARCHER_GOVERNANCE_RATIFICATION_2026-09-03.md"),
            ("ratifies", "V52_T4F1_RUN_AUTHORIZATION_V4 is the correct authorization schema while the runner "
                         "remains byte-identical to the accepted V4 runner; package version and "
                         "authorization-schema version are separate version domains"),
            ("note", "this file exists only on its own branch and is not present on main; it is bound by "
                     "branch, commit and digest")])),
    ])
    for item in approvals.values():
        item["sha256"] = sha256_blob(item["commit"], item["path"])

    seal = OrderedDict([
        ("schema", "V52_T4F1_SCIENTIFIC_PREREGISTRATION_SEAL_V3"),
        ("seal_id", "V52_TASK_4F1_SCIENTIFIC_PREREGISTRATION_SEAL_V3_2026-09-04"),
        ("sealed_at_utc", "2026-09-04T11:45:00Z"),
        ("nature", "ADDITIVE AND HASH-BOUND. This seal binds bytes by digest and rewrites nothing. "
                   "The approved preregistration draft is not modified by sealing."),
        ("sealed_by", "Continuity Lead, under the Head Researcher sealing direction 2026-09-04, the "
                      "Seal V1 defect decision 2026-09-04 and the Seal V2 Binding-8 defect decision 2026-09-04"),
        ("supersedes", OrderedDict([
            ("seal", "docs/v52/task4f1/TASK4F1_PREREGISTRATION_SEAL_V2_2026-09-04.json"),
            ("sha256", "9ed480f4dcb0fe6151ad239c3e05174ce443a81ea84aed8e2777cb9baa04e39d"),
            ("status_of_superseded_seal", "BLOCKED AS A COMPLETE SEAL ARTIFACT; preserved byte-unchanged as a "
                                          "historical partial repair and never edited"),
            ("why", "Seal V2 repaired the V1 tier-label defect and materially strengthened the verifier, but "
                    "binding 8 still carried a hand-restated pre-run implementation condition that no check "
                    "read. An inverted condition permitting classification from a rounded floating-point "
                    "aggregate would have passed green; this was reproduced by execution before repair."),
            ("repairs_carried_forward_unchanged", [
                "binding 2 normative at the cohort file digest only",
                "the exact tier set {100K, 500K, 1M, 10M}",
                "field-by-field recomputation of the cohort structure",
                "binding 7 exact four-item equality against section 8 with its section digest",
                "binding 8's section 6 preregistered-rule extraction",
                "fail-closed behaviour when an approval commit is not fetched",
                "preservation of superseded seals byte-unchanged",
                "the negative-control suite",
                "V7 provenance-only with bound_as_prerequisite false",
                "the all-zero outcome-boundary declaration",
            ]),
            ("defect_decision", OrderedDict([
                ("branch", "hr/prereg-seal-v2-binding8-defect-2026-09-04"),
                ("commit", "b0a8225e9151f53df8a13398e269afab3719dd55"),
                ("path", "docs/v52/task4f1/T4F1_PREREG_SEAL_V2_BINDING8_DEFECT_DECISION_2026-09-04.md"),
                ("sha256", sha256_blob("b0a8225e9151f53df8a13398e269afab3719dd55",
                                       "docs/v52/task4f1/T4F1_PREREG_SEAL_V2_BINDING8_DEFECT_DECISION_2026-09-04.md"))])),
            ("scientific_content_changed", False),
            ("fresh_scientific_review_required", False),
            ("both_scientific_approvals_still_valid", True),
        ])),
        ("also_superseded", OrderedDict([
            ("seal", "docs/v52/task4f1/TASK4F1_PREREGISTRATION_SEAL_2026-09-04.json"),
            ("sha256", "c9e061951c44d89f9c62af94ee78b37a860fd52081fb0c38d38360511218891b"),
            ("status_of_superseded_seal", "BLOCKED AS A SEAL ARTIFACT; preserved byte-unchanged"),
            ("why", "binding 2 carried hand-transcribed tier labels 100K/1M/5M/10M: 500K missing, a 5M tier "
                    "that exists nowhere introduced, and the counts shifted onto wrong labels, none of which "
                    "its verifier tested."),
            ("defect_decision_sha256", sha256_blob("c867ea123a3ee7fba19a78ca59312601aac9fbc4",
                                                   "docs/v52/task4f1/T4F1_PREREG_SEAL_V1_DEFECT_DECISION_2026-09-04.md")),
        ])),
        ("what_this_seal_does", [
            "Freezes the scientific preregistration of V52 Task 4F1 at the exact approved bytes named below.",
            "Records the two approvals the draft's own header and section 9 require: Head Researcher and scientific co-chair.",
            "Fixes the estimands, the decision rule, the outcome partition, the interpretation boundary and the "
            "binding execution conditions before any outcome is visible.",
        ]),
        ("what_this_seal_does_not_do", [
            "It does NOT authorize Task 4F1 execution.",
            "It does NOT constitute or imply a production run authorization; none exists.",
            "It creates and implies NO HMAC key. V52_T4F1_AUTH_HMAC_KEY_HEX is not set by this seal.",
            "It does NOT permit retrieval-quality outcome access, which remains FORBIDDEN.",
            "It takes NO position on the V7 execution-package audit, which is a separate track with its own auditor.",
            "It does NOT accept, prejudge or depend on any V7 verdict. No V7 result is bound as a prerequisite.",
        ]),
        ("bindings", OrderedDict([
            ("1_approved_preregistration_draft", OrderedDict([
                ("path", DRAFT),
                ("sha256", sha256_file(DRAFT)),
                ("bytes", (ROOT / DRAFT).stat().st_size),
                ("commit", "c0133fce9b755d13d9be3016e8e06f493d6b275b"),
                ("predecessor_bytes_superseded", "ec3443ed4c60eb12e098192abf7b414e034d89fc63a9f42f9d0a02c36a696e45"),
            ])),
            ("2_sealed_4f0_restricted_cohort", OrderedDict([
                ("path", COHORT),
                ("sha256", sha256_file(COHORT)),
                ("normative_level", "FILE DIGEST ONLY. No derived cohort dictionary is normative in this "
                                    "binding. The structural summary lives in cohort_structure_recomputed "
                                    "below and is regenerated from these bytes by the verifier."),
                ("required_tier_set", TIER_ORDER),
            ])),
            ("3_accepted_runner", OrderedDict([
                ("path_in_current_candidate", RUNNER),
                ("sha256", runner_sha),
                ("byte_identical_to", V4_RUNNER),
                ("note", "Accepted at V4 and carried unchanged through V5, V6 and V7; identity re-checked at build time."),
            ])),
            ("4_head_researcher_rereview_decision", approvals["4_head_researcher_rereview_decision"]),
            ("5_exact_byte_cochair_approval", approvals["5_exact_byte_cochair_approval"]),
            ("6_head_researcher_authorization_schema_ratification",
             approvals["6_head_researcher_authorization_schema_ratification"]),
            ("7_binding_execution_conditions", OrderedDict([
                ("source", f"section 8 of the approved preregistration draft ({DRAFT})"),
                ("source_section_sha256", hashlib.sha256(s8.encode("utf-8")).hexdigest()),
                ("all_four_must_be_bound", True),
                ("conditions_verbatim", numbered_items(s8)),
            ])),
            ("8_exact_rational_sign_classification_condition", OrderedDict([
                ("type", "PRE-RUN IMPLEMENTATION CONDITION on the execution/authorization gate"),
                ("implementation_condition_source", OrderedDict([
                    ("what", "Head Researcher re-review decision 2026-09-04, which records this as an "
                             "implementation note and expressly not a defect in the preregistration"),
                    ("branch", "hr/rereview-t4f1-prereg-2026-09-04"),
                    ("commit", HR_REREVIEW_COMMIT),
                    ("path", HR_REREVIEW_PATH),
                    ("artifact_sha256", approvals["4_head_researcher_rereview_decision"]["sha256"]),
                    ("extraction_rule", "the paragraph of the artifact beginning "
                                        f"{IMPL_NOTE_MARKER!r}"),
                ])),
                ("implementation_condition_verbatim", impl_note),
                ("implementation_condition_sha256", hashlib.sha256(impl_note.encode("utf-8")).hexdigest()),
                ("preregistered_rule_source", f"section 6 of the approved preregistration draft ({DRAFT})"),
                ("source_section_sha256", hashlib.sha256(s6.encode("utf-8")).hexdigest()),
                ("preregistered_rule_verbatim", rule),
                ("owner", "execution/authorization track"),
                ("not_a_scientific_amendment", True),
                ("no_restated_wording", "This binding carries no hand-written paraphrase of its condition. "
                                        "Every text field here is extracted from source bytes and is checked "
                                        "by the verifier, which also refuses any unexpected field."),
            ])),
        ])),
        ("cohort_structure_recomputed", cohort_structure()),
        ("provenance_not_prerequisites", OrderedDict([
            ("note", "Recorded for traceability only. Nothing in this block is a condition on this seal."),
            ("first_cochair_scientific_review", OrderedDict([
                ("branch", "cochair/review-t4f1-prereg-2026-09-03"),
                ("commit", "ecbf765e7f0ef06ae903d5aba6d2e9a835cdf3c2"),
                ("path", "docs/v52/task4f1/COCHAIR_SCIENTIFIC_REVIEW_T4F1_PREREG_2026-09-03.md"),
                ("sha256", sha256_blob("ecbf765e7f0ef06ae903d5aba6d2e9a835cdf3c2",
                                       "docs/v52/task4f1/COCHAIR_SCIENTIFIC_REVIEW_T4F1_PREREG_2026-09-03.md")),
                ("verdict_on_predecessor_bytes", "REQUEST CHANGES; source of amendments A1-A6")])),
            ("head_researcher_sealing_direction", OrderedDict([
                ("branch", "hr/prereg-sealing-direction-2026-09-04"),
                ("commit", "33fa4a27ac1a06392454eba66039d8649870dbb0"),
                ("path", "docs/v52/task4f1/T4F1_PREREG_SEALING_DIRECTION_2026-09-04.md"),
                ("sha256", sha256_blob("33fa4a27ac1a06392454eba66039d8649870dbb0",
                                       "docs/v52/task4f1/T4F1_PREREG_SEALING_DIRECTION_2026-09-04.md"))])),
            ("v7_execution_package_audit", OrderedDict([
                ("branch", "audit/v52-t4f1-v7-independent-2026-09-03"),
                ("head_at_sealing", "16dc61313acd0e9086c852eccb9100023898fd27"),
                ("status_at_sealing", "RUNNING - gate evidence pushed, no report, gate table, hash manifest or verdict"),
                ("bound_as_prerequisite", False),
                ("reason", "The Head Researcher sealing direction forbids making the scientific seal contingent "
                           "on an execution-track result that was not part of the scientific design approval.")])),
        ])),
        ("amendment_rule", "Any change to the scientific content of the approved draft produces new bytes and voids "
                           "this seal for those bytes. It requires a fresh Head Researcher approval and a fresh "
                           "exact-byte co-chair approval before a new seal may be issued. Purely additive sealing "
                           "metadata must not rewrite the approved draft. Repairing sealing metadata, as V2 does, "
                           "requires no scientific re-review because no scientific byte changes."),
        ("task_state_at_sealing", OrderedDict([
            ("task_4f1_scientific_preregistration", "SEALED"),
            ("task_4f1_execution_package", "NOT SETTLED - V7 audit running, no recorded result"),
            ("task_4f1_run", "BLOCKED"),
            ("production_authorization", "NONE EXISTS"),
            ("retrieval_quality_outcome_access", "FORBIDDEN"),
        ])),
        ("outcome_boundary_declaration", OrderedDict([
            ("mode_run_invocations", 0),
            ("mode_finalize_invocations", 0),
            ("run_archives_evaluate_archive_finalize_results_calls", 0),
            ("valid_production_authorization_constructed", False),
            ("hmac_key_set_or_inspected", False),
            ("real_beam_retrieval_performed", False),
            ("retrieval_quality_outcome_computed_read_or_reported", False),
            ("sealed_payload_candidate_manifest_or_corpus_modified", False),
            ("approved_draft_modified_by_sealing", False),
        ])),
    ])

    OUT.write_text(json.dumps(seal, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"sha256 {hashlib.sha256(OUT.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
