# PROTOCOL — Task E: partial KV reconstruction via frozen ridge decoders

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## 0. Scope (frozen before outcomes)

- Prototype only. NOT an EchoKV/xKV reproduction. No paper novelty claim.
- Question: can discarded odd-layer K/V of a frozen pretrained model be
  usefully reconstructed from retained even-layer K/V by a small fitted
  linear predictor, judged by real teacher-forced continuation quality
  (KL / NLL delta / top-1 agreement), not by KV MSE alone?
- Fixtures are 12 AUTHOR-WRITTEN FEASIBILITY texts, not a language benchmark.
  Fixed split: train IDs 0..5, validation 6..7, test 8..11. Never fit on test.
- Model (read-only): /mnt/c/Users/MDP/dev/llmzip-work/parallel_ideas_r1/model
  (HuggingFaceTB/SmolLM2-135M, rev 93efa2f097d58c2a74874c7e644dbc9b0cee75a2,
  Llama, 30 layers, d=576, 9 Q heads, 3 KV heads, head_dim=64).
- Load: local_files_only=True, trust_remote_code=False, dtype=torch.float32,
  attn_implementation='eager', model.eval(), torch.set_num_threads(1),
  torch BLAS single-thread. CPU only. Native config dtype is bfloat16;
  executed dtype is float32 — costs reported for FP32 executed AND
  hypothetical BF16 separately, never mixed.
- GQA KV width verified from config: 3 KV heads x 64 = 192 floats per K (or V)
  per layer per token. All 30 K and 30 V layers counted.

## 1. Context construction (frozen)

- Tokenizer from the same local model dir (local_files_only).
- Per text: tokenize full text with add_special_tokens=False -> base ids B.
- Cyclic stream S = B repeated (S[i] = B[i mod len(B)]); if len(B)==0, fail case.
- Prefix(ctx) = S[0:ctx] for ctx in {16, 64}. Continuation = S[ctx:ctx+8]
  (8 teacher-forced continuation tokens). No pad tokens; attention mask all 1s.
- Log full prefix token IDs, continuation IDs, masks per case.
- Rationale: avoids artificial pads; repetition is deterministic and logged.

## 2. Predictor (frozen choice: per-KV-head 64->64)

- Retain even-indexed layers {0,2,...,28} K/V (post-RoPE keys as stored in
  DynamicCache; values as stored). Predict each odd layer o from even layer o-1.
- Decoder: SEPARATE ridge linear map per (odd layer o, KV-head h in 0..2,
  component C in {K,V}): input 64-dim head slice of layer o-1 component C ->
  output 64-dim head slice of layer o component C. Intercept allowed
  (unpenalized bias), fixed lambda=1e-3, NO hyperparameter sweep.
- Count: 15 odd layers x 3 heads x 2 = 90 decoders, each 64x64 + 64 bias.
  Weight bytes (float32) = 90*(4096+64)*4 = 1,497,600 bytes. Fixed here.
- Closed form in float64, stored float32:
  Xa=[X,1], P=diag(lambda,...,lambda,0), W=(Xa'Xa+P)^{-1}Xa'Y via torch.linalg.solve.
- Fit data: tokenwise pooled states from TRAIN IDs 0..5 only, from full-cache
  prefix runs at BOTH ctx 16 and 64 -> 6*(16+64)=480 token samples.
  Each sample: one token position's post-RoPE K / V head slices.
- Validation IDs 6,7: diagnostics (MSE) only, MUST NOT tune or refit.
- Test IDs 8..11: final evaluation only. Never test-target inputs in decoding.
- Original model weights frozen; no neural finetuning.
- RoPE convention: runtime keys in DynamicCache are POST-RoPE (rope applied
  before cache update in modeling_llama.py LlamaAttention.forward). Verified by
  code read + runtime check (cached keys != raw k_proj output; see tests.py).

## 3. Arms (frozen)

- A/full: original full DynamicCache prefix, stepwise teacher-forced
  continuation (8 steps, single-token forwards with cache).
- B/ridge: even layers kept, odd layers replaced by ridge prediction computed
  BEFORE cache use; continuation identical to A. Predictor weights + retained
  K/V bytes counted (Section 5).
- C/q4: generic per-token scaled 4-bit KV quantization of the FULL prefix
  cache (NOT labeled KIVI): per (layer, position, head, K/V) min/max affine to
  int4 0..15, real nibble packing (2 values/byte, odd widths padded + logged),
  float32 scale+zero per group stored alongside. Dequantize before cache use.
- D0/zero: odd layers zero-filled (same-layer zero ablation).
- D1/copy: odd layer o = copy of even layer o-1 (previous-layer-copy ablation).
- E/recompute: plain prefix recomputation wall time (one full forward of
  prefix+continuation vs cached stepwise), timing only.
- Cache-consumption proof (poison/perturbation): rerun B with odd K multiplied
  by 100 (or +50); continuation logits MUST change vs unpoisoned B, else
  integration is declared broken (traceback retained, integration blocked).

## 4. Metrics (frozen formulas)

Per test case (id, ctx) and arm X in {B,C,D0,D1}, per continuation step t=1..8,
with p=softmax(full logits), q=softmax(X logits) in float64:
- KL(full||X)[t] = sum_i p_i * (log p_i - log q_i).
- dNLL[t] = NLL_X(true tok) - NLL_full(true tok) = -log q_true + log p_true.
- top1_agree[t] = 1(argmax q == argmax p); also top1_true for reference.
- Tensor MSE: mean over all elements of (pred-target)^2 per odd layer and
  component, plus pooled mean. Bytes also stored.
- Report per-step arrays AND means. Never infer equivalence from
  nonsignificance; fixtures do not establish benchmark perplexity/accuracy.
- Timing: time.perf_counter, single thread, median of 3 repeats for E and for
  one B/A continuation step sample; CPU contention => exploratory only.

## 5. Memory accounting (frozen)

- Executed FP32 baseline per token: 30 layers*2*192 floats*4 B = 46,080 B/tok.
  Hypothetical BF16: half = 23,040 B/tok. Reported separately, never mixed.
- Candidate B per-token retained: 15*2*192*4 = 23,040 B/tok (FP32).
- Predictor fixed cost: 1,497,600 B (FP32 weights incl. bias). No optimizer state.
- Crossover: total_B(N) = 1,497,600 + 23,040*N vs full(N) = 46,080*N (FP32) =>
  N* = 1,497,600/23,040 = 65 tokens (derived here; recheck in run).
  Report actual small-context totals (ctx 16/64 + 8 cont tokens) even if worse.
- Serialized size (packed payload bytes on disk) vs residency (process RSS)
  reported separately. Baseline full caches needed for scoring stay alive as
  INSTRUMENTATION and are excluded from candidate memory (disclosed); never
  report combined RSS as compression.
- Peak RSS via resource.getrusage ru_maxrss; measured arrays/serialized bytes
  distinguished from hypothetical ideal packing.

## 6. Seeds, budget, failure handling (frozen)

- Seeds: torch.manual_seed(0); numpy default_rng(0) for any sampling
  (ridge itself is closed-form deterministic). Recorded in summary.json.
- Budget: single-thread torch/BLAS, PYTHONDONTWRITEBYTECODE=1, CPU only,
  peak RSS target < 3 GB, wall budget ~25 min session (<=6 min plan).
  No package installs, no network, timeouts on all heavy probes.
- Failures: any integration failure keeps its traceback in REPORT.md + log,
  retains runnable tensor-level tests, marks that arm 'blocked'; partial truthful
  output beats fabricated success. Never hardcode converged=True (no
  convergence flags used at all). No retuning after observing candidate
  outcomes; validation never refits.
- Determinism: run.py prints exact reproducible command; source_hashes.json
  holds sha256 of model files (config, tokenizer, safetensors), inputs,
  PROTOCOL.md, run.py, tests.py.
