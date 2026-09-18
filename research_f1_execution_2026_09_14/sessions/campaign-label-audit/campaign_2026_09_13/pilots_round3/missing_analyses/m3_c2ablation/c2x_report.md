# c2x — MISSING-3 ablation package (D5 follow-up to c2)

**[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]. Numpy only; no network; read-only on /mnt/c. Machinery replicated from c2.py VERBATIM (SMALL=SPREAD48 repaired rank-linspace, LARGE=NATIVE96, sha256(c2|qid) split, logistic IRLS lam=1.0, routing gain with abstain-top-alpha predicted-fail, random baselines rng(20260913+i)); only OUT dir/filenames changed.

## 0. Reproduction gate (abort on fail — all PASS)

| Check | Recomputed | Reference | Tol | Diff |
|---|---|---|---|---|
| LME gain@0.20 pp | +3.086283 | +3.086000 | 0.005 | 0.000283 PASS |
| LOCO gain@0.20 pp | +1.481028 | +1.481000 | 0.005 | 0.000028 PASS |
| LME random-mean@0.20 pp | +1.833481 | +1.833000 | 0.005 | 0.000481 PASS |
| LOCO random-mean@0.20 pp | +1.134598 | +1.135000 | 0.005 | 0.000402 PASS |
| LME COMBO test AUC | +0.686229 | +0.686000 | 0.002 | 0.000229 PASS |
| LOCO COMBO test AUC | +0.557635 | +0.558000 | 0.002 | 0.000365 PASS |

## 1. LARGE-free ablation (drop margin34_large, crowd3_large)

Audit: the only features computed from the per-question full-budget (LARGE) retrieval ordering are margin34_large and crowd3_large — both dropped. Kept: margin34, crowd3, crowd4, crowd_pm1, top3_tie_share, boundary_share (SMALL arm only); N (archive size, free); var_decay (96-dim archive variance, per-archive precomputable, no per-question LARGE run); qent (query sign entropy, redefinable on SMALL bits); dup_top20 (BORDERLINE: top20 selected by SMALL ordering but distinctness evaluated on full-96-bit codes — kept in primary FREE10, dropped in STRICT9 sensitivity).

| Benchmark | Variant | Test AUC | gain@0.10 | gain@0.20 | gain@0.30 | gain@0.40 (pp) |
|---|---|---|---|---|---|---|
| LME | FREE10 (primary) | 0.6702 | +0.900 | +1.973 | +4.421 | +6.335 |
| LME | STRICT9 (no dup_top20) | 0.6660 | +0.900 | +2.128 | +4.185 | +6.335 |
| LOCO | FREE10 (primary) | 0.5683 | +0.667 | +1.185 | +2.378 | +2.908 |
| LOCO | STRICT9 (no dup_top20) | 0.5723 | +0.641 | +1.502 | +2.411 | +3.243 |
| LME | full COMBO (ref) | 0.6862 | +1.110 | +3.086 | +4.347 | +6.103 |
| LOCO | full COMBO (ref) | 0.5576 | +0.529 | +1.481 | +1.939 | +3.120 |

FREE10 remaining features (standardized coef, bias first):
- LME: bias=-1.150, margin34=-0.539, crowd3=+0.051, crowd4=+0.090, crowd_pm1=-0.024, top3_tie_share=+0.152, boundary_share=+0.153, dup_top20=-0.157, var_decay=-0.151, N=+0.161, qent=+0.223
- LOCO: bias=-1.652, margin34=-0.380, crowd3=+0.105, crowd4=+0.088, crowd_pm1=-0.174, top3_tie_share=-0.392, boundary_share=+0.210, dup_top20=+0.113, var_decay=+0.201, N=-0.193, qent=+0.070

## 2. Gain CIs (paired bootstrap over test questions, B=2000, gain@0.20)

Fixed train-fit scores, resampled test evaluation; same resamples for full vs free (paired). 90% CI = 5th/95th percentiles. Seeds: LME 20260914, LOCO 20260915.

| Benchmark | Model | Mean gain (pp) | 90% CI (pp) |
|---|---|---|---|
| LME | full | +2.890 | [+1.593, +4.421] |
| LME | free | +2.144 | [+1.088, +3.293] |
| LME | paired free-minus-full | -0.746 | [-2.087, +0.332] |

| LOCO | full | +1.426 | [+0.688, +2.165] |
| LOCO | free | +1.217 | [+0.420, +2.003] |
| LOCO | paired free-minus-full | -0.210 | [-0.728, +0.317] |

## 3. Formal vs-random test (200 draws, rng(20260913+i), k=round(alpha*n))

One-sided p = fraction of random draws with gain >= model gain; percentile = % draws <= model. Bonferroni x4 across alphas per benchmark; beats-random iff p_bonf < 0.05.

| Benchmark | alpha | Model gain (pp) | Random mean [min,max] (pp) | Percentile | p_raw | p_bonf | Verdict |
|---|---|---|---|---|---|---|---|
| LME | 0.10 | +1.110 | +0.981 [-0.232,+2.533] | 62.0 | 0.3800 | 1.0000 | inside-noise |
| LME | 0.20 | +3.086 | +1.787 [+0.164,+3.540] | 95.5 | 0.0450 | 0.1800 | inside-noise |
| LME | 0.30 | +4.347 | +2.648 [+0.779,+4.275] | 100.0 | 0.0000 | 0.0000 | beats-random |
| LME | 0.40 | +6.103 | +3.506 [+0.732,+5.680] | 100.0 | 0.0000 | 0.0000 | beats-random |
| LOCO | 0.10 | +0.529 | +0.537 [-0.204,+1.330] | 46.5 | 0.5350 | 1.0000 | inside-noise |
| LOCO | 0.20 | +1.481 | +1.170 [+0.098,+2.543] | 80.0 | 0.2000 | 0.8000 | inside-noise |
| LOCO | 0.30 | +1.939 | +1.819 [+0.528,+3.546] | 62.0 | 0.3800 | 1.0000 | inside-noise |
| LOCO | 0.40 | +3.120 | +2.315 [+1.023,+4.009] | 92.5 | 0.0750 | 0.3000 | inside-noise |

LARGE-free variant vs-random (same test, for the deployability question):
| Benchmark | alpha | Free gain (pp) | Percentile | p_raw | p_bonf | Verdict |
|---|---|---|---|---|---|---|
| LME | 0.10 | +0.900 | 46.0 | 0.5400 | 1.0000 | inside-noise |
| LME | 0.20 | +1.973 | 63.5 | 0.3650 | 1.0000 | inside-noise |
| LME | 0.30 | +4.421 | 100.0 | 0.0000 | 0.0000 | beats-random |
| LME | 0.40 | +6.335 | 100.0 | 0.0000 | 0.0000 | beats-random |
| LOCO | 0.10 | +0.667 | 67.0 | 0.3300 | 1.0000 | inside-noise |
| LOCO | 0.20 | +1.185 | 52.0 | 0.4800 | 1.0000 | inside-noise |
| LOCO | 0.30 | +2.378 | 90.5 | 0.0950 | 0.3800 | inside-noise |
| LOCO | 0.40 | +2.908 | 87.0 | 0.1300 | 0.5200 | inside-noise |

## 4. Preregistration readiness

c2 is NOT prereg-ready as-is: the LoCoMo leg is vacuous vs random-abstention (inside-noise at every alpha after Bonferroni; COMBO test AUC 0.558), and the router as specified pays the full budget to compute its LARGE-arm features. The binding gate for any future c2 preregistration: on held-out data, model gain@0.20 must exceed the max (not the mean) of >=200 same-protocol random-abstention draws, separately per benchmark; the LARGE-free variant must be the registered model (no full-budget features at routing time). LoCoMo must NOT be called a replication unless that gate fires there too.

## 5. Honesty: what this cannot show

- n: LME 470 (train 244 / test 226, test fails 52); LoCoMo 1535 (train 777 / test 758, test fails 112). Test routing n is small on LME; pp gains and CIs there are noisy.
- Single learner (logistic IRLS, L2=1.0, train-standardized); fixed a-priori feature sets (12 full, 10 LARGE-free, 9 strict). No feature search; a different set/learner could differ.
- Failure = small strictly worse than large (FR_small < FR_large - 1e-12); identically-failing questions are not routable by construction.
- Bootstrap fixes the train fit and resamples only test evaluation: CIs cover test-sampling noise, not train-fit or split arbitrariness (single fixed sha256 split).
- Random-abstention draws share one seed protocol; p-values are exact only w.r.t. that null (uniform random subsets of size k). Bonferroni x4 is per benchmark; no correction across benchmarks or model variants.
- dup_top20/var_decay/qent caveats (see audit): LARGE-free means free of the per-question LARGE retrieval pass, not free of all full-bank statistics.
- [LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE].