# Coordinate-scale uncertainty completion — explicitly post-outcome

Status: APPROVED SCOPE / ANALYSIS PLAN; not a new preregistration or scientific acceptance.

The user answered "devam et" immediately after being asked to authorize completion of missing bootstrap analyses using existing frozen metric records. This authorizes this reporting work, not new retrieval, raw corpus access, rotation seeds, scale rules, Task4F1, historical seal edits or main/ledger changes. The parent already saw point estimates. All choices below not specified in the original document are POST-OUTCOME choices. Original preregistration inconsistency remains disclosed, not repaired retroactively.

## Sources

Research snapshot591e5d0fd7af8c265ac12a6176761475a19b2f02; canonical maina094452 (L-056). The executable pins complete SHA256 digests of both committed metric CSV.gz files and verifies them before analysis. These are the only outcome inputs; no corpus or research runner imports. Input identities are repeated in the machine output.

## Fixed design

- Rotation seeds59001..59010 remain fixed; no rotation-seed resampling or new rotations. Six paired arm scores for each question/seed move together in every resample.
- A = mean over seeds of (scaled-unscaled)/(native-unscaled). B = ratio of seed-mean gains to seed-mean losses. Report full and block A/B plus each route's full-minus-block interaction. Neither route is selected as the uniquely preregistered one.
- Paired-question bootstrap:1535 draws with replacement from1535 LoCoMo questions;470 from470 LongMemEval questions. Multinomial count representation.
- LoCoMo clustered bootstrap: draw10 of the10 persisted archive-ordinal groups with replacement; include all questions in each selected group with multiplicity, then use pooled question means. This preserves the question-weighted statistic, not an equal-conversation estimand. Sample size varies with drawn cluster sizes. Group mapping is producer metadata, not an independent raw-corpus join. No LongMemEval conversation bootstrap: a shared-conversation mapping is not established.
- Exactly10000 replicates per scheme; NumPy Generator(PCG64). Bootstrap RNG seeds2026090701 (LoCoMo question),2026090702 (LoCoMo cluster),2026090703 (LongMemEval question). These are bootstrap seeds, not retrieval/rotation seeds. Fixed processing chunks128; no adaptive extension.
- Each denominator is recomputed from each paired replicate. Float64 exact numerical zero makes a component undefined. A is undefined if any of its10 required components is undefined; its interaction requires both arms. B depends on its aggregate denominator. Retain every replicate. No clipping, denominator replacement or dropping seeds. Near-zero |denominator|<=1e-12 counts are diagnostic only, never exclusions or gates; float arithmetic does not certify mathematical exact zero.
- Report denominators' nonpositive/negative/zero/near-zero counts, ratio definedness and extrema, and fraction/interaction finite-replicate percentiles2.5/50/97.5 using NumPy linear quantiles. If undefined values occur, these are explicitly CONDITIONAL-ON-FINITE descriptive quantiles, not unconditional intervals. Even when all are finite, label all outputs sensitivity summaries rather than certified population intervals: ratio singularities, fixed seeds, ten LoCoMo clusters and shared pipeline limit inference.
- Report descriptive full/block band frequencies and interaction-positive frequency with ALL planned replicates as denominator; undefined replicates are counted separately. Frequencies are not probabilities hypotheses are true, formal tests, significance claims or a rule to upgrade a mechanism claim. No numerical definition of a 'large' interaction is invented.
- Retain per-replicate aggregate statistics (not resampled question IDs) and input/code hashes. Numerical environment recorded. No retry with changed method after seeing outputs.

## Verification and execution ordering

Pure synthetic tests must pass first: weighted sums equal explicit duplicated rows, cluster weighting equals concatenation, A differs from B on a constructed panel, zero-denominator undefinedness propagates, negative-denominator fractions stay visible, and paired arms remain equal. Plan/code/test bytes are committed and pushed before these new bootstrap outputs are computed. This is a pre-computation checkpoint for a post-outcome analysis, NOT pre-outcome preregistration.

The reporting deliverable must keep missing LongMemEval cluster identity, original aggregation ambiguity, and inconsistent mechanism decision rules open. Canonical acceptance belongs to the designated owner/independent audit, not this analysis script.
