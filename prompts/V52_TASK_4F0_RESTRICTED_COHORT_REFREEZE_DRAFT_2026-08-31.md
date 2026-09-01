# V52 Task 4F0 — Restricted-Cohort Refreeze (DRAFT)

Date: 2026-08-31  
Status: `DRAFT — NOT SEALED — NO OUTCOME ACCESS`  
Decision owner: Head Researcher / Codex

## Objective

Prepare a new exact-byte governance boundary for a BEAM evidence-retrieval feasibility run after the independent cold-start audit. This document is a preparation artifact. It does not authorize Task 4F1 execution and must be independently audited before any retrieval-quality outcome is read.

## Why the full cohort is not repaired here

The pinned BEAM generator can reuse raw message IDs after resume. Four 1M archives contain 1,720 divergent duplicate `(tier, conversation_id, raw_message_id)` keys. Public annotations identify only the raw ID and do not identify which divergent occurrence was intended. An ordinal or JSON-path suffix would make rows unique but would not recover the missing annotation mapping. Selecting an occurrence by answer text, lexical similarity, or retrieval outcome would invent labels and is forbidden.

The full 2,000-question evidence estimand is therefore rejected. No full-cohort result may be reported under this refreeze.

## Frozen cohort rule

Include a question if and only if all conditions hold:

1. it is non-abstention;
2. its annotation is classified `EXACT_SOURCE_IDS`;
3. its entire conversation archive has unique `(tier, conversation_id, raw_message_id)` keys.

This produces exactly 1,712 questions. Exclude the entire archives `1M::5`, `1M::26`, `1M::33`, and `1M::34` before any outcome access. The cohort file is `audit_v52_t4f0_codex_2026_08_31/estimand_primary_cohort.csv` with currently recorded SHA256 `9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a`.

No finer exclusion, reweighting, alternate cardinality rule, rescue seed, or post-outcome cohort repair is allowed under this draft.

## Memory-unit identity and text

The candidate memory key is `BEAM_MESSAGE_ID_V1 = (tier, conversation_id, raw_message_id)`. Memory text is exactly `role + ': ' + content`; IDs remain metadata only. A future repair using occurrence-qualified IDs is a separate data-repair task and cannot silently replace this estimand.

## Representation and future comparison boundary

The archive-only representation recipe is inherited from the accepted 4F0 manifest:

- word TF-IDF: lowercase, word n-grams 1–2, English stop words, sublinear TF;
- character TF-IDF: `char_wb`, n-grams 3–5, sublinear TF;
- latent block: 32 components, random state 5101, L2 normalization;
- mixed block: 96 components, random state 5204, L2 normalization, archive-mean centering;
- queries are transformed only after archive fitting; no query fitting.

The intended future arms are `NATIVE_SIGN96`, a signed-permutation control, and `HAAR96_SIGN` with the five predeclared seeds `43001, 43002, 43003, 43004, 43005`. `ITQ96_CENTERED` with seeds `101, 202, 303, 404, 505` is descriptive only. Exact implementation bytes, dependency versions, thread controls and tie-priority bytes must be bound in the final seal; this draft does not substitute prose for those byte identities.

## Metrics (to be bound before outcome access)

For each eligible question with gold set `G` and retrieved top-3 set `R3`:

- Fractional Source Evidence Recall@3: `|R3 ∩ G| / |G|`;
- ANY@3: `1` iff `R3 ∩ G` is non-empty, otherwise `0`;
- ALL@3: `1` iff `G ⊆ R3`, otherwise `0`.

The denominator is the 1,712 eligible questions. ALL@3 retains structural zero for every question with more than three gold units; 587 such questions are present. Seeds and nuisance trials are collapsed within question and are not independent statistical units.

## Mandatory pre-outcome gates

Before any retrieval-quality output is opened:

1. verify all input, cohort, prompt and script bytes against a new manifest;
2. verify the parent `llmzip` commit and pinned BEAM commit;
3. run deterministic adapter self-test and no-NaN/dimension checks;
4. run static leakage audit proving labels, answers, rubrics, source IDs and outcomes do not enter fitting or cohort selection;
5. verify signed-permutation Hamming invariance and centered continuous invariance;
6. record exact environment, dependencies, random states and thread controls;
7. obtain an independent audit sign-off.

Any failed gate is `BLOCKED`; no repair is permitted after outcome access.

## Stop rules

After outcome access, do not add archives, change the cohort, choose an occurrence from a divergent duplicate, alter seeds, thresholds, centering, dimensions, tie priority, metric definitions or denominators, add rotations, tune a representation, or substitute a system metric. Weak, null or reversed results remain the result.

## Required final seal fields

The final exact-byte refreeze must bind the prompt SHA256, full accepted-audit package digest, restricted-cohort digest, excluded archives, row-count/composition tables, representation and script bytes, dependency/environment lock, formulas, tie rules, all pre-outcome checks, and the no-expansion stop rule. Until those fields are populated and independently checked, this document remains a draft.
