# V52 Task 4F1 — Head Researcher Preregistration Seal V1 Defect Decision

Date: 2026-09-04  
Role: Head Researcher / final scientific approval authority  
Reviewed main: `d95ab8ec4d3b6018b188598fb9f1577caeac40d1`  
Reviewed seal: `docs/v52/task4f1/TASK4F1_PREREGISTRATION_SEAL_2026-09-04.json`  
Reviewed seal SHA256 as declared by sidecar: `c9e061951c44d89f9c62af94ee78b37a860fd52081fb0c38d38360511218891b`

## Verdict

**SEAL V1 BLOCKED / SUPERSEDED REQUIRED. THE SCIENTIFIC PREREGISTRATION BYTES AND BOTH SCIENTIFIC APPROVALS REMAIN VALID.**

This is a defect in sealing metadata and in the seal verifier, not a defect in the approved scientific preregistration. Do not modify the approved draft, the sealed 4F0 cohort, the accepted runner, either scientific approval artifact, or any outcome-bearing data.

No Task 4F1 execution authorization may be issued while this seal defect is open. Outcome access remains FORBIDDEN.

## D1 — Binding 2 contains incorrect tier labels

The approved preregistration at SHA256

`5e61898193421a3a18791202668c0974f23d2fb4080a107069e7b7127e35ea44`

defines the four tiers as:

- `100K`: 355 questions, 20 archives, zero-compression denominator 259
- `500K`: 629 questions, 35 archives, zero-compression denominator 461
- `1M`: 553 questions, 31 archives, zero-compression denominator 300
- `10M`: 175 questions, 10 archives, zero-compression denominator 105

Seal V1 instead records, inside binding `2_sealed_4f0_restricted_cohort`:

- `tier_denominators`: `100K:355, 1M:629, 5M:553, 10M:175`
- `ceiling_free_stratum_denominators`: `100K:259, 1M:461, 5M:300, 10M:105`
- `archive_counts`: `100K:20, 1M:35, 5M:31, 10M:10`

Thus `500K` is missing, a nonexistent `5M` tier is introduced, and the 500K/1M labels are shifted. Because these values appear in the seal's normative `bindings` object, this is not merely cosmetic provenance.

## D2 — The verifier does not test the incorrect metadata

`tools/verify_preregistration_seal.py` verifies only the SHA256 of the cohort file for binding 2. It does not recompute and compare:

- the exact tier key set,
- tier question denominators,
- zero-compression (`|gold| <= 3`) denominators,
- archive counts,
- or the excluded-archive set.

Therefore `PREREGISTRATION_SEAL: PASS` does not establish the correctness of the binding-2 structural metadata.

## D3 — Bindings 7 and 8 are not actually re-derived from source bytes

The verifier's current checks are also weaker than its stated claim that every binding is re-derived from bytes:

- Binding 7: it checks only that there are exactly four condition strings. It does not compare those strings against §8 of the approved preregistration.
- Binding 8: it checks only that the `condition` field is non-empty. It does not verify the exact-rational rule against the Head Researcher re-review decision and the approved preregistration's §6 rule.

No evidence currently indicates that the text written in bindings 7 or 8 is wrong. The defect is that the verifier does not establish the claim it says it establishes.

## Required repair — no new generalized scanner

Do **not** build another generalized consistency scanner.

Prepare a **new additive V2 seal** and preserve V1 plus its sidecar unchanged as a historical defective artifact. V2 must explicitly supersede V1 and bind the same approved scientific draft bytes.

Preferred minimal design:

1. Keep binding 2 normative at the cohort-file SHA256 level.
2. Either remove redundant derived cohort dictionaries from the normative binding entirely, or reproduce them with the correct tier labels and make the verifier recompute them directly from the sealed cohort CSV.
3. If structural summaries are retained, the verifier must at minimum assert the exact tier set `{100K, 500K, 1M, 10M}` and recompute the question counts, archive counts, zero-compression counts, and excluded archives from the cohort bytes.
4. Binding 7 must be verified against the exact four §8 conditions in the approved preregistration bytes, not by list length alone.
5. Binding 8 must be verified against its authoritative source bytes, not by non-emptiness alone. The implementation condition remains pre-run and does not become a scientific-draft amendment.
6. Preserve `V7 bound_as_prerequisite: false`.
7. Preserve the all-zero/all-false outcome boundary.
8. Add a SHA256 sidecar for V2.
9. Run the strengthened verifier and require `PASS`.
10. Independently verify the V2 seal artifact and sidecar before continuity records the scientific preregistration as sealed again.

The repair must not rewrite the approved preregistration draft. Because no scientific content is changing, a fresh Head Researcher scientific re-review and fresh co-chair review of the draft are **not** required.

## State until repaired

- Approved scientific preregistration bytes: **VALID AND FROZEN**
- Head Researcher scientific approval: **VALID**
- Exact-byte co-chair approval: **VALID**
- Seal V1 (`c9e06195...`): **BLOCKED AS A SEAL ARTIFACT**
- Science sealing gate: **REOPENED NARROWLY FOR SEAL-METADATA REPAIR**
- V7 execution audit: separate track, still unprejudged
- Task 4F1 run: **BLOCKED**
- Production authorization: **NONE**
- Retrieval-quality outcome access: **FORBIDDEN**

## V7 status observed during this decision

The V7 audit branch remained at:

`16dc61313acd0e9086c852eccb9100023898fd27`

with gate evidence but no final report, gate table, hash manifest, or verdict. This decision takes no position on V7.

## Outcome boundary

This review did not run or finalize Task 4F1, construct an authorization, access or set an HMAC key, perform BEAM retrieval, or access any Task 4F1 retrieval-quality outcome.
