# V52 static-storage PLAN-prep V3

Status: **DESIGN PREP / NOT EXECUTABLE / NOT FROZEN / NO MEASUREMENT AUTHORIZATION**.

Parent repair candidate: `ecd839b6519be9e56d3ead88c4bab8f7b30ff7b3`.
Canonical context observed during preparation: `main@5ec3db60c03edde490374bf9cd7c3e56dd6bcd00`.

V3 changes only the three blocking interface findings from the independent V2 re-audit. It retains the V2 capacity-safe probe policy and all prior storage-accounting boundaries.

## Retained budget semantics

Only `marginal_persistent_bytes_per_vector` is compared with the 12-byte cap. Required per-vector code/norm/scale/correction/ID/offset/metadata/lookup state remains inside the cap. Shared state remains separate and can enter effective cost only under a verified positive sharing denominator.

## Retained panel

- all frozen archives: `(N_i, q=1)`;
- lexicographic first/last archive only: additional `(N_i, q=8)`;
- same two sentinels: q=1 staircase at `N={0,1,31,32,33,63,64,65,255,256,257,1023,1024,1025}`;
- deduplicate identical archive/N/q requests before freeze;
- report all frozen requests/failures.

This yields LongMemEval <=500 probes / <=1000 BEFORE+AFTER populations and LoCoMo <=40 / <=80 under schema-1 limits.

## V3 companion schemas

The schema-1 plan stays unchanged. Before any future callback, the same externally frozen plan SHA256 must pass both:

1. the independently reviewed parent `measurement_plan_guard`;
2. V3 `storage_adapter_preflight_v3.py`.

Fixture bindings use `v52.fixture-bindings`, version 3. Physical bindings use `v52.physical-copy-bindings`, version 3. Both companion files are externally hash-bound before use.

Fixture content schema is `V52_SYNTHETIC_FIXTURE_BUNDLE_V3` with exact transform, multi-row toy ID mapping and corruption-method sections. Duplicate keys, NaN/Infinity, extra fields and coverage mismatches fail closed.

## Authenticated consumption

A successful preflight returns frozen objects containing the authenticated artifact bytes. Later adapter code may consume those bytes, not reopen the original source locator. Any future adapter that violates this boundary fails review.

## Empty population semantics

A zero-count diagnostic population is `EMPTY_NO_AMORTIZATION` and has no D_k. Its absolute persistent bytes may be reported; effective B/vector is undefined at that snapshot. Only positive populations receive numeric D_k.

## Current blockers that remain intentionally open

- actual fitted model/projector artifacts are unresolved for many items;
- actual persistent ID/offset representation is unresolved;
- actual physical copies/sharing populations are unresolved;
- actual serialization package identity is not frozen;
- real adapter/runner integration does not exist;
- external freeze record for a literal plan does not exist.

Therefore V3 does not generate a literal actual plan and cannot initiate storage measurement.

Task4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.
