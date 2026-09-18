# REPORT — narrow JVP repair + adversarial verification (Tasks 1–5)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Pretrained SmolLM2-135M, FP32 executed, single-thread CPU, peak RSS ~1203 MB
(<3 GB). Same grid as original: layers {0,14,29} × texts {8..11} × T=16 (12
cases) + segment 14–15 × T=64 (4 cases); 8 outer × 20 inner, x0=y,
`tols 1e-5/1e-3`. No 40×100 probe, no damping/line-search/retuning change.

## 1. JVP bug → acceptance → fix (Tasks 1–2)

- Coordinator FATAL confirmed here: `make_jvp_op` returned `(I+JB)*v`; segment
  `op` identical. Cold `B(x)=x`: request `[3,4]` → actual `[6,8]`.
- `test_acceptance.py`: RED on original 6/11 fail (identity, affine, 2×
  segment, real-layer FD vs autograd with FD-best 0.0038 @ eps 3e-3, one-step
  Newton affine res 0.33); GREEN on fixed 11/11. `test_mutation.py`: restored
  `v+` in both paths fails identity/affine as required. GMRES exact-solve
  passes both (solver itself intact); `inner_ok` shown finite-only by a
  1-iteration 5×5 probe. Logs: `test_acceptance_RED.log` / `_GREEN.log` /
  `test_mutation.log`.
- Fixed rerun (`run_fixed.py`, corrected `inverse_lib_fixed.py`): parity 12/12
  (rel 0.0, hook truth for every layer incl. 29); D2 0/12, **D3 0/12**,
  segment D3 0/4 — now an honest test of intended Newton-GMRES under budget.
  Fixed D3 fwd-res/recon (per text 8,9,10,11): L0 0.0045–0.0497 / ~18.5–19.2;
  L14 0.00068–0.00332 / 0.0032–0.0071; L29 0.26–0.72 / ~1.09–1.22. Segment D3:
  res 0.0047–0.0123, recon ~0.019–0.023. GMRES saturates 20/20 every outer
  (`inner_converged_all` False); `fevals` now 9 (8 loop + 1 verification),
  `n_jvp` 175–176/case. Raw histories/tensors/errors/counts/walltime/failures
  preserved in `per_case.jsonl` + `*.npz`.
- Independent replay (`replay_independent.py` → `replay_residual.json`):
  verdict MATCH 12/12 (FP32 tol 1e-6; success flags re-derived from recomputed
  `B(x_hat)`, hook truth, never worker flags). Wrapper parity 0.0 all cases.

## 2. Ledger + storage (Task 3)

- Ledger re-decode exact 12/12; recon matches worker to 1e-6
  (`ledger_storage_reconciled.json`). Construction is explicit lossy quantized
  `x−y` residual with `x_est=y` (M1 omission == C1 bit-exact 12/12; M2 flip
  changes output everywhere); never original `x`; not branch-bit/exact.
- Storage (backing payload only): ledger 4736 B/layer; FP32 KV 24576 B/layer
  (737280 B all-30); anchors FP32 every-2-layers 552960 B. Same-dtype FP32
  anchors+layerwise-ledger 695040 B vs KV 737280 B (42240 B headroom — NOT a
  win claim; excludes workspace/RSS, schedule/boundary gaps itemized).
  Hypothetical BF16 KV 368640 B vs BF16-anchors + FP32-metadata ledger 418560 B
  (exceeds by 49920 B; no BF16 numerics run). Generic 4-bit KV (~3328 B/layer
  median) stays the stronger comparator. One-ledger-per-segment (15×) also
  tabulated without re-designing for a win.

## 3. Continuation (Task 4)

- Original `continuation.json` retained with honest label (full hidden-state
  replacement at L14 + downstream recompute — NOT KV-only). Its NLL shift
  verified bit-exact vs model forward here (max diff 0.0, 4/4); KL is
  PATCH||FULL (kv-worker opposite direction never combined).
- New TRUE single-layer-14 KV-only (`kv_continuation.py` →
  `kv_continuation.json`, 4/4 tested, same 16+8 contexts, same shifted labels):
  Q from true hidden, post-RoPE K / V from per-arm hidden, residual true.
  Cache-parity true-KV vs full bit-exact 4/4 (maxabs 0.0); poison
  ledger-vs-noledger logits differ 0.78–2.25 (live payload). Means over 4
  texts: ledger ΔNLL −0.003, KL 0.00026, agree 0.97; no-ledger KL 0.0055, agree
  0.875; direct-4bit KL 1.11, agree 0.41 (destroyed); generic-4bit-KV KL
  0.0020, agree 0.97. Patched path recomputes logits full-size; NO resident
  compression claim.

## 4. Limits, files, reproduce

- Exploratory pilot (4 authored texts, 3 layers, teacher-forced, shared-CPU
  timing, FP32 only). 0/12 means "not under 8×20 from y", not noninvertibility.
  Segment parity gate kept; T=64 inputs use deterministic repetition of short
  texts (disclosed). `summary.json::agg_D2` uninformative (inherited key bug);
  use per-case counts. No self-certification: coordinator `CHECK.json`
  re-decode/storage/continuation findings independently reproduced here
  (replay MATCH, re-decode 12/12, NLL cross-check 0.0); remaining inferences
  are the author's, labeled pilot-only.
- Files (this dir only): `REPORT.md`, `ERRATA.md`, `PROTOCOL_DELTA.md`,
  `inverse_lib_fixed.py`, `run_fixed.py`, `test_acceptance.py` (+RED/GREEN),
  `test_mutation.py` (+log), `per_case.jsonl`, `summary.json`,
  `replay_independent.py` + `replay_residual.json`,
  `ledger_storage_reconciled.json`, `kv_continuation.py` +
  `kv_continuation.json`, `continuation.json` (retained hidden-injection),
  `segment.json`, `*.npz`, `source_hashes_fixed.json`, `hash_proof.json`,
  `COMMANDS.md`. Original `../inverse/` untouched (hashes before==after).
- Reproduce:
  `cd inverse_repair && PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1
  OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 run_fixed.py`
  then `ACCEPT_LIB=fixed python3 test_acceptance.py`,
  `python3 test_mutation.py`, `python3 replay_independent.py`,
  `python3 reconcile_ledger.py`, `python3 kv_continuation.py`.
