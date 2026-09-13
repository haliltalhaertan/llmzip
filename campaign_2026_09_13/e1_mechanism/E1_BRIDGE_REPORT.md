# E1 bridge analysis — variance-tail polarity vs SIGN–float direction

Labels: **[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

Source snapshot: `findings/campaign-2026-09-13 @ 8f6e0fab4c2fb2eeb8dcd5087376a6736e1865f1`.

## Why this bridge exists

The new PerLTQA reversal changes the research question. The useful question is no longer “does SIGN96 beat float96?” but “what property changes the sign of that comparison?”

A striking already-observed pattern connects two previously separate result families:

- SIGN96 vs centered-float96;
- low-variance (BOT) vs high-variance (TOP) axis subsets.

Define a descriptive polarity score `P_k = FR(BOT_k) - FR(TOP_k)`.

## Existing-result bridge table

| unit | SIGN−float (pp) | P_k = BOT−TOP (pp) | k |
|---|---:|---:|---:|
| LongMemEval | +10.038 | +7.896 | 48 |
| REALTALK | +5.224 | +2.207 | 64 |
| PerLTQA profile | +20.435 | +18.240 | 64 |
| PerLTQA social | −0.806 | −23.590 | 64 |
| PerLTQA events | −12.411 | −17.640 | 64 |
| PerLTQA dialogues | −1.476 | −1.360 | 64 |

Observed sign concordance: **6/6**. Descriptive Pearson `r=0.855`; Spearman `rho=0.829`.

These are **not hypothesis-test p-values** and must not be presented as such. The table was noticed after seeing the outcomes, PerLTQA sections are not independent, LME uses k=48 while the others use k=64, and several PerLTQA summary values are rounded.

## Negative finding: tie rate alone is insufficient

Known top-3-boundary tie shares are approximately LME 23.4%, REALTALK 35.46%, PerLTQA 29.20%. Yet SIGN−float is positive on LME/REALTALK and negative on PerLTQA. Therefore a scalar “more Hamming ties => SIGN advantage” story is already falsified at benchmark level.

Tie **geometry** can still matter; the earlier D2 result concerns strictly-closer rivals and gold-distance tie mass, not merely the aggregate boundary-tie rate.

## Working mechanism hypothesis

A better working hypothesis is:

> SIGN helps when task-relevant discrimination is disproportionately carried by the lower-variance / coordinate-heterogeneous part of C96, and hurts when the high-variance tail carries the relevant discrimination.

This unifies:
- the TOP-variance collapse on LME;
- BOT dominance on LoCoMo;
- BOT>TOP on REALTALK;
- the PerLTQA profile counter-win (BOT>TOP, SIGN wins strongly);
- the PerLTQA event reversal (TOP>BOT, float wins strongly);
- catastrophic damage from Haar mixing, which flattens coordinate heterogeneity.

This is a hypothesis, not yet a causal result.

## Decision

Do **not** open another codec race yet. Run E1 on raw C96/qC caches first.
