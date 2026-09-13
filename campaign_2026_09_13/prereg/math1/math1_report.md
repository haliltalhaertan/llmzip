[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# MATH-1: analytic model of top-3 sign-code retrieval + validation on frozen LME-470 data

**[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION]**
Read-only `/mnt/c`; wrote only `/tmp/math1/`. No network (no LIT-CHECK items pursued).
Code: `/tmp/math1/math1.py` (panel+budget+mixing), `math1b/c/d.py` (follow-ups);
numbers: `/tmp/math1/math1_details.json`.

## 1. Model

### 1a. Level-1 exact model (the core deliverable)

Fix one question: `n` docs, Hamming distances `d in {0..b}^n`, gold set `G` (|G|=m),
top-`k` with `k=3`. The frozen 20-trial scheme draws iid continuous priorities `p_t`
and ranks by `lexsort((p_t, d))` (distance primary). Within any tied-distance block
the order is therefore a uniform random permutation, independent across trials and
of the distances: **conditional-uniform tie resolution**.

For gold `g` with distance `d_g`, let `S_g = #{i: d_i < d_g}` (strictly closer),
`T_g = #{i: d_i == d_g}` (tie bucket, gold included). By symmetry among the tied
docs for the `k - S_g` remaining slots:

- `P(g in top-k) = 0` if `S_g >= k`;
- `= 1` if `S_g + T_g <= k`;
- `= (k - S_g)/T_g` otherwise.

By linearity of expectation over golds (no joint structure needed):

> **E[fractional-R@3] = (1/m) sum_g f(S_g, T_g)**, with `f` as above.

This is an exact combinatorial identity given the distance profile — a DP over the
histogram in the degenerate (exact, non-iid) sense: it consumes the full empirical
`(S,T)` pairs, so it needs **zero** independence assumptions. The 20-trial measured
FR is an unbiased MC estimator of it (per-question SE = sqrt(Var_trial/20)).

### 1b. Level-2 independent-bits plug-in (strawman that prices the assumptions)

Assume non-gold distances iid `Binomial(b, p_hat)`, `p_hat` = empirical non-gold
mean/`b`, gold distances fixed; predicted FR = E[exact formula] over multinomial
`(S,T)` draws (MC, seed-fixed). This bakes in: (A1) bits independent across docs;
(A2) bits homogeneous; (A3) smooth unimodal histogram (no spikes/duplicates).

### 1c. Level-3 pairing -> width (for the mixing dose-response)

`Var(d) = sum_j Var(A_j) + 2 sum_pairs Cov(A_j,A_j') + cross-pair terms`, where
`A_j` = query-sign agreement indicator of output bit `j`. Block-2 rotation induces
within-pair covariance; pairing structure moves it, width moves burial, FR follows.

### Independence assumptions: explicit ledger

| # | Assumption | Where used | Status after validation |
|---|-----------|-----------|-------------------------|
| A0 | Priorities iid continuous -> uniform tie order | Level-1 proof | CONFIRMED (gates bit-exact; residuals at noise scale, §2) |
| A1 | Doc distances independent (no shared near-dups) | Level-2 only | REJECTED: archives contain related-doc clusters; retrievable-regime ties 7-13x over binomial (§2c) |
| A2 | Bits homogeneous/independent within a doc | Level-2 only | REJECTED: sign bits correlated (lattice + duplicates); avg left-tail OK (~1.0-1.1x) but joint (position x tie) structure missed |
| A3 | Pairing only re-labels bits (no cov change) | Level-3 null | REJECTED: within-pair cov matched 0.0009 < random 0.0193 < anti 0.0386 |

What A1/A2 cost: Level-2 overpredicts every arm by +4 to +26pp and **flips the
TOP48-RAND48 ranking** (predicts TOP48 by +2.9pp; measured -12.3pp). A1/A2 are the
most suspect assumptions; A0 is safe.

## 2. Validation on frozen LME-470 data

Panel arms (frozen-verbatim): NATIVE96; SPREAD48 = per-question variance-rank
stride `od[::2][:48]`; TOP48 = `od[:48]`; RAND48_s0 = fixed global `rng(12000)`
subset (cols in details json); BOT48 = `od[::-1][:48]`. All gates **bit-exact**:
native aggregate 0.5419751773049645 (anchor match to the digit), per-question
native max-diff 0.0 vs pilot; TOP48/RAND48_s0/BOT48 exact vs probe48
(0.34949468/0.47292553/0.42845745); SPREAD48 exact vs extra_arms (0.45029078);
mixing 43001 bit-exact vs corrections, 44001 bit-exact vs d4_report.

### 2a. Per-arm: predicted vs measured (exact model)

| arm | pred | meas | plugin | r (per-q) | MAE | RMSE | MC floor |
|-----|------|------|--------|-----------|-----|------|----------|
| NATIVE96 | 0.542134 | 0.541975 | 0.711250 | 0.99904 | 0.00410 | 0.01771 | 0.01927 |
| SPREAD48 | 0.452337 | 0.450291 | 0.546498 | 0.99784 | 0.00644 | 0.02631 | 0.02389 |
| TOP48 | 0.352057 | 0.349495 | 0.606507 | 0.99682 | 0.00870 | 0.03028 | 0.02517 |
| RAND48_s0 | 0.473147 | 0.472926 | 0.577986 | 0.99828 | 0.00602 | 0.02353 | 0.02145 |
| BOT48 | 0.429568 | 0.428457 | 0.469200 | 0.99881 | 0.00500 | 0.01997 | 0.02114 |

**TOP48 collapse reproduced from distance profiles alone: YES.** Exact model gap
TOP48-RAND48 = -12.11pp vs measured -12.34pp (residual 0.2pp = trial noise).
Per-question r >= 0.9968 everywhere; MAE 0.004-0.009 against effect sizes ~0.10.
Residual scale test Xobs/Xexp = 0.85/1.21/1.45/1.20/0.89 across arms — order unity
both directions, consistent with pure 20-trial MC noise (E[m]=e is a theorem, so
there is no fitted parameter to be wrong; an early z2=5.9 alarm was traced to
conditioning on tvar>0 with discrete trial laws — selection artifact, documented
in details json followup). **No structural misfit; none localized anywhere.**

### 2b. The paradox, quantified (means point the wrong way; ties mediate)

Mean-distance separation `sep = mean_nongold - mean_gold` favors TOP48 on **58.1%**
of questions (mean sep 10.47 vs 9.55) yet TOP48 wins FR on only **13.4%** —
the separation paradox in one line. d2-parity reproduction (TOP48 vs RAND 3-seed
mean): W/T/L = **91/179/200 exact**; strictly-closer wins **0.55** vs losses
**5.51 exact**; tie-mass wins 1.87 vs losses 4.50. Distance-profile means:
gold distance TOP48 13.44 vs RAND48 14.43 (TOP "wins"), but S 31.4 vs 38.4 and
T 10.3 vs 11.5 jointly bury it. The independence plug-in sides with the means
(+2.9pp for TOP48, wrong sign) because it cannot see tie spikes.

### 2c. Where the independence assumption dies (misfit localization)

Marginal left-tails match binomial (~1.0-1.1x all arms) — the failure is purely
**joint**: conditional on the retrievable regime (S<3, where FR is decided),
empirical tie buckets are **12.7x** (TOP48: 1.91 vs 0.15, n=327 golds) and
**6.7x** (RAND48: 1.60 vs 0.24, n=393) bigger than binomial. Retrievable golds
sit inside duplicate/spike clusters the iid model smooths away; TOP48 additionally
has fewer retrievable golds (327 vs 393). Budget plug-in degrades with b
(RAND16/32/64: +1.8/+6.1/+16.3pp overpredict) — wider codes, more spike mass missed.

### 2d. Budget curve (phenomenon 1)

Measured (frozen-def subsets, seed 12000): RAND 8/16/24/32/48/64/80 =
0.072/0.211/0.287/0.372/0.473/0.474/0.515; TOP =
0.090/0.169/0.214/0.255/0.349/0.432/0.491. RAND degrades ~0.14pp/bit (96->48)
steepening to ~0.6pp/bit (48->32): near-linear at the top, convex below — the
Level-1 model traces it exactly (exact==meas to noise at every b); the *shape*
comes from histograms (separation ~ b, width ~ sqrt(b)), which Level-2 renders
only qualitatively (see 2c for its quantitative failure).

## 3. Second-order test: pairing -> width -> burial (phenomenon 3)

LME mixing, seeds 43001/44001 (all frozen-verbatim incl. QR sign-fix order):

| seed | matched | random | antimatched |
|------|---------|--------|-------------|
| 43001 FR | 0.53883 | 0.50713 | 0.47774 |
| 44001 FR | 0.53883 | 0.52149 | 0.49287 |
| width (ng sd) 44001 | 4.96 | 5.16 | 5.37 |
| within-pair Cov 44001 | **0.00093** | **0.01927** | **0.03858** |
| P(S<3) 44001 | 0.489 | 0.474 | 0.462 |

Chain confirmed: disparity-ordered pairing -> monotone within-pair agreement
covariance -> monotone histogram width (the within-pair term 2*48*Cov accounts
for ~85% of the matched-vs-anti variance gap: 3.6 of 4.2) -> monotone burial
fraction -> monotone FR. Ties-at-gold in the retrievable regime are flat
(~1.2-1.3): mixing damage works through **width/burial, not ties** — the
complementary mediator to §2. The micro-step (why anti-matching gives *positive*
Cov: high-variance member dominates both pair outputs' signs) is heuristic;
the Cov->width->FR links are measured, not assumed.

## 4. Verdict + limits

**What the model explains.** The Level-1 identity closes the retrieval step
entirely: given any arm's distance profile, FR follows with no free parameters
(r>=0.997, MAE<=0.009, residuals at MC scale). All three phenomena relocate to
*why profiles differ*, and the follow-ups answer each: (1) budget shape =
separation-vs-width scaling of subset histograms; (2) TOP48 collapse = tie-spike
burial invisible to means (paradox dissolved: sep favors TOP on 58% of questions,
FR on 13%); (3) mixing dose-response = within-pair covariance -> width ->
burial, with ties flat.

**What it does not explain.** Why variance-selected bits concentrate tie mass
(the bit-level mechanism: low-margin bits -> query-agreement ~ coin flip ->
lattice pile-up — supported by dg/T numbers but not derived from bit
distributions here); why archives contain the near-duplicate clusters that make
A1 fail (a data property, not a model property); the sign of the anti-matched
covariance from first principles (heuristic only).

**Most likely culprit for any residual misfit.** A1 (cross-doc independence):
related docs share distances, inflating ties exactly where golds sit. The R-test
shows no residual misfit at Level-1, so this bites only Level-2-style forward
models — any future predictor must model the duplicate-cluster process (e.g. a
two-component histogram: spike + bulk), not a single binomial.

**Discriminating data.** (i) Per-bit query-agreement margins for TOP vs RAND bits
(tests the lattice-pile-up story); (ii) archive deduplication ablation: if
removing near-dup docs shrinks retrievable-regime T toward binomial, A1 is the
confirmed culprit; (iii) more mixing seeds x Cov/width/FR triple (tests the
Cov->width link out of sample); (iv) LoCoMo-1535 rerun (tests benchmark scope).

## 5. Reproducibility

`python3 /tmp/math1/math1.py` (~25 s; reloads 470 pkls; writes
`math1_details.json`); then `math1b.py`, `math1c.py`, `math1d.py` (import from
`math1.py`). Frozen sources used verbatim: `deney1_lme.py` tie scheme
(`5_100_000 + lex*100_000 + t*100 + 99`, `lexsort((p, d))`, K=3, NT=20),
`pilot_axis_attack.py` arm defs (stable-argsort variance order, `rng(12000)`),
`pilot_extra_arms.py` RANKSTRIDE48, `d4_lme.py` mixing perms/QR. All gates in §2
bit-exact (0.0 / last-digit). LIT-CHECK items: none (no external literature used).

MATH1_VERDICT: EXACT conditional-uniform tie-model reproduces all panel FRs
(r>=0.997, MAE<=0.009, residuals at MC-noise scale) including the full -12.3pp
TOP48 collapse from profiles alone; independence plug-in fails sign (+2.9pp) and
level (+5..+26pp) — duplicate-spike ties are the mediator; mixing chain
pairing->Cov(0.001/0.019/0.039)->width->burial confirmed on LME seeds 43001/44001.
