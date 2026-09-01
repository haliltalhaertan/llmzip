# V52 Task 4F0 — Restricted-Cohort Refreeze Preparation Log

Date: 2026-08-31  
Status: `PREPARATION_ONLY — NOT SEALED`  
Owner: Head Researcher / Codex

## Purpose

This log records the single next action after acceptance of the independent cold-start audit: prepare a new exact-byte restricted-cohort refreeze. It does not authorize Task 4F1, inspect any Native-vs-Haar outcome, or alter an earlier frozen artifact.

## Provenance check completed

The current Google Drive 4F0 package was re-enumerated read-only. The five load-bearing files below each have exactly one Drive revision, with the recorded modification time and revision identity shown here:

| File | Drive ID | Size | Modified | Current revision |
|---|---|---:|---|---|
| `V52_T4F0_INPUT_MANIFEST.json` | `1VTBqTepqoC5eRSOz60yi2o8-AV5C9vMY` | 3,754 B | 2026-08-29 17:58:05Z | `0B07zs2LgBcb5c3hsVXRTOUJVc0dQRHBzNkx0UU9jQ0RsUWFBPQ` |
| `v52_t4f0_beam_adapter_evidence_freeze.py` | `1lE-TTVId7EQHvX5xckRIJgh0pGBc116B` | 15,822 B | 2026-08-29 17:58:09Z | `0B07zs2LgBcb5Qnc2Y0VsN2dvWmM1dStoQVhUSWJVeHBzTmhVPQ` |
| `V52_T4F0_COMPUTE_REPORT.md` | `1FsNVfRqCaBymtHKsDiTr8OjbGan3jzp3` | 3,673 B | 2026-08-29 17:58:47Z | `0B07zs2LgBcb5NEFpc0lhWUs0SGx3S1NuSmVLQ0pQOEh5dzBvPQ` |
| `V52_T4F0_HEAD_RESEARCHER_HANDOFF.txt` | `1hrfXZVZwSDO3xsV6RebHXCFO98Viyfp9` | 2,756 B | 2026-08-29 17:58:51Z | `0B07zs2LgBcb5TVEzVDUzUEtlY2FLeXhrRnhwdWFVM0F4eDMwPQ` |
| `V52_T4F0_OUTPUT_HASHES.json` | `19nOOdha6Y8KbiflWAKjQHrkEQwtaDWWk` | 1,798 B | 2026-08-29 17:59:00Z | `0B07zs2LgBcb5S1FoWG1xeGRXOCsyaVdTbTd5TlpET1Z5TkQ4PQ` |

Each row reports one revision and `previousRevisionId = null`. This is revision-level provenance, not a substitute for verifying downloaded bytes.

The Drive search found no occurrence-level BEAM source archive or canonical repaired message-key mapping beyond the pinned output package, prompt and provenance files. The independent audit identifies the upstream cause as a resumed-batch message-ID counter reset. Therefore no canonical re-key/remap is available at this time, and the restricted-cohort branch is selected.

## Accepted input boundary

The audit-accepted primary cohort is outcome-independent:

- 1,712 questions classified `EXACT_SOURCE_IDS`;
- the complete archive has unique `(tier, conversation_id, raw_message_id)` keys;
- excluded archives: `1M::5`, `1M::26`, `1M::33`, `1M::34`;
- no label, answer, rubric, evaluator output, or outcome is used to define membership;
- metrics to bind: fractional Source Evidence Recall@3, ANY@3 and ALL@3, including the structural zero for 587 questions with more than three gold units.

The local cohort digest currently recorded by the accepted audit is:

`estimand_primary_cohort.csv` SHA256 = `9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a`

The accepted audit hash inventory is:

`AUDIT_OUTPUT_HASHES.json` SHA256 = `3b3bb1a25cd9c8b7a56e1c29afbe8b3589f0c5c5f4705c000b7625da6f64fa65`

The preparation prompt draft is `prompts/V52_TASK_4F0_RESTRICTED_COHORT_REFREEZE_DRAFT_2026-08-31.md`. It is intentionally marked `DRAFT — NOT SEALED`; its digest is not yet a protocol seal.

Draft tracking hash (not a seal): SHA256 `a9737825ee73b3a15544605a94f0030ef164c8a54b2323e6f2229cbd024ccdcb`, 5,118 bytes.

These are anchors for preparation. A new refreeze must recompute and bind its own complete exact-byte manifest; it must not silently treat either value as the refreeze package digest.

## Refreeze gate checklist (not yet sealed)

Before any 4F1 preregistration, a new namespace must contain and independently verify:

1. exact prompt bytes and digest;
2. parent `llmzip` commit and pinned BEAM commit;
3. complete audit-package digest and restricted-cohort digest;
4. row count, excluded archive list, tier/ability composition and gold-cardinality distribution;
5. memory-unit identity and text construction;
6. representation family, dimensions, seeds, dependencies and thread controls;
7. metric denominators and formulas;
8. compute-script digest plus staged execution gates;
9. no-outcome leakage checks;
10. stop/no-expansion rules.

Required independent checks remain: exact-byte replay, manifest/hash closure, deterministic self-test, static leakage audit, and an auditor sign-off before any outcome-bearing run.

## Current decision

`TASK 4F0 REFREEZE PREPARATION: AUTHORIZED`  
`TASK 4F1 PREREGISTRATION: BLOCKED`  
`TASK 4F1 RUN: BLOCKED`  
`NATIVE-vs-HAAR OUTCOME INSPECTION: FORBIDDEN`

No Drive item was modified. No prior 4C3, 4D, or original 4F0 artifact was modified. The next operational step is to materialize the exact bytes for the new refreeze namespace and have them independently checked; until that check passes, this log remains preparation-only.

## Independent refreeze audit received

The cold-start auditor completed the package/cohort review and issued `BLOCKED — DO NOT SEAL / DO NOT PREREGISTER 4F1`. The receipt is recorded in `TASK4F0_RESTRICTED_REFREEZE_AUDIT_RECEIPT_2026-08-31.md`.

The candidate remains `PREPARED_NOT_INDEPENDENTLY_SEALED`. The blocking conditions are locked dependency/environment drift, absence of a separately byte-bound future 4F1 execution implementation, and pending independent sign-off. No outcome was accessed and no candidate or frozen artifact was modified.
