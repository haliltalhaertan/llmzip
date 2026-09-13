# Independent E1 V2 Raw-Cache Recovery Audit

**Verdict: `REQUEST_CHANGES`**

Label: `[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]`

## Integrity

Target `d5441698fa8fb8404873af47233569803b887376` has parent `4bfdb820904ead1b6378b00bd5bf71c1ab2fe138`; parent->target is one additive commit in `campaign_2026_09_13/e1_v2_raw_recovery_2026_09_13/`. The three heavy archives and the analysis ZIP all matched their bound SHA-256 values before computation. Required surfaces were present: 470 LME caches, 10 LoCoMo caches, 10 REALTALK caches, and both PerLTQA caches. Task4F1 was not accessed.

Independence limitation: the mandatory Git scope query returned target diff prose before Stage-1. No lead result JSON, derived per-query/archive output, or analysis package was intentionally inspected before the independent raw-only table was written and hash-frozen. This is an independently recomputed review, but not a perfectly blind one.

## Headline gates

- LME SIGN `0.5419751773049645`, centered float `0.4415957446808511`: PASS.
- REALTALK SIGN `0.22477507598784194`, centered float `0.17253405381064954`: PASS.
- PerLTQA SIGN `0.488941994930817`, centered float `0.551692074528853`: PASS.
- LoCoMo SIGN `0.23654714666441054`: PASS. Independently derived centered float `0.16826334541318252`, hence SIGN-float `+6.82838013 pp`.

The older LoCoMo `~+12pp` line was recovered only as “programme-reported; not recomputed”. Audit/raw and fractional/any/all variants lie about `+5.899` to `+7.681 pp`. No frozen centered-float source supporting ~12pp was found, so it is not an anchor.

## Claims A-H

**A — LoCoMo conflict:** lead `0.16826334541318252` is independently confirmed; old ~12pp is not an anchor.

**B — TOP/BOT structural asymmetry:** PHI_GAP>0 and EFFDIM_GAP>0 are both `520/520` recovered archives. Disjoint TOP32/BOT32 gives `520/520` again. No TOP/BOT constant bits were found, recovered C had no exact zeros, mean-square vs variance ranking selected the same axes, and no duplicate C-hash archives were found. This licenses “all 520 recovered archives”, not a universal law.

**C — P64:** average-rank Spearman reproduces LME `0.1085653`, REALTALK `0.0745275`, PerLTQA `0.1091675`, LoCoMo `0.2494691`. Alternative tied-rank methods materially alter magnitude; bootstraps are descriptive/post-hoc only.

**D — Ranking competition: REQUEST CHANGES.** The lead function collapses all golds to `dmin=min(distance[gold])` and counts once. Frozen V2 requires strictly-closer and gold-distance tie mass per gold, aggregated within query using D2. Multi-gold rates are LME `296/470`, REALTALK `386/705`, PerLTQA `2322/8265`, LoCoMo `432/1535`.

Corrected literal per-gold D2 Spearman coefficients versus lead min-gold coefficients:

| benchmark | lead strict | D2 strict | lead tie | D2 tie |
|---|---:|---:|---:|---:|
| LME | 0.099657 | 0.141686 | 0.098959 | 0.140454 |
| REALTALK | 0.061183 | 0.097939 | 0.087153 | 0.122820 |
| PerLTQA | 0.277387 | 0.254168 | 0.285059 | 0.279788 |
| LoCoMo | 0.093706 | 0.094920 | 0.095332 | 0.103760 |

All corrected directions remain positive, so this is repairable rather than blocked. In PerLTQA, `events/profile/social_relationship` are single-gold in the recovered surface and therefore hide the bug; multi-gold `dialogues` exposes it.

**E — Duplicate code:** mean DUP_GAP is LME `0.007856`, REALTALK `0.000642`, PerLTQA `0`, LoCoMo `0`; duplicate identity is not a broad explanation.

**F — Query magnitude:** Delta-vs-Q_ABS_CV is weak. Under the fixed 96-D definitions, `Q_EFF = 96/(1+Q_ABS_CV^2)`; residual <=`2.842e-14` and Spearman is `-1` on all four, so Q_ABS_CV and Q_EFF are not independent evidence.

**G — Archive prediction:** PHI/EFFDIM archive correlations are inconsistent across benchmarks and fragile for the two `n=10` archive sets. A `520/520` structural inequality is not a predictor of SIGN-vs-float direction.

**H — Licensed interpretation:** in all 520 recovered archives, high-variance TOP64 sign bits are more redundant and BOT64 bits have higher binary effective dimension, but this does not determine SIGN-vs-float outcome. P64 and correctly computed per-gold ranking competition are descriptive regime markers only. Causal, universal-population, or deployable-router claims are rejected.

## Lead cross-check after Stage-1 freeze

All non-competition per-query lead fields (`Delta`, FR_SIGN/FLOAT/TOP64/BOT64, P64, Q_ABS_CV, Q_EFF) match independent rows exactly. PHI/EFFDIM/DUP archive geometry also matches exactly. Only competition rows diverge materially, consistent with the min-gold implementation difference. Lead package hash manifest and sidecar rehashed cleanly.

## Required changes before PASS

1. Replace min-gold competition with frozen per-gold D2 aggregation and regenerate all competition-derived rows/correlations/bootstraps/prose.
2. Keep bootstrap inference explicitly descriptive/post-hoc.
3. Disclose Q_ABS_CV/Q_EFF exact algebraic redundancy.
4. Replace universal wording with sample-scoped “all 520 recovered archives”.
5. Keep LoCoMo centered float `0.16826334541318252`; do not promote old ~12pp prose to an anchor.
6. Do not refit representations, remap evidence, authorize E2, or access Task4F1.

Final verdict: **`REQUEST_CHANGES`**. The recovery and most reported results are sound; Claim D’s frozen-metric implementation must be repaired before a PASS.
