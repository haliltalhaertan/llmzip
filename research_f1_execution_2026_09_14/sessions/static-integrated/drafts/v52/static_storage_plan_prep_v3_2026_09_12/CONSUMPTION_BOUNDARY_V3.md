# V52 static-storage V3 authenticated-consumption boundary

Status: **DESIGN CONTRACT ONLY / NOT IMPLEMENTED IN A REAL ADAPTER / NO RUN AUTHORIZATION**.

The execution order for any future real storage adapter is fixed as follows:

1. `measurement_plan_guard.load_plan(...)` validates the exact externally frozen schema-1 plan and contract SHA256.
2. V3 `preflight(...)` authenticates the same plan SHA256 plus fixture/physical companion records and their referenced artifact bytes.
3. Only the returned `VerifiedBindings` object may cross into the future adapter measurement callback.
4. The adapter consumes `VerifiedFixture.raw_bytes` and `VerifiedPhysicalCopy.raw_bytes`; it must not reopen the original companion locator as authority.
5. If a third-party loader requires a path, the adapter may materialize an ephemeral object from the authenticated bytes, use that object in the same call, and discard it. The original source locator is never reopened to recover bytes after authentication.

The current repository does not yet contain that real adapter integration. Therefore V3 can close the design-level mutable-path contradiction but cannot claim runtime integration PASS.

## Fixture bundle V3

Each bound fixture artifact is exact JSON with these fields only:

- `schema = V52_SYNTHETIC_FIXTURE_BUNDLE_V3`
- `transform = {input_utf8}`
- `id_mapping = {rows}` where rows contain exactly `{logical_id, offset, payload_utf8}` and at least two rows with unique IDs and offsets
- `corruption = {strategy, byte_offset, xor_mask}` with `strategy = XOR_SINGLE_BYTE`

The companion record maps consumers exactly:

- `TRANSFORM -> transform`
- `ID_MAPPING -> id_mapping`
- `CORRUPT -> corruption`

This mapping identifies which frozen fixture section each operation/control consumes. It does not replace the parent plan controls.

## Physical-source binding

Each physical-copy companion record binds:

- physical copy ID;
- preflight-only source locator;
- source raw byte length;
- source SHA256 equal to the plan's `artifact_sha256`;
- `sharing_denominator_rule = POPULATION_COUNT`.

After successful authentication, only raw bytes plus immutable identity metadata are authoritative.

## Empty populations

For `population.count = 0`, denominator state is `EMPTY_NO_AMORTIZATION` and `D_k = None`. Absolute package bytes may still be observed at N=0, but no effective bytes/vector division is legal. Positive populations carry `POSITIVE, D_k=count`.

## Fail closed

Any hash mismatch, duplicate key, nonfinite JSON constant, extra/missing exact field, companion coverage mismatch, path escape, artifact size mismatch, fixture schema mismatch or unsupported denominator rule stops before the future adapter callback. A refusal means measurement NOT_READY, not a scientific result.
