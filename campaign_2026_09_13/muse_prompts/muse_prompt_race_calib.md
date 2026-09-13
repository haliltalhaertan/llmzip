# Muse session — RACE-1: DECISION MEMO + CALIBRATION NOTEBOOK (pre-seal)

You are the deciding analyst for the twelve-byte race's two open items, and you EXECUTE the
pre-seal calibration. Read-only /mnt/c; write only /tmp/rb1/. No network. This decides; the
orchestrator will adopt your numbers as literals.

## Context

Draft: /mnt/c/Users/MDP/dev/llmzip-work/DRAFT_PREREG_TWELVE_BYTE_RACE_v2.md (v2; §4/§8.12 = your
mandate). Evidence: prereg_race_2026-09-13/{pre1,pre2,math1,math2}/ reports; round3 missing_analyses
m1 (`missing1_kill_null.md/json`: no-edge vs-best-of-10 ≈ −1.62pp sd 1.38 (LME) / −1.20 sd 0.93
(LoCoMo), range to +1.91); deney1 details JSONs (per_q_test arrays: RANDOM32/48/64 panels, 10
seeds each, both benchmarks).

## Task 1 — Decision memo D1 (RaBitQ 32-dim rule)

Ratify or amend: **spread-32 (per-archive variance rank-linspace) = PRIMARY; random-32
(3 seeds) = SECONDARY sensitivity; TOP32 = curve point only (anti-optimality expected)**;
centering = same centered C; float query through same reduction; rotation panel = 3 seeds
(literals below). Give the formal rationale note (+ the erratum vs the HR-name `TOP32_RABITQ32`).
If you disagree, say so and specify the alternative cleanly.

## Task 2 — Decision memo D2 + EXECUTE the calibration notebook

Goal (F4): numeric kill/promote lines for the race, calibrated to a no-edge null over the FULL
sealed competitor set (not just best-of-10). Competitor set (v2 §5): random panels 10 seeds × 3
widths; SPREAD fixed (3 widths); BOT LoCoMo (3 widths); TOP control; RaBitQ32 (primary, 3 rotations
× spread-32) + secondary variants; PQ. ~27+ competitor looks/benchmark.

Method suggestions (choose, justify, execute; no race data needed):
- Model each competitor's aggregate mean as Gaussian with per-seed sd estimated from the existing
  random panels (LME ~1.3pp; LoCoMo ~0.9pp ranges: recompute exactly).
- Null for the primary contrast `SIGN − max_comp(·)`: simulate (or compute via order statistics)
  with (i) independence across competitor looks, and (ii) a conservative correlation model (e.g.,
  equicorrelation ρ estimated from data or set conservatively ≥0; report both).
- Output: the null distribution (mean/sd/percentiles) of the primary contrast per benchmark;
  propose LITERAL lines: kill line (SIGN loses when observed gap below null's Xth percentile —
  state X and why), promote line (require gap above null's Yth percentile AND ≥ observed-lift
  consistency), the complete 16-cell decision table (4 zones × 2 benchmarks → action), and the
  family-wise rule confirmation (Bonferroni across 2 benchmarks).
- Also: recompute the "true premium needed to clear" figure under the extended null (v2 says
  ≈+2.6pp for vs-best-of-10; update for the full set) and the required footnote wording.

## Frozen literals (ratify or amend; runners parameterize from ONE constants block)

- Random panels: `93000 + 10*width_idx + j`, j=0..9, width_idx {0:48b, 1:64b, 2:80b}.
- RaBitQ rotation seeds: [94101, 94102, 94103]; random-32 axes seeds: [94201, 94202, 94203].
- Bootstrap: B=5000, seed 94301 (+ offset per metric, stated).
- Tie draws: frozen as always (20 trials; same formulas as pilots).

## Outputs

/tmp/rb1/d1_decision_memo.md, /tmp/rb1/d2_calibration_notebook.md (+ calib.py, calib_details.json),
/tmp/rb1/frozen_literals.json. Gate: reproduce m1 numbers from its json (tol 0.05pp). Print
RB1_VERDICT: <D1 ratified/amended; kill/promote literals per benchmark; premium-needed figure>.
~1-2 hours scale.
