# V52 — Full-Haar Denominator: Sensitivity and Partial Closure

**Date:** 2026-09-06
**Track:** research (mechanism line). Canonical `main` unchanged by this document.
**Status:** `[DENOMINATOR UNCERTAINTY PARTIALLY COSTED — ADDITIVE. NO NEW EXPERIMENT. NO OUTCOME ACCESS.]`
**Applies to:** the inherited `frozen_full_haar_R3` denominator used by every
`rho` in the mechanism line on both benchmarks.

Additive. Rewrites nothing, retracts no number, supersedes no artifact.

---

## 1. The claim this document corrects

The boundary-localization audit and every record since have carried this:

> The Full-Haar denominator is inherited and its sampling uncertainty is
> **quantified nowhere in this package** — the single largest un-costed source
> of uncertainty in the line.

For LongMemEval that is **not true**, and has not been true since 2026-08-28.

## 2. The LongMemEval denominator is traceable, and its dispersion is measurable

`audit_v52_t4c3/AUDIT_REPORT.md` — on canonical `main`, sha256
`8f6b31050c6e211b7c34ba8214405cff91251d33bd590be97c996ce17f2be238`, the accepted
**independent** Task 4C3 audit — publishes the five per-seed full-Haar Fractional
R@3 values (`BLOCK_ORTHO_SIGN96`, `block_size = 96`, rotation seeds
`43001..43005`, 470 questions, 20 nuisance trials):

| seed | full-Haar R@3 |
|---|---|
| 43001 | 0.361395390 |
| 43002 | 0.391393617 |
| 43003 | 0.379320922 |
| 43004 | 0.380195035 |
| 43005 | 0.401278369 |

Their mean is `0.3827166666`, agreeing with the denominator in use
(`0.38271666666667`) to `6.7e-11` — exactly the residual expected from that
report's nine published decimal places. **The denominator in use is that
five-seed mean.** Its dispersion follows directly:

| quantity | value |
|---|---|
| sample sd | `0.014935802685146212` |
| standard error (n=5) | `0.0066794940205021636` |
| relative standard error | **1.745 %** of the denominator |
| seed envelope | `[0.361395390, 0.401278369]` |
| 95 % t interval (t₍.₉₇₅,₄₎ = 2.776) | `[0.364174391, 0.401258942]` |

## 3. Breakdown analysis: how wrong would the denominator have to be?

Because `rho = (native − arm) / (native − full_haar)` has a fixed numerator,
`rho` **rises** as the denominator rises toward native. For each arm there is a
single denominator value at which the verdict crosses the preregistered `0.25`
gate. Those values are computed in
`research/v52/audit_support/denominator_sensitivity.py`.

**LongMemEval** — every breakdown point lies **outside** the 95 % interval:

| arm | rho | verdict | shift needed | in SE | inside 95 % CI |
|---|---|---|---|---|---|
| B16 | 0.8048 | not sufficient | −92.35 % | 52.9 | no |
| B24 | 0.5765 | not sufficient | −54.35 % | 31.1 | no |
| **B32** | **0.1619** | **sufficient** | **+14.67 %** | **8.4** | **no** |
| **B48** | **0.1939** | **sufficient** | **+9.34 %** | **5.4** | **no** |
| B64 | 0.3600 | not sufficient | −18.31 % | 10.5 | no |
| RANDOM32 | 0.9909 | not sufficient | −123.33 % | 70.7 | no |

**No LongMemEval verdict is threatened by the denominator's measured sampling
uncertainty.** The tightest, `B48`, needs a 5.4-standard-error excursion. On this
benchmark the "largest un-costed source of uncertainty" is now costed, and it is
not load-bearing.

**LoCoMo** — no per-seed source is committed anywhere, so the dispersion is
**not measurable** and this document does not invent one. Only the breakdown
points can be given:

| arm | rho | verdict | shift needed |
|---|---|---|---|
| B16 | 0.8230 | not sufficient | −164.52 % |
| B24 | 0.5268 | not sufficient | −79.46 % |
| **B32** | **0.0824** | **sufficient** | **+48.12 %** |
| **B48** | **0.3034** | **excluded** | **−15.34 %** |
| B64 | 0.5309 | not sufficient | −80.63 % |
| RANDOM32 | 0.9372 | not sufficient | −197.29 % |

The LoCoMo `B32` **sufficiency** is the most robust verdict anywhere in the
line: the denominator would have to be understated by nearly half. The LoCoMo
`B48` **exclusion** is the least robust: it is lost if the true denominator is
about 15 % lower than recorded.

## 4. Two independent lines converge on the same single item

The Gate S bootstrap flagged one fragile item: the LoCoMo `B48` exclusion at
`rho = 0.303`, on which the uniqueness of `S_common = {32}` rests. This
denominator analysis, which uses no bootstrap and no resampling, arrives at the
same item from a different direction — `B48` is also the tightest breakdown
point on LoCoMo, by a factor of five over the next arm.

That convergence sharpens the standing narrowing rather than changing it. The
established finding — that **which** coordinates form the leading block matters,
not merely 32/64 block structure — is untouched: it rests on arms that need a
54 % to 197 % denominator error to overturn. What remains conditional is the
**uniqueness** of 32 on the tested grid, and the reason is now named twice by
two independent methods.

## 5. Scope, and what this is not

- Arithmetic on committed declared numbers and on one independently audited
  artifact. No corpus was read, no seed drawn, no retrieval computed, no
  experiment designed or run.
- The LongMemEval standard error is **not** transferred to LoCoMo. LoCoMo's
  denominator dispersion remains unmeasured; only the consequence of an error in
  it is bounded.
- `n = 5` is a small sample and the interval is a Student-t interval on five
  points. It is a real measurement, not a precise one.
- A breakdown point says how large an error would have to be, not how likely
  one is. Nothing here suggests any recorded denominator is wrong.

## 6. Disclosure of an error in this document's own tooling

The first version of `denominator_sensitivity.py` stated the direction of the
effect backwards — that `rho` falls as the denominator rises. It does the
opposite. The error was caught by this document's own directional control before
any number was published, and it changed only the direction labels; the
breakdown points and magnitudes were unaffected. The control that caught it is
retained in `test_denominator_sensitivity.py` with a comment recording why it is
there. **41/41 controls pass.**

## 7. What is now open, restated

- **LoCoMo denominator dispersion: still unmeasured**, and unmeasurable from
  bytes. Closing it requires re-running the frozen full-Haar arm over a seed
  panel and committing the per-seed values, as Task 4C3 did for LongMemEval.
  That is an experiment requiring authorization and is not proposed here.
- The LongMemEval half of the open item is **discharged** and should be recorded
  as such rather than carried forward unchanged.

## 8. Standing constraints observed

Task 4F1 untouched: SEALED (V3 `e906c6d2…`) / RUN BLOCKED / NO AUTHORIZATION /
OUTCOME ACCESS FORBIDDEN. No 4F1 payload, candidate, manifest, or audit
namespace was read or modified. No finer boundary scan, adaptive localization,
knee search, or new mechanism experiment was performed or prepared.
