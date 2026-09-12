# G-3 requirement → change → verification → disposition

All rows describe implementation-team evidence for a scoped synthetic candidate.
“Implemented” below does not mean accepted or execution-ready. Exact observed test
IDs, counts, source hashes and statuses are in `evidence/final/RESULTS.json`;
historical and adapted inherited suites are in `inherited/final/RESULTS.json`.
Provenance checks and diffs are in `provenance/final/RESULTS.json`.
The user's cold-start independent audit is pending.

Update after independent audit `2a025ee3b85f25af80e1b939f85f23c6cf06af30`:
initial candidate24d3351 was NOT ACCEPTED for A1. The latest implementation delta
uses sorted global LongMemEval ordinals both when binding and validating archive
diagnostics. `DeliveryIntegration.test_A1_longmemeval_diagnostics_follow_actual_sorted_assembly`
observes the unchanged real synthetic ingestion/fit/score path for sorted and
unsorted cohorts, checks actual question identity, and rejects rebound swapped
metadata. Old bridge fails this regression. Full updated suite54/5961 passes;
`evidence/a1_fixed/RESULTS.json` is current. Independent delta review remains pending.
Obligation4's synthetic closure cannot be accepted on the historical53-test receipt.

| Requirement from authoritative audit | Code / explicit change | Named verification in this namespace | Disposition |
|---|---|---|---|
| L-081 F1: caller identifiers in exceptions, including core validation | `pipeline_g3._validate_ingested_schema`, `validate_records`; `record_boundary.valid_records`; runner pre-core guard | `DeliveryPipelineTests.test_gap_05_F1_all_three_identifier_leak_paths_all_surfaces`, `test_gap_02_F1_F7_multi_archive_duplicate_question_ids_refused_upfront`, both `E_M_043` tests; `RelatedG2Tests.test_F1_F2_record_boundary_before_immutable_core` | Implemented for the named wrapper surfaces. Immutable core unchanged; arbitrary Python introspection is outside scope. |
| L-081 F2: successful empty cohort | Nonempty cohort/archive/record guards at M3 and synthetic bridge | `test_gap_04_F2_empty_cohorts_archives_and_records_refused`; integration empty-envelope negatives | Implemented; no empty synthetic success. |
| L-081 F3 plus N1: incomplete/canceling canary | Separate archive/query bit certificate and independent exact oracle, fixed literal family incl all-96 | All `CertificateTests`; 97 member-specific skip mutants, wrong-sign/permutation mutants, exact N1 fixture | Implemented to Decision 2 for synthetic fixtures; formal acceptance pending. |
| L-081 F4: same-object matched-block assertion | Independent redraw plus actual embedded-block extraction in `assert_embedded_blocks` | Three `test_F4_*` controls plus identity-embedding test; identity first shown to pass norm/dot | Implemented; a wrong orthogonal embedding now fails. |
| L-081 F5: E-M-005 swallowed by broad handler | Feature-count check outside fit exception handler | `test_F5_insufficient_features_retains_specific_E_M_005`; fit exception-context tests | Implemented with fixed diagnostic and empty context. |
| L-081 F6: CRLF checkout breaks core identity | Strict hash retained, repo-local LF clone setting and raw materialization documented | `RelatedG2Tests.test_F6_exact_blob_refuses_crlf_and_byte_mutation`; raw core/provenance checks; locked inherited replay | Operational remediation; default translated bytes still intentionally refuse. No normalization bypass. |
| L-081 F7: missing M3 schema validation | Exact container/value gates, cohort coverage, ownership/ordinal uniqueness, gold checks before fit | All `test_gap_02_*` methods, pre-fit refusal instrumentation | Implemented for both consumed synthetic ingestion schemas. |
| Gap 1: nuisance priorities reused but unasserted | Observe actual selector calls, shared object/bytes and twenty seed draws | `test_gap_01_every_topks_call_reuses_identical_immutable_priorities`, independent formula test and priority mutation | Evidence for all six arms × ten seeds; no performance/outcome inference. |
| Gap 2: no malformed M3 fixtures | Required/nested missing keys, wrong types, duplicates and coverage fixtures | `test_gap_02_F7_all_required_top_level_and_nested_keys_missing`, remaining gap-02 tests | Named malformed surfaces now tested. |
| Gap 3: E-M-026/027/028 untested | Separate empty-gold, anchor-coverage and benchmark controls | `test_gap_03_M3_all_three_declared_refusals` | All three exact refusal codes tested. |
| Gap 4: empty cohort untested | Both benchmark empty cohorts, archive and record controls | `test_gap_04_F2_empty_cohorts_archives_and_records_refused` | Closed as synthetic test gap. |
| Gap 5: exception suppression untested | Fit and query fault injection, recursive exception/output/write capture | `test_gap_05_text_fit_failures_all_exception_output_and_write_surfaces`, query counterpart, ID/core wrapper tests | Named surfaces tested, including cause/context and traceback; no universal privacy claim. |
| Gap 6: E-M-022 anchor type/range untested | Invalid numeric/container values and tolerance boundaries | `test_gap_06_anchor_types_ranges_and_container_refusals`, `test_gap_06_anchor_valid_endpoints_and_tolerance` | Synthetic anchors only; frozen anchor source remains a production obligation. |
| Gap 7: thin parity fuzz | AST-only historical function from raw pinned arithmetic; independent full-sort semantic oracle | `test_gap_07_gap_09_4000_exact_order_cases_against_raw_AST_function` (all 3 branches), 1,000 unique-priority lexsort cases | Code parity/selection evidence; module acquisition or outcome code is not executed. |
| Gap 8: partial canary coverage untested/undocumented | Each singleton and all-96 directly tested, zero in both directions/jointly, fixed family and seed verified | `CertificateTests.test_Decision2_each_member_has_own_negative_both_directions_and_joint_zero`, literal coverage and exact-zero tests | No earlier member may supply another member's negative. |
| Gap 9: selection ordering unasserted | Exact historical array parity tested; set-based metric contract documented | `test_gap_09_selection_order_is_not_rank_and_recall_is_set_based`, exact-order fuzz and six-arm order test | Selection array order matches inherited arithmetic in tested cases; no ranked-order API claim. |
| Obligation 4: preparation → bootstrap/output, provenance, overwrite protection | Explicitly synthetic bridge; closed validated envelope; accepted bootstrap arithmetic; exclusive output creation | `test_delivery_integration.py` end-to-end and negative controls; source/output provenance checks | Scoped synthetic bridge implemented. Real corrected-gold/anchor/source integration remains open. No finalizer operation performed. |
| Obligation 5: negatives, integration review, accepted lock, independent acceptance, pre-run seal | Full synthetic suite and inherited source regressions under exact five-version lock | `verify_delivery.py`, `run_inherited.py`, per-suite receipts; no inherited assertion changes | **PARTIAL:** synthetic components supplied; real integration review, independent acceptance and seal remain open. |
| L-080 F-1 (G2): int subclass loses intended diagnostic | Runner exact builtin `n_questions` type gate | `test_L080_F1_and_F3_exact_count_gates`, historical gate-regression mutant | Implemented, named DesignViolation retained; no numeric coercion. |
| L-080 F-2 (G2): spoof test passes for wrong exception | Test asserts `UnsafeErrorField` class and canary suppression | `test_L080_F2_spoof_exception_type_discriminates`, `test_L080_F2_historical_surviving_mutant_is_killed` | Historical M8-style mutant now caught; not retroactively labeled a confidentiality breach. |
| L-080 F-3 (G2): ingest count forwarded without local gate | `_manifest_n_questions` exact builtin integer validation at cohort-count sites | `test_L080_F1_and_F3_exact_count_gates`, `test_L080_F3_missing_local_gate_mutant_is_killed`; inherited ingest suite | Implemented; no new corpus count or cohort policy invented. |
| L-080 F-4 (G2): README too broad at two sites | README narrows claim to two local exact-type count gates and tested surfaces | README “What changed”, corresponding F-1/F-3 gate tests and raw/current source diff | Written disposition supplied; no claim that every caller-derived value is safe. |

## Working-candidate disposition

Recommend this G-3 successor as the **scoped synthetic working candidate**, carrying
forward v5's fixes instead of returning to v4. Historical v5 remains an audited
ancestor source, not a newly authorized production ingestion line. The user will
commission independent review before acceptance. This document records the
recommendation; it changes no canonical status label or ledger entry.

## Audit triage and explicit limits

- The recovered 42 checks really passed on the requested lock. Their original
  assertions do not establish Decision 2: they compared mismatch bits, used a
  substitute N1-style fixture, and did not isolate all-96. Recovery evidence and
  pre-edit bytes are preserved; the current suite replaces those assurance claims.
- The immutable core can emit caller IDs/paths and its writer is a check-then-write
  implementation. Wrappers prevent the tested malformed-record leakage and the
  synthetic bridge provides its own output protection. The core is not edited or
  presented as universally safe.
- Direct inherited `compute_results`/ingest APIs trust a mutable mapping stamp;
  a stamp alone is not cryptographic source provenance. The synthetic bridge must
  not masquerade a small fixture as an accepted production cohort. Production
  mapping immutability and a real authorized connector remain outside this review.
- The historical structural content policy permits short strings and cannot prove
  provenance confidentiality. `safe_report.counts` arbitrary-key/type-name behavior
  is retained as the audit explicitly recorded-but-did-not-reopen item.
- LoCoMo corrected-gold/dual reporting, actual anchor bytes and real cohort identity,
  production sharding, independent audit and pre-run seal are not closed here.
- Launcher and source-layout retries are reported separately from assertion or
  candidate failures in `VERIFICATION_RECEIPT.md`. No inherited assertion is
  removed, skipped or changed to manufacture a pass.
