# Scientific Co-Chair Review — Task 4F1 Preregistration Draft

Reviewer role: **Scientific co-chair.** Not the author of the reviewed document; not an
implementation auditor.
Review date: 2026-09-03
Review type: Cold, byte-exact. No prior project context was sought or used.

---

## 0. Review target and provenance

| Field | Value |
| --- | --- |
| Reviewed commit | `e12ac9514f0cd1d5823465761893898480dcbf74` (`main`) |
| Preregistration path | `docs/v52/task4f1/TASK4F1_PREREGISTRATION_DRAFT_2026-09-03.md` |
| Required SHA256 | `ec3443ed4c60eb12e098192abf7b414e034d89fc63a9f42f9d0a02c36a696e45` |
| **Independently verified SHA256** | `ec3443ed4c60eb12e098192abf7b414e034d89fc63a9f42f9d0a02c36a696e45` |
| Verification method | `git show e12ac95…:docs/v52/task4f1/TASK4F1_PREREGISTRATION_DRAFT_2026-09-03.md \| sha256sum` |
| Draft size | 248 lines, 12157 bytes |
| Hash match | **YES — proceeding with review** |

### 0.1 Evidence discipline

No prior REQUEST CHANGES, Continuity Lead summary, commit message, `CURRENT_STATE`, continuity
ledger, or chat narrative was accepted as evidence for what the draft says. Every statement about
the draft below is derived from the verified bytes and cites the draft's own line numbers.

Two independent recomputations were performed against the frozen structural cohort
`audit_v52_t4f0_restricted_refreeze_2026_08_31/estimand_primary_cohort.csv`, whose SHA256 was
verified as `9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a`, matching the value
the draft asserts at line 11. That file's columns are
`audit_question_id, tier, conversation_id, ability, audit_category,
primary_evidence_cohort_eligible, eligibility_reason, gold_source_unit_count,
all_at_3_structurally_possible, gold_source_ids` — structural only, carrying no retrieval-quality
outcome.

---

## 1. Outcome-boundary declaration

**Declared:** This review accessed no Task 4F1 retrieval-quality outcome, and produced none.

- No Native-vs-Haar BEAM retrieval result, ranking, Hamming distance, metric value, per-seed
  aggregate, or arm comparison was read, computed, inferred, or written.
- The only quantities computed by this reviewer are functions of `tier`, `conversation_id`,
  `ability` and `gold_source_unit_count` — that is, frozen cohort structure. These are permitted
  structural cohort statistics.
- Task 4F1 was **not** preregistered, sealed, authorized, or run. No outcome-bearing execution path
  was invoked.
- `main` was not modified. The preregistration draft was not modified. No frozen candidate, audit,
  seal, corpus, or historical namespace was modified. This review is additive on a new branch.

---

## 2. Independent verification of the draft's structural claims

All structural claims in the draft's §2 were recomputed from the frozen cohort by this reviewer.
Every value reproduces exactly.

| Tier | Questions | Archives | Mean \|gold\| | ALL@3 possible | ALL@3 zeros | Mean ceiling | Share ceiling 1.00 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 100K | 355 | 20 | 3.08 | 259 | 96 | 0.867 | 73.0% |
| 500K | 629 | 35 | 4.26 | 461 | 168 | 0.836 | 73.3% |
| 1M | 553 | 31 | 8.59 | 300 | 253 | 0.721 | 54.2% |
| 10M | 175 | 10 | 7.47 | 105 | 70 | 0.776 | 60.0% |
| Pooled | 1712 | 96 | 5.74 | 1125 | 587 | 0.799 | 65.7% |

Eligible rows: 1712 of 2000. The structural substrate of the draft is **sound and byte-reproducible**.
No structural misstatement was found anywhere in §2.

One structural identity worth naming explicitly, because Amendment A1 below depends on it:
`all_at_3_structurally_possible` is exactly the predicate `|gold| ≤ 3`, and `|gold| ≤ 3` is exactly
the set of questions whose Fractional Recall@3 ceiling `min(1, 3/|gold|)` equals **1.000**. The
counts 259 / 461 / 300 / 105 are therefore simultaneously the ALL@3-possible counts and the
**zero-compression** counts.

---

## 3. Answers to the nine review questions

### Q1 — Ceiling-normalised estimand: `D_t^norm`

**Finding: `D_t^norm` as currently specified is not a rescaling of `D_t`. It is a different
estimand under a different, tier-dependent question-weighting scheme, and it makes cross-tier
interpretation harder rather than cleaner. This is the principal blocking issue.**

The draft defines (line 123):

```
D_t^norm = mean_i [ ( Native_i − mean_Haar_i ) / min(1, 3/|gold_i|) ]
```

Dividing *inside* the mean is algebraically equivalent to an importance-weighted mean of the raw
per-question differences with weight `w_i = 1 / min(1, 3/|gold_i|) = max(1, |gold_i| / 3)`.

Per-question rescaling is defensible on its own terms: it maps each question's difference from
`[−c_i, +c_i]` into `[−1, +1]`, so no single question's contribution is capped below another's.
The problem is the aggregation step. **The mean of the rescaled quantities is not a rescaling of
the mean of the raw quantities.** It is a `|gold|`-weighted mean, and because `|gold|` composition
differs sharply across tiers, the weighting differs across tiers. Recomputed from the frozen cohort:

| Tier | n | max \|gold\| | max single-question weight | mean weight | top-1% of questions hold | top-10% hold | share with w > 1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 100K | 355 | 16 | 5.33 | 1.344 | 4.3% | 24.8% | 27.0% |
| 500K | 629 | 54 | 18.00 | 1.719 | 6.4% | 35.6% | 26.7% |
| 1M | 553 | 96 | 32.00 | 3.051 | 9.8% | 45.5% | 45.8% |
| 10M | 175 | 83 | 27.67 | 2.710 | 10.8% | 54.7% | 40.0% |
| Pooled | 1712 | 96 | 32.00 | 2.173 | 10.8% | 45.7% | 34.3% |

And by the draft's own mandated gold-cardinality strata (§5 line 179), showing **share of tier
questions / share of `D_t^norm` weight mass**:

| Tier | \|g\|=1 | \|g\|=2 | \|g\|=3 | \|g\|=4–6 | \|g\|≥7 |
| --- | --- | --- | --- | --- | --- |
| 100K | 29.0% / 21.6% | 36.9% / 27.5% | 7.0% / 5.2% | 18.6% / 23.4% | **8.5% / 22.3%** |
| 500K | 26.9% / 15.6% | 35.9% / 20.9% | 10.5% / 6.1% | 8.9% / 8.2% | **17.8% / 49.2%** |
| 1M | 17.9% / 5.9% | 20.1% / 6.6% | 16.3% / 5.3% | 21.0% / 11.0% | **24.8% / 71.3%** |
| 10M | 22.3% / 8.2% | 21.7% / 8.0% | 16.0% / 5.9% | 21.1% / 12.0% | **18.9% / 65.8%** |

Three consequences, all established **before any outcome exists**:

1. **The estimand changes, not merely the scale.** `D_t` answers "what is the average per-question
   advantage over the questions of tier `t`, each question counting once." `D_t^norm` answers "what
   is the average per-question advantage when a question with 96 gold units counts 32 times as much
   as a question with ≤3." Those are different scientific questions about different implied
   populations of interest. Neither is wrong a priori, but the draft nowhere states that the second
   question is being asked, and §3.2 (lines 126–127) motivates `D_t^norm` purely as a comparability
   correction, which it is not.

2. **The reweighting is tier-heterogeneous, which defeats the stated purpose.** `D_t^norm` exists
   (line 126–127) so that "a smaller raw contrast at 1M" is interpretable. But at 100K the top
   decile of questions carries 24.8% of the weight mass, while at 1M it carries 45.5%; the `|g|≥7`
   stratum carries 22.3% of the weight at 100K and 71.3% at 1M. Comparing `D_100K^norm` with
   `D_1M^norm` therefore compares two differently-weighted averages of different sub-populations.
   The normalization removes one cross-tier incomparability (achievable range) by introducing
   another (weighting), and the second is larger and less visible than the first. This is the
   precise failure mode the review brief asked me to test for, and it is present.

3. **`D_t^norm` is dominated by the stratum with the *least* homogeneous ceiling.** At 1M and 10M
   roughly two-thirds to seven-tenths of the weight sits in `|g|≥7`, where the ceiling ranges from
   0.429 down to 0.031. So the statistic intended to neutralize ceiling effects concentrates its
   mass exactly where ceiling variation is most extreme, and where the division amplifies each
   question's contribution most.

There is a further, separable defect: §2.2 (lines 92–94) states that `D_t` and `D_t^norm` "must be
**interpreted jointly**" and that "A conclusion supported by only one of the two is not reported as
supported." But §6 (lines 198–205) assigns the single global outcome category from the sign of
`D_t` alone. If `D_t > 0` at all four tiers while `D_t^norm ≤ 0` at some tier, §6 mandates "Full
replication" and §2.2 forbids reporting it as supported. **A preregistration must not contain two
decision rules that can return incompatible verdicts on the same data.** This is an unresolved
decision rule, not a stylistic gap.

**Options compared, as required.**

- **A — keep `D_t^norm` as a mandatory companion.** Rejected. It embeds an undisclosed,
  tier-varying reweighting into a co-equal decision input, and creates the §2.2/§6 conflict above.
- **B — demote to sensitivity/descriptive.** Necessary but not sufficient. It removes the decision
  conflict, but leaves the genuine problem the draft correctly identified in §2.2 unsolved: without
  *some* instrument, a smaller raw contrast at 1M really is ambiguous between "less retrieval
  advantage" and "less room to show one."
- **C — replace with gold-cardinality-stratified paired contrasts.** Strong, and nearly free: the
  draft already mandates exactly these strata (§5 line 179, buckets 1, 2, 3, 4–6, 7+) as sensitivity
  reporting. Stratification solves the comparability problem *without touching weights*, because
  within a stratum the ceiling is near-constant, so raw differences are directly comparable across
  tiers. Its only weakness is discarding the compact single-number summary.
- **D — stratified contrasts as the cross-tier instrument, plus `D_t^norm` retained as a declared
  sensitivity statistic.** **Selected.** It keeps the honest instrument and the compact summary,
  with the summary's weighting disclosed rather than hidden.

**The decisive fact making option D cheap** is the structural identity in §2 above: the stratum
`|gold| ≤ 3` has ceiling **exactly 1.000** — zero metric compression, nothing to normalize — and
has adequate cell sizes at every tier:

| Tier | n with ceiling ≡ 1.00 (`\|g\|≤3`) | n `\|g\|=4–6` | n `\|g\|≥7` (ceiling 0.031–0.429) |
| --- | ---: | ---: | ---: |
| 100K | **259** (73.0%) | 66 | 30 |
| 500K | **461** (73.3%) | 56 | 112 |
| 1M | **300** (54.2%) | 116 | 137 |
| 10M | **105** (60.0%) | 37 | 33 |

A cross-tier comparison restricted to `|gold| ≤ 3` is **ceiling-free by construction**, needs no
normalization, no reweighting, and no assumption — and it is already a named, frozen quantity in
the cohort. This should be the primary cross-tier comparability instrument. See Amendment **A1**.

**Verdict on Q1: REQUEST CHANGES.**

---

### Q2 — Primary scientific object: four tier contrasts vs. pooled contrast

**Finding: the draft's choice is correct. Keep the four tier-specific contrasts as the primary
family. No change required.**

The reasoning in §1 (lines 18–35) survives scrutiny, and independent grounds strengthen it:

1. **The pooled contrast is largely redundant.** LongMemEval (470 questions) and LoCoMo (1,535
   questions) already supply two fixed-benchmark, same-direction replications. A third pooled
   number is a third instance of a result already held twice. Its marginal information is low.

2. **The pooled contrast is not a clean estimand.** Recomputed, the pooled 1,712-question mean is a
   composition-weighted mixture whose tier shares are 20.7% / 36.7% / 32.3% / 10.2% — shares fixed
   by BEAM's construction, not by any scientific choice. Mean `|gold|` varies 3.08 → 8.59 across
   those strata and mean ceiling varies 0.867 → 0.721. So the pooled number answers "what is the
   effect on a benchmark whose tier mix someone else chose," which has no stable referent and is
   not comparable in composition to LongMemEval or LoCoMo either. Promoting it to primary would
   promote the least interpretable quantity in the document.

3. **The scale axis is the only genuinely new information BEAM supplies.** ~287 → ~20,870 raw
   message units within a single benchmark and single protocol (line 25–27) is a within-benchmark
   axis that neither prior benchmark has at all. If the tier profile is demoted to secondary, the
   task's entire incremental contribution is demoted with it.

4. **Tier-primary is the design that can fail.** Four separately-reported contrasts admit
   heterogeneity and tier-local failure as pre-specified, reportable outcomes (§6 lines 198–209).
   A pooled headline can absorb a tier-local failure into an aggregate and survive it. Choosing the
   design with more ways to be falsified is the correct choice, and it is notably *not* the design
   that is easiest to summarize — the draft explicitly accepts "There is no single headline number"
   (line 110). That is the right trade.

The draft's handling of the pooled contrast — retained, but explicitly secondary and framed as a
replication summary comparable to §1 (lines 147–148) — is correct and should be preserved verbatim.

**One limitation to record so it cannot later be silently strengthened:** the tiers are confounded
with composition. Mean `|gold|` runs 3.08 / 4.26 / 8.59 / 7.47 and archive counts run 20 / 35 / 31 /
10. Any observed tier profile is therefore a **scale-or-composition** profile, never a scale profile.
The draft acknowledges this (§5 lines 169–171, 179–180) and Amendment A1 materially reduces it by
supplying a composition-matched cross-tier view. It is not fully removable, and the write-up must
not describe it as removed.

**Verdict on Q2: ACCEPT as designed.**

---

### Q3 — Uncertainty

**Finding: the draft's refusals are correct and well-reasoned. But it conflates two of the three
distinct senses of uncertainty, and omits the one descriptive summary that is both legitimate and
material to its own pre-specified outcome rule.**

Taking the three senses separately, as required.

**(a) Population inference beyond the fixed BEAM benchmark.** The draft's refusal (lines 154–156)
is **correct and should not be softened**. The 1,712 questions are an enumerated, frozen set, not a
sample. p-values, question-level confidence intervals, and multiplicity correction would all
presuppose a sampling model that does not exist here. The explicit statement that no multiplicity
correction is applied *because no tests are performed* (lines 162–163) is good practice: it
forecloses the later misreading of an absence as an oversight. I endorse this in full and
specifically decline to request error bars for conventional reasons.

**(b) Descriptive stability of the finite benchmark contrast.** **This is a genuine gap.** Rejecting
population inference does not establish that the finite contrast's own composition is irrelevant.
The questions are **heavily clustered within archives**, and the draft never addresses this:

| Tier | Questions | Archives | Questions per archive | Effect of dropping one archive |
| --- | ---: | ---: | ---: | ---: |
| 100K | 355 | 20 | 17.8 | ~5.0% of tier questions |
| 500K | 629 | 35 | 18.0 | ~2.9% |
| 1M | 553 | 31 | 17.8 | ~3.2% |
| **10M** | **175** | **10** | **17.5** | **~10.0%** |

The 10M tier contrast rests on **ten archives**. Under §6 the *sign* of each `D_t` determines the
single global category, and one tier flipping sign moves the verdict from "Full replication" to
"Heterogeneous replication". So the question "would this tier's sign survive the removal of a single
archive?" is directly material to the pre-specified outcome classification — it is not decoration.

A **leave-one-archive-out (LOAO) range** on each `D_t` answers exactly this, and it makes **no**
population claim whatsoever. It is a statement about the sensitivity of a fixed statistic to its own
enumerated composition — the same epistemic status the draft already grants the per-seed min–max
spread (lines 116–118). It requires no additional execution, only re-aggregation of per-question
values the run already produces. It must be pre-specified now, while outcome-free, precisely so it
cannot be introduced later as a rescue or suppressed as inconvenient. See Amendment **A4**.

To be unambiguous: I am **not** requesting confidence intervals, standard errors, cluster-robust
variance, or any interval with coverage semantics. LOAO min–max is a descriptive range and must be
labelled as such.

**(c) Stochastic variation from Haar seed choice.** The draft's treatment (lines 157–158, and
116–118) — report all five per-seed aggregates and the min–max spread, with no inference to the
rotation distribution — is correct and sufficient. But see Q7: §4's wording contradicts §3.1's
framing of what those five seeds *are*.

**The 20 nuisance trials** (lines 159–161) are correctly excluded as a variance source. They are
deterministic replication identities; treating byte-identity checks as statistical units would be
an error, and the draft says so plainly. Endorsed without change.

**Verdict on Q3: REQUEST CHANGES — narrowly, for (b) only.** The refusals under (a) and the
treatment of (c) and the nuisance trials are accepted as correct.

---

### Q4 — Win / tie / loss

**Finding: W/T/L retains some value, but ties are structurally guaranteed to dominate, and the tie
rate is driven by `|gold|` composition that differs across tiers. It must be scoped, not removed.**

Fractional Recall@3 is supported on a coarse rational grid whose coarseness is set by `|gold_i|`:

| `\|gold\|` | Attainable values | Distinct values | Share of pooled cohort |
| --- | --- | ---: | ---: |
| 1 | {0, 1} | 2 | 23.9% |
| 2 | {0, ½, 1} | 3 | 29.6% |
| 3 | {0, ⅓, ⅔, 1} | 4 | 12.2% |

So **65.7% of the pooled cohort takes at most four distinct values**, and 23.9% is strictly binary.
On a binary question the arms tie whenever both retrieve the gold unit or both miss it. Structural
tie dominance is therefore near-certain, and this is knowable before any outcome.

The consequence that matters is not tie dominance itself but its **cross-tier incomparability**.
The share of questions with `|gold| = 1` is 29.0% at 100K and 17.9% at 1M; the share with
`|gold| ≤ 3` is 73.0% at 100K and 54.2% at 1M. The tie rate will therefore differ across tiers for
reasons that are purely compositional. A reader comparing tie rates across tiers would be reading
gold-cardinality composition and calling it scale.

The draft bars ALL@3 from all cross-tier scale claims for precisely this reason (§3.3 lines
132–133: "because gold cardinality drives it directly"). **W/T/L is exposed to the same mechanism
and carries no such bar** (lines 134–136). That asymmetry is the defect.

**Decision: keep W/T/L as descriptive, with two scoping constraints** (Amendment **A5**):

1. Bar cross-tier comparison of raw W/T/L counts and tie rates, on the same grounds as ALL@3;
   report W/T/L **within gold-cardinality strata** where cross-tier reading is intended.
2. Add `W / (W + L)` — the tie-excluded directional share — as the paired-effect summary. It is
   materially less distorted by structural ties, is still purely descriptive of the fixed
   benchmark, and costs nothing extra to compute.

Removal is not warranted: within a stratum, W/T/L is an honest and readable paired summary, and it
is the established house method.

**Verdict on Q4: REQUEST CHANGES — scoping only.**

---

### Q5 — Outcome classification: exclusivity, exhaustiveness, and the `D_t = 0` boundary

**Finding: the partition is formally correct. Two boundary defects at `D_t = 0` remain, one of them
material to falsifiability.**

**The partition is sound.** Let `P = {t : D_t > 0}` and `N = {t : D_t ≤ 0}`. `P` and `N` partition
the four tiers by construction. The three Step-2 categories map to `|P| = 4`, `1 ≤ |P| ≤ 3`, and
`|P| = 0` respectively. Exactly one holds for any assignment. **Mutually exclusive and exhaustive —
confirmed.** Resolving Invalidation first as a Step-1 gate (lines 189–195), rather than as a fourth
peer category, is cleaner than the alternative and is endorsed. The "tier-local direction reversal"
descriptor is correctly subordinated to the global category and cannot override it (lines 207–209).

**Defect 1 — no numerical resolution rule at the sign boundary. Material.**

The entire global category turns on the sign of four real numbers, and the draft specifies no
arithmetic by which "> 0" and "≤ 0" are decided. Under IEEE-754 accumulation, a genuinely null tier
can land at ±1e-17 and decide between "Full replication" and "Heterogeneous replication" on
representation error. §6 line 211 then forecloses the repair: "No threshold of 'practical
significance' is pre-specified, and none may be introduced afterwards." So the ambiguity cannot be
resolved after outcome access without violating the draft's own stop rule. **It must be resolved
now.**

The fix is clean because the quantities are exactly rational. Every `FracRecall@3` value is a
rational with denominator `|gold_i|`; each per-question difference has denominator dividing
`5·|gold_i|`; and `D_t` has denominator dividing `5·n_t·lcm(|gold_i|)`. Exact rational arithmetic
therefore makes `D_t = 0` a **well-defined, decidable event** with no tolerance and no threshold.
See Amendment **A2**.

**Defect 2 — `D_t = 0` is mislabelled a "reversal". Small but squarely on the boundary.**

Line 207: "A tier with `D_t ≤ 0` may additionally be described as a **tier-local direction
reversal**." At `D_t = 0` exactly nothing is reversed; the contrast is null. Describing an exact
zero as a direction reversal overstates it, and does so in the one case Q5 exists to examine.
Restricting the descriptor to `D_t < 0` and adding a **tier-local null** descriptor for `D_t = 0`
costs one line and removes the misdescription. See Amendment **A3**.

**A third boundary observation, recorded but not blocking.** "No replication" (`D_t ≤ 0` at all
four tiers) covers both a uniform exact null and a uniform substantial reversal. These are very
different scientific situations — a consistent reversal across all four tiers would be a striking
finding, not merely an absence. The per-tier descriptors under Amendment A3 make the distinction
visible in the report, which is sufficient; I do not require a fourth global category, because
adding one would break the clean trichotomy for a case that the descriptors already capture.

**Verdict on Q5: REQUEST CHANGES — Amendments A2 and A3.**

---

### Q6 — Interpretation boundary: ability balance and non-monotonic ceilings

**Finding: both previously identified overclaims are correctly retired. This section is now
accurate. No change required.**

**Ability balance (§2.1, lines 58–67).** The draft states the claim "at exactly its strength": *no
obvious marginal ability-composition imbalance explains tier differences*; then explicitly: "It does
not establish that ability is not a confounder. Marginal balance says nothing about the joint
distribution — ability could still covary with gold cardinality or archive length inside a tier."
It then makes ability-stratified reporting **mandatory** and states it "is not discharged by this
measurement" (lines 66–67). This is the correct epistemic move: a marginal balance check is a
measured structural fact, and the draft refuses to convert it into a causal no-confounding
conclusion. **No overclaim present.**

**Non-monotonic ceilings (§2.2, lines 87–94).** The draft states that the ceiling profile "does not
mechanically impose a monotone ordering on the tier contrasts," and then immediately marks the gap:
"That is weaker than saying a monotone observed profile cannot be explained by the ceiling — the
ceiling may still contribute through interaction with archive length, gold structure or other
unmeasured composition, and no measurement here excludes that." This is exactly right, and the
distinction between "does not mechanically impose" and "cannot explain" is the one that matters.
**No overclaim present.**

**§5 (lines 167–180)** forbids causal-effect language, "degradation law" framing, trend-fitting to
four strata, extrapolation beyond 10M, and cross-tier ALL@3 reading; and mandates gold-cardinality
and ability stratification. This is an appropriately strict boundary.

**One wording item recorded as imperfect-but-accepted, so it cannot be silently strengthened
later:** §1 line 29–30 names the scientific object "the **profile of the effect across scale**."
Given the tier/composition confound established in Q2, this is loose — it is a profile across tiers,
which are a scale-and-composition bundle. I do **not** block on it, because §5 constrains the
write-up explicitly and Amendment A1 supplies a composition-matched view. It is recorded here so
that "profile of the effect across scale" is not later cited as licence for scale-causal language
that §5 forbids.

**Verdict on Q6: ACCEPT.**

---

### Q7 — Haar target: finite mean of five enumerated seeds

**Finding: §3.1 is exemplary. §4 contradicts it in one clause. Small fix, material meaning.**

**§3.1 (lines 112–118) is correct and unusually precise.** The comparator is declared "a finite mean
over exactly five preregistered seeds"; the seeds are enumerated (`43001, 43002, 43003, 43004,
43005`) "and at no others"; the estimand is "a **fixed, enumerated comparator** — not as an estimate
of, and not as an inference to, the full Haar-rotation distribution"; and "No claim about 'Haar
rotations in general' follows from this task." The per-seed aggregates and min–max spread are
declared "sensitivity diagnostics on that fixed comparator, not a sampling distribution and not a
basis for interval estimation," and the same restriction is extended to the five ITQ seeds. This is
precisely the required framing.

**Consistency audit at every point the comparator is used:**

| Location | Text | Consistent? |
| --- | --- | --- |
| §3.1 line 105 | "mean over 5 Haar seeds" | Yes |
| §3.1 lines 112–118 | fixed enumerated comparator, no population inference | Yes — the governing statement |
| §3.2 line 123 | `mean_Haar_i` | Yes — inherits §3.1's definition |
| §3.3 line 135 | "the Haar mean" | Yes |
| §3.1 line 118 | same restriction for five ITQ seeds | Yes |
| **§4 line 157** | **"The only genuine stochastic element is seed choice."** | **NO** |

If the estimand is by definition the finite mean over five enumerated seeds, then seed choice is not
a stochastic element *of the estimand* at all — the seeds are constitutive of it. Calling seed
choice "the only genuine stochastic element" reintroduces exactly the sampling framing §3.1
forecloses: it implies the five rotations are a draw from a rotation population about which the
observed spread is informative. §3.1 says the opposite in explicit terms. A reader — or a later
write-up — could cite line 157 as licence for the generalization line 115 forbids.

This is one clause, but it is the clause that decides whether the comparator is *defined* or
*estimated*. See Amendment **A6**.

**Verdict on Q7: REQUEST CHANGES — one-clause wording fix (A6).**

---

### Q8 — Scientific value and stop/go decision

**Finding: GO — but explicitly as a bounded scale-profile study whose flat-replication value is
modest, which is the framing the draft itself already adopts.**

Answering the uncomfortable question directly, relative to the accepted LongMemEval and LoCoMo
evidence, and treating prior investment as irrelevant.

**Why running it is justified:**

1. **It is the only remaining source of a specific kind of evidence.** LongMemEval and LoCoMo
   already establish direction twice on fixed benchmarks. What they cannot establish, even in
   principle, is whether the effect holds across a ~2-order-of-magnitude context-scale range within
   a single benchmark and protocol (lines 25–27). BEAM supplies that axis; nothing else in the
   programme does.
2. **The informative outcomes are genuine falsification opportunities.** A tier-local failure or a
   changing profile would *bound the domain of validity* of a claim currently held only as "true on
   two fixed benchmarks." Bounding a claim's domain is real scientific information, and it is
   information a third same-direction replication cannot produce.
3. **The design has pre-committed against inflating a null.** §1 lines 37–40 state in advance that a
   flat, same-direction result carries "modest" marginal information "and should be reported as
   modest." Pre-registering the unfavourable interpretation of the most likely outcome is the single
   strongest integrity feature of this document, and it substantially reduces the main risk of
   running the study.
4. **Failure is detectable rather than ambiguous.** The signed-permutation negative control (§3.4,
   lines 141–143) is a mathematical identity, not an empirical comparison, so an invalid run is
   distinguishable from a null run. The stop rule (§7, lines 216–218) forecloses cohort repair,
   rescue seeds, extra rotations, threshold tuning, metric substitution, denominator changes, tier
   redefinition, and post-hoc exclusions. The cost is bounded and the failure modes are contained.

**Why the value must be stated as bounded, not high:**

1. Four strata is a very short axis, and no trend may be fitted to it (§5 line 175, correctly). The
   maximum yield is "the sign is or is not stable across four strata."
2. The strata are confounded with composition — mean `|gold|` 3.08 → 8.59, archives 20 / 35 / 31 /
   10 — so no observed profile isolates scale. Amendment A1 reduces this materially but does not
   remove it.
3. The 10M tier, where a scale effect would be most expected, is the thinnest: 175 questions from
   **10 archives**. Its conclusion is the least robust of the four, and it is the one most likely to
   drive the global category.
4. The most probable outcome, on the existing two-benchmark evidence, is a flat same-direction
   profile whose incremental value the draft itself pre-classifies as modest.

**Conclusion: worth running, as a bounded scale-profile and domain-of-validity study.** Not as a
third confirmation, and not as a scale law. Of the three options posed, I select the middle one and
reject the most flattering.

**Sunk cost explicitly discounted.** The recommendation is unchanged if all prior investment is set
to zero: the study is justified by the falsification opportunity on the scale axis alone. Equally,
the prior investment would not save it — had Q1's estimand defect gone unfixed, the recommendation
would have been to withhold approval regardless of work already done, which is what this review
does.

**Verdict on Q8: GO, bounded — conditional on the amendments below.**

---

### Q9 — Outcome-free integrity of the draft

**Finding: the draft is outcome-free. Confirmed by exhaustive mechanical scan.**

Every numeric literal in the 12,157 verified bytes was enumerated and classified:

| Draft lines | Values | Classification |
| --- | --- | --- |
| 19–22 | `54.197517730496%`, `38.271666666667%`, `23.654714666441%`, `13.770827054136%`, `+15.926 pp`, `+9.884 pp` | LongMemEval and LoCoMo — **previously accepted results on other benchmarks. Permitted.** |
| 25–26 | ~287 and ~20,870 raw message units | Archive size — **structural. Permitted.** |
| 48–56 | Tier question / archive / mean-`\|gold\|` / ALL@3 counts; excluded archives | **Structural. Permitted. Independently reproduced — all exact.** |
| 60–61 | Ability composition ranges | **Structural. Permitted.** |
| 72–80 | `0.375` ceiling example; mean ceilings and ceiling-1.00 shares | **Structural. Permitted. Independently reproduced — all exact.** |
| 108 | Denominators 355 / 629 / 553 / 175 | **Structural. Permitted.** |
| 114 | Seeds `43001`–`43005` | Preregistered constants — **not outcomes. Permitted.** |
| 147, 179, 187, 228, 232 | Cohort size 1,712; strata definitions; trial count; schema name | **Definitional. Permitted.** |
| all others | Section numbers (`2.1`, `2.2`, `3.1`–`3.5`) | Not data. |

**No BEAM Native-vs-Haar retrieval result, ranking, distance, metric value, per-seed aggregate, or
inferred arm comparison appears anywhere in the document.** The four retrieval-quality percentages
present are explicitly attributed to LongMemEval and LoCoMo (lines 18–22), both permitted. §9 lines
247–248 correctly hold outcome access at `FORBIDDEN`.

**Verdict on Q9: CLEAN — outcome-free integrity confirmed.**

---

## 4. Final verdict

`REQUEST CHANGES — SCIENTIFIC PREREGISTRATION DESIGN NOT YET ACCEPTED`

The draft is substantially sound. Its structural substrate is byte-reproducible, its outcome-free
integrity is intact, its refusal of population inference is correct, its interpretation boundary is
now honestly drawn, its Haar comparator is correctly framed in §3.1, its outcome partition is
formally valid, and its pre-commitment to reporting a flat result as modest is exemplary practice.

It is blocked on one substantive design defect and five small but material specification gaps.
The blocking defect is Q1: `D_t^norm` silently changes the estimand through a tier-heterogeneous
`|gold|` reweighting, is given co-equal interpretive authority in §2.2 that conflicts with §6's
`D_t`-only classification, and — because the reweighting differs by tier — makes cross-tier
interpretation harder rather than cleaner, defeating its own stated purpose. That must be fixed
before outcomes exist, because after outcome access any change to it is indistinguishable from
estimand selection.

---

## 5. Required amendments — smallest set that would secure approval

All six are local edits. **No part of the study design needs rewriting**; the tier-primary family,
the pooled secondary, the negative control, the stop rule, the outcome partition, the interpretation
boundary, and the binding execution conditions all stand as written.

### A1 — Restructure the ceiling-comparability instrument (blocking; §2.2, §3.2)

Replace the mandatory-companion status of `D_t^norm` with a three-part specification:

1. **Add a ceiling-free stratified contrast as the primary cross-tier comparability instrument.**
   Report `D_t` restricted to `|gold| ≤ 3` — the stratum whose ceiling is exactly 1.000 (n = 259 /
   461 / 300 / 105). Because it carries no compression, it is directly comparable across tiers with
   no normalization and no reweighting. Additionally report `D_t` within the strata already mandated
   at §5 line 179 (`4–6`, `7+`).
2. **Demote `D_t^norm` to a declared sensitivity statistic**, and state in §3.2 that it is a
   `|gold|`-weighted mean with weights `w_i = max(1, |gold_i|/3)`, that these weights differ in
   distribution across tiers, and that it is therefore **not** a rescaling of `D_t` and **not** a
   cross-tier comparability device.
3. **Resolve the §2.2/§6 conflict.** Replace "A conclusion supported by only one of the two is not
   reported as supported" (lines 93–94) with: the §6 global category is assigned from `D_t` alone;
   discordance between `D_t`, the stratified contrasts, and `D_t^norm` is reported as a labelled
   sensitivity flag accompanying the category, and never silently overrides or vetoes it.

### A2 — Pre-specify sign-boundary arithmetic (blocking; §6)

State that `D_t` is computed in exact rational arithmetic (all values being rationals with
denominator dividing `5 · n_t · lcm_i(|gold_i|)`), so that `D_t > 0`, `D_t = 0` and `D_t < 0` are
exactly decidable with no tolerance and no threshold. Record that this is a numerical-representation
rule fixed before outcome access and is not a practical-significance threshold under §6 line 211.

### A3 — Correct the `D_t = 0` descriptor (§6, line 207)

Restrict "tier-local direction reversal" to `D_t < 0`. Add "tier-local null" for `D_t = 0`. Both
remain per-tier descriptors subordinate to the single global category, exactly as line 208–209
already specifies.

### A4 — Pre-specify one descriptive stability statistic (§4)

Add: leave-one-archive-out min–max range for each `D_t`, computed over that tier's archives (20 /
35 / 31 / 10), reported alongside the per-seed min–max. Label it explicitly as a descriptive
sensitivity of a fixed statistic to its own enumerated composition — **not** a confidence interval,
**not** a standard error, and carrying **no** coverage or population semantics. It must be
pre-specified now so it can be neither introduced later as a rescue nor omitted as inconvenient.

### A5 — Scope win/tie/loss (§3.3, lines 134–136)

Add the same cross-tier bar that ALL@3 already carries: raw W/T/L counts and tie rates are not
compared across tiers, because tie structure is driven by `|gold|` composition, which differs across
tiers (share `|gold| = 1`: 29.0% at 100K vs 17.9% at 1M). Report W/T/L within gold-cardinality
strata where cross-tier reading is intended, and add `W / (W + L)` as the tie-excluded paired-effect
summary.

### A6 — Align §4 with §3.1 on the Haar comparator (§4, line 157)

Replace "The only genuine stochastic element is seed choice" with wording consistent with §3.1: the
five seeds are constitutive of the comparator's definition, not a sample from it; the per-seed
aggregates and min–max spread are reported to show how sensitive the fixed comparator is to which
rotations were enumerated, and license no claim about unenumerated rotations.

---

## 6. Recorded as imperfect but accepted

Listed explicitly so that none can later be cited as approved-in-full, and so that none can be
silently strengthened beyond the strength granted here.

1. **Four strata is a short scale axis.** Accepted because §5 line 175 forbids trend-fitting and
   line 176 forbids extrapolation beyond 10M. The tier profile may be reported as a profile; it may
   not be reported as a law, a trend, or a function of context length.
2. **Tiers are confounded with composition** (mean `|gold|` 3.08 → 8.59; archives 20 / 35 / 31 /
   10). Accepted because §5 lines 179–180 mandate stratified reporting and Amendment A1 supplies a
   composition-matched cross-tier view. The confound is **reduced, never removed**, and must not be
   described as removed.
3. **The 10M tier is thin** — 175 questions from 10 archives, the tier where a scale effect is most
   expected and least robustly measured. Accepted **only** with Amendment A4 in place, so its
   fragility is visible in the report rather than inferred later.
4. **`D_t^norm` is retained at all.** Accepted only in the demoted, disclosed form of A1. It may
   never be promoted to a decision input, a headline, or a cross-tier comparability device without a
   fresh co-chair review.
5. **"Profile of the effect across scale"** (§1 lines 29–30) is loose phrasing for a profile across
   composition-confounded tiers. Accepted because §5 governs the write-up; it may not be cited as
   licence for scale-causal language.
6. **The pooled 1,712-question contrast** is a composition-weighted mixture with no independent
   scientific referent. Accepted **only** in its current explicitly secondary framing (§3.5 lines
   147–148). It must not be promoted to a headline.
7. **W/T/L is retained** rather than replaced. Accepted only with the A5 scoping constraints.

---

## 7. Scope discipline of this review

- The V5/V6 generalized-scanner project was not resurrected and is not referenced as a requirement.
- No accepted runner implementation question was re-opened. §9 lines 240–243 describe an open
  packaging/documentation-consistency question inside the candidate; that is an implementation-audit
  matter, outside co-chair scope, and this review takes no position on it. It is untouched by the
  amendments above.
- No amendment above alters the runner, the cohort, the denominators, the seeds, the negative
  control, the stop rule, or the binding execution conditions of §8.
- No cosmetic or prose-only issue was raised to blocking status.

---

## 8. Persistence record

| Field | Value |
| --- | --- |
| Review branch | `cochair/review-t4f1-prereg-2026-09-03` |
| Branched from | `e12ac9514f0cd1d5823465761893898480dcbf74` |
| Review file path | `docs/v52/task4f1/COCHAIR_SCIENTIFIC_REVIEW_T4F1_PREREG_2026-09-03.md` |
| Preregistration SHA256 (verified) | `ec3443ed4c60eb12e098192abf7b414e034d89fc63a9f42f9d0a02c36a696e45` |
| Cohort CSV SHA256 (verified) | `9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a` |
| Review file SHA256 | recorded in the sidecar `COCHAIR_SCIENTIFIC_REVIEW_T4F1_PREREG_2026-09-03.md.sha256`, since a file cannot contain its own hash |
| Verdict | `REQUEST CHANGES — SCIENTIFIC PREREGISTRATION DESIGN NOT YET ACCEPTED` |
| `main` modified | No |
| Preregistration draft modified | No |
| Frozen candidate / audit / seal / corpus / historical namespace modified | No |
| Task 4F1 preregistered, sealed, authorized, or run | No |
| Retrieval-quality outcome accessed | No |
