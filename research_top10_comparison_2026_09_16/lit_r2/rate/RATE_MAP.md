[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# RATE MAP — bits vs retrieval quality: theory and curve shape

Role: literature analyst, rate cluster. No web access this session. [RECALLED-FROM-MEMORY]
claims below carry explicit confidence (low / medium / high) and are UNVERIFIED until the
coordinator fetches them. Nothing here is a citable source. Numbers from our programme are
[MEASURED HERE] with the file named. Derivations are [PROOF-SKETCH]. Hypotheses are
[CONJECTURE] with falsifiers stated.

Read first (all of them): [MEASURED HERE — established by reading the files]

- `digest_r1/FINDINGS_DIGEST.md` (system, anchors, central diagnosis)
- `incoming_20260916b/a_ladder/LADDER_AUDIT.md` (the 12/24/48 B ladder, verified packed)
- `incoming_20260916b/b_ideas/IDEAS_AUDIT.md` (companion packages, controls)
- `digest_r1/lit/LITERATURE_MAP.md` round 1 (Q5 "no plug-and-play bound" conclusion under test)
- `inventory/literature/DO_NOT_RESCAN.md` + `GAP_TO_100.md` (already-scanned boundary)

Coordinator-verified facts I take as given, not re-derived: ITQ = Gong & Lazebnik image
descriptors + Euclidean-neighbour ground truth; ABTT = Mu, Bhat, Viswanath arXiv:1702.01417
word vectors; RRF = Cormack, Clarke, Buettcher SIGIR 2009; Husbands et al. 2005 exists.
[MEASURED HERE — stated in this round's brief.]

System under discussion: per archive Z = [LSA32(word) | word-tfidf | char-tfidf] ->
TruncatedSVD(k) -> row-normalize -> center -> sign -> k bits = k/8 bytes/doc, each width
re-fits its own SVD (12 B code is NOT a prefix of 24 B). [MEASURED HERE — brief §THE SYSTEM.]

## VERDICTS FIRST (Q2 headline first, as instructed)

| Question | Verdict | One line |
|---|---|---|
| Q2 non-monotone quality in code length / k | PARTIALLY KNOWN [RECALLED-FROM-MEMORY: medium on folklore half; low on negative half] | Qualitative "too many LSI dims hurts" is old folklore; our exact shape (sign-coded bits, k/n -> 1, 48 B worse than 12 B SIG [MEASURED HERE], scorer-dependent [MEASURED HERE]) is not recalled anywhere. |
| Q1 bits->gold-Recall theory | OPEN, confirms round 1 [RECALLED-FROM-MEMORY: medium-high on the negative] | No recalled theorem bounds gold Hit@K/Recall@K from bits/doc; each candidate theory bounds something else [PROOF-SKETCH of mismatch per §Q1]. |
| Q3 sweet-spot scaling rule k(n) | OPEN [RECALLED-FROM-MEMORY: low-medium, negative recall] | No recalled scaling law; folklore says roughly fixed k, which our data contradicts in detail [CONJECTURE on folklore; interval MEASURED HERE]. |
| Q4 tiny-collection dimensionality | PARTIALLY KNOWN, split by era [RECALLED-FROM-MEMORY: medium on sizes; low on k pairings] | Early float-LSI work WAS on ~10^3-doc collections; modern sign/PQ/binary work is ~10^5+ [MEASURED HERE for scanned set]; our exact regime (per-archive sign codes, n ~ 300-1500) has no recalled modern counterpart. |

## Q2. HEADLINE: is non-monotone quality in budget known? — PARTIALLY KNOWN / OPEN in our regime

### Q2.0 The measured shape, stated precisely (so no fetch confuses it with something else)

- qscale FR@3: LME 52.47 -> 61.48 -> 61.75; PerLTQA 52.98 -> 54.82 -> 51.87 (192->384
  -2.95, CI [-3.87,-2.01] SIG); LoCoMo 35.11 -> 41.21 -> 44.15. [MEASURED HERE —
  `a_ladder/LADDER_AUDIT.md` §1 table.]
- qscale Hit@10 LME 88.72 -> 89.15 -> 86.60 (192->384 -2.55, CI [-4.47,-0.64] SIG;
  48 B worst of three). PerLTQA Hit@10 79.89 -> 80.71 -> 79.41 (192->384 SIG negative).
  [MEASURED HERE — `a_ladder/LADDER_AUDIT.md` §1/§4.]
- Solver confound separated: exact96-vs-original96 FR@3 is -1.81 (LME, ns), -0.25
  (PerLTQA, ns), -0.73 (LoCoMo, ns); dimension effects must be read exact96->192->384,
  never original96->384. [MEASURED HERE — `a_ladder/LADDER_AUDIT.md` §4.]
- LoCoMo rises monotonically but its gold is disputed (n=1531 vs 1535, 156 unapplied
  corrections). [MEASURED HERE — `digest_r1/FINDINGS_DIGEST.md` §OPEN + `a_ladder/LADDER_AUDIT.md` §7.5.]
- Rank-cap honesty: 8 PerLTQA archives (2217 queries, 26.82% of 8265) have effective rank
  293-381 < 384; missing dims are constant-filled while full 48 bytes are charged; 1 LoCoMo
  archive (81 queries) rank 369. [MEASURED HERE — `a_ladder/LADDER_AUDIT.md` §4 rank-cap
  paragraph; 26.82% = 2217/8265 [PROOF-SKETCH — arithmetic checked in-session with
  `$HOME/muse-work/ml-python`.]]

### Q2.1 The observation that narrows every explanation: non-monotonicity is scorer-dependent

Same documents, same fitted subspaces, same k ladder — different readouts diverge.
[MEASURED HERE — all rows from `a_ladder/LADDER_AUDIT.md` §2/§3; deltas re-arithmetic-checked
in-session [PROOF-SKETCH]:]

| Family (PerLTQA FR@3) | 96-dim | 192-dim | 384-dim | Shape |
|---|---|---|---|---|
| qscale (doc-bits, std query) | 52.98 | 54.82 | 51.87 | PEAK then SIG fall (-2.95) |
| hamming/sym (both sides bits) | 49.01 | 50.68 | 47.74 | PEAK then fall |
| float_std (std floats, no sign) | 56.24 | 57.78 | 54.49 | PEAK then fall (-3.28) |
| asym (doc-bits, UNstandardised query) | 53.71 | 57.30 | 58.03 | MONOTONE RISE (+4.31 over ladder) |
| float_raw (UNstandardised floats) | 55.03 | 58.55 | 60.43 | MONOTONE RISE (+5.39 over ladder) |

LME mirrors it: qscale Hit@10 peaks at 192 then falls SIG; asym FR@3 rises monotonically
49.51 -> 58.79 -> 61.59 and float_std rises monotonically 54.85 -> 59.89 -> 63.61 on the
same archives. [MEASURED HERE — `a_ladder/LADDER_AUDIT.md` §2/§3.]

- Implication: the decline tracks the STANDARDISED family (center and/or /sigma), not "more
  dimensions" per se. The two unstandardised readouts never decline. [CONJECTURE — falsified
  if a re-analysis shows the asym/float_raw monotonicity vanishing under a different
  tie-break or cohort; both use the same SHA tie-break and cohorts per the audit [MEASURED
  HERE — `a_ladder/LADDER_AUDIT.md` §5], so the falsifier must come from new data, e.g. a
  RealTalk ladder or a 4th rung.]
- Consequence for the literature search: any candidate explanation that predicts harm from
  trailing dims unconditionally (noise dims exist, therefore quality falls) is insufficient —
  it must explain why asym/float_raw are IMMUNE on identical trailing dims. Only
  standardisation-aware mechanisms (Q2.3 candidates (a)/(d) below) survive this filter
  without extra assumptions. [CONJECTURE — falsified by finding a standardisation-free
  mechanism that separates qscale from asym.]

### Q2.2 Candidate (i): classic LSI "optimal number of dimensions" — KNOWN qualitatively, OPEN quantitatively

- What I recall: early LSI work reported retrieval effectiveness rising with k to a broad
  optimum and then flattening or declining, attributed to trailing components re-introducing
  noise. I recall optimum estimates in the low hundreds of dimensions on English collections
  of that era, and Dumais-style dimensionality plots with a hump shape. [RECALLED-FROM-MEMORY:
  medium on the existence of hump-shaped k plots; low on every number, author, venue, year,
  collection, and metric.] I cannot confirm from disk which paper shows a STATISTICALLY
  significant decline (vs a flat plateau within noise), what metric (precision-recall, not
  gold Hit@10), or whether any paper separates solver from dimension effects as our audit
  does. [RECALLED-FROM-MEMORY: low — honest ignorance flag.]
- Fit to our data: GOOD qualitatively (peak at 192 then fall matches a hump), POOR in the
  obvious quantitative reading — I recall optima quoted as roughly corpus-independent
  (order ~100-300), while our k/n at the peak is ~0.35-0.47 on PerLTQA/LME-typical archives,
  i.e. the "optimum" here sits at a far larger FRACTION of n than any recalled LSI number.
  [CONJECTURE — falsified if the fetched LSI papers turn out to scale k with n, or quote
  optima above 300 on small collections.]
- What I recall about where the optimum sits and how it scales: I recall NO scaling rule in
  the LSI literature — the recalled practice is a fixed recommendation (order one-to-several
  hundred) essentially independent of corpus size, which is exactly why Q3 below is OPEN.
  [RECALLED-FROM-MEMORY: low-medium — a negative recollection, needs the targeted fetch to
  become evidence.]
- Assessment: KNOWN as folklore-shape, OPEN as a quantitative match. Fetch F1/F2 (fetch queue)
  settles it: record each LSI dimensionality plot's collection size n, metric, k grid, peak
  location, and whether the post-peak fall is SIG or plateau. [CONJECTURE about process.]

### Q2.3 Candidate (ii): peaking / Hughes phenomenon, k/n as governing ratio — PLAUSIBLE analogy, not a KNOWN match

- What I recall: Hughes (1968, "On the mean accuracy of statistical pattern recognizers")
  showed classifier accuracy peaking then falling as dimensionality grows at fixed training
  sample size; the later small-sample literature (I recall Raudys & Jain 1991 survey, and the
  Fukunaga/Foley-Sammon line on estimation error growing with d/n) treats parameters-per-sample
  as the governing ratio. [RECALLED-FROM-MEMORY: medium that Hughes 1968 exists with this
  thesis; low-medium on Raudys & Jain details; low that any of it mentions SVD, cosine
  retrieval, or sign codes.]
- Fit to our data: SUGGESTIVE on ratios, MISMATCHED on mechanism. Our k/n (checked in-session
  [PROOF-SKETCH]): at k=96, k/n ~ 0.11-0.33 (typical archives); at k=192, ~0.21-0.66; at
  k=384, ~0.43-1.31 (smallest PerLTQA archive exceeds 1.0 — more dims than documents).
  The fall appears exactly where k/n crosses ~0.4-0.7 on PerLTQA. But Hughes-style peaking is
  a statement about TRAINED CLASSIFIER generalisation with estimated parameters per class,
  not about an unsupervised per-archive SVD followed by query projection with no learned
  classifier weights. The transfer is analogy, not application. [CONJECTURE — falsified if the
  fetched peaking papers turn out to include unsupervised spectral-retrieval settings, or if
  our per-archive peak location does NOT track k/n (test: correlate per-archive 192->384
  delta against that archive's own k/n — see distinguishing tests).]
- Assessment: PLAUSIBLE framing device, NOT a KNOWN result for our pipeline. It earns its fetch
  rank (F3) because it is the only candidate that predicts k/n — not k — as the x-axis, which
  is directly testable on disk (see §Q2.6). [CONJECTURE.]

### Q2.4 Candidate (iii): near-full-rank / trailing-noise-components at n ~ 500 — OUR CONJECTURE with a recalled background

- The background fact is standard linear algebra, not literature: singular values of a noisy
  term-document matrix decay, and trailing singular vectors are increasingly
  archive-idiosyncratic (sensitive to single-document perturbations). That trailing SVD
  directions are unstable at k near rank(Z) is textbook matrix-perturbation content
  (Wedin-type sin-theta behaviour: sensitivity scales inversely with spectral gaps, which
  shrink in the tail). [RECALLED-FROM-MEMORY: medium on the textbook characterisation;
  low on any citable theorem number from memory.] No fetched source is needed for the math;
  a fetch is needed for whether anyone CONNECTED it to a retrieval-quality decline at
  k/n -> 1. I recall no such named result. [RECALLED-FROM-MEMORY: low — negative recall.]
- The sign-coding amplifier, specific to our pipeline: after row-normalize -> center -> sign,
  every retained dimension gets an EQUAL doc-side vote in Hamming, and an equal-magnitude
  doc-side vote in qscale (only the query side keeps /sigma magnitudes). So moving 96->384
  appends ~288 low-variance dims EACH VOTING AS LOUDLY AS dim 1. The float representation
  keeps variance weighting (dim 1 counts more); the sign code destroys it. Formally, with
  doc code b in {±1}^k, Hamming score differences weight all coordinates identically by
  construction; variance information survives only on the query side of qscale/asym.
  [PROOF-SKETCH — follows from the pipeline definition in the brief; checkable without any
  paper. Falsified if a re-read of the scorer shows per-dim doc-side weights I missed.]
- This amplifier PREDICTS the scorer split in §Q2.1 with no extra assumptions: float_raw
  (variance-weighted, unstandardised) keeps rising; asym (query magnitudes intact, no /sigma
  blowup of tail dims) keeps rising; qscale (query tail dims DIVIDED by small sigma_j,
  amplifying exactly the noisiest query coordinates) falls; Hamming (no magnitudes anywhere)
  falls. The /sigma division is the sharpest version of the story: standardisation whitens
  the tail noise up to unit variance before it votes. [CONJECTURE — the strongest single
  hypothesis in this report. Falsifiers: (1) per-dim analysis showing tail dims carry
  positive gold signal under qscale; (2) a variance-weighted sign readout (e.g. weight dim j
  by s_j at score time, still 48 B payload) that does NOT restore monotonicity; (3) the
  rank-cap-excluded re-analysis (drop the 8 capped PerLTQA archives) eliminating the SIG
  decline.]
- Rank-cap interaction: 26.82% of PerLTQA queries live in archives where 384-dim directions
  do not exist and bits are constant-filled — dead voting weight that can only add ties, and
  tie-breaks then decide ranks. [MEASURED HERE — cap counts from `a_ladder/LADDER_AUDIT.md`
  §4; tie-break mechanism [PROOF-SKETCH] from the deterministic SHA rule in the same file §5.]
  But rank-cap CANNOT be the whole story: LME Hit@10 falls SIG to worst-of-three with no
  reported cap, and float_std PerLTQA (no bits at all) also falls 57.78 -> 54.49.
  [MEASURED HERE — `a_ladder/LADDER_AUDIT.md` §§1-4; absence of LME caps is absence in the
  audit's rank_caps report, so flag as [MEASURED HERE with that caveat].]
- Assessment: background KNOWN (textbook perturbation theory); CONNECTION to a SIG
  gold-recall decline in sign-coded retrieval is OUR CONJECTURE. It is the hypothesis the
  programme can test cheapest (all tests on disk, §Q2.6). [CONJECTURE.]

### Q2.5 Candidate (iv): concentration of distances / hubness at fixed n — CONJECTURE, weakest fit

- What I recall: Beyer et al. (1999, "When is nearest neighbor meaningful?") on distance
  concentration degrading nearest-neighbour contrast as dimensionality grows; Radovanovic et
  al. (~2010, SIAM / JMLR-adjacent hubness work) on high-dimensional hubs skewing k-NN
  retrieval. I recall both as real lines with L_p-norm analyses. [RECALLED-FROM-MEMORY:
  medium on Beyer et al. thesis and era; medium-low on Radovanovic details; low on exact
  venues/years.] Neither, to my recall, studies binary Hamming codes from per-archive SVD at
  k/n -> 1, and concentration results standardly assume i.i.d. coordinates or growing d at
  fixed sample — our coordinates are orthonormal projections with decaying variance, a
  different geometry. [RECALLED-FROM-MEMORY: low; CONJECTURE on the mismatch.]
- Fit to our data: WEAK. Concentration predicts a GRADUAL contrast loss affecting all
  scorers on the same geometry, not a scorer split where asym/float_raw sail through the
  same 384-dim space. It also predicts the largest archives to suffer most at fixed k, yet
  our fall is sharpest on PerLTQA (mid-size archives), while LoCoMo (similar sizes) rises.
  [CONJECTURE — falsified by hubness diagnostics: if high-k archives show rising hub
  skewness (k-occurrence distribution) or collapsing relative contrast that tracks the
  per-archive 192->384 delta, this candidate revives.]
- Assessment: OUR CONJECTURE, currently disfavoured. Keep one fetch (F4, low rank) so the
  coordinator can rule it in/out with the primary theorems; do NOT design experiments around
  it first. [CONJECTURE.]

### Q2.6 Which explanations our data can distinguish, and how (all on-disk, no fetch needed)

1. Rank-cap vs genuine decline: re-aggregate PerLTQA 192->384 EXCLUDING the 8 capped
   archives (6028 queries remain). If the SIG -2.95 survives undiminished, caps are a
   side-show; if it halves, quote both numbers henceforth. [CONJECTURE about method —
   the exclusion re-aggregation is exact from stored per-query rows [MEASURED HERE —
   rows exist per `a_ladder/LADDER_AUDIT.md` §5].]
2. k/n as x-axis (peaking) vs k as x-axis (LSI-optimum): plot per-archive 192->384 delta
   against that archive's OWN k/n (or n). Peaking predicts the delta worsens with k/n;
   fixed-optimum predicts it depends on k only. Archives span n ~ 293-1548, so k/n at
   k=384 spans ~0.25-1.31 — enough spread to separate the axes. [PROOF-SKETCH of design;
   n-range [MEASURED HERE — brief + audit].]
3. Variance-weighting amplifier: score the EXISTING 384-bit payloads with a
   variance-weighted readout (dim weight s_j or s_j^2, still 48 B stored) without refitting.
   If monotonicity restores, the noise is in the VOTING, not the subspace; if not, the
   subspace itself is exhausted. Cost: rescore only. [CONJECTURE — design proposal, not a
   result. Also directly tests the IKI Idea-A residue: 96x2 Lloyd-Max lost to 192x1 on
   2/3 benches [MEASURED HERE — `b_ideas/IDEAS_AUDIT.md` Package 3], consistent with
   "directions beat precision" until the voting breaks.]
4. Nested-vs-refit: each width re-fits its own SVD (12 B NOT a prefix of 24 B).
   [MEASURED HERE — brief.] A nested truncation (top-192 of the 384-fit, still 24 B) that
   beats the refit-192 would implicate refit instability rather than intrinsic dimension.
   [CONJECTURE — design proposal.]
5. Hubness/concentration check: per-archive relative contrast and hub skewness at
   96/192/384 vs per-archive delta. A null correlation buries candidate (iv) with data
   instead of memory. [CONJECTURE — design proposal.]

Net Q2 verdict: PARTIALLY KNOWN. The hump SHAPE has classical precedent (LSI optimum);
the GOVERNING RATIO (k vs k/n), the SIGN-CODE AMPLIFIER with its scorer split, and the
48-B-WORSE-THAN-12-B significance are, to my recall, new. The single most decision-relevant
next number is test 1 (cap-excluded delta), then test 3 (weighted rescore) — both decide
whether to stop the ladder at 24 B or fix the readout and continue. [CONJECTURE on priority.]

## Q1. Is there ANY bits->gold-Recall theory? — OPEN (round-1 "no plug-and-play bound" survives harder scrutiny)

Round 1 verdict was OPEN with medium-high confidence. Re-tested against five named bodies
below; conclusion unchanged, confidence higher on the negative. Each entry states what the
theory DOES bound, so the coordinator never misquotes it as a gold-recall ceiling.

### Q1.1 Rate-distortion theory — does NOT bound what we need

- What it is (textbook): Shannon rate-distortion gives the minimum rate R(D) for a source
  to be reproduced within expected DISTORTION D under a STIPULATED single-letter distortion
  measure (classically squared error, Hamming distortion on reproduction alphabet).
  [RECALLED-FROM-MEMORY: high on the textbook statement; Cover & Thomas is the canonical
  reference, low on edition/page from memory.]
- Why the distortion is the wrong one: our loss is a top-K GOLD-RETRIEVAL indicator (Hit@10
  = any-gold-in-exactly-10; FR@3 = gold fraction in top 3) [MEASURED HERE —
  `digest_r1/FINDINGS_DIGEST.md` header], which is (a) a function of the QUERY-code GOLD
  geometry, not of doc reconstruction fidelity; (b) discontinuous in the code (one rank swap
  flips Hit); (c) query-distribution- and label-dependent. Rate-distortion has no query side,
  no ranking operator, and no gold labels. Instantiating "distortion = 1 - Hit@10" breaks the
  single-letter, source-only assumptions the theorems need. [PROOF-SKETCH of the mismatch —
  checkable from definitions, no paper needed.]
- What it bounds INSTEAD: reconstruction fidelity of DOCUMENT VECTORS at a bitrate (e.g. how
  well 96/192/384-bit codes approximate C itself) — the quantity our float-vs-sign gap
  already measures empirically (float_std384 beats qscale384 SIG on LME +1.86 and PerLTQA
  +2.62 [MEASURED HERE — `a_ladder/LADDER_AUDIT.md` §3]). A rate-distortion calculation
  would predict THAT gap's floor, never the gold-recall ladder. [CONJECTURE on use; numbers
  MEASURED HERE as cited.]
- Ancillary note: the programme's own 2^96-counting argument is vacuous for the same
  reason round 1 gave (2^96 codewords >> ~900 docs/archive, so distinguishing DOCS is not
  the constraint; the constraint is query-side generalisation through the spectral
  bottleneck that already loses to BM25 uncompressed, 48.51 vs 54.18 [MEASURED HERE —
  `digest_r1/FINDINGS_DIGEST.md` central diagnosis]). Q1 needs a QUERY-MAPPING bound, not a
  codebook count. [PROOF-SKETCH — repeats round-1 logic, still valid.]

### Q1.2 Fano-type bounds via I(code; gold) — a research project, not a citation

- What it is: Fano's inequality lower-bounds error probability given mutual information
  between observation and target. In principle P(error) >= f(I(code; gold)). [RECALLED-FROM-
  MEMORY: high on the inequality's existence and textbook status; medium on the exact form
  from memory, so I state no formula here.]
- Why it does not exist off-shelf for us: I(code; gold) for OUR pipeline (per-archive SVD +
  sign + qscale readout + top-K operator + 8-13-token queries) is itself unmeasured, and the
  bound also needs the gold prior entropy over ~300-1500 candidates per archive with 1-few
  positives — a degenerate, archive-varying quantity. Nobody banks a theorem with our
  pipeline's information numbers inside. The honest deliverable would be to ESTIMATE
  I(code; gold) on disk (an experiment), not to fetch a bound. [CONJECTURE — falsified by a
  fetch returning a retrieval-flavoured Fano bound with a worked binary-code example; I
  recall none [RECALLED-FROM-MEMORY: medium on the negative].]
- What it bounds INSTEAD (if built): a lower bound on ANY decoder's error given the measured
  information — a diagnostic of our codes, not a fact about bits-vs-recall in general.
  [PROOF-SKETCH of scope.]

### Q1.3 LSH / binary-hashing theory — bounds EFFICIENCY and APPROXIMATION, not gold recall

- What I recall: the LSH line (Indyk-Motwani; Charikar simhash for cosine; Datar et al.
  p-stable; Andoni-Indyk surveys) proves (c, r)-ANN guarantees: with stated space/time, a
  (1+eps)-approximate neighbour is returned with stated probability. Spectral Hashing
  (I recall Weiss et al.) and ITQ (verified this round: image descriptors, Euclidean-
  neighbour ground truth) optimise code balance / quantisation error as PROXIES.
  [RECALLED-FROM-MEMORY: medium on LSH/Charikar thesis; low on theorem numbers; ITQ scope
  [MEASURED HERE — brief's coordinator verification, taken as given].]
- Why it misses: every guarantee is relative to the FLOAT GEOMETRY the hash approximates
  ("returns nearly the float ranking's neighbour"), while our gap is float-geometry-vs-GOLD
  (BM25 beats our uncompressed 96-dim float by 5.67 pp [MEASURED HERE — FINDINGS_DIGEST
  central diagnosis]; float SOTA itself sits ~78% Recall@10 on hard multi-hop [MEASURED HERE
  — GAP_TO_100 coverage statement]). ANN-recall >99% of a float ranking whose gold rate is
  ~78% is still ~78%. The fetched-set review already records this cap explicitly for
  Extended RaBitQ. [MEASURED HERE — `inventory/literature/GAP_TO_100.md` row 7.]
- What it bounds INSTEAD: query TIME/SPACE vs approximation ratio to the INPUT metric —
  the right theory for "how fast is 48 B search", the wrong theory for "does 48 B retrieve
  gold". Our HIZ package already prices the engineering side (SIMD 1.7-1.9x over fair float
  SGEMV, encoder-dominated end-to-end [MEASURED HERE — `b_ideas/IDEAS_AUDIT.md` Package 7]).
  [RECALLED-FROM-MEMORY on LSH scope: medium; HIZ numbers MEASURED HERE as cited.]
- The one hashing-adjacent precedent that DOES speak to retrieval-vs-reconstruction (ScaNN
  anisotropic loss, recalled: penalise parallel/inner-product error over orthogonal error):
  supports the PRINCIPLE "reconstruction-optimal != retrieval-optimal" but tests dense
  embeddings only, not TF-IDF/SVD sign codes, and states a loss+win, not a bits->recall
  function. It was already starter S3 in round 1, still unfetched. [RECALLED-FROM-MEMORY:
  medium on thesis, low on details — fetch F6.]

### Q1.4 Similarity-preserving-hashing generalisation bounds — closest in spirit, still not our bound

- What I recall: a thinner line (I associate it with hashing-generalisation papers using
  Rademacher/stability arguments, and with the "learning to hash" survey literature) bounds
  the gap between empirical and expected HAMMING-AGREEMENT or pairwise-label loss as a
  function of code length and sample size. [RECALLED-FROM-MEMORY: low — I cannot name a
  canonical paper, state a rate, or confirm the loss from disk. This is the weakest recall
  in Q1 and the most likely place for the coordinator's search to prove me wrong, which
  would be welcome.]
- Why it still misses even if my recall is right: the loss is pairwise/similarity
  preservation, not top-K gold retrieval with 1-few positives per query over hundreds of
  candidates; the sample is assumed i.i.d. from one distribution, not 470 independently
  fitted per-archive encoders with 1 query each (LME) or 30 archives with ~275 queries each
  (PerLTQA). [MEASURED HERE — cohort structure from FINDINGS_DIGEST/LADDER_AUDIT headers.]
  A bound that needs i.i.d. (code, label) pairs does not transfer to per-archive-fitted
  codes scored by pooled Hit@10. [CONJECTURE — falsified by a fetched bound whose setup
  matches per-query top-K gold loss.]
- What it bounds INSTEAD: how well training-time similarity preservation generalises —
  relevant to learned-hash training, irrelevant to our fixed SVD+sign pipeline with no
  training pairs. [CONJECTURE.]

### Q1.5 Empirical "bits vs recall" curves for PQ / binary embeddings — the practical substitute for theory

- What I recall: PQ/OPQ/ANN papers routinely plot recall-vs-bytes (or recall-vs-komega)
  curves that RISE MONOTONICALLY and saturate — recall of the FLOAT ranking (ANN-recall),
  not gold recall. I recall BPR (already scanned: 96 B Top-20 recall 77.9 vs DPR 78.4
  [MEASURED HERE — GAP_TO_100 row 6]) and the RaBitQ-family >99% ANN-recall claims at
  ~4.5x compression [MEASURED HERE — GAP_TO_100 row 7] as instances; the snippet-level PQ
  primary (Jegou) is in the fetched set only as a snippet [MEASURED HERE — DO_NOT_RESCAN §A].
  I recall NO PQ/binary paper plotting GOLD Hit@K against bits where the curve TURNS DOWN
  significantly — but ANN-recall curves cannot turn down by construction (more bytes can only
  preserve the float ranking better), whereas GOLD curves can (better approximation of a
  representation that misranks gold is not monotone in gold). [RECALLED-FROM-MEMORY: medium
  on the shape of ANN curves; low-medium on the negative (no downturn) claim.]
- Why this matters: it predicts exactly our confusion pattern — a team reading ANN literature
  expects monotone, then meets a gold-metric downturn. The deliverable is to make the
  ANN-recall-vs-GOLD-recall distinction an explicit programme rule (it already is, per
  GAP_TO_100's "never reconvert metrics" hygiene [MEASURED HERE — DO_NOT_RESCAN §C]) and to
  fetch one clean PQ/OPQ/ScaNN curve PLUS one BPR-style gold curve to exhibit the two shapes
  side by side. [CONJECTURE on process; hygiene rule MEASURED HERE as cited.]
- Net Q1 verdict: OPEN. No plug-and-play bits->gold-Hit@K bound recalled despite harder
  probing; each theory prices something adjacent (reconstruction, any-decoder error given
  measured I, time-vs-approximation, similarity generalisation, ANN-recall). The fetch that
  could overturn this is F7 (documented null or live theorem with a stated retrieval loss).

## Q3. Sweet spot and scaling with corpus size — OPEN (no recalled rule; computed comparison delivered)

### Q3.1 What the literature is recalled to say (honestly: little)

- I recall NO scaling law of the form k ~ sqrt(n), k ~ n/c, or k ~ log n for RETRIEVAL
  dimensionality in LSI, hashing, PQ, or dense-embedding work. The recalled LSI practice is a
  roughly FIXED k (order 100-300) across collections spanning orders of magnitude in n; the
  recalled PQ/binary practice fixes BYTES (e.g. 8-128 B) across corpus sizes spanning 10^4-10^9.
  In both cases the budget is set by engineering (memory/latency/encoder), not by a k(n)
  law. [RECALLED-FROM-MEMORY: low-medium — a negative recollection across four literatures;
  the fetch that tests it is F2/F5, which ask each primary for its n AND its k in one table.]
- IKI Idea A is our own data point on the adjacent width-vs-precision question: at fixed
  24 B, 192x1-bit beats 96x2-bit on LME (-7.07) and LoCoMo (-3.75), ties on PerLTQA (+0.67
  ns) [MEASURED HERE — `b_ideas/IDEAS_AUDIT.md` Package 3] — i.e. directions beat precision
  until the Q2 voting breakdown. No recalled paper is needed to state it; a fetch is needed
  to check whether anyone published the same tradeoff first (candidate: PQ subquantizer
  width-vs-bits ablations — fetch F5). [RECALLED-FROM-MEMORY: low on the PQ-ablation recall.]

### Q3.2 The deliverable comparison: what candidate rules would predict for our n vs measured 192

Archive sizes n ~ 293 (smallest PerLTQA) to 1548 (largest RealTalk); typical ~410 (PerLTQA
mean), ~500 (LME-typical), ~894 (RealTalk mean). [MEASURED HERE — brief + FINDINGS_DIGEST
headers.] Measured best rung: k=192 on 2 of 3 ladders (LME FR@3 still +0.27 to 384 but Hit@10
SIG-worse; PerLTQA best at 192 on both metrics; LoCoMo still rising at 384 with disputed
gold). [MEASURED HERE — LADDER_AUDIT §1/§4.] Candidate-rule predictions (arithmetic checked
in-session [PROOF-SKETCH]):

| Rule (candidate) | Formula | Predicts at n=410 | Predicts at n=500 | Predicts at n=894 | vs measured 192 |
|---|---|---|---|---|---|
| sqrt(n) | k = n^1/2 | ~20 | ~22 | ~30 | Under by ~7-10x |
| n/5 | k = n/5 | ~82 | ~100 | ~179 | Under by ~1-2.4x (closest, still under) |
| fixed LSI folklore | k ~ 100-300 | 100-300 | 100-300 | 100-300 | CONTAINS 192 — only match |
| full-rank-adjacent | k ~ n/2-n | 205-410 | 250-500 | 447-894 | Contains/exceeds 192; predicts no fall where we fall |

- Reading: no dimensionally-motivated rule (sqrt, n/c with small c) comes within 2x of our
  peak except n/5, which has no recalled theoretical basis and is fitted post-hoc here
  (do NOT adopt it — it is numerology until a mechanism predicts c=5). The only candidate
  consistent with 192 is "fixed k in the low hundreds regardless of n" — which is practice,
  not a law, and which predicts the peak should sit at the SAME k on all three benchmarks
  while our third (LoCoMo) keeps rising. [CONJECTURE on interpretation; numbers as computed.]
- The decision-relevant form: report "best rung 192 dims at n ~ 400-1500 (k/n ~ 0.2-0.5)"
  as a MEASURED interval, not a law. The fetch (F2) then asks whether any primary's
  reported optimum, rescaled to ITS n, lands in k/n ~ 0.2-0.5 — if yes on small collections
  and no on large ones, the ratio framing (Q2.3) gains its first external support.
  [CONJECTURE about process.]

## Q4. Tiny independently-fitted collections — PARTIALLY KNOWN (split verdict by era)

- Early float-LSI era: SMALL WAS NORMAL. I recall the classic LSI/early-IR test collections
  (MEDLINE/MED ~1033 docs, CRAN ~1400, CACM ~3200, CISI ~1460, TREC small tracks) sitting in
  exactly our order of magnitude, with k ~ 100 reported on them. If that recall verifies,
  then "usable dimensionality at n ~ 10^3" IS studied — for FLOAT LSI with precision-recall
  metrics — and the honest statement is that our FLOAT arms (float_std/float_raw ladders
  [MEASURED HERE — LADDER_AUDIT §3]) can be checked against that era, while our SIGN-CODED
  byte ladder cannot. [RECALLED-FROM-MEMORY: medium on collection sizes existing; low on
  which paper pairs which k with which n and what it concluded.]
- Modern binary/PQ/dense era: LARGE IS THE NORM. I recall essentially all PQ/OPQ/RaBitQ/
  ScaNN/BPR/MUVERA-style evaluations running on corpora of 10^5-10^9 (NQ 21M, MS MARCO
  ~8.8M, GIST-1M, SIFT-1M, BEIR splits at 10^4-10^6) with SHARED encoders fitted on
  millions of passages. Per-archive INDEPENDENT fitting at n ~ 300-1500 with 1-275 queries
  per encoder has no recalled counterpart in that era. [RECALLED-FROM-MEMORY: medium on the
  corpus-size claim (supported for the 11 scanned sources by DO_NOT_RESCAN/GAP_TO_100
  corpus mentions [MEASURED HERE]); low-medium on the absolute negative.]
- The per-archive twist matters more than the size: with 470 independently fitted LME
  encoders and 1 query each, there is no shared codebook, no pooled calibration, and
  archive-clustered bootstrap is the correct (and used) inference [MEASURED HERE —
  LADDER_AUDIT §4 method note]. I recall no retrieval paper whose error bars are
  archive-clustered over hundreds of tiny independent fits. [RECALLED-FROM-MEMORY: low —
  negative recall.] If the coordinator's search confirms the negative, our inference design
  (not just our numbers) is the unstudied part. [CONJECTURE.]
- Plain-English bottom line for the coordinator: do NOT write "our regime is unstudied."
  Write: "float-LSI dimensionality at n ~ 10^3 was studied in the early 1990s (verify via
  F1/F2); per-archive SIGN-CODED byte ladders with gold Hit@K at n ~ 10^2-10^3, and
  archive-clustered inference over hundreds of independent fits, have no recalled modern
  counterpart — that part is, to my recall, open." [CONJECTURE on wording; era split as
  recalled above.]

## What is REDISCOVERED vs GENUINELY OPEN (rate-cluster scope only; no overlap with round-1 lists)

Rediscovered or strongly precedented (fetch to confirm attribution, not existence):

1. Hump-shaped quality-vs-dimension with a low-hundreds optimum (LSI folklore).
   [Principle RECALLED-FROM-MEMORY medium; our qscale/hamming instance MEASURED HERE.]
2. Small-n collections (~10^3 docs) as a legitimate dimensionality testbed (early LSI).
   [RECALLED-FROM-MEMORY medium; our n MEASURED HERE.]
3. Reconstruction-optimal != retrieval-optimal as a principle (ScaNN-style).
   [RECALLED-FROM-MEMORY medium via round-1 S3; our scorer split a candidate instance,
   CONJECTURE.]

Genuinely open to my recall (our data's contribution):

1. SIG gold-metric DECLINE with 48 B worse than 12 B (-2.95 FR@3 PerLTQA; LME Hit@10 worst
   of three) on packed, C-scored, independently verified byte payloads. [MEASURED HERE.]
2. The scorer split: standardised readouts fall, unstandardised readouts rise, on identical
   subspaces — implicating /sigma-whitened tail voting, not dimension per se. [MEASURED HERE
   pattern + CONJECTURE mechanism.]
3. Equal-vote amplifier as the sign code's specific pathology (variance weighting destroyed
   by sign; ~288 tail dims outvoting the head). [PROOF-SKETCH of voting + CONJECTURE of
   causality.]
4. k/n ~ 0.2-0.5 as the measured peak interval with k/n -> 1 (and beyond, via padding) in
   the declining rung — a ratio no recalled rule predicts. [MEASURED HERE interval;
   OPEN as a law.]
5. Rank-cap-padded "48 bytes" (up to 23.7% dead bits in the smallest archives) coexisting
   with genuine decline (LME Hit@10, float_std fall) — honest byte accounting for padded
   rungs. [MEASURED HERE.]

## What would change these verdicts

- F1/F2 returning an LSI dimensionality plot with SIG post-peak decline at stated n, k, metric
  -> Q2 candidate (i) upgrades to KNOWN-quantitative; peak k/n inside 0.2-0.5 on a ~10^3-doc collection
  -> first external support for the ratio framing.
- Cap-excluded re-aggregation (on-disk test 1) halving the SIG decline -> Q2's headline
  downgrades from "genuine non-monotonicity" to "partly a padding artefact"; verdict text
  above must be rewritten, no fetch needed.
- Variance-weighted rescore of existing 48 B payloads (test 3) restoring monotonicity ->
  candidate (iii-amplifier) promotes from CONJECTURE to MEASURED mechanism; a 4th ladder rung
  becomes worth running. Failure -> subspace-exhaustion story instead; stop at 24 B.
- F7 returning a real bits->gold-recall theorem -> Q1 flips; documented null with recorded
  search strategy -> Q1 stays OPEN with higher confidence.
- F1-collection table showing early LSI never ran below n ~ 10^4 -> Q4's "small was normal"
  halves to PARTIALLY KNOWN leaning OPEN.
