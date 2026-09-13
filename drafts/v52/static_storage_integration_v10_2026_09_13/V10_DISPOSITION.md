# V52 static-storage V10 — denominator-integrity repair candidate

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Status: **REPAIR CANDIDATE / NOT INDEPENDENTLY AUDITED / NOT FROZEN / NO MEASUREMENT AUTHORIZATION**.

Parent commit: `b300cbf70b158bc075d45e4bfb8e0105a970596b` (V9).

V10 is additive. It does not modify V7/V8/V9, the parent guard, the contract,
or any historical receipt. New files live only in
`drafts/v52/static_storage_integration_v10_2026_09_13/`.

## Defect repaired

Authoritative denominator data is keyed/emitted per physical copy: V9
`authoritative_denominators()` returns `(copy_id, population_id, d_k)`
triples with no archive identity. The plan contract requires physical copies
per archive/config/format/item, so two legitimate copies of one archive each
carry the same frozen N_i and a consumer summing rows counts one logical
archive twice (LongMemEval: 470 archives, total N=231606; doubled copy rows
naive-sum to 463212, making 12 B/vector for one representation appear as 6).
Reproduced through the public V9 surface in
`test_naive_sum_over_v9_public_rows_double_counts_duplicate_copies`, which
passed pre-fix (defect present) and still passes post-fix (defect documented).

## Accounting rule (normative)

V10 accounting rule (LongMemEval-only): the authoritative TOTAL logical
vector denominator is unique-by-archive -- exactly one frozen N_i per
archive_id, summed once. Every physical-copy denominator row must equal the
frozen N_i of its archive; copies of one archive that disagree with each
other or with the frozen N_i reject. Byte numerators are NOT deduplicated:
per-copy/per-representation byte counts remain per-copy, and V10 offers no
byte total, so a one-representation numerator divided by the logical
denominator stays valid while dividing it by a naive per-copy sum is refused
as a labeled error source. Only the logical vector denominator is
unique-by-archive.

The same text ships in code as `denominator_integrity_v10.ACCOUNTING_RULE`.

## API

- `LogicalDenominatorRow(archive_id, physical_copy_id, population_id, n_i)`.
- `enrich_denominator_rows(denominators, copy_to_archive, frozen_n)`:
  attaches archive identity; rejects unknown copies, out-of-roster archives,
  and inconsistent duplicates.
- `deduplicate_logical_total(rows)`: one N_i per archive_id, summed once;
  rejects conflicting N_i within an archive.
- `naive_copy_total(denominators)`: per-copy sum, defect demonstrator only.
- `load_longmemeval_anchor_map()`: frozen 470-archive map, no caller knobs.
- `V10Context` (same six path/hash fields as `V9Context`, no snapshot
  field): `fresh_snapshot()`, `logical_denominator_rows()`,
  `logical_total_vectors()`, `naive_copy_total_vectors()`; every access
  reruns the pinned V9 chain plus pinned plan/anchor cross-checks.
- `preflight_longmemeval_v9`-mirroring `preflight_longmemeval_v10(...)`.
- `labeled_summary(...)`: report string always prefixed with the exact
  `[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
  [DISCLOSE-BEFORE-USE]` labels.

Pinning: V10 executes the exact authenticated bytes of the V9 gate, the
parent guard, and the V7 gate in fresh private namespaces (same technique as
V9), and re-checks plan-vs-anchor agreement on every access.

## Scope

LongMemEval-only. LoCoMo remains blocked pending a separate reviewed anchor
profile. V10 creates no literal actual plan and measures no storage. Task4F1
remains `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.

Still open: independent V10 audit; canonical end-to-end consumption against a
real full-coverage plan plus fixture/physical bindings; the pre-existing V8
open items inherited by reference.
