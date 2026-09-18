[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Membership Under Scaling — candidate v3 (findings-limited correction of NEW-1, NEW-2, NEW-3)

Status: **`[IMPLEMENTATION PREPARATION — NOT AUTHORIZED TO RUN ON REAL DATA; NOT INDEPENDENTLY REVIEWED]`**

Prepared by the Continuity Lead, who therefore **may not** call it reviewed. The corpus-bound runner
is **still not written**, and closing the core does not authorize the experiment.

## What this is

A correction limited to the three findings of the independent **delta closure check of v2**, branch
`audit/v52-membership-v2-closure-2026-09-07` @ `712412a5947fa56374e05bf3e3a0b075d4578b6d`, report
sha256 `ec75beb4e054c4bc6e7c46aa5c2a006c749e2bd65b3d93f90543d31a1e19d0be`, verdict
**CLOSURE PASS WITH FINDINGS**.

This round is **not** a new design, not a new feature, and not a general audit round. The first-round
findings (F-1 … F-12) were **independently confirmed closed** by that check and are **not reopened**
here.

Earlier versions stay byte-unchanged and are bound by hash in `GOVERNING_DOCUMENTS.md`, together with
the four normative documents this code answers to. Those documents live on `main` and deliberately
not on this branch; read them there, hashing **raw Git blobs** rather than a Windows checkout.

| version | branch | commit | core sha256 |
|---|---|---|---|
| v1 | `impl/v52-membership-under-scaling-2026-09-07` | `a6d70ff63ce44ea0f066a075853c9e93dec53122` | `707e166c80d9231d089341a804e0acdd8845781fec7560821c67b3f6d0731a00` |
| v2 | `impl/v52-membership-under-scaling-v2-2026-09-07` | `8179ce31afc8ec9a2469c801a0a5e022b4494518` | `60141d05f2285d268a88d98344770c8cb5d166168a6fa29371a1ea330db0a1e1` |

## The three findings, and the change each one produced

| finding | what was wrong in v2 | change in v3 |
|---|---|---|
| **NEW-1** | The conformance test recomputed only **3 of the 7** published fields. The closed schema constrains key **names**, so a wrong value substituted **into a permitted key** was invisible: the check's mutants R1, R2, R3 and R6 all survived. | Conformance now recomputes **all seven** published fields of `aggregate` — the three scalars, the three per-seed vectors elementwise, and `n_question_slots` — against the independent reference. The schema equality check is kept, for the different job of catching a **new** key. |
| **NEW-2** | The F-1 `cv_sigma_before` check ended in `or True`, so it passed unconditionally; setting the value to `123456.0` did not fail it. | The check compares `cv_sigma_before` against a CV recomputed in the test from the fixture archive, and is paired with a control asserting that the comparison **rejects** a wrong value. |
| **NEW-3** | `build_clusters([], 0)` failed with a raw `ValueError` out of `np.concatenate`, three frames below the API — the defect class F-8 already fixed for index selections. | A named `DesignViolation` at the top of `build_clusters`, tested for `0` and for a negative count. |

### Tolerance used in the comparisons

`CONF_TOL = m.TOL` — the module's existing tolerance, which binding §6 fixes at an **absolute
`1e-12`**. Bitwise equality is **not** required and is not asserted: floating-point summation is
order-dependent in its last digits, and a bit-level demand here would be an unjustified new
condition. Measured agreement on the fixture is `max|diff| = 3.55e-15` on each per-seed vector.

### The `or True` sweep, and its exact scope

A machine sweep of this test file's own AST reports any `check(...)` whose condition is a boolean
expression ending in a literal `True` — the shape that slipped through twice. It currently reports
**none**, and it is paired with a control proving the sweep detects that shape when present.

**Scope:** that sweep covers **that one shape and nothing else**. It is not a claim that every check
in this suite is meaningful, and no such claim is made.

## What is checked, and what is not claimed

**No claim is made that any wrong computation is necessarily caught.** Two earlier versions of this
section were found overstated by independent review and are corrected here rather than re-argued:

- v1 claimed a **forbidden-word scan** was assurance. The implementation review defeated it by adding
  a genuine `Δ/G` ratio named `relative_change`; all 74 checks passed (F-4). **A word scan is not
  used as assurance anywhere in v3.**
- v2 claimed a quantity added under **any** name fails a test. The closure check defeated that too, by
  putting the ratio **into an existing permitted key** (NEW-1).

What is actually checked, and only this:

1. **Conformance** — all seven published fields of `aggregate` recomputed by an independent reference
   implementation written from the design text in plain Python, compared at `m.TOL`. Paired with
   negative controls: a perturbed scalar and one perturbed element of a per-seed vector are both
   rejected.
2. **Closed output schema** — the key set against a frozen expected set, which catches a **new** name.
   It cannot see a wrong value behind a permitted name; that is NEW-1's point and the reason for (1).
3. **AST enumeration** of divisions and of `aggregate`'s literal return keys — support, **explicitly
   not a proof**: `np.divide` is not a `Div` node, so this check alone can be walked around. Mutant
   R6 does exactly that and is killed by (1), not by this.
4. **The self-sweep** described above, for one named defect shape.
5. **The named fault variants** in `scripts/mutation_probes_v3.py`, each demonstrated to be caught.

## Evidence

- `evidence/synthetic_test_output.txt` — **99 checks, ALL PASS**. Synthetic data only.
- `evidence/mutation_probes_v3_output.txt` / `.json` — **22 mutations applied, 21 killed, 1 survived.**

Probe provenance: M1–M16 re-anchored from the implementation review's `scripts/mutation_probes.py`
@ `68819424`; **R1, R2, R3, R6** and the NEW-2 / NEW-3 probes from the closure check @ `712412a5`.
Neither audit namespace is modified.

**What the kill count means, and only this:** the suite catches exactly these 22 fault variants. It is
**not** evidence that the core is free of defects and must not be reported as such.

**The one survivor is expected and is not a hole.** `M16` removes the partition-coverage guard, which
is **unreachable** through the public API because label validation precedes it and every question
therefore carries exactly one label. A mutation test cannot kill an unreachable guard. It is reported
as such rather than removed, and rather than papered over with a test that reaches it only by
monkeypatching internals.

## Carried forward, unchanged by this round

- **F-12** — deliberately not acted on. Binding §6 fixes an absolute `1e-12` and says a relative form
  needs a new decision. The review's measured worst case (`5.116e-14`, ~19.5× headroom) is recorded in
  `LINEARITY_HEADROOM_NOTE` and acted on nowhere.
- **N-2, N-3, N-4** — runner obligations, not core defects: the bootstrap seed must be preregistered;
  the LongMemEval inheritance tag must be emitted and cluster-bootstrapping LongMemEval prevented; the
  identical `D` must be applied to the query with nothing estimated from it.

## Boundaries observed in producing this candidate

No corpus was read or downloaded, no model downloaded, no real fitting, retrieval or ranking, no
real-data bootstrap, no pilot, no sealing, no HMAC, no `run` and no `finalize`. Tests ran on this
machine's Python and NumPy, **not** the pinned research stack. Task 4F1 remains sealed, blocked and
untouched.
