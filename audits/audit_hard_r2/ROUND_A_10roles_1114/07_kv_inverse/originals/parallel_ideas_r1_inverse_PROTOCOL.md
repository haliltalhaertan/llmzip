# PROTOCOL — Tasks C (lost-information ledger + checkpoints) and D (bounded matrix-free inverter)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Frozen BEFORE any candidate (C/D) outcomes. No retuning after observing candidate outcomes.
Task prompt is the authority; IDEA_REVIEW.md is scope only, not measured evidence.

## 0. Model, runtime, dtype (fixed)

- Model: `/mnt/c/Users/MDP/dev/llmzip-work/parallel_ideas_r1/model` = HuggingFaceTB/SmolLM2-135M,
  rev `93efa2f097d58c2a74874c7e644dbc9b0cee75a2`, Llama arch, 30 layers, d=576,
  9 Q heads, 3 KV heads, head_dim=64, GQA KV width = 3*64 = 192 (VERIFIED at runtime
  from `config.num_key_value_heads * (hidden_size // num_attention_heads)` AND from the
  live `q_proj/k_proj/v_proj/o_proj` weight shapes; abort if they disagree).
- Load: `local_files_only=True, trust_remote_code=False, dtype=torch.float32,
  attn_implementation='eager'`, `.eval()`, `torch.no_grad()` except inside JVP probes,
  `torch.set_num_threads(1)`, `torch.set_num_interop_threads(1)`, BLAS single-thread
  (`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1`), `PYTHONDONTWRITEBYTECODE=1`.
- Native config dtype is bfloat16; ACTUAL executed dtype is float32. All measured numbers are
  FP32. Hypothetical BF16 costs are computed arithmetically in a SEPARATE column, never mixed.
- If the pretrained load fails: preserve traceback, stop, report gate-blocked. Random-init
  substitution is FORBIDDEN.
- Seeds: `torch.manual_seed(0)`; deterministic tokenization; no sampling (argmax/teacher-force only).
- Peak RSS tracked per case via `resource.getrusage`; budget < 3 GB. CPU-only, WSL ~16 GB host.

## 1. Cohort (frozen; no fitting on test)

- Fixtures: `/mnt/c/Users/MDP/dev/llmzip-work/parallel_ideas_r1/text_fixtures.json`
  (12 author-written feasibility texts, NOT a language benchmark).
- Train IDs 0..5, val 6..7, test 8..11. Decoding/quantizer settings frozen WITHOUT test
  (uniform per-token min/max needs no calibration). NOTHING is fit on test IDs.
- Primary cohort: layers {0, 14, 29} x test texts {8,9,10,11} x ctx T=16 → 12 cases.
- Context construction: tokenize text (no added prompt), take first T token IDs; if the text
  yields < T tokens, deterministically REPEAT the same text's token IDs (no pad/EOS injection).
  Attention is full-causal over real tokens, so mask = all-ones 2D + internal causal 4D mask;
  token IDs and mask type are logged per case.
- Gate: contiguous two-block segment (layers 14..15) x 64-token inputs runs ONLY if
  single-block forward parity succeeds on all 12 primary cases. NO other layer sweep.

## 2. Block definition and parity gate (must pass before any inversion)

- Block B(x) = one `LlamaDecoderLayer`: y = B(x), x,y ∈ R^{T×576} (COMPLETE sequence block
  input from block output; never tokenwise-as-independent).
- Wrapper `block_forward(x, layer_idx, position_ids, position_embeddings, causal_mask)` calls
  `model.model.layers[i](hidden_states=x, attention_mask=causal_mask, position_ids=...,
  position_embeddings=...)` with mask/positions rebuilt EXACTLY as `LlamaModel.forward` does
  (`create_causal_mask` + `rotary_emb`), RoPE + RMSNorms inside the layer untouched.
- Reference: full-model forward with `output_hidden_states=True`; hidden_states[i] is the true
  block input, hidden_states[i+1] the true output.
- PARITY GATE: max|wrapper − reference| and relative error per case; PASS iff
  rel_err = ||w−r||_2 / (||r||_2 + 1e-12) <= 1e-5 on all 12 cases. Inversion/ledger cases run
  only on parity-passing cases; else status = gate-blocked.

## 3. Task D — bounded matrix-free inverter

Per (layer, text, T=16) case, target y = B(x_true):

- D0 direct one-pass forward: y_ref = B(x_true); wall time t_D0 (the cost inversion must beat).
- D1 plain prefix replay/checkpointing: re-run B(x_anchor) from the saved FP32 input anchor
  (= one block forward from checkpoint); wall time t_D1; exact up to FP determinism.
- D2 residual fixed-point: x_{k+1} = y − F(x_k), F(x) := B(x) − x, x0 = y, max 8 corrections
  (1 correction = 1 F eval = 1 block forward). Stop early when TRUE forward residual
  rel_res = ||B(x_k)−y||_2/(||y||_2+1e-12) <= 1e-5.
- D3 matrix-free Newton-GMRES: solve G(x)=B(x)−y=0, x0=y, max 8 OUTER corrections.
  Each correction solves J(x_k)δ=−G(x_k) with GMRES, max 20 INNER iterations, rtol 1e-5,
  JVP operator via `torch.autograd.functional.jvp` (NO dense Jacobian; N=T*d up to 9216).
  Counts: n_jvp (each JVP call), n_feval (residual evals), inner iters used, wall time.
- Hard budget: 180 s wall per case per solver (monotonic clock; exceeded → status killed-budget,
  partial iterates retained).
- SUCCESS (both required, computed — NEVER hardcoded `converged=True`):
  (a) true forward residual rel <= 1e-5, AND (b) input reconstruction rel
  ||x_hat−x_true||_2/(||x_true||_2+1e-12) <= 1e-3.
  `converged`/`success` booleans are DERIVED from these two numbers per case.
- Nonfinite policy: any nonfinite tensor → arm FAILED-nonfinite, values logged as null + flag,
  case retained.
- Comparison: t_D2, t_D3 (incl. counts) vs t_D0 and t_D1 — solvers are compared against direct
  forward/replay, not only each other.

## 4. Task C — lost-information ledger + checkpoints

- Declared CHEAP inverse (fixed, no tuning): x_est = y (zero-order; 0 extra block evals).
- Truth-derived correction (allowed at ENCODE, CHARGED, not "branch bits"/"exact inversion"):
  c = x_true − x_est ∈ R^{T×576}.
- Ledger quantization: uniform 4-bit per scalar, PER-TOKEN (row-wise) min/max → FP32 scale s_t
  and zero/min m_t per token; q = round((c−m)/s·15) ∈ {0..15}; ACTUAL nibble packing
  (2 scalars/byte, low nibble first; odd count padded, pad logged); decoder uses ONLY
  (packed bytes, scales, y) — NEVER the original input. x_hat = y + dequant(packed).
- Checkpoint schedule for ACCOUNTING: full FP32 anchor every 2 layers (layers 0,2,...,28 → 15
  anchors). A short segment (layers 14..15, 64-token) is EXECUTED only after forward parity;
  full 30-layer deployment accounting is arithmetic from measured per-layer bytes.
- Arms (same case grid as D where applicable):
  - C0 full original (FP32 hidden/KV) — quality reference.
  - C1 no-ledger (x_hat = y).
  - C2 direct 4-bit input quantization (same per-token 4-bit scheme applied to x_true itself;
    matched bit-budget control).
  - C3 ledger (cheap inverse + packed 4-bit correction).
  - C4 plain anchor/replay (exact recompute from FP32 anchor; quality-exact, cost = anchors + time).
  - C5 direct 4-bit KV per-token scale (EXPLICIT generic baseline, NOT KIVI replication:
    per-token 4-bit uniform quant of that layer's K and V states).
  - C6 full original KV (FP32 K+V of the layer).
- Quality (only if forward/solver gates pass; else status blocked, NO fake zero-loss):
  real attention continuation with RECONSTRUCTED K/V: rebuild the layer's K,V by running the
  block forward on x_hat, run teacher-forced continuation ≥ 8 tokens through the FULL model,
  report per-token NLL difference vs C0/C6, predictive KL(recon||full) per position, top-1
  agreement rate. Fixtures do NOT establish benchmark perplexity/accuracy.
- Counterfactual/mutation probes (≥2, preserved red→green in tests.py + test log):
  M1 correction-omission (decode packed ledger with correction zeroed → must equal C1 bit-exact);
  M2 single-nibble flip in packed payload → reconstruction MUST change (detects fake passthrough).
- Storage accounting (measured vs hypothetical, separate columns):
  measured = actual packed bytes + FP32 scales/mins + anchors actually saved + decoder weights
  (0: no learned decoder) + transient workspace (peak RSS delta); hypothetical-ideal = L·b·d
  bit formula, labeled NOT-MEASURED. FP32-executed baseline AND hypothetical-BF16 columns separate.

## 5. Metrics, files, timing methodology

- Per-case record (identity-keyed `layer/text_id/T/case_id`): token IDs, mask spec, true/estimated
  arrays (saved .npy/.npz for independent re-decode), packed payload bytes, scales, residuals,
  rel errors, KL/NLL-deltas/top1 (continuation), counts (fevals, JVPs, GMRES iters), wall times
  (`time.perf_counter`, single-thread; CPU contention → timing EXPLORATORY), peak RSS, dtype,
  converges/success flags derived, status.
- Outputs in THIS dir only: PROTOCOL.md, protocol.sha256, run.py, tests.py, test log,
  per_case.jsonl, summary.json, REPORT.md, source_hashes.json, progress.json.
- Failure handling: every failed/killed/gated case is RETAINED with reason; partial output
  preferred over fabricated success; per-idea statuses (tested / gate-blocked / partial /
  unsupported) reported SEPARATELY for C and D.
- Timebox: ≤6 min inspect/plan, implement+run, 3 min report; hard per-case 180 s solver cap.
