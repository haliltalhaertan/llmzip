[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# V10 implementer test receipt

Status: **IMPLEMENTER TEST RECEIPT ONLY — NOT INDEPENDENT REVIEW**.

## V10 suite, default loader (repair)

Command (from `drafts/v52/static_storage_integration_v10_2026_09_13`):

`python3 -B -m unittest test_consumption_gate_v10`

Observed, 5 consecutive runs: 13 tests, 13 PASS, 0 failure, 0 error
(~0.5 s per run). Coverage: 5 parity tests, 12 healthy rejections,
12 rejections under deterministic concurrent poison publication,
2 concurrent valid chain loads under poison, static ambient poison,
exception restoration under overlap, 3x repeated fresh_snapshot rerun
count, exact sys.modules restoration, V9 bypass documentation.

## V10 suite against frozen V9 (defect evidence)

Command: `V52_LOADER_UNDER_TEST=v9 python3 -B -m unittest test_consumption_gate_v10`

Observed: 13 tests, 11 PASS, 2 FAIL, 0 error. Failures are exactly the two
interference tests (`test_twelve_rejections_hold_under_concurrent_poison`,
`test_two_concurrent_valid_chain_loads`); `test_v9_binds_concurrent_poison_silently`
passes. This is the required fail-on-V9 / pass-on-repair pair.

## Existing suites (unmodified, rerun here)

- `drafts/v52/static_storage_integration_v7_2026_09_13`:
  `python3 -B -m unittest test_storage_semantic_gate_v7` — 8 tests, OK.
- `drafts/v52/static_storage_integration_v8_2026_09_13`:
  `python3 -B -m unittest test_storage_semantic_gate_v8` — 7 tests, OK.
- `drafts/v52/static_storage_integration_v9_2026_09_13`:
  `python3 -B -m unittest test_consumption_gate_v9` — 7 tests, OK.

Python 3.14.4. `python -B` throughout (no `.pyc` written for test runs).

No storage measurement, retrieval, model fit, Task4F1 outcome access, HMAC,
seal, finalize, or run occurred.
