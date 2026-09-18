# REPORT (CORRECTED v2) — Task E: partial KV reconstruction

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Measurement repair of `../kv/REPORT.md`. Scientific design unchanged (same
model, fixtures, arms, λ=1e-3, 64→64 heads, seeds; no retuning). What changed
is measurement only — see `ERRATA.md` (affected vs unaffected metrics) and
`PROTOCOL_DELTA.md` (v2-1..v2-6). This is a measurement repair, not an
independent certification.

## Precise evaluation boundary (v2-1)

The eight continuation INPUTS are preserved exactly (`cont = S[ctx:ctx+8]`,
consumed stepwise, same eight outputs as the original run). An eighth
OSEF — a ninth stream token `S[ctx+8]` from the same deterministic fixture
stream — supplies correctly aligned next-token TARGETS `tgt = S[ctx+1:ctx+9]`.
`logits[t]` (emitted after consuming `cont[t]`) is scored against `tgt[t]`.
Evaluated prediction contexts are ctx+1..ctx+8 (stream indices ctx+1..ctx+8);
the first continuation token `S[ctx]` is consumed as input but NEVER scored
as a target. Every row carries `"align": "shifted-v2"`, `cont_input`,
`true_token`, `pred_index`, `context_len`. The rejected alternative
(first-prefix-logit design) would have changed the evaluated outputs and is
documented in `PROTOCOL_DELTA.md` only.

Shift proof: on fixture 8:16 (ext window asserted 9/9 unique at test time,
i.e. nonrepeating over every evaluated target), cached stepwise `logits[t]`
equals the no-cache full-sequence teacher-forced logits row `ctx+t` to
3.9e-05 max-abs at all 8 positions, including true-token log-probs
(acceptance test A1, `KV_HEAVY=1`). The old target `cont[t]` differs from the
correct target at all 8/8 steps (A2 mutation check).

## What was actually measured (corrected)

SmolLM2-135M, local, float32 executed (config declares bfloat16), 30 layers,
3 KV heads × 64 → GQA width 192, post-RoPE cache check passed. 90 ridge
decoders fit on train IDs 0–5 only (480 token samples); validation
diagnostics only; test IDs 8–11 × ctx {16,64} + 8 valid next-token targets.
Means below are per-case means (min–max over the 4 test texts), recomputed
directly from the 320 `shifted-v2` rows (`per_case.jsonl`).

| ctx | arm | mean KL(full\|\|arm) | mean ΔNLL (valid next-token) | mean top1-agree | prefix MSE (odd) |
|-----|-----|--------------------|------------------------------|-----------------|------------------|
| 16 | ridge | 0.30–0.48 | +0.12…+0.62 | 0.50–0.75 | 0.54–0.66 |
| 16 | q4 | 0.02–0.03 | −0.01…+0.04 | 0.625–1.0 | 0.04 |
| 16 | zero | 0.51–1.05 | +0.69…+1.20 | 0.375–0.75 | 2.33–2.43 |
| 16 | copy | 2.09–4.09 | +1.87…+4.49 | 0.125–0.25 | 4.40–4.66 |
| 64 | ridge | 0.23–0.77 | +0.30…+0.83 | 0.875–1.0 | 0.64–0.70 |
| 64 | q4 | 0.00–0.08 | +0.00…+0.12 | 1.0 | 0.04 |
| 64 | zero | 0.78–1.71 | +0.85…+1.87 | 0.625–1.0 | 2.62–2.68 |
| 64 | copy | 6.00–8.07 | +6.14…+8.26 | 0.0–0.125 | 5.01–5.14 |

Reading (unchanged in kind, corrected in sign): with VALID next-token NLL,
every arm mean ΔNLL is ≥ ~0 (approximations cost likelihood, as expected) —
the original's negative mean ΔNLL values were an artifact of scoring
already-consumed inputs and are WITHDRAWN (all 256 non-full ΔNLL values
changed, max shift 24.9; see `ERRATA.md`). Ridge still beats both ablations
on KL on every case (0.30–0.48 < 0.51–1.05 ≪ 2.09–4.09 at ctx16;
0.23–0.77 < 0.78–1.71 ≪ 6.00–8.07 at ctx64), so the fitted decoder still
shows cross-layer structure beyond trivial baselines — but the bar (copy)
remains low. Generic 4-bit quantization still beats ridge everywhere at
~1/6 the per-token backing bytes. KL and top-1 columns are CARRIED OVER WITH
PROOF: rerun equality gives max|KL_old−KL_new| = 0.0 (bit-identical, 256/256
rows), 0 top-1 agreement mismatches, identical argmax provenance — both arms
share conditioning, so the target shift cannot move them. (One prose slip in
the original table is corrected: ctx16 ridge KL per-case means are
0.30–0.48 in the original ROWS; "0.24" was a transcription error.)

## Integration (cache replacement consumed): TESTED, corrected gate (v2-2)

Poison test now compares POISONED RIDGE vs UNPOISONED RIDGE (odd-layer K
×100 on the same reconstructed cache): max-abs logit deltas 3.1–15.8 across
the 8 cases, consumed 8/8 (threshold 1e-3). The old poisoned-vs-full deltas
(8.1–20.5) are retained in `summary.json` as
`poison_vs_full_delta_disclosure_only` — they confound ridge approximation
error with the perturbation and are NOT the gate. Negative control
(acceptance test A3-neg): an installer that ignores the replacement yields
delta exactly 0.0 → correctly NOT consumed, so the gate is non-vacuous.

## Memory: backing bytes only, no resident-savings claim (v2-5)

- Executed FP32 full prefix: 46,080 B/tok (ctx16 = 737,280 B; ctx64 = 2,949,120 B).
- Hypothetical BF16 full: half (arithmetic, never mixed, not measured).
- Ridge retained BACKING bytes: 23,040 B/tok + fixed predictor 1,497,600 B.
  Totals: ctx16 → 1,866,240 B (2.5× full FP32); ctx64 → 2,972,160 B (still
  above full FP32 2,949,120 B). N\* = 65 is the EQUALITY point
  (total_B(65) == full(65)); strict backing-byte savings need N > 65.
- The runtime working cache in this repair is an EXPANDED full-float
  DynamicCache (reconstructed K/V materialized at full precision), and q4 is
  likewise dequantized to full float before use. Peak process RSS 1,338,976 KB
  (~1.3 GB, model + scoring instrumentation) is NOT a compression claim.
  No end-to-end resident memory savings are claimed.
- q4 payload case 8:16: 115,200 B backing (0.156× FP32).
- Candidate reconstruction build time (v2-3, measured, case 8:16):
  ridge 1.3 ms, q4 6.1 ms, zero 0.2 ms per prefix build. Full per-case build
  times in `summary.json:build_times_s` (40 entries).

## Timing (v2-4)

- Original pair (case 8:16, median of 3): full forward 0.176 s vs cached
  stepwise 0.518 s — marked NON-COMPARABLE as a cache-replacement speedup
  (full forward batches all positions in one kernel launch; stepwise pays
  per-step launch/cache overhead). Kept for disclosure only; do not cite.
- MATCHED timing, same 8 predicted positions (median of 3, exploratory, CPU
  contention): cached stepwise 0.490 s vs stepwise prefix-recomputation
  (fresh full forward per position, no cache) 1.145 s.

## Contexts: wrapping is conditional (v2-6)

Token base lengths: id8 = 55, id9 = 54, id10 = 54, id11 = 57. At ctx16 the
evaluated stream needs 25 tokens — NO case wraps. At ctx64 it needs 73
tokens — ALL FOUR test cases wrap (cyclic repetition active). The original
"near-deterministic repeats" language is restricted to ctx64; ctx16 cases are
naturally predictable-or-not on their own merits (ext windows are 9/9 unique
in all 8 cases). ΔNLL sign artifacts must not be explained by repetition;
they were an alignment bug (now fixed: all repaired mean ΔNLL ≥ ~0).

## Limitations

1. Only 4 authored test texts × 2 prefix lengths; ctx-64 continuations remain
   weakly discriminating (even zero-fill reaches up to 1.0 agreement).
2. Continuation K/V for new tokens is exact (only the prefix is compressed);
   error accumulation over long generation untested.
3. FP32 execution only; BF16 numbers are arithmetic, not measured.
4. Single seed, single λ=1e-3 (frozen, no sweep — by design). No retuning was
   done after observing repaired outcomes.
5. First continuation token S[ctx] is never evaluated as a target (boundary
   cost of preserving the original eight outputs).

## Reproduce

`PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 run.py`
then `PYTHONDONTWRITEBYTECODE=1 KV_HEAVY=1 python3 tests.py`.
Artifacts in this directory: `run.py`, `tests.py`, `per_case.jsonl` (320
shifted-v2 rows), `summary.json` (recomputed from rows), `REPORT.md` (this
file), `ERRATA.md`, `PROTOCOL_DELTA.md`, `source_hashes.json`,
`progress.json`, `predictor.pt`, `ORIGINAL_SHA256_BEFORE.txt`,
`ORIGINAL_SHA256_AFTER.txt`, `RED_ACCEPTANCE.txt`, `GREEN_LOG.txt`,
`RED_probe_offbyone_scratch.py` (measurement-bug demonstration; reads the
original module without executing its main or writing to `../kv`).
Original `../kv/` artifacts preserved unchanged (before/after SHA256 compared
in `ORIGINAL_SHA256_AFTER.txt`).
