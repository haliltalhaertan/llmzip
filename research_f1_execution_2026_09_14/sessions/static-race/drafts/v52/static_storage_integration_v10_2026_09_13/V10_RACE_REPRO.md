[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# V10 race reproduction against frozen V9 (exact)

Target: `drafts/v52/static_storage_integration_v9_2026_09_13/consumption_gate_v9.py`
at `b300cbf` (unmodified). Ordinary thread concurrency; no attacker model
beyond a concurrent in-process publisher of the kind V8 test setup leaves
behind (`import v8_runtime` at test top level).

## Mechanism

1. Worker thread calls the public boundary
   `preflight_longmemeval_v9(...)` with an invalid input.
2. V9 loads the pinned chain: exec runtime, exec snapshot (publishes
   `sys.modules["v8_runtime"]`), restore, exec gate (publishes
   `sys.modules["v8_runtime"]` and `["v8_snapshot"]`), restore.
3. Test instrumentation wraps `builtins.exec` and, exactly at the gate
   exec entry (identified by loader namespace prefix plus the pinned gate
   filename — no sleeps), signals a publisher thread and waits for it.
4. The publisher sets `sys.modules["v8_runtime"]` to a permissive fake
   (`need`/`digest` no-ops, canned `v7`/`guard`/`v6` chain feeding the real
   snapshot freezer) and releases the worker.
5. The gate source's `import v8_runtime as rt` binds the fake. All plan /
   hash / binding checks pass vacuously; the real snapshot freezer seals an
   attacker-shaped empty binding set. The public call returns a context
   instead of raising. V9's `finally` then restores `sys.modules`, hiding
   the evidence.

## Observed

- Scratch probe (throwaway, `/tmp`): 5/5 invalid inputs bypassed with
  interference; 5/5 rejected without it.
- Maintained suite `test_consumption_gate_v10.py` with
  `V52_LOADER_UNDER_TEST=v9`: `test_twelve_rejections_hold_under_concurrent_poison`
  and `test_two_concurrent_valid_chain_loads` FAIL (each exercised rejection
  flips to silent acceptance / each loaded gate is counterfeit), while
  `test_v9_binds_concurrent_poison_silently` passes as the pinned
  demonstration.
- Same suite with the default loader (`v10`): 13/13 pass, 5/5 repeat runs —
  the interference lands but is ignored by the private binding.

## Reproduce

From the V10 directory:

`V52_LOADER_UNDER_TEST=v9 python3 -B -m unittest test_consumption_gate_v10`

Expect `FAILED (failures=2)` with the two interference tests failing and
the remaining 11 passing. Default (unset) run: `OK`, 13 tests.

No storage measurement, retrieval, model fit, Task4F1 outcome access, HMAC,
seal, finalize, or run occurred.
