# V52 — Head Researcher Decision: Integration Obligations 2 and 3

**Date:** 2026-09-09
**Authority:** Head Researcher (repository owner)
**Prepared by:** Continuity Lead (prepares only; does not seal, does not self-approve)
**Status:** DRAFT — becomes binding only when committed with an agreeing `.sha256`
sidecar on an `hr/` branch and pushed. Chat text is not a pushed artifact.
**Intended repository path:** `docs/v52/V52_INTEGRATION_OBLIGATIONS_2_AND_3_HR_DECISION_2026-09-09.md`

---

## Scope

This decision disposes of **two** of the five integration obligations named in
`ops/CURRENT_STATE.json → task_state.next_single_action` and in the L-081 ledger
entry:

- **Obligation 2** — the LoCoMo gold reconciliation → **Decision 1**
- **Obligation 3** — the LongMemEval ordinal and shard convention → **Decision 2**

It additionally takes two consequential decisions that follow from those two but
are recorded separately so that each may be audited on its own terms:

- **Decision 3** — the conformance status of the accepted v5 ingestion
- **Decision 4** — withdrawal of the `SHARDED_EXACT` label

**Binding scope of Decisions 1 and 3:** the membership-under-scaling track and all
subsequent LoCoMo runs in this programme.
**Binding scope of Decisions 2 and 4:** the membership-under-scaling track and all
subsequent LongMemEval runs in this programme.

These are taken because obligations 2 and 3 are **scientific convention choices**,
not implementation defects. Both candidate behaviours are internally correct; they
disagree about what the ground truth and the enumeration are. No implementation and
no audit may take such a decision.

---

## DECISION 1 — LoCoMo gold evidence: the corrected key is authoritative

For the membership-under-scaling track and all subsequent LoCoMo runs, gold
evidence is derived by applying the **156 audit corrections** in
`audit/errors_conv_*.json`, under the three-step rule established in L-075:

1. Retain questions in categories `{1, 2, 3, 4}` → 1540 questions.
2. Load the 156 correction records; a record's `correct_evidence` **replaces** the
   question's raw evidence.
3. Resolve the evidence against the conversation's archive rows and **drop** the
   question when the resulting gold set is empty (`if not gold: continue`).
   1540 − 5 = **1535**.

**The binding LoCoMo cohort is 1535 questions.**

### Mandatory dual reporting

Both readings are reported **together, always**. Every LoCoMo result produced under
this decision reports the corrected-key figure and the raw-evidence figure side by
side, each with its cohort size stated (**1535** and **1540** respectively).

- Neither figure may be reported alone, in any document, table or summary.
- The **corrected-key** figure is primary and carries the claim.
- The **raw-evidence** figure is descriptive and carries no claim.
- The **divergence between them is itself a reportable quantity** and is stated
  wherever both appear.

This rule exists so that the choice made here remains visible and reversible to any
later reader, rather than becoming an invisible assumption.

### Rationale

- The corrections are the benchmark's own errata; `correct_evidence` is an explicit
  statement that the raw field is wrong.
- **Continuity is decisive.** Every frozen LoCoMo mechanism-stage result in this
  programme — Native SIGN96 `23.654715%`, Haar96 mean `13.770827%`,
  Δ `−9.884 pp` — was produced under this exact rule. A raw-evidence primary would
  produce numbers not comparable to the programme's own frozen baseline.
- The residual is understood, not hand-waved: `locomo_6_qa11` carries a
  `TEMPORAL_ERROR` correction whose `correct_evidence` field is **present but
  empty**, so step 3 drops it. Its raw evidence resolves without error, which is
  precisely why a two-step reconstruction could not see the discrepancy.

### Verification pointers

- `docs/CONTINUITY_LEDGER.md:1576` — the three-step rule, transcribed read-only
  from `research/v52/locomo_sign_mechanism_replication.py` at
  `692f599eedeb7e7a649443f24ff507e8c4d1c17d`.
- `docs/CONTINUITY_LEDGER.md:1577` — the `locomo_6_qa11` residual; end-to-end
  read-only check reproduces the bound cohort exactly: 1535 predicted, 1535 bound,
  zero on either side; corrections file loaded 156 records, matching the frozen
  constant.
- `docs/CONTINUITY_LEDGER.md:1739` — statement of the obligation.
- `docs/CONTINUITY_LEDGER.md:1517` — cohort identity: 1535 questions, 10
  conversations, per-conversation counts 150, 81, 152, 199, 178, 123, 149, 191,
  156, 156; corpus `locomo10.json` pinned at 2,805,274 bytes,
  sha256 `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4`.

---

## DECISION 2 — LongMemEval enumeration: the historical convention is bound

For the membership-under-scaling track and all subsequent LongMemEval runs, the
archive ordinal and shard convention are **bound to the historical convention**,
unchanged:

- **Archive ordinal:** `enumerate(cohort_ids)` over the sorted primary cohort.
- **Nuisance priorities:** keyed on the **global** lexical ordinal (not on a
  shard-local index).
- **Shard membership:** `i % num_shards` over the sorted primary cohort.

This convention **must be stated explicitly in any preregistration seal text** that
governs a run under it, not inherited implicitly from the implementation or from a
README.

### Rationale

- The ordinal is **load-bearing, not cosmetic**: it feeds the deterministic seed
  schedule, which determines the random projections and the tie-break priorities.
  The auditor demonstrated that permuting cohort order changed **2 of 120 scores**.
- Because it is outcome-affecting, it must be fixed **in writing before any run**.
  Leaving it unbound would admit the possibility — even unintentionally — of an
  enumeration chosen after outcomes were visible.
- Any alternative enumeration would break continuity with every frozen LongMemEval
  number in the programme while purchasing no scientific gain.

### Verification pointers

- `docs/CONTINUITY_LEDGER.md:1738` — the ordinal is decided as
  `enumerate(cohort_ids)`; the auditor DEMONSTRATED it is outcome-affecting
  (2 of 120 scores); disclosed in the README, therefore not silently decided, but
  load-bearing rather than a placeholder.
- `docs/CONTINUITY_LEDGER.md:1063` — shard membership `i % num_shards` over the
  sorted primary cohort; nuisance priorities keyed on the global lexical ordinal.
- `docs/CONTINUITY_LEDGER.md:823` — per-question persistence: LongMemEval 28,200
  rows across 470 unique questions and ten shards.

---

## DECISION 3 — Conformance status of the accepted v5 ingestion

The accepted v5 ingestion reads **raw** evidence and loads no corrections. Under
Decision 1 that behaviour is **non-conforming as a primary source** for the
membership-under-scaling track and for subsequent LoCoMo runs.

- The reconciliation must be completed before any run authorization on that track.
- This decision **does not itself modify** any accepted artifact, any sealed byte,
  or any frozen result. It states the target the reconciliation must meet.
- Codex's posture — flagging the difference as a source-level discrepancy requiring
  reconciliation by the authority, loading no corrections and changing no accepted
  gold — is recorded as **correct**. This decision supplies the authority ruling
  that posture was waiting on.
- Under the dual-reporting rule in Decision 1, the raw reading retains a defined
  descriptive role; it is not discarded.

### Verification pointer

- `docs/CONTINUITY_LEDGER.md:1739` — "the historical LoCoMo producer applies 156
  audit corrections … while the accepted v5 ingestion reads RAW evidence."

---

## DECISION 4 — The `SHARDED_EXACT` label is withdrawn

The label `SHARDED_EXACT` asserts more than has been shown. It is replaced
everywhere it appears by the claim that is true as stated:

> Shard-invariant **semantics** are demonstrable, and the aggregate reproduces to
> approximately `1e-16`. Bit-level exactness is **not** claimed.

This discharges the fourth binding caveat recorded as owed by the research track at
`docs/CONTINUITY_LEDGER.md:778`.

This decision is recorded separately from Decision 2 because it is a
**labelling-accuracy** correction owed independently of the enumeration choice, and
should be auditable without reopening that choice.

---

## What this decision explicitly does NOT do

- It does **not** authorize any execution, seal, pilot or run on any track.
- It does **not** grant retrieval-quality outcome access, and does not set or
  request `V52_T4F1_AUTH_HMAC_KEY_HEX`.
- It does **not** dispose of integration obligations 1, 4 and 5, of the seven
  findings, or of the nine named test gaps on the execution-preparation package.
  Those remain open and await separate Head Researcher disposition.
- It does **not** modify any sealed byte, any accepted audit, or any frozen result.

Task 4F1 remains **SEALED / RUN BLOCKED / OUTCOME ACCESS FORBIDDEN**. This sentence
is retained deliberately: the decisions above are scoped away from Task 4F1, and
this line records that scoping away does not relax any Task 4F1 prohibition.

---

## Recording

On approval:

1. Branch `hr/integration-obligations-2026-09-09`, created **from `origin/main`**
   (`a8e6d5d`, L-081) — not from the current `audit/…` HEAD.
2. Commit this file plus an agreeing `.sha256` sidecar. Additions only; no
   candidate, seal, manifest, draft or accepted byte touched.
3. Push.
4. Separately on `main`: update `ops/CURRENT_STATE.json` and append ledger entry
   **L-082** recording that obligations 2 and 3 are disposed and that Decisions 3
   and 4 are taken, with this file's commit and sha256 as the binding reference.

---

*Prepared by the Continuity Lead. Not binding until pushed as a hash-bound artifact
on an `hr/` branch.*
