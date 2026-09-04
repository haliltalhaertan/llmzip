# V52 Task 4F1 — Head Researcher Preregistration Sealing Direction

Date: 2026-09-04
Role: Head Researcher / final scientific approval authority
Reviewed state: `main @ 53b70e56025a371f11bf969731ab4318ba3013eb`

## Decision

**DO NOT APPLY THE PREREGISTRATION SEAL YET. OBTAIN CO-CHAIR SIGN-OFF ON THE EXACT AMENDED BYTES FIRST; THEN PREPARE AND APPLY THE SCIENTIFIC PREREGISTRATION SEAL WITHOUT WAITING FOR THE V7 EXECUTION-PACKAGE AUDIT.**

This is a sequencing decision, not a scientific reversal. The Head Researcher approval of the amended preregistration remains valid and bound to draft SHA256:

`5e61898193421a3a18791202668c0974f23d2fb4080a107069e7b7127e35ea44`

The reason not to seal immediately is internal to the approved draft's own authority rule: the draft states that it requires both Head Researcher and co-chair approval before becoming a sealed preregistration. The current scientific co-chair artifact reviewed the predecessor draft SHA256 `ec3443ed4c60eb12e098192abf7b414e034d89fc63a9f42f9d0a02c36a696e45` and returned `REQUEST CHANGES`. The six requested amendments A1–A6 were then applied, and the Head Researcher independently re-reviewed and approved the amended bytes, but no pushed co-chair artifact yet approves the exact amended SHA256 `5e618981...`.

Therefore the remaining science-track gate is narrow: a session-independent co-chair must review the exact amended bytes and return a pushed, hash-verifiable `APPROVE` or equivalent sign-off. The Continuity Lead session that prepared the amendments must not supply that independent co-chair sign-off itself.

## Relation to V7

The V7 independent execution-package audit is **not** a prerequisite for sealing the scientific preregistration. The two tracks remain independent.

At the reviewed state, the V7 audit branch remains at `16dc61313acd0e9086c852eccb9100023898fd27`, with Gates 1–7 evidence pushed but no final report, gate table, hash manifest, or verdict. This does not block the science seal once the co-chair exact-byte sign-off exists.

Likewise, sealing the preregistration does not authorize execution and does not prejudge V7. Task 4F1 run remains BLOCKED and retrieval-quality outcome access remains FORBIDDEN until the separate execution/governance gates close and a distinct run authorization is issued.

## Required co-chair re-review target

The co-chair re-review must bind exactly:

- commit containing the amended draft: `c0133fce9b755d13d9be3016e8e06f493d6b275b`
- path: `docs/v52/task4f1/TASK4F1_PREREGISTRATION_DRAFT_2026-09-03.md`
- SHA256: `5e61898193421a3a18791202668c0974f23d2fb4080a107069e7b7127e35ea44`
- Head Researcher re-review decision: branch `hr/rereview-t4f1-prereg-2026-09-04`, commit `19d9cbbfcbc48f80dc63ac179f2aa67e7eed490d`, decision-file SHA256 `8795abc7b58b3bae8f2333ba630f95642e9d2e653a31478d221ceb9d71272f3f`

The co-chair should verify only that A1–A6 are adequately discharged on these exact amended bytes and that no new scientific inconsistency was introduced. It need not reopen the V7 package audit or re-litigate already accepted implementation evidence.

## Seal contents after co-chair approval

Once that exact-byte co-chair approval is pushed and independently hash-verified, the Continuity Lead is authorized to prepare the preregistration seal immediately. Do not defer that science seal merely to wait for V7.

The seal should bind at minimum:

1. the exact amended preregistration draft SHA256 `5e61898193421a3a18791202668c0974f23d2fb4080a107069e7b7127e35ea44`;
2. the sealed 4F0 restricted cohort SHA256 `9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a`;
3. the accepted runner SHA256 `f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8`;
4. the Head Researcher re-review decision SHA256 `8795abc7b58b3bae8f2333ba630f95642e9d2e653a31478d221ceb9d71272f3f`;
5. the future exact-byte co-chair approval artifact SHA256;
6. the Head Researcher governance ratification that preserves the V4 authorization schema while the runner remains byte-identical to V4;
7. the four binding execution conditions already stated in §8 of the approved preregistration;
8. the pre-run implementation condition that the sign classification of `D_t` must honor the preregistered exact-rational arithmetic rule rather than use a rounded floating aggregate.

Do **not** bind a V7 audit verdict or V7 accepted-package seal into the scientific preregistration seal unless such an artifact already exists and is deliberately being added as provenance only. The scientific seal must not become contingent on an execution-track result that was not part of the scientific design approval.

Any later change to scientific content produces new preregistration bytes and requires a fresh scientific approval. Purely additive sealing metadata must not rewrite the approved draft.

## Owner-only repository items

The GitHub default branch pointing somewhere other than `main` and the environment's inability to push `refs/tags` remain repository-owner / environment issues. They are important governance hygiene items but do not prevent the exact-byte co-chair re-review or the subsequent branch-anchored scientific seal. They must not be used as a reason to access outcomes or run Task 4F1 early.

## Outcome boundary

This decision performs no Task 4F1 run or finalize operation, constructs no valid production authorization, sets no HMAC key, performs no real BEAM retrieval ranking, and accesses no Task 4F1 retrieval-quality outcome.

Task 4F1 preregistration remains unsealed at this moment; Task 4F1 run remains BLOCKED; retrieval-quality outcome access remains FORBIDDEN.
