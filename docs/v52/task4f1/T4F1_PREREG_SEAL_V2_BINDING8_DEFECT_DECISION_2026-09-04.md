# V52 Task 4F1 — Head Researcher Seal V2 Binding-8 Defect Decision

Date: 2026-09-04
Role: Head Researcher / final scientific approval authority
Reviewed main: `1b2323dc90918dd3318bc70b1c8993abc6bbb938`
Reviewed Seal V2: `docs/v52/task4f1/TASK4F1_PREREGISTRATION_SEAL_V2_2026-09-04.json`
Reviewed Seal V2 declared SHA256: `9ed480f4dcb0fe6151ad239c3e05174ce443a81ea84aed8e2777cb9baa04e39d`

## Verdict

**SEAL V2 IS BLOCKED AS A COMPLETE SEAL ARTIFACT. A NARROW V3 SUPERSESSION IS REQUIRED.**

The approved scientific preregistration bytes, the Head Researcher approval, the exact-byte scientific co-chair approval, the sealed 4F0 cohort, and the accepted runner remain valid and unchanged. This decision does not reopen the scientific design.

Seal V2 successfully repairs the Seal V1 tier-label defect and materially strengthens the verifier. The remaining defect is narrower: Binding 8 contains a normative pre-run implementation condition that is not itself derived from or checked against its authoritative Head Researcher source bytes.

No Task 4F1 execution authorization may be issued while this defect remains open. Retrieval-quality outcome access remains FORBIDDEN.

## What Seal V2 correctly repaired

The following repairs are accepted:

1. Binding 2 is normative at the sealed cohort file-digest level; the structural summary is recomputed from the CSV.
2. The exact tier set is constrained to `{100K, 500K, 1M, 10M}`.
3. Question counts, archive counts, zero-compression counts and excluded archives are recomputed and compared field-by-field.
4. Binding 7 is re-extracted from §8 of the approved preregistration and compared as an exact four-item list, with the source-section digest checked.
5. Binding 8's preregistered exact-rational rule is re-extracted from §6 and tied to the section-6 digest.
6. Bindings 4–6 fail closed when their named commits are not locally available for verification.
7. Seal V1 is preserved byte-unchanged as a historical defective artifact.
8. The negative-control suite mutates the historical V1 defect and multiple other sealed facts and requires BLOCKED behavior.
9. V7 remains provenance only and `bound_as_prerequisite` remains false.
10. The outcome boundary remains all zero / all false.

These are substantive improvements and are not being reopened by this decision.

## D1 — Binding 8 still contains an unchecked normative condition

Seal V2 Binding 8 contains:

`condition = "Before any run authorization, the outcome-analysis implementation must honour the preregistered exact-rational sign rule for D_t rather than classify the sign from a rounded or floating-point aggregate."`

The authoritative Head Researcher re-review artifact at:

- branch `hr/rereview-t4f1-prereg-2026-09-04`
- commit `19d9cbbfcbc48f80dc63ac179f2aa67e7eed490d`
- file `docs/v52/task4f1/T4F1_PREREG_REREVIEW_DECISION_2026-09-04.md`
- SHA256 `8795abc7b58b3bae8f2333ba630f95642e9d2e653a31478d221ceb9d71272f3f`

states the implementation note as:

`before any run authorization, the outcome-analysis implementation must honor this exact-rational rule rather than classify the sign from a rounded or floating aggregate.`

Seal V2's condition is a faithful paraphrase in meaning, but it is not an exact byte-derived value. It changes wording (`honor` → `honour`, `this exact-rational rule` → `the preregistered exact-rational sign rule for D_t`, `floating aggregate` → `floating-point aggregate`).

A normative condition that claims byte-derived sealing should not be hand-restated when its authoritative source already exists as a hash-bound artifact.

## D2 — The builder hard-codes the condition instead of extracting it

`tools/build_preregistration_seal_v2.py` extracts the §6 preregistered rule from the approved draft, but the separate Binding-8 `condition` field is a hard-coded string.

Therefore the builder's statement that every sealed value is derived from bytes is still too strong for Binding 8.

## D3 — The verifier never checks the Binding-8 `condition` field

`tools/verify_preregistration_seal.py` checks:

- the section-6 digest;
- that `preregistered_rule_verbatim` appears in §6;
- that Binding 8's origin-artifact digest equals Binding 4's digest.

It never reads or compares `b8["condition"]`.

Therefore the following mutation would still pass the current Binding-8 checks, provided every other field remains unchanged:

`condition = "Before any run authorization, classify D_t from a rounded floating-point aggregate."`

That would invert the normative implementation requirement while leaving the verifier green.

This is the load-bearing defect.

## D4 — The negative suite does not test this gap

`tools/test_verify_preregistration_seal.py` mutates `preregistered_rule_verbatim` and the origin-artifact digest, but does not mutate Binding 8's separate `condition` field.

Thus the 16/16 result is valid for the tested controls, but it does not cover this missing comparison.

## Required repair — V3, no generalized scanner

Do not modify Seal V1 or Seal V2. Preserve both and their sidecars byte-unchanged as historical artifacts.

Prepare a new additive Seal V3 that supersedes Seal V2 and binds the same approved scientific preregistration bytes.

Minimal required design:

1. Keep the accepted V2 repairs unchanged.
2. Treat the authoritative HR implementation note as a byte-derived source fragment, not as a hand-written paraphrase.
3. In the V3 builder:
   - read the HR re-review artifact from its exact named commit;
   - extract the exact implementation-note sentence or paragraph from the A2 section;
   - store that exact text as `implementation_condition_verbatim`;
   - store a digest of the extracted source fragment;
   - do not hard-code an alternative wording.
4. In the V3 verifier:
   - fetch/read the HR re-review artifact bytes;
   - re-extract the same source fragment;
   - compare the extracted text exactly to `implementation_condition_verbatim`;
   - recompute and compare the source-fragment digest;
   - retain the independent §6 exact-rational rule verification.
5. In the negative-control suite add at minimum:
   - mutate `implementation_condition_verbatim` to permit rounded floating classification → must BLOCK;
   - mutate its source-fragment digest → must BLOCK;
   - mutate the HR source commit/path to unavailable or wrong bytes → must BLOCK.
6. Do not create a generalized scanner. These checks are specific to Binding 8 and its named authoritative bytes.
7. V7 must remain `bound_as_prerequisite: false`.
8. The outcome boundary must remain all zero / all false.
9. Do not modify the approved preregistration draft, cohort, runner, or either scientific approval artifact.

No fresh scientific HR/co-chair review is required because no scientific byte is changing.

## State until V3 is independently verified

- approved scientific preregistration draft: VALID + FROZEN
- Head Researcher scientific approval: VALID
- exact-byte co-chair approval: VALID
- Seal V1: BLOCKED / historical defective artifact
- Seal V2: BLOCKED / historical partial repair
- science sealing gate: narrowly reopened for Binding-8 seal/verifier repair
- V7 execution-package audit: separate and unprejudged
- Task 4F1 run: BLOCKED
- production authorization: NONE
- HMAC key: not set / not inspected
- retrieval-quality outcome access: FORBIDDEN

## Outcome boundary

This decision performs no Task 4F1 run or finalize operation, constructs no production authorization, sets or inspects no HMAC key, performs no BEAM retrieval, and accesses no retrieval-quality outcome.
