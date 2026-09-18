# PROTOCOL — TASK B: fixed 96-bit B8 allocation (frozen, pre-outcome)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Frozen before any candidate outcome was observed. No width/axis/threshold sweep.
No retuning after observing candidate outcomes. No best-arm selection.

## B1. Task definition

Fixed 96-bit B8 allocation (NOT an extra suffix). Single frozen definition:

1. Per archive, from DOCUMENT float vectors only (no query, no gold), compute
   per-axis population variance `var_j = mean_i (C_ij - mean_j)^2` (ddof=0,
   float64). Order axes by descending variance, ties broken by lower
   coordinate index: `order = lexsort((arange(96), -var))`.
2. DROP the 8 lowest-variance axes: `DROP = order[88:96]`.
   Of the remaining 88, the 8 highest-variance axes are two-bit axes:
   `SEL = order[:8]`. The other 80 (`ONE = order[8:88]`) are one-bit axes.
3. Bit budget: 80 signs + 8 signs + 8 magnitude flags = 96 bits = 12 bytes.
   Magnitude flag on selected axis k for doc i:
   `flag_ik = (abs(C_{i,SEL_k}) > thr_k)` with STRICT `>`,
   `thr_k = median_i abs(C_{i,SEL_k})` (float64, document-only fit).
4. Packing (np.packbits, bitorder="big", sign convention `x >= 0`):
   88 sign bits in ascending-retained-axis order -> 11 bytes,
   8 magnitude flags in ascending-SEL order -> 1 byte.
   Real payload `[N,12]` uint8. Roundtrip-asserted before scoring.
5. Decoding: retained signs -> +/-1; flagged selected axes upgraded to +/-2
   (sign kept); dropped axes reconstruct to 0.
   Levels {+2,-2,+1,-1,0} are FIXED constants, not fitted, not gold-selected.
6. Primary score: `cosine(float q, reconstructed doc)`,
   `s_i = (r_i . q) / (||r_i||_code * ||q||)`.
   Per-doc reconstruction norm `||r_i||` is computed FROM CODE (exact norm of
   the decoded vector; always >= sqrt(88) > 0, asserted).
   Query float `q` is the disclosed float query channel (asymmetric scoring).
   If `||q|| == 0`, score is non-finite and mapped to worst (fail-closed).
   New scoring consumes ONLY packed docs + disclosed shared decoder state
   (axis IDs, thresholds, fixed levels) + float query. No per-document float
   cache/norm leakage: document float norms are never used in B8 scoring.
7. Shared decoder state charged explicitly per archive (content bytes):
   `drop_ids` uint8[8] (8 B) + `sel_ids` uint8[8] (8 B)
   + `thresholds` float64[8] (64 B) = 80 B. npz container overhead excluded;
   payload content bytes = N*12. This is total-payload matching,
   NOT equal full-system cost. Query workspace (transient float96 = 768 B)
   and fitting cost reported separately, never attributed to the document
   allocation.

## B2. Arms (every query, K=3)

- A0 SYM-SIGN96 (symmetric control): `-Hamming(doc_signs, query_signs)`,
  signs `(x >= 0)`. Identical tie structure to cosine(pm1,pm1).
- A1 ASYM-SIGN96 (primary baseline): `cosine(float q, pm1(doc signs))`,
  norm of pm1 vector from code (= sqrt(96)).
- A2 B8 (primary candidate): Section B1 scoring.
- A3 SIGN88 (ablation, same DROP axes, signs only): reconstruction +/-1 on
  retained axes, 0 on dropped; `cosine(float q, s)` with code norm
  (= sqrt(88)). Physical payload 11 B + dropped map. Separates
  dropping-axes effect from extra-precision effect.
- A4 FLOAT-RAW (control, isolated full-doc path): plain cosine
  `(C.q)/(||C||*||q||)`, source-compatible division, non-finite -> worst.
- A5 FLOAT-STD (control, isolated full-doc path): scale-only standardization
  fit on DOCUMENTS only: `std_j = sqrt(var_j)` (same var as B1; exact 0.0
  replaced by 1.0 — declared here), `zC = C/std`, `zq = q/std`,
  `cosine(zC_row, zq)`. No centering. Control state 96 float64 = 768 B,
  charged separately. No query/gold input to the fit.
- No other quantizer is claimed: PQ quality is NOT tested here (no runnable
  established quantizer under the frozen-plan/no-install constraints).

Primary contrast (per query): `d1 = FR_B8 - FR_ASYM-SIGN96`.
Secondary contrast: `d2 = FR_B8 - FR_SYM-SIGN96`.
Diagnostic contrasts: B8-SIGN88, B8-FLOAT-RAW, SIGN88-ASYM, ASYM-SYM.
Point estimates are raw paired means. No equivalence assertion from
nonsignificance.

## B3. Metrics

- FR@3: exact expected fractional recall@3 under uniform random
  within-bucket tiebreak (higher score better; non-finite mapped to worst).
  Walk unique score levels descending; full bucket inside top-3 counts gold
  hits fully; boundary bucket counts `(slots * gold_in_bucket / bucket_size)`,
  divided by gold count m.
- nDCG@3 (secondary, binary unique gold relevance rel in {0,1}, separate from
  FR): expected DCG@3 under uniform within-bucket tiebreak: a score bucket of
  size B occupying rank positions [p, p+B) contributes
  `gold_in_bucket * mean(discount over positions intersected with [0,3))`
  with `discount(pos) = 1/log2(2+pos)`; IDCG@3 from min(3, m) ones;
  nDCG = DCG/IDCG. Computed per arm per query when feasible; must not delay
  core FR counts.
- Oracle best/worst FR@3 of the SYM base at the K boundary (diagnostic only).

## B4. Cohorts (benchmarks kept separate, never pooled)

- PerLTQA: full 8265 queries / 30 archives. Report total AND sections
  events / profile / dialogues / social_relationship. Do not conflate counts.
- LME: 470 (one query per archive; archive == query cluster).
- REALTALK: 705 valid queries / 10 chat archives (23 excluded ids honored).
- LoCoMo: excluded pending gold provenance (unsupported here).

## B5. Gates (run first; reproduce BOTH comparators per identity, tol 1e-12)

Per benchmark, recompute SYM-SIGN96 FR@3 and FLOAT-RAW FR@3 from read-only
caches and compare EVERY per-query value to the original historical t=1.0
rows (PerLTQA: qid-keyed LOW48/HIGH48 dedup requiring identical native_exact
and float_exact; LME: (archive_id, qa_id)-keyed sign_exact/float_exact;
REALTALK: qid-keyed sign_exact/float_exact). Record n_compared, n_violations,
max abs diffs, recomputed vs stored means. Gate failure stops the affected
benchmark only; others proceed. Mean targets alone cannot pass.

## B6. Uncertainty

2000 cluster-bootstrap replicates, seed 20260915 (numpy default_rng), per
benchmark: resample archive clusters with replacement (PerLTQA: 30 char
clusters; REALTALK: 10 RT chat clusters; LME: 470 single-query clusters =
ordinary bootstrap). CI = 2.5/97.5 percentiles of replicate paired means.
Reported point = raw paired mean (NOT bootstrap mean).

## B7. Timing and memory methodology

- Env: `PYTHONDONTWRITEBYTECODE=1`, `OMP_NUM_THREADS=1`,
  `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, single-thread torch/BLAS,
  CPU only. Visible CPUs = 1 (shared WSL host; contention disclosed, not
  controlled).
- Declared subset: PerLTQA archive index 0 in sorted-char order, all its
  queries: 1 warmup run then 3 timed repeats of full 6-arm scoring
  (encoder fit timed separately). Report mean +/- std and per-query ms.
- Peak RSS via `resource.getrusage(RUSAGE_SELF).ru_maxrss` (peak, must stay
  < 3 GB); report per benchmark. Payload/shared/query-workspace bytes
  reported separately (Section B1).

## B8. Seeds, budget, failure handling

- Bootstrap seed 20260915, B=2000. No other randomness (deterministic codec).
- Budget: finish within 25 min wall; per-archive checkpoint after each
  completed archive (`ckpt_<bench>_<idx>.jsonl`); failed cases kept and
  listed in summary.json (`failed_cases`), never silently dropped.
- No `converged`-style flags anywhere (never hardcoded).
- Truthful partial output beats fabricated success: benchmark statuses are
  per benchmark: tested / gate-blocked / partial / unsupported.

## B9. Deliverables (all inside the assigned output directory)

PROTOCOL.md, protocol.sha256, lib_b8.py, run.py (actual entrypoint),
tests.py, test_log.txt, run.log, per_query.jsonl (identity-keyed raw
per-example outcomes for all arms), checkpoints + packed payloads (.npz with
12-byte payload, axis maps, thresholds) + decoder state, summary.json,
REPORT.md, source_hashes.json, progress.json. Exact reproducible command in
REPORT.md and summary.json.
