# Bit-budget-vs-quality: concrete ideation from the axis-attack findings

**Labels: [IDEATION ONLY] [NO NEW COMPUTE] [NOT PREREGISTERED] [DISCLOSE-BEFORE-USE]**
**Anchor (all [E] = established, independently recomputed EXACT):** LME-470 native SIGN96 (12 B) FR@3 = 54.20%; float96 = 44.16%; ITQ96 = 37.61%; Haar96 = 38.27%. LoCoMo-1535 native = 23.65%, Haar = 13.77%. Subset curve (LME): 10 B ≈ −2.7 pp, 8 B ≈ −5.9, 6 B ≈ −9.2, 4 B ≈ −17, 2 B ≈ −34 vs native [E]. Random ≈ uniform-spread ≈ best on LME; bottom-variance tail best on LoCoMo (10 B ≈ −0.1 pp) [E]. Block-2 matched-variance pairing ≈ native on LoCoMo (−0.04 pp); disparate pairing −4.3 pp [E]. Train-only mean drop-loss at 64 bits: +3.4 pp vs random-mean, +1.6 pp vs best-of-3 seeds on one held-out half [E, single split]. All axes weakly discriminate (min delta 0.066); 30/96 drop-loss ≤ 0 [E]. Variance ranking actively harmful [E]. Encode chain bit-reproducible [E].

**Confidence legend used below:** [E] established fact · [H] high · [M] medium · [L] low · [SPEC] speculation. Every quantitative prediction is [SPEC] unless tagged otherwise. **No network was used; literature-check flags are marked [LIT-CHECK].**

---

## A. Codec design under a total-bytes budget

Byte accounting convention used throughout: budget in *slots*, 1 slot = 1 stored bit [E-protocol]. 12 B = 96 slots (native 96×1-bit); 8 B = 64 slots; 6 B = 48 slots; 4 B = 32 slots. Heterogeneous codes trade *axes covered* against *bits per axis*, e.g. at 8 B: 64×1-bit (64 axes) vs 48×1 + 8×2 (56 axes, 64 slots) vs 32×1 + 16×2 (48 axes, 64 slots).

### A1. Drop-guided "spread base + a few double-bits" (heterogeneous 1-bit/2-bit)

(i) **Description.** Keep a gold-free isotropic spread base (e.g. rank-linspace axes), then spend remaining slots on a *second* bit for the top-`m` train-only drop-loss axes (`m` = 8–16 at 8 B). Second bit = archive-marginal tercile quantization on that axis only (two thresholds from archive values, no gold, no cross-axis mixing). Decode = concatenated Hamming with 2-bit axes contributing 0/1/2 per-axis distance (equivalently two binary sub-bits). Candidate 8 B arms: `S48+8×2`, `S32+16×2`; 6 B arms: `S32+8×2`, `S24+12×2`. Thresholds frozen from train-archive marginals only [H-gold-free].

(ii) **Expected effect [SPEC, reasoning attached].** Marginal spread bits are worth ≈ +3.3 pp per 16 bits (64-bit mean 0.4829 vs 48-bit mean 0.4499 [E]), i.e. ≈0.2 pp/bit. A second bit must beat *dropping* ~8–16 spread axes. Prior: drop64's +3.4 pp vs random-mean at 64 bits [E] shows the drop utility identifies ~+0.05 pp/axis of selection value; a second magnitude bit on exactly those axes plausibly recovers 1–3 pp at 6–8 B [SPEC, M]. Predict largest win at 6 B (where spread base is thinnest and magnitude disambiguation matters most) [SPEC, L]. Do **not** expect >4 pp: seed spread alone is 3.5 pp at 48 bits [E], so anything ≤1 pp is noise-scale.

(iii) **Cheapest test on frozen matrices.** Train/test question split (reuse R2B 239/231 sha-parity split [E]). Train: compute drop-loss + archive terciles (train-archive only). Test (frozen protocol verbatim): compare `S+double-bits` vs k-matched spread vs 3-seed random at 32/48/64 slots. Gates: (a) native recompute EXACT to 1e-12; (b) report vs *best-of-3* random, not just mean (R2D lesson [E]). Kill criteria: kill if test gain vs best seed < +1 pp at both 48 and 64 slots, or if gain vanishes under one resplit (see C3); promote only if positive on *both* LME-test and LoCoMo (C1).

(iv) **Risk/failure mode.** Second bits concentrate budget on few axes, reducing axis coverage — directly fights Fact 1 (signal spread over all 96 axes [E]). If magnitude bits are redundant with sign bits on the same axis (high sign-magnitude correlation), the upgrade buys ~0 and the lost spread axes cost ~2–3 pp net [M]. Tercile thresholds estimated on train-archive may misfire on test queries [M].

(v) **NOES + prereg path.** Touches NOES **"alternate bit widths as a programme claim"** [H] (any 2-bit arm is a width claim) and arguably **"learned thresholds"** (terciles from archive — disclose as threshold learning even though gold-free). Path: this pilot (train-only thresholds/selection) → disclose both pilots → preregister fixed `m`, thresholds-source, and distance rule, tested on held-out questions + second benchmark.

### A2. Archive-entropy / tail-emphasis allocation rule (gold-free, no learning)

(i) **Description.** Allocate the 1-bit subset (or the A1 double-bit upgrades) by an *archive-only* statistic instead of variance or learned utility: (a) **bottom-tail rule** (BOT-k, motivated by LoCoMo BOT80 ≈ native−0.1 [E]); (b) **sign-entropy rule** (prefer axes with archive P(sign=1) closest to 0.5, i.e. max binary entropy); (c) **mid-tail / stratified rule** (rank-stratified sample forced to include bottom quartile — a hardened version of the spread arm that already wins [E]). All three are computable from the archive matrix alone, zero gold [H].

(ii) **Expected effect.** BOT-k: +0 to +5 pp vs TOP-k depending on benchmark (LoCoMo BOT48 0.181 vs TOP48 0.132 = +4.9 pp [E]; LME BOT48 0.428 vs TOP48 0.350 = +7.9 pp [E]) but vs *random* the edge is small: LoCoMo BOT48 +1.5–2 pp over random-mean [E]; LME BOT48 −2 pp vs random-mean [E]. So expected: bottom-tail ≈ random ±2 pp, never worse than −3 pp [SPEC, M]. Sign-entropy rule [SPEC, L]: expect ≈ random (all sign entropies likely near-max since deltas are small [M]); value is as a *principled gold-free spread* rather than a gain. Stratified-mid-tail [SPEC, M]: expect +0–1.5 pp over pure random by guaranteeing tail coverage.

(iii) **Cheapest test.** No split needed (no learning): evaluate BOT-k / entropy-k / stratified-k vs 3-seed random + rank-spread at 32/48/64/80 on LME *and* LoCoMo frozen matrices. Kill: kill any rule that loses to random-mean on *both* benchmarks at ≥2 budgets; promote only rules that win-or-tie on both.

(iv) **Risk.** Benchmark-dependence is already proven (best arm differs LME vs LoCoMo [E]), so any fixed tail rule overfits one benchmark's "where the good bits live" [H]. Entropy rule may be near-constant across axes (no selection power) [M].

(v) **NOES + prereg.** Touches none of whitening/PCA/rotations/reweighting/thresholds/reranking/supervised-rotation if restricted to 1-bit subset selection [H]. (If extended to weighting axes by entropy at decode, that becomes **variance/entropy reweighting** — disclose.) Path: exploratory comparison → preregister the single winning rule with fixed k-grid on the *other* benchmark as confirmation.

### A3. Per-axis scalar transforms: median-shift, deadzone ternary, companding (NOT rotations)

(i) **Description.** Apply a *per-axis, monotone, axis-independent* scalar map before the sign, three families: (a) **median-shift**: `sign(C_j − med_j)` with median from archive only; (b) **symmetric deadzone ternary**: `−1/0/+1` via `|C_j − med_j| < t_j` (t from archive IQR fractile), distance = ternary overlap; (c) **companding**: `sign(tanh(C_j/s_j))` or rank-Gauss per axis (archive-fitted `s_j`), still 1 bit out. Why plausibly safe [M]: rotations are known-bad because they *mix* high- and low-variance axes, creating variance-disparate pairs whose damage is proven monotone (−1.6 → −3.8 → −5.4 pp LME; −0.04 → −2.35 → −4.28 LoCoMo [E]). Per-axis monotone maps never mix axes, preserve within-axis order and axis identity, and only move the decision boundary — they cannot create a disparate pair [H-mechanistic, still SPEC as a gain claim].

(ii) **Expected effect.** Median-shift: +0–1 pp [SPEC, L] — matters only where archive marginals are skewed; most embedding axes are near-symmetric so shift ≈ 0 [M]. Deadzone ternary at fixed slot budget: costs extra bit(s) for the zero state; as a *pure* 1-bit deadzone (map zero-zone to +1 deterministically) expect ±0.5 pp noise [SPEC, L]. As a real ternary (1.58 bits/axis via packing, or heterogeneous A1-style where only some axes get the zero state): +0.5–2 pp at 6–8 B [SPEC, L], rationale: deadzone directly suppresses near-zero unreliable signs that likely feed boundary ties (mechanism §B1) [SPEC]. Companding: ≈0, ±0.5 pp [SPEC, L] — monotone rescaling barely moves `sign()` except via float rounding; value is as a preconditioner for tercile thresholds (A1), not standalone.

(iii) **Cheapest test.** Archive-only fitted transforms (no question split needed for a/b-median; split needed if fractile tuned). Arms at 48/64 slots: sign-native vs median-shift vs deadzone vs compand+sign, all on the *same* axis subset (spread-48) to isolate transform from selection [H-design]. Kill: kill if median-shift differs from native-sign by <0.5 pp on both benchmarks (then thresholds are irrelevant and A1 should use zero thresholds); kill deadzone if it never beats its slot-matched binary control.

(iv) **Risk.** Deadzone/ternary needs a packing or distance-rule change — engineering surface for protocol drift (tie-priority, K=3, fractional recall must stay verbatim) [H]. Tuning `t_j` on test-adjacent data leaks into threshold-learning NOES territory [H].

(v) **NOES + prereg.** Median-shift/deadzone touch NOES **"learned/alternate thresholds"** — disclose even though archive-only/gold-free [H]. Companding touches nothing if output stays 1-bit sign with frozen `s_j` [M], but if `s_j` rescales Hamming weights it becomes **variance reweighting** — avoid that variant. Path: pilot transform-on-fixed-subset → disclose → preregister one transform + one subset rule jointly.

### A4. Subtractive dither + frozen tie-break randomization (attack the tie mechanism directly)

(i) **Description.** Two coupled, gold-free stochastic tricks with a *frozen* PRNG (determinism preserved [E]): (a) **subtractive dither**: `sign(C_j + U_j)`, `U_j ~ U(−a,a)` with `a` = small fractile of archive `|C_j|` (one global `a`, archive-fitted); (b) **randomized tie-break**: replace/extend the 20-trial `stable_archive_seed` tie-priority evaluation with a larger-trial estimate, and at *codec* level break exact Hamming ties by dithered second-look (re-encode only tied docs with fresh frozen dither). Rationale: retrieval is decided by fine tie structure at top-3, not mean separation [E]; TOP48 has higher tie-rate (0.460 vs 0.426–0.451) and 3× duplicates [E]; dither converts systematic ties into measurable win-rate mass [SPEC].

(ii) **Expected effect.** Dither `a→0` recovers native exactly (continuity check) [H]. At tuned `a`: ±1 pp on FR@3-mean, but *variance reduction* across tie-trials is the real win [SPEC, M]. Do not expect mean gains >2 pp: duplicate buckets are small (mean largest 3.2 vs 2.5 [E]) and per-question gaps correlate ≈0 with bucket excess [E], so ties explain only part of the deficit. Best case: +0.5–1.5 pp at 4–6 B where tie-rates are highest [SPEC, L]. A negative result (dither hurts monotonically in `a`) is itself mechanistically informative (proves ties are load-bearing signal, not noise) [H].

(iii) **Cheapest test.** Dose-response in `a` (0, 0.05, 0.1, 0.25 × median-`|C|`) on fixed spread-32/48, 20→100 tie trials, frozen seeds; report mean FR + trial-std + tie-rate + duplicate-fraction. Gates: `a=0` must reproduce native EXACT [E-requirement]. Kill: kill if FR(a) is monotone-decreasing from `a=0` on both benchmarks (dither is pure damage); promote to codec only if some `a>0` beats `a=0` on *both* benchmarks or halves trial-std at equal mean.

(iv) **Risk.** Adds stochasticity to a currently bit-reproducible chain [E] — must pin PRNG + seed protocol or determinism claim is lost [H]. Over-dithering destroys the weak per-axis deltas (min 0.066 [E]) [M]. Temptation to tune `a` per question (needs gold) — forbidden; keep one global `a` [H].

(v) **NOES + prereg.** Touches no NOES item as a codec (not a width/rotation/reweight/threshold/rerank claim) provided `a` is archive-fitted and frozen [M]; the *evaluation* already uses tie-priority trials, so extending trials is protocol-consistent but must be preregistered as an evaluation parameter. Path: pilot dose-response → disclose → preregister one frozen `(a, seeds, trials)` triple.

### A5. Gold-free per-question adaptivity (only via proven predictors)

(i) **Description.** Per-question axis masks are *forbidden by default* (R2A: per-question variance effects are adaptive/unexplained [E]). Allow only masks driven by a predictor computable from query+archive with no gold: candidates (1) **query-confidence mask**: keep axes with largest query `|qC_j|` (hypothesis: large query magnitude = reliable sign [SPEC]); (2) **archive-density mask**: drop axes where the query's archive neighborhood is densest/most-tied (hypothesis: dense axes cause boundary ties [SPEC]); (3) **two-code fallback**: 6 B spread code for all docs + extra 2 B refinement retrieved only when top-3 margin < threshold (a *budgeted* rerank-analogue; margin from Hamming distances only, no float) [SPEC]. All keep total bytes ≤ budget in expectation or worst case (prespecify which).

(ii) **Expected effect.** (1) and (2): 0 to +1.5 pp [SPEC, L]; base rate for adaptivity is poor (no metadata variable correlates |r|>0.15 with flips [E]; question-type gaps exist but don't explain flips [E]). (3): +0.5–2 pp at fixed *mean* budget [SPEC, L], because bits are spent where the boundary is contested — the only adaptive scheme that directly targets the tie mechanism [M]. All three risk *negative* vs static spread if the predictor is miscalibrated [H].

(iii) **Cheapest test.** Predictor-validation *before* any codec: correlate predictor (query `|qC|`, neighborhood density) with per-question flip/survival on frozen spread-48 vs native, analysis-only with gold labels used *only* for validation (tag gold-informed [E-protocol]). Proceed to codec only if |r| or AUC clears a prespecified gate (e.g. AUC ≥ 0.60 on train half). Then train-half-fitted rule → test-half FR vs static spread at matched mean bytes. Kill: kill adaptivity entirely if no predictor clears AUC gate on train; kill fallback if worst-case bytes exceed budget or if mean-byte-matched static spread wins.

(iv) **Risk.** Highest overfitting risk in the portfolio: per-question rules have 470 (LME) / 1535 (LoCoMo) degrees of freedom to fool oneself with [H]. Violates the "spread/static wins" regularity [E] unless predictor is genuinely out-of-sample [H]. Fallback scheme invites NOES-reranking creep (see v).

(v) **NOES + prereg.** (1)/(2) touch nothing if mask stays 1-bit subset selection [M]. (3) borders NOES **"reranking"** — disclose as rerank-adjacent; keep it inside the byte budget with Hamming-only scores to stay outside the float-rerank NOES core, and preregister mean-vs-worst-case byte accounting explicitly [H]. Path: predictor-AUC pilot (tagged analysis) → disclose → preregister one frozen predictor + threshold.

---

## B. Mechanism probes (cheap, on frozen matrices)

### B1. Tie-mass decomposition at the top-3 boundary (the single highest-value analysis)

(i) **Description.** For each question × arm (native, spread-48, TOP-48, BOT-48, drop-64), record the *boundary micro-structure*: `d_gold`, `d_(1..4)` (sorted Hamming distances), tie-cluster sizes at `d_gold` and at the top-3 cutoff, `#strictly-closer`, `#tied-with-gold`, `#tied-at-cutoff`, trial win-rate over 100 frozen tie-priorities, and duplicate-bucket membership of gold. Decompose every flip (TOP48-loses / spread-wins) into: strictly-beaten vs tied-out-vs cut-tied vs duplicate-collapsed [SPEC-taxonomy].

(ii) **Expected effect [SPEC, M].** Predicts 60–80% of flip variance from 2–3 tie features (vs current best |r| ≤ 0.15 [E]) — because R2A already shows decisive questions have collapsed tie-clusters (loser example: TOP48 cluster 11 vs RAND48 cluster 1 [E]). Quantitative tell: if tied-out mass explains flips, P(flip | tied-at-cutoff) ≫ P(flip | strictly-beaten) with odds ratio ≥ 3 [SPEC]. This is *diagnostic*, not a codec gain — its value is killing or licensing A4/A5 [H].

(iii) **Cheapest test.** Pure recomputation on frozen matrices + frozen protocol; 100 tie trials; no new arms. Gates: reproduce R2A W/T/L 63/250/157 EXACT before extending [E]. Kill: if tie features still give |r| < 0.3 / AUC < 0.60 for flips, abandon tie-centric codecs (A4/A5-fallback) and pivot to B2/B3.

(iv) **Risk.** Correlational: tie features are *consequences* of subset choice, not necessarily causes [H]. Low risk otherwise (read-only, cheap) [H].

(v) **NOES + prereg.** No NOES touch (analysis-only, gold-informed tagging required [E-protocol]) [H]. Path: exploratory decomposition → preregister tie-predicted codec (A4/A5) with the decomposition features as the declared mechanism check.

### B2. Bit-influence / flip-attribution curves (which bits decide the boundary?)

(i) **Description.** Per decisive question, attribute the gold-vs-cutoff-competitor gap to individual bits: for the gold `g` and the boundary competitor `c*` (nearest non-gold at/inside top-3), compute agreement vector `agree_j = [sign(q_j)==sign(g_j)] − [sign(q_j)==sign(c*_j)]` ∈ {−1,0,+1}; aggregate over losers/winners: mean influence per axis, influence-vs-variance-rank curve, influence-vs-drop-utility curve, and cumulative-influence (how many top-influence bits cover 50% of the gap?) [SPEC-method].

(ii) **Expected effect.** Predicts: influence curve is *flat-ish* (top-10 bits cover <30% of gap), corroborating spread-beats-concentration [E→SPEC, M]; and loser-questions' influence concentrates in bottom-variance axes (R2A reading [E] → expect loser-influence bottom-quartile share ≥ 40% vs ~25% null [SPEC, L]). Kill-or-license value for A1 (are drop-top axes also high-influence?) [H].

(iii) **Cheapest test.** Frozen matrices, gold-informed analysis-only; 200 decisive questions suffice. Gate: influence of axis 94 (max drop-loss 0.011 [E]) must rank high but not dominant (sanity). Kill: if influence curve is indistinguishable from uniform-permuted null, drop attribution-based selection ideas.

(iv) **Risk.** Pair choice (`c*`) is ambiguous under ties (multiple competitors) — average over tied set or results depend on tie-priority [M]. Uses gold — must stay analysis-only [H].

(v) **NOES.** None (analysis) [H]. Path: → preregister influence-weighted selection only if curve is non-flat *and* stable across splits (C3).

### B3. Effective-dimension / participation-ratio of the discriminative subspace

(i) **Description.** Compute archive covariance eigenspectrum → participation ratio `PR = (Σλ)²/Σλ²`; plus per-question discriminative PR: covariance of (gold − top-competitors) direction ensemble. Test: do survivor questions (keep FR=1 down to 32 bits) live in lower-PR subspaces than flip questions? And does PR predict per-question k-at-collapse (smallest k with FR<1 along a fixed nested spread ordering)? [SPEC]

(ii) **Expected effect.** Expect weak-to-moderate signal (|r| ≈ 0.2–0.4 [SPEC, L]): high-PR (isotropic) questions should survive aggressive subsets better (more redundant encodings of the gold direction) [SPEC]. If true, PR becomes the cheapest gold-free survivability predictor (archive + query only) and licenses A5-density ideas [M-value].

(iii) **Cheapest test.** Archive eigen-decomposition once per benchmark (96×96, trivial); per-question PR vs k-at-collapse rank correlation on spread arms. Kill: |r| < 0.2 on both benchmarks → PR is not the mechanism; do not build codecs on it.

(iv) **Risk.** Eigenspectrum of raw continuous features may not track *sign-code* geometry (the codec sees only signs) [H]. Confounded with archive size N (LoCoMo vs LME scale differs) [M].

(v) **NOES.** None as analysis [H]; a PR-*weighted* codec would touch **variance reweighting** — do not go there without preregistration [H]. Path: analysis → (if strong) preregister PR-stratified evaluation (report FR within PR terciles).

### B4. Duplicate-code / cluster-structure audit (close the "not duplicate collapse" claim)

(i) **Description.** R2 established duplicates don't *linearly* explain gaps (corr ≈ 0 [E]) but left the cluster mechanism open. Full audit: bucket-size distribution per arm (native/spread/TOP/BOT at 96/64/48/32), P(gold-in-bucket-size-≥3), conditional flip-rate given gold-bucketed vs unbucketed, and bucket-persistence across nested subsets (does TOP-48 *create* gold-buckets that spread-48 avoids?) [SPEC].

(ii) **Expected effect.** Expect: TOP-48 creates 2–4× the gold-bucketed rate of spread-48 (from 2.35% vs 0.8% overall duplicate fractions [E] → predict gold-bucketed OR ≈ 2–3 [SPEC, M]), yet conditional flip-rate given bucketed explains ≤30% of total TOP48 deficit (residual = boundary-tie mass, B1) [SPEC, L]. Closes the mechanism loop either way [H-value].

(iii) **Cheapest test.** Exact counting on frozen codes; no trials needed for bucket census, 100 trials for conditional win-rates. Kill: if gold-bucketed rates are equal across arms, drop all duplicate-centric stories permanently.

(iv) **Risk.** Near-zero (counting) [H]. Only risk is over-interpreting small-bucket counts at 96 bits [M].

(v) **NOES.** None [H]. Path: directly preregisterable as a mechanism check inside any subset/heterogeneous preregistration.

### B5. Sign-reliability anatomy: per-axis agreement, entropy, and |q|-conditioning

(i) **Description.** Three archive/query-only statistics per axis, validated gold-informed once: (a) archive sign entropy `H_j`; (b) query-magnitude-conditioned agreement `P(gold agrees | |q_j| decile)` (tests the A5 query-confidence hypothesis); (c) margin-conditioned agreement `P(gold agrees | |C_j − med_j| decile)` (tests deadzone hypothesis A3). Report curves, not scalars — the question is *shape* (flat vs sloped) [SPEC].

(ii) **Expected effect.** (b): expect mildly sloped (top `|q|` decile +5–10 pp agreement vs bottom [SPEC, L]); if flat, kill A5-query-mask permanently — highest-leverage negative result in set B [H-value]. (c): expect sloped near zero (small `|C−med|` ≈ chance 50% + delta-min 0.066 regions [E] → near-zero magnitudes least reliable [SPEC, M]); if sloped, licenses deadzone A3 [H-value]. (a): expect near-flat (all H near 1 bit) [SPEC, M].

(iii) **Cheapest test.** Decile curves on train half, confirm on test half (split needed because thresholds/deciles are fitted) [H-design]. Kill gates prespecified: slope (top−bottom decile) < 3 pp → predictor dead, do not build codec on it.

(iv) **Risk.** Gold-informed validation must be tagged analysis-only [E-protocol]; decile fitting on small per-axis counts is noisy at extremes [M].

(v) **NOES.** Analysis touches nothing [H]; any codec built on (c) thresholds inherits A3's **learned-thresholds** disclosure [H]. Path: curves → preregister the single sloped predictor, if any.

---

## C. Robustness / generalization (on existing data)

### C1. Cross-benchmark utility transfer (the load-bearing generalization test)

(i) **Description.** Compute train-only drop/delta/alone utilities on LME-train and LoCoMo-train separately; report (a) rank-correlation of utilities across benchmarks (Spearman of 96-axis orderings), top-k overlap (Jaccard at 32/48/64), and (b) *transferred* FR: LME-drop-64 axes evaluated on LoCoMo (all questions) and vice versa, vs within-benchmark drop-64 and vs 3-seed random on the target [SPEC-protocol].

(ii) **Expected effect.** Expect utility rank-correlation modest (ρ ≈ 0.2–0.5 [SPEC, L]): top-variance-worst replicates [E] but best-arm location differs (random-best LME vs bottom-best LoCoMo [E]), so transfer should beat TOP but trail within-benchmark learning by 1–3 pp [SPEC, M]. If transfer ≈ random, learned selection does not generalize and only benchmark-local or universal (spread) rules are preregistrable [H-consequence].

(iii) **Cheapest test.** No new matrices; reuse R2B utilities + R2C LoCoMo replication code. Gates: within-benchmark numbers must reproduce EXACT (drop64 test 0.4838 LME [E]; BOT80 ≈ native LoCoMo [E]). Kill: transferred arm ≤ random-mean on target → do not preregister transferred utilities; preregister spread instead.

(iv) **Risk.** Benchmarks differ in archive size, category mix, and difficulty (test-half harder on LME [E]; LoCoMo Cat1 0.109 vs Cat4 0.288 [E]) — transfer gap may reflect difficulty, not utility instability [M]. Mitigate by reporting within-category transfer (Cat2/Cat4 LoCoMo vs temporal/multi-session LME) [M].

(v) **NOES.** None (evaluation design) [H]. Path: exploratory transfer matrix → preregister whichever of {spread, within-learned, transferred} wins with a fixed seed budget.

### C2. Question-type-conditioned selection (does heterogeneity help?)

(i) **Description.** R2A type gaps are large (single-session-user −0.30, knowledge-update −0.17, multi-session −0.06 mean TOP48−RAND48 gap [E]) yet no variable explains flips (|r| ≤ 0.15 [E]). Test the residual hypothesis: learn drop-utility *within* each question type on train, select per-type top-k, evaluate per-type on test vs global-drop-k and vs random. Types are metadata, not gold — conditioning is legitimate if type is known at query time [M-assumption, verify].

(ii) **Expected effect.** Expect small and fragile: per-type n is 30–127 (LME) [E], so per-type utilities are noisier than global; predict per-type selection beats global by ≤1 pp on large types (temporal n=127, multi-session n=121) and loses on small types (preference n=30) [SPEC, L]. The single-session-user outlier (−0.30 [E]) is the only type where a dedicated rule might clear +2 pp [SPEC, L].

(iii) **Cheapest test.** Train-half per-type utilities → test-half per-type FR; report per-type W/T/L + global aggregate (global aggregate is the preregistrable metric; per-type is diagnostic) [H-design]. Kill: if global aggregate of per-type selection ≤ global-drop on test, kill type-conditioning (report the R2A type table as descriptive heterogeneity, not a selection rule).

(iv) **Risk.** Small-n overfitting per type [H]; multiple-comparison fishing across 6 types [H] — prespecify the single aggregate gate. Type taxonomy may not exist on LoCoMo (different categories) → non-portable [M].

(v) **NOES.** None if 1-bit selection [H]. Path: pilot per-type → disclose → preregister at most one type-specific rule (the largest-train-n type) with the aggregate gate primary.

### C3. Split-robustness + seed-sweep protocol (the anti-fooling harness every codec idea must pass)

(i) **Description.** Not a codec — the harness that decides whether A1–A5/C2 are real: (a) repeated train/test splits (≥10: sha-parity variants + random-seed splits at same 239/231 ratio), reporting the *distribution* of test gain vs random-mean **and** vs best-of-3 (R2D lesson [E]); (b) selection stability: Jaccard of top-k across splits; (c) seed sweep on random baselines (≥5 seeds at 48 bits; current range 3.5 pp [E]) so every claim is calibrated against baseline noise [H].

(ii) **Expected effect.** Expect the R2B drop64 +3.4-vs-mean/+1.6-vs-best to shrink under resplit (median vs-best ≈ 0 to +1 pp [SPEC, M]) — single-split modest gains usually attenuate [M]. Stability: expect top-64 Jaccard ≈ 0.5–0.7 across splits (drop-loss top-5 [23,72,88,2,58] [E] likely stable core + noisy tail) [SPEC, L]. Harness value is negative-result throughput: kills ≥50% of A-ideas cheaply [H-value].

(iii) **Cheapest test.** Rerun frozen R2B script under new splits; no new codec code. Gate: harness itself must reproduce R2B split-0 numbers EXACT first [E]. Kill rule for *any* codec idea: median-vs-best ≤ 0 across splits, or top-k Jaccard < 0.4 (selection is noise) → do not preregister.

(iv) **Risk.** Compute cost is the only risk (10 splits × arms) — modest on frozen matrices [H]. Risk of misreading: a real but small effect (+1 pp) will look "unstable" under a ±1.5 pp seed-noise floor [E-noise] — prespecify that sub-noise effects are *correctly* killed, not pursued [H].

(v) **NOES.** None [H]. Path: adopt as the mandatory exploratory→prereg gate for every A-idea; cite its noise-floor numbers inside the preregistration.

### C4. Determinism + byte-budget Pareto harness (12/8/6/4 B decision instrument)

(i) **Description.** Freeze the decision instrument the programme actually needs: for each budget {12,8,6,4 B} report native + spread + BOT + 5-seed random + best-learned (A1–A3 winners) on *both* benchmarks with identical protocol (K=3, 20+ trials, fractional recall), plus cross-library determinism spot-checks (Fact 6 [E]) on the new arms' codes. Output is a Pareto table with seed-spread error bars — the "proper sub-12-byte arm set" already requested in round-1 §7 [E].

(ii) **Expected effect.** Expect the Pareto to confirm: 10 B ≈ −2.7, 8 B ≈ −6, 6 B ≈ −9, 4 B ≈ −17 (LME [E]) with LoCoMo flatter at top (BOT80 ≈ native [E]); learned/heterogeneous arms shift the curve by at most +1–3 pp at 6–8 B [SPEC, M]. Decision value exceeds any single codec gain [H].

(iii) **Cheapest test.** Assemble from existing arms + A-winners; no new mechanism work. Kill: any arm whose codes are not bit-reproducible under pinned stack fails the harness regardless of FR [H-gate].

(iv) **Risk.** Temptation to add float-rerank or width-family arms into the same table — keep byte-budget Hamming arms separate from any NOES-family comparison [H].

(v) **NOES.** Touches **alt bit widths as claims** wherever 2-bit arms appear — table must label pilot-vs-programme arms [H]. Path: this harness *is* the preregistration's declared analysis plan.

---

## Top-5 ranked ideas (one-line "why first" each)

1. **B1 tie-mass decomposition — first because every codec bet (dither, deadzone, fallback, even heterogeneous) assumes a tie story that is currently OPEN [E]; B1 is cheapest and kills or licenses three A-ideas at once.**
2. **A1 spread-base + drop-guided double-bits — first codec bet because it is the only heterogeneous design that respects all three hard facts simultaneously (spread > concentration [E], all-axes-signal [E], no variance-disparity mixing [E]) while exploiting the sole proven learned signal (drop utility [E]).**
3. **C1 cross-benchmark utility transfer + C3 split-harness (paired) — first generalization bet because a +1.6-vs-best single-split gain [E] is indistinguishable from seed noise (3.5 pp range [E]) until transfer + resplits are measured; nothing else should be preregistered before this.**
4. **A4 frozen dither + tie-break dose-response — first mechanism-targeted codec because it is the minimal intervention on the proven decision variable (top-3 tie structure [E]) with a built-in continuity gate (`a=0` = native EXACT) and a valuable negative result.**
5. **B5(b/c) reliability curves (|q| and margin conditioning) — first predictor bet because a flat curve permanently kills two codec families (A5 query-mask, A3 deadzone) for the price of one analysis, while a sloped curve hands them a frozen, gold-free parameter.**

## Ideas considered and rejected (with reason)

1. **Variance-proportional precision (more bits to high-variance axes) — reject: directly contradicted by TOP-k catastrophic underperformance on both benchmarks [E] and by matched-vs-antimatched monotonicity [E]. Any "importance ∝ variance" rule is pre-killed.**
2. **PCA / whitening / learned rotation before sign — reject now: rotations known-bad (programme premise); block-2 evidence shows even same-rotation regrouping costs pp unless variance-matched [E]; touches three NOES items (PCA/learned rotations, whitening, supervised rotation) for an ex-ante negative expectation [H]. [LIT-CHECK if ever revisited: rotation-for-quantization literature assumes operating regimes our pilots falsify here.]**
3. **Variance (or magnitude) reweighting of Hamming distance at decode — reject as codec: converts the byte-budget Hamming code into a weighted-distance code, breaking budget comparability and touching NOES variance-reweighting [H]; pursue only as B3-analysis, never as an unregistered decode change.**
4. **Float-score reranking of Hamming shortlists — reject within byte-budget programme: defeats the budget (floats cost bytes/compute), touches NOES reranking [H]; the budgeted Hamming-only fallback (A5-3) is the admissible substitute.**
5. **Per-question adaptive subset with no validated predictor (e.g. per-question variance-order or top-|C| mask) — reject: R2A proves per-question variance effects are adaptive and unexplained [E]; no metadata correlates |r|>0.15 [E]; predictor-AUC gate (A5/B5) must pass first.**
6. **Mean-distance / separation optimization as a design objective — reject: separation paradox is established (TOP-48 wins every mean statistic yet loses 10 pp [E]); optimizing means is optimizing the wrong observable [H].**
7. **Single-axis or few-axis "load-bearing bit" search — reject: max drop-loss 0.011, 30/96 ≤ 0 [E]; single-axis retrieval ≈ chance-adjacent 0.006–0.010 [E]; concentration strategies fight Fact 1 [E].**
8. **Pure bottom-tail rule as a universal claim — reject as universal (accept as benchmark-local arm): best-arm location is benchmark-dependent (random≈best LME, bottom-best LoCoMo [E]); preregistering BOT-only would overfit LoCoMo [H]. Spread/stratified is the portable default [M].**
9. **Unfrozen / per-query-tuned dither or thresholds — reject: destroys bit-reproducibility (Fact 6 [E]) and converts gold-free tricks into test-time fitting; only frozen archive-fitted global parameters are admissible [H].**

## Literature-check flags (no network available; check before preregistration)

- Dithered / subtractive-dither quantization and tie-breaking in binary retrieval [LIT-CHECK].
- Ternary / deadzone quantization thresholds from marginals; entropy-constrained bit allocation across coordinates [LIT-CHECK].
- Heterogeneous-precision (mixed-bitwidth) coordinate coding vs dimensionality reduction at fixed bit budgets [LIT-CHECK].
- Participation-ratio / effective-dimension predictors of quantization robustness [LIT-CHECK].

*End of ideation report. All effect sizes above are [SPEC] except numbers cited [E] from the pinned pilot reports; no frozen-matrix recomputation was performed in this session (read-only ideation as instructed).*

