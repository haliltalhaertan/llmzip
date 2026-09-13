# Muse session — independent VALUE-LEVEL re-execution of the LoCoMo native representation

You are a fresh independent re-execution session. Do not read other sessions' scratch or logs.

## Environment

- **No network.** Use `~/muse-work/ml-python -c ...` as your python (it provides numpy 2.5.3,
  scipy 1.18.1, scikit-learn 1.9.1). Scratch: `/tmp/locomo_reval/`. Print your final report as
  your answer (writes outside /tmp are blocked in this session).

## Task

Independently re-execute the frozen LoCoMo representation construction and compare, value for
value, against the published per-conversation statistics. This is the second-party value-level
check that no artifact currently provides.

1. **Inputs (verify first):**
   - raw: `/mnt/c/Users/MDP/dev/llmzip-work/drive/locomo10.json` — sha256 must equal
     `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4`, 2,805,274 bytes.
   - audit layer: `/mnt/c/Users/MDP/dev/llmzip-work/drive/audit_layer/` — 20 files; recompute the
     canonical manifest exactly as the frozen script's `audit_layer_manifest()` does (sorted rows
     `{file, bytes, sha256}`, `json.dumps(sort_keys=True, separators=(",",":"))`, sha256 of that);
     it must equal `90a4e94c9247d8ace7aaf62acdda7315744b111d84e42658cccfeb0a3c89df06`.
2. **Execute the frozen producer's own code.** Import via `importlib` the file
   `/mnt/c/Users/MDP/dev/llmzip-work/drive/v52_t4d_locomo_frozen_cross_benchmark.py` (do NOT call
   its `main()`; only use its functions/constants — `raw_item_to_conv`, `build_representation`,
   `message_text`, etc.). For each of the 10 conversations: build `C` exactly as the frozen
   `build_representation` does. Record per conversation: N, feature counts, and
   `zero_mass = (C==0).mean()`.
3. **Compare value-for-value** against the published statistics in
   `/mnt/c/Users/MDP/dev/llmzip-work/regen/locomo/task1_locoMo_stats.json`:
   - per-conversation `variance_vector` and `occupancy_vector` (each is a `';'`-joined list of 96
     `%.17g` numbers): compute max relative deviation for variance and max absolute deviation for
     occupancy;
   - per-conversation scalar fields: `sign_entropy_ge`, `sign_entropy_gt`, `zero_mass`, `cv_sigma`,
     `top32_share`, `D4 off_mass/median_abs/p95_abs` — recompute each from YOUR C using the frozen
     definitions file `/mnt/c/Users/MDP/dev/llmzip-work/harness/ref/measure_representation_diagnostics.py`
     (import it; use its `matrix_diagnostics` / `variance_diagnostics` / `entropy` verbatim) and
     compare to the published values.
   - feature-count blocks vs the same file and vs `/mnt/c/Users/MDP/dev/llmzip-work/regen/locomo/counts_report.json`.
4. **Report**: environment versions; every comparison's max/mean deviation (state exact numbers);
   your conclusion: do the published values reproduce under an independent execution on a different
   numpy/scipy/scikit-learn stack, and at what tolerance? Explicitly list anything that does NOT
   reproduce. Note: small last-digit drift is expected across library versions — quantify it, do
   not hide it; report `zero_mass` exactly (integer-like count of exact zeros).

Rules: read-only outside `/tmp`; no repository writes; no network; do not regenerate anything other
than what step 2 says; do not touch Task 4F1 or any retrieval results.
