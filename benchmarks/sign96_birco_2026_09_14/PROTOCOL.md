# SIGN96 vs FLOAT96 — BIRCO complex-objective wave

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

This protocol freezes the BIRCO task set and evaluation boundary before this repository observes any BIRCO FLOAT96-vs-SIGN96 outcome.

## Frozen task set

All five official BIRCO task families are included through their MTEB-formatted test datasets:

- `doris-mae` -> `mteb/BIRCO-DorisMae-Test`
- `arguana` -> `mteb/BIRCO-Arguana-Test`
- `clinical-trial` -> `mteb/BIRCO-ClinicalTrial-Test`
- `wtb` -> `mteb/BIRCO-WTB-Test`
- `relic` -> `mteb/BIRCO-Relic-Test`

No task may be removed or substituted after outcomes are seen.

## Outcome-blind boundary

BIRCO differs from ordinary BEIR because each query has a query-specific candidate pool. The MTEB `default` parquet contains rows `(query-id, corpus-id, score)` for the candidate pool.

Before relevance is exposed, the runner may project only the structural columns `query-id` and `corpus-id` from this parquet to construct candidate pools. The `score` column is not projected or read until rankings are frozen and hashed.

For each task:

1. Freeze the exact Hugging Face dataset revision.
2. Read the complete corpus config and complete query config.
3. Read only `query-id, corpus-id` from the default parquet to define candidate pools; do not read `score`.
4. Fit the unchanged V52 archive-side representation on the complete task corpus only.
5. Construct the same centered 96D representation used in the prior NanoBEIR/full-BEIR/BRIGHT tests.
6. FLOAT96 ranks each query's candidate pool by centered cosine.
7. SIGN96 ranks the same candidate pool by Hamming distance after `sign()` of exactly the same centered 96 coordinates.
8. Freeze complete candidate-pool rankings for 20 deterministic relevance-independent nuisance tie trials and SHA-256 hash them.
9. Only then project `query-id, corpus-id, score` and score the frozen rankings.

## Metrics

Primary descriptive metrics:

- Recall@3
- nDCG@10

Secondary metrics:

- Recall@10
- Recall@100 (capped by candidate pool size)
- MAP@100
- MRR@10

Graded relevance values are retained for nDCG. Positive relevance (`score > 0`) defines the relevant set for recall/MAP/MRR. Paired query-bootstrap 95% confidence intervals use nuisance-averaged per-query SIGN-minus-FLOAT differences.

## Integrity

- V52 adapter SHA-256 must remain `0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722`.
- T4C2 source SHA-256 must remain `3bb1126090ab619c061d10d0f1a5c20db1372c5e2cd66b5158905a65f460061b`.
- Every input parquet is SHA-256 recorded.
- Candidate-pool rankings are frozen before relevance scores are read.
- `96 bits = 12 active SIGN code bytes` is not a whole-system storage-cost claim.

## Interpretation

BIRCO is a test of complex retrieval objectives, not a scale benchmark. It is intentionally complementary to full BEIR and BRIGHT. Results may support or weaken the hypothesis that the SIGN96 effect depends on task/corpus geometry, but this repository's run is not an independent reproduction.
