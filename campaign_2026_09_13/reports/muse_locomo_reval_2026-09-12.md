# LoCoMo native-representation independent re-execution — final report

**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

## Environment
`~/muse-work/ml-python -c`: python **3.14.4**, numpy **2.5.3**, scipy **1.18.1**, scikit-learn **1.9.1** (a different stack from the original producer run, as required). Scratch used: `/tmp/locomo_reval/reval.py`, `reval_out.json`. No repo writes; `main()` never called — only `load_dataset`/`build_representation` imported via `importlib` from the frozen producer, and `matrix_diagnostics`/`variance_diagnostics`/`entropy` used verbatim from the frozen definitions file.

## 1. Input verification — PASS (both exact)
- `locomo10.json`: sha256 `79fa87e9…698ff4` **matches**, size **2,805,274 bytes** matches.
- `audit_layer/`: 20 files (`conv_0..9.json`, `errors_conv_0..9.json`). Manifest recomputed exactly per the frozen `audit_layer_manifest()` recipe (rows `{file,bytes,sha256}` sorted by filename, `json.dumps(sort_keys=True, separators=(",",":"))`, sha256 of that): `90a4e94c…89df06` **matches**.

## 2. Execution
All 10 conversations rebuilt (`locomo_0..9`, N = 419/369/663/629/680/675/689/681/509/568). All C are float64, C-contiguous, finite (`no_nan` true).

## 3. Value-for-value comparison
**Exact (bit-identical, deviation 0.0):**
- N, all 8 feature-count fields, and C_shape vs **both** `task1_locoMo_stats.json` and `counts_report.json`, all 10 convs.
- `zero_mass`: exactly `0.0` everywhere — **0 exact zeros** in every C (e.g. 0/40224 entries for locomo_0). Integer-like, no tolerance needed.
- `occupancy_vector`: max abs deviation **0.0** under *both* `(C>=0)` and `(C>0)` hypotheses — indistinguishable because there are no exact zeros, and `%.17g` round-trips each k/N occupancy double exactly.
- `sign_entropy_ge`, `sign_entropy_gt`: abs diff **0.0** all convs (they equal each other, as zero_mass=0 requires).
- Summary-block means D1_ge, D2_cv_sigma: abs diff **0.0**.

**Last-ulp drift only (quantified, nothing hidden):**
- `variance_vector`: worst max relative deviation **1.91e-14** (locomo_3, coord argmax recorded per-conv), worst max absolute **3.05e-16**; mean relative ~2e-15. Consistent with SVD/LAPACK last-bit drift across library versions, not a semantic difference.
- Other scalars (all 10 convs): worst abs diff **2.53e-15** (locomo_6 `corr_median_abs`); `cv_sigma` ≤5.0e-16, top16/32/48 and first32 shares ≤9.4e-16, `off_mass` ≤2.5e-16, `p95_abs` ≤2.3e-15.
- `residual_mean_max_abs`: both mine and published are ~1e-16 cancellation noise; abs diffs ≤1.4e-16 (relative differences are meaningless at this scale).

## Conclusion
**Yes — the published values reproduce under an independent execution on the numpy 2.5.3 / scipy 1.18.1 / sklearn 1.9.1 stack at tolerance ~3e-15 absolute (~2e-14 relative worst case on variances).** Everything structural is bit-exact: counts, shapes, zero-mass (exactly 0), occupancies, and entropies.

**The one thing that does NOT reproduce:** byte-exact `C_sha256` — 0/10 of my `sha256(C.tobytes())` match `counts_report.json`/`task1_locoMo_stats.json` (all 10 of my hashes are self-consistent and unique). This is the expected, unavoidable consequence of the ~1e-14 SVD last-bit drift above: statistics agree to 15 digits, raw bytes do not. Anyone asserting C-byte-identity across LAPACK versions should expect failure; anyone asserting statistical identity to 1e-12 passes with ~3 orders of magnitude of margin.
