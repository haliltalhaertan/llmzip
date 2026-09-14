# V52 static-storage security regression audit — adversarial pilot

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Base: `b300cbf` (V9). Frozen V7/V8/V9 artifacts were read but never edited;
everything below is additive under
`drafts/v52/static_storage_security_regression_2026_09_13/`.

## 1. Why the broken variants survived the existing tests

Auditors built two deliberately broken gates — one retaining a validated
snapshot, one loading through ambient `sys.modules` — and the V7/V8/V9 tests
stayed green. Inspection of every test and receipt in
`static_storage_integration_v{7,8,9}_2026_09_13/` shows the blindness is
structural, and this pilot reproduces it executably (§4):

1. **The V9 tests mock the function whose behavior they assert.**
   `test_preflight_discards_validation_snapshot` and
   `test_fresh_snapshot_reruns_each_access` replace `v9._fresh_v8` with a
   lambda and count calls. Any variant that preserves the call pattern —
   including one that stashes the real snapshot in a module global and serves
   it from `authoritative_denominators()` — passes. **No V9-era test ever
   calls `authoritative_denominators()`**, the very path a retained snapshot
   would poison (same gap exists in the V8 suite for `refresh()` vs
   `authoritative_denominators()`).
2. **The loader test poisons the wrong name.** `test_exact_loader_...`
   plants a bare `victim` module and calls `_exec_exact` with no
   dependencies. A variant that stays byte-exact for direct calls but prefers
   ambient `sys.modules` for *dependency* names (`v8_runtime`,
   `v8_snapshot`) passes it, while the real chain executes planted code.
3. **The end-to-end canonical tests were skipped where it mattered.**
   All three receipts record `2 SKIP (canonical repo checkout unavailable)`.
   The only tests that execute the real pinned chain never ran in the
   receipted environments, so dependency-path sabotage had no executable
   coverage at all.
4. **Retention is asserted by field name, not by behavior.**
   `test_context_exposes_no_snapshot_field` checks `_fields`/`hasattr`. A
   stash kept outside the tuple (module global, closure) is invisible to it.

## 2. What was built (additive, parameterizable)

- `test_security_regression.py` — 7 executable tests; every one runs the
  REAL public entrypoint against REALISTIC temp plan/bindings files (470
  archives, real anchor + contract). No source-text grep assertions.
- `gate_adapter.py` — target selection without edits: `GATE_UNDER_TEST_PATH`
  (default: frozen V9 file), `GATE_PREFLIGHT_FN` (default
  `preflight_longmemeval_v9`). Refusals must be `ValueError` (V7/V8/V9
  convention).
- `e2e_fixtures.py` — valid-set builder plus single-layer sabotage helpers
  (each re-issues digests so only the targeted layer can refuse).
- `adversarial/malicious_v8_runtime.py`, `malicious_v8_snapshot.py` —
  explicit attacker dependencies (no-op checks, 10**9 denominators).
- `mutation_variants/` — `variant_retained_snapshot.py` (stash + stale
  `authoritative_denominators`), `variant_unsafe_loader.py` (ambient
  preference for dependency names). Thin shims over exact V9 bytes; both pass
  the full frozen V9 suite (§4).
- `run_matrix.py` → `RECEIPT.json` — runs the new suite × {V9, 2 variants}
  plus the frozen old suite × {V9, 2 variants}; exits non-zero on any
  surprise.

## 3. Results on V9 (b300cbf) — exact failing protections

| test | V9 | retained-variant | unsafe-loader-variant |
|---|---|---|---|
| valid_plan_end_to_end | pass | pass | pass |
| consumption_revalidates_after_corruption | pass | **FAIL** | pass |
| ambient_sysmodules_cannot_substitute_code | pass | pass | **FAIL** |
| ambient_hashlib_substitution_is_refused | **FAIL** | **FAIL** | **FAIL** |
| duplicate_physical_copy_rows_are_refused | pass | pass | pass |
| inflated_denominator_plan_is_refused | pass | pass | pass |
| concurrent_consumption_is_isolated | pass | pass | pass |
| frozen V9 suite (7 tests, incl. canonical) | pass | pass | pass |

Reproduced weaknesses: (a) **retained-snapshot service** — variant passes
all frozen tests, new suite catches it; V9 itself is clean here (both
consumption paths re-read and refuse after corruption). (b) **unsafe loader**
— variant passes all frozen tests, new suite catches it; V9 itself is clean
here (ambient `v8_runtime`/`v8_snapshot` are neutralized by exact-exec
injection on the valid and garbage paths). (c) **V9 failing protection**:
ambient-`hashlib` substitution — a byte-swapped plan presented with a stale
digest is ACCEPTED when ambient `hashlib.sha256` vouches for it (all layers
resolve the trust root dynamically). V10 must capture pristine references at
import. Full evidence: `RECEIPT.json` (verdict `MATRIX-AS-EXPECTED`).

## 4. Blindness proof (executed, not claimed)

`run_old_tests_against_target.py` runs the unmodified frozen
`test_consumption_gate_v9.py` with the target pre-seeded as
`consumption_gate_v9`: **7/7 pass on V9, 7/7 pass on the retained variant,
7/7 pass on the unsafe-loader variant** (recorded in `RECEIPT.json`). The
existing suite cannot distinguish the broken variants from V9.

## 5. Limitations and non-reproduced observations

- Concurrency: barrier-started mixed valid/invalid E2E passes on all
  targets. Aggressive churn probes (16 threads × 50 loads; ~800M
  `sys.modules` writes during loads; see §6) produced **zero** spurious
  failures and **zero** observable cross-binds: the plant→import path holds
  the GIL end to end, so the shared-name window is an inspection-level
  hazard (no lock around plant/exec/restore), not an executed failure.
  Behaviorally-identical pinned bytes make module cross-bind unobservable
  black-box; V10 should still avoid shared-name planting.
- One single non-reproduced event: one full-suite run on the unsafe variant
  reported `regen-conc-a: AttributeError: 'NoneType' has no attribute
  '__dict__'`; 12 subsequent full runs (6 V9, 6 variant) are clean. Treated
  as an unexplained flake, NOT as a finding.
- The ambient-hashlib test patches `hashlib.sha256` process-wide during one
  entrypoint call; digests used by the harness are computed before patching.
- Scope is preparation/consumption only: no measurement, retrieval, Task4F1
  outcome access, HMAC, seal, or run occurred.

## 6. Raw evidence paths

- `drafts/v52/static_storage_security_regression_2026_09_13/RECEIPT.json` —
  machine receipt of every run in §3–§4.
- Same directory: suite, adapter, fixtures, adversarial modules, variants,
  `run_matrix.py`, `run_old_tests_against_target.py`.
- Scratch probes (not committed, per policy): `/tmp/e2e_probe.py` (first
  successful real-entrypoint E2E: 470 denominators in ~0.2 s),
  `/tmp/race_probe.py` (800 concurrent `_load_v8_exact`, 0 errors),
  `/tmp/churn_probe.py` (~800M churn writes, 0 load failures),
  `/tmp/xbind_probe.py` (600 loads under churn, 0 cross-binds),
  `/tmp/ambient_probe.py` (V9 accepts byte-swapped plan under vouching
  hashlib; refuses without it).

## 7. Integration instructions for a V10 candidate

1. Do not modify this directory's expectations; copy or point it at the
   candidate:
   `GATE_UNDER_TEST_PATH=/path/to/candidate.py
   GATE_PREFLIGHT_FN=preflight_longmemeval_v10 python3 -B -m unittest -v
   test_security_regression` from the suite directory.
2. The candidate must keep the consumption surface (`preflight(...)` →
   context with `fresh_snapshot()` /
   `authoritative_denominators()`, refusals as `ValueError`) or document the
   mapping and set `GATE_PREFLIGHT_FN` accordingly.
3. Acceptance bar: all 7 tests pass, INCLUDING
   `test_ambient_hashlib_substitution_is_refused` (the one V9 fails).
4. Re-run `python3 -B run_matrix.py` with the candidate added to `TARGETS`
   only if its sabotage-class expectations are defined in advance; never
   reclassify a failure after seeing it.
