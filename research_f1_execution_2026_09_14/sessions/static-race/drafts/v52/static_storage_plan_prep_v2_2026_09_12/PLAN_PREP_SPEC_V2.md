# V52 static-storage PLAN-prep V2 specification

Status: **DESIGN PREP / NOT AN ACTUAL PLAN / NOT EXECUTABLE / NOT AUTHORIZED**.

Parent audited bytes: `94056a38443af112d2d3d82003324f6f5e1fa774` (`REQUEST_CHANGES`). Parent inventory V2: `552088ae8907b13d0dcf44dfc26c0a2389503125`.

## Unchanged scientific/accounting rules

- Binding cap object: `marginal_persistent_bytes_per_vector <= 12`.
- Required per-vector code/norm/scale/correction/ID/offset/metadata/lookup state is inside the cap.
- Shared state is separate and contributes only to effective persistent cost under verified sharing populations.
- `code_bytes_per_vector`, marginal persistent cost and effective persistent cost remain distinct.
- UNKNOWN never becomes zero.
- Missing fitted state is not reconstructed by raw-corpus refit.
- One actual plan contains one benchmark, one configuration and one serialization format.
- Task4F1 remains SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN.

## Capacity-safe panel

The full archive roster remains in the primary add-one estimand: every archive receives `(N_i,q=1)`. Only lexicographic first/last sentinels receive `(N_i,q=8)` and the fixed q=1 staircase at `0,1,31,32,33,63,64,65,255,256,257,1023,1024,1025`.

Maximum explicit population rows are 1000 for LongMemEval and 80 for LoCoMo, so the existing reviewed schema-1 entity cap is not changed.

## Companion binding records

Schema-1 remains the declaration/coverage guard. The actual run package additionally contains two externally frozen companion records:

1. `FIXTURE_BINDINGS.json`: locator, byte length, SHA256, fixture content schema and fixed operation-section mapping for every plan fixture.
2. `PHYSICAL_COPY_BINDINGS.json`: locator, source byte length, artifact SHA256 and exact denominator derivation rule for every plan physical copy.

Both companion files have their own raw SHA256 recorded in the external freeze record. Their rosters must exactly equal the plan fixture/physical-copy rosters.

## Fixture artifact contract

A fixture artifact is synthetic JSON with top-level sections `schema`, `transform`, `id_mapping`, `corruption`. Its entire raw byte sequence is hash-bound. The operation map is fixed as TRANSFORM->transform, ID_MAPPING->id_mapping and CORRUPT->corruption. Therefore corruption instructions and operation subfixtures cannot be selected after measurement.

Before callback dispatch, `storage_adapter_preflight.py` recomputes companion-file hashes, fixture raw length/hash, content schema and operation mapping. Mismatch stops the dispatch.

## Physical-copy contract

The schema-1 `artifact_sha256` remains the source-artifact identity. The companion record supplies its locator and source byte length. Snapshot serializer byte lengths are observations and are not predeclared as known results.

`sharing_denominator_rule` is fixed to `POPULATION_COUNT`. For each schema-1 `population_id` referenced by the copy, `D_k` is exactly that frozen population row's integer `count`. The preflight exports the derived `D_k_by_population` map; no second manually entered denominator is allowed.

## Required dispatch order

A future runner may call the existing schema-1 `guarded_probe` only after:

1. external freeze identities are checked;
2. schema-1 plan/contract validation succeeds;
3. companion binding preflight succeeds for the exact fixture and physical-copy rosters;
4. the adapter receives only the verified fixture/source identities from that preflight.

The preflight layer is not evidence that the later adapter performed the declared operation correctly. REMOVE/RESTORE/CORRUPT functional controls and real byte accounting remain future adapter obligations.

## Current status

The V2 repair resolves the three PLAN-prep interface contradictions at design/preflight level only. It does not resolve the underlying fitted-state UNKNOWNs, create `MEASUREMENT_PLAN.json`, choose real serialization bytes, measure any storage, or prove <=12.