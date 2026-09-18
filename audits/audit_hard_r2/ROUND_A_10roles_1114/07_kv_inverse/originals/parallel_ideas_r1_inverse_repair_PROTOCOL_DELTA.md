# PROTOCOL_DELTA — repair-only changes (frozen scientific arms unchanged)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Frozen protocol: `/inverse/PROTOCOL.md` (sha256 `65fa4200…`, copied verbatim to
`PROTOCOL_FROZEN_COPY.md` in this dir). No arm, budget, tolerance, cohort, or
recommendation change. In particular: same 8 outer / 20 inner, same x0=y, same
rtol `1e-5`, same `fwd<=1e-5` + `recon<=1e-3` gates, same layers {0,14,29},
texts {8,9,10,11}, T=16, segment 14–15/T=64. The original report's 40×100 probe
was NOT run (explicit non-follow per task).

## 1. JVP operator fix (both paths, implementation + bookkeeping only)

- `inverse_lib_fixed.py::make_jvp_op`: `_block_fn_grad` returns FULL `B(x)`, so
  `torch.autograd.functional.jvp` already yields `JB*v`. Original returned
  `(v+jv)` = `(I+JB)*v`. Fixed returns `jv` only. One-line math fix; no
  iteration, damping, line-search, preconditioner, or retuning change.
- `run_fixed.py` segment `op`: identical defect (`(v+jv)` on full `seg(x)` jvp);
  fixed to `jv` only. Same budgets.
- Added `gmres_converged(relres, rtol)`: original `gmres` 4th return and
  `inner_ok` are FINITE-only (`isfinite(relres)`), not convergence. Fixed code
  keeps `inner_ok` (finite, compat) and adds `inner_converged_all` /
  `inner_converged_list` / `gmres_relres` (finite AND `relres<=rtol`).
- Call counts now CHARGE the final verification residual eval: `fevals` =
  loop evals + 1 verification eval (`fevals_loop` / `fevals_verify` kept
  separately). Original omitted it (reported 8, actual 9 block forwards).
  `n_jvp` semantics unchanged (each JVP call). No success renamed: thresholds
  and `failed-residual` statuses identical.

## 2. Outputs stay separate

- `OUT_DIR` redirected to `inverse_repair/`; original `inverse/` never written
  (hash proof in `source_hashes_fixed.json` + `hash_proof.json`).
- `per_case.jsonl` / `*.npz` / `continuation.json` / `segment.json` /
  `summary.json` regenerated here with SAME case IDs/grid; `source_hashes*`
  renamed to `source_hashes_fixed.json` to avoid confusion.

## 3. Added (not protocol) verification collateral

- `test_acceptance.py` (acceptance suite, Task 1) + `test_mutation.py`;
  `replay_independent.py` (independent residual replay);
  `reconcile_ledger.py` (ledger/storage reconciliation);
  `kv_continuation.py` (true single-layer-14 KV-only probe; original
  hidden-injection in `continuation.json` retained under honest label).
