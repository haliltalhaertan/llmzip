# V52 static-storage PLAN-prep audit disposition

Status: **REPAIR CANDIDATE / NOT INDEPENDENTLY RE-AUDITED / NOT EXECUTABLE / NO MEASUREMENT AUTHORIZATION**.

Exact audited parent: `94056a38443af112d2d3d82003324f6f5e1fa774`.
Independent Drive audit verdict: `REQUEST_CHANGES`.
Task4F1 remains **SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN**.

## PLANPREP-AUD-001 — ACCEPTED

The old policy produced 968 LongMemEval probes and therefore 1,936 explicit BEFORE/AFTER population rows, while schema 1 caps each entity array at 1,024. The repair does **not** raise the reviewed guard cap.

Revised outcome-independent panel:
- every frozen archive: `(N_i, q=1)`;
- lexicographically first and last archive only: `(N_i, q=8)` batch diagnostic;
- the same two sentinels only: `q=1` at `N={0,1,31,32,33,63,64,65,255,256,257,1023,1024,1025}`;
- exact duplicate `(archive_id,N,q)` keys are deduplicated before freeze and recorded.

LongMemEval maximum is `470 + 2 + 28 = 500` probes and 1,000 population rows. LoCoMo maximum is `10 + 2 + 28 = 40` probes and 80 population rows. Both fit schema-1 without changing the full-archive add-one estimand. q=8 is explicitly secondary diagnostic, not required on every archive.

## PLANPREP-AUD-002 — ACCEPTED

Schema-1 fixture rows bind only fixture id/kind/SHA256/generator identity and the reviewed guard intentionally opens no declared fixture path. Therefore fixture byte verification is moved to a separately hash-bound **external fixture binding record** plus a real-adapter preflight that must execute before any guarded callback.

Each fixture binding records locator, raw byte length, SHA256, content schema and fixed operation-section mapping. The referenced fixture artifact itself contains the TRANSFORM payload, ID_MAPPING toy table and CORRUPT instructions; the artifact SHA256 freezes all of them. The preflight opens the bytes, recomputes length/hash, validates the declared sections and returns the verified fixture snapshot to the future adapter. A plan/fixture binding mismatch is blocking.

## PLANPREP-AUD-003 — ACCEPTED WITH DESIGN CORRECTION

The prior prep over-specified `raw_byte_length` and `D_k` as literal fields inside schema-1 physical-copy rows, where those fields do not exist. The repair uses a separately hash-bound **physical-copy binding record**.

For each schema-1 `physical_copy.id`, the external record binds:
- `physical_locator`;
- `source_raw_byte_length` for the pre-existing source artifact identified by `artifact_sha256`;
- the same artifact SHA256;
- `sharing_denominator_rule = POPULATION_COUNT`.

`D_k` is therefore not an unbound guess and is not redundantly hand-entered: for each referenced `population_id`, the exact denominator is derived from that frozen population row's `count`. The future adapter must emit this derived map in its preflight receipt. Snapshot serializer byte lengths remain measurement outputs; they are **not** predeclared as if already known.

## External freeze requirement

Before any actual probe callback, an external freeze record must bind exact raw SHA256 values for:
1. the schema-1 plan;
2. the reviewed contract;
3. fixture bindings record;
4. physical-copy bindings record;
5. adapter/preflight implementation;
6. every fixture/source artifact referenced by those records.

This repair creates no actual plan, no fitted-state recovery, no byte measurement and no <=12 verdict.