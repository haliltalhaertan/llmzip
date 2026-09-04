# V52 Task 4F1 — Post-Run Result-Audit and Interpretation Gate

Date: 2026-09-04
Role: Head Researcher / Research Manager
Status: PRE-RUN GOVERNANCE DESIGN; OUTCOME-FREE

## Decision

The accepted runner deliberately finalizes Task 4F1 with:

- `status = COMPLETE_PENDING_INDEPENDENT_RESULT_AUDIT`
- `interpretation_authorized = false`
- `console_outcomes_emitted = false`

Those fields are load-bearing. A successful production run/finalize does not by itself authorize interpretation or release of the preregistered replication category.

Therefore the exact-rational outcome analyzer is split into two roles:

1. a frozen exact-analysis implementation that an independent result auditor may execute after an authorized production run; and
2. a release/interpretation gate that refuses to expose the global category unless a hash-bound independent-result-audit attestation returns PASS on the exact raw-result manifest and the exact frozen analysis implementation.

## Result-audit attestation schema

The independent result auditor must produce exactly one machine-readable attestation with schema:

`V52_T4F1_INDEPENDENT_RESULT_AUDIT_ATTESTATION_V1`

Required fields, with no extras:

- `schema`
- `verdict` = `PASS`
- `auditor_role` = `COLD_START_INDEPENDENT_RESULT_AUDITOR`
- `post_run_manifest_sha256`
- `execution_candidate_seal_sha256`
- `run_authorization_sha256`
- `preregistration_seal_sha256`
- `analysis_bundle_manifest_sha256`
- `audited_exact_analysis_sha256`
- `results_namespace_basename`
- `report_sha256`

The attestation is produced only after the independent auditor has:

1. verified the authorized-run provenance/HMAC chain;
2. verified the 96 archive CSV/meta hashes and finalized output hashes against the runner post-run manifest;
3. verified the frozen exact-rational analysis bundle against its pre-run manifest;
4. re-derived the exact-rational analysis from discrete retrieved IDs and sealed gold IDs;
5. verified nuisance-trial identity and SIGNED_PERM negative-control identity;
6. checked the exact analysis output hash;
7. recorded any invalidation rather than interpreting a contaminated result.

Any verdict other than exact `PASS`, any missing/unavailable audit report, any hash mismatch, or any additional/unrecognized attestation field blocks interpretation.

## Outcome visibility boundary

The independent result auditor is the first role permitted to parse retrieval-quality outcome values after a valid run. The auditor must not publish a substantive interpretation before its integrity checks finish.

The Head Researcher / release path sees or releases the preregistered global category only after the PASS attestation is verified.

A failed or contaminated result audit does not authorize interpretation. It yields containment/invalidation facts only.

## Frozen-analysis requirement

Before any production run authorization, the exact-rational analysis bundle must be frozen by exact file hashes in a pre-run bundle manifest. The independent auditor must use those exact bytes; changing the analyzer after outcomes exist requires a new adjudication and cannot silently replace the preregistered analysis implementation.

The bundle includes at minimum:

- `tools/t4f1_exact_rational_outcome_analysis.py`
- `tools/t4f1_verify_post_run_provenance.py`
- the audit-mode entrypoint that combines provenance verification and exact analysis
- their outcome-free synthetic tests

The result-release/interpretation gate may be implemented separately because it consumes only the auditor attestation and audited exact-analysis artifact.

## Current status

No production Task 4F1 run exists.
No valid production authorization exists.
No HMAC key is set or inspected.
No real retrieval-quality result has been read or interpreted.
No independent result-audit attestation exists.
Therefore interpretation remains BLOCKED.
