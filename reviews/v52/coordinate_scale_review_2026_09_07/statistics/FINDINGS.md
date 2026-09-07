# Scoped statistical subreview

Target: checkout `591e5d0`, 2026-09-07. This is persisted-record reconstruction and statistical/specification review, not a full cold-start certification. No experiment runner was imported, no raw corpus was opened, and no Task 4F1 computation was performed.

## S1 — P1: implemented aggregate is not the specified mean of per-seed fractions

Preregistration `research/v52/V52_COORDINATE_SCALE_PARTICIPATION_PREREG_2026-09-05.md:122` says **"For each dataset independently, per rotation seed, paired at the question level:"**, followed by the two fraction formulas (125–126). Line 133 then specifies **"Resolved bands on the seed-panel mean, applied per arm"**. The ordinary combined reading is: calculate each seed's fraction, then average those fractions.

Instead, `research/v52/locomo_coordinate_scale.py:221-222` and `research/v52/longmemeval_coordinate_scale_shard.py:247-248` calculate a fraction from across-seed arm means. These are different estimands. The document could have explicitly specified a ratio of seed means but did not; at minimum this is an unresolved normative aggregation discrepancy, not a floating-point error.

Persisted gzip reconstruction confirms both the published ratio-of-means and the published per-seed fractions. Averaging those per-seed fractions gives:

| Dataset / quantity | Reported ratio-of-means route | Mean-of-seed-ratios route |
|---|---:|---:|
| LoCoMo full | 0.72610691 | 0.72718613 |
| LoCoMo block | 0.65164292 | 0.44544258 |
| LoCoMo I | 0.07446399 | 0.28174356 |
| LongMemEval full | 0.65633430 | 0.65697817 |
| LongMemEval block | 0.30845858 | 0.31651116 |
| LongMemEval I | 0.34787571 | 0.34046700 |

The categorical bands do not change here, but the LoCoMo interaction changes materially. Neither version rescues its unstable block ratio. Preserve original result bytes and record an additive deviation/correction; do not silently redefine the preregistration after outcomes.

## S2 — P1: mandatory uncertainty reports are absent

Preregistration lines 152–157 require per-seed mean/range of I, a paired question bootstrap, and an additional conversation-clustered bootstrap. The two summary JSONs contain controls/primary/diagnostics but no bootstrap/uncertainty section; neither runner contains bootstrap or cluster computation. The result checkpoint provides point estimates and arm seed ranges, not the required resampling outputs. Therefore the experiment is not fully reported as preregistered.

The full-arm seed dispersion is useful, but it does not replace question or conversation uncertainty. LoCoMo has only 10 archive diagnostics and clustered inference is necessarily limited. LongMemEval's positive block denominators on this seed panel do not prove positivity under resampling. Completing a missing required analysis from frozen records is distinct from running additional retrieval experiments; any singular-denominator treatment must be explicit and must not select away inconvenient resamples.

## S3 — P1: interpretation rule remains internally inconsistent

Preregistration section 7 defines per-arm fractions as primary (129–137), makes I secondary (142–143), and explicitly says a reduced native-versus-full gap alone is insufficient (148). Yet section 9 still defines positive/null cases in terms of a large/near-zero I (165–174), with no quantitative meaning of "large". This appears to leave an obsolete decision rule alongside the revised primary rule.

The checkpoint at 86–92 licenses participation from full-arm recovery under section 9, while at 107–111 it correctly withholds LoCoMo I interpretation. These two statements do not jointly satisfy the frozen rule at line 148. The defensible narrow claim is a measured intervention effect on the full-rotation retrieval score, conditional on this pipeline; stronger comparative participation verdicts require an explicit audit/acceptance resolution, not a favorable post-outcome choice of rule.

## S4 — supported caution: LoCoMo block ratio cannot be called a recovered share

Two of ten reconstructed block denominators are negative; the smallest positive values are about 0.0017 and 0.00195. Negative-loss seeds can have fraction >1 even when scaling worsens retrieval. Thus this number is not uniformly a recovery share. The checkpoint's lines 98–105 appropriately withhold interpretation. Keep that caveat attached to both aggregation versions and every LoCoMo I citation.

The `MOST`/`PARTIAL` bands are descriptive frozen panel classifications, not hypothesis-test conclusions or proof that benchmark populations occupy distinct bands. Full-arm seed values cross 0.70 within each dataset. Also, removing marginal scale variation changes the continuous geometry before mixing; it does not prove exclusive mediation or identify a universal mechanism.

## Reproduction

Run `python -B reviews/v52/coordinate_scale_review_2026_09_07/statistics/reconstruct.py` from this checkout with a Python standard-library runtime. No third-party imports are used. The script prints complete values; `RESULTS.json` is a compact transcription. It verifies unique question/seed/arm keys, score ranges, frozen seed IDs, and both published aggregation routes to tolerance 1e-10. A two-seed synthetic negative control asserts that averaging and division do not commute. It does not validate individual persisted metric scores against gold/retrieval IDs or reproduce numerical controls from raw representations.

Recommendation: **WITHHOLD scientific acceptance pending aggregation/decision-rule resolution and completion of required uncertainty reporting.** Preserve the useful point-estimate evidence and the original frozen package.
