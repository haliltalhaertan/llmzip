# E1 V2 raw-cache recovery R2 — corrected mechanism state after independent audit

**Labels:** [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Status: **R2 CORRECTED REPORT / FULL CLAIM-D PAYLOAD RERUN PENDING / RE-AUDIT REQUIRED**.

Parent lead recovery: `d5441698fa8fb8404873af47233569803b887376`.
Independent audit: `010bcbbe0ade15ed1dc501ce6d2f4e2e5ccd89b7`, verdict `REQUEST_CHANGES`.

This report supersedes R1 Claim-D competition numbers and tightens wording for the other audit findings. It does not alter the frozen representation caches or accepted headline gates.

Task4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.

## What survived independent audit

The recovery itself was real and byte-bound. The audit independently matched the three heavy backup archives and found all required frozen surfaces. Non-competition per-query fields and PHI/EFFDIM/DUP archive geometry matched the lead recovery exactly.

Headline gates remain:

| benchmark | SIGN96 | centered float | status |
|---|---:|---:|---|
| LongMemEval | 0.5419751773049645 | 0.4415957446808511 | reproduced |
| REALTALK | 0.22477507598784194 | 0.17253405381064954 | reproduced |
| PerLTQA | 0.4889419949308170 | 0.5516920745288530 | reproduced |
| LoCoMo | 0.23654714666441054 | 0.16826334541318252 | SIGN anchor reproduced; centered float independently derived from frozen cache |

LoCoMo frozen-cache SIGN-minus-float is therefore **+6.828380125122796 pp**. The historical `~+12pp` wording has no recovered frozen centered-float source and is not an anchor.

## Structural binary asymmetry

The audit independently confirmed:

- `PHI_GAP > 0`: 520/520 recovered archives.
- `EFFDIM_GAP > 0`: 520/520 recovered archives.
- disjoint TOP32/BOT32 robustness: 520/520 again for both signs.
- no exact-zero C entries in the recovered sample.
- no duplicate C-hash archive groups.

Licensed wording:

> In all 520 recovered archives, high-variance TOP sign bits are more redundant and low-variance BOT sign bits have higher binary effective dimension under the frozen metrics.

This is sample-wide structure, not a universal law and not a predictor by itself.

Archive-level relationships with SIGN-minus-float remain weak/inconsistent: LME is essentially null; REALTALK and LoCoMo have positive but n=10 fragile correlations; PerLTQA is weakly positive while SIGN loses overall. Structural redundancy asymmetry is therefore not sufficient to determine retrieval outcome.

## P64 remains descriptive

Average-rank Spearman `rho(Delta_q, P64_q)` remains positive on all four:

- LME `+0.1085653`
- REALTALK `+0.0745275`
- PerLTQA `+0.1091675`
- LoCoMo `+0.2494691`

Alternative tied-rank methods materially change magnitude, so P64 is only a descriptive regime marker. It is not a stable effect-size estimate and not a deployable router.

## Corrected ranking competition — Claim D

R1 was numerically wrong here for multi-gold queries because it collapsed all golds to the nearest gold distance and counted once. The independent audit recomputed the frozen per-gold metric.

Corrected point coefficients:

| benchmark | rho Delta vs per-gold TOP−BOT strictly-closer gap | rho Delta vs per-gold TOP−BOT gold-tie gap |
|---|---:|---:|
| LongMemEval | +0.1416863 | +0.1404538 |
| REALTALK | +0.0979391 | +0.1228195 |
| PerLTQA | +0.2541683 | +0.2797878 |
| LoCoMo | +0.0949196 | +0.1037602 |

The predicted direction remains positive on all four benchmarks. This is the main reason the audit judged the defect repairable rather than fatal.

PerLTQA section values under the corrected metric:

- dialogues: strict `+0.1305413`, tie `+0.1112309`
- events: strict `+0.3979063`, tie `+0.3892283`
- profile: strict `+0.0573253`, tie `+0.0187387`
- social_relationship: strict `+0.3042852`, tie `+0.2993013`

The important change in interpretation is that multi-gold sections/benchmarks can no longer use the R1 min-gold numbers. Full corrected per-query rows and corrected bootstrap intervals are still required before Claim D can seek PASS.

## Duplicate codes

Duplicate collapse remains a weak/non-general explanation:

- PerLTQA mean DUP_GAP = 0
- LoCoMo mean DUP_GAP = 0
- REALTALK mean DUP_GAP ≈ 0.000642
- LME mean DUP_GAP ≈ 0.007856 with weak archive association

## Query magnitude

`Delta` vs `Q_ABS_CV` is weak on all four benchmarks. More importantly, under the fixed 96-dimensional definitions:

`Q_EFF = 96 / (1 + Q_ABS_CV^2)`.

The two metrics are algebraically redundant and must not be counted as independent evidence.

## Current mechanism hypothesis

The strongest licensed model is now narrower than R1:

> SIGN-vs-float behaves like a query–archive ranking-regime interaction. High-variance sign coordinates carry more redundancy while low-variance coordinates provide more independent binary dimensions across the recovered sample. Whether that diversity helps retrieval depends on query-specific ranking competition. P64 and correctly computed per-gold competition gaps are descriptive regime markers only.

A `signal-versus-redundancy tradeoff` remains a working hypothesis, not a causal explanation.

## What is still open before PASS

The single blocking R2 task is mechanical, not conceptual:

1. regenerate corrected per-query competition rows from the exact frozen caches;
2. regenerate the descriptive cluster bootstrap from those corrected rows;
3. persist hashes/manifests;
4. independently re-audit the repaired package.

Until then, do not open E2/new-codec promotion on the basis of E1 V2.
