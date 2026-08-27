# V52 Task 4C2 — Centering / Sign-Geometry Diagnostic

**VERDICT:** `[LEAD — SIGN/HAMMING ADVANTAGE SURVIVES CENTERED FLOAT CONTROL]`

Fixed-benchmark paired estimands only; 470 shared-session connected questions. No population p-values, confidence intervals, superiority/equivalence/non-inferiority claims.

## Primary quality

| Method | ANY R@3 | ALL R@3 | Fractional R@3 |
|---|---:|---:|---:|
| FLOAT96_UNCENTERED | 61.063830% | 28.936170% | 44.010638% |
| FLOAT96_CENTERED | 61.276596% | 28.723404% | 44.159574% |
| SIGN96_CENTERED | 71.308511% | 38.457447% | 54.197518% |
| ITQ96_CENTERED | 54.276596% | 22.672340% | 37.614113% |

## Paired headline gaps

- Fc - F0 = +0.148936 pp
- S - Fc = +10.037943 pp
- I - Fc = -6.545461 pp
- S - I = +16.583404 pp

Decision variable G=S-Fc=+10.037943 pp, mapped without changing the frozen bands to **[LEAD — SIGN/HAMMING ADVANTAGE SURVIVES CENTERED FLOAT CONTROL]**.

## Protocol gates

- Task 4C1 reproduction: 9/9 metric checks exact within 1e-12.
- Same-input proof: max absolute difference = 0.000e+00.
- Dataset SHA/bytes, adapters, Task4B/Task4C1 sources: PASS.
- Duplicate-ID assertion: PASS.
- Pre-run script SHA remains unchanged at finalization.

## Geometry artifacts

Bit balance, collision, tie, gold/non-gold distance, continuous cosine separation, SIGN-vs-ITQ Spearman distance correlation, and packed binary codes are exported as separate reproducible artifacts.

## Question-level robustness (Fractional R@3)

- SIGN vs centered float: W/T/L = 122/304/44; median gap +0.000000 pp.
- Centered vs uncentered float: W/T/L = 7/458/5; median gap +0.000000 pp.

## Interpretation boundary

This is a controlled fixed-benchmark method comparison. It isolates the effect of archive-mean centering relative to the frozen uncentered continuous reference and asks whether a residual SIGN/Hamming gap remains. It does not establish population causality or cross-benchmark generalization.
