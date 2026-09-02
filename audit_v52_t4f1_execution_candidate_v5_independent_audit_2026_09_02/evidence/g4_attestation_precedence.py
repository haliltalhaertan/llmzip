#!/usr/bin/env python3
"""Gate 4: status and attestation semantics.

Establishes (a) what the bound seal can and cannot express, (b) whether the declared
detached attestation authority actually exists and what it currently asserts, and
(c) whether the two disagree under the package's own precedence rule."""
import hashlib, json, sys
from pathlib import Path

V5 = Path(sys.argv[1]).resolve()
REPO = Path(sys.argv[2]).resolve()

seal = json.loads((V5 / "CANDIDATE_EXECUTION_SEAL.json").read_text(encoding="utf-8"))
smap = json.loads((V5 / "NORMATIVE_SOURCE_MAP.json").read_text(encoding="utf-8"))
byname = {f["concept"]: f for f in smap["fields"]}

acc = byname["post_audit_acceptance_state"]
sub = byname["candidate_submission_status"]

att_dir = REPO / "docs" / "v52" / "task4f1"
att_files = sorted(p.relative_to(REPO).as_posix() for p in att_dir.rglob("*") if p.is_file()) \
            if att_dir.is_dir() else []
attestations = {}
for rel in att_files:
    p = REPO / rel
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        doc = None
    attestations[rel] = {
        "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        "schema": (doc or {}).get("schema"),
        "decision": (doc or {}).get("decision"),
        "authoritative_status": ((doc or {}).get("sealed_candidate") or {}).get("authoritative_status"),
        "sealed_namespace": ((doc or {}).get("sealed_candidate") or {}).get("namespace"),
        "mentions_v5": bool(__import__("re").search(r"(?<![0-9A-Za-z])V5(?![0-9])|candidate_v5|v5_2026_09_02", p.read_text(encoding="utf-8"))),
        "mentions_withdrawal": any(w in p.read_text(encoding="utf-8").lower()
                                   for w in ("withdraw", "cc-01", "cc01", "revoke")),
    }

v5_attestations = [r for r, m in attestations.items()
                   if m["mentions_v5"] or (m["sealed_namespace"] or "").endswith("v5_2026_09_02")]

report = {
    "seal_top_level_keys": sorted(seal.keys()),
    "seal_has_bare_status_field": "status" in seal,
    "seal_status_at_audit_submission": seal.get("status_at_audit_submission"),
    "seal_status_semantics": seal.get("status_semantics"),
    "seal_declares_required_gates_all_pending": sorted(
        set(seal.get("required_independent_gates", {}).values())),
    "seal_stop_rule": seal.get("stop_rule"),
    "seal_stop_rule_names_wrong_audit_generation":
        "independent V4 audit" in (seal.get("stop_rule") or ""),
    "map_submission_concept": {"authoritative_path": sub["authoritative_path"],
                               "locator": sub["locator"], "value": sub["value"]},
    "map_acceptance_concept": {"authoritative_path": acc["authoritative_path"],
                               "locator": acc["locator"], "value": acc["value"]},
    "acceptance_authority_is_a_bound_payload": acc["authoritative_path"] in
        {"CANDIDATE_EXECUTION_SEAL.json", "PAYLOAD_HASHES.json", "EXECUTION_SPEC.md",
         "README.md", "NORMATIVE_SOURCE_MAP.json", "RUN_AUTHORIZATION_TEMPLATE.json",
         "DEPENDENCY_LOCK.txt", "v52_t4f1_beam_retrieval.py", "candidate_package_preflight.py"},
    "acceptance_authority_is_a_resolvable_file_path": (REPO / acc["authoritative_path"]).exists(),
    "attestation_directory": att_dir.relative_to(REPO).as_posix(),
    "attestation_directory_exists": att_dir.is_dir(),
    "attestation_files": attestations,
    "v5_attestation_records_present": v5_attestations,
    "v5_acceptance_state_has_no_record_at_declared_authority": not v5_attestations,
    "precedence_rules": smap["precedence_rules"],
}

# cross-boundary consistency: the bound seal says V4's package seal is withdrawn; the
# declared sole authority for current state still asserts V4 is sealed.
v4_att = attestations.get("docs/v52/task4f1/V4_HEAD_RESEARCHER_ACCEPTANCE_2026-09-02.json", {})
report["v4_disposition_in_bound_seal"] = (seal.get("supersedes_candidate") or {}).get("disposition")
report["v4_status_at_declared_authority"] = v4_att.get("authoritative_status")
report["v4_withdrawal_recorded_at_declared_authority"] = bool(v4_att.get("mentions_withdrawal"))
report["bound_seal_and_declared_authority_disagree_on_v4"] = (
    "withdrawn" in (report["v4_disposition_in_bound_seal"] or "").lower()
    and not v4_att.get("mentions_withdrawal")
    and (v4_att.get("authoritative_status") or "").startswith("SEALED")
)
print(json.dumps(report, indent=2, sort_keys=True))
