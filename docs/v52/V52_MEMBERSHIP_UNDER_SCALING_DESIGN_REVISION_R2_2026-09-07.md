# V52 — Membership Under Scaling: Design Revision R2 (simplification)

Status: **`[DRAFT — NOT AUTHORIZED FOR EXECUTION]`**
Not accepted, not sealed, not triggered. No runner or workflow exists. No code was written.

Date: 2026-09-07
Author: Continuity Lead / co-chair
Supersedes, on every point where they differ: `…DESIGN_REVISION_R1_2026-09-07.md`
(sha256 `3d7a79b249e97a1bc2657a6782aec5e6a138f6a8c5e2681978ed66ad217b3391`) and the decision
apparatus of `…PREREG_DRAFT_2026-09-07.md` §8
(sha256 `3da80e3424a8f29bcd85ad1c0d5f5b8e97dfba857fbaaf042b2b0d06301e3399`).

Additive. **Neither bound document is edited.** Read all three together; on conflict **R2 governs**,
as the latest and narrowest.

Nothing was executed: no code, no experiment, no pilot, no bootstrap, no retrieval, no model or
corpus download, no agent. The closure audit is not reopened. Task 4F1 remains
`SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.

---

## 1. The criticism, accepted

This design began by replacing a ratio with a difference, because a ratio over a near-zero
denominator is what made the previous stage's block arm uninterpretable. R1 then **reintroduced a
ratio** — `ρ = Δ̄ / Ḡ` — in order to attach a categorical verdict, and that single choice dragged in
a denominator to protect, a `2.0` pp floor to protect it with, and four cut points to divide it. The
complexity was not in the science; it was in the labelling.

`ρ` is **not** the same quantity as the old block-loss ratio, and it would not automatically have
been as fragile. That is not the point. The point is that the question does not need it:

> How large was the grouping gap before the intervention, how large did it remain after, and by how
> many percentage points did it change?

Three numbers answer that. This revision removes everything that was not those three numbers and
their uncertainty.

## 2. The primary result — three quantities, in percentage points

Per rotation seed `k` of the fixed ten-seed panel, with all pairing, matching and arm definitions
exactly as R1 §2 fixes them:

```
G_k         = R@3(B32_FRESH, k)  − R@3(RANDOM32_FRESH, k)      gap before the intervention
G_scaled_k  = R@3(SCALED_B32, k) − R@3(SCALED_RANDOM32, k)     gap remaining after it
Δ_k         = G_scaled_k − G_k                                  paired change
```

Reported, all three, always, in percentage points:

| quantity | meaning |
|---|---|
| `Ḡ` = mean over the ten seeds of `G_k` | the grouping gap before scale equalisation |
| `Ḡ_scaled` = mean over the ten seeds of `G_scaled_k` | the gap that remains after it |
| `Δ̄` = mean over the ten seeds of `Δ_k` | how much the gap changed |

Plus every per-seed value of all three, and the uncertainty of §4 for each.

**Sign convention, unchanged from R1 §3.** `G > 0` means spectral membership outperforms random
membership. `Δ < 0` means the gap shrank under rescaling; `Δ > 0` means it grew.

**An aggregation ambiguity that cannot arise here, and why that matters.** Because `Δ` is *linear*
in the arm means, the two aggregation orders that split the previous stage give **identical** values:

```
mean_k (G_scaled_k − G_k)  =  mean_k G_scaled_k  −  mean_k G_k  =  Ḡ_scaled − Ḡ  =  Δ̄
```

exactly, not approximately. The A-versus-B question that consumed the closed stage was a consequence
of the estimand being a **ratio**; with a difference there is nothing to rule on. Removing the ratio
therefore removes that whole class of dispute rather than merely deciding it.

## 3. What is withdrawn — the full list

Every item below was proposed by me and is **removed from this design**. None of it may be
reintroduced later without a new decision made before outcome access.

| withdrawn | where it came from |
|---|---|
| `ρ = Δ̄ / Ḡ` as the primary decision quantity | R1 §5 |
| the five categorical labels — reversed / accounts-for-most / partial / does-not-account / gap-larger | R1 §5 |
| the cut points `−1.00`, `−0.60`, `−0.20`, `+0.20` | R1 §5 |
| the `2.0` pp floor on `Ḡ` | R1 §4; it existed only to protect `ρ`'s denominator, so it goes with `ρ` |
| the `[RELATIVE SCALE UNSUITABLE]` state | R1 §4; no longer has anything to guard |
| the `[INDETERMINATE — INTERVAL SPANS …]` overlay as a **verdict mechanism** | R1 §5; the interval is now reported directly instead of being converted into a label |
| the three-band decision rule | draft §8 |
| a preregistered band on the remaining gap `Ḡ_scaled` | proposed as open question 5 in R1; **declined** |
| the per-seed positivity gate on `G_k` | draft §8; already withdrawn in R1 §4, stays withdrawn |

**Consequence: this study produces an estimate, not a verdict.** That is deliberate. There is no
preregistered threshold and no categorical output.

**The loophole that removing thresholds could open, closed explicitly:** because no threshold is
preregistered, **no threshold may be introduced after outcome access** — not to declare "most", not
to declare "little", not to declare equivalence, and not under any other name. The no-tuning rule of
draft §13 covers this and is restated here so it cannot be read as applying only to seeds and
parameters.

**The ratio is not forbidden; it is simply not a deliverable.** It is not computed, not reported and
not part of the preregistered output. Anyone who later wants it can derive it from the three reported
numbers without re-running anything, and doing so requires no new design and opens no audit chain.

## 4. Uncertainty — targets, weights and limits, written separately per scheme

Mechanics unchanged from R1 §6: the question is the resampling unit, 10,000 replicates, **one**
resampled index set per replicate applied identically to all six arms and all ten seeds so pairing
survives, the **seed panel fixed and not resampled**, percentile interval at 2.5 and 97.5, and the
two benchmarks evaluated separately and never pooled. Intervals are reported for **each** of `Ḡ`,
`Ḡ_scaled` and `Δ̄`.

### LoCoMo — two schemes, stated separately

| | question-level | conversation-cluster |
|---|---|---|
| **target** | variability of the three quantities when questions are treated as exchangeable | variability when whole conversations are the exchangeable unit, each selected conversation carrying **all** of its questions |
| **weighting** | unweighted; every question counts once | question-weighted by construction; a larger conversation contributes more questions when drawn |
| **limit** | **does not account for within-conversation dependence at all.** LoCoMo's questions are nested in ten conversations, so this scheme's interval is narrower than the dependence structure warrants | built on **ten** units. A resampling estimate over ten clusters has limited reliability. Its width is an outcome and is not forecast here |

**Stated because it is easy to get backwards:** the existence of ten conversation clusters does
**not** make the question-level analysis more trustworthy with respect to dependence. It is the
reason the question-level analysis is inadequate on that axis, not a reassurance about it.

**The two schemes are not independent confirmation of each other.** They are two views of the same
fixed panel under different exchangeability assumptions, computed from the same records. Agreement
between them is not corroboration.

**If they diverge, that divergence is itself the finding** and is reported as such: the conclusion is
sensitive to the choice of resampling unit, and both intervals are given with the sentence that says
so. Neither is promoted over the other, and no single reconciled interval is manufactured.

### LongMemEval — one scheme, and what it is not

Question-level resampling only, and it stands **solely as a sensitivity analysis**. It must never be
presented as population inference. The reason is the recorded dependency structure: the 470 primary
questions lie in a single shared-session component. **That finding is inherited from Task 3A.1 and
provenance-verified; it is not recomputed here**, and any statement resting on it must carry:

> `[LONGMEMEVAL SINGLE-COMPONENT FINDING — INHERITED FROM TASK 3A.1; PROVENANCE VERIFIED, NOT RECOMPUTED HERE]`

No conversation-cluster bootstrap is defined for LongMemEval.

### Kept separate

Printed-decimal versus exactly-computed differences, of order `1e-14` in this programme's records,
are a reporting-precision matter. They are evidence about estimator stability in **neither**
direction and are never mixed into, or substituted for, these intervals.

## 5. How the result is stated

The reporting sentence, fixed in advance:

> Under the scale intervention defined in draft §5 and R1 §1 — `D = diag(1/σ)` with `ddof = 0`,
> `ε = 1e-12` as a fallback, estimated from archive content alone — the membership gap on the frozen
> question and seed panel was `Ḡ` pp before the intervention and `Ḡ_scaled` pp after, a paired change
> of `Δ̄` pp, with intervals as reported.

**Prohibited, in any outcome:**

- calling any change a causal mechanism, or saying the effect has been explained;
- generalising beyond the frozen panels, this pipeline, or this specific intervention;
- concluding "there is no effect" — including from an interval that spans zero;
- claiming practical equivalence;
- introducing any threshold, band or categorical label after outcome access;
- upgrading a `[LEAD]`.

**An interval that spans zero is reported as an interval that spans zero.** It means the data on
this panel do not resolve the sign of the change. It is not evidence of absence, and it must not be
converted into one.

**The follow-up framing stands** (draft §1, R1 §7): fresh seeds are drawn on the same previously
examined corpora; they prevent reuse of a panel already known to show an effect but do not make this
a fresh independent test and do not restore blindness.

## 6. What R2 does not change

Everything not listed in §3 stands: the six arms; the matched draw structure with seeds paired
one-to-one and not crossed (R1 §2); the scaling operator specification (R1 §1); unconditional
publication of all arms, seeds, per-question records, aggregates, diagnostics and controls under
every outcome (R1 §4); the mandatory control suite (draft §11); the no-tuning rule (draft §13); and
the outcome-licence limits (draft §10).

## 7. What this document does not do

It does not accept the design, seal anything, authorize implementation, or authorize a run. No code
exists. The author must not seal or run it.
