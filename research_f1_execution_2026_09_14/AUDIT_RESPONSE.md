[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Coordinator response to the F1 execution audit

Opinion received: **PASS WITH OBSERVATIONS**, six findings. The auditing session reproduced all six
coefficients **bit-for-bit** (max diff exactly 0) from its own cold-start implementation, frozen
before it read any coordinator code, and cross-checked against a third naive implementation and a
transcription of the auditor's own function. It also states plainly that it is NOT independent
(same model family, commissioned by the coordinator, brief quoted the numbers first). The
coordinator agrees and does not count this as satisfying the project's independence requirement.

## Dispositions

**F-6 (errata claim wrong) — ACCEPTED, confirmed first-hand, artifact corrected.**
I isolated both errors myself (`coordinator/coord_errata_check.py`): E1 (double centering) moves
LongMemEval by **+0.000000 pp**; E2 (ALL@3 instead of FR@3) accounts for the entire
**-0.376478 pp**. My ERRATA attributed the shift to both errors jointly. That was wrong.
`ERRATA_COORDINATOR.md` now carries a CORRECTION section; the original text is preserved unedited.
E1 remains a genuine methodological error — it would corrupt any cache that was not pre-centered —
but it changed no number in this dataset.

**F-2 (contract headline gate C3 never applied) — ACCEPTED as a real gap.**
`check_headline_gates()` exists in the package and I never called it. Applied now, all three
benchmarks FAIL at 1e-12. Diagnosis (VERIFIED): the failure is confined to the SIGN arm. The float
arm is exact — LongMemEval float differs from the frozen reference by **5.551e-17** — while the
sign arm differs by **1.584e-04**. The cause is the tie estimator, not the geometry: the frozen
reference averages NT=20 sampled tie-break permutations, and my exact expectation carries no
sampling noise. The auditor measured the frozen estimator's own seed spread at **2.7e-03**, which
is larger than every discrepancy under discussion. So a 1e-12 gate cannot be met by anyone using
the exact expectation, and cannot be met by the frozen estimator against itself either.
Consequence: **F1 stays OPEN**, and the gate question is now explicit rather than skipped.

**F-1 (hardcoded 4-dp auditor targets) — ACCEPTED as imprecise.**
The published README labels the column "(4 dp)" and prints every diff, and F1 was kept OPEN, so no
claim rests on it. But the contract specifies full-precision targets at 1e-12 and my script
compared against rounded ones. Both sides of the audit agree on the underlying cause: the
auditor's `INDEPENDENT_QUERY_ROWS.json` is not committed anywhere readable, so Delta_q must be
recomputed rather than reused. The auditor's own diagnosis is the actionable one — swapping only
the Delta_q source to a frozen surface improves agreement ~1000x (2.6e-04 to 2.9e-07). **Remedy:
publish that file.** Until it is published, 1e-12 reproduction is impossible for any party here.

**F-3 (exact-expectation substitution under-priced) — ACCEPTED.** Recorded with the 2.7e-03 seed
spread. The substitution remains the better estimator (order-independent, V43-compliant, no
sampling noise), but its relationship to the frozen estimator must be stated as an equality in
expectation, not as agreement in value.

**F-4, F-5 (LOW) — ACCEPTED without argument.** Delta_q was recomputed where the contract says to
reuse the frozen surface (same root cause as F-1); the input inventory omits the LoCoMo and
`drive/audit_layer` inputs that were read but not used for a reported number.

**Mutation testing: 7/10 caught, 3 proved equivalent mutants.** The three that passed unnoticed
(tolerance-on-integers x2, re-centering pre-centered data) are the same phenomenon as F-6: they
cannot change a result on this data. That is a property of the data, not a strength of my checks.

## What this changes about F1

Nothing in the F1 substance: the six coefficients are now reproduced twice, independently, at full
precision, and the bug's inconsistent direction is confirmed. What the audit changes is the
**honesty of the surrounding claim**: the contract's 1e-12 gate was skipped, the comparison targets
were rounded, and one errata attribution was false. All three are now on the record.

F1 disposition is unchanged: **still OPEN**. Not closeable here — not independent, LoCoMo leg
absent, archive-level identity unverifiable, and now also: the contract gate cannot be met without
the unpublished query-rows file.
