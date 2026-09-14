# SIGN96 vs FLOAT96 — Full BEIR heavy-wave protocol

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

This file is committed before the heavy-wave workflow is introduced or any full-BEIR outcomes are observed.

## Research question

Does the regime-dependent SIGN96-vs-FLOAT96 phenomenon observed on LongMemEval and NanoBEIR survive when the same representation/ranking comparison is evaluated on complete BEIR corpora rather than NanoBEIR subsets?

## Frozen wave-1 tasks

- `scifact` — 300 test queries, ~5K documents.
- `scidocs` — 1,000 test queries, ~25K documents.
- `arguana` — 1,406 test queries, ~8.7K documents.
- `fiqa` — 648 test queries, ~57K documents.
- `nfcorpus` — 323 test queries, ~3.6K documents.
- `trec-covid` — 50 test queries, ~171K documents.

The first wave deliberately spans roughly two orders of magnitude of corpus size while remaining compatible with the unchanged V52 corpus-fitted TF-IDF/SVD representation on standard GitHub-hosted runners. Larger BEIR corpora (382K to multi-million documents) are a later scale wave and must not be substituted into this wave after outcomes are seen.

## Frozen representation comparison

For each task independently:

1. Read full corpus and queries; do **not** open qrels.
2. Fit the existing V52 archive-side word TF-IDF + character TF-IDF + latent representation on corpus documents only.
3. Construct the same normalized 96D SVD representation used in the NanoBEIR cross-benchmark pilot.
4. Center corpus and query vectors by the corpus mean.
5. FLOAT96 ranks by cosine in that centered 96D representation.
6. SIGN96 takes the coordinate signs of exactly the same centered 96D vectors and ranks by integer Hamming distance.
7. Freeze top-100 rankings for 20 deterministic relevance-independent nuisance tie trials to disk and hash them.
8. Only after the frozen-ranking artifact exists may qrels be opened.

BEIR document payload is frozen as `title + newline + text` when a title is present, otherwise the available field alone. Identical query/document IDs are excluded, matching BEIR's default evaluation convention.

## Metrics

Primary descriptive metrics retained from the earlier generalization run:

- Recall@3
- nDCG@10

Secondary metrics:

- Recall@10
- Recall@100
- MAP@100
- MRR@10

nDCG uses trec_eval-style linear graded relevance gains. Per-query SIGN-minus-FLOAT differences are averaged over nuisance trials and receive paired query-bootstrap 95% confidence intervals.

## Integrity boundary

- Frozen V52 adapter SHA-256 must match `0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722`.
- Frozen T4C2 geometry source SHA-256 must match `3bb1126090ab619c061d10d0f1a5c20db1372c5e2cd66b5158905a65f460061b`.
- Official BEIR ZIP MD5 hashes are checked before extraction.
- Rankings are written and SHA-256 hashed before qrels are parsed.
- `96 bits = 12 active SIGN code bytes` is not a whole-system storage-cost claim. TF-IDF vocabulary/IDF, projectors/SVD state, and any indexing structure remain excluded from that number.

## Interpretation rule

This wave can support or weaken cross-corpus generalization, but it cannot establish universal superiority. Sign reversals are expected to remain scientifically meaningful. Any publication-level claim requires an independent implementation/reproduction rather than only repeated execution of this repository's code.
