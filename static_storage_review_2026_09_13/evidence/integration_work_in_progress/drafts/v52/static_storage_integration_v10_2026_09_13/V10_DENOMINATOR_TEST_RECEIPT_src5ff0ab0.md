# V10 implementer test receipt

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Status: **IMPLEMENTER TEST RECEIPT ONLY — NOT INDEPENDENT REVIEW**.

## Pre-fix failure (observed before `denominator_integrity_v10.py` existed)

Command:

`python -B -m unittest -v test_denominator_integrity_v10`
(run in `drafts/v52/static_storage_integration_v10_2026_09_13/`)

Observed:

- 18 tests discovered;
- 1 PASS: `V9DefectDemonstration.test_naive_sum_over_v9_public_rows_double_counts_duplicate_copies`
  (two physical copies of one archive through the public
  `V9Context.authoritative_denominators()` surface yield `(('ca1','pa1',10),
  ('ca2','pa1b',10))` with no archive identity; naive sum 20 vs logical 10;
  120 bytes billed per vector appears as 6 B/vector instead of 12);
- 17 ERROR: every V10 repair test failed with
  `ModuleNotFoundError: No module named 'denominator_integrity_v10'`;
- result line: `FAILED (errors=17)`.

## Post-fix runs (all green, same commands plus historical suites)

1. `python -B -m unittest -v test_denominator_integrity_v10`
   (in `drafts/v52/static_storage_integration_v10_2026_09_13/`)

   Observed: 18 tests discovered; 18 PASS; 0 SKIP; 0 failure; 0 error.

   Executed PASS cases:
   1. V9 defect demonstration through the public V9 surface (naive 20 vs
      logical 10; 12 B/vector appears as 6);
   2. duplicate-copy regression: two copies of one archive enrich with
      `archive_id` and dedup to one N_i (naive 20, logical 10);
   3. conflicting duplicate counts reject;
   4. agreeing duplicates against the wrong frozen N_i reject;
   5. enriched rows with conflicting N_i per archive reject;
   6. copy with no archive binding rejects;
   7. copy bound outside the frozen roster rejects;
   8. ordinary one-copy plan: naive equals logical (30);
   9. canonical 470-archive check: 940 doubled copy rows yield logical
      231606 while the naive per-copy sum is 463212;
   10. no byte-total helper exists and logical rows carry no numerator field;
   11. report labels exact;
   12. labeled summary carries labels, LongMemEval scope, and both totals;
   13. accounting rule states unique-by-archive denominators and
      non-deduplicated numerators;
   14. preflight signature mirrors V9;
   15. anchor loader takes no caller knobs;
   16. context path dedups (logical 10) while naive double-counts (20);
   17. context inconsistent duplicates reject;
   18. context exposes no retained snapshot field.

2. Historical suites (unmodified, rerun on this branch):
   - `drafts/v52/static_storage_contract_2026_09_12`: `python -B -m unittest`
     → 32 tests, OK.
   - `drafts/v52/static_storage_integration_v7_2026_09_13`:
     `python -B -m unittest` → 8 tests, OK
     (6 unit PASS + 2 canonical-repo PASS; anchor file present in checkout).
   - `drafts/v52/static_storage_integration_v8_2026_09_13`:
     `python -B -m unittest` → 7 tests, OK.
   - `drafts/v52/static_storage_integration_v9_2026_09_13`:
     `python -B -m unittest` → 7 tests, OK.

   Total: 32 + 8 + 7 + 7 + 18 = 72 tests, 0 failures, 0 errors.

Historical receipts were not rewritten; this file is the additive V10-only
receipt.

No storage measurement, retrieval, model fit, Task4F1 outcome access, HMAC,
seal, finalize or run occurred.
