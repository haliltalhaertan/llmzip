# V52 — Head Researcher Decision: Obligation 1, the F3/N1 closure criterion, and a stale-record correction

**Date:** 2026-09-09
**Authority:** Head Researcher (repository owner)
**Prepared by:** Continuity Lead (prepares only; does not seal, does not self-approve)
**Binding when** committed with an agreeing `.sha256` sidecar on an `hr/` branch and
pushed — see the commit and sidecar for status.
**Repository path:** `docs/v52/V52_OBLIGATION_1_AND_F3_N1_DECISION_2026-09-09.md`
**Follows:** `f9951c0` (obligations 2 and 3 disposed), ledger L-082.

---

## Scope

Three items, none of which any implementation or audit may settle:

- **Decision 1** — integration obligation 1: native-anchor provenance and granularity.
- **Decision 2** — the closure criterion for finding F3 together with the takeover
  review's finding N1.
- **Decision 3** — an additive correction of a stale record in the membership
  completion map.

Obligations 4 and 5 are **not** disposed here, and the README text is the reason:

- Obligation 4 — *"Existing runner's accepted bootstrap/output path must eventually
  consume these records with complete provenance and overwrite protection. This
  package does not implement that finalizer."* This is implementation work; it
  requires a code authorization, not a decision.
- Obligation 5 — *"Full mandatory negative-control coverage,
  real-ingestion-to-computation integration review, full accepted-lock regression,
  independent acceptance, and pre-run seal remain open."* This is not a decision at
  all; it is the description of the remaining gate chain and is discharged by
  executing it.

Source: `origin/codex/v52-membership-execution-prep-2026-09-08` (`ed4e22c`),
`drafts/v52/membership_execution_prep_v1_2026_09_08/README.md`, section
*"Remaining integration obligations — do not silently decide"*, items 1–5.

---

## DECISION 1 — Native-anchor provenance and granularity

### 1a. Granularity — RATIFIED as implemented

Native anchors are **one float per question**, keyed by question id, with **total
coverage of the cohort**.

This ratifies what the code already does and discloses; it is recorded here because
the obligation requires granularity to be *bound*, not merely disclosed. The
coverage requirement already enforced at
`pipeline.py: require(set(native_anchors) == set(ids), 'E-M-027: anchor coverage')`
is adopted as the binding rule rather than left as an implementation detail.

### 1b. Provenance — BOUND

The native-anchor source is the **`NATIVE` arm per-question values of the
coordinate-scale stage**, the most recent independently audited stage that persists
per-question records for both benchmarks. Both artifacts are already committed and
already hash-recorded.

**Branch:** `research/v52-sign-mechanism-locomo-2026-09-04`
**Head:** `0c9916bd7786d7ddb332f5b6da3d96d61a6223f0`
**Column:** `native_fractional_R3`, keyed on `question_id`

| benchmark | path | git blob | sha256 |
|---|---|---|---|
| LoCoMo | `research/v52/locomo_scale_outputs/locomo_scale_per_question.csv.gz` | `63b8138591d36f9b15228404be91fead6bacdc01` | `b7abd942c13cf9ce1b1c4a13e3ff39fb26a26e8b2f2749dd92d76f0b2a474602` |
| LongMemEval | `research/v52/longmemeval_scale_outputs/longmemeval_scale_per_question.csv.gz` | `1619a668bd2f01737692b6f07de2edb6423863fa` | `1db682a277b8fe7f0b3aa7cf02831bf07f0d5c4c340796a57c93df5441df3157` |

Both sha256 values are already recorded in the ledger at full 64-hex length in
**L-073** — `docs/CONTINUITY_LEDGER.md:1516` for LoCoMo and `:1519` for
LongMemEval. The earlier entry **L-055** (`docs/CONTINUITY_LEDGER.md:1101`) records
the LoCoMo digest only as a 16-hex prefix (`b7abd942c13cf9ce`) and states that the
LongMemEval per-question sha256 matches its summary without printing it. This
decision therefore pins artifacts the programme had already bound, rather than
introducing a new dependency.

### 1c. Verification performed before binding

Read-only, on the branch head above:

| check | LoCoMo | LongMemEval |
|---|---|---|
| rows | 92,100 | 28,200 |
| unique `question_id` | **1,535** | **470** |
| questions carrying more than one distinct `native_fractional_R3` | **0** | **0** |
| sha256 recomputed from the committed blob | matches the table | matches the table |
| empty / null / non-numeric `native_fractional_R3` | **0** | **0** |
| value range | `[0.0, 1.0]` | `[0.0, 1.0]` |

The one-float-per-question property of 1a holds in the bytes rather than by
assumption.

The coverage counts also corroborate `f9951c0`: **1,535** is exactly the
corrected-key LoCoMo cohort bound by that decision's Decision 1, and **470** is
exactly the LongMemEval primary cohort. Anchors produced by a raw-evidence (1,540)
run would contradict it; these do not. The two decisions agree in counts.

**Stated limitation.** Set identity between the anchor `question_id` values and the
bound cohort id lists is established here by count and by provenance, **not** by an
element-wise comparison. That comparison is not waived: the `E-M-027` refusal in 1d
forces it at load time, and a connector must fail closed if it does not hold.

### 1d. What the binding requires of any connector

1. Anchors are read from the two blobs named in 1b, at the pinned blob ids, and any
   pre-run seal governing a run on this track pins them by blob id.
2. The `E-M-027` total-coverage refusal is retained and is not relaxed.
3. **Synthetic anchors remain test fixtures only and may never substitute for these
   frozen values**, per the README text.
4. If a later stage supersedes the coordinate-scale stage as the governing control,
   the anchor source is re-bound by a new decision — never inherited silently.

---

## DECISION 2 — Closure criterion for F3 and N1

### The two findings are distinct and N1 subsumes the obvious repair

- **F3** (coverage): *"its fixed alternating sign vector negates only 48 of 96
  coordinates, so a zero at column 0 aborts while column 1 passes undetected."*
  (`origin/main:docs/CONTINUITY_LEDGER.md:1735`,
  `origin/main:ops/CURRENT_STATE.json:1912`.)
  The suggestion to negate every coordinate so that coverage becomes total is not in
  the F3 record; it is in the takeover review —
  `origin/research/llmzip-takeover-2026-09-09:research/takeover_2026_09_09/TAKEOVER_REVIEW.md:31`.
- **N1** (aggregation): *"even two coordinates which are both negated can undergo
  opposite disagreement changes, leaving the summed Hamming distance unchanged.
  Thus coverage of every coordinate by one sign vector is not a sufficient
  certificate of coordinatewise invariance."*
  (`origin/research/llmzip-takeover-2026-09-09` `1ad44c6`,
  `research/takeover_2026_09_09/TAKEOVER_REVIEW.md`.)

N1 therefore **invalidates the repair proposed for F3**. Completing coverage is
necessary and not sufficient. A criterion must be chosen before F3 can be closed.

### The decision — a coordinatewise certificate is required

The control is closed only when it certifies **coordinatewise** invariance. An
aggregate-distance comparison is not accepted as the certificate, at any coverage.

Required properties:

1. **Coordinatewise assertion, against an independent oracle.** Under a signed
   permutation `(P, s)` the check asserts that the code vectors correspond
   elementwise — each output bit equals the expected image of its source bit —
   rather than asserting that summed Hamming distances match. This removes the
   aggregation channel N1 exhibits. Three qualifications are binding, because the
   elementwise form alone can be satisfied vacuously:
   - **(a) Independent oracle.** The expected images are produced by an exact-
     arithmetic oracle written independently of the code under test. They must not
     come from the same `apply_signed_perm`-style helper the implementation uses; a
     common-mode error there would appear identically on both sides and the
     assertion would pass while proving nothing.
   - **(b) Every member, every coordinate.** The elementwise assertion runs on
     **every** member of the family in requirement 3, including the vector that
     negates all 96 coordinates — not only on the member that exhibits the N1
     witness.
   - **(c) Family fixed before data.** The family is drawn and fixed as source
     literals before any archive is observed, and **each member carries its own
     negative control**.
2. **Total coverage.** Every one of the 96 coordinates is negated by at least one
   tested sign vector. This discharges F3.
3. **A family, not a single vector.** The check runs over a preregistered family of
   signed permutations with declared fixed seeds, not one fixed canary. Seeds are
   source literals fixed before any data is observed, as the existing canary already
   is.
4. **Explicit exact-zero handling.** The `-0.0 >= 0` behaviour is asserted directly
   rather than left implicit, in both directions, including the all-zero coordinate
   case the current control never fires on.
5. **The existing fixed canary is retained** as a regression test, not as the
   certificate.
6. **A failing case is built first.** N1's own witness — the column-centered 96×96
   synthetic archive with zero columns 0 and 2 and query values `+1` and `-1` — is
   adopted as a mandatory negative control that the new check **must reject** and
   the old one accepts.

### Scope of what N1 does and does not establish

Recorded verbatim from the source so it is not overstated later: N1 *"reproduces a
limitation of the control's assurance, not an incorrect retrieval score"*, and *"does
not establish that the fixture occurs after fitting any real archive, that an accepted
result is wrong, or that the research hypothesis is false."* This decision changes the
certificate, not any accepted number.

---

## DECISION 3 — Stale records in the membership completion map

All line references below are on `origin/main` at `0a79017`; the map is
`docs/v52/V52_MEMBERSHIP_COMPLETION_MAP_2026-09-08.md` and the ledger is
`docs/CONTINUITY_LEDGER.md`.

The map records at `map:58` a runner+ingestion review as "in progress" and at
`map:105` that **G-1** ("independent review of runner + ingestion") is "in
progress"; at `map:106` that **G-2** ("disposition of whatever G-1 finds") is "not
reached". The two G-1 entries are stale because the review ran to a verdict; the
G-2 entry is stale for a different reason, given below. Neither correction disposes
of any finding.

### G-1: the chain and where it ends

G-1 is the independent runner+ingestion review and its chain terminates at **L-080**.
L-076 recorded that review's FAIL verdict, scoped only to the runner and ingestion
wiring at `22e44608` (`ledger:1595`, `ledger:1602`). L-077, L-078 and L-079 recorded
successive fix packages and their independent delta-closure checks. L-080 records the
audit of the Codex v5 repair package, verdict PASS WITH FINDINGS limited to that
repair package (`ledger:1703`, `ledger:1710`, `ledger:1718`). The review event is
complete; what is open is the disposition of its output.

### G-1's findings are L-080's four, not L-081's seven

G-1's findings are exactly the four non-blocking findings at `ledger:1713`, whose
disposition L-080 explicitly awaits (`ledger:1719`):

- **F-1** (optional, NEW) — `verify_source_identity` gates `n_questions` with
  `isinstance` while `_safe` requires an exact type, so an int subclass yields
  `UnsafeErrorField` instead of the intended named refusal; unreachable from JSON,
  fails closed, v5 strictly safer than v4 here and only less informative.
- **F-2** (optional, NEW) — one suite probe passes for the wrong reason and is the
  single mutant nothing caught; confirmed in isolation not to leak, so a
  test-discrimination gap rather than a hole.
- **F-3** (optional) — the ingest's cohort-size site forwards a manifest value with
  no local type gate, relying on the hash pin; not a v5 regression.
- **F-4** (wording) — one README sentence is slightly wider than the code at two
  gated sites.

The two further items at `ledger:1714` are explicitly recorded but **not reopened**
and are not among the four.

**Naming hazard, recorded so it is not repeated:** L-080's findings are `F-1`…`F-4`
(hyphenated) and L-081's are `F1`…`F7` (unhyphenated). An earlier draft of this
decision conflated them. Any future reference must state the ledger entry, not the
bare label.

### A second item L-080 leaves open

In the same sentence at `ledger:1719`, L-080 also awaits disposition of **whether the
Codex v5 package becomes the working candidate line in place of v4**. No later record
disposes of either item: L-081 reviews a different package (`ledger:1728`) and L-082
decides different obligations (`ledger:1755`, `ledger:1769`). L-082 is the final
ledger entry (the file ends at line 1770), so both items stand open.

### L-081 belongs to no gate in the map

The seven findings (`F1`–`F7`, `ledger:1735`) and the nine named test gaps
(`ledger:1736`) belong to **L-081** — the review of the execution-preparation
(M-1/M-2/M-3) package, verdict PASS WITH FINDINGS scoped to the prepared functions
only (`ledger:1728`, `ledger:1733`). They are not G-1's.

That review **corresponds to no gate in the chain**, and this is recorded here rather
than left for a reader to discover:

- `map:107` states **G-3**, the authorization to write M-1/M-2/M-3, is
  **"not granted; no design or code authority exists for them."**
- `map:108` states **G-4**, the review of *those components once written*, is
  "not reached".
- L-080's own closing clause is decisive: a scope-limited PASS on the v5 repair
  *"does not authorize the experiment, **does not open M-1/M-2/M-3**, and does not
  license a seal or a run"* (`ledger:1719`).

**Disposition:** L-081 is therefore **a preparation review lying outside the gate
chain**, not an early instance of G-4. G-4 reviews components written under G-3;
G-3 has not been granted. The prepared code was disclosed as such by its author and
recorded as such by L-081; it is a **candidate for review once G-3 is granted, never
an inheritance that substitutes for it.** G-3's status is unchanged by this decision.

### Consequence for G-2

"Not reached" (`map:106`) is stale. L-080 awaits the Head Researcher's disposition of
the four non-blocking findings (`ledger:1719`), and disposition of whatever G-1 found
is exactly G-2's definition (`map:106`). **G-2 is therefore reachable and pending, not
"not reached".** The map has no defined intermediate label for this state; the wording
of the replacement label is the Head Researcher's to choose, and this decision does
not invent one.

### What this addendum does NOT do

It does not dispose of L-080's four findings or of the v5-versus-v4 candidate
question; it does not dispose of L-081's seven findings, its nine test gaps, or
integration obligations 1, 4 and 5, all of which remain open per L-082
(`ledger:1766`, `ledger:1769`); it grants no authorization of any kind and does not
alter G-3.

Per the programme's additive-correction rule the map bytes are **not rewritten**. An
addendum is issued alongside this decision recording the corrected status, and this
decision is its authority.

---

## What this decision explicitly does NOT do

- It does **not** authorize any execution, seal, pilot or run on any track.
- It does **not** dispose of obligations 4 and 5, of findings F1, F2, F4–F7, or of
  the nine named test gaps.
- It does **not** grant retrieval-quality outcome access, and does not set or request
  `V52_T4F1_AUTH_HMAC_KEY_HEX`.
- It does **not** modify any sealed byte, accepted audit, or frozen result, and does
  not rewrite the completion map.
- It does **not** read, recompute or expose any retrieval-quality outcome: the
  verification in 1c counted rows, unique ids and value multiplicity only.
- Decision 3 of `f9951c0` — the v5 ingestion reconciliation — remains an open named
  prerequisite and is untouched here.

Task 4F1 remains **SEALED / RUN BLOCKED / OUTCOME ACCESS FORBIDDEN**. This line is
retained deliberately: scoping these decisions away from Task 4F1 does not relax any
Task 4F1 prohibition.

---

## Recording

On approval: branch `hr/obligation-1-and-f3-n1-2026-09-09` from `origin/main`
(`0a79017`, L-082); commit this file, its `.sha256` sidecar, and the completion-map
addendum with its sidecar; additions only; push. Then separately on `main`:
`ops/CURRENT_STATE.json` and ledger entry **L-083**.

---

*Prepared by the Continuity Lead.*
