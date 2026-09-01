# V52 Task 4F0 — Audit Summary Reconciliation

Date: 2026-08-31  
Authority: Head Researcher / Codex

## Canonical package verification

The newly supplied narrative summary was compared with the existing local cold-start audit package. The canonical files remain unchanged:

- audit report SHA256: `2cb451614309603c76b60b1114b2082e6db8db2828d032c343c9cbffa48ef2c1`;
- audit inventory SHA256: `3b3bb1a25cd9c8b7a56e1c29afbe8b3589f0c5c5f4705c000b7625da6f64fa65`;
- restricted cohort SHA256: `9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a`.

The materialization, chain-integrity, real-data representation and no-outcome findings are accepted. The narrative recommendation requires correction on cohort arithmetic and authorization.

## Count reconciliation

The counts describe different layers and must not be interchanged:

- `1,743`: questions whose public annotation structure is classified `EXACT_SOURCE_IDS` before applying the clean-archive rule;
- `41`: questions in the four defective 1M archives whose supplied source IDs become ambiguous because they refer to divergent duplicate message IDs; these are classified `SOURCE_AMBIGUOUS_OR_MISSING`, not eligible exact questions;
- `31`: questions in those same four archives that remain annotation-exact but are still excluded because their complete retrieval archive violates the frozen unique memory-key rule;
- `1,712`: exact questions in archives where every `(tier, conversation_id, raw_message_id)` memory key is unique; this is the accepted primary denominator.

The four defective archives contain 80 questions in total: 41 source-ambiguous, 31 annotation-exact, and 8 abstention. The accepted outcome-independent rule excludes all 80 because the retrieval archive itself has non-unique divergent memory keys.

Therefore `1,743` must not be used as the 4F1 denominator under `BEAM_MESSAGE_ID_V1`. Using it would silently re-admit 31 questions from archives that violate the frozen memory-key identity.

## Correct interpretation

Accepted status:

`[MATERIALIZATION / SCALE / REPRESENTATION BLOCKER RESOLVED]`

`[FULL-COHORT MEMORY-KEY DEFECT CONFIRMED]`

`[1,712-QUESTION RESTRICTED COHORT ACCEPTED FOR REFREEZE]`

Not accepted:

`[1,743-QUESTION PRIMARY DENOMINATOR]`

`[TASK 4F1 PREREGISTRATION ALLOWED]`

## Current authorization

The exact dependency environment has since been recovered and the pre-outcome representation self-tests pass at 100K, 500K, 1M and 10M. This closes the environment/representation blocker.

The candidate remains `PREPARED_NOT_INDEPENDENTLY_SEALED`. A separately byte-bound 4F1 execution implementation and a fresh independent audit/sign-off are still missing. Consequently:

- `TASK 4F1 PREREGISTRATION = BLOCKED`;
- `TASK 4F1 RUN = BLOCKED`;
- `RETRIEVAL-QUALITY OUTCOME ACCESS = FORBIDDEN`.

No Native-vs-Haar outcome was inspected in making this decision.
