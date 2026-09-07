# Coordinate-scale reporting resolution proposal

Status: **NONAUTHORITATIVE / PROPOSED ONLY / NO ANALYSIS AUTHORIZATION**.

Prepared 2026-09-07 as an additive follow-up to review `4769c2a`. This document neither replaces the commissioned independent auditor nor changes canonical state, the ledger, any frozen specification, any seal, or any historical result. It is not a new preregistration and does not claim that choices made after outcome access were preregistered.

## Evidence inspected and limits

- Review and statistics findings at `4769c2a`; research ancestry includes result checkpoint `1c725a56752d1059148f48b89d8138c76c2f70e9` and additive research head `591e5d0fd7af8c265ac12a6176761475a19b2f02`.
- Installed `research/v52/V52_COORDINATE_SCALE_PARTICIPATION_PREREG_2026-09-05.md`, especially sections 7-9 and 12. Its history has one installation commit, `59ae1b5`. Draft history identifies v1 `d815627`, v2 `2b743b1`, v3 `20ed5fc`, and final draft `bdc0db75`. The historical draft path is `drafts/v52/V52_COORDINATE_SCALE_PARTICIPATION_PREREG_DRAFT_2026-09-05.md`, not the installed research path.
- Commissioned audit prompt read directly from canonical snapshot `a0944522d122cfc3edb36b1d54bca3a1ade6661f`, path `prompts/V52_COORDINATE_SCALE_COLD_START_INDEPENDENT_AUDIT_PROMPT_2026-09-07.md`.

This subreview is textual adjudication preparation. It did not rerun the earlier reconstruction, access a raw corpus, compute resampling outputs, import experiment runners, or perform any Task 4F1 operation. The numeric values below are attributed to the earlier review, not independently reproduced in this subreview. Gate completion and byte verification remain separate obligations.

## R1: retain both aggregations; do not rewrite history

For each fixed benchmark, let N_s be native mean score on the complete question cohort for seed s, U_s the corresponding unscaled arm mean, and T_s the scaled arm mean. Let L_s = N_s - U_s and G_s = T_s - U_s.

- **A: mean of seed ratios:** A = mean_s(G_s / L_s), where each required ratio is defined.
- **B: ratio of seed means:** B = mean_s(G_s) / mean_s(L_s), where the aggregate denominator is nonzero.

Section 7 first says per rotation seed, defines a fraction, and then applies bands to the seed-panel mean. A is its ordinary reading. The runners' headline route is B. Both must be retained under explicit names. B is a loss-weighted average of per-seed ratios when the component ratios exist; negative L_s make those signed weights rather than probability weights. Neither numerical stability nor unchanged band labels establishes A = B or retrospectively authorizes replacing A with B.

The prior review reports LoCoMo block A = 0.44544258 versus B = 0.65164292, and LoCoMo interaction A_full - A_block = 0.28174356 versus B_full - B_block = 0.07446399. These are distinct summaries, not precision discrepancies. No proposal here promotes either LoCoMo block number to an interpretable recovery share.

**Proposed disposition:** append a deviation table that preserves the originally published B, reports reconstructed A alongside it, links exact frozen rows and code, and asks the independent auditor to adjudicate the registered endpoint from the pre-outcome text. If A is accepted as registered, B remains a historical/nonregistered descriptive summary. If the text is judged ambiguous, record ambiguity rather than retroactively claiming either was uniquely preregistered. Apply no new decision threshold.

## Undefined and unstable ratios

An exact zero L_s means the corresponding seed ratio is undefined; it is not zero, infinity to be averaged, or a reason to silently remove that seed. Near-zero nonzero loss is mathematically divisible but potentially unstable. Negative loss is not positive damage to be recovered. Overshoot above one can be valid and must not be clipped.

For any later approved analysis, retain the fixed seed panel and report numerator, denominator, sign, and definedness together. If a required component of A is undefined, mark A and its interaction undefined unless an explicitly post-outcome alternative estimand is approved and separately labelled. B can remain mathematically defined in that situation but is not a substitute for A. For bootstrap replicates, retain counts of all planned replicates, undefined replicates, denominator sign changes, and any algorithmic failures. A finite-only interval would condition on definedness; it must not be silently presented as the unconditional interval or used to establish a robust verdict. This proposal supplies no near-zero cutoff, clipping rule, or finite-only inference rule.

## R2: mandatory analyses are missing, not newly invented requirements

Section 8 already requires a paired question bootstrap on I and an additional conversation-clustered bootstrap. Section 12 fixes the question sampling unit with clustered reporting alongside. Completing these obligations from frozen records need not rerun retrieval or alter the experiment. Their absence nevertheless means current reporting is incomplete. The seed envelope is not a replacement.

The frozen text does **not** fully fix the implementation choices needed to execute these analyses. The decision packet must resolve and label the following before additional calculations:

1. Which interaction I is being resampled: the fraction interaction of section 7, under A, B, or separately both. Percentage-point interaction stays descriptive and cannot become the decision endpoint by convenience.
2. Pairing: resample the same question indices across every arm and the fixed seed panel, not independent arm rows. Recompute numerator and denominator from the paired replicate. Do not freeze the observed denominator while resampling only gains.
3. Seed treatment: whether the existing seed panel is held fixed or resampled as another level. Additional seed sampling is not explicitly specified. Neither new rotation seeds nor replacement trials are permitted by this proposal.
4. Cluster identity for each benchmark, its verifiable mapping from persisted question identifiers, handling of repeated clusters, and target weighting. A question-weighted cluster-resample score and an equal-conversation score are different estimands. LoCoMo's ten conversations constrain interpretation; the requested LME mapping/scope must be justified rather than presumed equivalent to LoCoMo.
5. Replicate count, random generator and bootstrap seed, interval level and construction, and whether/how Monte Carlo error is reported. No values are selected here.
6. Singular/sign-changing denominators, treatment of undefined statistics, and what interval can legitimately be reported if mass is undefined. No post-outcome rule may discard unfavorable seeds or replicates without explicit accounting.

**Proposed approval boundary:** the independent auditor first states what is genuinely inherited from the frozen text and what remains unspecified. The authorized decision owner then records an additive analysis-completion decision containing the full algorithm, limitations, exact source/code hashes, and the fact that unresolved choices were made after outcomes. A reviewed analysis-only implementation may then consume the existing records. This is not permission for new scale rules, arms, thresholds, rotation seeds, reranking, or retrieval. It cannot retroactively restore a fully prespecified design where one was absent.

## R5: unresolved interpretation cannot be repaired by selecting favorable wording

Section 7 makes per-arm fractions primary, the fraction interaction secondary, and full-gap reduction alone insufficient. Section 9 still defines a positive conclusion by a large I and a null by near-zero I, without a numerical definition of large. These clauses must be assessed together. The audit should not declare full compliance merely because the 0.70/0.20 bands can be reproduced.

**Proposed disposition:** retain the fixed-benchmark score changes and both explicitly labelled aggregations as descriptive evidence; withhold a clean preregistered comparative mechanism verdict while the contradiction and missing uncertainty remain unresolved. A post-outcome clarification may narrow claims and record the defect, but may not invent a quantitative large-I threshold or claim that a newly chosen rule was frozen. No conclusion of exclusive mediation, universal mechanism, or encoder/corpus generality follows. Any genuinely new scientific endpoint or intervention requires its own prospective design, separate from this reporting correction.

## Supplemental questions for the already commissioned auditor

These questions extend coverage; they do not replace G1-G13, change verdict vocabulary, or commission an additional raw-data run.

- **G4 supplement:** Beyond constants, do both runners implement the same order of aggregation that section 7 requires? Quote the per-seed and seed-panel clauses. Inventory the mandatory section 8 outputs and locate each in the result package, or mark it absent.
- **G8 supplement:** Reproduce A and B separately, distinguish equal-seed from loss-weighted summaries, and account for every seed's numerator, denominator, definedness and sign. Matching the published B alone is not endpoint-compliance evidence. Are paired question and clustered bootstrap artifacts actually present? If absent, is mandatory reporting established?
- **G9 supplement:** Apply frozen bands only after naming the estimand. Do not treat unchanged classifications as proof of aggregation compliance. Can a panel point classification support a population or cross-dataset statement given the reported uncertainty and unstable block loss?
- **G13 supplement:** Adjudicate sections 7, 8 and 9 jointly: can the stated participation lead follow when full-gap reduction is declared insufficient, I is secondary but still licenses the positive conclusion, and large I is undefined? Distinguish a limitation from an unregistered replacement rule. State exactly what narrow score-change statement survives.
- **Analysis-completion question:** Which bootstrap decisions were frozen, which remain open, and which outcomes would make an interval undefined rather than merely wide? Specify required approval and disclosure before implementing the omitted analysis; do not infer approval from this proposal.

## Deliverables if the decision owner approves later work

An additive discrepancy/interpretation receipt, an independently reviewable analysis-completion specification, then immutable input-bound reporting artifacts. Each should identify the old result unchanged and the new artifact's narrower role. Canonical state and ledger remain with the designated single writer. This proposal commits no acceptance, seal, run, finalize, bootstrap, or Task 4F1 authorization.
