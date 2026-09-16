# Baseline Top10-r1 REPORT

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Owner: `top10_comparison_r1/baseline` only. No writes outside this directory.
Prior source `parallel_ideas_r1/asymmetric/run.py` read as library reference only;
its write-producing main was never invoked. No paid APIs, no web tools,
no input changes, no git writes. Raw data export and model inference are
NOT owned by this job and were not run.

## Scope

Full cached-representation Top10 for all 9440 queries with no truncation:

- PerLTQA 8265 queries across 30 archives (archive_id = char name).
- LME 470 queries across 470 single-query archives (archive_id = question_id).
- REALTALK 705 valid gold queries across 10 archives (archive_id = conv_id
  RT01..RT10; 23/728 empty-gold exclusions preserved, no new exclusions).

Four arms only (this job does not own lexical BM25/TFIDF controls or any
PPLX/PCA/PQ model arms; those are labeled NOT RUN below).

## Method (own implementation)

Files: `metrics_top10.py` (own scorers/metrics), `tests_top10.py` (durable
TDD suite), `run_top10.py` (gates + execution), `audit_top10.py`
(independent audit). Runtime: `$HOME/muse-work/ml-python` (numpy available).

Arms (higher scores better; cached FLOAT96 vectors used directly):

- `sign96`: SIGN96 Hamming; score = -Hamming(packed docs, sign(query)).
  `pack_signs_bool(C >= 0)` big-endian 12B/doc; `sign(0) >= 0` is True.
- `float_raw`: FLOAT96 raw cosine `(C@q)/(||C||·||q||)`.
- `float_std`: FLOAT96 document-standardized cosine with existing definition:
  per-axis doc std (`ddof=0`), zero-variance axes replaced by 1.0 (declared),
  then `cosine_raw(C/std, q/std)`. Fit uses documents only.
- `asym`: asymmetric float-query x SIGN96 `dot(q, decode_pm1(packed))/sqrt(96)`.

Deterministic Top10: descending score, then ascending
`SHA256('top10-r1|'+archive_id+'|'+str(row_index))`, then ascending row_index
for hash collisions. Exactly 10 IDs (all corpora have N > 10); no gold-aware
order; no duplicates.

Zero-vector handling (declared before running): no zero docs or zero queries
were found in any cache (see gates); rule is nonfinite cosine maps to `-inf`
(worst) for ranking and expectation; Hamming/asym are total. Stored JSON uses
`null` for a nonfinite top-10 score entry; replay maps `null` to worst.

Metrics per query per arm (K=10):

- `hit10`: realized 1 if any gold row in exactly ten IDs else 0.
- `recall10`: `|gold ∩ top10| / |gold|`.
- `ndcg10`: binary DCG/IDCG with deterministic order.
- `exp_hit10`: exact expected Hit@10 under uniform random within-score-bucket
  tiebreak (closed form via `math.comb`; boundary bucket
  `1 - C(B-gb,take)/C(B,take)`; 1.0 if gold fully above cut; 0.0 if none).
- Legacy `fr3_sign`/`fr3_float`: exact expected Recall@3 (uniform ties) for
  SIGN96/FLOAT96-raw replay gate.

No text/model inference, so truncation count is 0 for all 9440 queries.

## Historical gates (SIGN/FLOAT FR3, tolerance 1e-12)

| benchmark | n | max |d_sign| | max |d_float| | viol | result |
|---|---|---|---|---|
| PerLTQA | 8265 | 0.0 | 0.0 | 0 | PASS |
| LME | 470 | 0.0 | 0.0 | 0 | PASS |
| REALTALK | 705 | 0.0 | 0.0 | 0 | PASS |

Caches unchanged (sha256 before == after for all 482 cache/control files).
PerLTQA native dedup LOW48==HIGH48 at t=1.0 verified; LME/REALTALK t=1.0
dedup verified. REALTALK archive binding (`chat`, `file`, `N`, `gold_count`)
verified per query; `id_to_row` verified as full 0..N-1 permutation per
archive and inverted for `gold_doc_ids`/`doc_ids` labels (IDs remain row
indices for replay). Doc-order reconstruction is cached row order.
Question-text exact equality against raw source is NOT verified by baseline
(raw export owned by data job); gold rows are cached row indices verified in
range and count-matched to controls. Details: `gates_top10.json`.

## Results (separate datasets, NOT averaged)

Means over per-query realized metrics (plus tie-sensitivity `exp_hit10`).
Full per-query rows: `per_query_top10.jsonl` (9440 rows).

PerLTQA (n=8265):

| arm | Hit10 | Recall10 | nDCG10 | expHit10 |
|---|---|---|---|---|
| sign96 | 0.7568 | 0.6182 | 0.4907 | 0.7576 |
| float_raw | 0.8081 | 0.7095 | 0.5822 | 0.8081 |
| float_std | 0.8396 | 0.7024 | 0.5775 | 0.8396 |
| asym | 0.8019 | 0.6760 | 0.5466 | 0.8019 |

LME (n=470):

| arm | Hit10 | Recall10 | nDCG10 | expHit10 |
|---|---|---|---|---|
| sign96 | 0.8638 | 0.7626 | 0.5914 | 0.8608 |
| float_raw | 0.8255 | 0.6895 | 0.5095 | 0.8255 |
| float_std | 0.8830 | 0.7955 | 0.6207 | 0.8830 |
| asym | 0.8574 | 0.7338 | 0.5559 | 0.8574 |

REALTALK (n=705 valid):

| arm | Hit10 | Recall10 | nDCG10 | expHit10 |
|---|---|---|---|---|
| sign96 | 0.4652 | 0.3434 | 0.2455 | 0.4668 |
| float_raw | 0.3660 | 0.2783 | 0.2020 | 0.3660 |
| float_std | 0.4851 | 0.3747 | 0.2622 | 0.4851 |
| asym | 0.4355 | 0.3306 | 0.2277 | 0.4355 |

No cross-dataset average is reported (separate benchmarks by protocol).
Tie-at-cut fractions (boundary bucket B>1 straddling rank 10):
PerLTQA sign96 0.7032, asym 0.0005, floats 0.0000;
LME sign96 0.6255, others 0.0000;
REALTALK sign96 0.6979, float 0.0028 each, asym 0.0043.
Hence `Hit10` vs `expHit10` gaps are small; Hamming ties are the sensitive arm
by design, handled by the exact expectation above.

## Costs (payload bytes; timing; all queries, no truncation)

Resident payload (summed once per archive over 510 archives):

- Packed SIGN96: 3,034,056 B (12 B/doc).
- FLOAT96 in-memory float64: 194,179,584 B (768 B/doc; cache dtype on disk).
- Shared std overhead: 391,680 B (768 B/archive).
- Saved replay states `state_*.npz` (510 files, packed+std): 3,682,776 B.
- Source caches on disk: 203,573,819 B (not charged as payload).
- `per_query_top10.jsonl`: 21,951,870 B; checkpoints `ckpt_top10_*.jsonl`
  total identical 21,951,870 B (persisted every archive; no fabricated rows).
- Query workspace (estimate, not resident): float64[96]=768 B/query plus
  transient N×8 B score vectors per arm during scan.
- Encoder weights / raw text storage / IDs-index: NOT MEASURED by baseline
  (not owned). SVD encoder missing note does not apply (no SVD arm here).
- No claim of equal total memory from equal payload.

Timing (single run, CPU-only, wall 199.9 s, cpu 199.9 s, peak RSS 165 MB):

- fit (std+pack over 510 archives): 0.38 s total.
- scoring (4 arms + FR3 over 9440 queries): 25.06 s.
- deterministic ranking + metrics (4 arms × 9440): 81.88 s.
- Per-archive breakdown: `summary_top10.json` → `timing.archives`.
- Truncation: 0; token lengths/timing for model encoding: NOT RUN (no model).

## Replay

Per-query fields: `benchmark, qid, archive_id, N, gold, gold_size`,
per arm `ids[10], scores[10], hit10, recall10, ndcg10, exp_hit10, tie{better,
bucket_size, gold_in_bucket, take, is_tie_at_cut}`, plus `fr3_sign/fr3_float`,
`ctrl_sign/ctrl_float`, `cache_file, cache_sha256, state_file, state_sha256,
state_bytes, packed_bytes`. REALTALK adds `gold_doc_ids` and per-arm
`doc_ids` via inverted `id_to_row`.

Independent replay: given cache file + `state_*.npz` (or recompute
packed/std with `metrics_top10` definitions) + `REPORT` tie rule, recompute
the four score vectors and `deterministic_top10`; compare IDs and recompute
metrics. `audit_top10.py` does this independently (inline ranking, no import
of runner ranking): structural 9440/9440, tie-order 9440/9440, spot full
rescore 30/30 match. Log: `audit_top10.log`.

TDD: `tdd_log_01_failing.txt` (ModuleNotFoundError before implementation) →
`tests_top10.py` 10 passed in `tdd_log_02_green.txt`, including packed
roundtrip/mutation, multi-gold, boundary-tie exactly-ten with adversarial
gold, hash-not-row order, nonfinite-worst, and brute-force permutation
enumeration for `exp_hit` (20 trials, N=6/K=3) and expected recall (10 trials).

## Blockers / NOT RUN (not invented)

- None blocking: all 9440 queries completed; no missing inputs invented.
- Raw-text question equality: not verified here (data-job owned).
- Model arms (PPLX INT8/BIN/asym, PCA96_SIGN, PQ12B) and lexical BM25/TFIDF:
  NOT RUN by baseline (separate owners).
- Larger models (e.g. 8B Nemotron FP32): NOT RUN (WSL 15 GiB infeasible).
- No 1M-corpus extrapolation; no bootstrap certification claimed.

## Checkpoints

`ckpt_top10_perltqa_*.jsonl` (30), `ckpt_top10_lme_*.jsonl` (470),
`ckpt_top10_realtalk_*.jsonl` (10), merged `per_query_top10.jsonl`,
`summary_top10.json`, `gates_top10.json`, `run_top10.log`, `audit_top10.log`,
`tdd_log_*.txt`.
