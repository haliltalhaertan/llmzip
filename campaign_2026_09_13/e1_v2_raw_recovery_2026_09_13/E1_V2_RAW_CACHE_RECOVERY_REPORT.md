# E1 V2 raw-cache recovery — joint redundancy / ranking-competition mechanism

**Labels:** [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Status: **IMPLEMENTER/LEAD RAW-CACHE RECOVERY — NOT INDEPENDENTLY AUDITED.**

Frozen design source: `research/e1-mechanism-checkpoint-frozen-2026-09-13` /
`E1_PREANALYSIS_SPEC_V2.md` (design parent `775a09c1ba6fd8c28f1e98ec1826d31a7f2c3484`).
The preceding checkpoint was independently audited at
`ec40dc34053a17a4058b51efc7d06038f225c8f0` with `PASS_WITH_FINDINGS`.

Task4F1 stayed `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.

## Recovery provenance

The prior independent audit correctly left raw-C96/qC tests `NOT_RUN / NOT_AVAILABLE`
in its own environment. After that audit, a separate Drive heavy-backup surface was located.
Three downloaded backup archives matched the Drive manifest byte-for-byte:

- `03_regen_caches.tar.gz`: `a16bdf95d3a96cb964fd6fd614d3b49d22bb9329c5afaf81cd692214d50f8aad`
- `04_bench3_runs_caches.tar.gz`: `87d6312ef6c195ac6c161a8693ab635c447074c969f6573a0d0b0ca994219ae4`
- `07_drive_frozen.tar.gz`: `370ea40962b078fc2fc09ab5319942b242f1559adeb62765e271f90cc21a9f59`

Recovered frozen surfaces: 470 LME `C/qC/gold` pickles, 10 LoCoMo `C/QC` pickles plus
audit corrections, 10 REALTALK chat caches, and PerLTQA's 30-archive + 8,265-query caches.
No representation was refit and no evidence mapping was regenerated.

## Headline gates

| benchmark | SIGN96 | centered float | gate status |
|---|---:|---:|---|
| LongMemEval | 0.5419751773049645 | 0.4415957446808511 | both accepted anchors reproduced |
| REALTALK | 0.2247750759878419 | 0.1725340538106495 | both accepted outputs reproduced |
| PerLTQA | 0.4889419949308170 | 0.5516920745288530 | both accepted outputs reproduced |
| LoCoMo | 0.2365471466644105 | 0.1682633454131825 | SIGN accepted anchor exact; float NEW exploratory derivation |

LoCoMo's newly derived centered-float result gives SIGN−float =
**+6.8284 pp**.
This conflicts with the old handoff's approximate `≈+12.0pp programme-reported; not re-derived`
row. No exact old source for ≈12pp was located in the committed campaign surface or recovered
transcript text. The old value is therefore left **UNRESOLVED / NOT AN ANCHOR**; the +6.83pp
result is an auditable frozen-cache candidate pending independent review.

## A — Delta vs P64

`Delta_q = FR_SIGN96 − FR_centered_float96`.
`P64_q = FR_BOT64 − FR_TOP64`.

| benchmark | Spearman rho | descriptive cluster-bootstrap 95% interval |
|---|---:|---:|
| LME | +0.1086 | [+0.0081, +0.2139] |
| REALTALK | +0.0745 | [+0.0024, +0.1579] |
| PerLTQA | +0.1092 | [+0.0831, +0.1335] |
| LoCoMo | +0.2495 | [+0.2146, +0.2881] |

Bootstrap seed/B (`96013`, B=2000) were operationally fixed during raw recovery after point
estimates were already known; intervals are descriptive, not preregistered inference.
P64 is positive on all four, but remains a weak per-query marker rather than a router.

## B/C — binary redundancy structure

TOP64 sign bits are more mutually correlated than BOT64 and BOT64 has higher binary
effective dimension in **every recovered archive**:

- `PHI_GAP > 0`: **520/520**
- `EFFDIM_GAP > 0`: **520/520**

| benchmark | mean PHI_GAP | mean EFFDIM_GAP | rho(Delta_archive,PHI) | rho(Delta_archive,EFFDIM) |
|---|---:|---:|---:|---:|
| LME | 0.012877 | 5.730 | -0.0140 | +0.0001 |
| REALTALK | 0.007327 | 3.422 | +0.3818 | +0.4545 |
| PerLTQA | 0.010581 | 5.982 | +0.1034 | +0.1920 |
| LoCoMo | 0.004010 | 1.640 | +0.4061 | +0.4424 |

Archive-bootstrap intervals cross zero for all PHI/EFFDIM coefficients (especially n=10
REALTALK/LoCoMo). The frozen V2 directional falsifier is not triggered, but archive redundancy
alone is not sufficient: LME is null and PerLTQA loses overall despite a large EFFDIM gap.

The structural result is sharper: **high-variance TOP64 bits carry more binary redundancy;
low-variance BOT64 bits carry more independent binary dimensions.** This structure is universal
in the recovered sample, but query regime decides whether that diversity is useful.

## D — duplicate collapse

Duplicate-code gaps are null/negligible: PerLTQA and LoCoMo have `DUP_GAP=0` in every archive;
REALTALK mean ≈ 0.000642; LME mean ≈ 0.007856,
with LME archive rho -0.0273.
Duplicate collapse alone is not the mechanism.

## E — query-specific ranking competition

The frozen predicted direction is positive on **all four benchmarks**:

| benchmark | rho Delta vs TOP−BOT strictly-closer gap | rho Delta vs TOP−BOT gold-tie-mass gap |
|---|---:|---:|
| LME | +0.0997 | +0.0990 |
| REALTALK | +0.0612 | +0.0872 |
| PerLTQA | **+0.2774** | **+0.2851** |
| LoCoMo | +0.0937 | +0.0953 |

PerLTQA events are strongest:
strictly-closer `rho=+0.3979`,
gold-tie-mass `rho=+0.3892`.
Profile instead has strong Delta–P64 association
`rho=+0.3550` with weak
strict/tie coefficients. More than one local route may therefore produce a SIGN advantage.

## Query magnitude

Delta vs `Q_ABS_CV` is weak on every benchmark:
LME +0.0460,
REALTALK +0.0648,
PerLTQA +0.0122,
LoCoMo +0.0803.
Simple query-magnitude heterogeneity is not the missing explanation.

## V2 disposition

Frozen falsifiers are not triggered:
- P64 is positively associated with Delta in all four now-available benchmarks.
- PHI/EFFDIM do not have wrong/non-positive direction in >=3 benchmark analyses.
- ranking-competition gaps have the predicted positive direction on all four.

But the result does **not** prove causality. The licensed conclusion is:

> TOP64 sign bits are universally more redundant and BOT64 bits universally have higher binary
> effective dimension in the recovered archives. That asymmetry is real but not sufficient to
> determine SIGN-vs-float direction. SIGN advantage is better localized as a query–archive
> ranking-regime interaction. P64 and TOP-vs-BOT ranking-competition gaps are descriptive markers
> of that regime.

A useful working model is a **signal-versus-redundancy tradeoff**: high-variance coordinates
carry stronger marginal signal but more redundant binary information; lower-variance coordinates
can supply more independent binary dimensions. Query semantics/ranking competition decides which
side matters. This remains a mechanism hypothesis.

## Next step

Do not open E2/new codec search yet. Independently audit this exact raw-cache recovery first,
including the backup hashes, anchor gates, new LoCoMo centered-float result, PHI/EFFDIM/DUP
metrics, P64/competition calculations, and the old ≈12pp LoCoMo conflict. If it passes, use an
unseen fifth benchmark for confirmatory generalization.
