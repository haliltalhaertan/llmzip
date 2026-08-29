# V52 Task 4D — Accepted Numerical Checkpoint

Date: 2026-08-29

## Status

- `[AUDITED — TASK 4D PASS WITH CONDITIONS]`
- `[FROZEN — TASK 4D NUMERICAL CHECKPOINT]`
- `[ESTABLISHED ON FROZEN LOCOMO — NATIVE AXIS-STRUCTURE EFFECT]`
- `[CROSS-BENCHMARK REPLICATION ESTABLISHED — LONGMEMEVAL + LOCOMO]`
- `[NOT ESTABLISHED — GENERALIZATION BEYOND LONGMEMEVAL + LOCOMO]`
- `[NOT ESTABLISHED — CAUSAL MEDIATOR]`

## Independent audit

Independent cold-start audit verdict: `PASS WITH CONDITIONS`.
Audit level: FULL RAW-TABLE + SEALED-SOURCE + FULL OUTPUT HASH-CHAIN/ZIP + CONTROL RECONSTRUCTION.
Chain of custody: PASS.
Preregistration temporal integrity: PASS.
Scientific defect found: NO.

Dataset/correction identity remains conditional only because the auditor did not independently re-download and re-hash the upstream original dataset and all 20 source correction JSONs. The sealed runtime verified the frozen dataset SHA, 10 conversations, 1,540 questions, 156 corrections, zero unmatched corrections, and frozen audit semantics.

## Frozen primary estimand

Frozen LoCoMo cohort: 1,540 Cat1–Cat4 questions.
Primary retrieval estimand: 1,535 audit-clean questions with at least one retrievable gold evidence item.

The five zero-retrievable-gold questions are excluded by the frozen retrievable-gold semantics, not outcome-dependent filtering. The earlier wording that could be read as treating all 1,540 questions as the retrieval denominator is classified as a non-load-bearing estimand/documentation defect.

Sensitivity:
- zero-imputation shift in D: `+0.032091 pp`
- conservative adversarial maximum shift: `0.356766 pp`
- strong preregistered verdict survives.

## Frozen result

- NATIVE_SIGN96 Fractional Evidence Recall@3: `23.654714666441%`
- Full-Haar96 mean Fractional Evidence Recall@3: `13.770827054136%`
- `D_LoCoMo = Haar - Native = -9.883887612305 pp`
- all five preregistered Haar96 seeds below native: YES
- signed-permutation control: PASS
- continuous orthogonal invariance: PASS; max error `1.6653345369377348e-15`

Haar seed values:
- 43001: `12.991972305653%`
- 43002: `13.805874420588%`
- 43003: `14.360296073814%`
- 43004: `13.537524120299%`
- 43005: `14.158468350325%`

Pre-registered verdict reproduced:

`[STRONG CROSS-BENCHMARK REPLICATION — NATIVE AXES MATTER ON LOCOMO]`

## Robustness

Native vs mean Haar96 at question level:
- W/T/L = `361 / 992 / 182`
- median paired gap = `0.000000 pp`
- after removing top 50 native-positive contributors, residual native advantage = `+6.849675073999 pp`

Category native-minus-Haar gaps:
- Cat1 `+4.271408 pp`
- Cat2 `+13.922917 pp`
- Cat3 `+1.614823 pp`
- Cat4 `+11.133571 pp`

All 10 conversations are positive:
- locomo_0 `+7.014444 pp`
- locomo_1 `+9.868313 pp`
- locomo_2 `+7.127741 pp`
- locomo_3 `+9.619765 pp`
- locomo_4 `+16.704387 pp`
- locomo_5 `+7.252033 pp`
- locomo_6 `+4.487360 pp`
- locomo_7 `+15.759860 pp`
- locomo_8 `+7.765298 pp`
- locomo_9 `+10.044872 pp`

## ITQ reference

ITQ96 Fractional Evidence Recall@3: `14.220856478786%`.
`[ITQ WITHIN FULL-HAAR ENVELOPE]`.
This does not establish that ITQ is mathematically equivalent to random Haar rotation.

## Protocol-defect sensitivity

Raw-vs-audit change in D_LoCoMo on the common-valid 1,534-question set: `-0.097787194 pp`.
Maximum quantified defect effect on D_LoCoMo: `0.356766 pp`, the conservative adversarial upper bound for the 1,540-vs-1,535 wording/denominator issue.
No quantified defect is large enough to erase the observed `-9.8839 pp` effect.

## Cross-benchmark scientific state

LongMemEval frozen/audited Task 4C3 showed the same directional intervention: native SIGN96 materially outperformed full orthogonal Haar mixing while centered continuous geometry was preserved.

Task 4D independently reproduces that native-basis sensitivity on full-real LoCoMo under a separately preregistered protocol.

Accepted cross-benchmark statement:

> Across the frozen LongMemEval and LoCoMo conversational long-term-memory evidence-retrieval benchmarks, preserving the native coordinate basis materially improves zero-threshold sign/Hamming retrieval relative to data-independent full orthogonal mixing, while the centered continuous geometry is preserved to numerical precision.

This is an empirical cross-benchmark result, not a universal theorem.

## Interpretation ceiling

Do NOT claim yet:
- universal native-axis superiority;
- population-level generalization beyond the two frozen benchmarks;
- variance heterogeneity, collisions, ties, or occupancy as the causal mediator;
- ITQ is equivalent to random Haar rotation;
- all embedding families have meaningful native coordinate axes;
- production latency/RAM superiority.

## Provenance conditions

- Upstream original LoCoMo dataset and all source correction JSONs were not independently re-downloaded/re-hashed in the audit environment.
- Runtime dataset/correction identity checks passed under sealed source.
- These are provenance conditions, not observed result mismatches.

## Head Researcher decision

`TASK 4D NUMERICAL CHECKPOINT MAY FREEZE: YES`

Task 4D is frozen with the 1,535 evidence-valid primary denominator stated explicitly.
Task 4E / LongMemEval-V2 requires a separately authorized and preregistered scientific branch; it is not a continuation of this audit.
