# PROTOCOL_DELTA — measurement repair v2 (design frozen, measurement fixed)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Base: `../kv/PROTOCOL.md` (9bef901a…). Nothing below changes the candidate or
scientific design: same model dir/rev, same 12 fixtures and train/val/test
split, same arms (full/ridge/q4/zero/copy + timing E), same ridge choice
(per-KV-head 64→64, λ=1e-3, intercept unpenalized, float64 closed form,
480 train token samples), same seeds/threads/budget rules. No new
model/fixture/arm/lambda/width choices; no retuning (validation never refit).

## v2-1 Target alignment (critical fix)

- Was: `true = cont[t]` scored against `logits[t]` emitted after consuming
  `cont[t]` (off-by-one; scored already-consumed input).
- Now: stream extended to `ctx+9` (`build_case_ids` returns
  prefix/cont_inputs/targets/mask); `true = tgt[t] = S[ctx+t+1]`; rows marked
  `"align": "shifted-v2"` with `cont_input`, `pred_index = ctx+t+1`,
  `context_len = ctx+t+1`. The eight continuation INPUTS (and hence all
  emitted logits, KL inputs, top-1 inputs, MSE, weights) are unchanged.
- Proof: acceptance test A1 (cached stepwise == shifted full-sequence
  teacher forcing at all 8 positions incl. true-token log-probs, nonrepeating
  ext window asserted); A2 (old target fails at 8/8 steps).
- Rejected alternative: first-prefix-logit design (score S[ctx] from the
  prefix forward) would evaluate different outputs/positions and break
  comparability of KL/top-1 columns with the original run; disclosed here,
  not implemented.

## v2-2 Poison gate (confound removed)

- Was: poisoned-ridge logits vs FULL logits (mixes ridge approximation error
  into the perturbation signal).
- Now: gate is `poison_delta(poisoned_ridge_step0, unpoisoned_ridge_step0) >
  1e-3`; old comparison kept as disclosure-only field. Added negative
  control (A3-neg): an installer ignoring the replacement gives delta 0.0 →
  NOT consumed, proving the gate is non-vacuous. Rerun across all 8 cases:
  consumed 8/8.

## v2-3 Build time (was computed, discarded)

- `run_case_arm` always returned `t_build`; the original caller dropped it.
  Now recorded per (case, arm) in rows' summary (`build_s`) and
  `summary.json:build_times_s` (40 entries). Values are candidate
  reconstruction time only (prefix-cache + stepping timed separately).

## v2-4 Timing comparability

- Was: one full forward of prefix+continuation vs cached stepwise, presented
  as arm E timing.
- Now: that pair is kept but labeled NON-COMPARABLE (batching/work differ).
  Added matched pair for the same 8 predicted positions: cached stepwise vs
  stepwise prefix-recomputation (fresh no-cache forward per position).
  Both exploratory (single-thread CPU, contention noted).

## v2-5 Memory accounting (wording narrowed, formulas kept)

- 1,497,600 predictor bytes, 46,080/23,040 B/tok, q4 payload formula:
  unchanged. N\*=65 restated as the EQUALITY point (strict savings N>65).
- Added and enforced in code comments: runtime working caches (ridge
  reconstruction AND q4) are expanded full-float DynamicCaches; peak RSS
  (≈1.3 GB incl. model + instrumentation) is not a compression claim; no
  end-to-end resident memory savings claimed.

## v2-6 Wrapping (conditional, logged per case)

- Was: contexts described as cyclic, implying repeats everywhere.
- Now: `base_len` + `wraps = (base_len < ctx+9)` logged per case. Measured:
  ctx16 (needs 25) never wraps; ctx64 (needs 73) wraps for all test IDs
  (base 54/55/54/57). No blanket repeat claim; naturally-predictable cases
  stay on their own merits.

## Row schema change (additive, guarded)

New required keys: `cont_input`, `true_token` (shifted), `pred_index`,
`context_len`, `align`. The runner refuses to append to a `per_case.jsonl`
containing foreign-`align` rows, and asserts exactly 320 unique
`(text_id, ctx, arm, step)` keys before writing `summary.json`, which is
recomputed from the rows (not from in-memory aggregates).
