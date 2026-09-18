[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# VERDICT.md

## Did the mechanism question move?

**Yes — one of the two surviving pictures is dead, and a third candidate died with it.**
The move is negative, and it is a real constraint on every future story.

### What was decided

1. **The LEVELS were measured** (the thing the two pictures disagreed about). Within PerLTQA
   the answer is clean: **profile — the only SIGN-winning section — is the only section with a
   positive per-gold competition gap** (STRICT_GAP +4.733, TIE_GAP +3.207; all three losing
   sections negative; median and frac>0 agree; within-archive paired 25/30). The picture
   requiring the SIGN-winning section to sit at a *negative* gap is **killed on levels**.

2. **The surviving picture was then killed by the cross-benchmark levels.** Same code, same
   definitions: LongMemEval has mean STRICT_GAP **−19.17** and Delta **+10.05 pp**; PerLTQA has
   mean STRICT_GAP **−38.70** and Delta **−6.27 pp**. *Same gap sign, opposite Delta sign.*
   LoCoMo agrees with LME (gap −5.78, Delta +6.66). A single counterexample suffices:
   **the level of the competition gap does not determine the sign of Delta.**
   A stratum rule built on it scores 11/24 = 45.8% against a 79.2% majority baseline.

3. **So both surviving pictures are now dead**, one by its own prediction (negative gap at the
   winner — contradicted inside PerLTQA) and the other by generalisation (positive-gap⇒SIGN-wins
   — contradicted by LME/LoCoMo). The levels measurement was decisive in the sense that mattered:
   it did not leave a winner standing.

4. **The new rule R (ALIGN) was frozen and cleanly killed**, 3/3 benchmarks. It predicted a
   negative Delta for 25 of 30 out-of-sample deciles; **zero** of those 30 deciles are negative.
   Reported dead, not rescaled, not retreated to an ordinal form (which also fails, P4 2/3 FAIL,
   P6 FAIL). Sixth story killed.

### The durable finding

**The slope is stable across benchmarks; the level is not.**

- `rho(Delta, STRICT_GAP)` > 0 in all four benchmarks (+0.142 / +0.098 / +0.254 / +0.103),
  two of which match published independent-audit targets.
- `rho(Delta, strict_BOT64)` is the tightest statistic yet measured in this programme:
  **−0.185 / −0.179 / −0.195 / −0.308** — same sign, same order of magnitude, four benchmarks,
  three different embedding corpora.
- But each benchmark carries an **additive offset** that no competition statistic sees. Grant an
  oracle that centers the gap within its own benchmark and stratum accuracy is still 58.3%
  against a 79.2% baseline.

This is a sharper statement of the E1 line's "query-archive ranking-regime interaction": the
*within-benchmark* ordering of Delta by competition geometry is real and reproducible; the
*between-benchmark* offset that sets the sign is a separate, unmeasured quantity. Every future
mechanism story must explain the offset, not the ordering. Four stories in a row (variance
heterogeneity, hubness, boundary-competition density, ALIGN) have explained the ordering and
died on the offset.

### Honest scope

- PerLTQA's SIGN-winning stratum is n=333 of 8265 (4.0%). Any rule calibrated there is calibrated
  on one small stratum of one benchmark — the exact fragility that killed the previous story, and
  the reason I declared it in `PREDICTION.md` § 6.2 before testing.
- `LEVELS.md` § 4's geometric portrait of a profile query (low norm 0.892 vs 0.935; concentrated,
  qPR 9.1 vs 11.8; energy off the high-variance axes, ALIGN 0.412 vs 0.530 paired 29/30; long
  gold vectors 1.075x paired 30/30; float margin negative, paired 30/30) is **VERIFIED and
  descriptively real** — and predictively worthless outside PerLTQA. Both halves are the finding.

## The next decisive measurement

**Measure the per-benchmark offset directly, by making a benchmark change sign under a controlled
intervention while its archives are held fixed.**

Concretely, in priority order:

1. **Axis-budget sweep.** For each benchmark compute FR@3 for SIGN restricted to the top-m axes
   for m = 8, 16, 24, 32, 48, 64, 80, 96, against float on the same m axes. The offset hypothesis
   predicts each benchmark has a characteristic **crossover m\*** where Delta changes sign, and
   that PerLTQA's m\* lies above 96 while LME's lies below. If m\* exists and is archive-invariant
   within a benchmark but varies between them, the offset is an *axis-budget* quantity and is
   measurable from `C` alone. The frozen caches already contain TOP/BOT/SPREAD/RANDOM arms at
   k = 48/64/80 (`step2_eval.py:31-39`) — the sweep is nearly free and needs no new representation.

2. **The rank-vs-magnitude decomposition.** SIGN discards magnitude and keeps orthant. Score a
   third arm: **float cosine on sign-quantised vectors with restored per-document norms**
   (`sign(C) * ||C_i||`). If this arm tracks SIGN on LME but float on PerLTQA, the offset is
   *document-norm informativeness* — consistent with the one geometric statistic that was
   strongly paired in PerLTQA (`gold_norm_rel` 30/30) yet sign-inconsistent across benchmarks
   (−0.094 / +0.003 / +0.040), i.e. exactly an offset-like variable.

3. **Do NOT run another per-query correlational rule.** Six have now failed the same way. The
   next measurement must be an *intervention* on the representation with the archives held fixed,
   not another statistic correlated with Delta.

## Reproduction

`control.py` (gate 1) → `levels.py` (levels + geometry) → `step3b.py` (gate 2 + gold-free stats)
→ **`PREDICTION.md` frozen** → `cross_check.py` (LME/REALTALK) → `step6_levels_xbench.py`
(levels out-of-sample + adversarial) → `step7_slope_vs_level.py` → `step8_locomo.py`.
Evidence in `evidence/`. Read-only on all caches; no git operations; Task4F1 seal untouched.
