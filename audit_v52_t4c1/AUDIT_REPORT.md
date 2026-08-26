# V52 Task 4C1 — Independent Adversarial Audit

**Auditor posture:** zero trust, adversarial. Goal was to break the result.
**Audit date:** 2026-08-26
**Verdict:** `PASS WITH CONDITIONS`
**Audit level:** `FULL RAW-TABLE NUMERICAL REPRODUCTION`

Not full end-to-end: `longmemeval_v52_adapter.py` / `_v2.py` and the Task 4B trial
table were not in the delivered package and could not be located in the source
Drive. The canonical dataset is available but is unusable without the adapters.

---

## 1. Chain of custody — PASS

| Binding | Result |
|---|---|
| 26/26 package files vs `AUDIT_PACKAGE_SHA256SUMS.txt` | all OK |
| script sha in pre-run seal == post-run manifest == actual file | `54930bd6…` identical |
| prereg / method-spec sha in seal == actual | match |
| post-run manifest `pre_run_seal_sha256` == actual seal | match |
| seal timestamp vs run completion | seal 2026-08-24T21:39Z, run 2026-08-26T20:22Z |

**No post-seal script mutation.** The script additionally self-enforces this
(`[PROTOCOL SEAL FAILURE] script changed after seal`) and re-verifies every input
hash at load time.

Preregistration freezes, all confirmed present *before* performance: widths
`{24,32,48,64,96}`; FLOAT96 and SIMPLE_SIGN96 both predefined as primary methods;
RaBitQ fail-closed gate; tolerances 0.5/1.0/2.0 pp; ITQ seeds 101/202/303/404/505;
SVD `random_state=5204`; nuisance trials 20; no reranker/shortlist; no adaptive
bit width. No post-hoc method appears anywhere in the outputs — exactly the 7
sealed methods are present in every table.

## 2. Dataset — NOT INDEPENDENTLY HASHED

Expected `d6f21ea9…`, 277,383,467 bytes. The Drive copy reports byte size
277,383,467 (exact match) but the content was not downloaded, so the SHA256 was
**not** independently recomputed. The run-time script does hash it and hard-aborts
on mismatch. Cohort counts (500 total / 470 primary / 30 abstention / 0 zero-gold)
are enforced in code and consistent with the raw table (470 unique non-`_abs` qids,
zero `gold_count==0` rows).

## 3. Leakage — NO DEFECT FOUND (source-limited)

Verified by reading `evaluate_item` directly: every SVD fit and every `fit_itq`
call executes before the first query transform (`wv.transform([question])`), which
appears strictly after `fit_archive_representation(texts)`. No `gold_rows`,
`gold_ids`, `answer_session_ids`, `question_type`, or `question` reaches any fit
call. Gold is used only in `metrics3` after ranking.

**Limitation:** the adapter internals (`fit_archive_representation`, `fit_itq`,
`build_archive`) were not readable. The shipped leakage audit is a static AST check
run by the audited script itself and verifies signatures only — it cannot exclude a
closure over module-level state. Not independently confirmed.

## 4. Raw table integrity — PASS

- 47,000 rows == 470 × 20 × 5 exactly
- 470 unique questions, **every** question has exactly 100 rows
- 0 duplicate `(question_id, trial, itq_seed)` cells; 47,000 distinct keys
- trials 0–19 complete, seeds exactly the 5 frozen values
- 0 NaN, 0 out-of-range values across all 21 metric columns
- no `_abs` question, no zero-gold question
- no hidden width, no hidden method

## 5. Independent aggregation — EXACT REPRODUCTION

Reconstructed from the raw table under correct nesting (nuisance trials averaged
inside question×seed → seeds collapsed as nuisance → equal weight per question).

| Method | ANY R@3 | ALL R@3 | Fractional R@3 | Claimed | Δ |
|---|---:|---:|---:|---:|---:|
| MIXED_FLOAT96_GLOBAL | 61.0638 | 28.9362 | **44.0106** | 44.0106 | 0.0000 |
| MIXED_SVD_ITQ96_GLOBAL | 54.2766 | 22.6723 | **37.6141** | 37.6141 | 0.0000 |
| MIXED_SVD_ITQ64_GLOBAL | 45.6745 | 17.4319 | **30.6287** | 30.6287 | 0.0000 |
| MIXED_SVD_ITQ48_GLOBAL | 39.5234 | 14.6277 | **26.2202** | 26.2202 | 0.0000 |
| MIXED_SVD_ITQ32_GLOBAL | 33.8936 | 13.0980 | **22.8093** | 22.8093 | 0.0000 |
| MIXED_SVD_ITQ24_GLOBAL | 30.4404 | 10.9511 | **19.9449** | 19.9449 | 0.0000 |
| SIMPLE_SIGN96_GLOBAL | 71.3085 | 38.4574 | **54.1975** | 54.1975 | 0.0000 |

Contrasts: SIGN96−ITQ96 **+16.5834 pp**, SIGN96−FLOAT96 **+10.1869 pp**,
FLOAT96−ITQ96 **+6.3965 pp**. All claimed values reproduce.

**Overweighting ruled out.** FLOAT96/SIGN96 are computed once per trial and written
into all 5 seed rows. Because the design is perfectly balanced (100 rows/question),
flat mean and correctly-nested mean agree to 7.1e-15. The 5× replication cancels
exactly and does **not** inflate SIGN96.

## 6. Frontier — REPRODUCES

| Width | Fractional | loss vs ITQ96 |
|---:|---:|---:|
| 24 | 19.9449 | 17.6692 |
| 32 | 22.8093 | 14.8048 |
| 48 | 26.2202 | 11.3939 |
| 64 | 30.6287 | 6.9854 |
| 96 | 37.6141 | 0.0000 |

Smallest width within 0.5 / 1.0 / 2.0 pp = **96 / 96 / 96**. No sub-96 width comes
close — the nearest (ITQ64) misses the widest band by 5 pp. Monotone in bits, with
no inversion, in aggregate and within every stratum.

## 7. SIGN96 / ITQ96 same-input — PROVEN AT SOURCE, NOT NUMERICALLY

```python
C = Cs[b]; qC = QY[b] - mus[b]        # ITQ path
D = (C @ R) >= 0 ; Q = (qC @ R) >= 0
signD = (Cs[96] >= 0)                  # SIGN path — same object
signQ = ((QY[96] - mus[96]) >= 0)[0]
```

ITQ96 and SIGN96 read the **identical in-memory array** `Cs[96]` for the archive,
and an identical deterministic expression for the query. Max abs difference is
exactly 0 by construction, not by tolerance. This is a clean rotation ablation.
Per-archive numerical confirmation was not possible (codes not exported), but the
source identity is stronger than a sampled check.

## 8. ITQ orientation — NOT VERIFIABLE; bug hypothesis does not survive

`fit_itq` lives in the unavailable adapter, so the encode orientation (`V@R` vs
`V@R.T`) could **not** be confirmed. Three independent lines of evidence argue the
orientation bug is *not* the explanation:

1. **Synthetic probe** (LSA geometry, correct Procrustes ITQ, `R = U@Wt` from
   `svd(V.T @ B)`): correct ITQ 20.50%, wrong-orientation ITQ 18.25%, random
   rotation 18.08%, identity-sign 9.38%. A transposed rotation degrades ITQ only
   toward random-rotation LSH — roughly 2 pp — and **never** below identity-sign.
   It cannot produce a 16.6 pp deficit.
2. **ITQ96 looks healthy, not broken.** Its 6.4 pp loss against the float reference
   is an ordinary 96-bit quantization loss, and quality rises smoothly and
   monotonically with bit width (19.9 → 22.8 → 26.2 → 30.6 → 37.6). A broken
   rotation would flatten that curve.
3. **Task 4B gate.** The script hard-fails unless ITQ96 matches the previously
   audited Task 4B `mixed96` to 1e-12; the shipped table shows a literal 0.0
   difference on all three metrics.

**The anomaly is therefore not "ITQ is broken" but "SIGN96 is unexpectedly good"** —
it beats the continuous 96-D representation it was derived from by 10.2 pp.

## 9. FLOAT96 definition — CONFOUNDED (preregistered, but load-bearing)

`float_scores = Ys[96] @ QY[96][0]` — **uncentered**, L2-normalized cosine, per
prereg §6.1. SIGN96 and ITQ96 are **centered**. So FLOAT96 vs SIGN96 differs by
*both* centering and retrieval geometry, and is not a clean quantization ablation.

Mean-centering is a well-documented retrieval improvement on TF-IDF/LSA
representations (common-component / hubness removal). **A centered continuous
control — `FLOAT96_CENTERED` — does not exist in the frozen method set, and it is
the single missing comparison needed to attribute SIGN96's advantage.**

Per audit §9: SIGN96 beating FLOAT96 must **not** be read as "binary carries more
information than continuous". They are different geometries (cosine vs Hamming) on
differently-preprocessed inputs.

## 10. Break attempts — all negative

| # | Hypothesis | Result |
|---|---|---|
| 1 | SIGN/ITQ different continuous inputs | Refuted — same array object |
| 2 | ITQ orientation bug | Not verifiable; cannot produce the gap (§8) |
| 3 | Sign threshold mismatch | Refuted — `>=0` for doc and query, both methods |
| 4 | Query centering mismatch | Refuted — both use `QY[96]-mus[96]` |
| 5 | Tie bias favouring SIGN96 | Refuted — one shared random priority per (question,trial) used by *every* method; SIGN96 tie sensitivity (0.965 pp) is *lower* than ITQ96's (1.216 pp) |
| 6 | Duplicate / imbalanced rows | Refuted — exactly 100 rows per question, 0 dupes |
| 7 | Incorrect seed nesting | Refuted — flat == nested to 7e-15 |
| 8 | Incorrect nuisance nesting | Refuted — same |
| 9 | Wrong gold denominator | Refuted — `hit/len(gold_rows)`, 0 zero-gold |
| 10 | Dataset / cohort mismatch | 470 primary confirmed in table; dataset hash not independently recomputed |
| 11 | Query / gold leakage | No defect found in the script; adapter unread |
| 12 | Post-selection | Refuted — seal predates run, 7 methods fixed |
| 13 | Hidden widths / methods | Refuted — only sealed 7 appear anywhere |
| 14 | Post-run code mutation | Refuted — hashes identical |
| 15 | Pathological constant ITQ bits | **NOT TESTABLE** — codes not exported |
| 16 | SIGN code complement handling | Refuted at source — no inversion |
| 17 | Wrong distance ordering | Refuted — `lexsort((priority,dist))` ascending Hamming; `lexsort((priority,-scores))` descending float |

**Quantified defect total: 0.0000 pp.** No arithmetic, aggregation, nesting,
duplication, tie, ordering or denominator defect was found. Nothing discovered
explains any part of the +16.58 pp.

## 11. Not verifiable from this package

Bit balance / dead bits (§15), duplicate-code and collision rates (§16), gold vs
non-gold Hamming distance distributions (§17), and per-archive numerical same-input
confirmation (§14) **all require the code matrices or the adapters**, neither of
which was shipped. These are precisely the diagnostics that would explain the
mechanism. Reported as NOT VERIFIABLE, not as PASS.

## 12. Robustness of the SIGN96 advantage

Broad, not driven by outliers:

- **W/T/L (SIGN96 vs ITQ96):** 248 / 141 / 81 of 470; median paired gap +5.00 pp;
  mean win +39.41 pp, mean loss −24.43 pp
- Removing the 50 largest contributors still leaves **+8.55 pp**
- Positive in **all 6** question types (+8.9 to +20.6 pp), **both** gold strata,
  **all 4** archive quartiles, **all 3** reuse tertiles — 15/15 frozen strata
- Best of 5 ITQ96 seeds (39.13%) is still 15.06 pp below SIGN96
- SIGN96 and FLOAT96 show exactly 0.0000 seed variance, confirming correct
  collapse across the ITQ seed dimension

## 13. Cost accounting — CLEAN, with a caveat

Code bits, continuous bytes, analytical touch, stored bytes, transform state, fit
time, query-transform time and scan time are reported as separate columns; FLOAT96
is booked as 768 continuous bytes/item and explicitly *not* as code bits. No
"96 bits = 96-bit system memory" or "50% fewer bits = 50% faster" claim appears.

Two facts the frontier must not be read against:
- **SIGN96 and ITQ96 cost identically** (96 bits, 5,913 stored bytes/archive,
  47,307 touch bits). SIGN96 buys quality, not compression.
- **Scan is ~1000× cheaper than query encoding** (0.0002 s vs 0.195 s), and shared
  transform state (~74.8 MB) dwarfs code payload (~5.9 KB). Bit-width reduction
  yields no measurable end-to-end latency benefit in this implementation. Runtime
  columns also carry warm-up ordering artifacts and should not be used for cost claims.

## 14. RaBitQ — CORRECTLY BLOCKED

`[BASELINE BLOCKED — IMPLEMENTATION SEMANTICS]` in prereg, seal and manifest. No
RaBitQ column exists in the raw table. No homemade approximation entered results.

## 15. Overclaims found

1. **Auto-generated falsification line is self-contradicting.** The report states
   *"FLOAT96 exceeds ITQ96 by >2 pp; 96-bit binarization is a material retrieval
   bottleneck here."* The same run's SIGN96 — a 96-bit binary method — beats
   FLOAT96 by 10.19 pp. That sentence is generated by a rule that only inspects
   `float_minus_itq` and ignores SIGN96. It must be withdrawn or rewritten as a
   statement about the *ITQ rotation*, not about binarization.
2. **Centering confound not disclosed** in the handoff. FLOAT96−ITQ96 = +6.3965 pp
   is not pure quantization loss; it mixes quantization with the absence of
   centering on the float side.

Otherwise the handoff is properly bounded — no generality, novelty, SOTA,
production-latency or population-inference claim was made.

## 16. Inference limitation — RESPECTED

All 470 primary questions form one shared-session connected component. No
population p-value, CI, superiority, equivalence or non-inferiority claim appears
anywhere in the package. This audit adds none. All W/T/L and strata figures above
are descriptive fixed-benchmark counts only.

## 17. Prior-art ceiling — RESPECTED

Sign/binary quantization is established prior art. A positive SIGN96 result is not
an algorithmic novelty and is not presented as one.
