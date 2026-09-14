> **ORCHESTRATOR ERRATA (2026-09-13, after D5 adversarial review).** F1/C8: the T/M model features (all except `margin`, `top20_entropy`) REQUIRE GOLD QRELS at inference — this is a MECHANISM result, not a deployable-predictor claim; the §4 verdict is downgraded to "cleared the roadmap kill-bar; the tie story graduates to c2 exploration". See ERRATA_ROUND3_D5.md §F1.

# DENEY 2 (c1) — tie-mass decomposition + flip predictor (LME)

**[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

Frozen protocol verbatim (lexsort tie priorities, 20 trials, fractional R@3); numpy only; no network. Factors: per-question frozen pkls (470), ALL-500 lex ordinals, stored natives from pilot_results.json, drop matrix from per_axis_matrices.npz.

## 1. Gates (all must pass; abort otherwise)

| Gate | Recomputed | Expected | Diff |
|---|---|---|---|
| Native mean | 0.5419751773049645 | 0.5419751773049645 | 0.0e+00 |
| TOP48 | 0.34949468085106 | 0.34949468085106 | 0.0e+00 |
| RAND48_s0 | 0.47292553191489 | 0.47292553191489 | 0.0e+00 |
| BOT48 | 0.42845744680851 | 0.42845744680851 | 0.0e+00 |
| per-q native vs stored | max abs diff 0.0e+00 (470/470) | | |

**All gates PASS.**

## 2. Arms (mirror pilots)

- TOP48: `od=np.argsort(var,kind="stable")[::-1]; od[:48]`; BOT48: `od[::-1][:48]` (RTD/E2 convention).
- RAND48: `rng(12000+s).choice(96,48)`, s=0,1,2.
- drop64: top-64 axes by full-data drop utility U_drop=mean(native-FR_drop_a); top-5 axes [94, 83, 72, 27, 88]. **GOLD-INFORMED, analysis-only.**
- Arm FR means: NATIVE=0.5420; TOP48=0.3495; BOT48=0.4285; RAND48_s0=0.4729; RAND48_s1=0.4410; RAND48_s2=0.4382; RAND48_mean=0.4507; DROP64=0.5257

## 3. Flip target

delta = FR(TOP48) - mean(FR RAND48 seeds); win delta>1e-12, tie |delta|<=1e-12, loss below. W/T/L = 91/179/200; mean gap -10.12 pp; median 0.00 pp.
Primary binary target: loss-vs-win, ties excluded (n=291; ties carry no flip direction; an ordinal target would be tie-dominated).
Split: train iff first hex char of sha256("c1|"+qid) even -> train 250 / test 220; binary train n=161 (wins 54), test n=130 (wins 37).

## 4. Held-out AUC (test split; positive class = win)

| Model | Features | Train AUC | Test AUC |
|---|---|---|---|
| T (tie) | tie_mass_at_dgold, margin, strictly_closer | 0.867 | 0.798 |
| M (mean) | d_gold_mean, mean_nongold, min_nongold, top20_entropy | 0.697 | 0.686 |
| T+M | all 7 | 0.874 | 0.806 |

Decision reference: AUC(T)>=0.65 AND AUC(T)-AUC(M)>=0.05 for a predictor claim. Observed: AUC(T)=0.798, AUC(T)-AUC(M)=+0.112.
**Verdict: AUC(T)=0.798 (>=0.65), AUC(T)-AUC(M)=+0.112 (>=0.05) => thresholds CLEARED: tie features carry held-out flip signal; provisional predictor claim licensed by the roadmap rule (single benchmark, exploratory).**

## 5. Standardized coefficients (train fit; + favors win)

- T: bias=-1.873; tie_mass_at_dgold=-1.210; margin=+0.210; strictly_closer_than_gold=-3.118
- M: bias=-0.757; d_gold_mean=-0.779; mean_nongold=-0.061; min_nongold=+0.930; top20_entropy=+0.353
- TM: bias=-1.803; tie_mass_at_dgold=-1.161; margin=+0.244; strictly_closer_than_gold=-2.946; d_gold_mean=-0.130; mean_nongold=-0.112; min_nongold=+0.331; top20_entropy=+0.010

## 6. Per-arm feature table (means: wins vs losses)

| feature | TOP48 win | TOP48 loss | RANDmean win | RANDmean loss | BOT48 win | BOT48 loss | DROP64 win | DROP64 loss |
|---|---|---|---|---|---|---|---|---|
| d_gold_mean | 11.917 | 13.732 | 14.530 | 13.751 | 17.331 | 14.337 | 19.799 | 18.625 |
| d_gold_min | 9.495 | 11.665 | 12.366 | 11.787 | 14.945 | 12.170 | 16.989 | 16.090 |
| tie_mass_at_dgold | 1.868 | 4.500 | 4.106 | 3.138 | 9.516 | 4.295 | 3.308 | 1.990 |
| tie_mass_at_dgold_m1 | 0.286 | 2.225 | 2.095 | 1.237 | 5.143 | 2.120 | 1.253 | 0.800 |
| tie_mass_at_dgold_p1 | 1.582 | 4.400 | 4.249 | 3.408 | 11.945 | 4.830 | 2.505 | 1.750 |
| gold_bucket_size | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| margin | 0.703 | 0.595 | 0.850 | 0.817 | 0.802 | 0.890 | 1.154 | 1.360 |
| strictly_closer_than_gold | 0.549 | 5.505 | 5.234 | 2.892 | 14.308 | 5.010 | 4.044 | 2.150 |
| top20_entropy | 1.794 | 1.777 | 1.600 | 1.605 | 1.447 | 1.483 | 1.741 | 1.739 |
| mean_nongold | 23.918 | 23.905 | 23.954 | 23.983 | 24.022 | 24.063 | 31.956 | 32.001 |
| min_nongold | 9.253 | 9.025 | 10.740 | 11.018 | 11.978 | 11.970 | 15.758 | 15.920 |

## 7. Honesty: what this cannot show

- Single benchmark (LME-470), single representation family; no cross-benchmark claim.
- drop64 is gold-informed (full-data utility) and analysis-only; its FR is not a selection claim.
- Binary target drops ties, shrinking n (test binary n=130); CIs are wide; no CI computed here.
- Model features use TOP48-arm geometry only; arm-difference features might predict better but would bake in the baseline.
- Logistic IRLS is one arbitrary learner (L2 lam=1.0); AUC differences near +/-0.03 are noise-scale at this n.
- Correlation/description only: no causal claim about why top-variance fails; mechanism stays OPEN.
- Margin/entropy use trial-0 ordering (declared); trial-averaged ranks could differ slightly.