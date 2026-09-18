[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# PREDICTION.md — frozen rule, written BEFORE any cross-benchmark measurement

**Freeze status: FROZEN.** Written after PerLTQA levels+geometry (steps 1-3), before any
LongMemEval / REALTALK / LoCoMo number was computed. This file is never edited after
freezing. Corrections, if any, go in `CROSS_CHECK.md` § "Post-freeze corrections".

## 0. Gates passed before anything below was written (VERIFIED)

- Control: PerLTQA float FR@3 `0.551692074528853` == frozen reference exactly;
  SIGN `0.48894479616364206`; Delta `-6.274727836521104` pp (frozen `-6.275`).
  Sections reproduce the coordinator to 6 dp. `evidence/control.json`, `control.py:60-95`.
- Independent gate: my per-gold competition rows reproduce the R2 audit's expected
  Spearman targets (`R2_COMPETITION_RERUN_CONTRACT.md` "Expected independent-audit
  targets") to <=1.2e-4 on all four sections and overall. `step3b.py:30-44`.

## 1. The statistic (gold-free, Delta-free, deployable at query time)

For archive `C` (N x 96, already centered; VERIFIED col-mean absmax 1.16e-16) let

    v_j = mean_i(C_ij^2)                   (spec axis statistic, R2 contract)

For query vector `qC` (96,) let `w_j = qC_j^2`. Define

    ALIGN(q) = cos( w , v ) = (w . v) / (||w|| * ||v||)

ALIGN is the cosine between the query's per-axis energy profile and the archive's
per-axis energy profile. It uses **no gold labels and no Delta**. It is computable
from the query and the archive alone.

Interpretation: ALIGN high = the query puts its energy exactly where the archive already
has its variance. ALIGN low = the query's energy sits on axes the archive treats as
low-variance.

## 2. The mechanism this rule encodes (what the LEVELS selected)

SIGN96 weights every axis equally (one bit each). Centered-float cosine weights each
axis by magnitude, so it is dominated by high-variance axes. Therefore SIGN96 should
beat float exactly when the discriminative information separating gold from rivals
lives on axes that float **under**-weights, i.e. the low-variance axes.

The PerLTQA levels say precisely this (VERIFIED, `evidence/levels_summary.json`):
`STRICT_GAP = STRICT_TOP64 - STRICT_BOT64` is **positive only in profile** (+4.733,
median +1.0, 54.05% of queries > 0), the only section where SIGN wins (+20.355 pp).
All three losing sections are negative (events -21.880, social -25.109, dialogues
-74.826). Positive gap == gold faces MORE rivals on TOP64 than on BOT64 == the
low-variance arm is the one that discriminates.

Consistently (VERIFIED): profile queries have the lowest ALIGN of the four sections,
and within each archive profile ALIGN < events ALIGN in **29/30** archives.

## 3. PerLTQA fitted values (in-sample; NOT evidence for the rule)

| section | n | Delta pp | mean ALIGN | STRICT_GAP | TIE_GAP |
|---|---:|---:|---:|---:|---:|
| profile | 333 | **+20.355** | **0.4119** | **+4.733** | **+3.207** |
| dialogues | 2742 | -1.502 | 0.4941 | -74.826 | -3.258 |
| social_relationship | 844 | -0.780 | 0.5290 | -25.109 | -6.250 |
| events | 4346 | -12.394 | 0.5301 | -21.880 | -5.509 |

Threshold frozen at the midpoint of the observed gap between the winning section and
the nearest losing section: (0.4119 + 0.4941)/2 = **THETA = 0.4530**.

## 4. THE RULE (frozen)

> **R:** For any stratum S of queries evaluated against its own archive,
> predict `sign(Delta_S) = +1` if `mean_{q in S} ALIGN(q) < 0.4530`, and
> `sign(Delta_S) = -1` if `mean ALIGN(q) > 0.4530`.

Scope declared in advance: **R is a STRATUM-level rule, not a per-query rule.** I am
declaring this before testing because the closely related per-query statistics measured
in step 3 already correlate with Delta at essentially zero within PerLTQA
(rho(Delta, EFFW) = -0.0127, rho(Delta, qPR) within sections |rho| <= 0.033;
`step3b.py` output). A per-query form of R is therefore *predicted by me to fail* and
is not claimed.

## 5. Falsifiable predictions, stated before measurement

- **P2 (LongMemEval, out-of-sample).** LME SIGN beats float by +10.038 pp (frozen).
  R therefore requires **mean ALIGN over the 470 LME queries < 0.4530**.
  *Falsified if LME mean ALIGN > 0.4530.*
- **P3 (REALTALK, out-of-sample).** REALTALK SIGN wins +5.224 pp (frozen).
  R requires **mean ALIGN over REALTALK queries < 0.4530**.
  *Falsified if REALTALK mean ALIGN > 0.4530.*
- **P4 (monotonicity, both benchmarks).** Stratify each benchmark's queries into ALIGN
  deciles. R requires Spearman(decile mean ALIGN, decile mean Delta) **< 0**.
  *Falsified if >= 0 in either benchmark.*
- **P5 (sharpest, riskiest).** Any decile whose mean ALIGN > 0.4530 must have mean
  Delta < 0; any decile with mean ALIGN < 0.4530 must have mean Delta > 0.
  Scored as accuracy over the 20 deciles (10 LME + 10 REALTALK) against the trivial
  majority-class baseline for those deciles. *R is dead if it does not beat the
  majority baseline.*
- **P6 (REALTALK per-chat strata).** Rank the 10 REALTALK chats by mean ALIGN. R
  requires Spearman(chat ALIGN, chat Delta) < 0.
- **P7 (LoCoMo).** Same as P4 at conversation level if a per-query float surface can be
  built from committed caches. If it cannot, record **untestable** — not support.

## 6. Declared failure modes (written in advance, so I cannot claim them post-hoc)

1. THETA = 0.4530 sits in a **narrow** window: the winning section is at 0.4119 and the
   nearest loser at 0.4941. An absolute threshold calibrated on a 0.08-wide gap from a
   single benchmark is fragile. If LME/REALTALK ALIGN levels are not comparable across
   benchmarks (different embedders/archive sizes), P2/P3 can fail for a scaling reason
   rather than a mechanism reason. **I commit in advance: if P2 or P3 fails, I report
   the absolute-threshold form of R as DEAD and do not rescale THETA to rescue it.**
   Only the *ordinal* predictions P4/P6 can survive separately, and I must report the
   absolute form as killed even if the ordinal form survives.
2. PerLTQA's winning section is a single section with n=333 out of 8265 (4.0%). R is
   effectively calibrated on one stratum. This is exactly the failure mode that killed
   boundary-competition density.
3. If R predicts a reversal (a stratum with Delta > 0) inside LME/REALTALK where the
   observed stratum Delta is > 0 anyway (because those benchmarks are overall positive),
   P5 is **trivially** satisfied. I must therefore report P5 against the majority
   baseline, not as raw accuracy.

## 7. Adversarial self-check declared in advance

The assumption that would most damage the conclusion of § 2: that `STRICT_GAP > 0` in
profile is an artifact of **gold multiplicity** or of the all-competitor convention
(dialogues has mean gold_n = 9.92 while profile/events/social are single-gold). Test to
run: recompute all gaps with the non-gold sensitivity variant and confirm profile stays
positive and the ordering is unchanged. (Already run: `STRICT_GAP_ng` profile +4.733,
events -21.880, social -25.109, dialogues -74.795 — identical to 3 dp for the
single-gold sections and within 0.03 for dialogues, so multiplicity is not the driver.)

Second adversarial test to run in cross-check: **is ALIGN just a proxy for query norm or
for section identity?** If ALIGN's cross-benchmark performance is entirely explained by
`qnorm`, report ALIGN as redundant.
