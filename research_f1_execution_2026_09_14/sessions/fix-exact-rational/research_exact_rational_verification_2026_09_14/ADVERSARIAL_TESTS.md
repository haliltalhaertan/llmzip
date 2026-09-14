[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Adversarial tests — PREPARED, NOT ACCEPTED

Runner: `test_exact_rational.py` (`python3 test_exact_rational.py`, exit 0 = pass).
Evidence: `evidence/results.json` (written by the runner: per-case expected/observed,
float-control observations, module sha256, Python version, UTC timestamp).
Observed this session (VERIFIED — runner stdout + `results.json` summary):
**31/31 exact checks passed; 3 cases expose the float control; exit 0.**
Second route (VERIFIED): the branch's own vendored outcome-free controls run unmodified from a
real-file mirror layout (`/tmp/t4f1_layout`, copies verified same-sha256) give
**10/10 behaved correctly**.

## Design principle

Each test states an independently hand-computed `fractions.Fraction` expectation (the oracle is
this file's arithmetic, never the implementation). Discriminating cases additionally require the
deliberately float-based negative control (`float_sign` / `float_classify` / naive-fold
`float_mean_naive_fold` defined in the runner) to give the WRONG answer; if it ever agrees
everywhere the suite exits 2 ("tests too weak"). A violation of binding 8 that any case would
expose is named in the last column.

| Case | Synthetic input (authored here) | Exact expectation | Violation it would expose |
| --- | --- | --- | --- |
| T1 | `D_t = 1/10^400` all tiers (`float() == 0.0`, VERIFIED) | `FULL_REPLICATION`, `sign == +1` | Rounding a tiny positive to zero/tie; classifying from a float aggregate |
| T2 | `D_t = -1/10^400` all tiers | `NO_REPLICATION`, `sign == -1` | Symmetric: tiny negative rounded to zero |
| T3a–e | Exact `0`: mixed profile with a zero tier; all-zero; 3 positives + 1 zero; canceling-pair mean | Hetero / No-rep / Hetero (zero flips Full); mean `== 0` | Nudging ties to a sign; treating zero as positive; epsilon-thresholding |
| T4 | Tiers `1/10^400` vs `2/10^400` (`float` equal, VERIFIED) | Distinguished; `FULL_REPLICATION` | Below-float-resolution tiers collapsed to the same class |
| T5 | `[1/10, 10^16, -10^16]` in 3 orders | Exact mean `1/30` all orders; naive-fold float gives `0.0, 0.0333, 0.0333` (VERIFIED) | Order-dependent float accumulation feeding the sign |
| T7a–d | All-positive / all-non-positive / mixed / single `-1/10^30` among positives | Full / No-rep / Hetero / Hetero | Wrong category boundaries (§6 partition) |
| T8 | `gold_counts [3,4,6]`, deltas `1/3,-1/4,1/6` | Mean `1/12`; bound `180`; `180 % 12 == 0` | Denominator not dividing `5·n_t·lcm` |
| T9 | Synthetic cohort + row with `retrieved_top3_ids ["g1","x","y"]`, gold `{g1,g2,g3}` | `fraction == 1/3` from discrete IDs; `isinstance Fraction` | Runner float aggregate used as sign input |
| T10 | `rational_payload(1/10^400)` | `sign == +1` while `decimal_18` is all zeros | Display rounding leaking into the decision |
| T11 | Deltas `[1/10^400, 0, -1/7]` | `W/T/L == 1/1/1`; `W/(W+L) == 1/2` | Tiny win miscounted as tie in win/tie/loss profile |
| T12 | Mean of `1/3, -1/6` | `1/12` | Inexact mean arithmetic |

## Negative control definition (the violation model)

`float_sign(x)` = sign of `float(x)`; `float_classify` applies the §6 category logic to those
float signs; `float_mean_naive_fold` accumulates `acc += float(v)` left to right. This is exactly
what a binding-8-violating implementation would do. Observed (VERIFIED): it returns
`NO_REPLICATION` for T1 (exact: Full), `0` for T1b (exact: +1), and `HETEROGENEOUS` for T4c
(exact: Full) — i.e. the suite fails the float version on 3 cases, so it is not flattering.

## Lesson recorded during the run (VERIFIED)

The first version of T5b used builtin `sum()` and FAILED (all orders gave `0.0333…`): on modern
CPython (3.14.4 here) builtin `sum()` uses compensated summation that masks order effects. The
hazard is real only for the naive accumulator pattern, so the suite models that pattern
explicitly and documents the choice in code. An implementation passing T5a is immune under both
models; a float implementation is exposed at least under the naive one.

## Scope limits

Synthetic inputs only; `main()` (which demands the sealed cohort + 96 archive CSVs) is never
invoked. Real-data behaviour, freezing, audit, and merge remain open — see `DISPOSITION.md`.
