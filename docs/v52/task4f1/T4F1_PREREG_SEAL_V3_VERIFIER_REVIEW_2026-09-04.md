# V52 Task 4F1 — Head Researcher Review of Preregistration Seal V3

Date: 2026-09-04
Role: Head Researcher / final scientific approval authority
Reviewed main: `bae7be2e8f3f2497d362194fdd93f7a5abaee595`
Reviewed Seal V3: `docs/v52/task4f1/TASK4F1_PREREGISTRATION_SEAL_V3_2026-09-04.json`
Declared Seal V3 SHA256: `e906c6d2b68b103c6c21906cbdf44acba10e31b7e5e17ffd2c7d1bbfb7a95cf4`

## Verdict

**SEAL V3 CONTENT: SUBSTANTIVELY ACCEPTED. FINAL VERIFIER ACCEPTANCE: ONE NARROW HARDENING REQUIRED. NO SEAL V4 IS REQUIRED IF THE V3 BYTES REMAIN UNCHANGED.**

The load-bearing Seal V2 Binding-8 defect is repaired in V3. The authoritative implementation condition is no longer a hand-written paraphrase. The builder reads the Head Researcher re-review artifact from exact commit `19d9cbbfcbc48f80dc63ac179f2aa67e7eed490d`, extracts the paragraph beginning `Implementation note, not a defect in this preregistration:`, stores that paragraph verbatim, and stores a digest of the exact extracted fragment.

The fragment SHA256 was independently recomputed by the Head Researcher from the authoritative paragraph and equals:

`13451be1dd8d05b41521faf64ffd3f7e45a8079edf5baf031986c22ca9778bed`

The V3 verifier independently reloads the HR source bytes, verifies the HR artifact digest, re-extracts the paragraph, requires exact equality with `implementation_condition_verbatim`, and recomputes the fragment digest. It also retains the separate exact Section-6 rule verification. The negative-control suite contains the required V2 escape mutations: inverted implementation condition, wrong fragment digest, unavailable source commit, wrong source path, and an injected extra top-level Binding-8 field.

The prior Seal V1 and Seal V2 files are not modified by the V2-to-V3 commit range. Their preservation remains part of the V3 verifier.

## Remaining verifier-hardening gap

The V3 verifier fixes the **top-level Binding-8 field set** with `BINDING_8_FIELDS`, but it does not verify every value of every field that the allowed schema contains, and it does not close the nested `implementation_condition_source` object by exact field set.

Examples that currently do not participate in a substantive verifier equality check include:

- Binding-8 `type`;
- Binding-8 `owner`;
- Binding-8 `not_a_scientific_amendment`;
- Binding-8 `no_restated_wording`;
- nested `implementation_condition_source.what`;
- nested `implementation_condition_source.branch` as provenance text;
- nested `implementation_condition_source.extraction_rule`.

The present V3 seal carries correct values for these fields, and none changes the authoritative implementation-condition fragment or the preregistered Section-6 rule. Therefore this is **not a defect in the scientific preregistration, not a defect in the actual bound implementation condition, and not a reason to issue Seal V4.** It is a remaining mismatch between the verifier's stated claim and what it actually checks.

In particular, the V3 field `no_restated_wording` says that every text field in the binding is extracted from source bytes and checked by the verifier. That statement is too broad as written: several descriptive/schema fields are fixed metadata rather than extracted source text, and some are not value-checked.

## Required narrow hardening

Keep Seal V3 and its sidecar byte-unchanged.

Patch only the verifier/test layer (plus continuity/state documentation as necessary) so that Binding 8 has a completely explicit verified schema:

1. define the exact allowed field set for `implementation_condition_source` and reject nested extra fields;
2. verify the source `commit`, `path` and `artifact_sha256` exactly as already done;
3. either verify `branch`, `what` and `extraction_rule` against fixed schema constants, or explicitly classify them as non-normative metadata outside the load-bearing comparison;
4. verify top-level `type`, `owner`, `not_a_scientific_amendment` and `no_restated_wording` against fixed expected constants, or remove them from the verifier's load-bearing claim by explicitly treating them as non-normative metadata;
5. add negative controls for at least:
   - changing `owner`;
   - changing `type`;
   - changing nested `extraction_rule`;
   - adding an unexpected nested `implementation_condition_source` field.

Do not build a generalized scanner. These are narrow schema assertions over one already-bound object.

If those checks pass while the Seal V3 blob remains byte-identical, the Head Researcher will accept **Seal V3 itself** as the final scientific preregistration seal. A V4 seal is unnecessary because no V3 load-bearing value needs to change.

## Standing status until the narrow verifier patch is independently checked

- approved scientific draft: `VALID + FROZEN`;
- Head Researcher scientific approval: `VALID`;
- scientific co-chair exact-byte approval: `VALID`;
- Seal V1: `BLOCKED` historical;
- Seal V2: `BLOCKED` historical partial repair;
- Seal V3 content: `SUBSTANTIVELY ACCEPTED`, pending verifier-hardening closure;
- Task 4F1 run: `BLOCKED`;
- production authorization: `NONE`;
- retrieval-quality outcome access: `FORBIDDEN`;
- V7 execution-package audit: separate and unprejudged.

No Task 4F1 outcome was accessed, computed or inferred in this review. No run/finalize invocation was performed, no authorization was constructed and no HMAC key was accessed.
