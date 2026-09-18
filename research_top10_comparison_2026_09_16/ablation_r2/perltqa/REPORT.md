# PerLTQA channel ablation (en_v2, 30 archives, 8265 queries)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## Fidelity gate (passed BEFORE any ablation number; see `FIDELITY_GATE.json`)

- Recipe recovered verbatim from `bench3/runs/b3b_perltqa/step2_build.py`
  (`build_items` + `fit_archive`); LSA32 `random_state=5101`, SVD96 `random_state=5204`.
- **G1:** sign(C_rebuilt) == sign(C_cached) elementwise on all 30 archives:
  **0 differing bits / 1,179,648**, max abs diff 0.0.
- **G2** (replay from cached C/qC with the shared scorers): qscale Hit@10 = 80.0000%
  (target 80.0000), sym deterministic Hit@10 = 75.6806% (target 75.6806, exact fraction
  6255/8265; sub-1e-6 rounding), sym expected-Hit@10 = 75.7612%, qscale FR@3 = 53.2375%
  (target ≈53.24%). GATE PASS.

## Method

- Arms (identical except Z assembly; SVD96 seed 5204, 96 dims, 12 B sign payload):
  FULL=[LSA32|word|char], NO_LSA=[word|char], NO_CHAR=[LSA32|word], WORD_ONLY=[word].
  `min(Z.shape) > 96` asserted for every archive x arm (min N = 293). LSA_ONLY not attempted (protocol).
- Scorers: `sym = -Hamming(doc bits, query bits)`;
  `qscale = dot(doc ±1 bits, qC/sigma)`, sigma = per-archive std of DOCUMENT C (ddof=0, floor 1e-12).
- Deterministic top-K per shared definition (score DESC, SHA256(`top10-r1|archive|row`), row);
  fast ranking verified element-equal to `audit_baseline_lib.det_top10` on 30 tied samples.
- Contrasts: arm − FULL, paired archive-clustered bootstrap, 20000 reps, seed 20260916.
- Verification (probe in `/tmp/verify_perltqa.py`, kept out of deliverable):
  66120 rows re-derived from `per_query.jsonl` match `RESULTS.json` exactly;
  fresh independent rebuild of one archive reproduces top10/metrics/expected_hit on all
  1728 of its rows via the library path; second-method bootstrap agrees within 0.02 pp.

## Results (pp = percentage points; CI = 95% clustered bootstrap)

| arm x scorer | Hit@10 (arm−FULL, CI) | FR@3 (arm−FULL, CI) |
|---|---|---|
| NO_LSA sym | +0.44 [−0.45,+1.29] ns | −0.13 [−1.03,+0.76] ns |
| NO_LSA qscale | −0.47 [−1.30,+0.34] ns | **−1.23 [−2.16,−0.30] SIG** |
| NO_CHAR sym | **+1.39 [+0.35,+2.48] SIG** | **+3.13 [+1.96,+4.27] SIG** |
| NO_CHAR qscale | **+0.83 [+0.14,+1.49] SIG** | **+2.26 [+1.60,+2.96] SIG** |
| WORD_ONLY sym | **+2.13 [+0.86,+3.48] SIG** | **+2.40 [+1.13,+3.69] SIG** |
| WORD_ONLY qscale | **+1.37 [+0.50,+2.21] SIG** | **+2.09 [+1.24,+2.94] SIG** |

Same pattern on Hit@3 / expected-Hit@10 (see `RESULTS.json`): NO_LSA qscale Hit@3
−1.42 [−2.65,−0.16] SIG; NO_CHAR and WORD_ONLY significantly positive in all 8 cells each.
Absolute levels: FULL sym Hit@10 75.68 / qscale 80.00; WORD_ONLY sym 77.81 / qscale 81.37.
Per-archive breakdowns in `RESULTS.json`.

Cost: mean Z features FULL 24055 / NO_LSA 24023 / NO_CHAR 6818 / WORD_ONLY 6786;
SVD-stage build time 28.1 s / 25.7 s / 5.4 s / 5.0 s (shared TF-IDF excluded equally);
payload 12 B/doc confirmed for every archive x arm.

## Verdict: LSA-redundancy hypothesis on PerLTQA — REFUTED

Dropping LSA32 is **not** beneficial here: 6 of 8 NO_LSA−FULL cells are null and the two
qscale recall cells are significantly *negative* (FR@3 −1.23 pp, Hit@3 −1.42 pp, both
excluding zero). The RealTalk direction (NO_LSA directionally better in 6/6 cells,
qscale Hit@10 +2.41 pp / FR@3 +3.44 pp, all CIs including zero) does **not** replicate —
with 30 clusters the CIs are ~3x tighter and they point flat-to-negative, not positive.
This is exactly the cross-benchmark reversal the programme warned about: a negative
result, and a genuinely useful one.

Additional reversal: the char channel, clearly valuable on RealTalk (−5.8 pp when
removed), is significantly *harmful* on PerLTQA — removing it (NO_CHAR) gains
+1.4/+0.8 pp Hit@10 and +3.1/+2.3 pp FR@3, and WORD_ONLY is the best arm overall
under both scorers. Channel value is benchmark-dependent; neither channel's RealTalk
effect generalized.

## Files

`ablation.py` (produces the rest), `FIDELITY_GATE.json`, `per_query.jsonl`
(66120 = 8265 queries x 4 arms x 2 scorers, top10 ids + gold), `RESULTS.json`, `REPORT.md` (this file).
