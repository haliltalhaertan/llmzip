[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# QUANT MAP — sign / rotation / quantization cluster (round 2)

Role: literature analyst for the quant cluster. No web access this session, no experiments run here. [PROOF-SKETCH] numbers below are from one small local Python check run this session; everything else numeric is quoted from the coordinator's artifacts. [MEASURED HERE] = coordinator-verified numbers from files on disk (paths cited). [RECALLED-FROM-MEMORY] = my memory of literature, with confidence, UNVERIFIED until the coordinator fetches it. [CONJECTURE] = my hypothesis plus its falsifier. Nothing recalled here is a verified quote; no recalled number, table, or result is asserted.

Files read before writing (so nothing already-scanned is re-reported as new): [MEASURED HERE — established by reading the files]

- `/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/inventory/literature/DO_NOT_RESCAN.md` (11 full + 13 snippet sources; §B genuine gaps; §C hygiene rules).
- `/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/inventory/literature/GAP_TO_100.md` (no stored source supports ~100% Hit@10 at ~12 B/doc).
- `/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/inventory/literature/LIT_ALREADY_COVERED.md` (PPLX-INT8/BIN, Nemotron/Qwen3 references, Anthropic cascade, BPR/RaBitQ/MUVERA/BGE-M3/ConvMemory-v2 cautions, B8/R8 status, LITERATURE_CORRECTION withdrawals).
- `/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/digest_r1/lit/LITERATURE_MAP.md` (round 1 of this job: Husbands, Ando & Lee, ScaNN-anisotropic, leverage identity; Q1–Q5 round-1 verdicts).
- `/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/digest_r1/FINDINGS_DIGEST.md` (system definition, central diagnosis, all arm levels).
- `/mnt/c/Users/MDP/dev/llmzip-work/incoming_20260916b/a_ladder/LADDER_AUDIT.md` (12/24/48 B ladder verified; 192→384 flat-to-harmful on LME/PerLTQA).
- `/mnt/c/Users/MDP/dev/llmzip-work/incoming_20260916b/b_ideas/IDEAS_AUDIT.md` (FIKIR1/KISITLI/IKI/HATA/HIZ verdicts; sign(C/σ)==sign(C) and rotation-lesson duplicates flagged as DO_NOT_REPEAT).
- `/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/digest_r1/lit/VERIFY_QUEUE.md` (round-1 fetch ranks; this map does not duplicate its items except where the quant questions narrow them).

Coordinator-verified givens used as premises, not re-derived: [MEASURED HERE — stated in the task brief as coordinator-verified]

- ITQ home setting is dense image descriptors with Euclidean-neighbour ground truth; ITQ = Gong & Lazebnik, "Iterative Quantization: A Procrustean Approach to Learning Binary Codes for Large-scale IMAGE Retrieval"; all-but-the-top = Mu, Bhat, Viswanath arXiv:1702.01417 (word vectors); RRF = Cormack, Clarke, Buettcher SIGIR 2009; Husbands et al. 2005 exists.
- Our six facts F1–F6 with the numbers quoted in the brief (anchors reproduce to 0.0000 pp).

System reminder (one line, from FINDINGS_DIGEST.md): [MEASURED HERE] per archive Z = [LSA32(word) | word-tfidf | char-tfidf] → TruncatedSVD(96) → row-normalize → center → sign → 96 bits; archives are small (RealTalk 410–1548 docs per the brief; PerLTQA median 408, max 546).

Tag convention: every claim-bearing bullet/paragraph below ends with its tag(s). Headings and pure pointers carry no claim.

---

## PER-FACT VERDICTS

### F1. ITQ does NOT beat random rotation (RealTalk ITQ−random = −2.27 pp; PerLTQA −0.13 pp) — verdict: OPEN as a measured regime; mechanism classes PARTIALLY KNOWN

- The numbers are ours: RealTalk Hit@10 qscale FULL 49.65, ITQ 32.77, random 35.04 (3 seeds 34.61–35.32); PerLTQA FULL 80.00, ITQ 78.91, random 79.04. [MEASURED HERE — task brief + `digest_r1/FINDINGS_DIGEST.md` "Quantization layer" section]
- That ITQ normally helps in its home setting (dense image descriptors, Euclidean-neighbour ground truth) is taken as coordinator-verified premise, not my finding. [MEASURED HERE — brief premise]
- I recall the ITQ paper reporting gains over baselines including randomized/non-optimized rotations on its own dense-descriptor datasets, but I cannot confirm the baseline set, datasets, or numbers from disk, so this stays a weak scope contrast, not evidence about our regime. [RECALLED-FROM-MEMORY, low-to-medium confidence, UNVERIFIED]
- I recall NO prior work reporting "learned rotation ≤ random rotation on TF-IDF/LSI-derived sign codes," and NO prior work testing ITQ on sparse/axis-aligned text features or per-archive small-n SVD codes at all. [RECALLED-FROM-MEMORY, medium confidence that I know of no such report (a negative claim — inherently weaker than a positive recall), UNVERIFIED until the FETCH_QUEUE searches confirm a null]
- The closest recalled *principle* (not instance) is score-aware/anisotropic quantization beating reconstruction-optimal quantization at equal bitrate on retrieval metrics, already identified in round 1 (`LITERATURE_MAP.md` S3) — it predicts the *direction* "reconstruction objective can mistarget retrieval" but tested neither ITQ, nor sign codes, nor TF-IDF/SVD inputs, so it does not cover our −2.27 pp number. [RECALLED-FROM-MEMORY, medium confidence on the core idea / low on details, UNVERIFIED]
- Small-sample-overfitting sub-question: a 96×96 rotation has 96·95/2 = 4560 free parameters; at n = 400/700/1000/1500 docs the ratios are n/k ≈ 4.2/7.3/10.4/15.6 and n/DOF ≈ 0.09/0.15/0.22/0.33 (checked this session on synthetic shapes, real arithmetic, not our data). [PROOF-SKETCH — counting + this-session Python sanity check]
- The scalar-count caveat cuts AGAINST a naive overfitting story: ITQ fits R from the full n×k centered matrix (n·k scalars: 38,400 even at n = 400) against 4560 rotation parameters, so the fit is over-constrained in raw scalar count; overfitting would also predict *worse* damage on *smaller* archives, while F2 measures the opposite (damage grows with n). [PROOF-SKETCH for the counts; MEASURED HERE for the F2 direction; CONJECTURE for the inference — falsified if per-archive ITQ training loss shows small-n archives stuck at worse quantization error yet better retrieval, i.e. the two objectives diverging in the predicted direction]
- Net verdict: the *instance* (ITQ ≤ random on LSI/TF-IDF sign codes, −2.27 pp RealTalk / −0.13 PerLTQA) is OPEN and, if the fetch queue returns a documented null, is OUR contribution; the *explanation classes* (objective mismatch; variance-imbalance sensitivity) are PARTIALLY KNOWN by analogy only. [CONJECTURE on verdict stability — falsified by any fetched source showing this exact regime]

### F2. Rotation damage tracks archive size (RealTalk per-archive Pearson r(n_docs, damage) = −0.78; n<700: −6.56 pp avg; n≥1000: −23.13 pp avg; PerLTQA's small archives alone explain the cross-benchmark gap) — verdict: OPEN; our most interesting unexplained regularity

- All numbers in the heading are quoted from the brief as coordinator-verified; PerLTQA median 408 / max 546 likewise. [MEASURED HERE — task brief]
- I recall NO paper predicting or reporting "rotation damage grows with n at fixed k" for sign codes, and NO recalled n/k threshold effect of this shape. [RECALLED-FROM-MEMORY, medium confidence as a negative claim, UNVERIFIED until the targeted searches in FETCH_QUEUE are run]
- The naive overfitting story predicts the WRONG sign here (see F1 counting point above): fewer docs should mean worse-fitted rotation, but small archives are the ones that survive rotation best. [PROOF-SKETCH for the directional argument; CONJECTURE as an explanation-killer — falsified if small-n archives turn out to have much worse ITQ training quantization error (i.e. the optimizer genuinely fails there) while still retrieving better]
- Two live candidate mechanisms, separated by what they predict (see Q2 for the discriminator): (a) spectral-concentration: larger archives concentrate energy in fewer dominant directions, so a variance-equalizing rotation wastes more capacity smearing a few good axes across 96 — predicts damage correlates with top-singular-mass share / spectral Gini even controlling for n; (b) hubness / distance-concentration: larger n at fixed k intensifies hub formation and pairwise-distance tightening, and rotation (which densifies the code) interacts with the resulting tie/collision structure — predicts damage correlates with hubness skew (N_10 occurrence distribution) even controlling for n. [CONJECTURE — each falsified by a near-zero partial correlation with damage after conditioning on n, computed on stored per-archive matrices]
- I recall hubness growing with n and dimensionality (Radovanovic-style results) and distance-concentration phenomena (Beyer-style results) as real literatures, but I recall NOTHING connecting either to learned-rotation damage on sign codes. [RECALLED-FROM-MEMORY, medium confidence on existence of those literatures / low on any rotation connection, UNVERIFIED]
- Confound warning I cannot resolve from memory: n may proxy for archive *content* (large RealTalk archives may be the chattiest/multi-topic ones), so "damage grows with n" may be composition, not cardinality — the brief's "alone explains the cross-benchmark difference" is a between-benchmark accounting claim, not proof of a within-mechanism n-cause. [CONJECTURE — falsified if size-matched RealTalk/PerLTQA archives show systematically different damage, or if subsampling large archives to n≈400 leaves damage unchanged; see Q2 cheapest test]
- Net verdict: OPEN. If the fetch queue confirms the null, F2 is OUR contribution (a new empirical regularity with two stated, discriminable candidate mechanisms).

### F3. Rotation makes bits MORE balanced and retrieval WORSE (production per-bit 1s-fraction range 0.309–0.658, mean 0.492; rotated 0.459–0.545, mean 0.499) — verdict: OPEN; state explicitly as a genuine contribution unless the balance-critique fetch finds otherwise

- The bit-balance numbers and the retrieval drops they accompany are ours. [MEASURED HERE — task brief + `digest_r1/FINDINGS_DIGEST.md` "Bit balance" lines]
- That balanced/variance-equalized bits are an explicit design goal in spectral hashing and ITQ is my recall of their textbook motivation (maximum-entropy / equal-variance arguments), already noted in round 1; I assert no equation, number, or quote from those papers. [RECALLED-FROM-MEMORY, medium confidence on the goal-level claim, UNVERIFIED]
- I recall NO paper reporting bit-balance *anti-correlating* with gold retrieval at fixed bit count — no "balanced-but-worse" result, no critique of balance as a proxy on text/SVD sign codes, and no isotropy-balance-hurts-retrieval theorem. [RECALLED-FROM-MEMORY, medium confidence as a negative claim, UNVERIFIED until FETCH_QUEUE item on Spectral Hashing + balance-critique search is run]
- The one adjacent recalled debate (follow-ups questioning whether isotropy explains all-but-the-top gains) is about a different operation (removing top PCs from word vectors) and, as I recall it, questions a *sufficient* explanation rather than reporting balance hurting retrieval — weak analogy at best. [RECALLED-FROM-MEMORY, low confidence, UNVERIFIED]
- Therefore, as the brief instructs to state explicitly: **F3 is a genuine contribution on current evidence — the first measured case we know of where a rotation improves textbook bit-balance while significantly harming gold retrieval at fixed 12 B.** [CONJECTURE on novelty — falsified by any fetched source showing balanced-worse on sign codes with gold retrieval metrics]
- Mechanism gloss (ours, not literature): an unbalanced axis that fires on a document minority carries discriminative mass, and rotation smears it across all 96 axes — consistent with F3 and with the brief's F6 collision-structure point, but untested against the Q2 spectral/hubness alternatives. [CONJECTURE — falsified if within-channel rotation (which preserves channel identity) hurts as much as full rotation; see Q5 lever (iv)]

### F4. sign(C_ij/σ_j) == sign(C_ij) exactly (0/63,552 doc bits, 0/8,160 query bits changed) — verdict: KNOWN (trivial mathematics); the pipeline implication is OUR framing

- For σ_j > 0, dividing by σ_j cannot change a sign; the 0-changed-bits check is therefore a code-correctness confirmation, not an empirical discovery, and needs no literature citation. [PROOF-SKETCH — one-line algebra, plus this-session synthetic recheck (0 of 40 changed) as implementation sanity, not as evidence about our data]
- The measured zero counts on real data are ours. [MEASURED HERE — task brief + `digest_r1/FINDINGS_DIGEST.md` verified-identity lines; duplicates flagged in `b_ideas/IDEAS_AUDIT.md` "Duplicates" section]
- The implication drawn ("only rotation or a shifted threshold can move a bit") holds for the stated pipeline (fixed zero threshold, pre-rotation rescaling) and is OUR framing; note the boundary I state precisely so Q5 is not misread: per-axis rescaling *after* a rotation, or per-axis threshold shifts, CAN move bits — F4 rules out neither. [PROOF-SKETCH for the implication given the pipeline; CONJECTURE-free]
- No fetch is justified for F4. [CONJECTURE-free procedural judgment]

### F5. Arbitrary quantile thresholds hurt badly (PerLTQA zero 0.76 vs q0.1 0.31); median roughly neutral (−0.43 RealTalk, −0.53 PerLTQA) — verdict: PARTIALLY KNOWN practice / OPEN magnitude; minor contribution

- The numbers are ours. [MEASURED HERE — task brief + `digest_r1/FINDINGS_DIGEST.md` "KNOWN NEGATIVE RESULTS"]
- That zero-after-centering is the standard binarization for PCA/SVD-derived codes (and median as the robust variant) is recalled practice, consistent with the direction of our measurement but cited here only as background, not as a covering result. [RECALLED-FROM-MEMORY, medium confidence on practice / low on any specific paper, UNVERIFIED]
- I recall NO systematic report of a quantile-threshold sweep on LSI/TF-IDF sign codes with gold Hit@10 showing a collapse of this size (0.76→0.31), so the *magnitude* and the *median-neutrality at 12 B on two benchmarks* are OUR measurements. [RECALLED-FROM-MEMORY, medium-low confidence as a negative claim, UNVERIFIED]
- F5 does NOT rule out learned *per-dimension* thresholds (it tested global quantile/median rules) — reserved for Q5. [PROOF-SKETCH of scope: a global rule is a 1-DOF restriction of a 96-DOF threshold vector]
- Contribution weight: small (confirms standard practice with unusual severity); do not headline. [CONJECTURE-free judgment]

### F6. PRESERVATION DOES NOT IMPLY RETRIEVAL (Hadamard pair: identical per-feature preservation 96/512 = 0.1875 and identical total error 416, but Hit@1 25% vs 100%; difference = collision structure, group size 4 vs 1) — verdict: principle PARTIALLY KNOWN (score-aware precedent); exact-shape counterexample OPEN

- The pair and all its numbers are the external reviewer's construction, taken as given; I did not rebuild it and assert nothing about it beyond the brief's description. [MEASURED HERE — task brief premise; construction itself is reviewer-provided, not my derivation]
- The *principle* "reconstruction-optimal ≠ retrieval-optimal" is the closest thing to KNOWN in this cluster, via the score-aware/anisotropic quantization precedent already identified in round 1 (`LITERATURE_MAP.md` S3/Q1) — but that precedent, as I recall it, compares *different losses at equal bitrate on retrieval metrics*, and I recall NO equal-reconstruction-error / wildly-different-retrieval constructed pair of this exact shape (identical preservation, identical total error, 4× Hit@1 gap via collision structure alone). [RECALLED-FROM-MEMORY, medium confidence on the principle / medium-low on the exact-shape null, UNVERIFIED until FETCH_QUEUE pins the ScaNN comparison and runs the equal-error-counterexample search]
- Adjacent recalled families (PQ/OPQ/RaBitQ reporting both reconstruction/estimator error and ANN recall; MUVERA Chamfer-vs-gold distinctions in `LIT_ALREADY_COVERED.md` A4) keep *fidelity* and *gold* metrics separate as a matter of practice, which is consistent with F6 but is not a counterexample of F6's shape. [RECALLED-FROM-MEMORY, low-medium confidence, UNVERIFIED; MUVERA/Chamfer-vs-gold separation itself is MEASURED HERE as a coverage statement in `GAP_TO_100.md`/`LIT_ALREADY_COVERED.md`]
- The collision-structure moral (group size 4 vs 1 invisible to any reconstruction metric) is, on current evidence, OUR (reviewer-supplied) contribution: it converts a folklore warning into a checkable artifact shape the coordinator can reuse (any proposed metric that scores the two matrices equally is disqualified as a retrieval proxy). [CONJECTURE on novelty — falsified by any fetched source giving an equal-error/different-retrieval pair]
- Right-citation answer today: ScaNN-anisotropic remains the closest *principle* citation (to be verified, not quoted); for the *exact shape* there is currently no citation — cite the reviewer's pair as an internal artifact, not literature. [CONJECTURE-free citation hygiene judgment]

---

## QUESTION-BY-QUESTION ANALYSIS

### Q1. Does any prior work report learned rotation failing to beat random, or rotation harming? (sparse/axis-aligned inputs; TF-IDF/LSI features; small n/k; retrieval-vs-reconstruction mismatch)

- Home-setting contrast is premise: ITQ's verified home is dense image descriptors with Euclidean-neighbour ground truth — a far cry from per-archive TF-IDF/SVD sign codes scored by gold Hit@10. [MEASURED HERE — brief premise]
- Sparse / axis-aligned inputs: I recall hashing-literature discussion that PCA axes on skewed heavy-tailed data should not be blindly mixed and that variance-equalizing rotations spend capacity on low-signal directions, but I cannot name a paper that *shows* rotation hurting on TF-IDF/SVD sign codes — this candidate stays OUR conjecture. [RECALLED-FROM-MEMORY, low confidence, UNVERIFIED; CONJECTURE — falsified by a fetched source showing rotation helping on sparse text codes, or by a within-channel-rotation ablation hurting as much as full rotation]
- TF-IDF/LSI-derived features: I recall NO ITQ-family evaluation on LSI/TF-IDF sign codes at all (recalled evals are GIST/SIFT/CIFAR-style dense descriptors — UNVERIFIED details). [RECALLED-FROM-MEMORY, low-medium confidence, UNVERIFIED]
- Small n/k + Procrustes overfitting: the counting argument above ([PROOF-SKETCH]: 4560 rotation DOF vs n·k scalars) does not establish an overfitting regime at n = 400–1500, and F2's direction (large-n worse) points away from overfitting as the driver; I recall NO known "ITQ overfits below n/k = X" threshold. [PROOF-SKETCH + MEASURED HERE direction; RECALLED-FROM-MEMORY negative claim, low-medium confidence, UNVERIFIED]
- Retrieval-vs-reconstruction mismatch: the only recalled precedent with real weight is score-aware/anisotropic quantization (round-1 S3), which I keep as *analogy*, explicitly not as coverage of our number. [RECALLED-FROM-MEMORY, medium/low as in F1, UNVERIFIED]
- Bottom line for Q1: no recalled source reports the failure regime; four sub-candidates assessed above with the overfitting one currently disfavored on directional grounds; F1 stays OPEN pending FETCH_QUEUE items 1, 5, 6, 7.

### Q2. Best explanation for damage-growing-with-n, with recall separated from conjecture; cheapest discriminating measurement

- Recalled candidates: (i) I recall NO n/k threshold effect for rotation damage. [RECALLED-FROM-MEMORY, medium-low confidence, UNVERIFIED] (ii) I recall hubness and distance-concentration as literatures where effects intensify with n at fixed dimensionality, but recall NO link from either to rotation damage on sign codes. [RECALLED-FROM-MEMORY, medium confidence on the literatures / low on the link, UNVERIFIED]
- Conjectured candidates: (a) spectral-concentration (large archives = peakier spectra = more to lose from variance-equalizing smear); (b) hubness/collision interaction (large n = worse hubs/ties, rotation densifies codes into the bad regime); (c) content-confound (n proxies multi-topic/chattiness, not cardinality). [All three CONJECTURE — falsifiers stated in F2]
- Cheapest discriminating measurement (no refits, uses stored per-archive matrices only — the coordinator can run it): for each RealTalk archive compute, from the ALREADY-STORED centered matrix C (or its singular values) and the production codes: (1) spectral stat = top-10 singular-mass share (or Gini of σ_j); (2) hubness stat = skewness (or max) of the 10-occurrence distribution under production-code Hamming distance; (3) concentration stat = mean/std of pairwise Hamming distances; then report the *partial* correlations of each stat with measured rotation damage (FULL−rotated Hit@10) *conditioning on n_docs*. [CONJECTURE as a proposal — its cost claim (no refits) is falsified if the required per-archive matrices/scales are not on disk]
- Decision rule for that test: if (1) survives conditioning on n and (2)/(3) vanish → spectral-smear leads; if (2) survives and (1) vanishes → hubness/collision leads; if all vanish given n → cardinality itself (or an unmeasured content confound) leads, and the confirmatory step is a size-matched subsample refit (large archives down to n≈400, refit SVD+ITQ+random, compare damage). [CONJECTURE — the subsample step is the more expensive confirmatory experiment, not the cheap discriminator]
- Why this ordering: the partial-correlation step reuses artifacts; the subsample step needs refits on ~5 large archives × conditions. [CONJECTURE-free cost judgment]

### Q3. Is bit balance anywhere reported to be a BAD proxy for retrieval quality?

- Short answer as instructed: on current (unfetched) evidence, NO — I recall balance/maximum-entropy as a design *goal* (spectral hashing, ITQ) and recall no report of balance anti-correlating with gold retrieval, so F3 should be stated as a genuine contribution pending the balance-critique fetch. [RECALLED-FROM-MEMORY, medium confidence, UNVERIFIED; explicit contribution claim per the brief]
- The fetch that could overturn this is narrow: Spectral Hashing primary (verify balance is indeed ITQ's inherited goal) + a forward/backward citation search for any "balance hurts / variance-equalization harms retrieval" report. [CONJECTURE-free search prescription; FETCH_QUEUE item 2]

### Q4. How close is score-aware/anisotropic quantization really? Is there an equal-error/different-retrieval counterexample already?

- Closeness verdict: closest *principle*, distant *shape*. [CONJECTURE on closeness — falsified if the ScaNN fetch shows it tested sign codes, TF-IDF/SVD inputs, or an equal-error pair]
- What I recall ScaNN showing (UNVERIFIED in every detail): an anisotropic (inner-product-aware, asymmetric) quantization loss that penalizes score-direction error more than orthogonal error and beats reconstruction-optimal quantization at equal bitrate on retrieval metrics — i.e. the *inequality* "better reconstruction ⇏ better retrieval" as a measured gap, not the *equality* "identical reconstruction + 4× retrieval gap" of F6. [RECALLED-FROM-MEMORY, medium confidence on idea / low on details, UNVERIFIED]
- I recall NO prior counterexample of F6's exact shape (equal per-feature preservation + equal total error + Hit@1 25% vs 100% via collision structure). [RECALLED-FROM-MEMORY, medium-low confidence as a negative claim, UNVERIFIED]
- Right citation today: for the principle, the ScaNN-anisotropic line (fetch to verify loss, comparison, dense-only scope — FETCH_QUEUE item 3); for the exact shape, no citation — reference the reviewer's Hadamard pair as an internal artifact and file F6's shape as OUR contribution until a fetch produces otherwise. [CONJECTURE-free hygiene judgment]
- Boundary with already-scanned sources: BPR (learned binary codes, 96 B, rescore) and Extended RaBitQ / MUVERA (ANN/Chamfer-vs-gold separations) are about *code families and metric hygiene*, not about equal-error counterexamples — they do not cover F6 and are not re-reported here beyond this boundary line. [MEASURED HERE — coverage established in `LIT_ALREADY_COVERED.md` A4 + `GAP_TO_100.md`]

### Q5. Given F4, is there a THIRD lever on sign codes at fixed bit count? (Both rotation and global threshold fail for us.)

- Scope lock first: F4 closes only *pre-rotation per-axis rescaling at zero threshold*; F5 closes only *global* quantile/median thresholds — everything below is outside both closures. [PROOF-SKETCH of scope]
- Candidate levers (each with ruled-out status against F4/F5 on current evidence): [CONJECTURE on promise; MEASURED HERE where prior packages tested the neighbor]
  1. Learned *per-dimension* thresholds t ∈ R^96, bit = sign(C_j − t_j): NOT ruled out (F5 tested 1-DOF global rules, not 96-DOF vectors). [PROOF-SKETCH of non-coverage]
  2. Post-rotation scaling/thresholding (rotate, then scale/shift, then sign): NOT ruled out (F4 is a pre-rotation identity; after R the axes are mixed and σ no longer factors out). [PROOF-SKETCH]
  3. Structured / block-diagonal rotation (within-channel only: LSA|word|char blocks): NOT tried, NOT ruled out; doubles as the direct test of the smearing hypothesis behind F3. [CONJECTURE — falsified as an explanation if it hurts as much as full rotation]
  4. Fixed-budget bit reallocation (2 bits on high-value dims, drop low-value dims, still 96 bits total): NOT ruled out at 12 B — B8 (80×1+8×2) has no qrels run (FLOAT-agreement only) per `LIT_ALREADY_COVERED.md` B2 [MEASURED HERE as coverage]; IKI Idea A 96×2-vs-192×1 is a 24 B result in a different budget per `b_ideas/IDEAS_AUDIT.md` Package 3 [MEASURED HERE]; the Bloom-split failure decomposes mostly to fusion design, not to allocation per se, per `FINDINGS_DIGEST.md` [MEASURED HERE].
  5. Asymmetric query-side treatment beyond qscale (continuous query × binary docs; rescore over l = 1000): NOT a new lever — qscale is already production [MEASURED HERE]; the unexhausted extension is BPR-style rescore with latency accounting, already queued as a local experiment in `GAP_TO_100.md` row 5, expectation single-digit ordering gains only. [MEASURED HERE as program status; CONJECTURE on gain size]
  6. Different code family at fixed bytes (PQ/OPQ/RaBitQ-style multi-bit quantizers): NOT ruled out, but changes the system class and cost model (codebooks/rotations/centroids/IVF charged on top per `LIT_ALREADY_COVERED.md` A4 [MEASURED HERE as coverage]) — a frontier control, not a sign-code lever.
- What F4/F5 jointly license: stop sweeping global rotations and global thresholds (both measured, both fail — file under DO_NOT_REPEAT with HATA §7 and KONTROL_EKI §§6–7 per `b_ideas/IDEAS_AUDIT.md` duplicates note [MEASURED HERE]); any revival must be per-dimension, post-rotation, structured, or asymmetric-rescore, each with the symmetric-competitor controls from FIKIR1's 15-cell harness. [CONJECTURE-free recommendation]

---

## OUR CONTRIBUTIONS (explicit list — nothing above covers these on current evidence)

1. F1 instance: ITQ ≤ random rotation on LSI/TF-IDF sign codes (−2.27 pp RealTalk, −0.13 PerLTQA), with ANY rotation doing the damage. [MEASURED HERE; novelty CONJECTURE pending FETCH_QUEUE 1/5/6/7 null]
2. F2 regularity: rotation damage grows with archive size (r = −0.78; −6.56 vs −23.13 pp; PerLTQA gap explained by size alone), with two discriminable candidate mechanisms and a stated cheap test. [MEASURED HERE; novelty CONJECTURE pending FETCH_QUEUE 4/5 null]
3. F3 balance paradox: rotation improves textbook bit-balance while harming gold retrieval — state as genuine contribution. [MEASURED HERE; novelty CONJECTURE pending FETCH_QUEUE 2 null]
4. F6 shape: equal-preservation / equal-error pair with 25% vs 100% Hit@1 via collision structure alone (reviewer-constructed artifact; principle-adjacent to ScaNN but shape-uncovered). [MEASURED HERE as artifact premise; novelty CONJECTURE pending FETCH_QUEUE 3 null]
5. F4/F5 scope closure: only rotation/shift move bits (identity), global thresholds fail with measured severity — small methodological closures licensing the Q5 shortlist. [MEASURED HERE + PROOF-SKETCH]
6. Honest-cost note the coordinator already holds but belongs to this cluster: a 96×96 rotation costs 3.43× (RealTalk) / 7.50× (PerLTQA) the document payload it fails to improve. [MEASURED HERE — brief premise]

## WHAT WOULD CHANGE THESE VERDICTS

- ITQ fetch showing a sparse/text ablation where rotation hurts → F1 moves PARTIALLY KNOWN; showing dense-only ANN scope with no negative regime → F1 firms up as OPEN/novel. [CONJECTURE-free conditional]
- Hubness/concentration fetch + the cheap partial-correlation test → F2 splits toward (a)/(b)/(c) or stays OPEN with higher confidence. [CONJECTURE-free conditional]
- Spectral-Hashing + balance-critique search returning a balanced-worse report → F3 moves PARTIALLY KNOWN; documented null → F3 firms as OUR contribution. [CONJECTURE-free conditional]
- ScaNN fetch returning an equal-error counterexample → F6 moves KNOWN-shape; returning only the unequal-loss gap → F6 shape stays OURS with ScaNN as principle citation. [CONJECTURE-free conditional]
- Per-dimension-threshold / allocation search returning a sign-code result at fixed bits → Q5 shortlist shrinks; null → shortlist stands as the next experiments (with FIKIR1-style symmetric controls). [CONJECTURE-free conditional]

## HONESTY APPENDIX

- No web access this session; no paper was fetched, quoted, or numerically cited from memory — every literature sentence above carries RECALLED-FROM-MEMORY + confidence + UNVERIFIED. [CONJECTURE-free session fact]
- No experiments run; the only computation was a shapes-level Python sanity check (sign-invariance on synthetic data; 4560-DOF rotation counting) — not evidence about our data. [PROOF-SKETCH, session fact]
- Nothing in `DO_NOT_RESCAN.md`, `GAP_TO_100.md`, `LIT_ALREADY_COVERED.md`, round-1 `LITERATURE_MAP.md`, or the LADDER/IDEAS audits is re-reported as a new finding; boundaries with BPR/RaBitQ/MUVERA/BGE-M3/PPLX/Anthropic are drawn from the inventory's own cautions. [MEASURED HERE — coverage comparison]
- Round-1 attributions reused as premises (ITQ = Gong & Lazebnik image-retrieval; ABTT = Mu et al. word vectors; RRF = Cormack et al. SIGIR 2009; Husbands et al. 2005 exists) are the coordinator's verified facts, not my derivations. [MEASURED HERE — brief premise]
