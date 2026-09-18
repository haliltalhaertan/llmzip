# REPORT — Task E: partial KV reconstruction (frozen ridge decoders)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## Status by idea/arm

- **E-ridge (retain even layers, ridge-predict odd, per-KV-head 64→64, λ=1e-3): TESTED** —
  end-to-end on the pretrained model, 8/8 test cases, 0 failures.
- **C-q4 (generic per-token scaled 4-bit KV, real nibble packing): TESTED** — same cases.
- **D0-zero / D1-copy ablations: TESTED** — both ran; copy is decisively worse
  than zero (see below), so the ridge gain over copy is real but the bar is low.
- **E-recompute timing: TESTED (exploratory)** — single-thread CPU, contention noted.
- **Integration (cache replacement consumed): TESTED** — poison test passed 8/8.
- No arm is gate-blocked; nothing is claimed beyond these authored fixtures.

## What was actually measured

SmolLM2-135M loaded locally (float32 executed; config file declares bfloat16;
30 layers, 3 KV heads × head-dim 64 → GQA width 192; runtime RoPE check passed:
cached keys are post-RoPE). 90 ridge decoders fit on train IDs 0–5 only
(480 token samples, ctx 16+64 pooled); validation (6,7) diagnostics only;
test IDs 8–11, prefix ctx {16,64} + 8 teacher-forced continuation steps via
real `DynamicCache` stepwise forwards. Means over 8 steps × 4 test texts:

| ctx | arm | mean KL(full\|\|arm) | mean ΔNLL | mean top1-agree | prefix MSE (odd) |
|-----|-----|--------------------|-----------|-----------------|------------------|
| 16 | ridge | 0.24–0.48 | −0.16…−1.06 | 0.50–0.75 | 0.54–0.66 |
| 16 | q4 | 0.015–0.030 | −0.05…−0.37 | 0.625–1.0 | 0.038–0.041 |
| 16 | zero | 0.51–1.05 | −0.19…−0.88 | 0.375–0.75 | 2.33–2.43 |
| 16 | copy | 2.09–4.09 | −1.47…+0.45 | 0.125–0.25 | 4.40–4.66 |
| 64 | ridge | 0.23–0.77 | −2.93…−3.85 | 0.875–1.0 | 0.64–0.70 |
| 64 | q4 | 0.002–0.076 | −1.75…+0.07 | 1.0 | 0.042–0.044 |
| 64 | zero | 0.78–1.71 | −1.69…−4.05 | 0.625–1.0 | 2.62–2.68 |
| 64 | copy | 6.0–8.07 | −3.34…−5.09 | 0.0–0.125 | 5.01–5.14 |

Per-step rows (320) in `per_case.jsonl`; aggregates + token-ID provenance in
`summary.json`. Negative ΔNLL means the arm assigned slightly higher likelihood
to the (highly predictable, cyclic) true token — with n=8 steps × 4 texts this
is reported, not claimed as superiority; nonsignificance is not equivalence.

Reading: ridge beats both ablations on every case (KL and MSE), confirming the
fitted decoder learned cross-layer structure beyond trivial baselines. Generic
4-bit quantization beats ridge everywhere at ~1/6 the per-token bytes — the
idea is feasible as reconstruction, but not competitive with direct low-bit KV
on these fixtures. No inference-from-MSE claim is made: quality is judged by
the KL/NLL/top-1 columns above.

## Memory: honest crossover (candidate is WORSE at tested sizes)

- Executed FP32 full prefix: 46,080 B/tok (ctx16 = 737,280 B; ctx64 = 2,949,120 B).
- Hypothetical BF16 full: half of the above (separate, never mixed).
- Ridge retained: 23,040 B/tok + fixed predictor 1,497,600 B payload
  (`predictor.pt` on disk 1,548,427 B — measured file vs idealized payload
  distinguished). Totals: ctx16 → 1,866,240 B (2.5× full FP32); ctx64 →
  2,972,160 B (still above full FP32 2,949,120 B). Crossover N\* = 65 prefix
  tokens (FP32). Small-context total cost reported even though worse.
- q4 payload case 8:16: computed 115,200 B (0.156× FP32); real packed tensors
  saved in `q4_payload_8_16.pt` (165,863 B with container overhead).
- Residency vs serialized size are separate: peak process RSS 1,235,676 KB
  (~1.2 GB, includes model + instrumentation caches) is NOT a compression
  claim; baseline full caches were retained as scoring instrumentation and
  excluded from candidate accounting (disclosed).
- Timing (exploratory, single-thread CPU): full forward 0.144 s vs cached
  stepwise 0.452 s medians (case 8:16, 3 repeats).

## Limitations

1. Only 4 authored test texts × 2 prefix lengths; cyclic-repetition contexts
   make ctx-64 continuations near-deterministic (even zero-fill reaches 1.0
   agreement) — weak discrimination at long ctx.
2. Continuation K/V for new tokens is exact (only the prefix is compressed);
   error accumulation over long generation untested.
3. FP32 execution only; BF16 numbers are arithmetic, not measured.
4. Single seed, single λ=1e-3 (frozen, no sweep — by design).

## Next smallest discriminating test

Natural (non-repeating) continuation passages of ≥64 tokens on held-out
authored texts, comparing ridge vs q4 at matched total bytes including the
amortized predictor (prefix ≥ 256 tokens so the predictor is past crossover),
with per-step KL as the primary metric.

## Reproduce

`PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 run.py`
then `PYTHONDONTWRITEBYTECODE=1 KV_HEAVY=1 python3 tests.py`.
Artifacts: `PROTOCOL.md` (+`protocol.sha256`), `run.py`, `tests.py`,
`test_log.txt`, `per_case.jsonl`, `summary.json`, `REPORT.md`,
`source_hashes.json`, `progress.json`, `predictor.pt`, `q4_payload_8_16.pt`.
