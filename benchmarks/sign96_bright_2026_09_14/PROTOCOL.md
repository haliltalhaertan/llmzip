# SIGN96 vs FLOAT96 — BRIGHT reasoning-intensive wave protocol

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

This protocol is committed before the BRIGHT workflow is introduced and before any BRIGHT result is observed.

## Frozen tasks

The first BRIGHT wave uses all eight non-code/non-math domains in the official BRIGHT release:

- biology
- earth_science
- economics
- psychology
- robotics
- stackoverflow
- sustainable_living
- pony

The special-exclusion BRIGHT tasks `leetcode`, `aops`, `theoremqa_questions`, and `theoremqa_theorems` are reserved for a separate second wave because their candidate-exclusion semantics and substantially larger source files warrant an isolated protocol.

## Outcome-blind boundary

For each task:

1. Freeze the exact Hugging Face dataset revision.
2. Read document parquet columns `id, content`.
3. Read only example parquet columns `id, query, excluded_ids`; the `gold_ids` column is not projected or read.
4. Fit the existing V52 archive-side representation on the complete task corpus only.
5. Build the same centered 96D representation used in the NanoBEIR/full-BEIR tests.
6. FLOAT96 = centered cosine. SIGN96 = sign of the same centered coordinates + Hamming distance.
7. Freeze top-100 rankings for 20 deterministic relevance-independent nuisance trials to `.npz`, write a pre-gold manifest, and SHA-256 hash both.
8. Only after that freeze is complete may a second parquet projection read `id, gold_ids` for evaluation.

The runner fails closed if any of these eight tasks unexpectedly contains a nonempty special `excluded_ids` list.

## Metrics

Primary descriptive metrics: Recall@3 and nDCG@10.
Secondary metrics: Recall@10, Recall@100, MAP@100, MRR@10.
Paired query-bootstrap 95% confidence intervals are computed from nuisance-averaged per-query SIGN-minus-FLOAT differences.

## Interpretation

BRIGHT tests reasoning-intensive retrieval rather than ordinary lexical/semantic matching, so it is a distribution-shift test of the sign-binarization phenomenon. A positive result does not prove a reasoning mechanism; a negative result does not refute the earlier ordinary-retrieval results. Cross-task sign reversals remain part of the target phenomenon.

`96 bits = 12 active SIGN code bytes` remains an active-code statement only, not a whole-system storage-cost claim.
