[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

> **ORCHESTRATOR ERRATA (2026-09-13, after D5 adversarial review).** F2: the LoCoMo leg is VACUOUS vs random-abstention (random routing alone passes the +0.5pp leg; COMBO AUC 0.558). "PROMOTE" is CONDITIONAL on a future preregistration carrying a BINDING vs-random superiority gate (model gain > random-range max at alpha=0.20); LoCoMo must NOT be called a replication. See ERRATA_ROUND3_D5.md §F2.

# DENEY 5 (c2) — gold-free failure predictor -> adaptive budget routing

**[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

Numpy only; no network; read-only on /mnt/c. SMALL=SPREAD48 (repaired rank-linspace, full-data variance ordering — gold-free), LARGE=NATIVE96, secondary SMALL2=SPREAD64. Split: train iff first hex of sha256("c2|"+qid) even (unstratified).

## 1. Gates (abort on fail — all PASS)

| Gate | Recomputed | Reference | Diff |
|---|---|---|---|
| LME native | 0.5419751773049645 | 0.5419751773049645 | 0.0e+00 |
| LME SPREAD48 | 0.4578262411347518 | 0.4578262411347518 | 0.0e+00 |
| LME SPREAD64 | 0.5021382978723404 | 0.5021382978723404 | 0.0e+00 |
| LME native vs stored | max abs diff 1.1e-16 (470/470) | | |
| LOCO native | 0.2365471466644105 | 0.2365471466644105 | 0.0e+00 |
| LOCO SPREAD48 | 0.1591186551414565 | 0.1591186551414565 | 0.0e+00 |
| LOCO SPREAD64 | 0.1918111698237680 | 0.1918111698237680 | 0.0e+00 |
| LOCO valid | 1535 | 1535 | |
| feature NaN-freeness | 0 non-finite (both benchmarks) | | |

Sanity vs round3 splits band (~0.46-0.47): LME SPREAD48 all-470 = 0.4578 (band refers to split means of 64-bit arms; 48-bit full-data mean sits just below it — reported, not gated).

## 2. LME: labels + base rates

fail iff FR_small < FR_large - 1e-12. n=470 (train 244 / test 226). Base rates: all 24.9% (117), train 26.6% (65), test 23.0% (52). Mean FR: SMALL=0.4578 LARGE=0.5420 (all); test SMALL=0.4572 LARGE=0.5477.

## 3. LME: held-out AUC (positive class = fail)

| Feature | Train AUC | Test AUC |
|---|---|---|
| margin34 | 0.658 | 0.651 |
| crowd3 | 0.663 | 0.651 |
| crowd4 | 0.605 | 0.669 |
| crowd_pm1 | 0.663 | 0.672 |
| top3_tie_share | 0.655 | 0.677 |
| boundary_share | 0.645 | 0.696 |
| dup_top20 | 0.491 | 0.511 |
| var_decay | 0.499 | 0.391 |
| N | 0.542 | 0.376 |
| qent | 0.550 | 0.504 |
| margin34_large | 0.592 | 0.648 |
| crowd3_large | 0.578 | 0.554 |
| COMBO | 0.711 | 0.686 |

COMBO standardized coef (bias first): bias=-1.176, margin34=-0.548, crowd3=+0.030, crowd4=+0.089, crowd_pm1=-0.087, top3_tie_share=+0.155, boundary_share=+0.165, dup_top20=-0.129, var_decay=-0.178, N=+0.162, qent=+0.262, margin34_large=-0.162, crowd3_large=+0.198

## 4. LME: selective routing gains on TEST (pp)

| alpha | k | model | oracle | random mean | random range |
|---|---|---|---|---|---|
| 0.10 | 23 | +1.110 | +6.667 | +1.078 | [+0.476, +2.087] |
| 0.20 | 45 | +3.086 | +10.044 | +1.833 | [+0.985, +2.220] |
| 0.30 | 68 | +4.347 | +10.470 | +2.301 | [+1.206, +3.156] |
| 0.40 | 90 | +6.103 | +10.470 | +3.314 | [+1.543, +4.923] |

Constant sanity: all-SMALL +0.000pp (0 by construction); all-LARGE +9.050pp.

## 2. LOCO: labels + base rates

fail iff FR_small < FR_large - 1e-12. n=1535 (train 777 / test 758). Base rates: all 15.7% (241), train 16.6% (129), test 14.8% (112). Mean FR: SMALL=0.1591 LARGE=0.2365 (all); test SMALL=0.1777 LARGE=0.2373.

## 3. LOCO: held-out AUC (positive class = fail)

| Feature | Train AUC | Test AUC |
|---|---|---|
| margin34 | 0.555 | 0.543 |
| crowd3 | 0.536 | 0.536 |
| crowd4 | 0.528 | 0.517 |
| crowd_pm1 | 0.525 | 0.543 |
| top3_tie_share | 0.537 | 0.544 |
| boundary_share | 0.537 | 0.530 |
| dup_top20 | 0.508 | 0.499 |
| var_decay | 0.528 | 0.521 |
| N | 0.486 | 0.501 |
| qent | 0.478 | 0.433 |
| margin34_large | 0.495 | 0.506 |
| crowd3_large | 0.514 | 0.498 |
| COMBO | 0.598 | 0.558 |

COMBO standardized coef (bias first): bias=-1.657, margin34=-0.389, crowd3=+0.086, crowd4=+0.101, crowd_pm1=-0.184, top3_tie_share=-0.368, boundary_share=+0.193, dup_top20=+0.113, var_decay=+0.204, N=-0.195, qent=+0.074, margin34_large=+0.069, crowd3_large=+0.134

## 4. LOCO: selective routing gains on TEST (pp)

| alpha | k | model | oracle | random mean | random range |
|---|---|---|---|---|---|
| 0.10 | 76 | +0.529 | +7.751 | +0.508 | [+0.106, +0.914] |
| 0.20 | 152 | +1.481 | +8.888 | +1.135 | [+0.547, +2.125] |
| 0.30 | 227 | +1.939 | +8.888 | +1.827 | [+0.920, +2.581] |
| 0.40 | 303 | +3.120 | +8.888 | +2.279 | [+1.535, +3.022] |

Constant sanity: all-SMALL +0.000pp (0 by construction); all-LARGE +5.955pp.

## 5. Promote gate (pre-declared)

Require LME gain@0.20 >= +1.0pp AND LoCoMo same sign, >= +0.5pp. Observed: LME +3.086pp, LoCoMo +1.481pp. **Decision: PROMOTE to a preregistered adaptive experiment.**

## 5b. Vs-random qualification (analyst note, part of the verdict)

- The pre-declared gate is absolute (pp thresholds) and it FIRES: PROMOTE. But the session question
  asks "beyond random abstention", and there the picture is split by benchmark.
- LME: model gain sits ABOVE the 10-draw random range at α=0.20 (+3.09 vs max +2.22), α=0.30 (+4.35 vs +3.16),
  α=0.40 (+6.10 vs +4.93); at α=0.10 it is inside (+1.11 vs [0.48,2.09]). COMBO test AUC 0.686.
- LoCoMo: model gain sits INSIDE the random range at every α (α=0.20: +1.48 vs [0.55,2.13]; α=0.40: +3.12 vs
  [1.54,3.02], a hair above max). COMBO test AUC 0.558 ≈ chance; every univariate LoCoMo AUC is 0.43–0.54.
  The LoCoMo "replication" therefore passes the letter of the gate (same sign, ≥+0.5pp) but does NOT
  separate from random abstention.
- Plausible reason (description, not a claim): on LoCoMo, variance/N features are per-ARCHIVE constants
  (10 convs share them across their questions), leaving only per-question distance geometry — which carries
  little fail signal there; on LME every feature varies per question.
- Recommendation: any preregistered adaptive experiment built on this should pre-declare a vs-random
  superiority margin (e.g. model gain > random-range max at α=0.20 on held-out), which the current LoCoMo
  leg would NOT meet as-is.

## 6. Honesty: what this cannot show

- Single learner (logistic IRLS, L2=1.0, train-standardized); one fixed 12-feature set chosen a priori from small-arm geometry + archive stats (+LARGE geometry, still gold-free). No feature search was run; a different set/learner could differ.
- n sizes: LME 470 (train 244 / test 226, test fails 52); LoCoMo 1535 (train 777 / test 758, test fails 112). Test routing n is small on LME; pp gains there are noisy.
- Failure is defined against the full budget (fail = small strictly worse than large); questions where both arms fail identically are NOT fails — routing cannot help them.
- LARGE-arm geometry features (margin34_large, crowd3_large) describe the full budget; a deployable router would need them without paying full-budget cost — they are included as analysis features, not as a deployment claim.
- Correlation/description only: no causal claim — predictable failure need not be fixable failure.
- [LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE].