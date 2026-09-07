# V52 — Narrow Closure Audit of the Coordinate-Scale Acceptance Record

Issued: 2026-09-07 by the Continuity Lead, at Head Researcher instruction.
Status: **PROMPT PREPARED — commissioning is a Head Researcher decision.**

## Your role and its hard limit

You are a cold-start independent auditor of a **record**, not of an experiment. The session that
wrote the record is the implementer and is explicitly barred from auditing it; that is why you exist.

Accept nothing from chat, commit messages, ledger prose or `ops/CURRENT_STATE.json` as evidence.
Re-derive from bytes. Commit only under
`audit_v52_acceptance_closure_2026_09_07/` on branch `audit/v52-acceptance-closure-2026-09-07`.

**Hash raw Git blobs (`git cat-file -p` / `git show`), never the checked-out working-tree file.**
Two earlier auditor sessions reported hash mismatches that were most likely Windows CRLF checkout
artifacts. Do not repeat that; if you do observe a mismatch, distinguish blob bytes from checkout
bytes before reporting it.

## Scope — narrow, and closed at its edges

**In scope, and nothing else:**

1. the acceptance decision document;
2. the A/B justification and whether it follows from the preregistration text;
3. the §7 / §9 deviation record;
4. the source/hash bindings, including the provenance-versus-recomputation separation;
5. current-state consistency.

**Out of scope — do NOT do any of these, at all:**

- re-running any completed experiment, the bootstrap, or the LoCoMo reproduction;
- reading any benchmark corpus or computing any retrieval outcome;
- recomputing the LongMemEval dependency graph (its status as *inherited, not recomputed* is itself
  one of the things you are checking);
- any Task 4F1 action. Never invoke `--mode run`/`--mode finalize`, never call
  `run_archives`/`evaluate_archive`/`finalize_results`, never set `V52_T4F1_AUTH_HMAC_KEY_HEX`,
  never read a BEAM outcome;
- a broad literature scan;
- reopening the accepted scientific conclusion. You judge the **record**, not the science.

## Objects

| item | anchor |
|---|---|
| canonical branch | `main` at the head that carries ledger entry `L-060` |
| acceptance decision | `docs/v52/V52_COORDINATE_SCALE_ACCEPTANCE_DECISION_2026-09-07.md`, sha256 `8ba55a616c33f23fd3e8cc6daf4565830b7e993f4749e8440c9c62e082d31d3f`, with `.sha256` sidecar |
| clarification note | `docs/v52/V52_ACCEPTANCE_DECISION_CLARIFICATION_2026-09-07.md`, with sidecar |
| deviation register | `research/v52/V52_COORDINATE_SCALE_DEVIATION_REGISTER_2026-09-07.md` @ research `0c9916bd`, sha256 `4f70340774624b0bcdc4e519f6c42f0733b549a2b065a3a4e0b939c5aa5f22dc` |
| preregistration | `research/v52/V52_COORDINATE_SCALE_PARTICIPATION_PREREG_2026-09-05.md`, sha256 `de6672119010bf561179014748e21836bff5c0ebf6efa10379213c59de5203fe` |
| result summaries | `research/v52/{locomo,longmemeval}_scale_outputs/` @ research `0c9916bd` |
| ledger entries under audit | `L-057` … `L-060` on `main` |

## Gates — ESTABLISHED / NOT ESTABLISHED / FAIL, from bytes only

**C1 — Document identity.** Each in-scope document's raw blob hashes to the value its sidecar and
the state file declare. Report any divergence between blob bytes and checkout bytes separately.

**C2 — The A/B ruling follows from the preregistration text.** Read §7 at its own verified hash.
Judge **independently** whether "A is the natural reading" follows from the text alone: the
governing "per rotation seed" clause, the bands applied to "the seed-panel mean", and the required
"per-seed dispersion" of denominators. Then check the converse claim — that §7 nowhere describes
collapsing arms across seeds before forming the ratio. Finally verify that the decision document's
reasoning section contains **no outcome value**, since it was required to be outcome-free. If you
think B is defensible from the text, say so; a contrary reading is a finding, not a failure.

**C3 — The §7/§9 deviation is accurately stated.** Both quoted passages must be verbatim. Verify the
two asserted defects independently: that §7 demotes `I_frac` to secondary while §9 attaches the
positive licence to it; and that **no** threshold, band or direction test for `I_frac` appears
anywhere in the preregistration. Search the whole document, not just §7 and §9. Confirm that the
record selects neither clause.

**C4 — The numerical correction is exact and complete.** Recompute A and B for all four
benchmark/arm combinations from the persisted per-question rows — not from the summaries — and
compare against the decision document's table to full precision. Then confirm that no rounded
restatement of the A/B difference survives anywhere in the in-scope documents.

**C5 — Provenance versus recomputation is honestly separated.** Verify each hash in the LongMemEval
evidence binding, including that the adapter's sha256 equals the `A2_SHA256` pinned by the frozen
base. Then check the harder thing: that **nothing in the record claims the dependency graph was
recomputed in this stage**, and that the clarification note's required citation label is present and
adequate. If the decision's §4 consequence reads as stronger than provenance warrants, say so.

**C6 — Current-state consistency.** `ops/CURRENT_STATE.json`'s `ledger_entry` matches the newest
ledger entry. Both verifiers pass when you run them yourself. No key contradicts the decision — in
particular no surviving "awaiting adjudication" text, and the label set is identical across the
state file, the acceptance decision and the register.

**C7 — Additivity.** Diff `main` across `L-057` … `L-060` and the research branch across the same
period. Confirm that **no frozen artifact was edited** — no seal, no preregistration, no checkpoint,
no result package, no historical audit namespace — and that the register's stale `D1`/`D2` rows were
left in place and superseded in writing rather than silently corrected. One in-place state-file
change was made deliberately (a stale key rename, its own commit, disclosed): judge whether the
disclosure is adequate or whether it should have been additive.

**C8 — Boundary.** Over the whole range, confirm no corpus read, no experiment or bootstrap re-run,
no new authorization created, and no Task 4F1 artifact, candidate, seal, HMAC material or outcome
touched.

## Verdict and deliverables

Verdict vocabulary: `CLOSURE PASS`, `CLOSURE PASS WITH CAVEATS`, `CLOSURE FAIL`, `BLOCKED` (naming
the gate). A caveat is not a blocker; say which of your findings, if any, would require the stage to
be reopened, and which would not.

Deliver in your namespace: `CLOSURE_AUDIT_REPORT.md` with a `.sha256` sidecar, `GATE_TABLE.md`,
`scripts/` (your re-derivation code, with negative controls that show each check can fail),
`evidence/` (JSON), and `HASH_MANIFEST.json` (recursive sha256 of your namespace, excluding itself).
Push the branch. Upload no corpus, no virtual environment, no `__pycache__`.

Do not interpret beyond the record. Do not upgrade any `[LEAD]`. Do not propose new experiments.
