# Coordinate-scale takeover review — 2026-09-07

Status: **REQUEST CHANGES / DO NOT ACCEPT THE STAGE AS FULLY AUDITED.**

This is a scoped team review, not the commissioned cold-start audit, not an execution authorization, and not a canonical state transition. The parent reviewer had prior scientific context; its two subagents inherited context and worked in disjoint output directories in the integration worktree. They are not claimed as independent cold-start auditors. No frozen research artifact was edited.

## Anchors and boundaries

- Canonical state examined: `a0944522d122cfc3edb36b1d54bca3a1ade6661f`, L-056.
- Research tree examined: `591e5d0fd7af8c265ac12a6176761475a19b2f02`.
- The result checkpoint is anchored at `1c725a56752d1059148f48b89d8138c76c2f70e9`.
- Both canonical tools printed `CONTINUITY_STATE: PASS` and `PREREGISTRATION_SEAL: PASS` in a detached checkout of a094452. These are structural checks, NOT acceptance of this research stage.
- No raw corpus was read; no real retrieval was run or retriggered. Task 4F1 run=0, finalize=0, HMAC=0; BEAM outcome access=false.
- Initial live refresh attempts failed with GitHub DNS/connection errors. After publication, remote readback confirmed main remains a094452 and the review commit8390e28 was pushed; neither commissioned audit nor literature target branch was present. The current health of those separate agents is unknown. A state string saying RUNNING is not a liveness check.

## Findings requiring adjudication

### R1 — Primary aggregation differs from the preregistration's natural reading (P1)

Preregistration section 7 defines fractions per rotation seed and then applies bands to the seed-panel mean. Both runners instead divide seed-averaged gains by seed-averaged losses for their headline fractions. Mean ratios and ratios of means are different estimands. The latter may be preferable for some questions, but cannot silently replace the former after outcomes.

The statistics evidence reconstructs both. For LoCoMo block mixing, the reported ratio of means is approximately 0.651643 while the mean seed ratio is 0.445443. The corresponding interaction changes from about 0.07446 to 0.28174. The existing broad band assignments survive this particular correction; exact registered-endpoint compliance does not follow from unchanged bands. LoCoMo block ratios remain scientifically unstable under either summary.

Required disposition: retain frozen outputs, append an explicit discrepancy report containing BOTH aggregations, and have an independent reviewer adjudicate the registered estimand. Do not retrofit the preregistration or quietly relabel historical numbers.

### R2 — Required uncertainty reporting is absent (P1)

Preregistration section 8 explicitly requires a paired question bootstrap on the interaction and, additionally, a conversation-clustered bootstrap. Per-seed ranges or denominator standard errors do not substitute for those analyses. Current summaries/checkpoint do not discharge the requirement. In particular, LoCoMo's near-zero block loss needs undefined/unstable-ratio accounting, not silent bootstrap sample deletion or clipping.

Required disposition: first settle R1 and document missing analysis choices (sampling, seeds, iterations, undefined ratios). Then implement a separately recorded analysis of the existing rows, without reranking or claiming its unspecified choices were frozen pre-outcome. The present review deliberately does not choose those values after seeing the results.

### R3 — Declared seal binding does not enforce the entire LoCoMo executable dependency chain (P1)

The ten explicitly listed seal entries match. However, the sealed LoCoMo base dynamically imports `locomo_sign_mechanism_replication.py`; it is not among the workflow's ten checked entries and its loader does not enforce the declared common blob. That file is recoverable from the pinned Git tree and was unchanged from installation to the examined result tree. Thus this is an enforcement/closure gap, NOT evidence of actual tampering or an irreproducible snapshot.

Required disposition: the independent auditor should explicitly verify the transitive execution closure at the original trigger commit. Future packages should bind/check it. Never mutate the old seal to conceal the omission.

### R4 — Aggregate validation accepts malformed synthetic records (P1 hardening; not proven result corruption)

The implementation review supplies synthetic counterexamples for non-finite diagnostics, out-of-range scores, cancelling per-question native/scaled-native differences and mismatch between supplied native-control scalar and row values. Existing synthetic tests passing does not establish rejection of these cases. These demonstrations do not prove that persisted real records contain those defects.

Required disposition: audit actual persisted rows independently; add adversarial aggregate tests and repairs only in a new implementation package if future execution is authorized. Retain the original execution bytes for reproduction.

## Scientific interpretation

**R5 — P1, unresolved decision rule:** section 7 makes per-arm fractions primary and the interaction secondary, yet section 9 still licenses the positive conclusion through an undefined 'large' interaction. This is an internal specification inconsistency, not merely missing error bars. Acceptance must explicitly address all frozen clauses rather than select the favorable one after outcomes.

Recovery in full-mixing arms is descriptive evidence worth investigating. It is not, by itself, the preregistration's sufficient mechanism criterion: section 7 explicitly rejects interpreting full-gap reduction alone, and section 9 refers to a positive interaction. Missing uncertainty and an unstable LoCoMo block denominator prevent a clean cross-dataset interaction claim. Keep the NOT INDEPENDENTLY AUDITED label, the LoCoMo block limitation and the MOST/PARTIAL heterogeneity attached to any internal status summary.

The newly measured Full-Haar seed panel is useful, but it does not recover the original uncommitted LoCoMo seed realizations or close query/conversation sampling uncertainty. No prior frozen denominator or boundary verdict is replaced here.

## Next single action

Deliver this review and its reproductions to the commissioned independent audit / canonical state writer for explicit adjudication of R1–R4. Do not rerun the experiment, change thresholds, add seeds, or claim a completed audit. No main/state/ledger mutation is performed by this review branch. Google Drive backup was not performed and is not claimed.

See `statistics/` and `implementation/` for scoped evidence and reproduction details. `REVIEW_HASHES.json` inventories the review payload, excluding itself to avoid self-reference.
