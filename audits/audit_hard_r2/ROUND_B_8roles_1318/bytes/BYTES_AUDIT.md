[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# BYTES audit — is "12 bytes" really 12 bytes? (round-2, byte-budget role)

## 1. VERDICT (3 lines)

No headline byte figure survives: "12/24/48 B/doc" counts packed sign bits only, while the
reported qscale accuracies additionally require per-archive sigma + mu + a ~122 MB (f32 lower
bound) per-archive query encoder that is never charged; under symmetric deployed accounting the
codes are ~188x LARGER than the BM25 index they claim a 5.83x win over.
The "858,624 bits / 0 difference" seal proves only doc-side sign equality at k=96, not size,
not the query path, not sigma, not k=192/384 — it is routinely misreadable as end-to-end proof.
Two narrow corrections are exact and machine-checked: true doc-side cost is 12.86/25.72/51.43
B/doc with sigma (13.72/27.43/54.87 with the uncounted mu); the fair BM25 rival is also 22.5%
CHEAPER than the quoted index.

## 2. Findings table

| ID | severity | claim audited | what you did to check | result |
|----|---|---|---|---|
| F1 | CRITICAL | "12/24/48 B/doc" headline sizes (LADDER.json bytes_per_doc; REPORT/LADDER/DECISION tables; ladder.py k/8) | Read scorer code (ladder.py:144-154; arm_decision.py:27-32); recomputed narrow totals in P4 (pure JSON arithmetic); verified doc counts + text bytes (8944 docs) | Headline counts packed bits only. Even inside the report's own narrow boundary (packed+sigma f64) truth is 12.86/25.72/51.43 B/doc (+7.15%). Published integers are wrong. |
| F2 | CRITICAL | "Honest storage: codes+sigma 115,008 B vs BM25 index 670,511 B (5.83x)" (REPORT sec 4; FINAL_STATE "Honest cost accounting") | Rebuilt RT05 pipeline at k=96/192/384 (P1, ml-python); fit vectorizers for all 10 archives (P2); summed encoder matrices + idf + term bytes; recomputed BM25 both tokenizers (P3) | Query encoder (per-archive TF-IDF vocabs+IDF, LSA-32 SVD, SVD-k components) totals ~126 MB lower bound (~14.1 KB/doc avg, range 7.2-34.4 KB/doc) vs BM25 index 0.67 MB. Symmetric ratio is ~188x AGAINST codes (~243x vs the fair frozen BM25). The 5.83x win is an asymmetric-boundary artifact. PQ worker flagged exactly this ("encoder missing... NOT MEASURED, not zero", pq/REPORT.md:58-61); never followed up. |
| F3 | HIGH | Sigma is the only side state ("codes + sigma 115,008 B", cost_audit.py:7,76-78) | Read build() (ladder.py:111-132; frozen build_representation:639-657): mu centering on both doc AND query path; checked cost_audit sums payload+sigma only | mu (k floats/archive, same size as sigma: 7,680 B f64 total at k=96) is load-bearing for ALL arms incl sym/asym yet counted nowhere. Adds +0.86/1.72/3.43 B/doc. MED medians (same size) disclosed only at worker level, never in headline. |
| F4 | HIGH | One byte label per k ("12 B" covers sym/qscale/asym/MED/ITQ/RAND) | Read all scorers (ladder.py:147-153; t3:62-68; quant_math.py:464-518: MED thr, ITQ/R fits) vs LADDER.json bytes_per_doc + quant_math.py:517 assert | Label is scorer-blind. Same "12 B" needs: sym mu+encoder; qscale +sigma; MED +96 medians; ITQ/RAND +96x96 R (36,864 f32 / 73,728 f64 per archive). The 3 pp qscale-over-sym gain and T3 asym-over-qscale inversion (61.09 vs 54.11 at "48 B") are bought with uncharged state. |
| F5 | HIGH | Mixed float precisions across the cost story (sigma f64, R f32-quoted, float arms f32) | Compared cost_audit.py:77 (10*96*8) vs REPORT:136-137 (3.43x/7.50x = f32, unstated; worker quant/REPORT:118-122 gives f32 AND f64) vs ladder.py:243 (4k) vs cache dtype float64 (probe: C (662,96) float64) | Main REPORT quotes the smaller f32 rotation multiple silently (f64 doubles it: 6.87x/15x). No test shows f32 sigma/R/mu reproduce the 0.0000pp anchors (floor 1e-12 lives in a regime f32 rounding can disturb). Precision boundary is UNVERIFIED. |
| F6 | MED | BM25 rival cost 670,511 B compact / 1,450,229 B pickle (cost_audit; REPORT sec 4) | Re-ran cost_audit encoding exactly (P3): reproduced coarse 670,511 / 1,450,229 / 998,654 to the byte; added frozen-tokenizer variant (the 65.67 fair baseline) | Fair (frozen) BM25 index is SMALLER: 519,740 B compact (-22.5%), pickle 1,097,138. Rival is stronger AND cheaper than presented. Narrow ratio vs fair rival is 4.52x, not 5.83x. LME cites Python-object IDF (351 MB) after rejecting pickle inflation on RealTalk: inconsistent scope. |
| F7 | MED | "Fidelity gate: 0 differing bits of 858,624" (LADDER_REALTALK.md:5-7); "0 of 276,480" (T3) | Read gate blocks (ladder.py:194-200; t3:125-128); verified 858,624 = 8944*96 in P4; checked Q96 built-but-uncompared | Gate seals ONLY (C96>=0)==(cached C>=0) at k=96 (T3: only n<384 subset). No QC, no sigma/mu, no scores, no k=192/384. Proves rebuild fidelity of doc bits, nothing about size or high-k validity. |
| F8 | LOW (clean, verified) | Hunt for per-doc scalars, float-residual scoring, ID/length/order leaks | Grep + reads: sigma axis=0 per-archive (ladder.py:150-151; quant_math.py:161-162); doc side +-1 only (arm_decision.py:27-32; ladder.py:147-152); det_top10 hash(archive,row) (audit_baseline_lib.py:79-83); lens unused on code path; PQ codebook properly charged (pq/REPORT:55-57) | No per-document sigma/norm/scale beyond bits. No doc-float residual in bit-arm scores (sigma/mu are float-DERIVED per-archive state, noted, not per-doc). No ID/length/order relevance leak. PQ's 98,304 B shared codebook (~22.99 B/doc amortized) is the package's one honest per-arm total. |

Sampling statement (read first): P3 BM25 and P4 arithmetic are EXHAUSTIVE (all 10 RT archives;
both tokenizers; pure-JSON gate math). P1 is a SAMPLE: full SVD rebuild of ONE archive (RT05,
smallest, 410 docs) at k=96/192/384. P2 covers all 10 archives but analytically (vectorizer +
LSA fit only; SVD-k bytes as k*D*4, not serialized). Encoder conclusions rest on P1 (sample) +
P2 (all-archive D dims); per-archive full per-doc figures are lower bounds (f32 matrices, f64
idf, raw term bytes; no pickle/object overhead, no row->id strings). Round-1 explicitly left
cost_audit unreviewed (HARD_AUDIT_NUMBERS.md:88 "cost_audit ... NOT RUN"), so this is new ground,
not a repeat.

## 3. Per-finding detail (paths, lines, commands)

### F1 — headline bytes count bits only (CRITICAL)

Where the claim lives:
- `/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10/research_top10_comparison_2026_09_16/coordinator/ladder.py:24-25`:
  "HONEST BYTE ACCOUNTING (the whole point): sign coding costs k/8 bytes per document.
  k=96 -> 12 B k=192 -> 24 B k=384 -> 48 B".
- Same file `:243-244`: `b = k/8 if sc != "float" else 4*k` -> `bytes_per_doc` in LADDER.json.
- `/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10/research_top10_comparison_2026_09_16/coordinator/LADDER.json:11,18,29,36,47,54`:
  12.0/24.0/48.0 for sym AND qscale alike; float 384/768/1536.
- `/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10/research_top10_comparison_2026_09_16/REPORT.md:21-27` table
  ("qscale (our 12-byte code) ... 12 B/doc", "sign96 ... 12 B/doc", "PQ ... 12 B/doc").
- `LADDER_REALTALK.md:11-15` ladder table (bytes/doc 12/24/48); `DECISION_TESTS.md:28-32`
  ("12 B qscale", "24 B qscale", "48 B qscale" vs BM25 gaps).

What the scorers actually need (same files):
- `ladder.py:147-153` (`score_arms`): `B=sign(C)`, `sym=QB@B.T` (bits only),
  `sigma=C.std(axis=0)` floored 1e-12, `qscale=(QC/sigma)@B.T` (needs sigma),
  `float=cosine` (needs full floats). `t3_perltqa_kltn.py:62-68` adds `asym=QC@B.T`
  (needs QC float, no sigma). `arm_decision.py:27-32`: identical three arms,
  `qscale=B@(q/sg)` with `sg=std(C,axis=0)`.
- `ladder.py:111-132` (`build`): `mu=Y.mean(axis=0)`; `C=Y-mu`, `QC=QY-mu`. QC
  (hence every arm, incl sym) is unreproducible without mu + the full upstream
  encoder (vectorizers, LSA SVD, SVD-k). The byte field charges none of it.

Exact narrow correction (P4, pure arithmetic, exhaustive):
- 8944 docs verified from source JSON (command below): payload 96/192/384 =
  107,328 / 214,656 / 429,312 B. Sigma f64 = 10*k*8 = 7,680 / 15,360 / 30,720 B.
- Totals packed+sigma: 115,008 / 230,016 / 460,032 B = **12.86 / 25.72 / 51.43 B/doc**.
  With mu (same shape, required): 122,688 / 245,376 / 490,752 = **13.72 / 27.43 / 54.87**.
- Commands (all read-only; outputs in this dir):
  `python3 -c "import json; ..."` doc/text count per archive (RT01 662 ... RT10 1256;
  total 8944; payload 107,328; sigma 7,680; total 115,008) — reproduced §F6 P3 run.
  `python3 P4_gate.py` -> `P4_gate.json` (this dir): gate 858,624 == 8944*96 TRUE;
  narrow/with-mu tables above.

### F2 — the encoder dwarfs everything; symmetric accounting reverses the result (CRITICAL)

What must be stored/transmitted to reproduce qscale/sym/asym accuracy on a NEW query:
per-archive (fit unsupervised on archive docs only, but fit per archive — no global encoder
exists in this codebase): word TF-IDF vectorizer (vocab+idf), char TF-IDF vectorizer
(vocab+idf), LSA TruncatedSVD d~=32 (components d x Vw), SVD-k (components k x D,
D=d+Vw+Vc), mu (k), sigma (k; qscale/MED only), R (k x k; rotated arms only), medians
(k; MED only); per-document: packed bits (k/8). Evidence:
- Frozen family: `drive/v52_t4d_locomo_frozen_cross_benchmark.py:196-216`
  (`fit_archive_representation`: per-archive wv/cv/svd fits) and `:639-657`
  (`build_representation`: Z=hstack, s96=TruncatedSVD(96), mu, C, QC=QY-mu).
- Ladder rebuild: `coordinator/ladder.py:111-132` (same per-archive recipe; `kk=min(k,...)`).
- Cache proves f64 pipeline: production `bench3/runs/b3a_realtalk/rt_repr/RT01.pkl`
  keys `C/QC/qids/questions/gold_rows/...`; `C (662,96) float64 508,416 B`,
  `QC (85,96) float64` (probe command in §F6 box). Deployed bits would be 7,944 B for
  that archive; the cache itself stores 64x that in C alone.

Measured sizes (READ-ONLY; scripts + JSON in this dir only):
- P1 full rebuild RT05 (410 docs) via `~/muse-work/ml-python P1_pipeline_sizes.py` ->
  `P1_pipeline_sizes.json`: at k=96, s96 components f32 12,376,320 B vs packed 4,920 B
  (2516x); k=192: 24,752,640 vs 9,840; k=384: 49,505,280 vs 19,680. sv (LSA) f32
  1,256,960 B; mu+sigma f64 1,536 B; R f32 36,864 B; word_terms_utf8 117,803,
  char_terms_utf8 96,280 (RT05 row).
- P2 all-archive dims via `~/muse-work/ml-python P2_vocab_dims.py` -> `P2_vocab_dims.json`
  (vectorizer+LSA fit; SVD-k analytic): s96 f32 k=96 per archive 8.99M-12.77M;
  total s96 f32 110,506,752 B; sv f32 11,524,608 B; matrices alone 122,031,360 B =
  **1137x packed payload** (107,328 B). Amortized s96 alone: 6,296-30,186 B/doc
  across archives (large RT06 6.3 KB/doc ... small RT05 30.2 KB/doc).
- Full lower bound (f32 matrices + f64 idf + raw term bytes + mu/sigma f64 + packed;
  excludes pickle/object overhead, excludes row->id strings):
  **126,289,042 B total, 14,119.97 B/doc mean** at k=96 (range 7,223 RT06 ... 34,418 RT05);
  k=192: 236,795,794 (26,475/doc); k=384: 457,809,298 (51,186/doc).
- BM25 from actual corpora (P3, exhaustive): coarse compact 670,511 (74.97/doc);
  frozen-fair compact 519,740 (58.11/doc); coarse+text 1,669,165 (186.62/doc).
- Symmetric ratios (full lower bound vs rival): **188x vs coarse index**
  (126,289,042/670,511), **243x vs fair frozen index**, **76x vs coarse index+text**.
  The published 5.83x win (670,511/115,008) inverts. Even doc-side-only with mu
  (122,688) vs fair index gives 4.24x for BM25 — the "win" shrinks before the encoder.
- The package was warned: `pq/REPORT.md:58-61`: "Equal 12-byte document payload does NOT
  imply equal total memory; the shared codebook is charged separately above and SIGN96 has
  its own separate shared state. Original SVD encoder/projector ... is missing from the old
  cache: NOT MEASURED, not zero." No follow-up measurement exists anywhere in the package
  (searched: no file under coordinator/ quantifies wv/cv/svd/s96 bytes). This audit is the
  first measurement, and it is a lower bound (f32; f64 doubles matrices to ~244 MB).

Why this is CRITICAL not pedantry: the programme's comparative claim is explicitly a storage
claim ("honest cost accounting", "5.83x", "76x/112x" on LME). A storage comparison with the
encoder on one side excluded is not honest, and the omitted term is 3 orders of magnitude
larger than the charged term. Dense-retrieval papers may conventionally quote vector bytes,
but they do not then ratio them against an index that INCLUDES its query-time state. Note the
STOP verdict itself does not depend on storage (codes already lose on accuracy); what is wrong
is every sentence presenting codes as the compact alternative.

### F3 — mu: same size as sigma, load-bearing, counted nowhere (HIGH)

- `ladder.py:125-132`: `mu=Y.mean(axis=0,keepdims=True)`; return `(Y-mu),(QY-mu)`.
  Frozen `:648-649,657`: identical. Every arm's query path subtracts the DOCUMENT mean.
- `cost_audit.py:76-78`: `code_payload=n_docs*12; sigma=10*96*8; code_total=payload+sigma`.
  mu absent. `FINAL_STATE.md:79-83` and `REPORT.md:216-219` cost tables: "codes + sigma
  115,008 B" — no mu row. 115,008 = 107,328 + 7,680 exactly (verified), so mu=0 in the total.
- Cost of mu: 10 archives x k x 8 B = 7,680 (k=96) / 15,360 / 30,720 B f64 — identical to
  sigma. True doc-side totals with mu: §F1 box. MED medians are the same object class
  (96 floats/archive; worker quant/REPORT:123-124: "384 / 768 B per archive" f32/f64) and are
  likewise absent from every headline byte label (quant_math.py:509-513 fits med; :517 asserts
  12 B for MED too).

### F4 — scorer-blind byte labels (HIGH)

- `LADDER.json`: k96/sym, k96/qscale share 12.0; k384/sym,qscale share 48.0 (full JSON §P4).
  `quant_math.py:515-517`: FULL/ITQ_C/RAND_x3/MED all assert `packed.shape==(N,12)` as the
  payload proof — R (96x96), medians (96), sigma (96) never enter the "payload" check.
- Consequence 1: the flagship 49.65 (qscale) vs 46.52 (sym) gap at "12 B" (+3.13 pp) is the
  price of sigma + float query path, not of bytes. Consequence 2: T3's best arm is asym at
  384 (61.09 FR@3) vs qscale 54.11 (T3 table, DECISION_TESTS.md:79-87) — same "48 B", 7 pp
  apart, different uncharged state (asym skips sigma; needs mu+encoder regardless).
- The package already retracted this error class once for the EXTERNAL ladder
  ("Dimensions are not bytes ... cannot be rewritten as 48 bytes without the sign-coded arm",
  EXTERNAL_AUDIT3_RESPONSE.md:215-226, esp. :219-223) and specified the fix ("sign=k/8;
  float=4k; plus unprojected controls", :252-258) — but applied it only as
  packed-bits-vs-float-payload, not as side-state-inclusive bytes. The retraction's logic
  convicts the project's own table.

### F5 — precision shell game: f64 costs, f32 multiples (HIGH)

- Sigma: f64 everywhere costs are summed (`cost_audit.py:77`: `10*96*8`; caches float64,
  probe §F2). R: main REPORT (`REPORT.md:136-137`) quotes "96x96 floats: 3.43x (RealTalk)
  and 7.50x (PerLTQA)" with NO precision; worker (`math_r1/quant/REPORT.md:118-122`) shows
  36,864 f32 / 73,728 f64 per archive -> 3.4x/6.9x RT, 7.5x/15x PerLTQA. Main text prints the
  smaller of each pair silently (verified arithmetic §P-probe: 10*96*96*4/107328=3.4347;
  f64=6.8694; PerLTQA f32=7.5 exact on 12,288 docs). Float arms: `ladder.py:243` charges 4k
  (f32) while accuracy was produced AND gated in f64 (cache probe; gate max_abs ~1e-13 scale
  in ladder.py:200/T3:127-128 context).
- Why it matters: qscale's floor (`sigma<1e-12 -> 1e-12`) and the tiny-sigma high-k regime
  (the programme's own collapse story) are exactly where f32 rounding bites. No
  f32-sensitivity run exists (searched: no "float32" rerun of ladder/qscale anchors). Whether
  the 0.0000pp anchors survive the cheaper precision is UNVERIFIED — the cheaper numbers are
  quoted against the dearer measurements.

### F6 — the rival is cheaper than quoted, and LME scope is inconsistent (MED)

- Reproduction (exhaustive, this dir): `python3 P3_bm25.py` -> `P3_bm25.json`. Per-archive
  coarse vocab/compact (RT01 2462/64,558 ... RT10 2576/73,203) sum to compact **670,511**,
  pickle **1,450,229**, raw **998,654**, compact+text **1,669,165** — all EXACT vs
  cost_audit CLAIM (payload/pickle/raw to the byte; pickle within 2% tolerance rule,
  here exact). Method: term bytes + 1 + varint(df) + f32 idf + delta-gap varint rows +
  varint tf + varint doc_lens + 8 (cost_audit.py:60-69, mirrored in P3).
- New (fair-rival) variant in the same run: frozen tokenizer (stopwords removed,
  `\b\w\w+\b` — the 65.67 Hit@10 baseline, DECISION_TESTS.md:19-24; ladder.py:64,74-77):
  compact **519,740** (-22.5%), pickle 1,097,138, +text 1,518,394. The accuracy tables
  compare against frozen BM25 while the storage tables charge coarse BM25. Narrow ratio vs
  the actually-compared rival: 519,740/115,008 = **4.52x** (4.24x with mu), not 5.83x.
- LME: REPORT.md:256-257 cites incoming-package memory (packed+sigma 3.14 MB; text 237.87;
  IDF dict OBJECTS 351.18 MB; 76x/112x) while EXTERNAL_AUDIT3_RESPONSE.md:124-134 carries the
  serialized-scope table (LME index 213.29 MB int32+f32 postings+vocab+idf; 0.90x text) and
  :242-244 explicitly warns the ~64 MB JSON vs 213 MB postings are different scopes "rather
  than compared directly". Quoting 351 MB Python objects as the BM25 side repeats, on LME,
  the pickle-inflation error the coordinator correctly rejected on RealTalk
  (FINAL_STATE:85; REPORT:217-219; cost_audit note). LME 3.14 MB itself is the same narrow
  packed+sigma boundary (encoder uncharged) — UNRECOMPUTED here (external method; see §4).

### F7 — what the 858,624-bit gate actually seals (MED)

- LADDER_REALTALK.md:5-7: "Fidelity gate: 0 differing bits of 858,624. Anchors exact:
  k96 qscale 49.6454 ... k96 sym 46.5248 ...". LADDER.json gate: {differing_bits:0,
  n_bits:858624} (P4 readout).
- Code: ladder.py:194-200 builds `(C96,Q96,_)=build(texts,questions,96)`, loads
  `CACHE/{aid}.pkl ["C"]`, records `nd=count((C96>=0)!=(Cc>=0))`, `n_bits=C96.size`,
  `max_abs`. Q96 is DISCARDED: no QC-vs-cache comparison exists in ladder.py (contrast
  quant_math.py:250-280 G1 which checks C AND QC signs + maxabs + G2 metric replay).
- P4 verifies 858,624 = 8944 x 96 exactly: the gate counts every RealTalk doc bit at k=96
  once, and nothing else. T3 "0 of 276,480" (T3 JSON gate {diff:0,bits:276480};
  DECISION_TESTS.md:73) is the same check restricted to the n<384 subset
  (t3:76-80,125-128: gate only `if k==96`, only `(C>=0)!=(Cc>=0)`).
- What it does NOT seal: stored SIZE (bit-equality holds for any container), sigma/mu
  values, query-path fidelity (QC unchecked), scores/metrics (no replay in ladder gate),
  k=192/384 arms (no cache reference; brand-new SVDs), or the byte label. It is a
  same-pipeline rebuild check of doc signs at one rung — valuable against
  reimplementation drift, routinely misreadable as "the 12/24/48 B ladder is verified".
  The ladder's high rungs, where the headline gain lives (+5.67/+2.55), run unsealed.

### F8 — hunted side channels that came back clean (LOW)

- Per-document sigma/norm/scale/offset/mean: NONE. sigma is `C.std(axis=0)` (per-archive
  per-dim; ladder.py:150-151; quant_math.py:161-162 `sigma_docs`; arm_decision.py:29).
  mu is `Y.mean(axis=0)` (per-archive; ladder.py:125-131). R is per-archive 96x96
  (quant_math.py:140-158 fit on DOCUMENTS ONLY; REPORT:136-137). Medians per-archive
  (quant_math.py:506-513). No per-doc float accompanies the bits in any bit-arm.
- Float residuals in scoring: doc side is +-1 only in sym/qscale/asym
  (arm_decision.py:27-32 `B=decode_pm1(pack(C>=0))`; ladder.py:147-152; t3:62-68).
  Floats DO enter via per-archive statistics (sigma/mu from C) and the live query vector
  (QC/sigma, QC) — a per-archive float-derived side channel, not a per-doc residual. Float
  reference arms (4k B) use full C/QC cosine (ladder.py:153) — honestly labelled as
  uncompressed references, subject to the f32/f64 caveat (F5).
- IDs/lengths/ordering: `audit_baseline_lib.py:79-83` det_top10 = score DESC, then
  SHA256("top10-r1|archive|row"), then row. Tie-break is content- and gold-blind (row index
  only); doc_lens exist in BM25 blobs (cost_audit.py:53-58) but the code path never reads
  lens (ladder.py:111-154; quant_math.py:464-518); storage order is row order, ranking is
  score order; expected-hit metrics account for ties (audit_baseline_lib.py:98-119).
  Gold rows/qids/texts in caches and PQ npz files (pq/REPORT:101-106) are eval artifacts,
  not retrieval state. Row->id maps (~N short strings/archive) are needed by BOTH sides at
  serve time; negligible (~90 KB total) and symmetric — noted for completeness, not charged.
- The one honest total: PQ's shared codebook 98,304 B f32 (12,256,8) amortized ~10.99/doc
  -> ~22.99 B/doc effective (pq/REPORT:55-57; run_pq.py:228-231 asserts nbytes). PQ trained
  ONCE GLOBALLY (pq/REPORT:21-23; run_pq.py:186-226) while sign projections are PER-ARCHIVE
  (10x/30x replication) — the disclosed PQ overhead is smaller AND shared, yet disclosed;
  the larger sign overhead is neither shared nor disclosed. Credit to the PQ worker; the
  asymmetry is the finding.

## 4. What you could NOT check and why

1. PerLTQA / LoCoMo / LME encoder sizes: SAMPLED, not exhaustive. Full rebuilds measured on
   RealTalk only (P1: RT05 x k=96/192/384; P2: all 10 RT archives' D dims). Other benchmarks'
   true per-doc deployed costs are UNVERIFIED; their narrow packed+sigma figures inherit the
   same structural omission (per-archive encoder + mu) by code inspection (same frozen recipe:
   pq_build/fit paths in quant_math.py:385-400; t3:115-124), but I did not re-derive their
   megabyte totals. Need: rerun P1/P2 recipe against PerLTQA/LoCoMo/LME caches.
2. f32 fidelity: UNVERIFIED. No f32 rerun of qscale/sym anchors exists; whether sigma/mu/R
   at f32 (or int8) preserve Hit@10 to 0.0000pp — especially the 1e-12-floored tiny-sigma
   dims — needs a dedicated sensitivity run (rebuild + rescore at f32, report deltas + CIs).
3. A shared/global encoder alternative: UNVERIFIED by design. All measured accuracy uses
   per-archive fits; a global projection would be a NEW method with its own (unmeasured)
   accuracy. Cannot be assumed to rescue the ratio.
4. LME 3.14 / 237.87 / 351.18 MB: NOT re-derived (external incoming package's method;
   IDEAS_AUDIT.md:89-90,322,423-429). Quoted here only to flag scope inconsistency (Python
   objects vs serialized). Need: the incoming authors' scripts + LME cache manifest.
5. k=768 rung, NOPROJ arms, LoCoMo gold dispute (1531 vs 1535), rerank latency/energy:
   out of byte-role scope; k=768 was dropped on record (ladder.py:56-62); gold dispute is
   already-known (do-not-re-report list) and untouched by byte accounting either way.
6. Serving-time row->id maps, stopword lists, tokenizer code: acknowledged, negligible,
   symmetric; not byte-counted on either side. No finding rests on them.

## 5. Corrected size-vs-accuracy table (RealTalk, n=705 queries / 8944 docs)

Hit@10 / FR@3 from LADDER.json (qscale/sym) and DECISION_TESTS.md T1 (fair BM25 65.67).
"Headline" = published bytes_per_doc. "Narrow+sigma" = report's own boundary, corrected.
"+mu" = minimal reproducible doc-side (mu required for QC). "Deployed lower bound" = +mu +
per-archive encoder (s96 f32 + LSA f32 + f64 idf + raw term bytes); per-doc mean over corpus
(range across archives in notes). BM25 compact recomputed from actual corpora (P3, exact).

| system | Hit@10 | FR@3 | headline B/doc | narrow+sigma total / B/doc | +mu B/doc | deployed lower bound B/doc |
|---|---:|---:|---:|---:|---:|---:|
| qscale k=96 ("12 B") | 49.65 | 22.41 | 12 | 115,008 / **12.86** | **13.72** | **~14,120** (7,223-34,418) |
| qscale k=192 ("24 B") | 55.32 | 29.75 | 24 | 230,016 / **25.72** | **27.43** | **~26,475** |
| qscale k=384 ("48 B") | 57.87 | 32.79 | 48 | 460,032 / **51.43** | **54.87** | **~51,186** |
| sym k=96 | 46.52 | 22.87 | 12 | 12.86 (needs mu not sigma: 12.86 w/ mu 13.72*) | 13.72 | ~14,120 |
| sym k=384 | 54.18 | 31.48 | 48 | 51.43 | 54.87 | ~51,186 |
| float k=96 (ref) | 36.60 | 17.25 | 384 (f32 claim) | 768 f64 equiv | — | — |
| BM25 coarse (quoted rival) | 55.32 | 33.91 | — | index 670,511 / 74.97/doc; +text 186.62/doc | — | — |
| BM25 frozen IDF-only (fair rival) | **65.67** | **40.02** | — | index **519,740** / **58.11**/doc; +text 169.78/doc | — | — |

*sym needs mu+encoder but not sigma; table shows same narrow column for comparability —
byte label cannot distinguish scorers (F4). Deployed column is a LOWER bound at f32
matrices; f64 doubles it (~28 KB/doc at k=96). PQ at "12 B" is honestly ~22.99/doc
(payload 12 + shared codebook ~10.99; pq/REPORT:55-57) — and still needs the same
unmeasured encoder (flagged NOT MEASURED, pq/REPORT:60-61).

Reading the table: the accuracy gap the STOP verdict rests on (48 B qscale 57.87 vs fair
BM25 65.67, -7.80 pp) is urgency-independent of storage. The storage story told alongside
it (codes 5.83x smaller) holds ONLY inside the narrow packed+sigma boundary against the
coarse rival (670,511/115,008); vs the compared fair rival it is 4.52x (4.24x with mu);
vs symmetric deployed reality it is ~1/188. If a text-free/index-free deployment ever
reopens the programme (FINAL_STATE's one reopen condition), its budget must be the deployed
column, at which point NOTHING about "12 bytes" transfers.

## 6. How to reproduce (read-only; do not run project scripts in place)

All probes live in `/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/bytes/` and write ONLY
there (source trees untouched; no project file executed in place except read-only imports):
- `P1_pipeline_sizes.py` (run: `PYTHONDONTWRITEBYTECODE=1 ~/muse-work/ml-python
  P1_pipeline_sizes.py`) -> `P1_pipeline_sizes.json` (RT05 k=96/192/384 full component bytes).
- `P2_vocab_dims.py` (same runner) -> `P2_vocab_dims.json` (all 10 archives Vw/Vc/D, analytic
  s96/sv bytes). Pure fit, no serialization of project state.
- `P3_bm25.py` (`python3 P3_bm25.py`) -> `P3_bm25.json` (both tokenizers; exact
  670,511/1,450,229/998,654 reproduction + frozen 519,740/1,097,138).
- `P4_gate.py` (`python3 P4_gate.py`) -> `P4_gate.json` (858,624=8944x96; narrow/with-mu tables).
- Shell checks: `sed -n` gate blocks (ladder.py:194-200; t3:125-128); `grep -n` byte claims
  (ladder.py:24-25,243; REPORT:21-27,136-137; FINAL_STATE:79-85; EXTERNAL:215-226);
  cache probe (`python3 -c pickle.load RT01.pkl`: keys, C (662,96) float64 508,416 B).
- `python3` here is the system interpreter (no sklearn); `~/muse-work/ml-python` is the
  wrapper named in the task brief. No network used. Heavy-SVD exposure limited to RT05
  (P1); RT06-k768-scale rebuilds deliberately NOT attempted (ladder.py:56-62 timeout note).
