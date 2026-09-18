[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# V10 integration disposition — one public preflight over the hardened chain

Status: **REPAIR CANDIDATE / NOT INDEPENDENTLY AUDITED / NOT FROZEN / NO
MEASUREMENT AUTHORIZATION**. LongMemEval-only. No storage measurement,
retrieval, model fit, run authorization, seal, or Task4F1 outcome access.
Base branch `muse/integrate-static-v10` at `35b5058`; frozen V7/V8/V9 bytes
unmodified (no edits under their directories).

## Sources merged (same object store, no cherry-pick overwrites)

- `35b5058` (this branch HEAD): `consumption_gate_v10.py` + concurrency
  tests — hardened loader ingredient. Untouched.
- `5ff0ab0` (static-denom): `denominator_integrity_v10.py` +
  `test_denominator_integrity_v10.py` copied byte-exact (SHAs
  `b4808b1d…`, `0d8c996a…` verified on copy). Its `V10_DISPOSITION.md` /
  `V10_TEST_RECEIPT.md` / `HASHES.json` preserved under
  `V10_DENOMINATOR_*_src5ff0ab0.*` — the shared
  `static_storage_integration_v10_2026_09_13/` directory name was NOT blind
  cherry-picked and the concurrency report was NOT overwritten.
- `6e764b1` (static-tests): cherry-picked (additive distinct directory
  `static_storage_security_regression_2026_09_13/`), then `run_matrix.py`
  hardened (see below). Its V9-only `RECEIPT.json` left untouched; V10
  evidence goes to `RECEIPT_V10.json`.

## Single public API

`drafts/v52/static_storage_integration_v10_2026_09_13/static_storage_preflight_v10.py`:
`preflight_longmemeval_v10(...)` → `V10Context` (paths/hashes only).
`V10Context` offers fresh V9-shape consumption (`fresh_snapshot()`,
`authoritative_denominators()`) AND the archive-identified layer
(`logical_denominator_rows()` → `LogicalDenominatorRow(archive_id,
physical_copy_id, population_id, n_i)`, `logical_total_vectors()`
unique-by-archive, `naive_copy_total_vectors()` defect demonstrator). No
byte totals exist anywhere; byte numerators are never deduplicated.

The denominator candidate's standalone `V10Context` wrapped the frozen V9
loader (shared-`sys.modules` publication); it is preserved for provenance
but SUPERSEDED — the integrated path runs the same denominator math over
the hardened chain. Pure math is inlined (self-contained gate, no
sibling-import trust dependency); behavioral equivalence with the
candidate file is asserted executably in
`test_static_storage_preflight_v10.py`.

## Hardening across ALL loading paths (V8 chain, parent guard, V7 anchor)

Scoped `__import__` (dependency names never published), whole-transaction
reentrant `_CHAIN_LOCK`, exact-byte SHA256 auth with a digest primitive
captured at trusted import, frozen `hashlib` served to pinned code.
One necessary refinement found during integration: pinned V7/guard sources
use `@dataclass`, which on Python 3.14 resolves
`sys.modules[cls.__module__]` at class-creation time, so the module is
registered under its own unique per-transaction private name for the exec
only (counter-suffixed, never a shared dependency name, removed in
`finally`). Verified: post-consumption `sys.modules` delta is exactly
empty and `v8_runtime`/`v8_snapshot` never appear.

## Threat-model decision (D): ambient-hashlib — IN MODEL, FIXED

Capturing the digest primitive at trusted import and serving the frozen
`hashlib` through the full pinned chain was feasible, so the
`test_ambient_hashlib_substitution_is_refused` protection now PASSES on the
integrated gate (matrix: integrated-v10 7/7, old suite 7/7). No
BLOCKED/CONDITIONAL scope exception. Residual assumption, stated openly:
this module must itself be imported before any in-process mutator runs —
the same trust assumption the pinned SHA constants already require. The
gate still disclaims a broader arbitrary same-process code attacker.

## Contract note (A): no adaptation was required

The guard's copy inventory is keyed by (archive, config, format, item) as
a SET plus distinct `artifact_identity` per copy, with a comment
explicitly permitting distinct physical identities ("two actual file
copies"); V7 emits one denominator row per plan copy bound to the single
authoritative BEFORE population. The acceptance fixture (940 DISTINCT
copy ids, same coverage, distinct identities/bytes/digests) is therefore a
legitimate plan the contract accepts — nothing was weakened to fake
security, and the same-id duplicate remains refused (separate test).

## run_matrix hardening (C)

Fail-closed: expected-fail entries must outcome exactly `fail`; roster
membership is exact (missing/extra/dupe-run/unparsed/skip/error =
surprise); crashed/unparsed children = surprise; old suite must be exactly
its 7 tests all `pass` on every target. Original per-target expectations
preserved verbatim; `integrated-v10` added with an empty expected-fail set.
Full stdout/stderr, exit codes, and target SHAs are recorded in
`RECEIPT_V10.json`.
