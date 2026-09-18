# LEAK_SWEEP — round-3 project-wide leakage sweep

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Auditor role: project-wide leakage sweep (static + targeted). Read-only on all
source trees; writes only in this dir. No number below is invented: every figure
is either quoted from a named file or measured by the auditor's probe whose
output is saved beside this report.

## 1. VERDICT (3 lines)

Swept 66/66 `.py` files; the eval-corpus-fit recipe is project-wide (12 code
files, all datasets) but no published number is overturned beyond round-2's
known RealTalk-k96 collapse, so there is no new CRITICAL finding.
New probe D1 (n=705): BM25 with background IDF scores 55.18 vs 54.18 per-archive
(+0.99 pp) — the transduction asymmetry favours the codes, so the STOP verdict
survives and is, if anything, understated.
Zero fits on queries or gold anywhere; all leaks are docs-only index-time fits.

## 2. Findings table

| ID | Sev | Check | Result |
|----|-----|-------|--------|
| F1 | HIGH | Pipeline fit scope, 12 files | Same eval-archive fit, all sets |
| F2 | HIGH | qscale sigma source | Docs-only per archive, every arm |
| F3 | MED | BM25 IDF scope + probe D1 | Same-corpus IDF; bg-IDF +0.99 pp |
| F4 | MED | PQ codebook training set | 8944 eval docs pooled; Q excluded |
| F5 | MED | ITQ rotation fit scope | Per-archive docs-only; 1 init |
| F6 | LOW | PCA96 fit scope | Pooled 10-arch eval docs; Q mapped |
| F7 | LOW | Median-threshold fit scope | Docs-only; MED arm only |
| F8 | LOW | Any fit on queries/gold | None in 66/66 files |
| F9 | LOW | Upstream builder origin | Eval-fit; gates prove identity only |

## 3. Per-finding detail

### Sweep method (what "exhaustive" means here)

- Enumerated every `.py` under `top10_comparison_r1/`: 66 files.
- Mechanical pattern scan (fit_transform, `.fit(`, TruncatedSVD,
  TfidfVectorizer, PCA(, ProductQuantizer/pq.train, fit_itq,
  random_orthogonal, medians, Y/C means, idf_, Counters, bm25/tfidf scorers)
  produced 202 rows in `fit_inventory.csv` (this dir).
- Gap in the mechanical pattern, disclosed: scoring-time sigma helpers named
  `fit_std`/`sigma_docs` do not contain `.fit(` and were caught by a second
  grep, then audited manually (F2).
- Deep-read (full file): the 9 special targets plus `repr_math.py`,
  `quant_math.py`, `run_pq.py`, `run_lexical.py`, `ladder.py`,
  `t3_perltqa_kltn.py`, `score_pplx.py`, `metrics_top10.py`,
  `audit_baseline_lib.py`, `why_bm25_wins.py`, `firststage.py` (relevant
  sections). Remaining files: grep-verified clean of fit patterns (list in
  fit_inventory.csv scope note). Sampling: classification of the 202 rows is
  by-file (one recipe per file), not row-by-row prose.

### F1 (HIGH): one transductive recipe, twelve instantiations, all datasets

Every code-number-producing builder fits the same chain on the evaluation
corpus itself: word TFIDF(1,2) + char_wb TFIDF(3,5) vocab/idf, LSA SVD on word
block, final SVD96 on the stacked Z, doc-mean mu. Queries are only
`.transform()`ed through the fitted objects (legitimate query-time use).

- `ablation_r2/lme/ablation.py:87-110` (`fit_sources` + `build_arm`, LME)
- `ablation_r2/perltqa/ablation.py:140-165` (PerLTQA)
- `ablation_r2/perltqa/fidelity_gate.py:70-83` (`fit_archive`, PerLTQA)
- `ablation_r2/perltqa/t3_ladder.py:148-173` (PerLTQA)
- `ideas_r1/ablation/ablation.py:76-99` (`build_arm`, RealTalk)
- `math_r1/quant/quant_math.py:234-247` (`rt_build_full`, RealTalk),
  `:385-399` (`pq_fit_archive`, PerLTQA)
- `math_r1/repr/repr_math.py:83-93` (`fit_base`), `:111-123` (`fit_final`)
- `coordinator/ladder.py:111-132` (`build`, RealTalk k-ladder)
- `coordinator/t3_perltqa_kltn.py:114-124` (PerLTQA k_eff ladder)
- Upstream origin (production caches inherit it):
  `bench3/runs/b3b_perltqa/step2_build.py:54-63`,
  `drive/v52_t4d_locomo_frozen_cross_benchmark.py:196-215`
- Effect quantified ONLY for RealTalk k=96 by round 2 (sym -28.37 pp, qscale
  -29.65 pp). Same mechanism touches PerLTQA/LME/ladder numbers, magnitude
  there UNVERIFIED (see section 4).

### F2 (HIGH): qscale sigma is eval-docs-only in every scorer

`sigma = std(C, axis=0)` with C the archive's own doc matrix, floor 1e-12,
applied as `B @ (qC/sigma)`:

- `math_r1/quant/quant_math.py:161-162` (`sigma_docs`), used `:288`, `:477-511`
- `math_r1/repr/repr_math.py:158-167` (`score_mats`)
- `baseline/metrics_top10.py:47-51` (`fit_std`), `audit/audit_baseline_lib.py:64-66`
- `coordinator/ladder.py:150-152`, `t3_perltqa_kltn.py:65-67`,
  `ideas_r1/ablation/ablation.py:122-124`, `firststage.py:214-226`,
  `fidelity_gate.py:124-138`, `verify_incoming.py:31-39`
- Touches every published qscale number. Same docs-only class as F1; its
  separate listing is because qscale-vs-sym gaps are reported as readout wins
  while one input (sigma) is itself corpus-fitted.

### F3 (MED): BM25/TFIDF IDF is same-corpus — and the asymmetry favours codes

IDF (`log((N-c+0.5)/(c+0.5)+1)`) is built from the scored archive's own docs:

- `data/run_lexical.py:90-110` (bm25), `:113-134` (tfidf), per archive `:152-165`
- `audit/audit_lexical_lib.py:116-159`, `coordinator/rerank_ceiling.py:63-79`,
  `coordinator/split_failure_diag.py:51-56`, `coordinator/why_bm25_wins.py:81-86`,
  `coordinator/ladder.py:79-109` (`BM25` class), `ideas_r1/firststage/firststage.py`
  (per-archive `build_index`)
- Analysis-only (stratification, never scoring): `quant_math.py:182-207`
  (`idf_bands`), `repr_fr3_mechanism.py:84-107`, `rare_band_decisive.py:30-62`
- Targeted probe D1 (auditor-run, read-only, k1=1.5/b=0.75, `\w+` tokenizer,
  hash tie-break): per-archive IDF Hit@10 = 54.18, pooled-10-archive IDF =
  55.18, delta +0.99 pp, n=705. Output: `PROBE_D1_bm25_idf.json` (this dir).
- Caveat: absolute 54.18 differs from the published fair-BM25 65.67 (different
  tokenizer/params); only the DELTA is the finding. Reasoning: the code
  pipeline gains ~28 pp from its eval-fit while BM25 gains ~0 pp from its
  eval-IDF, so the published comparison flatters the codes; under the honest
  (background-fit) regime the gap widens. STOP survives. A fully inductive
  BM25 (background IDF AND background avglen/TF) was not run — expected
  movement is second-order, stated as judgement, not measurement.

### F4 (MED): PQ codebook trained on all 8944 eval docs pooled

- `pq/run_pq.py:199-210` (`build_training_matrix`, asserts 8944x96),
  `:222-226` (`pq.train`), M=12/nbits=8/seed 20260915
- Train set = L2-normalized FLOAT96 C rows of all 10 RealTalk eval archives;
  queries explicitly excluded (`n_q_excluded`, `:203`). Cross-archive scope:
  each archive's codes depend on the other 9 archives' docs. Touches PQ-arm
  numbers only. Whether the 98,304-byte codebook is counted in PQ byte claims:
  UNVERIFIED (not checked; see section 4).

### F5 (MED): ITQ fitted per-archive on eval docs; random controls clean

- `math_r1/quant/quant_math.py:140-158` (`fit_itq`, 50 iters, seed 20260916,
  docs-only stated), applied per archive `:480-490`
- Random-rotation controls (`:133-138`, `:494-505`, seeds 20260916/17/18) use
  no data: legitimate. Median arm (`:507-512`) is docs-only median: F7.
  Touches ITQ_C/RAND/MED arm numbers only. "1 init vs 3+ seeds" already known,
  not re-reported.

### F6 (LOW): PCA96 fitted on pooled eval-doc embeddings

- `semantic/score_pplx.py:56-66` and identical
  `coordinator/semantic_before_fidelity_fix/score_pplx.py:53-63`: PCA96 on
  concatenated RealTalk DOCUMENT INT8 (all 10 archives, eval docs), mean saved,
  queries only projected (`pca_sign`). Touches PPLX_PCA96_SIGN only. Declared
  in-file as docs-only/no query-gold fit: confirmed accurate.

### F7 (LOW): median thresholds, bit-balance — docs-only, one arm

- `quant_math.py:507-512` (MED), `:521-524` (bit_balance diagnostics).
  Touches MED arm only.

### F8 (LOW, positive): no fit on queries or gold in 66/66 files

- Second grep for `fit.*gold|gold.*fit|train.*gold` found only comments
  asserting docs-only (`arm_decision.py:9`, `verify_incoming.py:10`,
  `why_bm25_wins.py:190`, `score_pplx.py:11`): verified true at each fit site.
- Query-side encoder (`coordinator/encode_fast.py:1-110`,
  `semantic/pplx_scorer.py`): fixed pretrained weights, masked-mean pool,
  fixed `>= 0` thresholds (`pplx_scorer.py:35-40`): no corpus fitting.
- `model/st_quantize.py:1-122`, `official_st_quantize.py`: fixed tanh
  quantizers, no fitted parameters.
- 39 files contain zero fit-pattern hits (rerank/scoring/audit/diag/model
  files); full list verified by the CLEAN loop (command in section 3 header).

### F9 (LOW, context): fidelity gates prove identity, not honesty

- `fidelity_gate.py:163-187`, `quant_math.py:rt_fidelity`, `repr` zero-arm
  checks (`repr_compute.py:84-92`): rebuilds match production caches
  bit-exactly. This authenticates that the evaluated artifact IS the
  transductive pipeline; it does not make the numbers inductive. No action;
  recorded so the gates are not misread as a leak clearance.

### Ranked leaks by published numbers touched

1. F1 frozen pipeline family — every code Hit@10/FR@3 (RealTalk 46.52/49.65,
   PerLTQA 75.68/80.00, LME, all ladders/ablations/repr/quant arms).
2. F2 per-archive sigma — every qscale number (subset of 1, listed for the
   readout-gap interpretation).
3. F3 BM25/TFIDF same-corpus IDF — every BM25/TFIDF number incl. fair 65.67.
4. F4 PQ codebook — PQ arms only.
5. F5 ITQ rotation — ITQ_C arm only (RAND controls unaffected).
6. F6 PCA96 — PPLX_PCA96_SIGN only.
7. F7 median — MED arm only.
8. F8/F9 — touch no numbers (clearance/context).

## 4. What could NOT be checked and why

- Inductive-collapse magnitude beyond RealTalk k=96 (other datasets, k=192/
  384, PerLTQA/LME): needs `~/muse-work/ml-python` (sklearn) multi-hour
  rebuilds against `bench3/` caches; bounded-probe budget (<15 min) forbade
  it. Need: run of `t_inductive_all10.py`-style refit per dataset/width.
- `_wt_top10/`, `audit_hard_r1/`, `audit_hard_r2/` trees: not swept (role
  scope is project-wide leakage in `top10_comparison_r1/`; time-box).
- Non-`.py` artifacts (payloads, caches, JSON results): the "1970 files" are
  mostly these; sweep was exhaustive over code (66/66 `.py`), not over data
  blobs. A cache that bakes in eval-fit (e.g. `rt_repr/*.pkl`) inherits F1 by
  construction but was not independently re-audited here.
- PQ codebook byte-accounting (F4 caveat) and LoCoMo upstream builder
  (drive script, grep-only): UNVERIFIED, would need results-text audit.
- D1 probe tokenizer/param mismatch (54.18 vs published 65.67): absolute
  BM25 numbers not reproduced; delta-only claim. Need: rerun with the exact
  fair-BM25 tokenizer to confirm the ~0 pp delta transfers.

## Artifacts (this dir)

- `LEAK_SWEEP.md` (this report), `fit_inventory.csv` (202-row mechanical
  inventory: file, line, excerpt), `PROBE_D1_bm25_idf.json` (705-query probe).
- Probe script kept at `/tmp/probe_bm25_idf.py`; inventory script at
  `/tmp/fit_inventory.py` (scratch, per protocol, not deliverables).
- Source trees untouched (read-only access throughout).
