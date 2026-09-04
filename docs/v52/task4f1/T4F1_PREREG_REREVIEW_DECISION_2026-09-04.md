# V52 Task 4F1 — Head Researcher Preregistration Re-Review Decision

Date: 2026-09-04
Role: Head Researcher / reviewing authority
Review target commit: `c0133fce9b755d13d9be3016e8e06f493d6b275b`
Review target file: `docs/v52/task4f1/TASK4F1_PREREGISTRATION_DRAFT_2026-09-03.md`
Independently verified target SHA256: `5e61898193421a3a18791202668c0974f23d2fb4080a107069e7b7127e35ea44`
Target size independently cross-checked against GitHub metadata: 14,688 bytes

## Verdict

**APPROVED FOR SEALING — SCIENTIFIC PREREGISTRATION DESIGN ACCEPTED.**

This decision approves the exact amended preregistration bytes identified above for sealing as the
Task 4F1 scientific preregistration. It does **not** authorize Task 4F1 execution, does **not** accept
or pre-judge the separate V7 execution-package audit, and does **not** permit retrieval-quality
outcome access.

The prior `REQUEST CHANGES — SCIENTIFIC PREREGISTRATION DESIGN NOT YET ACCEPTED` is discharged for
this exact draft SHA256.

## Independent byte and scope verification

The draft was fetched from the exact reviewed commit rather than from the repository default branch.
Its UTF-8 bytes were independently reconstructed from the connector-fetched file content and hashed.
The resulting SHA256 is exactly:

`5e61898193421a3a18791202668c0974f23d2fb4080a107069e7b7127e35ea44`

GitHub reports the same blob at 14,688 bytes. The amendment commit changes the preregistration draft
by five scientific hunks (+50/-13 lines) and does not alter an execution candidate as part of that
scientific amendment.

The amended draft remains outcome-free with respect to Task 4F1: no BEAM retrieval-quality result,
ranking, distance, metric outcome, or Native-vs-comparator arm result was accessed or used in this
re-review.

## A1–A6 discharge table

### A1 — ceiling-comparability instrument
**ADEQUATELY DISCHARGED.**

Sections §2.2 and §3.2 now make the ceiling-free `|gold| <= 3` stratum the primary cross-tier
comparability instrument, with frozen denominators stated in advance. The remaining gold-cardinality
strata are reported without rescaling. `D_t^norm` is explicitly demoted to a sensitivity statistic,
its induced high-|gold| upweighting is disclosed, and it is explicitly barred from silently
overriding or vetoing the §6 category assigned from `D_t`.

This resolves both parts of the blocking finding: the hidden estimand change is no longer hidden,
and the prior §2.2/§6 decision-rule conflict is removed.

### A2 — exact sign-boundary arithmetic
**ADEQUATELY DISCHARGED.**

Section §6 now fixes exact rational arithmetic for the sign of `D_t` and states a valid common
denominator bound. `D_t > 0`, `D_t = 0`, and `D_t < 0` are therefore defined without an
outcome-dependent floating-point tolerance or a later-chosen practical-significance threshold.

Implementation note, not a defect in this preregistration: before any run authorization, the
outcome-analysis implementation must honor this exact-rational rule rather than classify the sign
from a rounded or floating aggregate. That implementation requirement belongs to the later
execution/authorization gate and does not require changing the approved scientific draft.

### A3 — zero versus reversal
**ADEQUATELY DISCHARGED.**

Section §6 now reserves `tier-local direction reversal` for `D_t < 0` and uses `tier-local null`
for `D_t = 0`. Both are subordinate descriptors and do not create overlapping global categories.

### A4 — descriptive stability
**ADEQUATELY DISCHARGED.**

Section §4 pre-specifies the leave-one-archive-out min-max range for every tier, using the frozen
archive counts, and explicitly states that it is not a confidence interval, not a standard error,
and has no population-coverage interpretation. This provides a bounded composition-sensitivity
summary without importing unsupported population inference.

### A5 — win/tie/loss scope
**ADEQUATELY DISCHARGED.**

Section §3.3 prevents raw win/tie/loss counts and tie rates from being interpreted as cross-tier
scale evidence, requires gold-cardinality stratification for a cross-tier reading, and adds the
tie-excluded `W/(W+L)` descriptive summary. It remains descriptive and does not enter the global
decision rule.

### A6 — finite Haar comparator
**ADEQUATELY DISCHARGED.**

Sections §3.1 and §4 consistently define the comparator as the finite mean over the exact five
pre-specified Haar seeds. The seeds are constitutive of the comparator, not a random sample from a
larger Haar-rotation population; the per-seed range is sensitivity reporting only and licenses no
distributional inference.

## Remaining scientific defects

**None found that require amendment before sealing.**

The following limitations remain real but are already stated at adequate strength in the draft and
therefore are not defects:

- tier is bundled with benchmark composition and is not a randomized or isolated context-length
  intervention;
- four tiers are too few to justify a degradation law, trend fit, extrapolation, or causal claim;
- the ceiling-free stratum removes metric-ceiling compression but does not erase all remaining
  composition differences;
- a flat same-direction profile would add only bounded incremental scientific information beyond the
  already accepted benchmark evidence;
- the pooled 1,712-question quantity remains secondary rather than a headline estimand;
- no population-level inference is licensed by this fixed benchmark.

## Sealing and execution boundary

Approval here means only that the **scientific preregistration design may be sealed**.

The seal must bind the exact approved draft SHA256 above and the already frozen cohort and execution
anchors required by the preregistration. Any scientific-content change to the draft after this
decision produces new bytes and requires a new approval decision.

Task 4F1 execution remains blocked until the separate execution-package/governance track is closed
and a distinct Head Researcher run authorization is issued under the accepted authorization
contract. This decision creates no HMAC key, no authorization, and no permission to run or finalize.

## Outcome-boundary declaration

During this re-review:

- CLI `--mode run` invocations: 0
- CLI `--mode finalize` invocations: 0
- valid production authorization constructed: false
- HMAC key set or inspected: false
- real BEAM retrieval ranking performed: false
- Task 4F1 retrieval-quality outcome computed/read/reported: false/false/false
- execution candidate modified: false

No retrieval-quality outcome is contained in this decision artifact.
