# V52 Task 4F0 — Restricted-Cohort Refreeze Protocol

Date: 2026-08-31  
Status: `PREPARED — CANDIDATE SEAL — NOT INDEPENDENTLY SEALED`  
Decision owner: Head Researcher / Codex

## Scope and authorization

This is a new exact-byte governance boundary for a possible BEAM evidence-retrieval feasibility run. It is a preparation artifact and does not authorize Task 4F1 preregistration, execution, or retrieval-quality outcome access. The original Task 4C3, Task 4D and original Task 4F0 artifacts are outside this namespace and must not be modified.

The full 2,000-question evidence estimand is rejected. Four 1M archives contain divergent duplicate `(tier, conversation_id, raw_message_id)` keys; public annotations do not identify the intended occurrence. No occurrence may be selected by answer text, lexical similarity, retrieval outcome, or any other post hoc rule.

## Frozen primary cohort

Include a question if and only if all conditions hold:

1. it is non-abstention;
2. its annotation is classified `EXACT_SOURCE_IDS`;
3. its entire conversation archive has unique `(tier, conversation_id, raw_message_id)` keys.

The exact row-level cohort is `estimand_primary_cohort.csv` in this namespace. It contains 2,000 question records, of which exactly 1,712 are eligible. The denominator for every primary retrieval metric is 1,712 eligible questions. The excluded archives are exactly `1M::5`, `1M::26`, `1M::33`, and `1M::34`.

No finer exclusion, reweighting, alternate cardinality rule, rescue seed, post-outcome repair, or cohort expansion is permitted.

## Memory-unit and text identity

The candidate memory key is `BEAM_MESSAGE_ID_V1 = (tier, conversation_id, raw_message_id)`. The memory text is exactly `role + ': ' + content`, encoded as UTF-8. Keys are metadata only and must not be included in fitted text. Duplicate raw IDs in excluded archives are a hard exclusion; an occurrence-qualified key is a separate data-repair task and cannot silently replace this estimand.

## Archive-only representation

For each eligible question, fit independently on its complete conversation archive. The fitting payload may contain only the ordered memory texts.

- word TF-IDF: lowercase, word n-grams 1–2, English stop words, sublinear TF;
- character TF-IDF: `char_wb`, n-grams 3–5, sublinear TF;
- latent block: 32 components, randomized SVD, `random_state=5101`, L2 normalization;
- mixed block: 96 components, randomized SVD, `random_state=5204`, L2 normalization, archive-mean centering;
- query text is transformed only after archive fitting; no query fitting and no cross-question fitting;
- no pretrained embeddings, supervised projection, whitening, PCA rescue, query-adaptive fitting, reranking, or threshold tuning.

The precise implementation byte identity is the SHA256-bound `v52_t4f0_restricted_preflight.py` in this namespace for the pre-outcome gate. A future outcome-bearing 4F1 execution implementation is not authorized by this candidate and requires its own byte binding before use.

## Future arms, fixed before outcome access

If and only if this candidate is independently accepted and a separate 4F1 preregistration is approved, the planned arms are:

- `NATIVE_SIGN96`;
- `SIGNED_PERM_CONTROL96`, using a common signed permutation and expected exact Hamming invariance;
- `HAAR96_SIGN`, full 96D orthogonal mixing with seeds `43001, 43002, 43003, 43004, 43005`;
- `ITQ96_CENTERED`, descriptive only, with seeds `101, 202, 303, 404, 505`.

The future run uses 20 fixed nuisance trials per question and arm. Seeds and nuisance trials are collapsed within question; they are not independent statistical units. Any change requires a new protocol.

## Tie priority

For every archive memory key, use one deterministic, label-independent priority:

`priority = uint128_be(SHA256(b'V52_T4F0_TIE_PRIORITY_V1' + b'\0' + archive_id_utf8 + b'\0' + memory_key_utf8)[:16])`.

Rank Hamming distances ascending; break equal distances by ascending priority, then by the canonical archive order. The priority input must not contain question answers, source IDs, gold labels, outcomes, or source-list order.

## Metrics

For eligible question `q`, gold set `G_q`, and retrieved top-three set `R_q,3`:

- Fractional Source Evidence Recall@3: `|R_q,3 ∩ G_q| / |G_q|`;
- ANY@3: `1` iff `R_q,3 ∩ G_q` is non-empty, otherwise `0`;
- ALL@3: `1` iff `G_q ⊆ R_q,3`, otherwise `0`.

Aggregate each metric as the arithmetic mean over the 1,712 eligible questions. ALL@3 retains structural zero for all 587 eligible questions with more than three gold units. No metric substitution, denominator change, or abstention recoding is allowed.

## Required pre-outcome gates

Before opening any retrieval-quality output, an independent auditor must verify:

1. exact prompt, cohort, summary, composition-table, dependency, script and manifest bytes;
2. accepted audit-package closure and the pinned cohort digest;
3. parent `llmzip` commit `d3c7aa09c9553cd5ac100e668923abab602e4257` and BEAM commit `3e12035532eb85768f1a7cd779832b650c4b2ef9`;
4. deterministic adapter self-test, finite values and exact dimensions on raw archives;
5. static and runtime leakage audit proving labels, answers, rubrics, source IDs and outcomes do not enter fitting or cohort selection;
6. signed-permutation Hamming invariance and centered-continuous invariance;
7. exact environment, dependency versions, random states, thread controls and tie-priority implementation;
8. independent sign-off recorded in the candidate seal.

Any failed gate is `BLOCKED`. No repair is permitted after outcome access.

## Stop rule

After outcome access, do not add archives, change the cohort, choose an occurrence from a divergent duplicate, alter seeds, thresholds, centering, dimensions, tie priority, metric definitions or denominators, add rotations, tune a representation, or substitute a system metric. Weak, null, or reversed results remain the result.

## Candidate status

The exact-byte payloads and their hashes are recorded by `PAYLOAD_HASHES.json` and `CANDIDATE_SEAL.json`. This namespace is `PREPARED`, not `SEALED`: independent audit sign-off, raw-corpus self-tests, and any future 4F1 execution implementation remain outstanding. Until those gates pass, `TASK 4F1 PREREGISTRATION = BLOCKED` and `TASK 4F1 RUN = BLOCKED`.
