# V52 Task 4C3 — Accepted Numerical Checkpoint

Date: 2026-08-28

## Status

- `[AUDITED — TASK 4C3 PASS WITH CONDITIONS]`
- `[FROZEN — TASK 4C3 NUMERICAL CHECKPOINT]`
- `[ESTABLISHED ON FROZEN LONGMEMEVAL — NATIVE AXIS-STRUCTURE EFFECT]`
- `[NOT ESTABLISHED — VARIANCE-HETEROGENEITY CAUSAL MEDIATOR]`
- `[NOT ESTABLISHED — CROSS-BENCHMARK GENERALIZATION]`
- `[STOP — NO TASK 4C4 / LOCOMO / RESCUE FROM THIS AUDIT]`

Independent audit source: `audit_v52_t4c3/AUDIT_REPORT.md`, accepted into `main` via PR #1.

## Frozen result

Primary cohort: 470 non-`_abs` LongMemEval questions.

- Native SIGN96 Fractional Evidence Recall@3: `54.197517730496%`
- Full-Haar96 mean Fractional Evidence Recall@3: `38.271666666667%`
- `D96 = -15.925851063830 pp`
- All five preregistered Haar96 seeds are below native.
- Signed-permutation control: exact PASS.
- Continuous orthogonal invariance: PASS; maximum deviation `1.1102230246251565e-15`, below the frozen `1e-12` gate.

Preregistered decision:

`[STRONG AXIS-STRUCTURE EFFECT — FULL ORTHOGONAL MIXING HURTS SIGN RETRIEVAL]`

## Block-mixing gradient

| block size | Fractional R@3 | gap vs native |
|---:|---:|---:|
| 2 | 50.393085% | -3.804433 pp |
| 4 | 47.261950% | -6.935567 pp |
| 8 | 43.695390% | -10.502128 pp |
| 16 | 40.634752% | -13.562766 pp |
| 32 | 39.425709% | -14.771809 pp |
| 96 | 38.271667% | -15.925851 pp |

The gradient is strictly monotone across the preregistered block sizes; `rho(log2 b, gap) = -1.0` is descriptive only.

## Robustness / concentration

Native vs mean Haar96 at question level:

- native better / tie / native worse: `245 / 138 / 87`
- median native advantage: `+4.75 pp`
- after removing the top 50 positive contributors, remaining mean native advantage: `+8.560675 pp`

This supports a broad fixed-benchmark effect rather than a result explained entirely by a tiny handful of questions. It is not a population inference.

## Mechanism boundaries

Rotation strongly flattens coordinate-variance heterogeneity, but the preregistered heterogeneity-alignment condition failed:

`[HETEROGENEITY-ALIGNMENT NOT CONSISTENT]`

Therefore the checkpoint does **not** establish variance heterogeneity as the causal mediator.

ITQ96 Fractional R@3 is `37.614113%`, inside the five-seed full-Haar96 range `36.139539%..40.127837%`:

`[ITQ WITHIN FULL-HAAR ENVELOPE]`

This does not imply ITQ is mathematically equivalent to random Haar rotation.

## Accepted scientific statement

On the frozen 470-question LongMemEval benchmark and sealed centered 96D representation, preregistered data-independent full orthogonal mixing preserved centered continuous geometry to numerical precision while reducing mean Fractional Evidence Recall@3 from `54.1975%` to `38.2717%` (`D96 = -15.9259 pp`), with all five Haar seeds below native. Therefore preserving native coordinate axes materially matters for zero-threshold sign/Hamming retrieval on this frozen benchmark.

## Provenance conditions retained

The independent audit found no scientific defect and quantified the observed governance/temporal-attestation defect effect on D96 as `0.000 pp`. Remaining conditions:

- the full 277 MB dataset was not independently re-downloaded/re-hashed in the audit environment;
- adapter sources were inspected and sealed runtime hashes matched, but their raw-byte SHA256 values were not independently recomputed in that audit environment;
- the heterogeneity temporal-freeze work flag is not a canonical output artifact, although the deterministic quintile assignment reconstructs exactly.

These are provenance conditions, not observed result mismatches.

## Stop rule

Do not launch Task 4C4, LoCoMo, larger-scale benchmark runs, alternate widths, thresholds, rotations, or rescue experiments as a continuation of this audit. A new branch requires a separate Head Researcher decision and a new preregistration.
