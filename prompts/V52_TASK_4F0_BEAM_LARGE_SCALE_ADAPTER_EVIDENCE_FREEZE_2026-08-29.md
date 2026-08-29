# V52 TASK 4F0 — BEAM LARGE-SCALE ADAPTER / EVIDENCE-IDENTIFIABILITY FREEZE

Date: 2026-08-29
Role: Mathematical Compute Specialist / Adapter Auditor
Authorized by: Head Researcher

Canonical full prompt in Drive: https://docs.google.com/document/d/1sauXtiWdifx8oOSM9hPLqQLPxIYPCHQSRkxFDhq22E4/edit?usp=drivesdk

## HEAD RESEARCHER DECISION

Task 4E0 (LongMemEval-V2) is BLOCKED for direct replication: the frozen mixed96 representation did not transfer cleanly and public answer-bearing evidence labels are unavailable, so Fractional Evidence Recall@3 is not identifiable there. This is NOT a negative result about the native-axis phenomenon; it is a benchmark/estimand incompatibility.

We therefore open a new PRE-OUTCOME feasibility branch on BEAM (ICLR 2026), a public long-term-memory benchmark with conversations at roughly 100K / 500K / 1M / 10M token scales. The only purpose of Task 4F0 is to determine whether BEAM can support a faithful evidence-level replication of the already-audited native-axis intervention. DO NOT compute Native-vs-Haar retrieval-quality outcomes in this task.

## CANONICAL PARENT STATE

Project repository: https://github.com/haliltalhaertan/llmzip
Canonical branch: main
Parent commit: 599b9e7bb13fd5d9f19ea8e378fef0d7273ad2b6
Frozen Task 4C3: LongMemEval native-axis effect audited.
Frozen Task 4D: LoCoMo native-axis effect audited.
Task 4E0: [BLOCKED — DO NOT RUN 4E1].

BEAM official repository: https://github.com/mohammadtavakoli78/BEAM
Pin upstream repository state to commit: 3e12035532eb85768f1a7cd779832b650c4b2ef9
If using Hugging Face copies, record exact dataset revision / file hashes and prove semantic identity with the pinned official repository.

## WHY BEAM IS A CANDIDATE

Official public BEAM materials expose long conversations and probing questions. At least some answerable probing-question records contain fields such as `source_chat_ids` and/or `conversation_references`; the raw chat JSON exposes stable message IDs. This suggests evidence-level retrieval may be identifiable, unlike public LongMemEval-V2. However this MUST be proven across the intended cohort before any quality outcome is allowed.

Do not assume `source_chat_ids` are exact evidence units merely because the field exists. Establish their official semantics, mapping, coverage, and cardinality.

## PRIMARY 4F0 QUESTION

Can the frozen V52 mixed96 representation family and an evidence-level retrieval estimand be transferred to BEAM without label leakage, hand-created pseudo-gold, post-outcome choices, or ambiguous source-ID semantics?

## HARD NO-OUTCOME RULE

Task 4F0 MUST NOT calculate or reveal Native SIGN96, Haar96, ITQ, or any comparative retrieval-quality outcome. Only representation construction, ID mapping, source-label coverage, static leakage tests, dimensional/integrity checks and compute-cost estimates are allowed.

## BENCHMARK INVENTORY

Independently inventory the pinned BEAM release: tier/chat counts, total validated probing questions, question-type counts, raw turn/message counts, token-scale accounting, archive-unit distribution, schema fields, duplicate/malformed IDs, and whether the 10M tier is fully present in the pinned repository or requires a separate public artifact. Hash all canonical local inputs.

## EVIDENCE-LABEL IDENTIFIABILITY

For every probing question classify BEFORE retrieval outcomes:
A. EXACT_SOURCE_IDENTIFIABLE — public metadata maps unambiguously to one or more raw memory units.
B. COARSE_SOURCE_IDENTIFIABLE — metadata identifies a containing chat/session but not a unique exact unit.
C. ABSTENTION_NO_POSITIVE_EVIDENCE — intentionally no supporting evidence.
D. SOURCE_AMBIGUOUS_OR_MISSING — no defensible public gold mapping.

Produce counts by tier/question type. If `source_chat_ids` map to stable raw IDs, prove it by deterministic joins and report unmatched, multi-mapped and duplicate cases. Inspect all question-type schemas. Never infer gold via lexical search, answer matching, LLM judging, embeddings or manual guessing.

## MEMORY-UNIT SEMANTICS

Determine the smallest official raw unit for which public labels are valid: individual message, turn pair, batch/session, or other official unit. Required proof: stable ID; deterministic gold join; text reconstructed without labels; tie priority independent of gold/source order; abstention separable from missing-label failure.

If only coarse labels exist, name the future metric accordingly instead of pretending it equals prior turn-level evidence recall.

## REPRESENTATION TRANSFER

Test whether the exact frozen V52 representation/source-block FAMILY applies to the chosen BEAM memory units using archive text only: frozen word TF-IDF family, frozen char_wb TF-IDF family, latent TruncatedSVD family/random state, concatenate blocks, archive-only mixed TruncatedSVD(96, random_state=5204) when feasible, frozen L2 normalization, archive mean centering, query transformed only after archive fitting.

Do not substitute pretrained embeddings, new dimensions, supervised projection, whitening, PCA rescue or query-adaptive fit. For each tier report rank feasibility, sparse feature dimension, RAM/time estimate, degenerate cases and whether per-conversation archive-local fitting is practical. Implementation-equivalent streaming/sparse solvers are allowed only if shown to compute the same frozen mathematical object within stated tolerance.

## LEAKAGE GATE

Fit may use only archive memory text. Forbidden fit inputs: probing questions, answers/ideal answers, rubrics, source IDs/references, difficulty, question type, abstention labels and evaluator output. Query text enters only at transform/retrieval time after fit. Perform static/AST and runtime payload checks.

## CANDIDATE EVIDENCE METRIC — IDENTIFICATION ONLY

Determine whether `Fractional Source Evidence Recall@3 = |retrieved_top3 ∩ gold_source_units| / |gold_source_units|` plus ANY@3 and ALL@3 are identifiable. Do not freeze a misleading turn-level metric if source labels are coarser. Abstention questions must not receive fabricated positive evidence.

## SCALE-TIER DESIGN FOR FUTURE 4F1

Without outcomes, determine feasibility of 100K -> 500K -> 1M -> 10M progression and exact evidence-valid counts per tier. Estimate archive units, 96-bit code storage, float32 96D storage, brute-force XOR+popcount work/query, and representation-fit cost separately. No wall-clock superiority claim in 4F0.

## DATASET / PROVENANCE SEAL

Before any outcome-like retrieval code create `V52_T4F0_INPUT_MANIFEST.json` pinning upstream BEAM commit, all canonical file hashes/revisions, local adapter SHA256, project parent commit, inventory, intended memory-unit candidate(s), leakage rules and no-outcome rule.

## REQUIRED OUTPUTS

Create a Task 4F0 Drive folder containing at minimum: input manifest, adapter/source-inspection script, dataset inventory, question-schema coverage, source-ID mapping, evidence-identifiability table, memory-unit semantics note, representation-transfer proof, leakage checks, scale-cost estimate, compute report, Head Researcher handoff, and all-outputs ZIP.

## REQUIRED HANDOFF

TASK: V52 TASK 4F0 — BEAM LARGE-SCALE ADAPTER / EVIDENCE-IDENTIFIABILITY FREEZE
STATUS: COMPLETE / BLOCKED / BUG
UPSTREAM BEAM COMMIT: ...
TIERS FOUND: ...
TOTAL CONVERSATIONS: ...
TOTAL PROBING QUESTIONS: ...
QUESTION TYPES: ...
EXACT_SOURCE_IDENTIFIABLE: ...
COARSE_SOURCE_IDENTIFIABLE: ...
ABSTENTION_NO_POSITIVE_EVIDENCE: ...
SOURCE_AMBIGUOUS_OR_MISSING: ...
SOURCE-ID MAPPING: PASS/FAIL; unmatched=...; duplicate=...
FROZEN MEMORY UNIT CANDIDATE: ...
FRACTIONAL SOURCE EVIDENCE R@3 IDENTIFIABLE: YES/NO/COARSE-ONLY
ANY@3 IDENTIFIABLE: YES/NO
ALL@3 IDENTIFIABLE: YES/NO
REPRESENTATION TRANSFER: PASS/BLOCKED
LEAKAGE GATE: PASS/FAIL
100K FEASIBLE: YES/NO; evidence-valid questions=...
500K FEASIBLE: YES/NO; evidence-valid questions=...
1M FEASIBLE: YES/NO; evidence-valid questions=...
10M FEASIBLE: YES/NO; evidence-valid questions=...
MAX ARCHIVE UNITS: ...
MAX APPROX TOKENS: ...
96-BIT CODE STORAGE AT MAX SCALE: ...
ESTIMATED REPRESENTATION FIT BOTTLENECK: ...
OUTPUT DRIVE FOLDER: ...
INPUT MANIFEST SHA256: ...
ADAPTER SCRIPT SHA256: ...

Then exactly one terminal label:
`[READY FOR HEAD-RESEARCHER TASK 4F1 PREREGISTRATION REVIEW]`
or
`[BLOCKED — DO NOT RUN TASK 4F1]`

## INTERPRETATION CEILING

Task 4F0 establishes only benchmark/adapter/estimand feasibility. It cannot strengthen or weaken the native-axis claim because no Native-vs-Haar outcome is allowed. If READY, Head Researcher separately preregisters 4F1. If BLOCKED, do not rescue by inventing pseudo-gold or changing representation semantics.

## STOP RULE

Stop after the handoff. Do not run Task 4F1, inspect Native/Haar quality, start mechanism experiments or draft publication claims.