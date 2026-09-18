# ERRATA — corrections to original `/inverse/REPORT.md`

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

1. **Newton-GMRES 0/12+0/4 did not test the intended method.** `make_jvp_op`
   (`inverse_lib.py:174`) and the segment `op` (`run.py:265`) returned
   `(I+JB)*v` instead of `JB*v` (identity counted twice; cold `B(x)=x` gives
   `[6,8]` for request `[3,4]`). The old linearity test passes on the wrong
   operator too, so it could not catch this. The "Newton beats fixed-point yet
   stays >1000× above threshold" inference is WITHDRAWN pending repair. Repaired
   run (same budget) still gives 0/12 + 0/4 — now an honest test of intended
   Newton-GMRES under 8×20 (see REPORT.md for numbers).
2. **`inner_ok` never meant convergence.** `gmres` returns finite-only
   (`isfinite(relres)`); a 1-iteration 5×5 probe stays finite yet unconverged.
   Original `inner_ok:true` alongside `failed-residual` is consistent with
   saturated-but-unconverged inner loops, not hidden convergence. Fixed code
   reports `inner_converged_all` separately (all False in repair grid).
3. **Call counts undercounted by one.** Reported `fevals=8` omitted the final
   verification `B(x)` eval (actual 9). Fixed `fevals` charges it
   (`fevals_loop`/`fevals_verify` split in per-case records).
4. **"Plain prefix replay" is one retained-input block forward (~3.5 ms,
   bit-exact), not whole-model prefix recomputation.** It re-runs a single
   `LlamaDecoderLayer` from the already-saved FP32 input anchor.
5. **Small L14 ledger error (≈1.8e-3) is not all-layer inverse success.**
   Per-layer truth: L14 ≈1.5–1.9e-3 (good), L29 ≈0.26–0.43, L0 ≈5.6–6.2 (layer-0
   residual norm ≈19× input norm). The 0.33 median mixes regimes.
6. **Zero success = under tested budget, not mathematical noninvertibility.**
   No claim beyond 8 outer × 20 inner, x0=y, fixed tolerances is supported.
7. **Storage gate mixed dtypes.** Comparing FP32 anchors+ledger (695040 B) to
   hypothetical BF16 KV (368640 B) as if matched dtype is invalid. Same-dtype
   FP32: 695040 vs 737280 B (42240 B headroom, backing payload only, no win
   claimed). Hypothetical BF16 anchors + FP32-metadata ledger (418560 B) still
   exceeds hypothetical BF16 KV (368640 B). No BF16 numerics were executed.
   Direct generic 4-bit KV (~3328 B/layer) remains the stronger comparator.
   RSS (~1.2 GB) is working set, not resident size; schedule/boundary gaps
   (layerwise vs per-segment, 15 anchors cover 0..28, global stack unexecuted)
   are now itemized in `ledger_storage_reconciled.json`.
8. **Original continuation was hidden-injection, not KV-only.** It replaced the
   full hidden state at L14 over the whole sequence and recomputed downstream —
   a different experiment from KV-cache replacement. NLL shift there is correct
   (verified bit-exact vs model forward here); KL there is PATCH||FULL (kept;
   kv-worker FULL||PATCH never combined). True single-layer-14 KV-only results
   are new in `kv_continuation.json` (cache-parity bit-exact 4/4).
9. **Bookkeeping gaps retained from runner:** `summary.json::agg_D2` is
   uninformative (`D2_fe` key never exists); use per-case `fevals`/`n_jvp`/
   `gmres_iters`. Segment parity gate and physical repeated-input fixture
   disclosure (short texts repeated to reach T=64) are kept and re-verified.
