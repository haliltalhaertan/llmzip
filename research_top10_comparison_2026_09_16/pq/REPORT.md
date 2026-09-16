# PQ12B conventional equal-payload arm — REALTALK705 Top10 r1

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## Outcome

Actual Faiss `ProductQuantizer(d=96, M=12, nbits=8)` comparison on the full
REALTALK corpus against the 12-byte SIGN96 arm. Trained once globally on all
real documents only, L2-normalized FLOAT96 `C`, asymmetric LUT ADC scoring of
original normalized `QC` against unnormalized reconstructions.

Overall on all 705 valid gold queries: Hit@10 0.3305, Recall@10 0.2439,
nDCG@10 0.1734, exact expected Hit@10 under uniform tie-breaking 0.3305
(4/705 cutoff ties; tie-sensitivity negligible). Per-archive Hit@10 varies
widely (RT03 0.603, RT04 0.563, RT05 0.557, RT01 0.424, RT02 0.343,
RT10 0.271, RT09 0.270, RT07 0.143, RT06 0.054, RT08 0.043), so the pooled
mean must not be read as uniform behavior.

## Method (exactly as tasked, no tuning)

- `faiss.omp_set_num_threads(1)`, `ProductQuantizer(96, 12, 8)`,
  `cp.seed=20260915`, `cp.niter=20`. Single global train on 8,944 stacked
  L2-normalized document rows (RT01..RT10 order). No query (`QC`) or gold
  rows in training; 728 query rows excluded by construction.
- Existing FLOAT96 `C`/`QC` (float64, norms C 0.799..1.027, QC 0.724..1.046,
  zero zero-vectors observed) L2-normalized row-wise before train/code/score.
  Zero-norm or nonfinite rows raise `ValueError` and abort (declared before
  running; none observed).
- Each document code is exactly 12 bytes (`(N,12)` uint8, `code_size=12`).
  Codebook `(12,256,8)` float32, actual 98,304 bytes, matches expected
  12*256*8*4. Saved as `centroids.npy`.
- Primary scorer is centroid-LUT ADC with no per-query document
  reconstruction: for query `q`, `LUT[m,k]=||q_m-c_{m,k}||^2`,
  `score=-sum_m LUT[m,code[m]]`. Higher is better. Reconstructions are kept
  unnormalized; normalizing them would silently change L2 ADC and was not done.
- Deterministic Top10: score descending, then ascending
  `SHA256('top10-r1|'+archive_id+'|'+str(row))`, then ascending row. Exactly 10
  IDs even at boundary ties, no gold-aware ordering, no duplicates.
  Nonfinite scores raise instead of ranking.
- Metrics per query: binary Hit@10, Recall@10, nDCG@10 (binary, `1/log2(i+2)`,
  ideal over `min(|gold|,10)`), plus exact expected binary Hit@10 under uniform
  random choice among cutoff-tied docs
  (`1-C(n_tied-gold_tied,slots)/C(n_tied,slots)`, 1 if any gold strictly above
  the cutoff, 0 if none tied).
- No hyperparameter search. No other workers' result scores were read or used
  for tuning. Faiss emitted `please provide at least 9984 training points'
  warnings (8,944 < 9,984; ~35 points/centroid per subspace); training still
  converged and is reported as a limit below.

## Costs — payload vs total (no equal-total claim)

- Counts: 10 archives, 8,944 documents (662/476/453/422/410/1548/1511/1162/
  1044/1256), 728 questions total, 705 valid, 23 original empty-gold
  exclusions preserved, no new exclusions.
- Payload: 12 bytes/doc, 107,328 bytes total.
- Shared codebook: 98,304 bytes actual (expected 98,304), amortized
  ~10.99 bytes/doc, effective amortized ~22.99 bytes/doc.
- Equal 12-byte document payload does NOT imply equal total memory; the shared
  codebook is charged separately above and SIGN96 has its own separate shared
  state. Original SVD encoder/projector that produced the cached FLOAT96 is
  missing from the old cache: NOT MEASURED, not zero.
- Timing (artifact-producing run, WSL CPU): train ~18.0 s, encode-all
  ~47.6 s, query-all (705, LUT ADC) ~41.6 s (~59.0 ms/query), total ~111.7 s.
  An earlier identical-config run took ~9.5/3.3/14.7 s; variance is shared-CPU
  noise, both runs gave identical metrics. Peak process RSS ~76.6 MB
  (`resource.getrusage`, excludes temporary numpy/faiss buffers which were not
  instrumented beyond the codes arrays).
- Repro: `~/muse-work/ml-python run_pq.py` in this directory (faiss 1.15.0,
  numpy 2.5.3, sklearn 1.9.1, python 3.14.4).

## Verification (observed this session)

- TDD RED (`tdd_red.log`): `test_pq_top10.py` collected against missing
  `run_pq` → import error, 1 collection error.
- TDD GREEN (`tdd_green.log`): 9/9 passed after implementation plus a
  corrected hypergeometric expected-Hit (an initial count-based version could
  return values >1 and was fixed; the durable test now pins the combin formula
  with above-cutoff and zero-gold cases).
- Durable suite `test_pq_top10.py` covers: L2 unit/reject, packed 12 B shape,
  pack/unpack roundtrip, LUT-vs-brute force ≤1e-5 on a random fixture,
  training-matrix shape (8,944,96) with all 728 QC rows excluded and first row
  equal to normalized RT01 `C[0]`, determinism/tie-hash/gold-blindness/
  higher-better/nan-reject, multi-gold Hit/Recall/nDCG plus expected-Hit,
  all-705 canonical gold ranges, and `centroids.npy` shape/bytes.
- Runtime cross-checks: per-archive first-valid-query LUT vs full-reconstruction
  brute force max abs diff 1.78e-15 (tolerance 1e-5); pack/unpack byte roundtrip
  per archive; determinism rerun per query; input-SHA binding per archive;
  independent second-path audit (RT06_q000 brute-reconstruction ranking with the
  same tie rule) reproduces the stored LUT Top10 exactly
  `[1095,255,1111,1054,1114,1118,341,414,138,512]`.
- Per-query audit of `per_query.jsonl` (705 lines): every row has exactly 10
  unique rows/IDs/scores, scores nonincreasing, adjacent equal-score pairs
  respect hash order (61 pairs corpus-wide), and every gold list matches the
  source cache `gold_rows`/`qids` exactly.

## Artifacts (this directory only)

- `run_pq.py` — library (normalize, LUT ADC, ranking, metrics) plus pipeline.
- `test_pq_top10.py`, `tdd_red.log`, `tdd_green.log`.
- `centroids.npy` — (12,256,8) float32, 98,304 bytes.
- `RT01_codes.npz` … `RT10_codes.npz` — each `{codes (N,12) uint8, QC_norm,
  QC_orig, qids, gold_rows, qa_valid, row_to_id, input_sha, archive_id,
  source_file, faiss_params}`; input SHAs: RT01 `4afb6d6f…`, RT02 `cb67a8fc…`,
  RT03 `5c04ae97…`, RT04 `d0b5320c…`, RT05 `c0335825…`, RT06 `e690eed7…`,
  RT07 `98650a41…`, RT08 `7c2a49ec…`, RT09 `4689673d…`, RT10 `7ac5333f…`
  (full values in `SUMMARY.json`); adapter SHA `a1dec27c…`.
- `per_query.jsonl` — 705 lines, each `{qid, archive_id, query_index, n_docs,
  gold_rows, gold_ids, top10_rows, top10_ids, top10_scores, hit10, recall10,
  ndcg10, expected_hit10_uniform, category}`. IDs are cached `dia_id` strings
  via `id_to_row` inversion; rows are integer row indices.
- `SUMMARY.json` — params, counts, memory, overall and per-archive metrics,
  verification, timing/RSS, input SHAs, tuning:none.

## Independent protocol-risk audit (from adapter + caches, not from scores)

- Frozen gold semantics (`bench3_realtalk_adapter.py` + frozen T4D path):
  `norm_evidence` regex-extracts `D\d+:\d+` tokens, dedupes preserving order,
  keeps range endpoints only with no expansion; gold keeps only tokens present
  in `id_to_row`; QA valid iff ≥1 resolved; 23 zero-gold QAs excluded from the
  denominator, partial (unresolved-but-valid) QAs retained. Representation fit
  input is archive `message_text` strings only
  (`speaker: clean_text [+ IMAGE: caption]`, no date, no events);
  `events_session_*` never read; questions transformed post-fit. Any
  re-normalization or text-format change would silently shift gold and vectors;
  this run reuses cached rows/SHAs verbatim and asserts all 705 bindings.
- Risks: (a) FLOAT96 carries the frozen TF-IDF+SVD96/seed-5204 pipeline whose
  weights are absent, so end-to-end build cost and any encoder-side bias are
  unmeasured; PQ inherits whatever archive-mean-centering/normalization that
  encoder applied. (b) L2-normalizing before PQ discards norms; correct for a
  cosine-oriented comparison but a different choice (raw-L2 PQ) would rank
  differently — labeled here explicitly. (c) 256 centroids/subspace on 8,944
  training points is below the faiss 9,984-point guideline; rare subpopulations
  may be coarsely coded. (d) Expected-Hit must use the hypergeometric form for
  binary Hit; a count-based version overstates multi-gold tie sensitivity
  (caught and fixed during TDD). (e) Per-archive pools differ 10x in size
  (410..1,548) and Hit@10 varies 0.04..0.60, so cross-archive means are
  exploratory, not certified; protocol's 10 archive-cluster bootstraps are
  limited and no unseen-corpus claim is made. (f) No SIGN96/FLOAT96 FR@3 replay
  gate was re-run in this worker (other workers' scope); comparability rests on
  shared frozen caches/SHAs above, not on a replayed baseline here.
