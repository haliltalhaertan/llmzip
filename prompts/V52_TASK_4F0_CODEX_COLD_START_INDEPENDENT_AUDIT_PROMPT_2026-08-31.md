# V52 TASK 4F0 — CODEX COLD-START INDEPENDENT AUDIT

## ROLE
You are an independent adversarial auditor working in a fresh Codex environment. Treat all prior summaries, verdicts, and researcher interpretations as untrusted claims until independently verified from source files, raw data, sealed artifacts, and upstream repositories.

Your target is NOT to continue the scientific experiment and NOT to optimize the method. Your target is to determine whether the current Task 4F0 `[BLOCKED — DO NOT RUN TASK 4F1]` verdict is technically and scientifically justified, and whether the blocker can be resolved by full-corpus materialization and source-ID verification without looking at Native-vs-Haar outcome metrics.

## PROJECT REPOSITORY
Canonical project repository:
https://github.com/haliltalhaertan/llmzip

Use branch `main` as the canonical accepted project state unless repository evidence proves otherwise.

Relevant project artifact:
`prompts/V52_TASK_4F0_BEAM_LARGE_SCALE_ADAPTER_EVIDENCE_FREEZE_2026-08-29.md`

Task 4F0 output folder:
https://drive.google.com/drive/folders/1nxDNk78sfTUqAPPNhOeGi-cyKscI-c3c

Original Task 4F0 prompt on Drive:
https://docs.google.com/document/d/1sauXtiWdifx8oOSM9hPLqQLPxIYPCHQSRkxFDhq22E4/edit

Upstream BEAM repository:
https://github.com/mohammadtavakoli78/BEAM

Pinned upstream commit to verify:
`3e12035532eb85768f1a7cd779832b650c4b2ef9`

Previous Task 4F0 result claimed:
- STATUS: BLOCKED
- tiers found: 100K/500K/1M/10M
- official counts: 100 conversations / 2000 validated probing questions
- exact source identifiability: only sample-level support; full cohort unverified
- source-ID mapping: verification incomplete, not a discovered semantic contradiction
- frozen memory unit candidate: `BEAM_MESSAGE_ID_V1 = (tier, conversation_id, individual raw message id)` with text `role + ': ' + content`
- Fractional Source Evidence R@3 / ANY@3 / ALL@3: not yet identifiable across the intended full cohort
- representation transfer: blocked because real full-tier execution was unavailable; synthetic invariants passed
- leakage gate: PASS
- Task 4F1: DO NOT RUN

Do not trust these claims. Reproduce or refute them.

## NON-NEGOTIABLE STOP RULE
DO NOT calculate, inspect, estimate, or compare any Native SIGN96 vs Haar96 retrieval quality result.
DO NOT run Task 4F1.
DO NOT tune thresholds, dimensions, embeddings, memory-unit definitions, source interpretation rules, or cohorts based on retrieval outcomes.
DO NOT use question answers, rubrics, `source_chat_ids`, or other evidence annotations to fit/learn representation parameters.

This audit may materialize the corpus, inspect annotations, build deterministic joins, and run representation-shape/repeatability checks. It may NOT reveal the scientific Native-vs-Haar outcome.

## AUDIT OBJECTIVES

### A. Chain of custody and temporal integrity
1. Verify the project `main` commit that contains the Task 4F0 prompt.
2. Verify the upstream BEAM commit exactly equals `3e12035532eb85768f1a7cd779832b650c4b2ef9`, or document the exact discrepancy.
3. Locate Task 4F0 input manifest, adapter/source code, reports, and output artifacts in the Drive folder.
4. Recompute SHA256 where bytes are available, including the claimed:
   - INPUT MANIFEST SHA256 `5bccceb575952e541e576b65bb010708dc23e5d231b950f2b3eea779ccf3f6c3`
   - ADAPTER SCRIPT SHA256 `b8056aa1eb0445eef12c5a3f78d8c596d06922b2a508bbe88125e161bdb36a57`
5. Determine whether any post-outcome change could have altered the adapter, evidence mapping rules, memory-unit definition, or eligibility logic.

### B. Full BEAM corpus materialization
Attempt a genuine full materialization of the pinned BEAM corpus, not a README-only audit.

For every intended tier available at the pinned commit:
- 100K (note if README labels it 128K),
- 500K,
- 1M,
- 10M,

enumerate all conversation directories/files and probing-question files that are actually present.

Report separately:
- exact number of conversations discovered per tier,
- exact number of probing questions discovered per tier,
- total unique conversation IDs,
- total raw message units,
- minimum/median/mean/max messages per conversation,
- raw bytes where practical,
- token counts only if computed with an explicitly named frozen tokenizer; otherwise label token counts UNVERIFIED rather than estimating them as facts.

If GitHub cannot provide all large files due provider/API limits, try legitimate alternative materialization paths documented by the upstream repository. If still blocked, identify the exact missing paths/files and the precise provider limitation. Do not convert an access failure into a semantic failure.

### C. Question taxonomy and evidence annotation census
Enumerate the full probing-question cohort and reproduce the official question-type taxonomy.

For every question, classify the public annotation into one and only one audit category such as:
1. EXACT_SOURCE_IDS — explicit raw message/chat IDs that can in principle be joined to unique raw messages.
2. COARSE_SOURCE — conversation/session references exist but do not uniquely identify raw messages.
3. ABSTENTION_NO_POSITIVE_EVIDENCE — intentionally unanswerable/absent-information item.
4. SOURCE_AMBIGUOUS_OR_MISSING — answerable item but no usable public evidence locator.
5. MALFORMED/CONTRADICTORY — annotation itself is internally invalid.

Do not infer source IDs from answer text or rubrics if they are not explicitly supplied by the benchmark.

Report exact counts by tier and question type.

### D. Source-ID join verification
For every record classified EXACT_SOURCE_IDS:
- deterministically join each source ID to the raw conversation representation,
- prove whether the join is unique,
- record unmatched IDs,
- record duplicate/ambiguous IDs,
- distinguish message-level IDs from conversation/session-level IDs,
- test whether IDs are globally unique or only unique within a conversation,
- test whether the frozen key `(tier, conversation_id, raw_message_id)` is sufficient to make every raw memory unit unique.

Output at minimum:
- exact_source_questions,
- exact_source_id_count,
- matched_source_ids,
- unmatched_source_ids,
- ambiguous_source_ids,
- duplicate_memory_unit_keys,
- affected_question_ids for every failure class.

A nonzero unmatched count is not automatically fatal: inspect whether it is a benchmark annotation bug, an adapter bug, a tier mismatch, an indexing convention mismatch, or an access/materialization failure.

### E. Estimand identifiability
Without computing Native/Haar outcomes, decide whether each metric is objectively identifiable from public data:
- Fractional Source Evidence R@3
- ANY@3
- ALL@3

State the exact eligible denominator rule before any scientific run.

If some questions are abstention or source-ambiguous, explicitly define which cohort would be the primary retrieval-evidence cohort and which records would be excluded. Exclusion must follow benchmark semantics only, never retrieval outcomes.

Return one of:
- `[EVIDENCE ESTIMAND IDENTIFIABLE — FREEZEABLE]`
- `[PARTIALLY IDENTIFIABLE — DEFINE RESTRICTED COHORT]`
- `[NOT IDENTIFIABLE FROM PUBLIC DATA]`

### F. Frozen representation transfer audit
Audit whether the project’s frozen representation family can be transferred to BEAM without changing its scientific meaning.

The intended memory unit candidate is:
`BEAM_MESSAGE_ID_V1 = (tier, conversation_id, individual_raw_message_id)`
text: `role + ': ' + content`

Check on REAL materialized BEAM data, not only synthetic matrices:
- deterministic message extraction,
- no query/gold/source-label leakage into representation fitting,
- source-block construction matches the frozen project family,
- latent32 / lexical blocks / mixed96 dimensionality is correct,
- no NaN/Inf,
- rank/dimension conditions are satisfied,
- archive-local fit uses archive contents only,
- repeated execution with frozen random states is bitwise or numerically reproducible as appropriate.

Do not change the representation to make BEAM work. If a frozen-family assumption genuinely fails, report the exact assumption and classify it as semantic incompatibility vs engineering limitation.

Return:
- `REPRESENTATION TRANSFER: PASS / FAIL / BLOCKED`
with evidence.

### G. Scale feasibility
For each tier separately, determine whether a future sealed 4F1 run is computationally feasible with the frozen representation.

Report:
- archive memory units,
- 96-bit code storage = exactly `12 bytes × number_of_units` for code storage only,
- expected dominant fit stages,
- measured peak RAM/time if you actually run the representation fit,
- otherwise clearly mark estimates as estimates,
- whether sparse char_wb 3–5gram or randomized SVD is the real bottleneck.

Return one of PASS/BLOCKED for 100K, 500K, 1M, 10M separately.

Do not confuse code storage with whole-system RAM.

### H. Adversarial review of the current BLOCKED verdict
Try hard to falsify the previous interpretation that Task 4F0 is merely blocked by incomplete data materialization.

Specifically test alternatives:
- public annotations are fundamentally insufficient even after full materialization,
- `source_chat_ids` refer to a different granularity than raw message IDs,
- IDs reset/collide in a way the frozen key cannot resolve,
- evidence annotations exist only for a biased subset of question types,
- restricted exact-source cohort would be too small or systematically unrepresentative,
- representation family cannot be transferred without a method change,
- large tiers are technically inaccessible from the public benchmark,
- the previous 100/2000 counts are README claims not supported by pinned data.

For each hypothesis give `CONFIRMED / REFUTED / UNRESOLVED` and evidence.

## REQUIRED FINAL VERDICT
Choose exactly one primary verdict:

1. `[PASS — ORIGINAL 4F0 BLOCKED VERDICT CORRECT]`
The blocker is real and remains unresolved.

2. `[PASS WITH CONDITIONS — ORIGINAL BLOCKED VERDICT CORRECT BUT RESOLVABLE]`
The original run correctly stopped, and the audit now identifies a concrete path to close the blocker.

3. `[BLOCKER RESOLVED — 4F0 MAY BE RE-FROZEN AS READY]`
Full materialization/source verification succeeds, evidence estimand is freezeable, representation transfer passes, and no scientific outcomes were inspected. In this case state explicitly whether Head Researcher may preregister Task 4F1; DO NOT run it.

4. `[FAIL — ORIGINAL 4F0 CONCLUSION OR IMPLEMENTATION DEFECTIVE]`
A substantive defect invalidates the previous adapter/estimand analysis. Quantify the defect and specify repair.

5. `[BENCHMARK UNSUITABLE — CLOSE BEAM BRANCH]`
Even with adequate materialization, public BEAM semantics cannot support the intended controlled evidence-retrieval experiment without inventing labels or materially changing the frozen method.

## REQUIRED OUTPUT FORMAT
Return a concise executive block first:

TASK: V52 TASK 4F0 — CODEX INDEPENDENT AUDIT
VERDICT: ...
AUDIT LEVEL: ...
UPSTREAM COMMIT IDENTITY: PASS/FAIL
FULL CORPUS MATERIALIZED: YES/NO/PARTIAL
CONVERSATIONS ENUMERATED: ...
PROBING QUESTIONS ENUMERATED: ...
EXACT SOURCE QUESTIONS: ...
COARSE SOURCE QUESTIONS: ...
ABSTENTION QUESTIONS: ...
AMBIGUOUS/MISSING SOURCE QUESTIONS: ...
SOURCE-ID JOIN: PASS/FAIL/BLOCKED
UNMATCHED SOURCE IDS: ...
AMBIGUOUS SOURCE IDS: ...
DUPLICATE MEMORY KEYS: ...
FRACTIONAL SOURCE EVIDENCE R@3 IDENTIFIABLE: YES/NO/RESTRICTED
ANY@3 IDENTIFIABLE: YES/NO/RESTRICTED
ALL@3 IDENTIFIABLE: YES/NO/RESTRICTED
REPRESENTATION TRANSFER: PASS/FAIL/BLOCKED
LEAKAGE GATE: PASS/FAIL
100K FEASIBLE: YES/NO/BLOCKED
500K FEASIBLE: YES/NO/BLOCKED
1M FEASIBLE: YES/NO/BLOCKED
10M FEASIBLE: YES/NO/BLOCKED
MAX QUANTIFIED DEFECT EFFECT: ... or N/A
TASK 4F1 MAY BE PREREGISTERED: YES/NO
SCIENTIFIC NATIVE-vs-HAAR OUTCOME INSPECTED: MUST BE NO

Then provide:
1. chain-of-custody findings,
2. full-corpus inventory,
3. evidence/source-ID census,
4. representation-transfer audit,
5. scale feasibility,
6. defect table,
7. final scientific/governance recommendation.

## ARTIFACTS
Save all audit-only scripts, inventories, join tables, hash logs, and report files under a clearly separate audit directory/branch, e.g.:
`audit_v52_t4f0_codex_2026_08_31/`
or an audit branch such as:
`audit/v52-t4f0-codex-2026-08-31`

Do not modify or overwrite frozen Task 4C3/4D/4F0 artifacts. Do not merge to `main` and do not push destructive changes unless explicitly authorized by the user.

If storage or network constraints prevent full verification, preserve partial outputs and report the exact blocker rather than guessing.

Begin from zero trust.