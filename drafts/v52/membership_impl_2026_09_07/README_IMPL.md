# Membership Under Scaling — implementation preparation

Status: **`[IMPLEMENTATION PREPARATION — NOT AUTHORIZED TO RUN ON REAL DATA; NOT INDEPENDENTLY REVIEWED]`**

Prepared by the Continuity Lead, who therefore **may not** call it reviewed. It is handed over as a
package ready for **independent implementation review**, which is a separate commission that has not
been made.

## What governs this code

`docs/v52/V52_MEMBERSHIP_UNDER_SCALING_ACCEPTANCE_BINDING_2026-09-07.md` on `main`, whose precedence
is **R2 → R1 → draft**. That record's §1 lists the apparatus that R2 withdrew and that must not
appear here; the test suite asserts its absence rather than trusting this sentence.

## Files

| file | role |
|---|---|
| `membership_scaling_core.py` | the whole computation: scaling operator, membership, rotation, distances, record validation, the three quantities, both resampling schemes, output safety |
| `test_membership_scaling_core.py` | 74 synthetic checks, every guard paired with the failing case |

There is **no workflow file**, and this directory is not `research/v52/`, so nothing here can be
triggered by a push, a schedule or a dispatch.

## Real-data execution is off by default

`REAL_DATA_EXECUTION_ENABLED = False`, and `require_real_data_authorization()` raises unless an
explicit argument overrides it. No function in this module reads a corpus, downloads anything, or
imports anything that does. The suite asserts both the default and that the gate can fail.

## What the tests demonstrate rather than assert

- **Percentage-point units and aggregation weights are explicit.** Arm fractions `0.30 − 0.22` give
  exactly `8.0` pp; the mean divides by the number of selected question **slots**, so a repeated
  index counts twice.
- **Pairing is demonstrated, not assumed.** With a per-question change fixed at `−5` pp, the paired
  bootstrap returns a degenerate interval `[−5.000000, −5.000000]` while the level `G` still varies
  across replicates. Independent per-arm resampling could not produce that.
- **Cluster multiplicity is demonstrated.** With cluster A worth `1.0` pp and cluster B worth `0.0`,
  drawing A twice returns exactly `1.0` pp over `6` slots, and drawing A then B returns `3/8` — the
  question-weighted value, not the cluster-averaged `0.5`.
- **Records are not accepted silently.** Missing, duplicated, NaN, out-of-range, unknown-arm,
  unknown-seed and malformed records each raise.
- **Results are not overwritten silently.** `safe_write_json` refuses an existing path.
- **The matched-`Q` control can fail**, as can the identity check, the orthogonality check, the
  invariance check, the partition check and the linearity consistency check.
- **Linearity is checked at `1e-12`, not bitwise**, because floating-point summation is
  order-dependent in its last digits and demanding exact equality would fail for a reason unrelated
  to the science.

## A defect this preparation found in itself

`DEGENERATE_FLAG_THRESHOLD` was defined and never used: the code recorded the degenerate-coordinate
count but never applied the per-archive **flag** that R1 §1 requires. It was dead code standing in
for a design requirement. Fixed by returning a diagnostics dictionary from `scale_matrix` that
carries the count **and** the flag together, so a caller cannot record one and forget the other, with
tests that the flag fires above 4 and does not fire at 3.

Disclosed here rather than quietly corrected, and the tests that would have caught it earlier are
retained.

## What is NOT validated

Anything requiring a corpus. No pipeline has been executed end to end, no real retrieval has been
computed, and no real-data bootstrap has been run. The runner that would wire this core to the frozen
bases is **not written**, because writing it is not authorized at this stage.

The tests ran on this machine's Python and NumPy, not on the pinned research stack. The functions do
not depend on the version, but that is an inference and not a run.

## Boundary

No corpus read, no model or corpus download, no real fitting, retrieval, ranking or bootstrap, no
pilot, no sealing, no HMAC material, no `run`/`finalize`, no agent commissioned. Task 4F1 remains
`SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.
