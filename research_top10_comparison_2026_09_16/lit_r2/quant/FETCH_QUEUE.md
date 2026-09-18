[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# FETCH QUEUE — quant cluster (ranked; coordinator has web access, I do not)

Every item below is a fetch-or-search prescription, not a citation. Anything I "recall" about the target is tagged [RECALLED-FROM-MEMORY] with confidence and is UNVERIFIED — do not quote it; verify bibliographic details AND content from the primary source before any citation or any kill/promote decision. Nothing here re-fetches anything in `inventory/literature/DO_NOT_RESCAN.md` (PPLX, Nemotron, Qwen3, Anthropic contextual retrieval, BPR, Extended RaBitQ, MUVERA, MuSiQue panel, BGE-M3, ConvMemory v2, hashing/KV snippets) or re-derives the coordinator-verified round-1 attributions (ITQ = Gong & Lazebnik image retrieval; ABTT = Mu et al. arXiv:1702.01417; RRF = Cormack et al. SIGIR 2009; Husbands et al. 2005 exists).

## Rank 1 — ITQ original paper (objective, eval scope, any negative regime) → settles Q1/F1

- Target: the ITQ paper (Gong & Lazebnik as verified). [MEASURED HERE — brief premise for the attribution; everything about content below is RECALLED-FROM-MEMORY, low-medium confidence, UNVERIFIED]
- Search terms: `Iterative Quantization Procrustean binary codes`, `Gong Lazebnik iterative quantization full text`, `ITQ binary codes GIST CIFAR evaluation`, `ITQ "quantization error" objective Procrustes`.
- Verify and record: (a) exact objective (recalled: min over binary B and rotation R of ||B − VR||_F — UNVERIFIED); (b) eval datasets and ground truth (recalled: dense visual descriptors, Euclidean-neighbour ANN — per brief premise, confirm which collections); (c) whether ANY ablation touches sparse/text/TF-IDF/SVD inputs, small-n fits, or a regime where learned rotation ties or loses to random rotation.
- Settles: whether F1's regime (ITQ ≤ random on LSI/TF-IDF sign codes, −2.27 pp RealTalk) is outside ITQ's tested scope (→ F1 stays OPEN/ours) or an already-reported failure (→ F1 moves PARTIALLY KNOWN).
- Stop rule: record the objective equation number, the dataset/metric table, and one line "negative regime reported / not found (pages searched)".

## Rank 2 — Spectral Hashing + balance-critique search (is balance ITQ's inherited goal? has balanced-worse ever been reported?) → settles Q3/F3

- Targets: (a) Spectral Hashing primary (recalled: Weiss et al. — UNVERIFIED [RECALLED-FROM-MEMORY, medium confidence on existence, low on details]); (b) forward/backward search for any critique. [RECALLED-FROM-MEMORY throughout, UNVERIFIED]
- Search terms: `spectral hashing balanced bits maximum entropy`, `Weiss Torralba Fergus spectral hashing`, `binary hashing "balanced bits" retrieval harm`, `variance equalization hashing hurts retrieval`, `bit balance anti-correlates retrieval`, `isotropy balance binary codes retrieval ablation`.
- Verify and record: (a) whether balance/variance-equalization is stated as a design goal the ITQ line inherits; (b) whether ANY source reports balance improving while gold retrieval degrades at fixed bit count (any code family, any gold metric).
- Settles: F3's status as genuine contribution (null → OURS stands, state it) vs PARTIALLY KNOWN (a balanced-worse report → downgrade and cite it).
- Stop rule: one line per source audited: "states balance as goal Y/N; reports balanced-worse Y/N (metric, K, code size)".

## Rank 3 — ScaNN anisotropic quantization (exact loss, comparison, scope; any equal-error pair?) → settles Q4/F6 and Q1-objective-mismatch

- Target: the ScaNN anisotropic-quantization paper (recalled: Guo et al., ICML 2020 — UNVERIFIED [RECALLED-FROM-MEMORY, medium confidence on idea, low on details]). Note: already identified as closest precedent in round-1 `LITERATURE_MAP.md` S3 — this fetch pins it, it does not discover it.
- Search terms: `ScaNN anisotropic quantization score-aware loss`, `Guo anisotropic vector quantization inner product`, `anisotropic quantization parallel orthogonal residual retrieval`.
- Verify and record: (a) exact anisotropic loss form and anisotropy constant; (b) the reconstruction-vs-retrieval comparison (datasets, bitrates, metrics — recalled: beats reconstruction-optimal at equal bitrate on retrieval — UNVERIFIED); (c) scope (recalled: dense embeddings only — UNVERIFIED); (d) whether ANY figure/table gives an equal-reconstruction-error / different-retrieval pair (the F6 shape: identical preservation + identical total error, divergent Hit@K via collision structure).
- Settles: the principle citation for F6/Q1 (if (b) confirms) AND whether F6's exact shape is covered (if (d) exists → F6 moves KNOWN-shape; if absent → F6 shape stays OURS with ScaNN cited for the principle only).
- Stop rule: quote the loss, the head-to-head table location, and "equal-error counterexample found / not found".

## Rank 4 — Hubness + distance-concentration primaries (do the Q2 candidate mechanisms exist as stated? any rotation link?) → settles Q2/F2 mechanism shortlist

- Targets: hubness line (recalled: Radovanovic et al. — UNVERIFIED) and concentration line (recalled: Beyer et al. — UNVERIFIED). [RECALLED-FROM-MEMORY, medium confidence the literatures exist, low on details, UNVERIFIED]
- Search terms: `hubness high dimensional nearest neighbor Radovanovic`, `hub occurrence skewness dataset size`, `distance concentration nearest neighbor meaningfulness Beyer`, `hubness text retrieval TF-IDF`, `hubness binary codes Hamming`.
- Verify and record: (a) whether hubness/concentration intensify with n at fixed dimensionality (the directional premise Q2 needs); (b) whether ANY source connects either to learned-rotation or sign-code damage.
- Settles: whether Q2 candidates (a)/(b) in `QUANT_MAP.md` have real foundations ((a) yes + (b) no → both stay CONJECTURE with recalled-literature backing for the premise only) or are already-linked (→ F2 moves PARTIALLY KNOWN).
- Stop rule: record the claimed n-dependence with its stated conditions; record "rotation link found / not found".

## Rank 5 — Small-sample rotation / Procrustes estimation regime (is n/k ≈ 4–16 with k = 96 a known unstable zone?) → settles Q1-overfitting and Q2-n-direction

- Target: no recalled candidate — this is a SEARCH, not a fetch. (If it returns empty under a recorded strategy, that null itself raises confidence that F1/F2 are novel.)
- Search terms: `orthogonal Procrustes sample complexity small sample`, `ITQ overfitting small dataset rotation estimation`, `high dimensional rotation estimation n/k threshold`, `covariance estimation binary hashing small sample`, `Procrustes analysis stability number of samples dimensions`.
- Verify and record: any stated threshold, rate, or empirical curve for rotation/orthogonal-matrix estimation quality vs n at fixed k; note the parameter reality from this session ([PROOF-SKETCH]: 4560 rotation DOF; n·k scalars 38k–144k across our n range — over-constrained in raw count, so a naive overfit story is already disfavored alongside F2's wrong-sign direction [MEASURED HERE for the direction]).
- Settles: whether the "ITQ fits 96×96 from 400–1500 docs" fact has a known overfitting reading (→ Q1 gains a mechanism) or the counting + directional evidence stands unopposed (→ overfitting stays disfavored, F2 stays OPEN).
- Stop rule: record search strategy + "threshold found (state it) / documented null".

## Rank 6 — Sparse / axis-aligned sensitivity to rotation (does mixing interpretable coordinates have a known cost?) → settles Q1-sparse

- Target: no single recalled candidate — SEARCH (candidates to test inside it: sparse-PCA rotation sensitivity; "don't mix heavy-tailed PCA axes" folklore; LSI-vs-rotation discussions). [RECALLED-FROM-MEMORY, low confidence, UNVERIFIED]
- Search terms: `sparse PCA rotation interpretability`, `PCA axes heavy-tailed rotation hashing`, `TF-IDF SVD binary hashing rotation`, `LSI binary codes sign quantization`, `axis-aligned features rotation harm retrieval`.
- Verify and record: any result where rotation/mixing of sparse or individually-meaningful coordinates hurts a downstream task, ideally retrieval with sign codes.
- Settles: Q1 candidate (a) — found → F1 mechanism PARTIALLY KNOWN; null → stays OUR conjecture (with the within-channel-rotation ablation in Q5 as the local test).
- Stop rule: "sparse-rotation-harm report found (cite) / documented null".

## Rank 7 — LSI/TF-IDF × sign-code intersection (has anyone signed an SVD of TF-IDF before?) → settles F1 scope novelty directly

- Target: SEARCH at the intersection our pipeline occupies.
- Search terms: `"LSI" binary codes retrieval`, `SVD sign quantization document retrieval`, `TF-IDF hashing binary codes gold retrieval`, `latent semantic indexing Hamming retrieval`, `truncated SVD sign bits passage retrieval`.
- Verify and record: any paper that builds sign/1-bit codes on top of TF-IDF/SVD features and evaluates gold (not ANN-agreement) retrieval — plus its rotation/threshold choices.
- Settles: whether our entire quant regime has direct prior art (→ F1/F3/F5 re-scoped as instances) or is unstudied (→ regime novelty firms up; consistent with `GAP_TO_100.md`'s "no tiny-code gold Hit@10" bounded finding [MEASURED HERE as coverage]).
- Stop rule: "direct prior art found (cite with K, metric, bits) / documented null".

## Rank 8 — Per-dimension thresholds / fixed-budget bit allocation / asymmetric sign-code scoring (third-lever novelty check) → settles Q5

- Targets: SEARCH across three sub-families (no single recalled primary; BPR-style asymmetric rescore and PQ-ADC are already-covered background per `LIT_ALREADY_COVERED.md` — do not re-fetch them for this).
- Search terms: `learned thresholds binary hashing per dimension`, `adaptive threshold spectral hashing ITQ`, `mixed precision binary codes bit allocation retrieval`, `asymmetric binary hashing float query rescore`, `two-bit per dimension vs more dimensions retrieval`.
- Verify and record, per sub-family: (a) per-dim learned thresholds on sign codes at fixed bit count (F5 tested only global rules [MEASURED HERE]); (b) variable-bits-per-dimension at fixed total (B8 has no qrels; IKI-A 96×2 is 24 B — both [MEASURED HERE] from the audits); (c) asymmetric extensions beyond our production qscale (already production [MEASURED HERE]; BPR-style l = 1000 rescore unexhausted per `GAP_TO_100.md` row 5).
- Settles: which Q5 levers are genuinely untried (null → shortlist stands) vs already-reported (→ shrink the shortlist before spending runs; every revival uses FIKIR1-style symmetric-competitor controls per `b_ideas/IDEAS_AUDIT.md` Q2 summary [MEASURED HERE]).
- Stop rule: per sub-family "prior art found (cite) / null"; never present the 24 B IKI-A or no-qrels B8 numbers as 12 B evidence.

## Explicit non-fetches (do not spend web time here)

- F4 needs no fetch (one-line algebra + our 0-changed-bits check [PROOF-SKETCH + MEASURED HERE]).
- BPR / RaBitQ-original / Jégou-PQ primaries are needed ONLY if the team implements those equal-byte ANN controls (per `DO_NOT_RESCAN.md` §B.6) — not for any quant-cluster novelty verdict above.
- RRF original + hybrid storage audits belong to the fusion cluster (round-1 VERIFY_QUEUE item 7), not to F1–F6.
- LoCoMo numbers anywhere: gold authority disputed (n = 1531 vs 1535; 156 unapplied corrections [MEASURED HERE — `digest_r1/FINDINGS_DIGEST.md` + `a_ladder/LADDER_AUDIT.md`]) — never use LoCoMo levels to settle a quant verdict.
- RealTalk 24/48 B numbers do not exist by design (0 RealTalk rows in the ladder package [MEASURED HERE — `a_ladder/LADDER_AUDIT.md` Q5]) — do not go looking for them in these fetches.
