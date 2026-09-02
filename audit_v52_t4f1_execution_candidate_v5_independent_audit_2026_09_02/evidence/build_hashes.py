#!/usr/bin/env python3
"""Build INDEPENDENT_V5_EXECUTION_AUDIT_HASHES.json: hashes every recursive output in the
audit namespace except itself, and binds the exact V5 anchors."""
import hashlib, json, sys
from pathlib import Path

AUD = Path(sys.argv[1]).resolve()
SELF = "INDEPENDENT_V5_EXECUTION_AUDIT_HASHES.json"


def sha(p):
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


files = {}
for p in sorted(AUD.rglob("*")):
    if p.is_file():
        rel = p.relative_to(AUD).as_posix()
        if rel == SELF:
            continue
        files[rel] = {"bytes": p.stat().st_size, "sha256": sha(p)}

doc = {
    "schema": "V52_T4F1_V5_INDEPENDENT_DELTA_AUDIT_HASHES_V1",
    "role": "cold-start independent implementation auditor",
    "audit_date_utc": "2026-09-02",
    "audit_namespace": AUD.name,
    "audit_branch": "audit/v52-t4f1-v5-independent-2026-09-02",
    "audited_repository_commit": "4244485c5aa874130026d44cd20104118361c9a7",
    "audited_repository_commit_descendant_checked": {
        "commit": "c44495f6fc365ee1957e8029c42fc6fd45d0b0bd",
        "files_changed_vs_audited_commit": ["docs/CONTINUITY_LEDGER.md", "ops/CURRENT_STATE.json"],
        "v5_candidate_namespace_byte_identical_at_both": True,
    },
    "instruction_set": {
        "path": "prompts/V52_TASK_4F1_EXECUTION_CANDIDATE_V5_INDEPENDENT_DELTA_AUDIT_PROMPT_2026-09-02.md",
        "sha256": "a9d95906ca04aba83d812d80e4906fab181ff31d12bdd8c122385b7e0270e0bb",
    },
    "self_excluded_file": SELF,
    "recursive_output_count": len(files),
    "files": files,

    "audited_candidate": {
        "namespace": "task4f1_execution_candidate_v5_2026_09_02",
        "recursive_file_count": 9,
        "nested_files": 0,
        "pycache_entries": 0,
        "implementation_sha256": "f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8",
        "payload_inventory_sha256": "171acc06bdc8d791518f95bf7679ad91bd7f67c42f7ede7b7195a62597731b4e",
        "execution_seal_sha256": "e8f2f9e87a46d96fbec744e6bd5b0ca494755a023aeb592d206762da0d1a40cc",
        "normative_source_map_sha256": "d64b865c200f3857659cf3da021e934d5b69e01770b3c549a50e0a35dc697002",
        "execution_spec_sha256": "e649476303207fd59d2135500f63cec3b69b2950e63c447ef8c197ddbe9b54a4",
        "package_preflight_sha256": "0b0a57f838c9437233f90f8870dcf0998bab6612af6b736ba84cb11594e1bd94",
        "readme_sha256": "334745497dc35ff2cb4f9f7ae719360410cf93cac9e5a4f28db2351b671f77fa",
        "run_authorization_template_sha256": "df1e9f8a53199ad82cc04b680893581dc1976db3a449e7b801ad495e9ebf79e9",
        "dependency_lock_sha256": "86a4db447ea3f9403231f53556be19ed07763c6e2eb0de42c83807505066655e",
        "status_at_audit_submission": "PREPARED_NOT_INDEPENDENTLY_AUDITED",
        "authorization_key_commitment": "PENDING_HEAD_RESEARCHER_PREREGISTRATION",
        "bytes_modified_by_this_audit": False,
        "all_six_prompt_declared_hashes_matched": True,
    },
    "implementer_evidence_read_only": {
        "namespace": "task4f1_execution_candidate_v5_preflight_2026_09_02",
        "preflight_hashes_sha256": "b6fb9cfd4e7517857072ff939a39022d5185e161a9ac0c57319b931a6f316b0f",
        "declarative_change_evidence_sha256": "80dbab381988b501513040f4e95fde4af76a13cdf42f34e5a73aa7b35bfa80cb",
        "single_source_gate_fixtures_sha256": "909ce3769ce3ae318b5541a4c051f469bde32f11872ad3dced085f0a93e0e0f4",
        "implementation_preflight_sha256": "ed430708e5c42e14303f296c5970dad755256ec7715e81bd1946e3f5bba876fc",
        "used_as_evidence": False,
        "read_for_coverage_only": True,
    },
    "preserved_read_only": {
        "accepted_v4_runner_sha256": "f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8",
        "v4_candidate_seal_sha256": "1bf740f573fc74c6e8aa6e23a3f07a5bcc97a10d1fa7e6e7358560e1598f06e9",
        "v4_candidate_recursive_file_count": 8,
        "v4_candidate_bytes_modified_by_this_audit": False,
        "v4_audit_branch": "audit/v52-t4f1-v4-independent-2026-09-01",
        "v4_audit_commit": "641568d8b78af97eb69c9dc4e0434e7b6564a26c",
        "v4_audit_hashes_sha256": "8dcb2fb8b23980fd3fe0e65a25834e1af259bdef855ed577ae40ab4a43ee4387",
        "v4_audit_manifest_entries_verified": "30/30",
        "v4_audit_manifest_authentic": True,
        "cochair_review_commit": "776c45f333b262754aa0020e8043db54942d1bea",
        "cochair_approval_commit": "4bd32782c4148d15a632fb822dae8cab358892c6",
        "detached_v4_acceptance_sha256": "f04eecd5f1b9e81aa2bb90830d3c678deb9dcf80adc335130e54314ac5f6c547",
    },
    "upstream_anchors_independently_verified": {
        "beam_pinned_commit": "3e12035532eb85768f1a7cd779832b650c4b2ef9",
        "beam_tree_manifest_sha256": "650cc145b853314411b1f4a9b762e6f64b33132f74f93cbb0638490319d8d318",
        "beam_selected_blobs_verified": "205/205",
        "beam_selected_total_bytes": 804231963,
        "restricted_cohort_sha256": "9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a",
        "cohort_total_rows": 2000,
        "cohort_eligible_rows": 1712,
        "cohort_archives": 96,
        "cohort_excluded_archives": ["1M::5", "1M::26", "1M::33", "1M::34"],
        "sealed_4f0_final_seal_sha256": "596c8056342e75110a940ee838cb080e9cd830f269aca0d1d87a0c4d482f859c",
        "restricted_protocol_sha256": "f75e6c93adc33b9db19be7c58240c7a0b38e3082a4f5b79ef67aad7c66493cf1",
        "dependency_lock_sha256": "86a4db447ea3f9403231f53556be19ed07763c6e2eb0de42c83807505066655e",
        "llmzip_parent_commit": "d3c7aa09c9553cd5ac100e668923abab602e4257",
        "all_independently_verified": True,
    },
    "environment": {
        "python": "3.12.13",
        "python_source_tarball_sha256": "0816c4761c97ecdb3f50a3924de0a93fd78cb63ee8e6c04201ddfaedca500b0b",
        "python_built_from_source": True,
        "numpy": "2.3.2", "scipy": "1.16.1", "scikit_learn": "1.7.1", "psutil": "7.0.0",
        "single_thread_controls": ["OMP_NUM_THREADS=1", "MKL_NUM_THREADS=1",
                                   "OPENBLAS_NUM_THREADS=1", "NUMEXPR_NUM_THREADS=1",
                                   "PYTHONHASHSEED=0"],
        "bytecode_disabled": "-B and PYTHONDONTWRITEBYTECODE=1",
        "numerical_backend_observed": "scipy-openblas 0.3.30; OPENBLAS_CORETYPE unset",
    },
    "delta_route": {
        "precondition_1_runner_byte_identity": "PASS",
        "precondition_2_runner_ast_equality": "PASS",
        "precondition_3_inputs_and_estimand_anchors_unchanged": "PASS",
        "precondition_4_v4_audit_package_authentic": "PASS",
        "precondition_5_changes_declarative_only": "PASS",
        "precondition_6_single_source_gate_passes": "FAIL",
        "change_set_is_genuinely_declarative": True,
        "delta_route_justified": True,
        "delta_route_justification_note": "Preconditions 1-5 were established from the bytes, so "
            "delta scoping was correct. Precondition 6 fails on substance, which is why the "
            "verdict is BLOCKED rather than an expansion to full cold-start scope.",
        "numerical_semantic_drift": False,
    },
    "gate_results": {
        "gate1_recursive_byte_closure_and_bindings": "PASS",
        "gate2_v4_to_v5_declarative_change_isolation": "PASS",
        "gate3_single_source_normative_gate": "FAIL",
        "gate3_item_3_2_one_source_per_concept": "PASS",
        "gate3_item_3_3_all_repetitions_typed": "FAIL",
        "gate3_item_3_4_no_surviving_deprecated_literal": "PASS",
        "gate3_item_3_5_registry_exemption_exact": "PASS",
        "gate3_item_3_6_cc01_removed_one_canary_definition": "PASS",
        "gate3_item_3_7_gate_blocks_reintroduced_cc01": "PARTIAL",
        "gate3_item_3_8_coverage_not_under_declared": "FAIL",
        "gate4_status_and_attestation_semantics": "FAIL",
        "gate5_package_preflight_behaviour": "PARTIAL",
        "gate6_preserved_implementation_gates": "PASS_BY_CITATION_PLUS_OWN_REDERIVATION",
        "gate7_active_bug_hunt": "SEVEN_DEFECTS",
    },
    "gate6_citation_boundary": {
        "cited_from_v4_audit_not_rederived_here": [
            "B1_no_replace_finalization_and_crash_temp",
            "B2_exact_gold_metric_recomputation",
            "B3_native_signed_exact_top3_and_distance",
            "output_schema_and_aggregation",
            "static_leakage_audit",
        ],
        "rederived_independently_here": [
            "recursive_byte_closure", "v4_to_v5_change_isolation", "runner_byte_identity",
            "single_source_gate_claim", "status_and_attestation_semantics",
            "authorization_fail_closed", "canary_sign_digests_on_real_beam_data",
            "pinned_corpus_tree_manifest", "cohort_anchor", "package_preflight_fixtures",
        ],
    },
    "blocking_findings": [
        "G3_8_MISSING_CONCEPTS: methods/arm identifiers and tie priority undeclared; five "
        "load-bearing runner anchors (BEAM tree manifest, 4F0 final seal, restricted protocol, "
        "parent commit, TIE_PREFIX) have no declared concept",
        "G3_3_UNLABELLED_SECOND_NORMATIVE_SOURCES: 19 repetitions of declared authoritative "
        "values in bound payloads that are neither the authoritative path nor a declared mirror",
        "G4_ATTESTATION_AUTHORITY_UNRESOLVED: declared sole authority holds no V5 record, is not "
        "a resolvable path, and contradicts the bound seal on V4's withdrawal",
        "G7_GATE_DOES_NOT_ESTABLISH_ITS_CLAIM: literal scan defeated by line splitting and "
        "casing; vacuous on an emptied registry or a dropped concept; a new contradictory "
        "normative source is not detected; acceptance re-enters the seal under an alias field",
    ],
    "non_blocking_observations": [
        "README.md title still reads 'Execution Implementation Candidate V4' inside V5",
        "canary README mirror locator points at the V5 change summary but the restatement sits "
        "in the V4-versus-V3 section",
        "seal stop_rule requires a fresh independent 'V4' audit inside a V5 package",
        "byte-identical runner reads seal['status'], which V5 removed, so its preflight "
        "provenance emits execution_seal_status: null",
        "gate prints '5 typed mirrors equal' against 13 declared mirrors",
    ],
    "outcome_boundary": {
        "cli_mode_run_count": 0,
        "cli_mode_finalize_count": 0,
        "cli_mode_preflight_count": 1,
        "hmac_key_env_set_count": 0,
        "valid_production_authorization_constructed": False,
        "real_retrieval_ranking_performed": False,
        "retrieval_quality_computed": False,
        "retrieval_quality_read": False,
        "retrieval_quality_reported": False,
        "candidate_bytes_modified": False,
        "seals_or_authorization_fields_modified": False,
        "v1_v2_v3_v4_or_sealed_4f0_namespaces_modified": False,
        "run_archives_called_on_real_beam_data": False,
        "evaluate_archive_called_on_real_beam_data": False,
        "finalize_results_called_on_real_beam_data": False,
        "guarded_launches": 13,
        "commands_refused_before_launch": 6,
        "harness": "evidence/guarded_run.py",
    },
    "verdict": "BLOCKED - DO NOT SEAL / DO NOT PREREGISTER / DO NOT RUN TASK 4F1",
}
out = AUD / SELF
out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print("wrote", out)
print("recursive_output_count", len(files))
