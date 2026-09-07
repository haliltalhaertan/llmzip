# V52 — LoCoMo Full-Haar Denominator: Dispersion Measured, Consequence Costed

Date: 2026-09-07
Status: `[ADDITIVE ADDENDUM — ARITHMETIC ON COMMITTED BYTES; NOT INDEPENDENTLY AUDITED]`
Author: Continuity Lead / co-chair. Companion to
`V52_FULL_HAAR_DENOMINATOR_SENSITIVITY_ADDENDUM_2026-09-06.md` (L-051), which costed the LongMemEval
side and could only *bound* the LoCoMo side because no LoCoMo full-Haar seed panel was committed.
Nothing frozen is replaced. No corpus read, no seed drawn, no retrieval computed here.

## 1. What changed

The coordinate-scale stage (result commit `bce57b64`, checkpoint `1c725a56`) ran a fresh ten-seed
full-Haar arm, `FULLHAAR_FRESH` (seeds `59001..59010`), on the same frozen LoCoMo pipeline and
persisted per-question rows. That is exactly the "re-run over a seed panel" that L-051 and the
takeover prompt §7C said would be needed to measure the LoCoMo denominator's dispersion.

This document derives everything from those rows and from the committed boundary-localization
summary, via `research/v52/audit_support/locomo_denominator_dispersion.py` (evidence JSON beside
it; 16 controls in `test_locomo_denominator_dispersion.py`, including a negative control that
forces the `B48` breakdown *inside* the interval so the check is shown able to fail).

## 2. The measurement

| quantity | value |
|---|---:|
| fresh ten-seed full-Haar mean | 0.139131063 |
| sample sd across seeds | 0.005200 (3.78% of the inherited denominator) |
| se of a **five**-seed mean (the inherited denominator was one) | 0.002326 (1.69%) |
| se of the ten-seed mean | 0.001644 |
| inherited denominator (frozen, unchanged) | 0.13770827054136 |
| fresh − inherited | +0.001423 = **+0.27 sd** |
| 95% Student-t interval around the inherited value, as a five-seed mean | [0.131253, 0.144164] |

The inherited five-seed mean and the fresh ten-seed panel are independent draws under the same
pipeline; they agree to about a quarter of a standard deviation. This is consistency, not identity,
and it is not a re-measurement of the original five seeds (which remain uncommitted).

## 3. Consequence for the boundary-localization verdicts (LoCoMo)

Breakdown points re-derived from the committed `locomo_boundary_summary.json` (every recorded `rho`
re-derives to better than `1e-9`); shifts are relative to the inherited denominator.

| arm | rho | verdict | shift needed | in se (5-seed) | in sd | breakdown outside the 95% interval |
|---|---:|---|---:|---:|---:|---|
| B16 | 0.8230 | not sufficient | −164.52% | −97.4 | −43.6 | yes |
| B24 | 0.5268 | not sufficient | −79.46% | −47.1 | −21.0 | yes |
| **B32** | **0.0824** | **sufficient** | **+48.12%** | **+28.5** | **+12.7** | **yes** |
| **B48** | **0.3034** | **excluded** | **−15.34%** | **−9.1** | **−4.1** | **yes** |
| B64 | 0.5309 | not sufficient | −80.63% | −47.8 | −21.4 | yes |
| RANDOM32 | 0.9372 | not sufficient | −197.29% | −116.8 | −52.3 | yes |

**Every LoCoMo breakdown point lies outside the 95% interval.** The tightest, the `B48` exclusion
on which the *uniqueness* of `S_common = {32}` rests, would need the denominator to be 9.1 standard
errors (4.1 seed-sd) below its recorded value. L-051 recorded the LongMemEval `B48` at 5.4 se; the
LoCoMo `B48` is, by this measurement, less fragile than that, not more.

## 4. What this does and does not close

- **Closed:** the LoCoMo denominator's sampling dispersion is now measured from committed bytes; the
  item can no longer be described as "unmeasurable from bytes". The consequence is costed on both
  benchmarks by the same method.
- **Unchanged:** the standing narrowing. `[PC32-LOCALIZED SUFFICIENCY LEAD — ON TESTED GRID]` and
  `[BOUNDARY-SET HETEROGENEITY PRESENT]` still travel together; uniqueness of 32 remains conditional
  on the ten-seed panel and on the inherited denominator, as the audit bound it. This document says
  the denominator's *sampling* uncertainty does not threaten it; it says nothing about systematic
  error, and a breakdown point is not a probability.
- **Not done:** the frozen denominators are not replaced; no verdict is recomputed with the fresh
  mean; the inherited five per-seed values are still not committed anywhere.
- **Independence:** the panel comes from a stage this author prepared and triggered. The
  coordinate-scale audit (gate G12) is asked to reproduce the panel statistics; until then this
  addendum carries `[NOT INDEPENDENTLY AUDITED]`.

## 5. Outcome boundary

LoCoMo/LongMemEval mechanism track only. No Task 4F1 artifact, candidate, seal, authorization, HMAC
material or outcome touched; Task 4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME
ACCESS FORBIDDEN`.
