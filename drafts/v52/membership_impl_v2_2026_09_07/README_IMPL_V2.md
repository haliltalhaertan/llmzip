# Membership Under Scaling — candidate v2 (findings-limited correction)

Status: **`[IMPLEMENTATION PREPARATION — NOT AUTHORIZED TO RUN ON REAL DATA; NOT INDEPENDENTLY REVIEWED]`**

Prepared by the Continuity Lead, who therefore **may not** call it reviewed. Corpus-bound runner
**still not written**; closing the core does not authorize the experiment.

## What this is

A findings-limited correction of `drafts/v52/membership_impl_2026_09_07/`, which is **left
byte-unchanged** (core `707e166c80d9231d…`, tests `97e6e7206864dffe…`). The audit namespace
`audit_v52_membership_impl_review_2026_09_07/` is likewise untouched.

Source of the findings: independent implementation review on branch
`audit/v52-membership-impl-review-2026-09-07` @ `68819424765ed3da89377c89980d7e42546bfe02`,
verdict `PASS WITH FINDINGS`.

## Findings mapped to changes

| finding | severity | change in v2 |
|---|---|---|
| **F-1** | BLOCKER | `cv_sigma_after` is now a genuine CV (`spread / mean`) via a shared `_cv` helper. **No epsilon is added** and the definition is not weakened: a zero mean returns `NaN`, tested on an all-zero archive. The v1 quantity is still published under its true name `sd_sigma_after`, so nothing is silently dropped. |
| **F-2** | BLOCKER | `build_clusters` validates **before** grouping: rejects `None`, `NaN`, `bool`, unsupported types, and **mixed** label kinds (rejected rather than coerced, because coercion would merge `1` with `"1"` or split one conversation). Requires every cluster non-empty and **proves** the partition — every question in exactly one cluster, total membership equal to the question count. Diagnostics separate the two things that were previously confusable: `questions_lost_to_invalid_labels` (structurally 0) and `mean_clusters_not_drawn_per_replicate` (ordinary resampling). |
| **F-3** | REAL | duplicate question ids raise a named `DesignViolation`, not an `IndexError`. |
| **F-4** | REAL | the word scan is **gone as an assurance claim**. See "What this suite claims" below. |
| **F-5** | REAL | the cluster fixture is replaced by three clusters of unequal size and value, on which slot-, distinct- and cluster-weighting give three different answers; the suite asserts the core matches the slot value and differs from the other two. README claims now match what is tested. |
| **F-6** | REAL | `require_real_data_authorization` reads the module global **at call time**; tested by flipping the constant and restoring it. Still declarative: no runner exists to call it, and that is stated rather than implied. |
| **F-7 / F-8** | COSMETIC | index selections are validated for integer dtype and range; negative indices no longer wrap, floats are no longer truncated, out-of-range raises `DesignViolation`. |
| **F-9** | COSMETIC | a boolean score is rejected explicitly. |
| **F-10** | COSMETIC | an archive of fewer than two rows is rejected. |
| **F-11** | COSMETIC | the no-op `body.replace("block","")`, the dead `"distinct" if False else "partition"` conditional and the vacuous `spans_zero in (True, False)` are gone. `spans_zero` is now asserted **`is True`** on a fixture centred at zero and **`is False`** on one far from it. |
| **F-12** | COSMETIC | **not acted on, deliberately.** Binding §6 fixes an absolute `1e-12`; the review's measured worst case (`5.116e-14`, ~19.5× headroom) is recorded in `LINEARITY_HEADROOM_NOTE`. A relative tolerance would need a new decision. |
| N-2, N-3, N-4 | — | runner obligations, not core defects. Carried forward for the unwritten runner: the bootstrap seed must be preregistered; the LongMemEval inheritance tag must be emitted and cluster-bootstrapping LongMemEval prevented; the identical `D` must be applied to the query with nothing estimated from it. |

## What this suite claims, and what it does not

The v1 suite scanned the source for forbidden words and presented that as assurance. **It was not.**
The reviewer added a genuine `Δ/G` ratio named `relative_change` and all 74 checks still passed.

v2 does not repeat that claim. A word scan cannot see a quantity spelled differently, and the AST
enumeration below — while much stronger — **is still not a proof** that no ratio can ever be
introduced.

The primary guarantee is neither:

1. **Conformance.** The three reported quantities are recomputed by an independent reference
   implementation written from the design text in plain Python, and must agree exactly.
2. **Closed output schema.** `aggregate`'s keys are compared against a frozen expected set, so a
   quantity added under *any* name fails a test instead of slipping past a scan. This is what kills
   the reviewer's `relative_change` mutation.
3. **AST enumeration**, offered as a supporting check and explicitly not as a proof.

## Evidence

- `evidence/synthetic_test_output.txt` — **88 checks, ALL PASS**, every guard paired with its
  failing case.
- `evidence/mutation_probes_v2_output.txt` / `.json` — 16 mutations, **15 killed, 1 survived**.

**What the kill count means, and only this:** the suite catches exactly these 16 fault variants.
It is **not** evidence that the core is free of defects and must not be reported as such.

**The survivor is expected.** `M16` removes the partition-coverage guard, which is **unreachable
through the public API** because label validation precedes it. A mutation test cannot kill an
unreachable guard; that is a property of defence in depth, not a hole. It is reported rather than
removed, and rather than papered over with a test that reaches it only by monkeypatching internals.

**A defect in my own probe, disclosed rather than corrected quietly.** My first re-anchoring of the
reviewer's `M3` computed the cluster average into an *unused* variable, so it mutated nothing and
reported a false hole in the suite. The probe was repaired to replace the assignment that is
actually used; `M3` is now killed. Both the error and the repair are recorded in the script.

## Not validated

Anything requiring a corpus. No pipeline executed end to end, no real retrieval, no real-data
bootstrap. The corpus-bound runner is **not written**; writing it is not authorized. Tests ran on
this machine's Python and NumPy, not the pinned research stack — an inference, not a run.

## Boundary

No corpus read, no model or corpus download, no real fitting/retrieval/ranking, no real-data
bootstrap, no pilot, no sealing, no HMAC, no `run`/`finalize`, no agent commissioned by this file.
Task 4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.
