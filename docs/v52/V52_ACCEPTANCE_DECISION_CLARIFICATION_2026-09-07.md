# V52 — Clarification Note to the Coordinate-Scale Acceptance Decision

Date: 2026-09-07
Author: Continuity Lead / co-chair, at Head Researcher instruction
Bound object: `docs/v52/V52_COORDINATE_SCALE_ACCEPTANCE_DECISION_2026-09-07.md`,
sha256 `8ba55a616c33f23fd3e8cc6daf4565830b7e993f4749e8440c9c62e082d31d3f`

Additive. The bound decision document is **not edited**; this note carries the two clarifications
the Head Researcher required. It changes no decision and authorizes nothing.

---

## 1. Wording of the comparative mechanism claim — checked, no change made

The Head Researcher required that the comparative mechanism claim be expressed as **not established
on current evidence and not taken into the acceptance scope**, never as *falsified* or scientifically
*rejected*, and directed that no change be made if the documents already carry that meaning.

A scan was run over the acceptance decision, the deviation register, the result checkpoint and the
ledger entries written in this session (L-057 to L-059), for the terms *falsify*, *refute*,
*disprove*, *reject*, *defeat*, *debunk* and their Turkish equivalents.

Two matches were found and **neither concerns the mechanism claim**:

- deviation register D6, "18 deliberately corrupted samples were rejected" — describes negative
  controls on a record verifier;
- ledger L-057, "altered lock REJECTED" — quotes the output of Codex's evidence-lock verifier.

The mechanism claim itself is stated only as:

- "**Not accepted:** the comparative mechanism claim" (acceptance decision §1);
- "limits any comparative mechanism inference" (accepted conclusion text);
- "`[COMPARATIVE MECHANISM CLAIM NOT ACCEPTED — …]`" (label set);
- "**NOT ESTABLISHED**" (ledger L-057);

together with the explicit non-implication recorded at the Head Researcher's instruction: *this
decision does not mean "there is no mechanism."*

**Conclusion: the constraint is already satisfied in the bound bytes. No document is changed.** This
section is the record that the check was performed, so that a successor does not have to redo it or
assume it.

## 2. Source verification and computational verification are different things

The Head Researcher required that the evidence binding for the LongMemEval single-component finding
must **not** be equated with recomputing the dependency graph in this stage, and that the two be
written separately. They are separated here.

### 2.1 What was verified in this stage — provenance only

All of the following were performed and are true:

| check | result |
|---|---|
| `docs/v52/task3/V52_T3A1_PROTOCOL_PATCH.md` exists at `main` `e97fbe05` | git blob `36505bcffd7d1ce983a71c5ec4d000a2c94ae1ac`, sha256 `930db8e923652319f169ba0701febdc07a8cebc49b21c978960384682b37bef1`, 744 bytes |
| it contains the decisive sentence | "Dependency graph: 1 component(s), largest=470/470. question-level bootstrap cannot be interpreted as independent underlying-memory population inference." |
| `adapters/longmemeval_v52_adapter_v2.py` exists at the same commit | git blob `aa0b6f956a9bbc7f27778760c2c6fc708ae72ba1`, sha256 `643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218` |
| that adapter states the same finding | yes |
| the frozen LongMemEval base pins that adapter | `A2_SHA256` in `research/v52/longmemeval_spectral_band_haar_causal.py` (blob `79dd4a5e`) equals the adapter's sha256 — **verified** |

What this establishes, exactly: **the recorded finding is authentic, is located in the repository at
known bytes, and sits inside the adapter the pipeline actually executes rather than in a stale or
orphaned note.** That is a provenance result about *where the claim lives and which artifact carries
it*.

### 2.2 What was NOT done in this stage

The dependency graph over the 470 primary LongMemEval questions was **not recomputed**. Nothing in
this stage:

- read the LongMemEval corpus;
- rebuilt the `haystack_session_ids` sharing graph;
- recounted its connected components;
- re-derived the "1 component, largest = 470/470" figures.

Those figures are **inherited from the Task 3A.1 stage that produced them**. They have the standing
that stage gave them, no more. Confirming that a file contains a number is not confirming the
number.

### 2.3 Consequence for how the decision may be cited

The §4 consequence of the acceptance decision — that the standard component-cluster bootstrap for
LongMemEval leaves the outstanding-work list as ill-posed — rests on an **inherited, provenance-
verified** finding, not on a computation performed or re-checked in this stage. Any citation must
carry:

> `[LONGMEMEVAL SINGLE-COMPONENT FINDING — INHERITED FROM TASK 3A.1; PROVENANCE VERIFIED, NOT RECOMPUTED HERE]`

If a future decision needs the finding to be load-bearing at a higher standard than provenance, an
independent recomputation of the component structure from the frozen corpus is the way to get it.
That recomputation is **not proposed and not authorized here**; it would be a separate, corpus-
reading task requiring its own decision.

## 3. Outcome boundary

No corpus was read, no experiment run, no bootstrap or reproduction repeated in producing this note.
No Task 4F1 artifact, candidate, seal, authorization or HMAC material was touched. Task 4F1 remains
`SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.
