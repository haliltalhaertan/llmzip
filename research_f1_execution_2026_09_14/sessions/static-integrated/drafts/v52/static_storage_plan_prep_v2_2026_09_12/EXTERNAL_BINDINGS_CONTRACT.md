# V52 external bindings contract

Status: DESIGN CANDIDATE / NOT EXECUTABLE / NO MEASUREMENT AUTHORIZATION.

Schema-1 remains byte-unchanged. Two hash-bound companion records supply information that schema-1 does not carry.

## Fixture bindings

`FIXTURE_BINDINGS.json` contains one row per schema-1 fixture id with exact fields:

`fixture_id`, `relative_path`, `byte_length`, `sha256`, `content_schema`, `operation_sections`.

Rules:
- `sha256` must equal the fixture SHA256 declared in the plan.
- `relative_path` is resolved below the bindings file directory; absolute paths and `..` are rejected.
- raw file length and SHA256 are recomputed before callback dispatch.
- `content_schema` is `V52_SYNTHETIC_FIXTURE_BUNDLE_V1`.
- `operation_sections` is exactly `{"TRANSFORM":"transform","ID_MAPPING":"id_mapping","CORRUPT":"corruption"}`.
- the fixture artifact is JSON with top-level `schema`, `transform`, `id_mapping`, `corruption`; the artifact hash freezes all literal fixture bytes and corruption instructions.

A fixture mismatch blocks dispatch. The future adapter receives only the already verified fixture snapshot or an identity derived from it; it may not silently reopen a different fixture.

## Physical-copy bindings

`PHYSICAL_COPY_BINDINGS.json` contains one row per schema-1 physical copy id with exact fields:

`physical_copy_id`, `physical_locator`, `source_raw_byte_length`, `artifact_sha256`, `sharing_denominator_rule`.

Rules:
- `artifact_sha256` must equal schema-1 `physical_copies[].artifact_sha256`.
- `physical_locator` identifies the pre-existing source artifact; its raw bytes are checked before dispatch.
- `source_raw_byte_length` is the source artifact length, not a predeclared measurement result for N or N+q snapshots.
- `sharing_denominator_rule` is exactly `POPULATION_COUNT`.
- for each referenced `population_id`, `D_k` is derived as that frozen population record's integer `count`; the preflight receipt exports the derived map.

This avoids hand-entering a second denominator that could disagree with the plan while still making D_k deterministic and auditable.

## Freeze record

Before any callback, a separate freeze record must bind raw SHA256 values for the plan, contract, both companion records, adapter/preflight code and every referenced fixture/source artifact. Changing any of those bytes creates a new plan package identity.

No companion record may convert UNKNOWN state to zero bytes or reconstruct missing fitted state from raw corpus.