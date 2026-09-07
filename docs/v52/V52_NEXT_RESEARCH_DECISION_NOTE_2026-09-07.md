# V52 — Next Research Decision Note: Option A versus Option B

Date: 2026-09-07
Author: Continuity Lead / co-chair
Status: **`[DECISION NOTE — NOT A PREREGISTRATION, NOT A SEAL, NOT A RUN AUTHORIZATION]`**

No experiment, retrieval, fitting, ranking, bootstrap or seed sweep was run to produce this note. No
corpus was read, no model downloaded, no dependency graph recomputed, no agent commissioned. It is
read-only analysis over committed artifacts, plus arithmetic on numbers already in the repository.

Verification performed first: `origin/main` is `675e6d8392675355ceb49bb8ec2ce3fb02116103` and has
**not** advanced since the reference in the task; the Claude→Codex handover blob hashes to
`240c5256…` as claimed; `ops/CURRENT_STATE.json` records `ledger_entry` `L-063`, `state_writer`
"Continuity Lead only (sole writer)", `task_4f1_run` `BLOCKED`, outcome access `FORBIDDEN`. Hashes
were taken from raw Git objects, not from a working tree.

---

## 1. A narrow correction that must be made before either option is chosen

The task asks what the "three orders" figure in erratum **E8** rests on. Checking it against the
audit's own evidence file `evidence/c4b_exact_rational.json` at `16e95a80`, **the claim as I relayed
it is not supported**, and I withdraw it.

What the evidence actually measures is `|document printed value − exact rational value|` for each of
A and B in four benchmark/arm cells. It therefore mixes float64 computation error with my own
decimal truncation when typing the decision document. It is **not a clean estimator-stability
measurement in either direction.**

| benchmark / arm | err(A) | err(B) | larger |
|---|---:|---:|---|
| LoCoMo / full | 2.542e-16 | 2.858e-16 | B by 1.1× |
| LoCoMo / block | 9.682e-15 | 1.102e-14 | B by 1.1× |
| LongMemEval / full | 2.108e-16 | 6.345e-16 | B by 3.0× |
| LongMemEval / block | 4.723e-16 | 7.270e-15 | B by 15.4× |

Three consequences, reported narrowly and without opening a new audit chain:

1. **"A is less numerically stable than B, confirmed by exact arithmetic" is not supported.** In
   four cells out of four, B's error is the larger one. The audit report's F8 narrative draws an
   A-versus-B conclusion from a table that compares **arms**, not estimators. That is a real
   inconsistency between the audit's narrative and its own evidence, and it is recorded here rather
   than adjudicated.
2. **"Three orders of magnitude" is wrong.** Pooling both estimators, the block/full arm gap is
   `1.102e-14` against `6.345e-16` — **1.24 orders**, about 17×. My Turkish relay compounded the
   error by rendering "three orders" as "üç kat" (three times).
3. **What survives of E8 is the conceptual point, and it survives on different evidence.** Averaging
   ten ratios whose denominators change sign within their own envelope is a fragile construction.
   That rests on deviation-register **D4** — LoCoMo block per-seed denominators from −0.0066 to
   +0.0164, per-seed fractions from −3.40 to +2.64 — not on the audit's error table. **The direction
   also survives**: the fragility is a property of the block-arm denominator, so it strengthens the
   refusal of the comparative claim regardless of which estimator is primary.

**No estimator ruling changes.** A remains the preregistered estimand on the textual grounds of §7,
which never depended on numerical stability. Estimator fragility is not evidence that a mechanism is
absent, and nothing here touches that.

The Codex handover repeats the unsupported phrasing and is superseded on this point by this note.

## 2. What is fixed before either option

The closed stage's boundaries carry forward unchanged: the LoCoMo result is a computational
reproduction of the same implementation and not an independent methodological replication; the
comparative mechanism claim is **not established on current evidence and outside the acceptance
scope**, which is not a demonstration that no mechanism exists; A is the preregistered statistic and
B is preserved as the historical implementation output, with no re-selection by looking at outcomes;
the §7/§9 conflict is a recorded open deviation and cannot be repaired retroactively; the
LongMemEval single-component finding is **inherited and provenance-verified, not recomputed here**.

---

## 3. Option A — mechanism decomposition inside the current representation

> After coordinate scales are equalised, does the spectral 32/64 split give different retrieval
> performance from a matched-size random split?

### Which open question it answers

Two facts sit next to each other and have never been connected. The **membership effect** is the
audited-established result: *which* coordinates form the leading block matters, not merely 32/64
block structure — 8.448609 pp on LoCoMo, 13.203121 pp on LongMemEval, with per-seed `rho` ranges
that do not overlap between `B32` and `RANDOM32` on either benchmark. Separately, the **accepted
descriptive finding** is that equalising coordinate scale recovers much of full-mixing damage.
Nobody has asked whether the second accounts for the first.

### What makes it not a repeat

The coordinate-scale stage compared scaled against unscaled **within** the full arm and within the
block arm. This compares `B32` against `RANDOM32` **under rescaling**. Those two arms exist in the
audited boundary stage but have never been run with a scale intervention. No completed computation
is repeated.

### What each outcome teaches, and what it does not

- **Gap persists.** Licensed: *equalising coordinate scale is not by itself sufficient to account
  for the membership gap.* Not licensed: that scale plays no role — it could participate through a
  route this intervention does not touch, and `1/σ` on the centered representation is one specific
  rescaling, not "scale" in general. Not licensed: that two separate causal mechanisms exist, nor
  that any particular alternative is supported. Elimination is not positive evidence.
- **Gap shrinks.** Licensed: *this rescaling accounts for most of the membership gap on the frozen
  panel.* Not licensed: a single mechanism, identification, or that the membership finding is
  explained. Consistency is not identification, and this outcome would **weaken the independence**
  of the audited membership result, a cost any write-up must carry.
- **Ambiguous.** Bounds the share on a contrast whose two terms are far apart. Using a difference
  rather than a ratio removes the near-zero-denominator problem specifically; it does **not**
  automatically dissolve floor or ceiling effects, nor any other source of uncertainty.

### Minimum viable design

Six arms: `NATIVE`, `SCALED_NATIVE` (bit-identity abort), `B32_FRESH`, `SCALED_B32`,
`RANDOM32_FRESH`, `SCALED_RANDOM32`. Ten fresh rotation seeds and ten fresh partition seeds.

**Order of operations, stated explicitly:** centre → rescale by `D = diag(1/σ)` computed on the
centered archive representation from archive content only → then apply the block rotation. `D` is
never derived from queries, gold sets or outcomes, and the scaled and unscaled partners share the
identical rotation matrix.

**The essential inherited control:** `B32` and `RANDOM32` must use the **identical numeric**
`Q32`/`Q64` blocks and differ only in which coordinates are assigned to them. This exists in the
audited boundary runner and must be carried unchanged.

**Primary estimand, aggregation order fixed in the text before anything runs** — per rotation seed,
then the seed-panel mean, matching the A ruling prospectively:

```
G_s        = R@3(B32_FRESH, s)  − R@3(RANDOM32_FRESH, s)
G_scaled_s = R@3(SCALED_B32, s) − R@3(SCALED_RANDOM32, s)
Δ_s        = G_scaled_s − G_s ;   primary = mean over seeds of Δ_s, per-seed values reported
```

Bands, to be frozen before the run, phrased as what the intervention accounts for rather than as
properties of a mechanism:

- `Δ ≥ −0.20 · G` → `[SCALE EQUALISATION ALONE DOES NOT ACCOUNT FOR THE MEMBERSHIP GAP]`
- `Δ ≤ −0.60 · G` → `[SCALE EQUALISATION ACCOUNTS FOR MOST OF THE MEMBERSHIP GAP]`
- otherwise → `[PARTIAL]`

**Basis for the band choices, written rather than fitted:** `0.20` and `0.60` are inherited from the
`0.20`/`0.70` cut points already frozen in the coordinate-scale preregistration, so the programme
keeps one scale of "little" and "most" rather than inventing a second. `0.60` rather than `0.70`
because `Δ` is a difference of differences and therefore noisier than a single fraction. These are
**not** chosen to fit any observed value; no outcome for this contrast exists.

**Uncertainty, dependence, pairing, multiplicity, seeds:** pairing is at (question, rotation seed),
with scaled and unscaled partners sharing the rotation. Report the seed-panel mean **and** the
per-seed range for `G`, `G_scaled` and `Δ`. Question-level paired bootstrap on both benchmarks;
conversation-clustered bootstrap on **LoCoMo only**; **no** cluster bootstrap on LongMemEval, whose
470 questions form one dependency component — cited as inherited and not recomputed. Two primary
bands over two benchmarks is four decisions; report them separately and pool nothing, so no
multiplicity correction is smuggled in by aggregation. Seeds are a nuisance factor, not independent
statistical units, and no seed may be replaced after outcome access.

**What generalisation would be defensible:** question-level statements on the frozen LoCoMo and
LongMemEval panels under one shared pipeline. Not conversation-level for LongMemEval. Not
population-level for either. Not beyond this encoder.

### Artifacts reusable, and what must be new

Reusable essentially whole: both frozen bases and their corpus acquisition and identity checks; the
audited boundary runner's `matched_random32_matrix` and `boundary_matrix`; the coordinate-scale
runners' `scale_matrix`, bit-exact identity check, narrowed invariance check and per-question
persistence; both workflow shapes with the seal-by-git-blob gate; the adapters, pinned at their
existing hashes; the frozen native anchors, which give a run-time proof that the pipeline is the
audited one.

New: the arm table and the `Δ` estimand; a fresh seed panel; the preregistration; a pre-run seal;
the two runners assembled from the existing pieces; negative controls for the new estimand.

### Cost

| item | estimate |
|---|---|
| new code | two runners assembled from validated pieces, plus tests — comparable to the coordinate-scale runners |
| data download | none new; the LongMemEval workflow already fetches the pinned 277,383,467-byte dataset it verifies by hash |
| model download | none |
| memory | same as the audited stages; the invariance check is already narrowed away from the archive Gram matrix |
| compute | LoCoMo one job; LongMemEval ten shards plus an aggregate |
| wall time | of the order of minutes |
| money | none beyond GitHub Actions minutes already in use |

**Basis and uncertainty.** The estimate comes from the coordinate-scale stage's own measured
timings: its LoCoMo invocation is recorded at **59.309 s** in the reproduction audit's run receipt,
and on the triggered run the LoCoMo result was persisted at `07:07:20Z` and the LongMemEval
aggregate at `07:11:15Z` against a trigger at `07:06:19Z`. Arm count (6), seed count (10) and cohort
sizes are identical here, so the dominant cost driver is unchanged. Uncertainty is mostly queueing
and runner variance rather than the computation; a factor of two either way would not change the
decision. This is an estimate from comparable recorded runs, not a measurement of this design.

### Independent controls and permissions required

Controls: native reproduction against the frozen anchors within `1e-12`; `SCALED_NATIVE`
bit-identical to `NATIVE` on distances, with a negative-diagonal rejection; orthogonality and
within-representation invariance at `1e-12`; exact matched-`Q32`/`Q64` equality between `B32` and
`RANDOM32`; signed-permutation Hamming invariance; per-question records for every arm and seed; and
negative controls proving each check can fail.

Permissions: a Head Researcher authorization; a preregistration approved before sealing; a pre-run
seal binding every blob; exactly one trigger. A cold-start independent audit afterwards, by a
session that did not prepare it.

---

## 4. Option B — generalisability across representation methods

> Does the observation appear under a text representation other than TF-IDF/SVD?

### Which open question it answers

The largest standing threat to this whole line, and the one no stage has touched: **the effect may
be a property of one representation rather than of memory retrieval.** LoCoMo and LongMemEval share
a single pipeline, so their agreement is a cross-benchmark check, not an independent methodological
replication. If the effect vanishes under another representation, every downstream claim narrows
sharply; if it survives, the line gains the external validity it currently lacks.

On value alone this is the more important question, and the programme's stated leaning toward it is
well founded.

### What "a different representation" would have to mean — and why the option is not yet well posed

This is the blocking issue, and it is definitional rather than empirical.

In the current pipeline the archive representation is built by hstacking word TF-IDF, char TF-IDF
and an LSA block, then reducing to 96 dimensions with `TruncatedSVD`, normalising, centering and
taking the sign. **The native coordinates are therefore SVD components, ordered by singular value.**
Every finding in this line is stated in that ordering: the spectral bands are `High32 = 0:32`,
`Mid32 = 32:64`, `Low32 = 64:96`; the boundary grid is a cut point in that index; "which coordinates
form the leading block" means *leading in variance order*.

That produces a fork with no free option:

- **Keep an SVD/PCA step** on top of a new encoder. The 96 axes are again variance-ordered, so the
  object of study survives — but a positive result is then consistent with the effect being a
  property of **variance-ordered truncation** rather than of the encoder, which is close to what the
  current result already shows. The risk that a new SVD step simply reproduces the old mechanism is
  real and is the main threat to interpreting this arm.
- **Drop the reduction** and take 96 dimensions directly from an encoder. Then the axes carry no
  ordering semantics, the 32/64 boundary has no referent, and the membership and spectral-position
  findings cannot even be posed — the intervention has nothing to intervene on.

So "does the observation generalise" is not one question. It is at least two: *does the
sign/Hamming advantage over continuous scoring survive a different encoder* (posable without axis
ordering), and *does the axis-ordering structure survive* (requires a reduction step and inherits the
confound above). Choosing between them is a design decision that should be taken deliberately, in
writing, before any compute is spent.

### What each outcome would teach, and what it would not

- **Effect appears under the new representation.** Licensed: the observation is not unique to this
  exact pipeline. Not licensed: universality — a single additional representation is one more point,
  not a population. Not licensed, under the SVD-preserving variant: that the encoder rather than the
  reduction is responsible.
- **Effect absent.** Licensed: the observation does not survive **this particular** substitution.
  Not licensed: that it is an artifact in general, because a null could equally come from the
  substitution changing something incidental — dimensionality, sparsity, normalisation or the
  meaning of a "coordinate".
- **Ambiguous.** The most likely outcome if the design question above is not settled first, because
  a partial result would be uninterpretable between encoder and reduction.

### Minimum viable design, conditional on the definitional question being settled

Freeze one candidate representation, chosen and justified **before** any result is seen and on
grounds independent of outcomes — for example a widely used sentence encoder selected for being
architecturally unlike TF-IDF, pinned by exact model identity and hash. Build and freeze a new
adapter with the same memory-unit construction, gold mapping and leakage controls the current
adapters enforce. Establish **new frozen anchors** for it, because none exist. Then run the minimal
arm set the chosen sub-question needs, with the same tie/nuisance scheme and per-question
persistence.

Fairness of the 96-bit comparison must be argued explicitly, not assumed: equal bit budget, equal
tie-breaking, equal centering, and a stated position on whether the comparison is at equal bits,
equal dimensions or equal storage. Those are not the same constraint.

### Artifacts reusable, and what must be new

Reusable: the benchmark cohorts and their dataset hashes; the memory-unit and gold-mapping
discipline; the metric, tie-breaking and nuisance scheme; the workflow and seal machinery; the
governance apparatus.

Must be new: the representation step itself; a new adapter with its own leakage audit; **new frozen
anchors**, which means there is no native-reproduction abort to prove the pipeline is the audited
one until they exist; the entire control suite for the new representation; and a defensible
justification of the encoder choice.

### Cost

| item | estimate |
|---|---|
| new code | a new adapter plus its leakage and identity audit — the largest single cost, comparable to Task 3A rather than to a runner |
| data download | the same pinned benchmark corpora |
| model download | one encoder, typically of the order of 10²  MB; must be pinned by hash and licence-checked |
| memory | higher than the current pipeline; dense encoder inference over every memory unit rather than sparse vectorisation |
| compute | encoding every memory unit in both benchmarks, then the retrieval arms |
| wall time | plausibly hours rather than minutes, dominated by encoding |
| money | none if it fits GitHub Actions limits; **this is the least certain line** |

**Basis and uncertainty.** There is **no comparable recorded run in this repository**, so unlike
Option A this estimate is not anchored to a measurement. It comes from the shape of the work — one
encoding pass over the archive units of 470 LongMemEval archives and 10 LoCoMo archives, plus the
existing retrieval cost — and the uncertainty is correspondingly wide. Whether it fits inside Actions
runner limits and timeouts is genuinely unknown and would need a small feasibility check before any
authorization. That check is **not** performed here.

### Independent controls and permissions required

Controls: everything Option A needs, plus a leakage audit of the new adapter equal to the one the
current adapters carry, plus new frozen anchors and a demonstration that the new pipeline is
deterministic under its pinned model.

Permissions: a Head Researcher decision on **which** sub-question is being asked; approval of the
encoder choice on stated, outcome-independent grounds; permission to download and pin a model;
confirmation that its licence permits this use; and then the ordinary preregistration, seal, trigger
and audit chain.

---

## 5. Recommendation — one next step

**Recommended next step: Option A.** **Option B is deferred, and not because it is less valuable.**

Three reasons, in order of weight:

1. **B is not yet a well-posed experiment; A is.** The effect under study is defined over
   variance-ordered axes. Any "different representation" must either keep a reduction step, which
   confounds encoder with reduction, or drop it, which removes the object of study. That fork is a
   decision to be taken in writing first. Spending the next effort on B before settling it risks a
   result that cannot be interpreted either way — the worst outcome available, and one the
   programme's own history with the block-arm denominator already illustrates.
2. **A's outcome changes what B should test.** If scale equalisation accounts for most of the
   membership gap, the property worth testing for generalisation is *scale heterogeneity*. If it
   does not, the property worth testing is *axis ordering*. Running B first means choosing that
   target by guess.
3. **The cost asymmetry is large and one estimate is anchored while the other is not.** A reuses
   every validated control and is estimated from this repository's own recorded timings. B needs a
   new adapter, a new leakage audit, new frozen anchors and a model download, and its cost estimate
   has no comparable run behind it.

**The condition under which this recommendation should be overridden:** if the programme's near-term
goal is external validity for a write-up rather than mechanism, then B is the right spend and A can
wait — but B should then begin with a short scoping decision on the fork above and a feasibility
check on encoding cost, not with an experiment. Both are cheap and neither needs compute
authorization.

**A third admissible answer is to defer both.** Nothing in the record is unstable, the closed stage
needs nothing further, and the open items that do not need an experiment — the `.gitattributes`
infrastructure item, the Drive backup, the GitHub default branch — are unblocked and currently
owned elsewhere.

## 6. What this note is not

It is a design and decision note. It is **not** a preregistration, not a seal, not a run
authorization, and it selects no threshold, seed, metric, model or experiment. Nothing in it may be
cited as evidence about any outcome. Task 4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION /
OUTCOME ACCESS FORBIDDEN` and is untouched.
