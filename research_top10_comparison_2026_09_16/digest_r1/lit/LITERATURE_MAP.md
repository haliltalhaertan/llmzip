[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# LITERATURE MAP — what is already known about the phenomena we measured

Role: literature analyst. No experiments. All paper content below is
RECALLED-FROM-MEMORY (no web access in this session) unless tagged otherwise.
Nothing here is a verified quote. Numbers quoted from the programme are tagged
MEASURED HERE and come from the coordinator's re-derived digest
(`../FINDINGS_DIGEST.md`), not from my own runs. Derivations from first
principles are tagged CONJECTURE or PROOF-SKETCH (checkable without any paper).
"UNVERIFIED" means: I cannot confirm this from a file on this disk; it must be
fetched before it can be cited or used to kill/promote an arm.

Already-scanned sources (NOT re-reported as new): the 11 full sources + 13
snippet sources listed in
`../../inventory/literature/DO_NOT_RESCAN.md` (PPLX, Nemotron, Qwen3,
Anthropic Contextual Retrieval, BPR, Extended RaBitQ, MUVERA, MuSiQue panel,
BGE-M3, ConvMemory v2, plus hashing/KV-cache snippets). None of the four
starter items below, and none of the five questions' core literatures
(all-but-the-top, RRF, BM25 saturation, rate-distortion-for-retrieval), appear
in that list. [MEASURED HERE — established by reading the inventory file.]

---

## STARTER ITEMS — what I actually know, and what must be verified

### S1. Husbands, Simon, Ding — "Term norm distribution and its effects on LSI" (2005)
- Status: RECALLED-FROM-MEMORY, low-to-medium confidence on details.
- What I can say honestly: I recall a paper in this line arguing that LSI/SVD
  is dominated by high-norm (high-variance) terms, so low-norm/rare terms are
  poorly represented, and that some form of term normalization/weighting is the
  remedy. This is *consistent* with our mathematics and measurements, but I
  cannot confirm from disk that this paper exists under exactly this
  title/venue/year, what normalization it proposes (row norm? column norm?
  TF-IDF variant?), what corpus it tests on, or whether it examines anything
  like an IDF power dial. Do NOT treat the reviewer's one-line gloss as a
  verified summary.
- Why it is plausible anyway (PROOF-SKETCH, no paper needed): TruncatedSVD
  minimizes Frobenius reconstruction error. A term column's contribution to
  that objective scales with its squared norm, so all else equal, rare-term
  columns get less of the rank-k budget. Our leverage identity
  (sum_i rho_i = k, MEASURED HERE to 1e-14) plus our reconstruction medians
  (df=1 ~0.15–0.19 vs df>20 ~0.53–0.55, MEASURED HERE) are exactly the shape
  this mechanism predicts. The math stands even if the attribution fails.
- What would settle it: fetch full text; verify title/authors/venue/year;
  record the exact normalization proposed and whether rare-term emphasis
  limits/backfire are discussed. Rank 1 in VERIFY_QUEUE.

### S2. Ando & Lee — "Iterative Residual Rescaling" (SIGIR 2001)
- Status: RECALLED-FROM-MEMORY, low-to-medium confidence.
- What I can say honestly: I recall Ando working on LSI's sensitivity to
  skewed topic distributions (dominant topics capture the top singular
  vectors; minority topics are washed out) and an iterative reweighting/rescaling
  remedy. I cannot confirm the exact title, that Lee is the co-author, that
  the venue is SIGIR 2001, the algorithm's update rule, its test collections,
  or whether it reports benchmark-dependent sign reversals. The reviewer's
  gloss ("LSI distorted by imbalanced topic distributions; compensates") is
  UNVERIFIED as a summary of the paper.
- Relevance caveat (CONJECTURE): our setting is per-archive SVD over small
  (~400–900 doc) conversational archives, not one global SVD over a TREC-style
  collection, so even a correct Ando & Lee result transfers only by analogy
  (dominant-topic distortion within an archive). It does NOT directly predict
  our IDF^p or SHIFT reversals.
- What would settle it: fetch full text; verify bibliographic details, problem
  setup (global vs per-subset SVD), remedy, and whether any reversal/robustness
  across collections is reported. Rank 5 in VERIFY_QUEUE.

### S3. Guo et al. — ScaNN anisotropic quantization (ICML 2020)
- Status: RECALLED-FROM-MEMORY, medium confidence on the core idea, low on details.
- What I can say honestly: I recall the ScaNN line introducing an
  *anisotropic* (score-aware, asymmetric) quantization loss: penalize inner-product
  (parallel-direction) error more than orthogonal error, because for
  maximum-inner-product retrieval only the score-direction error matters. I
  recall this beating reconstruction-optimal quantization at equal bitrate on
  retrieval metrics. I cannot confirm authors/year/venue from disk, the exact
  loss form, the anisotropy constant, datasets, or numbers. Any equation or
  number attributed to it is UNVERIFIED.
- Why it matters here (CONJECTURE, but the analogy is tight): it is the
  cleanest recalled precedent for "reconstruction-optimal ≠ retrieval-optimal,"
  which is one of our Q1 candidate explanations. It does NOT test ITQ, sign
  codes, or TF-IDF/SVD inputs, so it supports the *principle*, not our
  specific -14 pp number.
- What would settle it: fetch full text; verify the loss, the
  reconstruction-vs-retrieval comparison, and the scope (dense embeddings only).
  Rank 4 in VERIFY_QUEUE.

### S4. Drineas et al. — statistical leverage scores (JMLR 2012), rho_i = sum_j U_ij^2
- Status: the IDENTITY is certain by proof (no fetch needed); the ATTRIBUTION
  is RECALLED-FROM-MEMORY and UNVERIFIED.
- PROOF-SKETCH (checkable now): let U_k be n×k with orthonormal columns. Row
  i leverage rho_i = ||e_i^T U_k||^2 = sum_{j≤k} U_ij^2. Sum over i:
  sum_i rho_i = ||U_k||_F^2 = trace(U_k^T U_k) = trace(I_k) = k. Exact.
  The digest's 1e-14 numerical verification (MEASURED HERE) is therefore a
  check of code correctness, not evidence for a empirical claim.
- What I recall (UNVERIFIED): leverage scores in this form are standard in
  randomized numerical linear algebra (CUR decomposition, column subset
  selection, least-squares sampling), associated with Drineas/Mahoney/Muthukrishnan
  and co-authors; a JMLR 2012 paper of Drineas et al. is a plausible canonical
  reference but I cannot confirm it states this identity or anything about
  retrieval. Nothing in that line, to my recall, says anything about IR,
  rare-term ranking, or bit codes — the *application* of rho to "unique-feature
  retention budget" is OUR interpretation (CONJECTURE, though the budget math
  plus the co-occurrence counterexample in the digest correctly limit it: rarity
  alone does not determine rho).
- What would settle it: fetch the cited paper; verify it contains the identity
  and record what it actually claims (sampling guarantees, not retrieval).
  Rank 6 in VERIFY_QUEUE. Note: settling the attribution changes no number.

---

## Q1. Why does rotation (ITQ AND random) HURT? — verdict: PARTIALLY KNOWN / OPEN

**Verdict: PARTIALLY KNOWN mechanism classes; OPEN as a measured regime.
Confidence: medium.** The *classes* of explanation exist in recalled
literature; the specific phenomenon — ITQ ≤ random, -14 to -17 pp on RealTalk
vs ~-1 pp on PerLTQA, rotation improving textbook bit-balance while hurting
retrieval (MEASURED HERE) — is not, to my recall, reported anywhere.

- Evidence (MEASURED HERE): RealTalk Hit@10 qscale FULL 49.65 | ITQ 32.77 |
  random 35.04 (3 seeds 34.61–35.32); PerLTQA FULL 80.00 | ITQ 78.91 | rand
  79.04. ITQ−random = −2.27 pp / −0.13 pp. Bits MORE balanced after rotation
  (per-bit range 0.309–0.658 → 0.459–0.545) with WORSE performance.
  sign(C/sigma)==sign(C) identity (0/63552 doc bits changed) proves only
  rotation/shift can move bits in this pipeline.
- Candidate (a) — axis-aligned/sparse, individually-meaningful coordinates:
  CONJECTURE with weak recalled support. I recall hashing-literature discussion
  that PCA axes on skewed, heavy-tailed data should not be blindly mixed, and
  that variance-equalizing rotations waste capacity on low-signal directions —
  but I cannot name a paper that *shows* rotation hurting on TF-IDF/SVD sign
  codes, so this is our conjecture until verified. Falsifiable prediction we
  already own (CONJECTURE): rotation within a single channel should hurt less
  than rotation that smears LSA/TFIDF/char channels together; the digest's
  channel-ablation reversals (char ESSENTIAL on RealTalk, HARMFUL on PerLTQA,
  MEASURED HERE) make this testable without new literature.
- Candidate (b) — reconstruction-optimal vs retrieval-optimal:
  PARTIALLY KNOWN by analogy (ScaNN anisotropic quantization, S3 above,
  RECALLED-FROM-MEMORY). ITQ minimizes ||B − VR||_F (quantization error),
  which is a reconstruction objective; NOTHING in that objective knows about
  gold Hit@10. Supported as a principle; unsupported as the *quantitative*
  cause of −14 pp. Needs ITQ-paper verification (objective + eval protocol).
- Candidate (c) — bit-balance as a bad proxy: MEASURED HERE as a phenomenon
  (balanced-worse); RECALLED-FROM-MEMORY only as folklore (I recall balance /
  variance criteria as design goals in Spectral Hashing and ITQ, but no
  recalled paper *demonstrating* balance anti-correlating with retrieval).
  Until a source is fetched, "balance is a bad proxy *here*" is OUR finding,
  not a citation.
- Candidate (d) — TF-IDF/SVD inputs vs ITQ's usual dense-embedding setting:
  SUPPORTED as a scope fact at low-medium confidence (RECALLED-FROM-MEMORY: I
  recall ITQ evaluated on dense visual descriptors such as GIST/SIFT/CIFAR —
  UNVERIFIED, must check the ITQ paper's datasets), plus MEASURED HERE scope
  (our features are per-archive TF-IDF/SVD, centered, signed). The causal step
  ("therefore ITQ fails") remains CONJECTURE.
- Benchmark interaction (−14 pp vs −1 pp): OPEN. No recalled source predicts
  this split. The digest's own regularity — "sign reversal is the norm in this
  programme" (MEASURED HERE) — is currently a better predictor than any cited
  paper.
- To settle: fetch (i) the ITQ paper — verify objective, datasets, metrics,
  and whether any negative/ablation regime is reported; (ii) Spectral Hashing
  (Weiss et al.) — verify the balance/variance assumption ITQ inherits;
  (iii) ScaNN — verify the retrieval-vs-reconstruction precedent. Ranks 2–4.

## Q2. Is "all-but-the-top" known, and are sign reversals reported? — verdict: KNOWN technique / OPEN reversal

**Verdict: technique KNOWN (medium-high confidence, still UNVERIFIED until
fetched); our application + benchmark-dependent SIGNIFICANT reversal OPEN.
Confidence: medium-high on existence, low on details.**

- What I recall (RECALLED-FROM-MEMORY, UNVERIFIED in every detail): "All-but-the-top"
  is postprocessing for *static word embeddings* (Mu, Bhat, Viswanath — I
  recall ICLR 2018 but am not certain of venue/year): subtract the mean and
  remove the first few principal components, motivated by removing
  frequency/common-word bias and improving isotropy; reported gains on word
  similarity / sentence-similarity tasks. I cannot confirm authors, venue,
  number of components removed, tasks, or numbers from disk.
- Three mismatches with ours that keep this PARTIALLY KNOWN at best
  (CONJECTURE, checkable against the fetched paper): (1) classic ABTT is
  applied to word vectors, not to per-archive TF-IDF/SVD document codes;
  (2) classic ABTT *subtracts* top PCs (same dimensionality, denoised), while
  our SHIFT_m1 *replaces* components m+1..m+96 (discards top, appends lower —
  still exactly 96 dims, MEASURED HERE); (3) our effect is a cross-benchmark
  SIGNIFICANT reversal (PerLTQA SHIFT_m1 Hit@10 +1.58 CI [+0.69,+2.47] SIG vs
  RealTalk −0.28 ns and sym FR@3 −1.06 CI [−2.02,−0.03] SIG, MEASURED HERE) —
  I recall NO paper reporting a significant win on one benchmark and a
  significant loss on another for this technique; hyperparameter sensitivity
  (how many PCs to drop) is recalled as folklore, not as a SIG reversal.
- To settle: fetch the ABTT paper; verify object, operation, tasks, and
  whether any negative/cross-dataset result is reported. Rank 3. Also check
  citing/follow-up work for isotropy critiques (recalled: debate over whether
  isotropy explains the gains — UNVERIFIED, secondary).

## Q3. IDF power: how far can rare-term weighting be pushed? — verdict: PARTIALLY KNOWN tradeoff / OPEN dial + reversal

**Verdict: PARTIALLY KNOWN (the tradeoff is old); OPEN (IDF^p as a dial, the
band-localized mechanism, and the cross-benchmark SIG reversal). Confidence: medium.**

- Evidence (MEASURED HERE, with the digest's own caveat): RealTalk FR@3 qscale
  IDF_p2 rare band +4.78 pp CI [+0.69,+8.43] SIG (replicated +4.83 under second
  tokenization), Hit@10 in-band +0.49 ns (ordering, not pool); PerLTQA IDF_p2
  FR@3 −1.76 CI [−2.78,−0.74] SIG, IDF_p1 −1.17 SIG. Subgroup chosen AFTER
  seeing results — exploratory only (digest's caveat, endorsed here).
- What is KNOWN-by-folklore (RECALLED-FROM-MEMORY, needs fetch): IR has
  institutionalized *both sides* of this tradeoff — IDF rewards rarity
  (Salton SMART tradition), while TF saturation (BM25 k1), length normalization
  (pivoted normalization, Singhal et al. — recalled), and log-entropy LSI
  weightings (recalled: often beating raw TF-IDF on TREC — UNVERIFIED) exist
  precisely because raw rare-term emphasis is noisy (typos, OCR, burstiness).
  "Pushing rarity too far backfires" is therefore an old qualitative
  prediction; but I recall NO paper testing an IDF^p dial to p=2 with
  band-level FR@3 on small per-archive SVD codes, and NO paper predicting the
  *same* arm SIG-helps one benchmark and SIG-hurts another.
- Husbands et al. (S1) is the claimed closest prior art for the *help* side;
  Ando (S2) for the *distortion* side. Both UNVERIFIED. Neither, on the
  reviewer's gloss alone, predicts a SIG reversal.
- A mechanism worth naming (CONJECTURE, consistent with MEASURED HERE): the
  rare band is where BM25 beats us most (+14.37) and the only band IDF_p2
  helps — i.e., IDF^p moves our codes *toward* lexical behavior where lexical
  has headroom (RealTalk rare) and *away* from distributional behavior where
  distributional wins (PerLTQA common/mid, where WE win per the digest
  stratification). This predicts the reversal from corpus composition (rare-band
  share, paraphrase vs verbatim rate), not from p itself. Testable on disk
  (band shares × arm deltas); no new literature needed for the *correlation*,
  literature needed for whether anyone stated it first.
- To settle: fetch Husbands et al. (rank 1), BM25 saturation/length-norm
  primaries (rank 8), and any LSI-weighting comparison (log-entropy vs TF-IDF,
  rank 9). Ask of each: is there a stated limit on rare-term emphasis, and is
  any cross-collection reversal reported?

## Q4. Hybrid RRF: WHY does it win, and what is honest storage accounting? — verdict: WHY known / ACCOUNTING open

**Verdict: WHY (complementarity) KNOWN at folklore level (medium confidence,
UNVERIFIED in detail); honest-storage-accounting practice OPEN/UNVERIFIED —
do NOT quote any claim about what "published hybrids typically do" until the
coordinator audits papers one by one. Confidence: medium on why, low on the
field-practice claim.**

- Evidence (MEASURED HERE): RealTalk pool@100 CODE 75.60 | BM25 78.16 |
  RRF(k=60) 81.28; RRF−CODE +5.67 CI [+3.23,+8.20] SIG; RRF−BM25 +3.12 SIG.
  Complementarity counts: CODE-only 49, BM25-only 67 queries. Honest cost:
  codes+sigma 115,008 B vs BM25 varint delta-gap index 670,511 B (~5.8×);
  pickle 1,450,229 B explicitly NOT quotable (digest). Index+raw-text
  1,669,165 B.
- WHY (RECALLED-FROM-MEMORY): rank-fusion (I recall RRF from Cormack, Clarke,
  Buettcher, SIGIR 2009 — UNVERIFIED) is recalled as robust precisely under
  input complementarity, with the standard lexical-vs-semantic division of
  labor: lexical wins verbatim/rare, dense/distributional wins paraphrase — a
  division our stratification directly instantiates (we win common/mid,
  BM25 wins rare, MEASURED HERE). This explanation is therefore consistent but
  circular if cited as confirmation: our numbers *are* the complementarity,
  not independent evidence for the theory.
- ACCOUNTING (the decision-relevant part): I recall MIXED practice —
  dense-retrieval papers variously reporting vector bytes only, vector + index
  overhead, or full system footprints, with inverted-index costs sometimes
  footnoted or omitted — but this is a weak, aggregate recollection and I
  CANNOT attribute it to any specific paper from disk. The honest statement
  is: **UNVERIFIED whether any given published hybrid charges itself for the
  BM25 index; the coordinator must check each cited comparison individually.**
  Our programme's position is strong regardless: we HAVE done the honest
  accounting (MEASURED HERE), including the varint-vs-pickle distinction —
  that methodology is ours and stands without a citation.
- Implication (CONJECTURE, decision-relevant): any "12-byte code + RRF" claim
  that does not add ~5.8× storage (plus raw text at serve time) is a
  category error, not a 12-byte result. This needs no literature to enforce —
  it follows from our own byte counts.
- To settle: fetch the RRF original (verify formula, k=60, and what it claims
  about complementarity — rank 7a) and audit 2–3 specific hybrid baselines the
  programme actually compares against for their storage reporting (rank 7b;
  named only after the coordinator picks the comparison set — I will not
  invent which papers those are).

## Q5. Is there a bits→recall ceiling bound for 96 bits / ~900 docs? — verdict: OPEN

**Verdict: OPEN. I recall NO established rate-distortion or information-theoretic
bound that maps bits-per-document to achievable Recall@K / Hit@10, and a naive
counting bound is vacuous here. Confidence: medium-high that no plug-and-play
bound exists (a negative claim — inherently harder to verify; needs a targeted
search, rank 10).**

- Evidence (MEASURED HERE): scorer-oracle (pick better of our two scorers per
  query, knows gold) saturates at ~55% on RealTalk — the ~45-point gap is
  representational, not ranking-order. Do not conflate with the rerank-oracle
  (FR@3 22.41→61.30 @100 cands, MEASURED HERE), which bounds a different
  thing (pool quality vs scorer choice).
- The counting argument that does NOT work (PROOF-SKETCH): 96 bits address
  2^96 codewords ≫ ~900 docs/archive (RealTalk 8944/10 ≈ 894; PerLTQA
  12288/30 ≈ 410, MEASURED HERE). Capacity for *distinguishing documents* is
  not the constraint. The constraint is *query-side generalization*: the query
  must land on the gold codeword through the same lossy 96-dim spectral
  bottleneck that already loses to BM25 uncompressed (48.51 vs 54.18,
  MEASURED HERE — the digest's central diagnosis). Any bound that counts
  codewords without modeling the query mapping answers the wrong question.
- What theory I recall (all RECALLED-FROM-MEMORY, none applicable off-shelf):
  Shannon rate-distortion covers *reconstruction* distortion, not top-K
  retrieval indicator loss; binary-hashing/LSH theory gives *query-time /
  approximation* tradeoffs for neighbor search, not gold-recall ceilings at
  fixed K over labelled queries; Fano-type arguments could lower-bound error
  given mutual information I(query-code; gold), but I(gold; code) for our
  pipeline is itself unmeasured — the bound would be a research project, not a
  citation. I also recall NO source reporting gold Hit@10 at K=10 from
  ≤12–16 B/doc codes on any corpus (digest: confirmed absent from fetched set,
  MEASURED HERE as a coverage statement) — consistent with "no bound exists
  because the regime is unstudied," not with "a bound forbids it."
- What would settle or advance it: (1) a targeted search for
  rate-distortion-for-retrieval / hashing lower bounds / "bits vs recall"
  results (rank 10; success = a real theorem with stated distortion measure,
  or a documented null); (2) on-disk work outside my role: estimate
  I(code; gold) or a query-generalization gap directly — that is an experiment,
  not a fetch, and I propose nothing further here.

---

## WE ARE REDISCOVERING (measured instances of established principles — fetch to confirm attribution, not existence)

1. SVD/Frobenius under-represents low-norm (rare) features; term weighting is
   the classical remedy. [MEASURED HERE instance (recon 0.15 vs 0.53);
   principle RECALLED-FROM-MEMORY via S1; math PROOF-SKETCH certain.]
2. sum_i rho_i = k leverage budget — mathematical identity, verified 1e-14.
   [MEASURED HERE; PROOF-SKETCH certain; attribution to Drineas et al.
   RECALLED-FROM-MEMORY/UNVERIFIED.]
3. Reconstruction-optimal ≠ retrieval-optimal as a principle (score-aware
   quantization beats Frobenius-optimal at equal bitrate).
   [RECALLED-FROM-MEMORY via S3; our ITQ failure is a candidate instance,
   CONJECTURE.]
4. "All-but-the-top" removal of leading components as a denoising operation.
   [Technique RECALLED-FROM-MEMORY; our SHIFT is a variant with an OPEN
   reversal, MEASURED HERE.]
5. Lexical+dense complementarity (verbatim/rare vs paraphrase) and RRF
   exploiting it to beat both inputs. [MEASURED HERE instance (49/67 split);
   principle RECALLED-FROM-MEMORY/UNVERIFIED.]
6. Rare-term emphasis is a double-edged sword (IDF value vs noise), the reason
   TF saturation and length normalization exist. [MEASURED HERE instance
   (band-localized gain + cross-bench loss); folklore RECALLED-FROM-MEMORY.]

## GENUINELY OPEN (not obviously covered by prior work; our data's contribution)

1. Rotation catastrophe in the TF-IDF/SVD→sign regime: ITQ ≤ random, −14 to
   −17 pp on one benchmark vs ~−1 pp on another, with balance improving as
   retrieval collapses. [MEASURED HERE; no recalled precedent.]
2. Bit-balance anti-correlating with gold retrieval at fixed 12 B.
   [MEASURED HERE; recalled literature treats balance as a goal.]
3. IDF^p: SIG rare-band-only FR@3 gain (+4.78) on RealTalk with null Hit@10,
   and SIG loss (−1.76) on PerLTQA, from the SAME arm. [MEASURED HERE,
   exploratory-subgroup caveat attached.]
4. SHIFT_m1: SIG win on PerLTQA (+1.58 Hit@10) and SIG harm on RealTalk
   (−1.06 sym FR@3) at identical 96-bit budget. [MEASURED HERE.]
5. Channel reversals: char channel significantly essential on RealTalk,
   significantly droppable on PerLTQA; LSA helps/hurts oppositely; WORD_ONLY
   5.6× faster AND +1.37 pp on PerLTQA. [MEASURED HERE.]
6. "No arm has EVER won on both benchmarks" as a programme-level regularity.
   [MEASURED HERE; the best cross-bench predictor we own, and unexplained.]
7. Honest 12 B vs BM25 accounting (varint 670 KB vs pickle 1.45 MB; ~5.8×;
   plus raw text) as an enforced reporting standard. [MEASURED HERE,
   methodological contribution.]
8. The 55% two-scorer oracle ceiling with a vacuous 2^96 counting bound —
   i.e., the representation/generalization gap stated as an open problem with
   no applicable theorem. [MEASURED HERE + PROOF-SKETCH.]
9. Budget-split decomposition (fusion design, not truncation, dominates loss
   at 80/16; 32-bit Bloom ≈ 5 distinct values/query — tie-break pathology).
   [MEASURED HERE; design-specific negative result.]

## What would change these verdicts

- Fetching S1 as described and finding it tests an IDF-like dial with a stated
  backfire point → Q3 moves toward KNOWN; finding it is purely about
  normalization without rarity analysis → Q3 stays PARTIALLY KNOWN and S1 is
  downgraded to background.
- Fetching the ITQ paper and finding its evals are all dense-descriptor ANN
  (no TF-IDF/SVD, no gold-recall) → Q1(d) firms up and the regime is confirmed
  OPEN; finding an ITQ ablation where rotation hurts on sparse/text codes →
  Q1 moves toward KNOWN.
- Fetching ABTT and finding cross-dataset negative results → Q2 reversal moves
  to PARTIALLY KNOWN; finding word-embedding-only scope → stays OPEN.
- A targeted search returning a real bits→recall theorem → Q5 moves; a
  documented null (search strategy recorded) → Q5 stays OPEN with higher
  confidence.
- Per-paper storage audit (Q4) is the only item that can be settled without
  any new theory: it is bookkeeping, and I have not done it (no web) —
  everything about field practice there is UNVERIFIED.
