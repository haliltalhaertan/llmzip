# V52 Acceptance-Closure Narrow Audit — Gate Table

Auditor: cold-start independent session. Branch `audit/v52-acceptance-closure-2026-09-07`.
Canonical anchor: `main` @ `ed2b2f74347da6be68beae2c22d5c3d22992f1a3` (L-060);
research @ `0c9916bd7786d7ddb332f5b6da3d96d61a6223f0`.
Controlling prompt blob sha256 `c6a0da6a3076793b5b3cc0b0d0796b3fe30a1a21644e539c3b4f9a0bd1649faf` — **matches**.

| gate | subject | verdict | one-line basis |
|---|---|---|---|
| C1 | Document identity | **ESTABLISHED** | All six in-scope blobs hash to their sidecars and to every value the state file and prompt declare; blob-vs-checkout divergence isolated and explained. |
| C2 | A/B ruling follows from prereg §7 | **ESTABLISHED** | Independently reached the same reading: A. Converse claim holds — `seed-mean` occurs 0 times in the preregistration and no collapse-language exists anywhere. Two presentational caveats. |
| C3 | §7/§9 deviation accurately stated | **ESTABLISHED** | Both named passages byte-verbatim; both defects independently confirmed; no `I_frac` band, threshold or numeric cut anywhere; neither clause selected. |
| C4 | Numerical correction exact and complete | **ESTABLISHED** | A and B recomputed for all four cells from the persisted per-question rows in float64 **and** in exact rational arithmetic; all eight values agree to ≤1.1e-14. No rounded restatement survives. One caveat on the word "exact". |
| C5 | Provenance vs recomputation honestly separated | **ESTABLISHED** | Every binding re-derived from blobs including the `A2_SHA256` pin; every recomputation-word hit in the record sits inside a negative statement; required citation label present. One placement caveat. |
| C6 | Current-state consistency | **NOT ESTABLISHED** (one clause) | `ledger_entry` = newest = L-060 ✔; both verifiers PASS ✔; zero surviving "awaiting adjudication" ✔; **label set is NOT identical** — the register says `NOT ESTABLISHED` where the decision and state file say `NOT ACCEPTED`, and the register lacks the `MOST / PARTIAL` label. |
| C7 | Additivity | **ESTABLISHED** | 10 pure additions plus ledger/state on `main`, 2 pure additions on research; no seal, preregistration, checkpoint, result package, adapter or historical audit namespace touched; D1/D2 left stale and superseded in writing; the one in-place state change is adequately disclosed. |
| C8 | Boundary | **ESTABLISHED** | No Task 4F1 path, candidate, seal, HMAC material, corpus path or result package in the whole range; `hard_stops` byte-identical L-056 → L-060; no prohibited action performed by this audit. |

## Verdict

**CLOSURE PASS WITH CAVEATS.**

**Nothing found requires the stage to be reopened.** All findings are
presentational or citation-hygiene defects in the record, correctable additively.

## Findings, by whether they would reopen the stage

| # | finding | gate | reopen? |
|---|---|---|---|
| F1 | The §7 block quoted as "verbatim" in decision §2.1 is not byte-verbatim: bold added to `per rotation seed`, em dashes substituted for the source's ASCII hyphens. | C2 | No — additive erratum. |
| F2 | "no outcome value appears in this section's reasoning" is true of §2.1–2.3 but §2.4 sits inside the same numbered section and carries the full A/B table. | C2 | No — wording. |
| F3 | The A−B column is called "The exact differences"; three of four cells are truncated renderings of a float subtraction and none equals the exact difference (max gap 2.08e-14). | C4 | No — immaterial at 1e-14. |
| F4 | `[LONGMEMEVAL SINGLE-COMPONENT FINDING — INHERITED … NOT RECOMPUTED HERE]` is carried by the clarification note and the state file, but **not** by the acceptance decision whose §4 draws the consequence, nor by the register. | C5 | No — but attach it at §4. |
| F5 | Citation label set diverges: register `NOT ESTABLISHED` vs decision/state `NOT ACCEPTED`; register lacks the `MOST / PARTIAL` label. | C6 | No — additive reconciliation note. |
| F6 | The accepted-conclusion text's final sentence differs between the decision and the state file, while the state key asserts "the text itself is unchanged from the version that was proposed". | C6 | No — align the state file to the decision. |
| F7 | §9 writes `I`, never `I_frac`; the record identifies them without saying so. The identification is supportable but unstated. | C3 | No. |
| F8 | The record does not note that ruling **A** primary selects the *less* numerically stable estimator on the block arm, whose per-seed denominators change sign. | C2/C4 | No — the ruling is textual and correct; this is a missing consequence, not an error. |
| I1 | Infrastructure: the repository ships no `.gitattributes`, so on any default Windows clone (`core.autocrlf=true`) **both** shipped verifiers report mass SHA256 mismatches. Proven to be a checkout artifact. | C1/C6 | No — but fix it, or every future Windows auditor repeats it. |
