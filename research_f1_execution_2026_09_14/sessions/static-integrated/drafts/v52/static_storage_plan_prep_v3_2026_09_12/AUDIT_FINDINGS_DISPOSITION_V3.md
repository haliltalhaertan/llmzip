# V52 static-storage PLAN-prep V3 — audit findings disposition

Status: **REPAIR CANDIDATE / NOT INDEPENDENTLY AUDITED / NOT EXECUTABLE / NO MEASUREMENT AUTHORIZATION**.

Parent audited V2 candidate: `ecd839b6519be9e56d3ead88c4bab8f7b30ff7b3`.
Independent audit: `audit/v52-static-storage-plan-prep-v2-independent-2026-09-12` @ `11654538c9aca798a34368cfb5e0874420b10889`, verdict `REQUEST_CHANGES`.
Task4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.

## PLANPREP2-AUD-001 — authenticated content vs mutable paths

Accepted. V2 authenticated artifact bytes but returned `artifact_path`, allowing a later consumer to reopen a mutable path.

V3 returns frozen dataclasses containing immutable authenticated `raw_bytes` for fixtures and physical source artifacts. Original locators are preflight-only discovery inputs and are not returned as the authority for later consumption. A future real adapter MUST consume these authenticated bytes. If a third-party library requires a filesystem path, the adapter must materialize a temporary staging object from the authenticated bytes and consume that staged object; reopening the original locator is forbidden. The real adapter integration remains OPEN and must be independently audited.

Operational safety cap: V3 currently refuses an individual artifact above 64 MiB. Such refusal means `NOT_READY`; it is not absence, zero bytes, or negative evidence about the method. If a required real artifact exceeds this cap, a separately reviewed streaming/staging design is required before measurement.

## PLANPREP2-AUD-002 — weak/ambiguous JSON validation

Accepted. V2 used ordinary `json.loads`, so duplicate keys/nonfinite constants and underspecified sub-sections were insufficiently controlled.

V3:
- rejects duplicate JSON keys;
- rejects nonfinite constants;
- bounds JSON depth, entity count and string/numeric domains;
- requires exact fields for companion records;
- requires fixture binding schema version 3;
- requires exact consumer mapping `TRANSFORM -> transform`, `ID_MAPPING -> id_mapping`, `CORRUPT -> corruption`;
- requires exact fixture content schema `V52_SYNTHETIC_FIXTURE_BUNDLE_V3`;
- requires one transform UTF-8 input;
- requires at least two unique synthetic ID-mapping rows with unique logical IDs and offsets;
- requires an exact single-byte XOR corruption method.

This is fixture/preflight validation only. It does not prove a future real adapter applies the operations faithfully.

## PLANPREP2-AUD-003 — zero sharing denominator

Accepted. `N=0` BEFORE is a mandatory diagnostic snapshot and cannot carry a positive amortization denominator.

V3 maps population count zero to:

`("population_id", "EMPTY_NO_AMORTIZATION", None)`

and maps positive counts to:

`("population_id", "POSITIVE", D_k)`.

The empty snapshot may report absolute persistent bytes but MUST NOT compute `shared_bytes / 0` or an effective B/vector value. Only `POSITIVE` states may enter amortization.

## Capacity repair retained

The V2 capacity repair remains unchanged: all archives retain binding `(N_i, q=1)` probes; only lexicographic first/last sentinels receive `q=8` and the fixed staircase. LongMemEval remains 500 probes / 1000 population rows; LoCoMo 40 / 80, within schema-1 population capacity.

## Current boundary

No literal actual `MEASUREMENT_PLAN.json` is generated here. No fitted state is reconstructed. No storage bytes are measured. No <=12 claim is made. No retrieval/query/gold/outcome access is authorized.
