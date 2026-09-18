[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# V10 integration test receipt (implementer-run, not independent review)

Python 3.14.4, `python -B` throughout (no `.pyc`). No storage measurement,
retrieval, model fit, Task4F1 outcome access, HMAC, seal, finalize, or run.
Historical frozen receipts untouched; this file and `RECEIPT_V10.json`
(next directory) are the only new evidence files.

## 1. Frozen suites, unchanged (commands from each directory)

- `static_storage_integration_v7_2026_09_13`:
  `python3 -B -m unittest test_storage_semantic_gate_v7`
  → Ran 8 tests, OK. exit 0. skips 0.
- `static_storage_integration_v8_2026_09_13`:
  `python3 -B -m unittest test_storage_semantic_gate_v8`
  → Ran 7 tests, OK. exit 0. skips 0.
- `static_storage_integration_v9_2026_09_13`:
  `python3 -B -m unittest test_consumption_gate_v9`
  → Ran 7 tests, OK. exit 0. skips 0.

## 2. V10 component suites (from `static_storage_integration_v10_2026_09_13`)

- `python3 -B -m unittest test_denominator_integrity_v10`
  → Ran 18 tests, OK. exit 0. skips 0.
- `python3 -B -m unittest test_consumption_gate_v10`, 5 consecutive runs
  → Ran 13 tests, OK each time (0.7–1.0 s per run). exit 0. skips 0.
- `V52_LOADER_UNDER_TEST=v9 python3 -B -m unittest
  test_consumption_gate_v10` → Ran 13 tests, FAILED (failures=2), exit 1.
  Exactly the two expected interference failures (fail-on-V9 / pass-on-repair):
  `test_two_concurrent_valid_chain_loads`,
  `test_twelve_rejections_hold_under_concurrent_poison`.

## 3. Integrated suite (new, real entrypoint, no stubs on acceptance path)

- `python3 -B -m unittest test_static_storage_preflight_v10`
  → Ran 12 tests, OK. exit 0. skips 0.
  Acceptance: 940 DISTINCT physical copies / 470 archives via the real
  `preflight_longmemeval_v10` on temp files → `logical_total_vectors()
  == 231606`, `naive_copy_total_vectors() == 463212`, 940
  `LogicalDenominatorRow`s, 940 unique copy ids, 470 archives, pairs share
  one N_i with distinct copy ids.

## 4. Adversarial matrix (hardened `run_matrix.py` → `RECEIPT_V10.json`)

- `python3 -B run_matrix.py` (from
  `static_storage_security_regression_2026_09_13`) → exit 0,
  verdict `MATRIX-AS-EXPECTED`, surprises `[]`.
- New suite (7 tests) per target:
  - `v9` (gate `a5c98065…092e66dc6`, fn `preflight_longmemeval_v9`):
    6 pass, 1 FAIL (`test_ambient_hashlib_substitution_is_refused`,
    expected). returncode 1.
  - `variant-retained-snapshot` (gate `a195bc8c…e890ee16ac`):
    FAIL exactly `test_ambient_hashlib_substitution_is_refused` +
    `test_consumption_revalidates_after_corruption` (expected; proves
    suite sensitivity to the retained-snapshot class). returncode 1.
  - `variant-unsafe-loader` (gate `59c0d0d6…b572af0ead1b`):
    FAIL exactly `test_ambient_hashlib_substitution_is_refused` +
    `test_ambient_sysmodules_cannot_substitute_code` (expected; proves
    suite sensitivity to the unsafe-loader class). returncode 1.
  - `integrated-v10` (gate `f84e7db8…f80200be7428`, fn
    `preflight_longmemeval_v10`): 7/7 pass, INCLUDING the ambient-hashlib
    protection V9 lacks. returncode 0.
- Old frozen suite (7 tests) per target: 7/7 `pass` on ALL four targets
  (returncode 0), reproducing the documented blindness (both broken
  variants pass the old suite) and proving the integrated gate keeps the
  old contract.
- Negative controls are the FAIL rows above: they fail by design and are
  stated here, not counted as passes. Full stdout/stderr, exit codes, and
  per-target SHAs are embedded in `RECEIPT_V10.json`.

## 5. Unresolved failures / scope exceptions

None open. The ambient-hashlib item is fixed in-model (see disposition);
no test was silently dropped; no BLOCKED/CONDITIONAL items remain for
coordinator review.
