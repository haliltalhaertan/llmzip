# V52 Task 4F1 — Head Researcher Seal V3 Final Verifier Review

Date: 2026-09-04  
Role: Head Researcher / final scientific approval authority  
Reviewed main: `df9b0f59b898d77673e4d577c0e21465bddada1d`  
Reviewed Seal V3: `docs/v52/task4f1/TASK4F1_PREREGISTRATION_SEAL_V3_2026-09-04.json`  
Declared Seal V3 SHA256: `e906c6d2b68b103c6c21906cbdf44acba10e31b7e5e17ffd2c7d1bbfb7a95cf4`

## Verdict

**SEAL V3 CONTENT REMAINS SUBSTANTIVELY ACCEPTED. FINAL VERIFIER CLOSURE IS [FIXABLE / BLOCKED] PENDING ONE NARROW IDENTITY-AND-EXACTNESS HARDENING.**

Do not create Seal V4. Do not modify Seal V3 or its sidecar. The approved scientific draft, Head Researcher approval, exact-byte co-chair approval, cohort and runner remain unchanged and valid. Task 4F1 execution remains BLOCKED and retrieval-quality outcome access remains FORBIDDEN.

The 2026-09-04 hardening at `df9b0f59...` correctly closes the seven reported Binding-8 metadata escapes: exact top-level and nested field sets are enforced; `owner`, `type`, `no_restated_wording`, `preregistered_rule_source` and nested `what` are digest-pinned; `not_a_scientific_amendment` is required to be true; source branch/commit/path are cross-checked to Binding 4; source artifact digest is checked; and the authoritative implementation-condition paragraph and fragment digest remain exactly verified.

Three remaining verifier-level defects prevent final closure.

## F1 — the Seal V3 verifier does not verify the identity of the seal it is verifying

`tools/verify_preregistration_seal.py` reads `SEAL_PATH` and validates its internal/reference relationships, but it never computes the SHA256 of Seal V3 itself against the committed sidecar or against the approved Seal V3 digest `e906c6d2...`.

It explicitly verifies that superseded Seal V1 and Seal V2 remain byte-unchanged, but does not perform the analogous identity check on the current Seal V3.

`tools/verify_continuity_state.py` currently provides a separate repository-state anchor for Seal V3, which is useful defense in depth, but that does not discharge an artifact verifier's own identity obligation. The seal verifier must establish that the bytes under `SEAL_PATH` are the exact sealed bytes before interpreting them.

### Required repair

Production verification must fail closed unless all of the following hold:

1. `sha256(SEAL_PATH) == e906c6d2b68b103c6c21906cbdf44acba10e31b7e5e17ffd2c7d1bbfb7a95cf4`;
2. the V3 `.sha256` sidecar exists;
3. the sidecar names exactly `TASK4F1_PREREGISTRATION_SEAL_V3_2026-09-04.json`;
4. the sidecar declares exactly the same `e906c6d2...` digest.

Prefer a verifier constant for the accepted V3 digest plus a sidecar cross-check. Reading a mutable sidecar without pinning the accepted digest is weaker.

## F2 — the §6 bound rule is checked as a substring, not as the exact authoritative paragraph

The current verifier accepts `b8["preregistered_rule_verbatim"]` whenever its stripped text appears anywhere inside the verified §6 section. This proves presence, not exact binding.

Therefore a weakened value such as only `**Sign-boundary arithmetic.**` can satisfy the current membership test while no longer carrying the full exact-rational rule.

### Required repair

Independently extract from the approved draft's §6 the paragraph beginning `**Sign-boundary arithmetic.**`, exactly as the V3 builder does, and require:

`b8["preregistered_rule_verbatim"] == extracted_rule_paragraph`

Do not use substring containment as the acceptance condition.

Add a negative control that replaces the bound rule with a strict true substring of the authoritative paragraph; it must BLOCK.

## F3 — the declared extraction rule is only marker-containing, not exact

The verifier currently accepts any `implementation_condition_source.extraction_rule` string containing `repr(IMPL_NOTE_MARKER)`. A materially different descriptive rule can therefore pass if it embeds the marker text.

This does not change the implementation condition actually extracted by code, so it is not a scientific-content defect. It is nevertheless inconsistent with the hardened schema's goal that Binding-8 metadata have no unchecked semantics.

### Required repair

Pin the exact V3 `extraction_rule` value by digest or exact string equality. Add a negative control that changes the rule while preserving the marker substring; it must BLOCK.

## Negative-test architecture requirement

Adding a Seal V3 self-digest check creates a testing trap: if every mutated temporary seal is sent through production `main()`, all field-level negative tests could become trivially green merely because the temporary file no longer hashes to `e906c6d2...`.

Do not accept that as evidence that the inner controls work.

Structure the verifier so that:

- production verification first enforces exact Seal V3 identity, then runs content/source verification;
- field-level negative controls exercise the content/source verification layer directly (or otherwise supply the mutated file's identity in a test-only harness) and assert the intended specific failure;
- separate production negative controls prove that a one-byte Seal V3 mutation, missing sidecar, wrong sidecar digest, and wrong sidecar filename are rejected by the identity layer.

The test suite should therefore preserve two independent claims: (A) the verifier recognizes only the exact sealed V3 bytes in production mode, and (B) the semantic/source checks independently reject their targeted mutations rather than being shadowed by the identity mismatch.

## Accepted facts carried forward

- Seal V3 substantive content remains accepted.
- Exact implementation-condition fragment SHA256 `13451be1dd8d05b41521faf64ffd3f7e45a8079edf5baf031986c22ca9778bed` remains accepted.
- Seal V3 remains byte-unchanged at declared SHA256 `e906c6d2b68b103c6c21906cbdf44acba10e31b7e5e17ffd2c7d1bbfb7a95cf4` according to the committed sidecar and the unchanged-file history from `bae7be2...` to `df9b0f59...`.
- The seven Binding-8 metadata escapes reported in L-037 are correctly hardened in the code reviewed here.
- No new generalized scanner is authorized.
- No Seal V4 is requested.

## Closure condition

Final scientific sealing closure may be recorded on the unchanged Seal V3 once an independently reviewed verifier patch satisfies F1-F3 and the two-layer negative-test architecture above.

Until then:

- scientific draft: `VALID + FROZEN`
- scientific approvals: `VALID`
- Seal V3 substantive bytes: `ACCEPTED / UNCHANGED`
- Seal V3 verifier closure: `BLOCKED — FIXABLE`
- Task 4F1 run: `BLOCKED`
- production authorization: `NONE`
- outcome access: `FORBIDDEN`
- V7 execution audit: separate and unprejudged
