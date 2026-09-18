# NEXT_5 — ranked experimental plan

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Ranked by **information gained per CPU-hour**, not hoped-for gain. Every item
states: question, arm, prespecified success criterion (fixed BEFORE running —
these paragraphs ARE the preregistration draft), honest cost, strongest reason
it will FAIL, and what we learn if it fails. Evidence cited from CRITIQUE.md
(`C§1a` etc.) is not re-argued here.

Graduation rule assumed throughout (from C§1d): no arm leaves exploratory
without (i) one prespecified contrast, (ii) same-sign replication on a second
benchmark or held-out archives, (iii) effect larger than the archive-level
spread. Anything not on a path to graduation is marked WORTHLESS and dropped
(list at the end).

---

## #1 — Untruncated TF-IDF cosine vs BM25 (name the real villain)

- **Question.** Is SVD the villain, or is the defect at/before term weighting?
  (C§1a: the float<BM25 gap is representation-or-query-folding jointly.)
- **Arm.** Frozen TF-IDF vectors (same word+char tokenization as production,
  NO LSA, NO SVD, NO truncation), cosine scoring, RealTalk. Deterministic; zero
  new fitting choices. References: float_std 48.51, BM25 54.18 [COORDINATOR].
- **Prespecified success criterion.** Single contrast, paired
  archive-clustered bootstrap (20000 reps, seed 20260916), Hit@10: if
  TF-IDF-cosine lands within ±2pp of BM25 → **SVD is the villain** (stop all
  quantization/SVD-tuning work, change family). If it lands within ±2pp of
  float_std or below → **the villain is term weighting/scoring or earlier**
  (stop touching SVD; work BM25-style saturation/length-norm into the
  pipeline). Midway (elsewhere) → inconclusive BY DESIGN, see fail-lesson.
- **Honest cost.** Minutes. Sparse cosine over cached texts; no SVD refit, no
  index build beyond a counter.
- **Strongest reason it will FAIL.** BM25's TF saturation + length
  normalization routinely beat raw cosine even untruncated, so the likely
  outcome is "midway below BM25" — informative about scoring but not the clean
  kill either camp wants. Second risk: query-side handling differs (fold-in vs
  raw query vector), smuggling the query-folding confound back in.
- **What we learn if it fails.** A midway outcome still bounds SVD's marginal
  guilt (untruncated-minus-float = the truncation/warp component, measured for
  the first time) and redirects the programme to scoring/weighting — which is
  where BM25's actual machinery lives. No outcome leaves the plan unchanged.
- **Worth check.** Positive result changes the recommendation either way
  (abandon SVD vs abandon bit-tuning). NOT worthless.

## #2 — Split-half execution of the IDF_p2 rare-band claim (the zero-CPU killer)

- **Question.** Does the +4.78pp rare-band FR@3 gain survive prespecification,
  or is it the expected false positive out of dozens of cells? (C§1c.)
- **Arm.** IDF_p2 vs FULL, qscale, FR@3, rare band ONLY — banding = coordinator
  tokenization-2 recipe, cutoffs 2/4, multi-gold FR@3 = mean of
  |gold∩top3|/|gold|, 705 valid queries, no_shared (n=7) dropped (decided
  here, now). Split: odd/even qid within archive. The test runs ONCE on the
  held half with the same bootstrap; the other half is never contrasted.
- **Prespecified success criterion.** Same-sign gain on the held half with 95%
  CI excluding 0 → mechanism survives to LME replication. Anything else
  (wrong sign, CI covers 0) → the claim is retired AND the graduation rule
  becomes programme policy. PerLTQA reversal (−1.76 SIG) is reported as-is win
  or lose — no goalpost-moving.
- **Honest cost.** ~Zero. Stored `math_r1/repr/per_query.jsonl` + band code
  already in this directory (`check_decisive.py` §B). Minutes.
- **Strongest reason it will FAIL (my prior: ~70% it fails).** Halving n widens
  CIs; the full-sample lower bound is already +0.69; within-benchmark archive
  effects range −8.43 to +12.76, so either half can wash out. A "fail" here may
  mean underpowered rather than false — which is itself the lesson (see below).
- **What we learn if it fails.** Post-hoc subgroup SIGs in this programme do
  not replicate; every RealTalk-first claim reverts to hypothesis status; the
  methods rule (prespec + replication) is adopted with a worked example of why.
  That lesson is worth more than the arm. If it SURVIVES, the lesson is
  "mechanism deserves LME replication with raw texts" — also decisive.
- **Worth check.** Kills or saves a research line at ~zero CPU. NOT worthless.

## #3 — BM25-rerank restricted to CODE's top-100 (price the dumb text signal)

- **Question.** How much of the oracle gap (FR@3 22.41→61.30 @100
  [COORDINATOR]) does DUMB text signal recover — i.e., is the rerank ceiling
  semantic or just lexical? (C§2.2.)
- **Arm.** For each query, score ONLY CODE's top-100 pool with BM25, take
  top-10/top-3. Inputs all STORED (`firststage/per_query.jsonl` pools + BM25
  machinery). Comparators, all prespecified: CODE own (49.65/22.41), RRF own
  (55.74/31.45), oracle ceiling (—/61.30).
- **Prespecified success criterion (decision thresholds, not hopes).**
  Gap-closed = (arm − 22.41)/(61.30 − 22.41) on FR@3: ≥50% → text signal
  suffices, kill all learned-reranker plans; 20–50% → rerank helps but pool
  composition dominates, work FIRST-STAGE recall instead; <20% → the gap is
  semantic, so either price a real (local, byte-counted) text model honestly
  or exit reranking. Hit@10 reported, FR@3 decides (stated now).
- **Honest cost.** ~Zero CPU beyond recomputation; storage cost already counted
  (needs the BM25 index — the honest marginal is stated, not hidden).
- **Strongest reason it will FAIL.** Pool restriction may destroy what makes
  BM25 good (global rank calibration across the full corpus; top-100 of CODE
  is BM25-adversarially selected — the 49 CODE-only queries are ones BM25
  scores badly). Outcome ≈ RRF own-ranking would mean gains come from pool
  COMPOSITION, not reranking — killing the rerank framing, which is still
  information.
- **What we learn if it fails.** "Reranking" as a programme direction is
  misnamed: the action is all in pool construction (fusion), and reranker
  budgets should be reallocated to first-stage recall. Either outcome reprices
  the direction. NOT worthless.

## #4 — Equal-storage shootout: 600-bit codes vs fusion (reframe the goal)

- **Question.** At 75 B/doc (the compact-index budget [MEASURED HERE]), do
  bigger codes beat CODE+BM25 fusion — i.e., is 12B even the right operating
  point? (C§2.3.)
- **Arm (ONE, prespecified).** Keep k=96, quantize each dim to ~6 bits
  (~600-bit budget, Lloyd-Max 1D per axis fit on DOCUMENTS ONLY — thresholds
  from docs, never queries; quantile-init explicitly BANNED given the known
  negative result [COORDINATOR]). Doc-side magnitudes now carry information;
  scorer = whitened-dot on level-centroids (the float-dot analog,
...[truncated 3888 chars]