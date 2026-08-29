# V52 TASK 4E0 — LONGMEMEVAL-V2 ADAPTER / ESTIMAND FREEZE

Date: 2026-08-29
Role: Mathematical Compute Specialist / Benchmark Adapter Engineer
Authorized by: Head Researcher

Canonical full prompt in Drive: https://docs.google.com/document/d/1g8BD01w9zcNAaF-BJLSqEt0FqAIZx78mGXuUPsOiQmw/edit?usp=drivesdk

## HEAD RESEARCHER DECISION

[TASK 4E0 — ADAPTER / ESTIMAND FREEZE AUTHORIZED]

Task 4D is independently audited and frozen. The next intended scientific target is a large-memory external validation on LongMemEval-V2. However, the official public LongMemEval-V2 release explicitly removes answer-bearing annotation labels/construction provenance. Therefore the old LongMemEval/LoCoMo primary metric, Fractional Evidence Recall@3 against released gold evidence, CANNOT be silently ported to LongMemEval-V2.

Task 4E0 is PRE-OUTCOME ONLY. Do not compute Native-vs-Haar retrieval quality, answer accuracy, or any basis-sensitivity result.

Goals:
1. reproduce and freeze LongMemEval-V2 public data identity;
2. characterize exact public cohort and haystack scales;
3. freeze a semantically faithful memory-unit/text adapter;
4. prove archive-only fitting and no QA-answer/gold leakage;
5. determine which evaluation estimand is actually available from public labels;
6. produce a sealed Task 4E1 preregistration candidate, or declare the branch blocked.

Do not invent pseudo-gold evidence.

## CANONICAL PROJECT PARENT

Project repository: https://github.com/haliltalhaertan/llmzip
Canonical branch: `main`
Parent commit before Task 4E0: `e8d8ca2ddea05c2af911217de82d35a867ed5b2f`
Frozen Task 4D checkpoint: `docs/v52/task4d/TASK4D_ACCEPTED_CHECKPOINT_2026-08-29.md`

Prior audited hypothesis source only:
- LongMemEval Task 4C3: Native SIGN96 54.1975%, Haar96 38.2717%, D=-15.9259 pp.
- LoCoMo Task 4D: Native SIGN96 23.6547%, Haar96 13.7708%, D=-9.8839 pp.

Do not tune LongMemEval-V2 design toward these values.

## OFFICIAL LONGMEMEVAL-V2 SOURCES

Official repo: https://github.com/xiaowu0162/LongMemEval-V2
Pin current official main commit: `2cc8c540bdb87fe6761629b585e727e1c4704520`
Official dataset: https://huggingface.co/datasets/xiaowu0162/longmemeval-v2

Record exact Hugging Face revision downloaded and verify official checksums where covered.

Known public facts to verify:
- 451 questions;
- 1,870 trajectories;
- web + enterprise domains;
- Small tier exactly 100 trajectories/question and shared within each domain;
- Medium tier most questions 500 trajectories, some web questions fewer;
- largest histories reported up to ~115M tokens;
- public questions expose id/domain/environment/question_type/question/image/answer/eval_function;
- trajectories expose id/domain/environment/goal/outcome/start_url/states and state action/thought/accessibility_tree/screenshot;
- public release intentionally removes answer-bearing annotation labels, construction provenance, original task IDs, URL-pattern labels and annotation-pipeline tags.

## HARD LABEL-AVAILABILITY RULE

Do not fabricate or infer gold evidence IDs from reference answers, lexical matching, URL patterns, trajectory outcomes, question wording, LLM labels or heuristic search.

If no official public answer-bearing trajectory/state annotation exists, record:
`[PUBLIC EVIDENCE-GOLD UNAVAILABLE — FRACTIONAL EVIDENCE R@3 NOT IDENTIFIABLE ON LME-V2 PUBLIC RELEASE]`

This means a future 4E1 must use a different explicitly frozen estimand, most likely official end-to-end answer score under an identical fixed reader/context budget, and must be called LARGE-MEMORY EXTERNAL VALIDATION rather than exact evidence-recall replication.

## PHASE A — DATA IDENTITY / COHORT INVENTORY

Use official download/prepare/validate scripts where possible. Hash questions.jsonl, trajectories.jsonl, Small/Medium haystacks, SCHEMA.md, DATA_CARD.md and checksums.sha256.

Report exact question/domain/type/image counts; trajectory/domain/environment counts; states-per-trajectory; accessibility-tree text size/token estimate; Small and Medium haystack distributions; distinct reachable trajectories; candidate memory-unit counts and archive sizes.

No answer quality outcomes.

## PHASE B — MEMORY-UNIT ADAPTER FREEZE

Primary candidate is the official raw-state retrieval unit used by the public LME-V2 RAG implementation. Inspect pinned `memory_modules/rag.py` plus imported AgentRunbook-R raw-state construction functions and reconstruct exact public text materialization semantics.

Freeze one unit definition before outcomes. Preferred rule: one indexable record per official raw state entry/slice using only deployed-public trajectory fields; preserve provenance externally; no question ID/answer/eval_function/type/relevance labels in representation fitting.

Screenshot paths may remain provenance/context payload, but the V52 mixed96 representation is text-only. Do not add image embeddings.

If exact official raw-state semantics cannot be reproduced, STOP:
`[BLOCKED — LME-V2 MEMORY-UNIT SEMANTICS NOT REPRODUCIBLE]`

Do not switch to arbitrary chunks, trajectory-level indexing or LLM summaries without Head Researcher approval.

## PHASE C — REPRESENTATION TRANSFER PROOF

Frozen family only:
- word TF-IDF (1,2; English stop words; sublinear);
- char_wb TF-IDF (3,5; sublinear);
- latent32 SVD random_state=5101;
- concatenate latent/word/char;
- archive-only SVD96 random_state=5204;
- frozen L2 normalization;
- archive mean centering.

Answers/eval_function/type/question ID and benchmark metadata do not enter fitting. Question text transforms only after archive fit.

Determine haystack-equivalence caching classes from ordered trajectory IDs and materialized memory units only, without outcomes.

Report source hashes, equivalence classes, archive document counts, feature dims, rank feasibility, finite checks, leakage audit, repeatability, runtime/RAM/disk estimates.

No Native/Haar/ITQ quality metrics.

## PHASE D — MULTIMODALITY GATE

Inventory text-only vs question-image questions; confirm official query_image/read path; confirm whether official raw-state contexts can include screenshots.

Desired future 4E1 if feasible: binary retrieval query uses question TEXT ONLY in all arms; official query image reaches downstream reader identically; retrieved text/screenshot payload policy identical; no image embedding.

If basis-only symmetry cannot be maintained:
`[BLOCKED — MULTIMODAL INTERFACE PREVENTS BASIS-ONLY INTERVENTION]`

Do not silently restrict to text-only. Any subset proposal must freeze exact IDs/count before outcomes.

## PHASE E — ESTIMAND AVAILABILITY

Without running outcomes, classify:
A. Fractional Evidence Recall@3 — NOT IDENTIFIABLE unless official public evidence labels exist.
B. Official end-to-end answer score — candidate primary; use official eval_function and fixed reader.
C. Deterministic-evaluator answer subset — possible pre-outcome fallback if external judge unavailable; IDs/evaluator classes must be frozen first.
D. Latency/context footprint — engineering secondary only.
E. answer-string containment / pseudo-evidence — `REJECTED — NOT GOLD EVIDENCE`.

Recommend exactly one primary 4E1 quality estimand.

## PHASE F — DRAFT TASK 4E1 (DO NOT EXECUTE)

If feasible, create `V52_TASK_4E1_LONGMEMEVAL_V2_MEDIUM_LARGE_MEMORY_BASIS_SENSITIVITY_DRAFT.md`.

Primary tier candidate: Medium.
Frozen arms candidate:
1. NATIVE_SIGN96
2. SIGNED_PERM_CONTROL96
3. HAAR96_SIGN seeds 43001..43005
4. ITQ96_CENTERED reference seeds 101,202,303,404,505
5. centered-float invariance control

Continuous invariance tolerance <=1e-12. Tie priority independent of source order, answers, IDs/types or relevance.

Retrieval top-k/context budget must be frozen here from official raw-state semantics; do not copy top3 mechanically if official slice expansion changes context size.

If full-cohort end-to-end evaluation is feasible:
- fixed reader: official repo/paper default `Qwen/Qwen3.5-9B`, decoding settings pinned;
- identical memory context max tokens across arms;
- official per-question eval_function;
- external judge model/version/settings pinned where required;
- judge stochasticity nuisance only;
- answers/eval labels never enter retrieval fitting/ranking.

Do NOT reuse the old -5 pp threshold automatically because the metric differs. Recommend decision bands before outcomes or a simple directional preregistration. Head Researcher freezes final rule.

Predeclared strata candidate: web/enterprise; five memory-ability families and abstention suffix; query image present/absent; Medium haystack-size bands; deterministic evaluator vs LLM checker. No post-hoc subgroup search.

## COMPUTE / COST GATE

Estimate distinct fits, memory units, text size, TF-IDF/SVD fit time/RAM, binary storage, reader calls, judge calls and expected external API cost. If full design is too expensive, propose a metadata-only cost-bounded cohort now, before outcomes; do not shrink after seeing results.

## REQUIRED OUTPUTS

Create `V52_TASK_4E0_LONGMEMEVAL_V2_ADAPTER_ESTIMAND_FREEZE` result folder containing source pins, data identity, question inventory, haystack scale, memory unit spec/examples, representation transfer proof, multimodal interface audit, estimand availability, compute/cost estimate, 4E1 draft if feasible, compute report, Head Researcher handoff and all-outputs zip. Hash canonical outputs.

## REQUIRED HANDOFF

Return:
`TASK: V52 TASK 4E0 — LONGMEMEVAL-V2 ADAPTER / ESTIMAND FREEZE`
`STATUS: COMPLETE / BLOCKED / BUG`
`OFFICIAL GITHUB COMMIT: ...`
`OFFICIAL DATASET REVISION: ...`
`QUESTIONS: ... / 451`
`TRAJECTORIES: ... / 1870`
`SMALL HAYSTACK IDENTITY: PASS/FAIL; DETAILS=...`
`MEDIUM HAYSTACK IDENTITY: PASS/FAIL; MIN/MEDIAN/MAX=...`
`TEXT-ONLY QUESTIONS: ...`
`QUESTION-IMAGE QUESTIONS: ...`
`PUBLIC ANSWER-BEARING EVIDENCE LABELS AVAILABLE: YES/NO`
`FRACTIONAL EVIDENCE R@3 IDENTIFIABLE: YES/NO`
`MEMORY UNIT SPEC: ...`
`OFFICIAL RAW-STATE SEMANTICS REPRODUCED: PASS/FAIL`
`REPRESENTATION TRANSFER: PASS/FAIL/BLOCKED`
`LEAKAGE GATE: PASS/FAIL`
`MULTIMODAL BASIS-ONLY INTERVENTION FEASIBLE: YES/NO`
`RECOMMENDED 4E1 PRIMARY ESTIMAND: ...`
`RECOMMENDED 4E1 PRIMARY COHORT/TIER: ...`
`RECOMMENDED RETRIEVAL CONTEXT BUDGET: ...`
`READER REQUIREMENT: ...`
`JUDGE REQUIREMENT: ...`
`ESTIMATED 4E1 COMPUTE/COST: ...`
`TASK 4E1 DRAFT CREATED: YES/NO`
`OUTPUT DRIVE FOLDER: ...`
`MAX OBSERVED ADAPTER/PROTOCOL DEFECT: ...`

Then exactly one:
`[READY FOR HEAD-RESEARCHER 4E1 PREREGISTRATION REVIEW]`
or
`[BLOCKED — DO NOT RUN 4E1]`.

## INTERPRETATION CEILING / STOP RULE

Task 4E0 yields no scientific Native/Haar quality result. It establishes only whether a fair pre-registered LME-V2 large-memory basis-sensitivity experiment is possible. Stop after adapter/estimand outputs and handoff. Do not run 4E1, inspect Native/Haar differences, tune, rescue mechanisms, or draft paper conclusions.