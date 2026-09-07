# V52 — Membership Under Scaling: Design Clarification and Revision R1

Status: **`[DRAFT REVISION — NOT AUTHORIZED FOR EXECUTION]`**
Not accepted, not sealed, not triggered. No runner or workflow exists. No code was written.

Date: 2026-09-07
Author: Continuity Lead / co-chair
Bound object: `docs/v52/V52_MEMBERSHIP_UNDER_SCALING_PREREG_DRAFT_2026-09-07.md`, sha256
`3da80e3424a8f29bcd85ad1c0d5f5b8e97dfba857fbaaf042b2b0d06301e3399`

Additive. **The bound draft is not edited.** Where it already specifies something, this document
cites the section. Where it is incomplete or wrong, this document supplies the specification and
says so. Read the two together; on any conflict **this document governs**, because it is later and
narrower.

Two substantive design changes are made here, both accepted from the review: the interpretation gate
is reformed so it cannot suppress reporting (§4), and a fourth and fifth outcome category are added
because the draft's three bands could not express a reversal (§5).

Nothing was executed: no experiment, pilot, bootstrap, retrieval, fitting, ranking, model or corpus
download, and no agent. The closure audit is not reopened. Task 4F1 remains
`SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.

---

## Item 1 — the scaling operator, completely

Partly in draft §5 Step 1. That section fixes the estimand of `σ`, its per-archive scope and the
archive-only provenance. It does **not** fix the estimator's degrees of freedom, the justification
for the floor, the query rule as a normative statement, or the diagnostic threshold. Supplied here.

**The operator.** For one archive with centered representation `C ∈ ℝ^{n×96}`, where `C = Y − μ` and
`μ` is the archive mean row of the normalised 96-dimensional representation:

```
σ_i  = std over the n archive rows of column i of C, computed with ddof = 0
d_i  = 1/σ_i   if σ_i ≥ ε
d_i  = 1       if σ_i <  ε
D    = diag(d_1 … d_96)
ε    = 1e-12
```

- **`ddof = 0`** — the population form, not the sample form. This is stated because the two differ
  by `√(n/(n−1))` and would define different interventions. It matches the estimator already
  implemented and audited in the closed stage; adopting the sample form here would silently make
  this a different experiment from the one whose behaviour is known.
- **`σ` is computed on `C`, the exact centered matrix used downstream** — not on raw SVD outputs,
  not on singular values, and not on the uncentered `Y`.
- **The floor is a fallback, not a clip.** A coordinate below `ε` gets `d_i = 1`, i.e. it is left
  alone; it is never divided by `ε` and never dropped. This keeps the transform total and keeps the
  coordinate in the sign code.
- **Why `ε = 1e-12`.** It is inherited unchanged from the closed stage rather than re-chosen here,
  so that the intervention is the same operator whose identity property has already been exercised.
  Its role is to catch coordinates that are numerically dead — a constant column has `σ = 0` exactly
  and `1/σ` would be infinite. It is a guard against division by zero, not a tuning parameter, and
  it must not be adjusted after outcome access (draft §13).
- **The query.** The **identical** `D` is applied to the query: `q ↦ q D`. `D` is estimated from the
  archive alone and **nothing is estimated from the query**. There is no query-side normalisation,
  no re-centering of the query by its own statistics, and no separate query scale.
- **Diagnostics, recorded per archive and reported:** the count of coordinates taking the fallback;
  an archive is flagged if that count exceeds **4** of 96; `CV(σ)` before and after rescaling. These
  are declared diagnostics, **not decision inputs**.
- **Abort, not repair:** any non-finite value in `C` or in `C D` stops the run (draft §11.9).

**Why this operator and not a gentler one.** `1/σ` fully equalises per-coordinate variance. A
gentler rule such as `σ^{-1/2}` was examined in the closed stage's pilot and rejected there for being
indecisive by construction. It is not re-litigated here; this design tests the same operator whose
behaviour on the full-mixing arm is already characterised.

## Item 2 — how the four conditions are matched

Partly in draft §5 Step 3 and §7. Those fix the shared-`Q` control and question-level pairing. The
draw structure, the pairing convention and the totals were not stated. Supplied here.

**Seeds are paired one-to-one by position, not crossed.** Rotation seed `60000+k` is used with
partition seed `70000+k` for `k = 1…10`. There are ten (rotation, partition) pairs and **not** a
10×10 grid. A crossed design would multiply cost tenfold and answer no question this experiment
asks; the pairing is fixed here so it cannot be chosen later.

**Per seed `k`, exactly one draw of each kind:**

| drawn from | what | used by |
|---|---|---|
| rotation seed `60000+k` | one `Q32` (32×32 Haar), then one `Q64` (64×64 Haar), head block first from a single stream | all four rotated arms at seed `k` |
| partition seed `70000+k` | one permutation of `0…95`; `S_rand` is its first 32 entries, `T_rand` the rest | both random-membership arms at seed `k` |

**The four cells at seed `k`** — this is the table the review drew, made exact:

| | unscaled | scaled |
|---|---|---|
| spectral membership `S_spec = {0…31}` | `C · R_spec` | `C · D · R_spec` |
| random membership `S_rand` from seed `70000+k` | `C · R_rand` | `C · D · R_rand` |

where `R_spec` places `Q32` at `ix(S_spec, S_spec)` and `Q64` at `ix(T_spec, T_spec)`, and `R_rand`
places **the same numeric `Q32` and `Q64`** at `ix(S_rand, S_rand)` and `ix(T_rand, T_rand)`.

**What is therefore held identical across all four cells at a given seed:** the questions, the gold
sets, the tie priority and its 20 nuisance trials, the archive representation `C`, the numeric `Q32`
and `Q64`. **What varies:** membership (columns of the table's rows) and the presence of `D` (its
columns). Nothing else. Any difference between cells is attributable to those two factors and to
nothing drawn separately, which is the point of the design.

**Totals per benchmark:** 10 Haar `(Q32, Q64)` draws, 10 partitions, 4 rotated arms per seed = 40
rotated evaluations, plus `NATIVE` and `SCALED_NATIVE` which are rotation-independent. Per-question
rows are written for all six arms at all ten seeds, so the persisted table is
`n_questions × 10 × 6` — 92,100 for LoCoMo and 28,200 for LongMemEval, matching the schema of the
closed stage so an auditor can rebuild every aggregate.

**Checked at run time:** `max |Q32_spec − Q32_rand| = 0.0` and `max |Q64_spec − Q64_rand| = 0.0`
exactly (draft §11.5); partition cardinality, uniqueness, disjointness, exhaustiveness (draft §11.6).

## Item 3 — the primary formula, its sign, and what is always reported

In draft §7 for the formulas. The **sign convention** was implied by the bands but never stated in
words, and the reporting requirement was not mandated. Supplied here.

```
G_k         = R@3(B32_FRESH, k)  − R@3(RANDOM32_FRESH, k)      unscaled membership gap
G_scaled_k  = R@3(SCALED_B32, k) − R@3(SCALED_RANDOM32, k)     scaled membership gap
Δ_k         = G_scaled_k − G_k                                  change in the gap
Ḡ, Ḡ_scaled, Δ̄  = means over the ten seeds; Δ̄ = Ḡ_scaled − Ḡ
ρ̂          = Δ̄ / Ḡ  =  Ḡ_scaled/Ḡ − 1                         relative change
```

**Sign convention, stated explicitly.** `G > 0` means spectral membership outperforms random
membership, which is the direction the closed stage observed on a different panel. **`Δ < 0` means
the gap shrank under rescaling; `Δ > 0` means it grew.** On the relative scale, `ρ̂ = 0` is no
change, `ρ̂ = −1` is the gap exactly eliminated, and `ρ̂ < −1` is the gap reversed in sign.

**Always reported together, in every outcome and whatever any gate does:** `Ḡ` (the gap before
rescaling), `Ḡ_scaled` (the gap remaining after), `Δ̄` (the change), `ρ̂`, all per-seed values of
each, and the uncertainty of §6. Reporting `Δ̄` without `Ḡ` and `Ḡ_scaled` is barred: a change is
uninterpretable without the level it changed from and the level it left behind.

## Item 4 — the gate, reformed so it cannot suppress anything

Draft §8 as written created exactly the hazard the review names: an outcome-dependent door that
could read as licence to withhold results. **Revised here.**

**What is published unconditionally, under every outcome of every check:** all six arms; all ten
seeds; every per-question record; `Ḡ`, `Ḡ_scaled`, `Δ̄`, `ρ̂` and their per-seed values; every
uncertainty output of §6; every diagnostic; and every control result. **No gate suppresses any
number.**

**What a gate may do, and only this:** decline to attach the *categorical verdict* of §5. Nothing
else. Specifically it may **not** trigger new seeds, a re-run, a selective exclusion of seeds,
archives or questions, or the withholding of any measurement. Those remain barred by draft §13.

**The per-seed positivity requirement is withdrawn.** The draft required `G_k > 0` on every one of
ten seeds before the normalised reading applied. The review is right that a single seed should not
suspend an entire interpretation, and the requirement is dropped. **Replacement:** the number of
seeds with `G_k ≤ 0` is a **reported diagnostic**, and its effect enters through the uncertainty
interval of §6 rather than through a switch. If seeds disagree in sign about whether spectral beats
random, that is information about the panel and must be visible, not a reason to say nothing.

**One gate survives, on the relative scale only.** `ρ̂` is a ratio, so it is meaningless when its
denominator is near zero — the failure mode that ended the previous stage. Therefore:

> if `Ḡ < 2.0` percentage points, the **categorical verdict of §5 is not attached**. `Δ̄`, `Ḡ`,
> `Ḡ_scaled` and all uncertainty are still reported, in percentage points, and the record reads
> `[RELATIVE SCALE UNSUITABLE — Ḡ BELOW 2.0 pp; ABSOLUTE RESULTS REPORTED]`.

**Why 2.0 pp, honestly.** It is a judgment, not a derivation, and it is set in advance so that it
cannot be chosen afterwards. Its basis: it is roughly a quarter of the smaller of the two gaps
previously observed on a *different* seed panel, which places it far enough above zero that `ρ̂` is
not dominated by its denominator, while being loose enough that it does not encode a prediction
about this run. It is **not** a claim that `Ḡ` will exceed 2.0 pp here. If a reviewer prefers a
different floor, it must be changed **now**, before any run, not after.

## Item 5 — the positive decision rules, including the two cases the draft could not express

Draft §8 offered three bands and had **no category for the gap growing or reversing**. That is a
real gap: `Δ̄ > 0` would have been classified as "does not account for the gap", which is true but
hides a qualitatively different result. Revised here.

**Point classification on `ρ̂`:**

| condition | verdict label |
|---|---|
| `ρ̂ ≤ −1.00` | `[DIRECTION REVERSED UNDER RESCALING]` — after rescaling, random membership performs at least as well as spectral |
| `−1.00 < ρ̂ ≤ −0.60` | `[SCALE EQUALISATION ACCOUNTS FOR MOST OF THE MEMBERSHIP GAP]` |
| `−0.60 < ρ̂ < −0.20` | `[PARTIAL]` |
| `−0.20 ≤ ρ̂ ≤ +0.20` | `[SCALE EQUALISATION ALONE DOES NOT ACCOUNT FOR THE MEMBERSHIP GAP]` |
| `ρ̂ > +0.20` | `[MEMBERSHIP GAP LARGER UNDER RESCALING]` |

**The uncertainty overlay, which is the actual decision rule.** The point classification alone does
not carry the verdict. Compute the question-level paired bootstrap interval for `ρ̂` (§6). Then:

- if the interval lies **entirely inside one** category, the verdict is that category;
- if it **spans two or more** categories, the verdict is
  `[INDETERMINATE — INTERVAL SPANS <categories>]`, and the point classification is reported as a
  point observation with no verdict attached.

This is what replaces deciding by the sign of `Δ̄` or by whether per-seed ranges overlap, both of
which remain barred (draft §9).

**Naming discipline, binding on every category.** None of these labels may be restated as a
mechanism having been explained. A reduction in the gap is a statement about *what this
intervention accounts for*, never about what causes the effect. `[SCALE EQUALISATION ACCOUNTS FOR
MOST OF THE MEMBERSHIP GAP]` does not license "coordinate scale explains the membership effect", and
`[SCALE EQUALISATION ALONE DOES NOT ACCOUNT FOR THE MEMBERSHIP GAP]` does not license "axis ordering
is the mechanism" or "there are two mechanisms" (draft §10).

## Item 6 — the uncertainty method, completely

Partly in draft §9, which fixed what may not carry a verdict and which resampling schemes apply. The
mechanics were not specified, and one sentence overreached. Supplied and corrected here.

| element | specification |
|---|---|
| primary resampling unit | the **question**, resampled with replacement |
| replicates | 10,000, matching the closed stage |
| pairing | **one** resampled index set per replicate, applied identically to all six arms and all ten seeds, so every pairing the design establishes is preserved inside each replicate |
| weighting | unweighted at question level |
| seed panel | **fixed, not resampled.** The ten seeds are the panel. Within a replicate, `Δ_k` is recomputed on the resampled questions for each of the ten seeds and then averaged over the fixed panel |
| statistic | `ρ̂` and `Δ̄`, both recomputed per replicate from the resampled questions |
| interval | percentile, 2.5 and 97.5 |
| datasets | **evaluated separately, never pooled.** Two benchmarks give two independent reports and no cross-benchmark statistic is defined |
| LoCoMo secondary | conversation-clustered bootstrap: clusters resampled with replacement, each selected cluster carrying **all** of its questions, so the statistic is question-weighted by construction — the scheme the closed stage used |
| LongMemEval clustered | **none.** Its 470 questions form a single shared-session dependency component; that finding is inherited from Task 3A.1 and provenance-verified, **not recomputed** here |

**Correction to the draft.** Draft §9 states that the LoCoMo clustered interval "will be wide and
unreliable". That predicts a result before the run and is withdrawn. The accurate statement:
**LoCoMo has ten conversation clusters, and a resampling estimate built on ten units has limited
reliability; the interval's actual width is an outcome and will be reported, not forecast.**

**Both schemes are sensitivity analyses, not certified sampling intervals.** For LongMemEval in
particular, the question-level bootstrap **must not be presented as population inference**: the
recorded single-component dependency means questions are not exchangeable, and the interval
describes resampling variability on a fixed panel, nothing more.

**Kept separate, per the standing rule:** differences between a printed decimal and an exactly
computed value, of order `1e-14` in this programme's records, are a reporting-precision matter. They
are evidence about estimator stability in **neither** direction and are never mixed into, or
substituted for, the intervals above.

## Item 7 — the follow-up framing is unchanged

Already in draft §1, which discloses that the design was written after the closed stage's results
were read and lists what was known to the author. Restated for completeness and to close the
specific point raised:

**Fresh seeds are not a new question and not new data.** Seeds `60001…60010` and `70001…70010` are
drawn on the **same** LoCoMo and LongMemEval corpora, already examined repeatedly by this programme.
They prevent reuse of a panel already known to show an effect; they do **not** make this a fresh
independent test, and they do not restore blindness. This remains a follow-up experiment designed
with prior findings in view, on previously examined datasets, and every report of it must say so.

---

## Design decisions still open

1. **The `2.0` pp floor on `Ḡ`** (§4). A judgment, changeable now and not later.
2. **The band cut points** `−1.00 / −0.60 / −0.20 / +0.20` (§5). `−0.60` and `−0.20` are inherited
   from the closed stage's scale; `−1.00` and `+0.20` are new and were chosen for symmetry and for
   marking the qualitative boundaries, not derived.
3. **Whether the LoCoMo clustered bootstrap is reported as a co-primary or as a secondary** to the
   question-level interval. This document treats it as secondary; ten clusters is the reason, and a
   reviewer may reasonably prefer it co-primary.
4. **Whether the `[INDETERMINATE]` overlay uses the question-level interval alone** (as written) or
   requires both schemes to agree on LoCoMo.
5. **Whether `Ḡ_scaled` deserves its own preregistered band**, since "the gap remaining" is arguably
   as interesting as "the change in the gap". Not proposed here; noted because it would have to be
   added before sealing, not after.

## What this document does not do

It does not accept the design, seal anything, authorize implementation, or authorize a run. No code
exists. No experiment, pilot, bootstrap, retrieval, model or corpus download was performed. The
closure audit is not reopened. The author must not seal or run this.
