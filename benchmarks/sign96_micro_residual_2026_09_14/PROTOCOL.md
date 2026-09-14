# SIGN96 micro-residual NanoBEIR protocol

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## Question

Can a very small, relevance-free magnitude residual reduce SIGN96 collisions/ties and recover retrieval quality without giving up the 96-bit sign code as the primary retrieval key?

## Frozen comparison

All methods start from the exact same centered 96-dimensional V52 representation.

- FLOAT96: centered cosine on all 96 real-valued coordinates.
- SIGN96: 96 sign bits, integer Hamming distance.
- SIGN96+4R: SIGN96 plus 4 magnitude-residual bits.
- SIGN96+8R: SIGN96 plus 8 magnitude-residual bits. **Primary candidate.**
- SIGN96+16R: SIGN96 plus 16 magnitude-residual bits.

Active bit budgets and minimum byte-aligned packed storage are:

- SIGN96: 96 bits = 12 bytes.
- SIGN96+4R: 100 bits = 13 packed bytes.
- SIGN96+8R: 104 bits = 13 packed bytes.
- SIGN96+16R: 112 bits = 14 packed bytes.

These are active-code sizes only; they do not include shared projector/vectorizer/index state.

## Residual construction — frozen before outcomes

The residual uses **corpus only**. No queries or relevance labels participate in fitting it.

1. Let `C` be the centered 96D corpus representation.
2. For each coordinate `j`, compute `Var(|C_j|)` across corpus documents.
3. Rank coordinates by decreasing `Var(|C_j|)`, deterministic coordinate index as the tie-break.
4. For each coordinate, compute the corpus median `median(|C_j|)`.
5. For an R-bit budget, take the first R ranked coordinates and emit one magnitude bit per coordinate:
   - 1 if `|C_j| >= corpus_median_j`
   - 0 otherwise.
6. Queries use the same frozen coordinate list and corpus-derived thresholds.

The +4, +8 and +16 residuals are nested prefixes of one frozen 16-coordinate order.

## Ranking rule

Residual bits are **not** allowed to overturn a strict SIGN96 Hamming advantage.

For each query/document pair rank lexicographically by:

1. base 96-bit Hamming distance,
2. residual Hamming distance (for +4R/+8R/+16R),
3. deterministic SHA-256 nuisance priority independent of relevance.

Therefore the experiment specifically tests whether a tiny magnitude signature can resolve Hamming ties/collisions; it is not a reweighted 100/104/112-bit Hamming method.

## Outcome-blind boundary

For every NanoBEIR task:

1. load corpus and queries only;
2. fit the V52 representation on corpus only;
3. derive the residual specification on corpus only;
4. generate FLOAT96, SIGN96, +4R, +8R and +16R top-100 rankings for 20 deterministic nuisance trials;
5. write the ranking tensor to disk and SHA-256 hash it;
6. only then load qrels and score outcomes.

## Primary and secondary endpoints

Primary scientific comparison:

- SIGN96+8R versus SIGN96, task-macro Recall@3 across the 13 frozen NanoBEIR tasks.

Secondary comparisons:

- +4R and +16R dose response;
- each residual method versus FLOAT96;
- nDCG@10, MRR@10 and MAP@100;
- exact code collision fraction and maximum collision bucket;
- top-3 boundary tie rate before relevance is opened;
- whether residuals preferentially rescue tasks where SIGN96 loses to FLOAT96.

No residual budget will be relabeled as the primary method after outcomes are observed.

## Interpretation boundary

This experiment can show whether small label-free magnitude residuals improve the existing SIGN96 retrieval phenomenon. It cannot establish novelty, a causal mechanism, a whole-system 13-byte cost, or external independent reproduction.
