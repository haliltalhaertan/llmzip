# FINDINGS DIGEST — llmzip top10 programme, as of 2026-09-16
[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Every number below was RE-DERIVED by the coordinator from stored per-query top-10 ids,
not copied from a worker's summary. Production anchors reproduce to 0.0000 pp.
Paired archive-clustered bootstrap, 20000 reps, seed 20260916. "SIG" = 95% CI excludes 0.

## THE SYSTEM
Per archive: Z = [LSA32(word) | word-tfidf | char-tfidf] -> TruncatedSVD(96, seed 5204)
-> normalize -> center -> sign -> 96 bits = 12 bytes per document.
Scorers: sym = -Hamming(doc bits, query bits); qscale = dot(doc +-1, qC/sigma),
sigma = per-archive std of DOCUMENT C columns (documents only, never fitted on queries).

Benchmarks: RealTalk (10 archives, 705 q, 8944 docs), PerLTQA (30 archives, 8265 q,
12288 docs), LME (470 archives, 470 q). Hit@10 = at least one gold in exactly 10 ids.

## THE CENTRAL DIAGNOSIS (the thing to reason about)
RealTalk Hit@10:
  float_std  (96 dims, FULL FLOAT, 384 B/doc, NO quantization) = 48.51
  sign96     (96 dims, 1 bit/dim,   12 B/doc)                  = 46.68
  qscale     (same 12 B codes, better query reading)           = 49.65
  BM25       (plain lexical, no learning)                      = 54.18
=> Quantization costs only 1.83 pp. BM25 beats the UNCOMPRESSED representation by 5.67 pp.
   The bottleneck is the 96-dim REPRESENTATION, not the 12-byte budget.

Stratifying 705 queries by max IDF of a term shared between query and its gold doc:
  band        n     CODE    BM25   BM25-CODE
  no_shared   24   20.83   16.67      -4.17
  common     224   20.98   15.62      -5.36   <- WE WIN
  mid        116   49.14   45.69      -3.45   <- WE WIN
  rare       341   70.67   85.04     +14.37   <- WE LOSE BADLY
(341/705 = 48.37%, the largest band but NOT a majority. Two tokenization rules give
 341 and 412 for this band; conclusions below hold under both.)

Mathematical reading (a second reviewer derived and we verified numerically to 1e-14):
for a feature present in exactly ONE record i, the energy kept by a rank-k projection is
rho_i = sum_{j<=k} U_ij^2, and sum_i rho_i = k EXACTLY. So in a 500-record archive at
k=96, the AVERAGE retention for such unique features is 96/500 = 0.192. Keeping every
unique detail at full strength is mathematically impossible, not an implementation bug.
IMPORTANT LIMIT: this does NOT prove "rare is always discarded" — an explicit counterexample
exists where, holding frequencies and k fixed, changing only the co-occurrence structure
flips a rare feature from fully dropped to fully preserved. Co-occurrence structure matters,
not rarity alone. Measured on 3 LME archives (1486 records, rebuilt bit-exactly): median
reconstruction quality of word features in [0,1] where 1 = perfect, 0 = as bad as writing
the column to zero: df=1 features 0.153/0.179/0.189 vs df>20 features 0.531/0.547/0.536.

## WHAT WE TESTED AND WHAT HAPPENED (all arms keep exactly 96 bits / 12 bytes)

### Quantization layer — 4 of 4 FAILED
  RealTalk Hit@10 (qscale): FULL 49.65 | ITQ 32.77 | random rotation 35.04 (3 seeds
  34.61..35.32) | median threshold 49.22.   PerLTQA: FULL 80.00 | ITQ 78.91 | rand 79.04.
  ITQ minus random = -2.27 pp RealTalk, -0.13 pp PerLTQA => ITQ's 50-iteration optimization
  bought NOTHING; ANY rotation does this damage. This is the informative part.
  Verified identity on real data: sign(C_ij/sigma_j) == sign(C_ij), 0 of 63552 doc bits and
  0 of 8160 query bits changed by per-axis rescaling. Only rotation or a shifted threshold
  can change a bit.
  Bit balance: production mean frac-of-1s 0.492 with per-bit range 0.309..0.658; rotated
  arms 0.499 with range 0.459..0.545. Rotation makes bits MORE balanced (textbook "better")
  and performance WORSE. Interpretation on the table: our unbalanced, axis-aligned bits are
  a FEATURE — an axis that fires on a minority of documents carries discriminative mass, and
  rotation smears it across all 96 axes.
  Cost: rotation R is 96x96 floats per archive = 3.43x (RealTalk) / 7.50x (PerLTQA) the
  entire document payload it fails to improve.

### Representation layer — mixed, and it REVERSES across benchmarks
  Zero-arm identity verified: IDF_p0 and SHIFT_m0 differ from production in 0 queries.
  A) IDF^p reweighting of the word block (p=0 control, 0.5, 1, 2):
     RealTalk Hit@10: all arms ns. RealTalk FR@3 qscale IDF_p2: +2.61 pp, CI [-0.12,+5.30] ns.
     MECHANISM CHECK (RealTalk, FR@3, qscale, IDF_p2 vs FULL, by band):
        common n=133  -0.75 ns | mid n=153 -0.20 ns | RARE n=412 +4.78 pp CI [+0.69,+8.43] SIG
     The gain sits ONLY in the rare band — exactly where the stated mechanism predicted.
     Replicated under a second tokenization rule (n=408): +4.83 pp CI [+0.70,+8.50] SIG.
     Hit@10 in that band: +0.49 ns => ordering improves inside an unchanged pool.
     CAVEAT: this is a subgroup contrast chosen AFTER seeing results. Exploratory only.
     PerLTQA REVERSES and significantly: IDF_p2 FR@3 qscale -1.76 CI [-2.78,-0.74] SIG;
     IDF_p1 -1.17 SIG. Same idea, opposite sign, both significant.
  B) all-but-the-top / component shift (use components m+1..m+96, still exactly 96 dims):
     PerLTQA(subset n=2967) SHIFT_m1 Hit@10 +1.58 CI [+0.69,+2.47] SIG (sym +1.35 SIG).
     RealTalk SHIFT_m1 Hit@10 -0.28 ns, and sym FR@3 -1.06 CI [-2.02,-0.03] SIG (harmful).
     Again opposite signs.

### Channel ablation — reverses across benchmarks
  RealTalk (n=705, qscale Hit@10): FULL 49.65 | NO_LSA 52.06 (+2.41, CI [-0.28,+5.15] ns)
    | NO_CHAR 43.83 (-5.82 SIG, harmful) | WORD_ONLY 46.24 (-3.40 SIG, harmful)
  PerLTQA (n=8265, qscale Hit@10): FULL 80.00 | NO_LSA 79.53 (FR@3 -1.23 SIG, HARMFUL)
    | NO_CHAR 80.83 | WORD_ONLY 81.37 (+1.37 CI [+0.50,+2.21] SIG, and FR@3 +2.09 SIG)
  So the char channel is significantly ESSENTIAL on RealTalk and significantly HARMFUL to
  drop... no: significantly BENEFICIAL to drop on PerLTQA. Dropping LSA helps RealTalk
  (ns) and hurts PerLTQA (SIG). LME is still running.
  WORD_ONLY is also 5.6x faster to build (28.1s -> 5.0s per archive on PerLTQA).

### First-stage retrieval — the LARGEST measured gain, and it is not ours
  RealTalk pool quality @100 candidates: CODE 75.60 | BM25 78.16 | RRF(k=60) 81.28.
  RRF - CODE = +5.67 pp CI [+3.23,+8.20] SIG; RRF - BM25 = +3.12 SIG.
  Complementarity is real: at 100 candidates CODE alone finds 49 queries BM25 misses,
  BM25 alone finds 67 queries CODE misses.
  Honest cost (RealTalk, 8944 docs): our codes+sigma 115,008 B; BM25 inverted index
  670,511 B under a fair varint delta-gap encoding (a pickle dump inflates this to
  1,450,229 B — do not quote the pickle number); index + raw text 1,669,165 B.
  So BM25 is ~5.8x our storage, and better.

### Reranking ceiling (oracle reranker over the pool we already retrieve, FR@3)
  PerLTQA 53.24 -> 76.52 @100 candidates (+23.3) | LME 54.27 -> 92.62 (+38.4)
  RealTalk 22.41 -> 61.30 (+38.9). At 500 candidates LME gold-in-pool = 100%.
  The right evidence is usually ALREADY in the pool and fails to reach the top 3.
  (Oracle = knows gold. Not a usable method; an upper bound only.)

### Budget splitting — FAILED, and the failure decomposes
  Splitting the 96 bits between SVD dims and a rare-term Bloom sketch:
    96+0 = 49.65 | 80+16 = 33.33 | 64+32 = 34.61 | 48+48 = 33.48
  SVD-only truncation alone: 96 -> 45.39(80) -> 40.85(64) -> 36.45(48).
  Decomposition of the loss: at 80/16 truncation explains only 26% of the damage (the
  fusion design caused the rest); at 64/32 it is 59%; at 48/48 it is 82%. An earlier
  claim that "truncation is the sole cause" was WRONG and is retracted.
  Also: a 32-bit Bloom score yields only ~5 distinct values per query, so it ranks
  almost entirely by tie-break. The failure is partly a bad sketch, not only truncation.

## KNOWN NEGATIVE RESULTS — DO NOT REDISCOVER
  - Arbitrary quantile thresholds hurt badly (PerLTQA zero-threshold .76 vs q0.1 .31).
  - asym (old asymmetric arm) helps PerLTQA but LOSES on LME (-3.56 pp FR@3): benchmark
    sign reversal is the norm in this programme, not the exception.
  - qscale is not new: identical results exist in our hit10/QSCALE.json, in an external
    gpt-6-pro package, and in a fresh rerun — all to 0.000 deviation.
  - PPLX-0.6B semantic arm was ABANDONED: encoder ran at ~4.3 texts/s (73 tok/s) and the
    cause was never diagnosed.

## OPEN, UNRESOLVED
  - LoCoMo gold authority is contradictory (n=1531 vs 1535; 156 audited gold corrections
    never applied). Every LoCoMo number is disputable.
  - RealTalk has only 10 archives; its CIs are wide and it is exploratory throughout.
  - No arm has EVER won on both benchmarks simultaneously.
  - Literature: no source found reporting gold Hit@10 at K=10 from <=12-16 byte/doc codes.
    Our target is unmeasured in the literature, neither confirmed nor refuted.
  - Uncompressed SOTA reaches only ~78 Recall@10 on hard multi-hop questions.
  - An oracle selector that picks the better of our own two scorers per query saturates at
    ~55% on RealTalk => the ~45-point gap is representational, not a ranking-order problem.
