# V52 — Membership Effect Under Scale Equalisation: PREREGISTRATION DRAFT

Status: **`[DRAFT — NOT AUTHORIZED FOR EXECUTION]`**
Also: not approved, not sealed, not triggered. No runner or workflow exists for it.

Date: 2026-09-07
Author: Continuity Lead / co-chair
Authorization in force: the Head Researcher approved **preparation of a design and a preregistration
draft only**. That approval is explicitly *not* acceptance of this draft, not a sealing authority,
not permission to change any implementation, and not permission to run anything.

Nothing was executed to produce this document: no new code, no pilot, no model or corpus download,
no retrieval, no fitting, no ranking, no bootstrap, no agent. Task 4F1 remains
`SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.

---

## 1. Disclosure: this is a follow-up built on evidence already seen

This design was written **after** the coordinate-scale stage and the boundary-localization stage had
been run, audited and read. It is not a blind design and must not be presented as one.

Specifically, the following were known to the author before this draft existed:

- the membership gap between `B32` and `RANDOM32` on both benchmarks, and its per-seed spread on the
  `58001…58010` panel;
- that a `1/σ` rescaling recovers much of full-mixing damage, which is the accepted descriptive
  finding of the closed stage;
- that the scale rule `1/σ` was chosen in the prior stage partly on the evidence of a synthetic
  pilot;
- that block-normalised ratios misbehaved in the closed stage, which is why the estimand here is a
  difference.

**What is not known is Δ**, the quantity this design measures. No value of it exists anywhere, and
no arm combination in this design has ever been run.

## 2. The question

> After coordinate scales are equalised, does the spectral 32/64 split give different retrieval
> performance from a matched-size random split, and by how much less than it does unscaled?

## 3. Why this question, and why now

Priority is argued on **expected information gain per unit of preparation cost**, not on any claim
that this work is a precondition for anything else. It is not a prerequisite for the
representation-generalisation question, which can be taken up independently at any time and is on
its own merits the more important question.

The case for this one is narrow: it asks something currently unanswerable from the record, it is the
only question in the line whose entire control suite is already validated, and its preparation cost
is close to zero because every component exists and has been audited. Its expected gain is a bound
on how much of one already-established effect one already-characterised intervention accounts for.
Both possible answers change what a write-up may claim.

## 4. Frozen sources — inherited unchanged

The same LoCoMo and LongMemEval cohorts, dataset and adapter digests, archive-local SVD to 96
coordinates, archive-mean centering, `>= 0` sign quantization, `TOPK = 3`, 20 nuisance trials, the
same tie and nuisance scheme, and the same deterministic sharding as the audited stages. No frozen
artifact is modified. Task 4F1 execution candidates, seals, authorization state and outcomes are not
touched.

## 5. Order of operations, and what is learned from which data

This section is normative. Any implementation that reorders these steps implements a different
experiment.

**Step 0 — representation (inherited, unchanged).** The frozen base fits word TF-IDF, char TF-IDF
and an LSA block **on the archive's memory units only**, hstacks them, reduces to 96 dimensions with
`TruncatedSVD` at the frozen random state, normalises, and subtracts the archive mean to give `C`.
The query is *transformed* by those already-fitted objects and centered by the same archive mean to
give `q`. **Nothing in the representation is fitted on queries, gold sets, answers or outcomes.**

**Step 1 — scale.** `σ_i` is the standard deviation of coordinate `i` computed on `C`, the exact
centered archive representation used downstream, **per archive, from archive content only**.
`d_i = 1/σ_i` when `σ_i ≥ ε` and `d_i = 1` otherwise, `ε = 1e-12`. `D = diag(d)`.
**Learned from: the archive's own centered representation. Never from queries, gold sets, retrieval
outcomes, or any other archive.** The count of coordinates falling back to `1` is recorded per
archive.

**Step 2 — group membership.** Two partitions of the 96 coordinate indices into a 32-set `S` and its
64-complement `T`:

- `B32`: `S = {0,…,31}`, the leading SVD components in variance order. Determined entirely by Step 0,
  i.e. by archive content. No per-experiment fitting.
- `RANDOM32`: `S` is the first 32 entries of a permutation drawn from a **partition seed**.
  Determined entirely by the seed. **No data enters this choice.**

**Step 3 — rotation.** From a **rotation seed**, draw `Q32` (32×32 Haar) and then `Q64` (64×64 Haar)
from one stream, head block first, exactly as the audited stages do. Build `R` by placing `Q32` at
`ix_(S,S)` and `Q64` at `ix_(T,T)`. **`B32` and `RANDOM32` at the same rotation seed use the
identical numeric `Q32` and `Q64` and differ only in `S`.** This is the essential control and is
inherited from the audited boundary runner; equality is asserted exactly, not within tolerance.

**Step 4 — order.** Centre → rescale → rotate: the scaled arms use `C D R` and `q D R`; the unscaled
arms use `C R` and `q R`. Because `D` is diagonal, coordinate `i` remains coordinate `i` under
rescaling, so membership in Step 2 is defined on the same indices in both scaled and unscaled arms.
**Scaling is applied before rotation and never between group selection and rotation.**

**Step 5 — scoring (inherited).** Sign quantization at zero, Hamming distance, `TOPK = 3` with the
frozen tie priority and 20 nuisance trials, fractional recall against the frozen gold sets.

## 6. Arms

| arm | archive transform | membership | purpose |
|---|---|---|---|
| `NATIVE` | `C` | — | control; must reproduce the frozen anchors |
| `SCALED_NATIVE` | `C D` | — | identity check: sign code and distances bit-identical to `NATIVE`, or the run aborts |
| `B32_FRESH` | `C R(S=lead32)` | leading 32 | unscaled spectral split |
| `SCALED_B32` | `C D R(S=lead32)` | leading 32 | same `R` as above |
| `RANDOM32_FRESH` | `C R(S=perm32)` | random 32 | unscaled matched random split |
| `SCALED_RANDOM32` | `C D R(S=perm32)` | random 32 | same `R` as above |

## 7. Primary estimand — one definition, no alternatives

Per benchmark independently. Per **rotation seed** `s`, paired at the question level, with the
partition seed `p_s` fixed to `s` by position:

```
G_s        = R@3(B32_FRESH, s)  − R@3(RANDOM32_FRESH, s, p_s)      the membership gap, unscaled
G_scaled_s = R@3(SCALED_B32, s) − R@3(SCALED_RANDOM32, s, p_s)     the membership gap, scaled
Δ_s        = G_scaled_s − G_s                                       the change in the gap
```

**Primary quantity: the mean over the ten seeds of `Δ_s`, in percentage points.** Per-seed values are
reported alongside. There is **no division** in the primary quantity.

**Aggregation order is fixed here, before any run:** the quantity is defined per seed and then
averaged over the seed panel. This matches the ruling that the per-seed-then-average form is the
preregistered aggregation, and it is stated in advance rather than settled afterwards.

**Pairing:** at (question, rotation seed). A scaled arm and its unscaled partner share the identical
rotation matrix; `B32` and `RANDOM32` at the same seed share the identical `Q32` and `Q64`.

**Explicitly not the primary quantity:** any ratio whose denominator is the block loss
`R@3(NATIVE) − R@3(BLOCK32)`. That quantity approached zero in the closed stage and its ratio is
barred here.

## 8. Decision rule, its scale, and its preconditions

The bands are applied to `Δ̄ / Ḡ`, where `Δ̄` and `Ḡ` are the seed-panel means of `Δ_s` and `G_s`
**both measured in this run**. `Ḡ` is the membership gap, a different quantity from the block loss
of §7, and it is measured here rather than inherited.

- `Δ̄ / Ḡ ≥ −0.20` → `[SCALE EQUALISATION ALONE DOES NOT ACCOUNT FOR THE MEMBERSHIP GAP]`
- `Δ̄ / Ḡ ≤ −0.60` → `[SCALE EQUALISATION ACCOUNTS FOR MOST OF THE MEMBERSHIP GAP]`
- otherwise → `[PARTIAL]`

**Basis for the cut points, written and not fitted.** `0.20` and `0.60` keep the programme on one
scale of "little" and "most": `0.20` is the lower cut already frozen in the coordinate-scale
preregistration, and `0.60` is deliberately looser than that document's `0.70` because `Δ` is a
difference of differences and therefore noisier than a single fraction. No value of `Δ̄` or `Ḡ` for
this arm combination exists, so nothing here can have been fitted to an observed result.

**Preconditions, checked at run time on this run's own arms.** The normalised reading is applied
only if both hold:

1. `G_s > 0` on every one of the ten seeds;
2. `Ḡ ≥ 2.0` percentage points.

If either fails, the verdict is `[WITHHELD — GAP SCALE UNSUITABLE]` and `Δ̄` is reported in
percentage points descriptively, with no band. The prior stage observed a gap of `8.448609` pp on
LoCoMo and `13.203121` pp on LongMemEval **on a different seed panel**; that is the reason `2.0` pp
is a loose floor rather than a prediction, and those figures are **not** a guarantee about this run.
`Ḡ` here is a new measurement on a new panel.

## 9. Uncertainty, dependence, multiplicity, and what may not carry the verdict

**What may not carry the verdict, on its own or in combination:** the sign of `Δ̄`; the fact that
per-seed ranges of two arms do or do not overlap; a difference visible in a point estimate without
its dispersion. These are point observations on one fixed panel and are not evidence of a population
difference.

**Reported for every arm and for `Δ`:** the seed-panel mean and the per-seed range.

**Resampling.** A question-level paired bootstrap on both benchmarks, and a
conversation-clustered bootstrap on **LoCoMo only**. Both are **sensitivity analyses, not certified
sampling intervals**. The LoCoMo clustered bootstrap resamples from **ten** conversations; ten
clusters is a very small number and the resulting interval will be wide and unreliable. That is a
limitation to be stated with the number, not a reason to omit it.

**No clustered bootstrap on LongMemEval.** Its 470 primary questions form a single shared-session
dependency component. That finding is **inherited from Task 3A.1 and provenance-verified, not
recomputed**, and any citation of it must carry that label. A cluster bootstrap over one cluster is
ill-posed.

**Seeds.** Rotation and partition seeds are a nuisance factor, not independent statistical units.
Ten seeds is a small panel. Per-seed dispersion describes the panel and does not license a
population statement.

**Multiplicity.** Two benchmarks × one primary band = two decisions. They are reported separately
and never pooled; no cross-benchmark statistic is defined, so no cross-benchmark correction is
implied. Agreement between the two benchmarks would be a consistency observation under **one shared
pipeline**, not an independent replication.

**Numerical representation is a separate matter from sampling uncertainty.** Differences between a
printed decimal and an exactly computed value, of the order `1e-14` in this programme's records, are
a reporting-precision question. They are not evidence about estimator stability in either direction
and must never be mixed into, or substituted for, resampling uncertainty. Both are reported; neither
is used to argue the other.

**Defensible generalisation.** Question-level statements about the frozen LoCoMo and LongMemEval
panels under one shared pipeline. Not conversation-level for LongMemEval. Not population-level for
either. Not beyond this representation.

## 10. What each outcome would and would not license

**The gap persists (`Δ̄ / Ḡ ≥ −0.20`).** Licensed: *the specific scale intervention defined in §5 —
`1/σ` on the centered archive representation — is not by itself sufficient to account for the
membership gap.* **Not licensed:** that axis ordering is the operative factor; that two separate
causal mechanisms exist; that coordinate scale plays no role, since it could participate through a
route this intervention does not touch; or that any alternative explanation is positively supported.
Ruling one intervention insufficient is elimination, not identification.

**The gap shrinks (`Δ̄ / Ḡ ≤ −0.60`).** Licensed: *this rescaling accounts for most of the membership
gap on the frozen panel.* **Not licensed:** that a single mechanism underlies both this and the
full-mixing result; that the membership finding is explained; or that anything has been identified.
Consistency with a shared channel is not identification. This outcome would also **weaken the
independence** of the audited membership result, and that cost must be carried in any write-up.

**Partial.** Bounds the share on a contrast that is a difference rather than a ratio over a near-zero
denominator. Using a difference removes that specific failure mode and does **not** automatically
dissolve floor or ceiling effects or any other source of uncertainty.

**Any outcome.** Does not identify a mechanism, establish necessity or exclusivity, prove or
disprove the participation of coordinate scale in general, claim production benefit, transfer to
other encoders or corpora, or license upgrading a `[LEAD]`.

## 11. Controls, all mandatory — any failure yields `[INVALID / VERDICT WITHHELD]`

1. Source and cohort identity match the frozen anchors.
2. `NATIVE` reproduces the frozen anchors within `1e-12`.
3. `SCALED_NATIVE` sign code and distance vector **bit-identical** to `NATIVE`; a deliberately
   negative diagonal must be rejected.
4. Every rotation matrix orthogonal to `1e-12`.
5. `B32` and `RANDOM32` at the same seed use `Q32` and `Q64` equal with **maximum absolute
   difference exactly `0.0`**.
6. Partition cardinality, uniqueness, disjointness and exhaustiveness checked per seed.
7. Norm and dot invariance checked **within** a representation and its own rotation, in the narrowed
   query-to-archive scope, at `1e-12`; never asserted between `C` and `C D`.
8. Signed-permutation Hamming invariance exact.
9. Non-finite values abort rather than being repaired, checked on `C` and again on `C D`.
10. Degenerate-coordinate counts recorded per archive.
11. Per-question records persisted for **every** arm and seed, so all aggregates can be rebuilt by an
    auditor without re-running.
12. Every check above paired with a negative control demonstrated to fail.

## 12. Seeds, scope and stopping rule

Rotation seeds `60001…60010`; partition seeds `70001…70010`, paired by position. Ten seeds, once,
per benchmark. Fresh panels, not the audited `58001…58010` or the coordinate-scale `59001…59010`, so
that no panel already known to show an effect is reused. **No replacement seeds after outcome
access.**

## 13. No-tuning rule

After outcome access: no alternate scale rule, no learned `D`, no alternate `ε`, no extra or
replacement seeds, no additional arms, no threshold movement, no alternate membership definition, no
reranking, no change of aggregation order. A different rule is a different, separately preregistered
experiment.

## 14. Minimum scope, resources and estimated time

**Scope.** Two benchmarks × ten seeds × six arms. LoCoMo as a single job; LongMemEval as ten
deterministic shards plus an aggregate.

**Code.** Two runners assembled from already-validated components — the frozen bases, the audited
boundary runner's matched partition construction, and the closed stage's scale rule, identity check
and narrowed invariance check — plus their negative-control test suites. **None of it is written
yet**, and writing it is not authorized by this draft.

**Data and models.** No new corpus and no model. The LongMemEval workflow already fetches the pinned
dataset it verifies by hash.

**Memory.** As the audited stages; the invariance check is already narrowed away from the archive
Gram matrix.

**Time.** Of the order of minutes rather than hours. **This is an expectation, not a guarantee.** It
is reasoned from the fact that the arm count, seed count, cohorts and per-question workload are the
same as a stage that has run — not from a promise that a past duration repeats. Queueing, runner
variance, a different invariance-check cost, or any implementation difference could move it. A
factor of two either way would not change whether the experiment is worth running.

**Money.** None beyond GitHub Actions minutes already in use.

## 15. What must happen before this could ever run

In order, each a separate decision that this draft does not make: Head Researcher review and
acceptance of the design; implementation of the two runners and their tests in a non-triggerable
location; independent review of that implementation; a pre-run seal binding every blob; exactly one
trigger; and a cold-start independent audit afterwards by a session that did not prepare it.

**The author of this draft must not seal it and must not run it.**

## 16. Outcome boundary

LoCoMo and LongMemEval mechanism track only. No corpus was read, no model downloaded, no code
written, no experiment, pilot, retrieval, fitting, ranking or bootstrap run in producing this draft.
No Task 4F1 artifact, candidate, seal, authorization or HMAC material was touched.
