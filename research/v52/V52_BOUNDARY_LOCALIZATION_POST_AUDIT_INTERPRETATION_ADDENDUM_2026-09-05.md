# V52 Boundary Localization Post-Audit Interpretation Addendum

Date: 2026-09-05
Status: `[BINDING INTERPRETATION NARROWING — POST-LOCALIZATION-AUDIT]`
Research branch: `research/v52-sign-mechanism-locomo-2026-09-04`

## 1. Why this addendum exists

The cold-start independent audit of the boundary-localization stage returned:

`AUDIT PASS WITH CAVEATS`

- Audit branch: `audit/v52-boundary-localization-independent-2026-09-04`
- Audit commit: `27f50f44490b419921b1d634f11006529b290a6f`
- Audited research target: `1a33ef0d1a2715257920201f7a3db8ab4677a007`
- Audit report SHA-256: `80f6a3aa0da5e9e81442c486cb35f11c3bf91a4384840f8cb53ff2d2d90965f3`

Gates A–R passed and passed as *established*. Gate S completed with the adjudication that the case
against the result weakens it without defeating it.

A subsequent peer review of that audit was published at:

- Review branch: `codex/v52-mechanism-next-step-2026-09-05`
- Review commit: `b795aaac980826970dab4b52883bc7931d44f27a`
- Review path: `reviews/v52/mechanism_next_step_2026_09_05/REVIEW.md`
- Disposition: byte receipt and persisted-result reconstruction PASS; acceptance recommended with
  interpretation corrections.

Both were recorded in continuity on `main` at L-043 (`722db79`) and L-044 (`8656aad`).

**This addendum is additive.** It does not rewrite the frozen checkpoint
`CROSS_DATASET_HEAD_TAIL_BOUNDARY_LOCALIZATION_CHECKPOINT_2026-09-04.md`, any summary, any seal, any
manifest or any per-question record. Those bytes stay exactly as executed and audited. What follows
is the narrowing that all subsequent work in this line must inherit.

## 2. Binding narrowing A — the frozen-panel set is a fact; its stability is what is uncertain

`S_LoCoMo = {32}`, `S_LongMemEval = {32, 48}` and `S_common = {32}` are **deterministic descriptive
results**: they are exactly what the preregistered rule returns on the persisted ten-seed panel.
Question resampling does not make a computed result partially true.

Wording that describes `S_common = {32}` as "about a 73% event", or as being some probability of
being correct, is **withdrawn**. The correct formulation is:

> The frozen-panel result is exact. Its **stability under question resampling is limited**: in the
> auditor's empirical bootstrap the same set is recovered in about 73% of resamples
> (`{32,48}` ≈ 17%, empty ≈ 10%), because the uniqueness of 32 within the tested grid rests on a
> single exclusion — LoCoMo 48/48 at `rho = 0.303` — close to the 0.25 threshold.

A bootstrap frequency is **not** a posterior probability of a scientific hypothesis and **not** a
guaranteed replication rate.

## 3. Binding narrowing B — what the bootstraps do and do not certify

Two bootstraps exist. The auditor's reports `P ≈ 0.2103` over 20,000 resamples for the LoCoMo 48/48
reversal; the Continuity Lead's reports `P ≈ 0.166` over 2,000. **They are not claimed to be
numerically equivalent**, and neither has reproduced the other.

Both share the same limitations, which must be stated wherever either is cited:

- questions are resampled independently, with **no clustering by conversation or archive**, although
  LoCoMo questions are nested within conversations and are therefore not independent — so both
  intervals are likely **too narrow**;
- rotation seeds are **not** resampled;
- the inherited Full-Haar denominator's own sampling uncertainty is **not** propagated;
- a frequency of zero among finitely many resamples is not proof of zero probability.

Both are **sensitivity analyses**. They legitimately challenge strong uniqueness language and they
certify nothing about population sampling. A population-level interval would require a declared
sampling target and an appropriate dependence treatment; neither exists in this package.

## 4. Binding narrowing C — bounded integrity language

Git ancestry and the GitHub Actions history establish ordering and observed execution provenance
**within the inspected records**. They cannot establish that no private or local computation ever
existed.

Required phrasing: *"no undisclosed execution was found in the inspected records."*
Withdrawn phrasing: *"no result could have existed before the preregistration bytes did."*

The same bounding applies to superlatives. The position-dependence finding is strong **within the
measured contrast and the inspected design**; words such as "unassailable" or "no sampling argument
touches this" are not to be used.

## 5. Binding narrowing D — membership is the manipulated factor, not an identified mediator

Holding the numeric `Q32`/`Q64` fixed while changing block membership is strong design evidence that
**which coordinates are grouped together** matters. It does not identify the mediating quantity: the
downstream changes to energy mixing, sign dependence and query relevance are not disentangled.

Both datasets run through **one shared representation pipeline**. They are two frozen datasets under
that pipeline, **not independent methodological replications**.

## 6. Binding narrowing E — say "the 32/64 split", never "32 alone"

The `B32` arm uses **all 96 coordinates** under a 32/64 partition. It is not a Head32-only code, and
the leading block alone is in fact weak.

- Required: "the 32/64 split satisfies the sufficiency rule on the frozen panel on both datasets".
- Turkish: *"32/64 bölünmesi, donmuş panelde her iki veri kümesinde de yeterlilik kuralını sağlıyor."*
- Withdrawn: any phrasing of the form "32 alone is sufficient" / *"32 tek başına yeterlidir"*.

This corrects a phrase that appears in the audit report's own Turkish summary (§9). The audit report
is a frozen external artifact and is **not** edited; this addendum supersedes that phrasing for all
subsequent reporting in this line.

## 7. What is unchanged

- The audit verdict remains `AUDIT PASS WITH CAVEATS`; gates A–R remain PASS as established.
- Both mandatory labels remain correct and **must always be reported together**:
  `[PC32-LOCALIZED SUFFICIENCY LEAD — ON TESTED GRID]` and `[BOUNDARY-SET HETEROGENEITY PRESENT]`.
- The **position-dependence** half needs no probabilistic hedge: matched random 32/64 partitions
  using the identical numeric `Q32`/`Q64` destroy almost all of the advantage
  (`Δ32 ≈ 0.855` LoCoMo, `≈ 0.829` LongMemEval; direct contrast `+8.45 pp` and `+13.20 pp`).
- The **localization** half is a lead **conditional on the ten-seed panel and the inherited
  denominator**, not an established property of the grid.
- Sufficiency is not necessity. A tested grid is not a global optimum. Nothing transfers to other
  encoders, corpora, production retrieval, or to Task 4F1.

## 8. Carried-forward open items

1. The inherited **Full-Haar denominator** is a fixed input whose own sampling uncertainty is
   quantified nowhere in this line. It is currently the largest un-costed source of uncertainty.
2. The earlier **matched random-partition null stage** (`410bcf59e29c64096bfb988d6d95e89658f50f6e`)
   carries an audit dispatch record but no auditor branch; its LongMemEval position result has never
   been independently audited. The boundary stage's fresh matched random arms provide current
   evidence without retroactively auditing that stage.
3. The **LoCoMo seed 56001 sign inversion** from the historical Head/Tail panel
   (`rho_2 ≈ -0.067`) remains a binding disclosure and is not erased by the new panel showing no
   inversions.
4. Literature positioning is corrected: binary signature retrieval on these two benchmarks has prior
   art (Hippocampus, MLSys 2026), so no empty-intersection claim may be made. The defensible
   contribution candidate is the controlled comparison of spectral versus matched-random block
   membership under this specific SIGN96 pipeline — and no exact predecessor was identified, which is
   not proof of priority.

## 9. Status of the next question

A next direction has been proposed — testing whether relative coordinate scale contributes to the
damage done by cross-band mixing, using the identity `sign(xD) = sign(x)` for positive diagonal `D`.

It is a **direction only**. It is not preregistered, not sealed, not authorized. No seeds, workflow,
runner or trigger exist for it, and no experiment may begin without a separate Head Researcher
decision and a separate preregistration.

## 10. Outcome boundary

Task 4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`. This addendum
performs no run or finalize, constructs no authorization, touches no HMAC material, performs no BEAM
retrieval and accesses no Task 4F1 outcome.
