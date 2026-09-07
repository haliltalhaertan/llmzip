# V52 — Coordinate-Scale Stage: Head Researcher Acceptance Decision

Date: 2026-09-07
Decision owner: Head Researcher (repository owner)
Recorded by: Continuity Lead / co-chair, sole writer on `main`
Provenance: **relayed as chat text, not a pushed Head-Researcher-signed artifact.** This document is
the Continuity Lead's record of that decision, in the same form as the 2026-09-03 and 2026-09-04
mechanism decisions. If the Head Researcher wants a signed artifact, it must be pushed separately on
an `hr/…` branch; this record does not substitute for one.

Nothing frozen is edited by this decision. It adjudicates items D1 and D2 of the deviation register
and binds the evidence for D7. It authorizes no experiment.

---

## 1. Decision — the narrow conclusion is ACCEPTED, within stated limits

**Accepted:**

- For LoCoMo, the **computational reproduction of the same implementation** succeeded.
- The **scale-equalisation improvement on the frozen panel is preserved as a descriptive finding.**

**Not accepted:**

- The **comparative mechanism claim**.
- Any **population-level inference** drawn from the `MOST` / `PARTIAL` band labels.

**Explicit non-implication, recorded at the Head Researcher's instruction:**

> This decision does **not** mean "there is no mechanism."

The accepted text is therefore:

> On a fixed pipeline, positive coordinate rescaling preserves the native sign representation
> exactly while raising retrieval score after full orthogonal mixing. The LoCoMo computation
> reproduced numerically from verified raw data across 92,100 question/seed/arm records. Denominator
> instability in the block-normalised comparisons, together with preregistration aggregation and
> interpretation inconsistencies, limits any comparative mechanism inference. Post-hoc sensitivity
> analyses do not repair that limit; they make it visible. This is not a general mechanism result,
> not a production claim, and does not generalise to other encoders or corpora.

Citations of this stage must carry the four labels listed in §7 below.

---

## 2. Decision — A versus B, ruled from the preregistration text

The Head Researcher directed that this be justified by the **original preregistration text**, not by
which value either definition produces. That instruction is followed here: no outcome value appears
in this section's reasoning.

### 2.1 What §7 says

Preregistration §7 (`V52_COORDINATE_SCALE_PARTICIPATION_PREREG_2026-09-05.md`, sha256
`de6672119010bf561179014748e21836bff5c0ebf6efa10379213c59de5203fe`), verbatim:

> For each dataset independently, **per rotation seed**, paired at the question level:
>
> ```
> frac_full  = ( R@3(SCALED_FULLHAAR) - R@3(FULLHAAR_FRESH) ) / ( R@3(NATIVE) - R@3(FULLHAAR_FRESH) )
> frac_block = ( R@3(SCALED_BLOCK32)  - R@3(BLOCK32_FRESH)  ) / ( R@3(NATIVE) - R@3(BLOCK32_FRESH)  )
> ```
>
> `frac_arm` is the share of that arm's **own** loss that rescaling recovers. It is the primary
> quantity, reported **per arm**. Both denominators are measured **inside this experiment** — they
> are not inherited — and must be reported with their per-seed dispersion.
>
> **Resolved** bands on the seed-panel mean, applied per arm: …

### 2.2 The derivation

Three textual facts settle it:

1. The quantity `frac_arm` is **defined per rotation seed**. The governing clause is "per rotation
   seed", and the formulas sit under it.
2. The decision bands are applied to "**the seed-panel mean**" — that is, the mean over the seed
   panel of the quantity just defined, which is `frac_arm` itself.
3. The denominators "must be reported with their **per-seed dispersion**", which presupposes that a
   denominator exists per seed and is not first collapsed across seeds.

Composing 1 and 2 gives: compute `frac_arm` for each seed, then take the mean over seeds. That is
definition **A** (the mean of the per-seed ratios).

Definition **B** (the ratio of the seed-mean gain to the seed-mean loss) requires averaging each arm
across seeds *before* forming the ratio. §7 nowhere describes that operation, and it is inconsistent
with the "per rotation seed" clause that governs the formulas.

### 2.3 Ruling

- **A is the natural reading of the preregistration and is ruled the preregistered estimand.**
- **B is preserved as the historical implementation output.** The sealed runner emitted B as its
  headline; that fact is part of the record and is not erased. B is labelled a historical
  implementation result, not the preregistered statistic.
- **Both are published, always together.** No file needs to change for this: the runner already
  persists `frac_*_per_seed` beside the seed-mean ratio, so A and B are both recoverable from the
  existing bytes at research commit `0c9916bd`.
- **No frozen file is edited.** The preregistration, the seals, the checkpoint and the result
  packages stay byte-unchanged. This document is the additive correction.

### 2.4 Correction demanded by the Head Researcher, applied

An earlier Continuity Lead statement said the A/B difference on the full arm is "within 0.001". That
rounded phrasing is **withdrawn**. The exact differences, recomputed from the persisted summaries at
`0c9916bd`:

| benchmark | arm | A | B | A − B |
|---|---|---:|---:|---:|
| LoCoMo | full | 0.7271861342884777 | 0.7261069075901362 | **+0.0010792266983414844** |
| LoCoMo | block | 0.4454425786787960 | 0.6516429195680419 | **−0.2062003408892458** |
| LongMemEval | full | 0.6569781664714960 | 0.6563342970957214 | **+0.0006438693757745** |
| LongMemEval | block | 0.3165111621882831 | 0.3084585844542308 | **+0.0080525777340523** |

The correct statement is: the LoCoMo full-arm difference is approximately **0.001079**, and the
divergence **grows chiefly in the block arm** (−0.206 on LoCoMo). Any restatement must use these
figures rather than a rounded paraphrase.

Note on scope: this table is a presentational correction, not a re-derivation of the accepted
conclusion, and it does not reopen §1.

---

## 3. Deviation record — preregistration §7 and §9 are inconsistent

Recorded as an **explicit deviation**, per the Head Researcher's instruction, and **not resolved**.
The frozen preregistration is not edited.

§7 makes the per-arm fraction the primary quantity and demotes the interaction:

> **Secondary:** the interaction on the fraction scale, `I_frac = frac_full - frac_block`. It is
> secondary precisely because the pilot showed it nearly vanishes once the floor effect is removed.

§9 nevertheless attaches the positive interpretation licence to that same secondary quantity:

> **Positive (`I` large).** Supports that relative coordinate scale *participates* in the damage from
> cross-band mixing.

Two defects follow:

1. **A demoted statistic carries the licence.** §7 says the interaction is secondary; §9 makes it the
   thing that licenses the positive reading. A result can satisfy §7's primary bands and fail §9's
   clause, or the reverse.
2. **"large" is never defined.** §7 supplies numeric bands for `frac_arm` (0.70 / 0.20) but the
   document supplies **no** band, threshold or direction test for `I_frac` anywhere. §9's condition
   is therefore not operational.

This conflict existed in the sealed text before any outcome was seen. It is recorded here so that it
cannot later be closed by selecting whichever clause favours an observed result. **No clause is
selected by this decision.**

---

## 4. Decision — the LongMemEval single-component finding, evidence bound

The Head Researcher required the source commit, path and hash evidence to be bound into the decision
record before the consequence is drawn. Bound here:

| item | value |
|---|---|
| evidence A — path | `docs/v52/task3/V52_T3A1_PROTOCOL_PATCH.md` |
| evidence A — commit | `e97fbe052306e9042e994d2e83031c6e8edd6b3d` (`main`, L-058) |
| evidence A — git blob | `36505bcffd7d1ce983a71c5ec4d000a2c94ae1ac` |
| evidence A — sha256 | `930db8e923652319f169ba0701febdc07a8cebc49b21c978960384682b37bef1` |
| evidence A — size | 744 bytes |
| evidence B — path | `adapters/longmemeval_v52_adapter_v2.py` |
| evidence B — commit | `e97fbe052306e9042e994d2e83031c6e8edd6b3d` |
| evidence B — git blob | `aa0b6f956a9bbc7f27778760c2c6fc708ae72ba1` |
| evidence B — sha256 | `643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218` |
| pin that makes evidence B load-bearing | `A2_SHA256` in `research/v52/longmemeval_spectral_band_haar_causal.py` (blob `79dd4a5ec462102da5d82530088a4b7e89bef437`, research commit `0c9916bd`) equals evidence B's sha256 — **verified** |

Decisive line, quoted verbatim from evidence A:

> Dependency graph: 1 component(s), largest=470/470. question-level bootstrap cannot be interpreted
> as independent underlying-memory population inference.

The identical finding is stated inside evidence B, which the pin proves is the adapter the pipeline
actually executes rather than a stale note.

**Consequence, decided:**

1. The **standard component-cluster bootstrap for LongMemEval is removed from the outstanding-work
   list.** With a single connected component it is ill-posed, not merely undone: cluster resampling
   either returns the identical dataset in every replicate, carrying no information, or requires an
   arbitrary partition that violates the independence assumption the scheme exists to respect.
2. An **alternative dependency-aware inference design** for a single connected component is kept as
   **separate and not yet authorized work**. It is a design question, not a re-run, and nothing here
   authorizes it.
3. The LongMemEval **question-level** bootstrap that was run inherits evidence A's warning verbatim:
   it is a sensitivity analysis and never a population inference.
4. The asymmetry with LoCoMo is explained rather than anomalous: LoCoMo's ten clusters were recovered
   from producer archive-ordinal metadata, and ten is not one.

---

## 5. Standing prohibitions reaffirmed by this decision

- Do **not** restart the stopped coordinate-scale audit or literature-scan agents.
- Do **not** issue any new Task 4F1 execution authorization. Task 4F1 remains
  `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.
- Do **not** re-run completed experiments or the bootstrap.
- Do **not** edit frozen files; corrections stay additive.

---

## 6. What remains open after this decision

- **Re-commissioning** of the coordinate-scale independent audit and the literature scan, and by
  whom. The Continuity Lead session is not independent of the stage and cannot supply that audit.
- **Task 4F1 execution track** (V8 package audit, exact-rational `D_t` analysis) — no decision taken.
- **Drive backup (D11)** — never performed for this stage or for the five Codex packages; needs an
  operator with Drive access. Do not describe it as done.
- **GitHub default branch** still resolves away from canonical `main` — owner-only setting.
- **Alternative single-component inference design** — unauthorized, per §4.2.
- Deviation-register items **D3–D6 and D8–D10** stay as recorded; none is adjudicated here.

The register's `D1` and `D2` rows still read "OPEN — needs adjudication". They are **superseded by
§2 and §3 of this document** and are deliberately left unedited, because corrections in this program
are additive rather than in-place. This document is that correction.

---

## 7. Labels that must travel with any citation of this stage

> `[LOCOMO COMPUTATIONAL REPRODUCTION PASS — SAME METHOD, NOT INDEPENDENT REPLICATION]`
> `[COMPARATIVE MECHANISM CLAIM NOT ACCEPTED — DENOMINATOR INSTABILITY AND PREREGISTRATION DEVIATIONS]`
> `[UNCERTAINTY ANALYSIS IS POST-OUTCOME]`
> `[NOT INDEPENDENTLY AUDITED AS A WHOLE STAGE]`

And, when the band labels appear at all:

> `[MOST / PARTIAL ARE POINT CLASSIFICATIONS ON THE FROZEN PANEL — NOT A POPULATION-LEVEL DIFFERENCE]`

## 8. Outcome boundary

LoCoMo/LongMemEval mechanism track only. No corpus was read and no experiment run in producing this
decision record. No Task 4F1 artifact, candidate, seal, authorization or HMAC material was touched.
