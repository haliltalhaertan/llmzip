# V52 — Coordinate-Scale Participation in Cross-Band Mixing Damage: PREREGISTRATION DRAFT

Status: **`[CANDIDATE PREREGISTRATION v3 — COMPLETE, AWAITING AUTHORIZATION. NOT SEALED, NOT TRIGGERED]`**
Revision history: v1 drafted; v2 after a synthetic pilot found the v1 primary estimand confounded;
v3 after pilot 04 resolved the last three open design questions. Every value below is now decided.
Nothing is sealed and nothing is authorized: the remaining steps are a Head Researcher decision, a
pre-run seal, and a trigger. See `drafts/v52/pilot/PILOT_FINDINGS.md` for the evidence behind the
choices.
Date: 2026-09-05
Author: Continuity Lead / co-chair, at Head Researcher direction to continue.
Branch: `draft/v52-coordinate-scale-prereg-2026-09-05` (deliberately **not** the research branch)

No runner exists, no workflow exists, no trigger exists, no seal exists. Every design value is now
**decided and stated**, so this document is complete enough to be sealed as written — but it is not
sealed, and freezing happens only on an explicit Head Researcher authorization, not by this document
existing. Where a choice was resolved by measurement rather than preference, the evidence is cited.

---

## 1. The question

The audited result establishes that **which coordinates are grouped together** matters: a matched
random 32/64 partition, using the identical numeric `Q32`/`Q64`, destroys almost all of the
Native-vs-Full-Haar advantage (`Δ32 ≈ 0.855` LoCoMo, `≈ 0.829` LongMemEval).

It does **not** identify *why*. Membership is the manipulated factor, not an identified mediator.

This experiment tests one specific candidate channel:

> **How much of the damage done by cross-band mixing is attributable to the relative scale of the
> coordinates being mixed?**

## 2. Why the design is possible at all

For any positive diagonal `D`:

```
sign(x D) = sign(x)
```

A positive, archive-derived rescaling therefore leaves the **native sign code exactly unchanged**,
bit for bit, while changing `sign(x D Q)` after an orthogonal mixing `Q`.

This is what makes the intervention clean: any change in rotated retrieval **cannot** be attributed
to a change in the unrotated baseline, because the unrotated baseline is provably identical. The
experiment carries that as an executable identity check, not as an argument (§6, arm `SCALED_NATIVE`).

## 3. Relation to the literature — stated before outcomes, not after

The hashing literature prescribes exactly this operation in the opposite direction: IsoHash argues
for equalising variance across projected dimensions, and ITQ/RaBitQ rotate toward isotropy. Xiao
(arXiv 2605.17524) argues that coordinate heterogeneity `CV(σ)` governs whether rotation helps or
hurts, and that rotation drives `CV²(σ) → 0`.

If that account is right for this pipeline, then removing heterogeneity **before** rotating should
remove most of what rotation had to destroy — so rescaling should help **full** mixing much more
than it helps **within-block** mixing, because within-block mixing was already preserving most of
the between-block heterogeneity.

That is a directional prediction made in advance. It is not assumed, and a null result is
informative (§9).

## 4. Frozen sources — inherited unchanged

Identical to the boundary-localization stage: the same LoCoMo and LongMemEval cohorts, dataset and
adapter digests, archive-local SVD to 96 coordinates, archive-mean centering, `>= 0` sign
quantization, `TOPK = 3`, 20 nuisance trials, the same tie/nuisance scheme and the same deterministic
sharding.

**Do not touch Task 4F1 execution candidates, seals, authorization state or outcomes.**

## 5. The scale rule `D` — the part most likely to be wrong, so it is fixed first

**Resolved** (pilot 04):

- `σ_i` is the standard deviation of coordinate `i` computed **on the exact centered archive
  representation actually used downstream** (`C = Y − mu`), per archive, from **archive content
  only**. It is **not** the raw SVD singular value and must not be assumed equal to it.
- `d_i = 1 / σ_i` when `σ_i >= ε`, and `d_i = 1` otherwise, with `ε = 1e-12`.
  **Why `1/σ` and not the gentler `σ^(-1/2)`:** pilot 04 showed `1/σ` drives `frac` to ≈1.00
  regardless of heterogeneity, so the experiment can actually discriminate; `σ^(-1/2)` yields
  0.46–0.82 drifting with heterogeneity, which would land in a "partial" band by construction and
  answer nothing. The gentler rule is not the more cautious choice, it is the less informative one.
  **Why per-archive and not global:** per-archive matches the archive-local SVD and is tighter; a
  global `σ` overshoots on the block arm (1.096) and flips the sign of `I_frac` between settings.
- The count of coordinates falling back to `d_i = 1` is **recorded per archive** and reported. Pilot
  04 stress-tested 12 of 96 degenerate coordinates and the fallback behaved correctly with the
  identity intact. If any archive has more than `4` of 96 degenerate coordinates, that archive is flagged in the
  output — flagged, not dropped.
- `D` is computed **before** and independently of any query, and **never** from query labels,
  retrieval outcomes, or gold sets. This is a hard constraint, not a preference.

Underflow and overflow: computation in float64; any non-finite value anywhere in `C D` aborts the
run rather than being repaired.

## 6. Arms

All arms are evaluated on the same questions, with the **same rotation matrices** shared between a
scaled arm and its unscaled partner. Pairing is at the level of (question, rotation seed).

| Arm | Transform | Purpose |
|---|---|---|
| `NATIVE` | none | control; must reproduce the frozen anchors |
| `SCALED_NATIVE` | `C D` | **identity check**: must produce a sign code **bit-identical** to `NATIVE`; any deviation aborts the experiment |
| `FULLHAAR_FRESH` | `C Q` | fresh full Haar, fresh seed panel |
| `SCALED_FULLHAAR` | `C D Q` | same `Q` as above |
| `BLOCK32_FRESH` | `C R` | block-diagonal 32/64, `R = diag(Q32, Q64)` |
| `SCALED_BLOCK32` | `C D R` | same `R` as above |

`FULLHAAR_FRESH` is not decoration. It gives the **Full-Haar reference its own seed panel**, which
this research line has never had: every published `rho` divides by an inherited constant whose
sampling uncertainty is quantified nowhere. This experiment closes that gap as a by-product, and the
resulting dispersion must be reported whether or not the primary result is interesting.

## 7. Primary estimand — REVISED after the synthetic pilot

> **Changed 2026-09-05.** The first version made the percentage-point interaction primary. A
> synthetic pilot (`drafts/v52/pilot/`) showed that estimand is confounded by a floor effect: both
> arms recovered about 100% of their own loss, so the pp interaction was driven by full mixing simply
> having more loss available. The revision below is that pilot's consequence.

For each dataset independently, per rotation seed, paired at the question level:

```
frac_full  = ( R@3(SCALED_FULLHAAR) - R@3(FULLHAAR_FRESH) ) / ( R@3(NATIVE) - R@3(FULLHAAR_FRESH) )
frac_block = ( R@3(SCALED_BLOCK32)  - R@3(BLOCK32_FRESH)  ) / ( R@3(NATIVE) - R@3(BLOCK32_FRESH)  )
```

`frac_arm` is the share of that arm's **own** loss that rescaling recovers. It is the primary
quantity, reported **per arm**. Both denominators are measured **inside this experiment** - they are
not inherited - and must be reported with their per-seed dispersion.

**Resolved** bands on the seed-panel mean, applied per arm:

- `frac >= 0.70` -> relative coordinate scale accounts for most of that arm's damage
- `frac <= 0.20` -> it accounts for little of it
- otherwise -> partial

The bands must admit `frac > 1`: the pilot showed rescaling can **overshoot** native at low
heterogeneity, so 1 is not a ceiling and "recovery" is not the right word for such a case.

**Secondary:** the interaction on the fraction scale, `I_frac = frac_full - frac_block`. It is
secondary precisely because the pilot showed it nearly vanishes once the floor effect is removed.

**Descriptive only, barred from carrying any verdict:** the percentage-point quantities
`delta_full`, `delta_block` and their difference.

A reduction in the native-versus-full gap alone remains explicitly insufficient evidence.

## 8. Uncertainty — the lesson from the last stage, applied in advance

- Report the seed-panel mean **and** the per-seed range for every arm and for `I`.
- Report a **question-level paired bootstrap** on `I` — and state in the same breath that it
  resamples questions and does **not** cluster by conversation or archive, so it is a sensitivity
  analysis and not a population interval.
- **Required:** additionally report a **conversation-clustered** bootstrap, since LoCoMo questions are
  nested within conversations. This is the correction the last stage could not make after the fact.
- Report `CV(σ)` before and after rescaling, per archive, as a declared diagnostic. It is a
  descriptive statistic, **not** a decision input.
- No standard error may be presented as total uncertainty while the denominator's own dispersion is
  unreported; with `FULLHAAR_FRESH` that dispersion now exists and must be shown.

## 9. What each outcome would and would not license

**Positive (`I` large).** Supports that relative coordinate scale *participates* in the damage from
cross-band mixing. It would **not** establish exclusive mediation, would **not** identify the
mechanism, would **not** claim improved production retrieval, and would **not** transfer to other
encoders or corpora.

**Null (`I ≈ 0`).** Restricts **this specific intervention**: inverse-σ rescaling of the centered
archive representation. It would not exclude every energy- or scale-based explanation, and in
particular would not exclude correlation structure or subspace alignment as the operative channel.

**Either way**, this is a fixed-benchmark causal-intervention result on two datasets under one shared
pipeline — not an independent methodological replication, not a theorem, not a universal claim, and
nothing to do with Task 4F1.

## 10. Controls, all mandatory — any failure yields `[INVALID / VERDICT WITHHELD]`

1. Source and cohort identity match the frozen anchors.
2. `NATIVE` reproduces the frozen anchors within `1e-12`.
3. `SCALED_NATIVE` is **bit-identical** to `NATIVE` in its sign code. Not "within tolerance" — identical.
4. Every rotation matrix is orthogonal to `1e-12`.
5. The scaled and unscaled partners provably share the **same** `Q` / `R` (max abs difference `0.0`).
6. Norm and dot-product invariance is checked **within each transformed representation and its own
   rotation** — i.e. `‖C D‖` against `‖C D Q‖`. It is **not** expected between `C` and `C D` and must
   not be asserted there.
7. Signed-permutation Hamming invariance passes exactly.
8. Degenerate-coordinate counts recorded per archive.
9. Per-question records persisted for **every** arm and seed, as the boundary stage did, so that all
   aggregates can be rebuilt by an auditor without re-running the pipeline.

## 11. No-tuning rule

After outcome access: no alternate scale rule, no learned `D`, no alternate `ε`, no extra or
replacement seeds, no additional arms, no threshold movement, no boundary variation, no reranking.
A different scale rule is a different, separately preregistered experiment.

## 12. Seeds and stopping rule

**Resolved:** rotation seeds `59001..59010`, used identically for the full-Haar and block arms and
their scaled partners. Ten seeds, once, per dataset. No replacement seeds after outcome access.

**Fresh seeds, not the audited `58001..58010`** (pilot 04, Q3): reusing the audited panel would
invite the objection that a panel already known to show the effect was chosen, and fresh seeds cost
nothing. The boundary stage already showed a fresh panel reproduces the shape.

**Sampling unit:** the question, with conversation-clustered resampling reported alongside.

## 13. The four design questions, and how each was resolved

All four are now settled. Three by measurement, one by argument — and one of them was settled
**against** this document's own earlier preference, which is recorded rather than quietly dropped.

1. **Choice of `D`** — `1/σ`, resolved by pilot 04. Decisive where `σ^(-1/2)` is not.
2. **Scope of `σ`** — per-archive, resolved by pilot 04. Global overshoots and flips `I_frac`.
3. **Block-arm seeds** — fresh `59001..59010`, resolved by argument: reuse invites a
   panel-selection objection and buys almost nothing.
4. **Percentage points or fraction** — the fraction scale, resolved by the earlier pilot **against**
   this draft's original stated preference for percentage points, which were shown to be confounded
   by a floor effect.

What remains genuinely open is **not** a design question: it is where the real archives sit on the
`CV(σ)` axis. That cannot be computed from repository bytes, and it is why `CV(σ)` before and after
rescaling is a mandatory declared diagnostic in §8.

---

## Appendix A — a gap this draft cannot close, reported rather than left implicit

The audit named the inherited Full-Haar denominator's unquantified sampling uncertainty as an open
item. An attempt was made to close it from repository bytes alone. **It cannot be closed that way.**

- The per-seed Full-Haar panel is **not persisted anywhere in the repository**. The T4C3 audit script
  `audit_v52_t4c3/reproduce_raw_table_audit.py` computes `haar96_seed_values`, but its output JSON is
  not committed and the script requires a raw table that is not in git.
- Therefore the denominator's dispersion can only be obtained by re-running, which is a new
  experiment. `FULLHAAR_FRESH` in §6 is the cheapest legitimate route.

One related item **was** closable and is now settled: the frozen LongMemEval denominator is carried
as `0.38271666666667` while the T4C3 script asserts `0.3827166666666667`. The truncation shifts every
published `rho` by between `3e-15` and `2e-14` — immaterial, and now verified rather than assumed.
The LoCoMo denominator `0.13770827054136` has **no higher-precision source committed anywhere**, so
its true precision remains unverified from bytes.

## Appendix B — outcome boundary

This draft performs no run or finalize, constructs no authorization, touches no HMAC material,
performs no BEAM retrieval and accesses no Task 4F1 outcome. Task 4F1 remains
`SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.
