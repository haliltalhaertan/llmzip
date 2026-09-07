# V52 — Membership Under Scaling: Design Acceptance and Binding Record

Status: **`[DESIGN ACCEPTED — IMPLEMENTATION PREPARATION ONLY; NOT SEALED, NOT AUTHORIZED TO RUN ON REAL DATA]`**

Date: 2026-09-07
Decision owner: Head Researcher (repository owner)
Recorded by: Continuity Lead / co-chair, sole writer on `main`
Provenance: **relayed as chat text, not a pushed Head-Researcher-signed artifact.** This is the
Continuity Lead's record of it, in the same form as the earlier mechanism decisions.

**What was accepted:** the core design of R2 — three absolute percentage-point quantities, paired
uncertainty analysis, unconditional reporting, and no categorical mechanism verdict.

**What was not:** sealing, and execution on real data. Neither is authorized.

---

## 1. Normative source index and precedence

Three documents now describe this design and they stay separate, because corrections here are
additive. **Precedence is R2 → R1 → draft**, latest and narrowest first.

| document | sha256 | status |
|---|---|---|
| `V52_MEMBERSHIP_UNDER_SCALING_PREREG_DRAFT_2026-09-07.md` | `3da80e3424a8f29bcd85ad1c0d5f5b8e97dfba857fbaaf042b2b0d06301e3399` | in force **except** §8 |
| `…DESIGN_REVISION_R1_2026-09-07.md` | `3d7a79b249e97a1bc2657a6782aec5e6a138f6a8c5e2681978ed66ad217b3391` | in force **except** §4 and §5 |
| `…DESIGN_REVISION_R2_2026-09-07.md` | `39cbfcea3a93307d582f9765529d6d99c09d0204706befa6470b8b932f451669` | in force entirely |

**In force, and what governs each subject:**

| subject | governing source |
|---|---|
| question, arms, follow-up framing, controls, no-tuning, outcome licences, seeds | draft §§1–7, 10–13 |
| scaling operator: `ddof = 0`, `ε = 1e-12` as fallback, identical `D` applied to the query, nothing estimated from the query, diagnostics | R1 §1 |
| draw structure: seeds paired one-to-one and not crossed, one `(Q32, Q64)` per seed serving all four rotated arms, matched-`Q` control, countable totals | R1 §2 |
| sign convention and mandatory joint reporting of all three quantities | R1 §3, R2 §2 |
| unconditional publication of every arm, seed, record, aggregate, diagnostic and control | R1 §4 |
| **primary quantities, uncertainty, reporting sentence, prohibitions** | **R2 §§2, 4, 5** |

**Dead and forbidden in the implementation.** None of the following may appear in code, output
schema, configuration or reporting. An implementation that contains any of them does not implement
this design:

- any ratio of `Δ` to `G` — including `ρ`, under any name;
- the cut points `−1.00`, `−0.60`, `−0.20`, `+0.20`;
- the five categorical labels, or any categorical verdict;
- the `2.0` pp floor on `Ḡ`, and the `[RELATIVE SCALE UNSUITABLE]` state;
- the `[INDETERMINATE — INTERVAL SPANS …]` overlay as a verdict mechanism;
- the three-band rule of draft §8;
- any band on `Ḡ_scaled`;
- the per-seed positivity gate on `G_k`.

**The old hash-bound documents are not edited.** This index exists so that an implementer reads the
right rule without needing to reconstruct the history.

## 2. Clarification — how the question-level scheme's limitation is stated

**Withdrawn:** R2 §4's phrasing that the question-level interval "is narrower than the dependence
structure warrants". That asserts a direction the analysis has not established.

**Binding replacement:** *the question-level scheme does not model within-conversation dependence and
may therefore understate uncertainty.* No claim is made about the interval's width, in either
direction, before it is computed.

## 3. Clarification — the panel's point estimate and the resampling envelope are different things

These are separated and must be reported separately:

- **The point estimate on the fixed panel is a computed number and its sign is known.** If `Δ̄` is
  `−5` pp, then on this panel, under this intervention, the gap decreased by 5 pp. That fact does not
  become unknown because an interval is wide.
- **The resampling interval describes variability under the stated resampling scheme.** An interval
  that spans zero means that, under resampling, both directions of change are supported and the
  interpretation is unresolved.

**An interval spanning zero does not make the panel's point estimate unknown, and it is not
evidence of absence of effect or of practical equivalence.** Both statements are reported together
and neither is allowed to erase the other.

## 4. Binding — the exact LoCoMo cluster bootstrap algorithm

Question-weighting is **not** an automatic property of a cluster bootstrap; it follows only from this
procedure, which the implementation must follow literally. Per replicate:

1. draw `n_clusters` conversations **with replacement** from the `n_clusters` available;
2. for each draw, take **all** of that conversation's questions;
3. **preserve multiplicity** — a conversation drawn twice contributes its questions twice;
4. concatenate into the replicate's question multiset;
5. compute each quantity as a mean over that multiset, i.e. **divide by the total number of selected
   question slots**, not by the number of distinct questions and not by the number of clusters;
6. apply the **same** selection to **all six arms** and to the **fixed ten-seed panel**.

If a different algorithm is ever contemplated, it must be declared **before** implementation, not
discovered afterwards in the code.

## 5. Binding — the status of any ratio computed later

If anyone derives a ratio from the three reported numbers at any later time, that derivation is
**not a deliverable of this experiment, not a preregistered result, and not part of its record.** It
may not silently alter the scientific statement this study makes. Changing that statement requires a
new decision taken before the new quantity is looked at.

## 6. Binding — what linearity does and does not require of the implementation

Because `Δ` is linear in the arm means, `mean_k(Δ_k)` and `Ḡ_scaled − Ḡ` are the same quantity, which
is why no aggregation-order ruling is needed here.

**What the implementation must preserve:** the same question scope and the same weights on both
sides of that identity.

**What the implementation must not require:** bitwise equality of the two computations. Floating-point
summation is order-dependent in its last digits. The consistency check is therefore a **tolerance
check at `1e-12`**, and an implementation that asserts exact equality is wrong and would fail for a
reason that has nothing to do with the science.

## 7. What is authorized from here, and what is not

**Authorized:** preparation of runners in a separate implementation namespace, and unit and negative
tests **on synthetic data only**.

The implementation must:

- verify question, arm and seed coverage and their pairing;
- refuse missing, duplicated or invalid records rather than accepting them silently;
- apply the percentage-point unit and the aggregation weights explicitly;
- refuse to overwrite result files silently;
- demonstrate paired resampling and cluster multiplicity in synthetic tests;
- keep real-data execution **off by default**.

**Not authorized at this stage:** reading or downloading any raw corpus; real fitting, retrieval or
ranking; any bootstrap on real data; a pilot; any new model download; sealing; HMAC material;
`run`/`finalize`. Task 4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS
FORBIDDEN`. The independent auditor is **not** to be commissioned yet.

**The author of the implementation may not declare it independently reviewed.** It is handed over as
a package ready for independent implementation review, and that review is a separate commission.
