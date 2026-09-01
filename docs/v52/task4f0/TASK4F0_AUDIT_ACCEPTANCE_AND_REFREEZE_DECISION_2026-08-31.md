# V52 Task 4F0 — Audit Acceptance and Refreeze Decision

Date: 2026-08-31

## Head Researcher decision

- `TASK 4F0 INDEPENDENT AUDIT ACCEPTED: YES, WITH CONDITIONS`
- `ORIGINAL TASK 4F0 STOP DECISION CORRECT: YES`
- `RESTRICTED-COHORT REFREEZE PREPARATION AUTHORIZED: YES`
- `TASK 4F1 MAY BE PREREGISTERED: NO`
- `TASK 4F1 MAY RUN: NO`
- `SCIENTIFIC NATIVE-vs-HAAR OUTCOME INSPECTED: NO`

Accepted verdict:

`[PASS WITH CONDITIONS — ORIGINAL BLOCKED VERDICT CORRECT BUT RESOLVABLE]`

The audit closes the prior access and scale uncertainty, but confirms a real upstream memory-key defect. Four 1M archives contain divergent duplicate raw message IDs, so the original full-cohort evidence key is not scientifically recoverable from public annotations without inventing labels.

## Accepted restricted estimand

Primary inclusion rule:

> Include only non-abstention questions classified `EXACT_SOURCE_IDS` whose entire conversation archive has unique `(tier, conversation_id, raw_message_id)` keys.

This rule yields exactly 1,712 primary questions. Entire archives `1M::5`, `1M::26`, `1M::33`, and `1M::34` are excluded before outcome access. The rule covers `95.111%` of all 1,800 answerable questions and `99.074%` of answerable questions in clean archives.

Accepted metrics on this restricted cohort are:

- Fractional Source Evidence Recall@3;
- ANY@3;
- ALL@3, retaining structural zero for the 587 questions with more than three gold units.

No alternate cardinality restriction may be selected after viewing outcomes.

## Verification record

Complete compact audit package: `audit_v52_t4f0_codex_2026_08_31/`

- files: 34 total, comprising 33 manifest-declared payloads plus the hash inventory;
- manifest verification: `33/33`, mismatch `0`;
- deterministic independent rerun: 11 corpus, anomaly and estimand outputs reproduced byte-for-byte;
- `AUDIT_OUTPUT_HASHES.json` SHA256: `3b3bb1a25cd9c8b7a56e1c29afbe8b3589f0c5c5f4705c000b7625da6f64fa65`;
- `estimand_primary_cohort.csv` SHA256: `9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a`;
- `V52_T4F0_CODEX_INDEPENDENT_AUDIT_REPORT.md` SHA256: `2cb451614309603c76b60b1114b2082e6db8db2828d032c343c9cbffa48ef2c1`.
- the subsequently received pasted-text report had raw SHA256 `c2ad8009336f4b0a10b833f1b092ff44e7f575b888f3c32464b5c09dcb43d4ff`; its only byte difference was 162 CRLF line endings, and LF normalization reproduced the package-report SHA256 exactly.

The independent representation A/B records remain accepted audit evidence. They were not recomputed during this acceptance pass because the bundled runtime lacked `psutil`; the package records bitwise A/B equality, finite rank-96 outputs and the measured resource envelope. This is a bounded verification condition, not a mismatch.

## Refreeze requirements

The new 4F0 restricted-cohort refreeze must be a separate, exact-byte governance artifact. It must bind:

1. parent `llmzip` commit and pinned BEAM commit;
2. exact prompt bytes and prompt digest;
3. full audit-package digest and restricted-cohort digest;
4. row count, exclusion list, tier/ability composition and gold-cardinality distribution;
5. memory-unit identity and text construction;
6. representation family, dimensions, random states, dependencies and thread controls;
7. metric denominators and formulas;
8. compute script digest and staged execution gates;
9. no-outcome audit checks;
10. stop/no-expansion rules.

The refreeze must not modify any Task 4C3, 4D or original 4F0 frozen artifact. A new namespace is required.

## Interpretation ceiling

This decision establishes that BEAM is usable for a restricted, evidence-identifiable feasibility branch. It does not establish a BEAM native-axis effect, generalization to 10M contexts, a causal mediator, model-family universality, or production readiness.
