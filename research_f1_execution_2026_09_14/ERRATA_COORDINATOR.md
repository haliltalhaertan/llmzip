[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# ERRATA — two coordinator measurement errors, found and corrected in-session

Both errors were made by the coordinating session (not by a subagent), were caught by reading the
frozen scorer's bytes, and are recorded here because superseded artifacts are preserved with their
correction rather than deleted.

## E1. Double centering

Cached representation matrices on the E1 caches are ALREADY centered: column-mean absolute max
measured at 1.16e-16 (PerLTQA) and 1.55e-16 (LongMemEval). The first coordinator scripts subtracted
the column mean again, producing a different geometry from the frozen one.

## E2. Wrong retrieval metric

The frozen metric is FR@3 (fractional recall: |gold ∩ top3| / |gold|), read from
`origin/research/e1-mechanism-checkpoint-frozen-2026-09-13:campaign_2026_09_13/bench3/b3b_perltqa/step2_eval.py:15-19`
where `met()` returns (any, all, frac) and the third element is used. The first coordinator scripts
used ALL@3 (all golds inside top-3), a strictly harsher metric.

## Effect of the two errors

| quantity | wrong (ALL@3, double-centered) | corrected (FR@3) | frozen reference |
|---|---:|---:|---:|
| LME delta | +9.677305 pp | +10.053783 pp | +10.037943 pp |
| PerLTQA delta | -5.917495 pp | -6.274728 pp | -6.275 pp |
| REALTALK delta | +4.413712 pp | +5.300077 pp | +5.2241 pp |

## Claims retracted as a result

1. **"AQS wins at large N."** Asserted from ALL@3 numbers. Under FR@3 the AQS arm is negative at
   every probed scale (-2.50, -5.36, -2.79, -2.66, -3.86, +0.26 pp; the last is n=60, noise).
   RETRACTED.
2. **The first F1 coefficient table.** Computed under ALL@3; superseded by
   `evidence/f1_results_fr3.json`. Kept under `coordinator/superseded/`.

## Residual difference against the frozen numbers (not an error)

The frozen scorer averages NT=20 seeded tie-break permutations; this session uses the exact
expectation E[FR@K] = (g_strict + g_tied * slots / bc) / |gold|, which is order-independent and
carries no sampling noise. Signature is consistent with sampling noise in the reference: the
residual is smallest on the largest sample (PerLTQA n=8265, +0.000272 pp) and largest on the
smallest (REALTALK n=705, +0.075977 pp).
