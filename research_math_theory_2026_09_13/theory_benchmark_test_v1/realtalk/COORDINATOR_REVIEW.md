# Coordinator review — REALTALK transfer pilot

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Reran worker verification.py: 23/23 reported checks passed; original 728/705/23 roster and per-QA baseline values match. Independently parsed 10575 unique (qid,group,t) rows covering 705 QA and recomputed primary paired contrasts and whole-archive bootstrap. Raw independent output in COORDINATOR_AGGREGATE.json.

POINT-ESTIMATE ERROR: transfer_runner.py defines eff_low/eff_high as means of bootstrap replicate estimates, not the prespecified mean per-QA endpoint contrast. Correct raw LOW48 estimate = -0.0009360576381852989 = -0.09360576381852989 percentage points. Nominal archive bootstrap 95% CI = [-1.9330018939393943,+1.8490314014998683] pp; this matches the stored CI. Correct HIGH48 raw estimate is the exact opposite (+0.09360576381852989 pp). Original headline estimates must not be used; checker repeated the same estimator mistake and did not catch it.

INTERPRETATION: Negative point estimate, but interval includes substantial effects in either direction. No positive support under the planned rule; statistically inconclusive for a population mean effect, NOT proof that the population transfer hypothesis has been falsified. An exploratory label 'negative' cannot turn failure to detect into proof of absence. Only 10 archive clusters; no familywise significance claim.

Strong pointwise claim is separately contradicted on these evaluated QAs: 41/705 LOW48 queries have a decreasing adjacent sign-minus-float gap. This is evidence against unconditional monotonicity for this chosen proxy on these arrays; it does not refute the conditional synthetic theorem or identify true nuisance coordinates.

RECIPROCAL CONTROL: LOW48(t) and HIGH48(1/t) jointly scale both document and query vectors by a common overall positive factor relative to each other. Their cosine ranking must agree mathematically. All stored per-QA float-recall pairs match exactly (max difference 0), not merely 'about 2e-4' as report says. HIGH48 is therefore not an independent corroborating intervention. Difference between their reported bootstrap point estimates comes from using separate bootstrap samples, not float tie flips.

INVARIANCE EVIDENCE SCOPE: stored full96_float_maxabs_vs_t1 measures recall differences, not raw cosine score ulps or rank arrays. Sign invariance checker similarly compares reported recall, not every encoded byte. Do not claim stronger raw-score/bit-array invariance verification without adding actual checks. Scaling construction analytically preserves sign, but test evidence must be named correctly.

No new codec win; no causal explanation of original benchmark gap established. All original worker reports/scripts/results preserved unchanged beside this correction. Further independent recompute/adversarial audit remains pending.
