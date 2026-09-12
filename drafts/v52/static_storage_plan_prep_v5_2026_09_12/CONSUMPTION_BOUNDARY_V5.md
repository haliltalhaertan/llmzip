# V52 static-storage V5 authenticated-consumption boundary

Status: **DESIGN CONTRACT ONLY / NOT IMPLEMENTED IN A REAL ADAPTER / NO RUN AUTHORIZATION.**

Supersedes `CONSUMPTION_BOUNDARY_V3.md` for the physical-copy binding record and for the
preflight signature. That file's bytes are unchanged; the V3 text still describes a
five-field physical-copy record at schema version 3, which is no longer what the code
accepts.

## Execution order

1. `measurement_plan_guard.load_plan(plan_path, expected_plan_sha256, contract_path)`
   validates the frozen schema-1 plan and returns its plan and contract digests.
2. `archive_anchor_guard.verify_plan_against_anchor(plan_data, anchor)` anchors every
   `N_i` to a frozen, digest-bound size table and yields ONE denominator per physical
   copy. Without it the effective-cost figures are unanchored; see AUD-001 and AUD-008.
3. V5 `preflight(...)` authenticates the plan, the contract from its own bytes, both
   companion records and every referenced artifact. **All ten arguments are required**,
   including the two digests step 1 returned.
4. Only the returned `VerifiedBindings` may cross into a future adapter callback.
5. The adapter consumes `VerifiedFixture.raw_bytes` / `VerifiedPhysicalCopy.raw_bytes`
   after calling `reverify()`, and never reopens the original locator as authority. A
   third-party loader that needs a path gets an ephemeral object built from the
   authenticated bytes, used in the same call and discarded.

Step 2 is not enforced by step 3. Nothing in this module can tell whether the anchor
guard ran, and V5 still refuses to select among the denominator states it reports.

## Physical-copy binding record — schema version 4

`v52.physical-copy-bindings`, **version 4**, exact fields:

- `physical_copy_id`
- `physical_locator` — preflight-only, relative, below the binding directory
- `source_raw_byte_length`
- `artifact_sha256` — equal to the plan's `artifact_sha256`
- `sharing_denominator_rule` — `POPULATION_COUNT`
- `absence_basis` — a stated non-blank reason when the artifact is zero bytes, otherwise null

V4 added `absence_basis` while leaving the version at 3, so two incompatible field sets
shared one schema name and number. Version 4 exists to separate them; a version-3 record
is now refused rather than silently reinterpreted.

The fixture bundle and the fixture binding record are unchanged from V3.

## Fail closed

Every refusal is a `PreflightError`. A non-regular file, a path escape, a lone surrogate
in a locator, a hash mismatch, a duplicate JSON key, a nonfinite constant, an extra or
missing exact field, a coverage mismatch, an unsupported denominator rule, a corruption
offset outside the artifact, an unexplained zero-byte artifact, two declared artifacts
resolving to one file, an aggregate byte budget overrun, and a guard digest that does not
match all stop before any adapter callback. A refusal means measurement NOT_READY; it is
not a scientific result.

One thing that is not a `PreflightError`: calling `preflight` without the guard digests
is a `TypeError` from the signature itself, which is the stronger failure. It cannot be
called wrongly at all.
