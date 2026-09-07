# Synthetic design pilot for the coordinate-scale draft — findings

Status: `[SYNTHETIC PILOT — NO REAL CORPUS, NO REAL OUTCOMES, NO TASK 4F1]`
Date: 2026-09-05

Run **before** anything in the draft is frozen, to test the *design* rather than the hypothesis.
All data is synthetic: 96 coordinates whose per-coordinate standard deviation decays geometrically,
documents drawn i.i.d. under that profile, and a query built as a noisy copy of its gold document.
No benchmark corpus was read. No retrieval outcome from LoCoMo, LongMemEval or BEAM was touched.

Scripts: `pilot_01_identity_and_direction.py`, `pilot_02_heterogeneity_sweep.py`,
`pilot_03_floor_artifact_test.py`.

## Finding 1 — the identity holds exactly, as the design requires

`sign(xD) = sign(x)` held **exactly** in float64 for every archive and every query, and
`SCALED_NATIVE` reproduced `NATIVE` identically. Zero degenerate coordinates arose at `eps = 1e-12`
in this regime. The draft's §6 identity arm is implementable as specified.

## Finding 2 — the qualitative shape of the real result reproduces

As heterogeneity `CV(sigma)` grows, full-Haar mixing becomes catastrophic while block-32 mixing does
not, which is the shape observed on the real benchmarks:

| decay | CV(sigma) | NATIVE | FULL | B32 |
|---|---:|---:|---:|---:|
| 0.99 | 0.279 | 0.9444 | 0.9294 | 0.9406 |
| 0.97 | 0.793 | 0.9444 | 0.7450 | 0.8689 |
| 0.95 | 1.224 | 0.9444 | 0.5622 | 0.7594 |
| 0.92 | 1.732 | 0.9444 | 0.3917 | 0.5944 |
| 0.90 | 2.013 | 0.9444 | 0.3156 | 0.5311 |
| 0.85 | 2.605 | 0.9444 | 0.2056 | 0.3939 |

This is a synthetic model, not evidence about the real pipeline. It shows only that a
heterogeneity-driven account can *produce* this shape.

## Finding 3 — the draft's proposed primary estimand is confounded. This is a defect in the draft.

The draft proposed the interaction on a percentage-point scale, `I = delta_full - delta_block`, with
a "supported" band at `I >= +3.0 pp`.

In the pilot `I` is enormous — `+13` to `+22` pp across the whole heterogeneous range — and it would
have been read as strong support for scale participating *differentially* in full mixing.

It is almost entirely a **floor artifact**:

| decay | CV(sigma) | I (pp) | frac_full | frac_block | I on the fraction scale |
|---|---:|---:|---:|---:|---:|
| 0.99 | 0.279 | +1.67 | 1.407 | 1.143 | +0.265 |
| 0.97 | 0.793 | +12.94 | 1.031 | 1.007 | +0.023 |
| 0.95 | 1.224 | +20.28 | 1.016 | 1.003 | +0.013 |
| 0.92 | 1.732 | +20.83 | 1.011 | 1.002 | +0.009 |
| 0.90 | 2.013 | +22.11 | 1.010 | 1.001 | +0.008 |
| 0.85 | 2.605 | +19.39 | 1.008 | 1.001 | +0.007 |

where `frac_arm = (scaled - unscaled) / (native - unscaled)` is the share of that arm's own loss that
rescaling recovers.

**Both arms recover essentially 100% of their own loss.** Full mixing shows a larger
percentage-point gain only because it had more loss available. On the fraction scale the interaction
nearly vanishes.

Had the draft been frozen as written, a large positive `I` would have been reported as "rescaling
helps full mixing much more than block mixing" when the correct reading in this model is "rescaling
restores **both**, and the pp gap is baseline-driven."

## Consequence — the draft's section 7 is revised before freezing

- The **primary** quantity becomes `frac_full` and `frac_block`, reported per arm.
  `frac ~ 1` means relative coordinate scale accounts for essentially all of that arm's damage;
  `frac ~ 0` means it accounts for none of it.
- The interaction is retained but **only on the fraction scale**, and demoted to secondary.
- The percentage-point interaction is retained as a **descriptive** figure and is explicitly barred
  from carrying the verdict.
- This reintroduces a denominator, which the draft had tried to avoid. That is now a conscious trade:
  the denominator `native - unscaled` is **measured within this experiment**, not inherited, and both
  arms' denominators must be reported with their per-seed dispersion.

This resolves the draft's open question 4 empirically rather than by preference.

## Finding 4 — rescaling can overshoot native

At low heterogeneity, `frac = 1.407` and `1.143`: the rescaled rotated code beat the native code.
The bands must therefore admit `frac > 1` rather than treating 1 as a ceiling, and no narrative may
describe rescaling as merely "recovering" what was lost.

## What this pilot does NOT establish

It says nothing about where the real archives sit on the `CV(sigma)` axis, and the results depend
strongly on that. `CV(sigma)` for the real cohorts cannot be computed from repository bytes, because
the corpus is not in git — so band calibration against real heterogeneity remains open, and is a
reason to measure `CV(sigma)` as a declared diagnostic in the first authorized run.

The generative model here — i.i.d. coordinates scaled by a geometric profile, gold as a noisy copy —
is a caricature. It has no correlation structure between coordinates, which the literature says
contributes 30-50% of ranking signal. A real archive may differ in magnitude, and possibly in kind.

## Boundary

No corpus was read, no benchmark outcome was computed, and no Task 4F1 artifact, authorization, HMAC
material or outcome was touched. Task 4F1 remains
`SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.

---

# Addendum — pilot 04: the three remaining design questions

Script: `pilot_04_scale_rule_and_scope.py`. Synthetic only; same boundaries as above.

## Q1 — is `D = 1/sigma` the right rule, or the gentler `sigma^(-1/2)`?

`frac` = share of each arm's own loss recovered.

| decay | rule | scope | frac_full | frac_block |
|---|---|---|---:|---:|
| 0.97 | `1/sigma` | per-archive | 1.031 | 1.007 |
| 0.97 | `1/sqrt(sigma)` | per-archive | 0.774 | 0.816 |
| 0.92 | `1/sigma` | per-archive | 1.011 | 1.002 |
| 0.92 | `1/sqrt(sigma)` | per-archive | 0.462 | 0.610 |

**Resolved: `D = 1/sigma`.** It is decisive — `frac` lands at approximately 1.00 regardless of
heterogeneity, so the experiment can distinguish "scale explains the damage" from "it does not".
`sigma^(-1/2)` produces middling values (0.46 to 0.82) that drift with heterogeneity and would land
inside a "partial" band by construction, answering nothing. A gentler rule is not a more cautious
choice here; it is a less informative one.

## Q2 — per-archive or global `sigma`?

| decay | rule | scope | frac_full | frac_block | I_frac |
|---|---|---|---:|---:|---:|
| 0.97 | `1/sigma` | per-archive | 1.031 | 1.007 | +0.023 |
| 0.97 | `1/sigma` | global | 1.022 | 1.096 | -0.073 |
| 0.92 | `1/sigma` | per-archive | 1.011 | 1.002 | +0.009 |
| 0.92 | `1/sigma` | global | 1.008 | 1.021 | -0.013 |

**Resolved: per-archive.** It matches the archive-local SVD the representation is built from, and it
is tighter: both arms sit near 1.00 with a small consistent `I_frac`. A global `sigma` overshoots
more on the block arm (1.096) and **flips the sign of `I_frac`** between the two settings, which is
exactly the instability a mismatched scale introduces.

## Q3 — fresh block seeds, or reuse the audited panel `58001..58010`?

Not decidable by measurement; it is a question about how the result can be attacked.

**Resolved: fresh seeds `59001..59010`.** Reusing the audited panel would invite the objection that a
panel already known to show the effect was chosen, and the cost of fresh seeds is nil. The boundary
stage already demonstrated that a fresh panel reproduces the shape, so tighter pairing with the
audited stage buys little and costs the appearance of independence.

## Degenerate-coordinate stress test

Forcing 12 of 96 coordinates to approximately zero variance, 360 fallbacks across 30 archives:

| rule | degenerate handled | frac_full | frac_block | identity |
|---|---:|---:|---:|---|
| `1/sigma` | 360 | 0.985 | 0.970 | exact |
| `1/sqrt(sigma)` | 360 | 0.460 | 0.580 | exact |

The `eps = 1e-12` fallback to `d_i = 1` behaves correctly and the `sign(xD) = sign(x)` identity
survives it. This is the case most likely to appear in real archives, and it does not break the
design.

## Standing limitation, unchanged

None of this says where the real archives sit on the `CV(sigma)` axis, which cannot be computed from
repository bytes. The synthetic model still has no inter-coordinate correlation structure.
