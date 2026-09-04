# Task 4F1 — Preregistration Draft (outcome-free)

Status: **DRAFT. Not preregistered, not authorized, not run.**
Date: 2026-09-03
Author: Continuity Lead. Requires Head Researcher and co-chair approval before it becomes a
sealed preregistration.

This document contains no retrieval-quality outcome. Every number in it is a structural fact
about the frozen cohort, recomputed from
`audit_v52_t4f0_restricted_refreeze_2026_08_31/estimand_primary_cohort.csv`
(SHA256 `9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a`), or a previously
accepted result from LongMemEval and LoCoMo.

---

## 1. Why run this at all

Two benchmarks already replicate the direction. On the frozen 470-question LongMemEval cohort
Native SIGN96 scored `54.197517730496%` against a mean Full-Haar96 of `38.271666666667%`; on the
frozen 1,535-question LoCoMo cohort, `23.654714666441%` against `13.770827054136%`. In the sign
convention used throughout this document — **positive means Native is better** — those are
**+15.926 pp** and **+9.884 pp**.

A third benchmark that merely repeats "same direction again" is worth little. BEAM earns its cost
on one axis the other two do not have: **scale**. Its archives span roughly 287 raw message units
at 100K to roughly 20,870 at 10M — nearly two orders of magnitude — inside a single benchmark
with a single protocol.

So the scientific object here is **not** a third confirmation. It is the **profile of the effect
across scale**. State that plainly now, before any outcome is visible, so the result cannot later
be re-framed into whichever claim it happens to support.

What this cannot establish, regardless of outcome: population-level generalization beyond these
benchmarks, a causal mediator for why sign codes beat Haar rotations, or production superiority.
Those remain open and are not addressed by this task.

**Honest prior on value.** If the four tiers come back with the same direction and similar
magnitude, the marginal information over LongMemEval and LoCoMo is modest and should be reported
as modest. The informative outcomes are a *changing* profile across scale, or a failure at some
tier. This is written down so that a flat result is not later inflated.

---

## 2. Frozen cohort structure

All denominators are frozen before outcome access. Recomputed and confirmed:

| Tier | Questions | Archives | Mean \|gold\| | ALL@3 structurally possible | ALL@3 structural zeros |
| --- | ---: | ---: | ---: | ---: | ---: |
| 100K | 355 | 20 | 3.08 | 259 | 96 |
| 500K | 629 | 35 | 4.26 | 461 | 168 |
| 1M | 553 | 31 | 8.59 | 300 | 253 |
| 10M | 175 | 10 | 7.47 | 105 | 70 |
| **Pooled** | **1712** | **96** | **5.74** | **1125** | **587** |

Excluded archives, exactly: `1M::5`, `1M::26`, `1M::33`, `1M::34`.

### 2.1 Marginal ability composition is near-balanced

Within every tier the nine abilities are near-uniformly represented (100K min 36 max 40; 500K
69/70; 1M 58/62; 10M 16/20).

The claim this supports is narrow and is stated at exactly its strength: **no obvious marginal
ability-composition imbalance explains tier differences**. It does not establish that ability is
not a confounder. Marginal balance says nothing about the joint distribution — ability could still
covary with gold cardinality or archive length inside a tier. Ability-stratified reporting
therefore remains **mandatory**, not optional, and is not discharged by this measurement.

### 2.2 Gold cardinality is NOT balanced, and this caps the metric

Fractional Source Evidence Recall@3 is bounded above by `min(1, 3/|gold|)`. A question with eight
gold units cannot exceed 0.375 no matter how good retrieval is. Mean ceiling by tier:

| Tier | Mean ceiling | Share of questions with ceiling 1.00 |
| --- | ---: | ---: |
| 100K | 0.867 | 73.0% |
| 500K | 0.836 | 73.3% |
| 1M | 0.721 | 54.2% |
| 10M | 0.776 | 60.0% |
| Pooled | 0.799 | 65.7% |

Two consequences, both pre-specified here:

1. The contrast is **paired within a question**, so the ceiling constrains both arms identically
   and does not bias the sign. But it does compress the achievable *magnitude*: a tier with a
   lower ceiling has less room for any difference to appear.
2. The ceiling profile is **non-monotonic in tier** (1M is lower than 10M). The correct and
   limited statement is: the ceiling profile **does not mechanically impose a monotone ordering**
   on the tier contrasts. That is weaker than saying a monotone observed profile cannot be
   explained by the ceiling — the ceiling may still contribute through interaction with archive
   length, gold structure or other unmeasured composition, and no measurement here excludes that.
   Accordingly the cross-tier comparability instrument is the **ceiling-free stratified contrast**
   of §3.2, not a normalised scalar. The §6 global category is assigned from `D_t` alone.
   Discordance between `D_t`, the stratified contrasts and `D_t^norm` is reported as a labelled
   sensitivity flag accompanying the category; it never silently overrides or vetoes it.

---

## 3. Estimands

### 3.1 Primary family — four tier-specific contrasts

For each tier `t`, over the questions in that tier, equally weighted:

```
D_t = mean_i [ FracRecall@3( Native SIGN96 )_i  −  mean over 5 Haar seeds FracRecall@3( HAAR96_SIGN )_i ]
```

Positive means Native better. Denominators are the frozen 355 / 629 / 553 / 175.

There are four primary quantities. There is no single headline number.

**The comparator is a finite mean over exactly five preregistered seeds.** `HAAR96_SIGN` is
evaluated at seeds `43001, 43002, 43003, 43004, 43005` and at no others. The estimand is the mean
over those five, treated as a **fixed, enumerated comparator** — not as an estimate of, and not as
an inference to, the full Haar-rotation distribution. No claim about "Haar rotations in general"
follows from this task. The five per-seed aggregates and their min–max spread are **sensitivity
diagnostics** on that fixed comparator, not a sampling distribution and not a basis for interval
estimation. The same restriction applies to the five ITQ seeds.

### 3.2 Cross-tier comparability: ceiling-free stratified contrasts

The **primary** cross-tier comparability instrument is `D_t` restricted to the stratum where the
metric carries no compression at all:

```
D_t^(|gold| ≤ 3) = the §3.1 contrast computed only over questions with |gold| ≤ 3
```

That stratum has ceiling exactly 1.000, so it is directly comparable across tiers with no
normalisation and no reweighting. Its frozen denominators are **259 / 461 / 300 / 105**.

`D_t` is additionally reported within the remaining mandated strata (`4–6`, `7+`), giving a
composition-matched view of the profile without any rescaling.

**Declared sensitivity statistic.** `D_t^norm` is retained but demoted:

```
D_t^norm = mean_i [ ( Native_i − mean_Haar_i ) / min(1, 3/|gold_i|) ]
```

It is **not** a rescaling of `D_t` and **not** a cross-tier comparability device. Dividing by the
ceiling is algebraically a `|gold|`-weighted mean with weights `w_i = max(1, |gold_i|/3)`, so it
upweights high-`|gold|` questions — and those weights are distributed differently in each tier
(mean `|gold|` runs 3.08 / 4.26 / 8.59 / 7.47). It therefore answers a different question from
`D_t` rather than a corrected version of the same one. It is reported as a declared sensitivity
statistic only.

### 3.3 Supportive and descriptive

- **ANY@3**: the same tier-specific contrast. Supportive.
- **ALL@3**: reported per tier with structural zeros retained, and **excluded from all cross-tier
  scale claims**, because gold cardinality drives it directly (§2.2).
- **Win / tie / loss profile** per tier: the count of questions where Native exceeds, equals, or
  falls below the Haar mean. Descriptive of the fixed benchmark, not an inference. It carries the
  **same cross-tier bar as ALL@3**: raw W/T/L counts and tie rates are **not** compared across
  tiers, because tie structure is driven by `|gold|` composition, which differs (share of
  `|gold| = 1` is 29.0% at 100K against 17.9% at 1M). Where a cross-tier reading is intended,
  W/T/L is reported **within gold-cardinality strata**. `W / (W + L)` is additionally reported as
  the tie-excluded paired-effect summary.
- **ITQ96_CENTERED**: reported, descriptive only, no claim attached.

### 3.4 Negative control — invalidating, not supportive

`SIGNED_PERM_CONTROL96` must reproduce Native's ordered top-three IDs **and** exact Hamming
distances for every question, seed and trial. This is a mathematical identity, not an empirical
finding. Any divergence invalidates the entire run; it is not reported as a result.

### 3.5 Secondary

The pooled 1,712-question contrast is reported as a replication summary comparable to the
LongMemEval and LoCoMo numbers in §1. It is **secondary**: the tier profile is the primary object.

---

## 4. Uncertainty, and what is deliberately not computed

- **No population inference, no p-values, no confidence intervals over questions.** The cohort is
  a fixed benchmark, not a random sample from a population. The research programme has explicitly
  not established population-level generalization, and this task does not attempt it.
- **The five seeds are constitutive of the comparator's definition, not a sample from it.** The
  per-seed aggregates and their min–max spread at each tier are reported to show how sensitive the
  fixed comparator is to *which* rotations were enumerated. They license no claim about
  unenumerated rotations and are not a sampling distribution.
- **The 20 nuisance trials are deterministic replication identities.** They must be byte-identical
  across trials. They are an integrity check and are **never** treated as a variance source or as
  independent statistical units. Any trial-varying result invalidates the run.
- **One descriptive stability statistic is pre-specified**, so it can neither be introduced later
  as a rescue nor omitted as inconvenient: the **leave-one-archive-out min–max range** for each
  `D_t`, computed over that tier's archives (20 / 35 / 31 / 10), reported alongside the per-seed
  min–max. It is a descriptive sensitivity of a fixed statistic to its own enumerated composition.
  It is **not** a confidence interval, **not** a standard error, and carries **no** coverage or
  population semantics.
- **No multiplicity correction is applied**, because no null-hypothesis tests are performed. Stated
  explicitly so that its absence is not later read as an oversight.

---

## 5. Interpretation boundary

Any ordered pattern across tiers is an **association across fixed benchmark strata**. The tiers are
neither paired nor randomized; their archives, questions and gold cardinality all differ.

Explicitly forbidden in any write-up of this task:

- calling the tier profile a **causal effect of context length**;
- calling it a **degradation law** or fitting a trend line to four strata;
- extrapolating beyond 10M;
- reading ALL@3 differences across tiers as scale effects.

Mandatory sensitivity reporting: results stratified by gold cardinality (buckets 1, 2, 3, 4–6, 7+)
and by ability, so composition cannot be mistaken for scale.

---

## 6. Pre-specified outcomes

Fixed before any outcome access. **Integrity is resolved first, and the remaining three categories
form an exhaustive, mutually exclusive partition** over the four tier contrasts.

**Step 1 — integrity gate.**

| Category | Definition |
| --- | --- |
| **Invalidation** | The signed-permutation control diverges from Native in top-three IDs, order or distances; or results vary across the twenty nuisance trials; or any integrity gate blocks |

If invalidation occurs, **no replication category is assigned** and no contrast is interpreted.

**Step 2 — only if integrity holds**, exactly one of:

| Category | Definition |
| --- | --- |
| **Full replication** | `D_t > 0` at all four tiers |
| **Heterogeneous (partial) replication** | at least one `D_t > 0` **and** at least one `D_t ≤ 0` |
| **No replication** | `D_t ≤ 0` at all four tiers |

These three are exhaustive and non-overlapping by construction.

**Sign-boundary arithmetic.** `D_t` is computed in exact rational arithmetic — every value is a
rational with denominator dividing `5 · n_t · lcm_i(|gold_i|)` — so `D_t > 0`, `D_t = 0` and
`D_t < 0` are exactly decidable with no tolerance and no threshold. This is a numerical-representation
rule fixed before outcome access; it is not a practical-significance threshold and must not be read
as one.

Per-tier descriptors, subordinate to the single global category and never overriding it:
`D_t < 0` is a **tier-local direction reversal**; `D_t = 0` is a **tier-local null**.

No rescue analysis follows any category. No threshold of "practical significance" is pre-specified,
and none may be introduced afterwards.

## 7. Stop rule (binding after outcome access)

No cohort repair. No rescue seeds. No additional rotations. No threshold tuning. No metric
substitution. No denominator change. No re-definition of tiers. No post-hoc exclusion of archives
or questions. If the run blocks, it blocks; it is not repaired into completion.

---

## 8. Binding execution conditions

Carried from the audit chain; all four must be bound in the sealed preregistration:

1. **POSIX filesystem with hard-link support.** The exclusive-commit path uses `os.link`; a
   non-POSIX target would need a re-audited commit path.
2. **Fresh authorization** declaring schema `V52_T4F1_RUN_AUTHORIZATION_V4` — the schema the
   byte-identical runner verifies. A prior authorization cannot be replayed.
3. **HMAC key custody.** Never stored in the repository, any audit package, any log or any output.
   Single-use, held by the Head Researcher.
4. **Trial-row reporting condition** bound explicitly, as the candidate seal requires.

---

## 9. What is still open before this can be sealed

- Head Researcher and co-chair approval of this document.
- A settled execution package. The runner has been byte-identical and audit-confirmed since V4;
  what remains unsettled is documentation consistency inside the candidate, which two independent
  audits have blocked. That is a packaging question, not an execution-correctness question, and it
  should be closed by removing restated values from bound documents rather than by further
  automated checking.
- A sealed preregistration binding this document's exact bytes, the cohort hash, the runner hash
  and the four conditions above.

Until all of that is complete, Task 4F1 remains `BLOCKED` for preregistration and execution, and
retrieval-quality outcome access remains `FORBIDDEN`.
