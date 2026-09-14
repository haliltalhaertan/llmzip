# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# Wraps raw harness arrays into final evidence envelopes with static findings.
# Outcome-free: reads candidate JSON/text bytes and hashes only.
import hashlib
import json
from pathlib import Path

NS = Path(__file__).resolve().parent.parent
CAND = Path("/home/mdp/muse-work/fix-v7-gapfill/task4f1_execution_candidate_v7_2026_09_03")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


seal = json.loads((CAND / "CANDIDATE_EXECUTION_SEAL.json").read_text(encoding="utf-8"))
manifest = json.loads((CAND / "PAYLOAD_HASHES.json").read_text(encoding="utf-8"))
runner = (CAND / "v52_t4f1_beam_retrieval.py").read_text(encoding="utf-8")
checker = (CAND / "candidate_package_preflight.py").read_text(encoding="utf-8")

static_g4 = {
    "seal_top_level_keys": sorted(seal.keys()),
    "seal_has_bare_status": "status" in seal,
    "seal_has_acceptance_state": "acceptance_state" in seal,
    "seal_has_accepted": "accepted" in seal,
    "seal_has_sealed": "sealed" in seal,
    "seal_status_at_audit_submission": seal.get("status_at_audit_submission"),
    "seal_has_status_semantics": "status_semantics" in seal,
    "seal_has_attestation_pointer": any(
        k in seal for k in ("attestation", "attestation_path", "acceptance_attestation")),
    "manifest_top_level_keys": sorted(manifest.keys()),
    "manifest_has_status_key": "status" in manifest,
    "signed_fields_include_status": "status" in seal.get("authorization_control", {}).get(
        "signed_fields", []),
    "runner_imports_checker": "candidate_package_preflight" in runner,
    "runner_mentions_current_state_or_ledger": ("CURRENT_STATE" in runner)
    or ("CONTINUITY_LEDGER" in runner),
    "runner_mentions_attestation": "ttestat" in runner,
    "runner_status_read_context": "runner line ~1219 execution_seal.get(\"status\") reads the "
    "RUNTIME execution seal supplied at run time, not CANDIDATE_EXECUTION_SEAL.json; "
    "runner AUTH_SIGNED_FIELDS (lines ~79-88) and line ~245 expected runtime value "
    "AUTHORIZED_FOR_TASK_4F1_EXECUTION concern runtime authorization, not package acceptance",
    "nothing_binds_seal_bytes": "PAYLOAD_HASHES.json covers 4 files; seal asserts "
    "payload_inventory.sha256 but no in-package hash covers CANDIDATE_EXECUTION_SEAL.json "
    "itself; root of trust is external prompt anchors only",
    "conclusion": "Status/attestation binding is sound against a non-resealing adversary "
    "(exact submission value pinned; four post-audit field names forbidden; inventory "
    "status forbidden; F5-style acceptance file blocked at all reseal levels by set "
    "equality) and vacuous against a full-reseal adversary (seal bytes unbound; "
    "status_semantics prose unpinned). No attestation pointer exists, so F5 redirection "
    "is inapplicable BY CONSTRUCTION; the residual risk is prose misdirection, not "
    "package misbinding.",
}

g4 = {"banner": "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] "
                "[DISCLOSE-BEFORE-USE] PREPARED NOT ACCEPTED",
      "gate": 4, "method": "candidate_package_preflight.py on pristine + 10 synthetic "
      "mutated copies in own namespace; static key analysis of seal/inventory/runner bytes",
      "candidate_hashes_reverified": {f.name: sha(f) for f in sorted(CAND.iterdir())
                                      if f.is_file()},
      "static_findings": static_g4,
      "cases": json.loads((NS / "evidence" / "g4_status_attestation.json").read_text(
          encoding="utf-8")),
      "boundary": {"mode_run_count": 0, "mode_finalize_count": 0, "hmac_env_set": 0,
                   "real_authorization_constructed": False, "retrieval_outcome": False,
                   "candidate_bytes_modified": False}}

static_g5 = {
    "check_mechanism": "set equality over file NAMES (declared manifest set vs "
    "EXPECTED_BOUND_PAYLOAD vs on-disk set) + per-file bytes+sha256 + runner V4 "
    "constant pin + template safety fields",
    "content_blindness": "g5_06 embeds a planted operator requirement inside "
    "RUN_AUTHORIZATION_TEMPLATE.json under its functional name, reseals manifest+seal, "
    "checker PASSES: set-equality sees names only. Corroborates branch g35 F06/F08.",
    "runner_pin": "runner sha pinned to V4 constant IN the checker; runner substitution "
    "fails even when resealed (branch g35 F21 BLOCKED).",
    "case_sensitivity": "g5_07: POSIX set-equality is case-sensitive; case-variant extra "
    "file BLOCKED by closure mismatch (branch g35 F09 agrees).",
    "conclusion": "All five mandated defeat classes (extra/missing/renamed/mutated/"
    "hash-mismatch) BLOCKED without reseal. With full reseal, name-level attacks still "
    "BLOCKED but content-under-functional-name SURVIVES: the claim is ESTABLISHED for "
    "file-set integrity, NOT-YET-FALSIFIED at best for content integrity of the three "
    "non-runner bound files.",
}

g5 = {"banner": "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] "
                "[DISCLOSE-BEFORE-USE] PREPARED NOT ACCEPTED",
      "gate": 5, "method": "candidate_package_preflight.py on pristine + 7 synthetic "
      "fixtures of own construction in own namespace (branch implementer fixtures read "
      "for coverage only, never as evidence)",
      "static_findings": static_g5,
      "cases": json.loads((NS / "evidence" / "g5_checker_fixtures.json").read_text(
          encoding="utf-8")),
      "boundary": {"mode_run_count": 0, "mode_finalize_count": 0, "hmac_env_set": 0,
                   "real_authorization_constructed": False, "retrieval_outcome": False,
                   "candidate_bytes_modified": False}}

(NS / "evidence" / "g4_status_attestation.json").write_text(
    json.dumps(g4, indent=2) + "\n", encoding="utf-8")
(NS / "evidence" / "g5_checker_fixtures.json").write_text(
    json.dumps(g5, indent=2) + "\n", encoding="utf-8")
print("envelopes written")
