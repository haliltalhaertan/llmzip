# NEW vs KNOWN — element-by-element verdict on the 2026-09-16 package

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Method: every number below marked VERIFIED was re-derived this session from
their raw per-query CSVs or raw caches (see INCOMING_AUDIT.md + recheck.py +
recheck_results.json). CLAIM = their files state it; not re-run here.

## GENUINELY-NEW (we did not have these)

1. **qscale / weighted scorer as a frozen candidate** — `sum_j b_dj·qC_j/σ_j`,
   σ = per-archive DOCUMENT std, ddof=0, floor 1e-12, α=1, frozen BEFORE LoCoMo
   in `PLAN_BEFORE_RUN.json`. Our baseline never defined this arm. (VERIFIED:
   reproduced exactly by coordinator + rank-equivalence shown in audit §1.)
2. **LoCoMo transfer measurement** — 1531 kept / 1986 with logged pre-score
   exclusions (`locomo_adapter_before_scores.json`), quality for 6 arms, paired
   deltas + CIs (`locomo_paired_comparisons.json`). New data for ANY scorer.
   (VERIFIED: re-aggregated exactly from `quality_per_query.csv`.)
3. **`query_sign_doc_std` arm** — their per-doc-normalized variant
   (`readout_diagnostic.py:97`). New definition; value unclear (see §3 of
   audit). (VERIFIED to exist + re-derived to 0.000000 pp.)
4. **Native kernels** (`scripts/kernels.c`, `native_scorers.py`) — exact LUT
   scalar + AVX-512 SoA weighted scorer, Hamming kernels, fused float32-BLAS
   path. New engineering artifact; speed numbers are machine-bound CLAIMs.
5. **Raw-stage fidelity rebuild** — `raw_stage_per_query.csv` (+summary):
   48 LME + 30 PerLTQA archives rebuilt from raw, 0 sign-bit changes; RealTalk
   explicitly not rebuilt. We never rebuilt raw stages. (CLAIM — CSVs
   inspected, not re-derived.)
6. **Scale diagnostics** (`scale_diagnostics.json`) — per-archive σ stats
   (σmax/σmin ≈ 3.7–3.8, floor never active). New descriptive numbers.
   (CLAIM — file read, not re-derived.)
7. **Counterfactual diagnostics** — `sign_tie_by_std` arm + two-factor Shapley
   split of standardize×sign-removal (`readout_summary.json:paired`). New
   analysis; producer-caveated, not deployable. (VERIFIED present in raw CSV.)
8. **DENETIM counter-review artifacts** — `check_ndcg_ties.py` refutation of
   the QUOTED nDCG tie formula, `paired_metric_differences.csv`,
   `package_crosschecks.json` (43-file manifest re-verification), FR@3
   cross-table (LME +0.06/+3.62, PerLTQA +4.34/−0.29, RealTalk −0.14/+2.35,
   LoCoMo +4.35/+1.58 for qscale−Hamming / qscale−old-asym). New argumentation;
   the FR@3 columns are re-aggregations of shipped CSVs. (CLAIM — not re-run.)
9. **LITERATUR oracle bounds** (`complementarity.json`) — hindsight
   per-query max-of-two-arms upper bounds (e.g. LME hit10 ≤ 90.21). New numbers
   but producer-labeled NOT a method. (CLAIM.)
10. **End-to-end text→top10 protocol + numbers** (`end_to_end.json`, 19
    archives / 51 queries, "no 2× win shown"). New measurement design; numbers
    machine-bound. (CLAIM.)

## ALREADY-HAD (their shipment re-measures what our baseline owns)

| Their element | Our file that already has it |
|---|---|
| sign96/Hamming quality, all 3 benchmarks, 9440 queries | `baseline/per_query_top10.jsonl` (arm `sign96`); coordinator 12/12 cells EXACT |
| float_raw = centered cosine quality | same file, arm `float_raw` (their `centered_cos`) |
| float_std = standardized cosine quality | same file, arm `float_std` (their `standardized_cos`) |
| old asym = doc_sign_query_raw quality | same file, arm `asym` (their `doc_sign_query_raw`) |
| exact expected-Hit@10 under uniform ties | `baseline/metrics_top10.py` + `audit_top10.py` (same math as their `common.expected_metrics`) |
| FR@3 SIGN/FLOAT replay gate (tol 1e-12, PASSED) | `baseline/per_query_top10.jsonl` (`fr3_sign`/`fr3_float`) + `REPORT.md` |
| deterministic top-10 / tie discipline discussion | `baseline/REPORT.md` (hash-ordered top10; expected-hit metric) |
| "standardized float beats Hamming on PerLTQA/RealTalk" | already in our `float_std` vs `sign96` columns |

## CONTRADICTS-OURS (exactly one — a definitional fork, not a data dispute)

- **`query_sign_doc_std` / "qsign_dstd"**: THEIR formula
  (`readout_diagnostic.py:87,97`: per-doc unit-normalized scaled docs dotted
  with query signs) vs COORDINATOR's formula (`verify_incoming.py:42`:
  unnormalized `(C/σ)@qb`). Same label, different arm; deviations LME
  +0.6383 / PerLTQA −0.2662 / RealTalk −0.8511 pp (coordinator-minus-theirs)
  are the arithmetic consequence. Both pipelines are self-consistent
  (theirs re-derives to +0.000000 pp — VERIFIED). **Do not merge the two
  series under one name; do not average across benchmarks.**

## Bottom line for the team

Do not re-run: old-arm quality on LME/PerLTQA/RealTalk, the tie-metric math,
the FR@3 gate, or qscale on the three old benchmarks (all reproduced
exactly). Genuinely unconsumed: LoCoMo cohort reuse for FUTURE scorers
(adapter is pre-score and reusable), the frozen qscale definition, the native
kernel code (needs our own machine for timings), and the open question the
data actually poses — whether anything beats old asym on PerLTQA at all
(current answer: no; qscale trails it by 0.19 pp).
