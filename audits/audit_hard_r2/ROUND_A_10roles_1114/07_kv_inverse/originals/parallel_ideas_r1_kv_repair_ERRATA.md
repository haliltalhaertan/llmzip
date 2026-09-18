# ERRATA — what the alignment bug affected and did not affect

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Original: `../kv/` (`run.py` 81e0349a…, `REPORT.md` e98ba624…). Repaired:
this directory (`run.py`, `per_case.jsonl` with `"align": "shifted-v2"`).
Root cause: `full_logits[t]` / `arm_logits[t]` are emitted AFTER consuming
`cont[t]` (original `run.py:409-425`), hence predict the NEXT token; `dnll`
scored `true = cont[t]` (original `run.py:436`), i.e. the already-consumed
input. Every published ΔNLL was therefore an invalid next-token NLL.

## WITHDRAWN (affected): all ΔNLL numbers in the original REPORT/summary/rows

- All 256 non-full ΔNLL values changed (0/256 unchanged; max abs shift 24.9).
  The original's negative mean ΔNLL values (e.g. ridge ctx64 −2.93…−3.85,
  zero ctx64 −1.69…−4.05) are withdrawn: with valid next-token targets every
  arm mean ΔNLL is ≥ ~0 (ridge ctx16 +0.12…+0.62, ctx64 +0.30…+0.83; q4
  −0.01…+0.12; zero +0.69…+1.87; copy +1.87…+8.26 per-case-mean ranges).
- The sentence "Negative ΔNLL means the arm assigned slightly higher
  likelihood to the (highly predictable, cyclic) true token" is withdrawn
  together with the numbers it interpreted. Repetition must not be invoked to
  explain ΔNLL signs; the sign pattern was an alignment artifact.
- `top1_true_full` / `top1_true_arm` provenance columns in old rows pointed
  argmax values at mislabeled targets; repaired rows re-emit them against
  shifted targets (argmax LOGITS themselves are unchanged — see below).

## CARRIED OVER WITH PROOF (unaffected): KL, top-1 agreement, MSE, bytes

- KL(full||arm): rerun equality over all 256 non-full identity-keyed rows
  gives max|KL_old − KL_new| = 0.0 (bit-identical). Carried over; the
  qualitative order ridge < zero ≪ copy per case is unchanged.
- top1_agree: 0 mismatches over 256 rows; argmax provenance identical.
  Carried over.
- prefix MSE (odd), predictor bytes (1,497,600), q4 payload bytes, per-token
  byte formulas: computed from prefix caches / packing only, independent of
  continuation targets. Unaffected (values identical).
- Fitted predictor weights: training uses prefix caches only; unchanged
  procedure/seed/pool. (Repaired `predictor.pt` in this directory is a fresh
  fit of the same frozen procedure, not a retune.)
- One prose-only correction inside carried-over territory: the original
  REPORT's ctx16 ridge KL range "0.24–0.48" does not match its own rows
  (per-case means 0.304–0.482); corrected to 0.30–0.48. Rows were always
  ground truth; the "0.24" was transcription.

## SUPERSEDED (method, not numbers): poison gate, timing, memory wording

- Poison gate: old poisoned-vs-full deltas (8.1–20.5) are superseded as a
  gate by POISONED-RIDGE-vs-UNPOISONED-RIDGE deltas (3.1–15.8, consumed 8/8);
  old values retained only as `poison_vs_full_delta_disclosure_only`.
- Timing: the original full-forward-vs-cached-stepwise pair is superseded as
  a speedup comparison (marked NON-COMPARABLE); replaced for that purpose by
  the matched stepwise pair (cached 0.490 s vs prefix-recompute 1.145 s,
  medians, exploratory). Raw original numbers are disclosed, not deleted.
- Memory: crossover "N\*=65" is reworded from implied-savings to the equality
  point (strict backing-byte savings need N > 65); added explicit
  expanded-working-cache / dequantized-q4 / RSS disclosures. Byte FORMULAS
  are unchanged; only the claim scope shrank.
- Context cyclicity: blanket "near-deterministic repeats" restricted to
  ctx64 (all 4 test IDs wrap: base 54–57 < 73 needed); ctx16 never wraps
  (25 needed ≤ 54). No numbers change; interpretation scope narrows.

## Boundary disclosure (what the repair costs)

Preserving the original eight outputs means the first continuation token
S[ctx] is never evaluated as a target, and all evaluated predictions enjoy
one extra token of context (ctx+1..ctx+8). The alternative (scoring S[ctx]
via the prefix forward's first-logit) would evaluate different outputs and
was rejected; see `PROTOCOL_DELTA.md`.
