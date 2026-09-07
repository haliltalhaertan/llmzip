# V52 — Acceptance Record: Closure-Audit Result and Erratum

Date: 2026-09-07
Author: Continuity Lead / co-chair (the implementer whose record was audited)
Audit: `audit/v52-acceptance-closure-2026-09-07` @ **`16e95a8035297e18891c4e51f1261bc27d64000b`**
(final commit, including the auditor's own addendum). Report sha256
`669a06c9d8e0efc95fd988252c85ac6c99123cba272040e80fc7716f4c4c25a9` — **verified against its
committed sidecar from the pushed blob**. Branch adds 15 files, all inside the auditor's namespace;
**zero** files touched outside it. Auditor base: `main` `ed2b2f74` (L-060), research `0c9916bd`.

Additive. No bound document is edited. Every correction is stated here and nowhere else, so the
audited bytes stay exactly as the auditor saw them.

---

## 1. Verdict, as delivered

**`CLOSURE PASS WITH CAVEATS`.** Seven of eight gates `ESTABLISHED`; `C6` `NOT ESTABLISHED` on one
clause of four. The auditor states explicitly that **nothing found requires the stage to be
reopened**, and that every finding is presentational or citation hygiene, correctable additively.

What the audit independently confirmed — the reason it was commissioned:

- **C2** — the auditor reached the **same reading of §7 independently**, tested the converse, and
  found the string `seed-mean` occurs **zero** times in the preregistration with no collapse-language
  anywhere. It reports it **could not construct a defensible reading of B**. The A ruling therefore
  stands on the text, not on my argument for it.
- **C4** — A and B were recomputed for all four cells from the persisted per-question rows in
  float64 **and in exact rational arithmetic**, agreeing to ≤ 1.1e-14. The exact-rational pass was
  not required by the brief. It also confirmed that `within 0.001` survives in three places and is
  inside a withdrawal every time.
- **C7** — no seal, preregistration, checkpoint, result package, adapter or historical audit
  namespace touched across `L-056` → `L-060`; and the auditor judges the one in-place state change
  at `cf03007` adequately disclosed in three places, adding that it **should not** have been forced
  to be additive.
- **C8** — `hard_stops` byte-identical L-056 → L-060; no Task 4F1 path, candidate, seal or HMAC
  material anywhere in range.
- 15 negative controls, each shown actually failing.

## 2. Corrections — every finding accepted, none disputed

### E1 (F1) — the §7 block called "verbatim" is not byte-verbatim

Four of seven quoted lines differ from the source: **bold was added** to `per rotation seed` — the
exact phrase the ruling turns on — with no "emphasis added" note; **em dashes were substituted** for
ASCII hyphens; and an elision marker was used (conventional, correctly applied).

Accepted. The correct designation is **"quoted with emphasis added and typographic dashes
substituted"**. The phrase is genuinely present, in that position, governing the formulas, so the
ruling is unaffected — but emphasising the load-bearing phrase and then calling the block verbatim
is a liberty, and it is withdrawn. The two passages that decision §3 puts under a verbatim
requirement were checked and **are** byte-exact.

### E2 (F2) — the outcome-free assertion was scoped too loosely

"no outcome value appears in this section's reasoning" should have read **"§2.1–2.3"**; §2.4 carries
the A/B table inside the same numbered section. The derivation is outcome-free; the sentence was
broader than the bytes support.

### E3 (F3) — "The exact differences" are float64 differences

| cell | printed in the decision (float64) | exact rational difference | gap |
|---|---|---|---:|
| LoCoMo full | `0.0010792266983414844` | `0.001079226698341468…` | 1.60e-17 |
| LoCoMo block | `-0.2062003408892458` | `-0.20620034088926660…` | 2.08e-14 |
| LongMemEval full | `0.0006438693757745` | `0.000643869375775023…` | 5.24e-16 |
| LongMemEval block | `0.0080525777340523` | `0.008052577734044557…` | 7.74e-15 |

The correct label is **"float64 differences"**. Nothing moves at 1e-14, but a correction whose whole
purpose was to withdraw a rounded paraphrase should not itself round while calling the result exact.
The auditor also notes `ops/CURRENT_STATE.json` carried *higher* precision than the document for
three cells.

### E4 (F4) — the inherited-not-recomputed label must travel with §4 and with D7

`[LONGMEMEVAL SINGLE-COMPONENT FINDING — INHERITED FROM TASK 3A.1; PROVENANCE VERIFIED, NOT
RECOMPUTED HERE]` is present in the clarification note and the state file but **absent from the
acceptance decision's §4, where the consequence is drawn, and from register D7**. Accepted: the
label **applies to both**, and must accompany any citation of either.

### E5 (F5) — the label set is reconciled, and the fuller phrasing is preferred

Two label sets are in circulation: the register's `NOT ESTABLISHED` against the decision's and state
file's `NOT ACCEPTED`, and the register lacks the `MOST / PARTIAL` label. Accepted.

The auditor notes an irony worth keeping: the Head Researcher's own required wording is *not
established*, which is the register's. Both labels are therefore correct and they denote the same
status. Rather than declare one canonical and discard the other, the reconciliation is:

> **preferred citation form:** the comparative mechanism claim is **not established on current
> evidence and therefore outside the acceptance scope**. Neither `NOT ESTABLISHED` nor `NOT
> ACCEPTED` asserts falsification or scientific rejection.

The `[MOST / PARTIAL ARE POINT CLASSIFICATIONS ON THE FROZEN PANEL — NOT A POPULATION-LEVEL
DIFFERENCE]` label **applies to the register as well**, which predates it.

### E6 (F6) — the state file's copy of the accepted text is aligned to the decision

The final sentence differed between the two records while the state key asserted textual identity.
The **acceptance decision is the normative object**; `ops/CURRENT_STATE.json` now carries its
sentence, lifted from the committed blob by script rather than retyped. The decision is untouched.

### E7 (F7) — `I` and `I_frac` denote the same quantity

Preregistration §9 writes `I`; §7 defines `I_frac`. They **are** the same quantity — §7 introduces
`I_frac` as "the interaction on the fraction scale" and §9 refers to it as `I` — and the
identification is now stated rather than left silent.

### E9 (new, from the final report) — "no direction test" was marginally overstated

Decision §3 asserts that no band, **threshold or direction test** for `I_frac` appears anywhere. The
auditor confirms this for band and threshold but finds it **marginally overstated on direction**:
§9 does draw a qualitative distinction between `I` large and `I ≈ 0`.

Accepted, and it narrows my own claim rather than the deviation. The accurate statement is: §9
distinguishes *large* from *approximately zero* **qualitatively, with no numeric cut**, so the
licence it attaches remains inoperable. The §7/§9 conflict recorded in decision §3 stands; the
sentence describing it was one word too strong.

## 3. A substantive observation I did not make, and now record

### E8 (F8) — ruling A selects the less stable estimator exactly where instability bites

Definition A averages ten per-seed ratios. On the block arm the record's own D4 reports per-seed
denominators running from −0.0066 to +0.0164 — changing sign inside their own envelope — and
per-seed fractions from −3.40 to +2.64. Averaging ten such ratios is **less numerically stable** than
B's ratio-of-means; the auditor's exact arithmetic confirms it, with block-arm float error ~1e-14
against the full arm's ~1e-16.

The ruling is textual and stands: §7 defines the estimand per seed and applies the bands to the
seed-panel mean, regardless of numerical properties. What the record failed to say is that its own
ruling selects the more fragile estimator precisely where the instability it cites elsewhere is
worst.

The direction matters: this **strengthens** the refusal of the comparative claim rather than
weakening it. The preregistered estimator is the less stable one on the very arm whose denominator
misbehaves, so the case for not carrying a comparative block or interaction conclusion is firmer
than the decision argued.

## 4. The auditor's addendum, and a repair

### E10 — an in-place revision left a recorded hash unresolvable, and that is now fixed

Flagged by the auditor outside its commissioned range, with no verdict taken: **L-061 modified
`V52_NEXT_QUESTION_DESIGN_PROPOSAL_2026-09-07.md` in place**, rewriting a published, sidecar-hashed
document rather than adding a new file beside it, so the hash `c0828c5d…` that **L-060 records in
the canonical ledger no longer resolved to any file on `main`**. The auditor notes this is exactly
the pattern gate C7 exists to police, and that it is the second in-place change in two days.

**Accepted, and the specific defect is repaired.** The v1 bytes are restored on `main` at
`docs/v52/V52_NEXT_QUESTION_DESIGN_PROPOSAL_2026-09-07_v1_SUPERSEDED.md`, whose sha256 is
`c0828c5debf64d6a1d39e67dc6ecb9b57fff6746cb327ad1e794df3db47466bb` — byte-identical to what L-060
recorded, so the ledger's hash resolves on `main` again. v2 stays where it is and is unchanged.

**My reasoning at L-061 was wrong in one respect.** I justified the in-place edit by the
coordinate-scale draft's own v1→v2→v3 history. That precedent does not carry: those revisions
happened on a **draft branch, before publication and before any sidecar hash entered the canonical
ledger**. This document was already published on `main` with a sidecar and a ledger-recorded hash.
Note the contrast the auditor draws — it judged the `cf03007` state-key rename adequately disclosed
and said it *should not* have been forced additive, because `ops/CURRENT_STATE.json` is a live
single-writer state file that is rewritten every entry. A published, sidecar-hashed document is not.

**Forward rule, recorded so the pattern does not settle by default:** on `main`, any document that
carries a `.sha256` sidecar or whose hash has been recorded in the ledger is **additive-only** —
supersede it with a new file and record both hashes. In-place revision remains available for
unpublished drafts on draft branches and for the live state file. Whether the Head Researcher wants
this rule stated more broadly is a governance decision, not mine.

## 5. What is not changed

No bound or frozen artifact is edited: not the acceptance decision, the clarification note, the
preregistration, any seal, the deviation register, any checkpoint or any result package. The audited
bytes remain exactly as the auditor saw them. No verdict is revised: the acceptance decision stands
in full, and the comparative mechanism claim remains **not established on current evidence and
outside the acceptance scope** — not falsified, not rejected.

## 6. Outcome boundary

No corpus read, no experiment or bootstrap re-run, no new authorization. Task 4F1 remains
`SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.
