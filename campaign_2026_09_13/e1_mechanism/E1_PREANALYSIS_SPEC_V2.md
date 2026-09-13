# E1 pre-analysis specification V2 — joint redundancy / tie geometry

Status: **FROZEN DESIGN CANDIDATE / LOCAL EXPLORATORY FOLLOW-UP / NOT YET RUN**.

Parent design: V1 at `d1e429ccc227f233389dfc97c368cbea3752b1ec`.
V1 was refined before any E1 raw-cache result was produced. The reason is recorded in `E1_V1_DISPOSITION.md` and comes from pre-existing LongMemEval round-1 evidence.

## Question

When SIGN96 beats or loses to centered float96, is the direction associated with how informative coordinates combine jointly — especially redundancy and top-k tie competition — rather than with marginal axis variance alone?

## Frozen inputs and gate

Use only the accepted frozen/local C96/qC/gold caches for LongMemEval, LoCoMo, REALTALK and PerLTQA. No representation refit or evidence remapping.

For each benchmark, reproduce the accepted SIGN96 and centered-float headline to <=1e-12 where an exact accepted evaluator output exists. A failed gate stops that benchmark.

## Outcomes

Per query:

- `Delta_q = FR_SIGN96(q) - FR_FLOAT96(q)`.
- `P64_q = FR_BOT64(q) - FR_TOP64(q)`; TOP/BOT are defined only from archive-side C96 variance and never from gold labels.

Per archive/conversation:

- `Delta_archive = mean_q Delta_q`.
- `P64_archive = mean_q P64_q`.

## Archive geometry from document C96 only

Let `v_j = mean_i(C_ij^2)`.

Retain V1 descriptive concentration metrics:

1. `VAR_CV = std(v)/mean(v)`.
2. `EFF_COORD = (sum(v))^2/sum(v^2)`.
3. `TOP64_VAR_SHARE`.
4. `SIGN_IMBALANCE`.

Add the load-bearing joint-geometry metrics. Let `B = 2*1[C>=0]-1`.

5. `MEAN_ABS_PHI_TOP64`: mean absolute off-diagonal Pearson/phi correlation among TOP64 sign bits.
6. `MEAN_ABS_PHI_BOT64`: same for BOT64.
7. `PHI_GAP = TOP64 - BOT64`.
8. `SIGN_EFFDIM_TOP64 = tr(S)^2 / tr(S^2)` for the centered TOP64 sign-bit covariance S.
9. `SIGN_EFFDIM_BOT64`: same for BOT64.
10. `EFFDIM_GAP = BOT64 - TOP64` (positive means BOT is less redundant / higher effective binary dimension).
11. `DUP_FRAC_TOP64`: fraction of archive rows belonging to a duplicated TOP64 code.
12. `DUP_FRAC_BOT64`: same for BOT64.
13. `DUP_GAP = TOP64 - BOT64`.

Constant columns are retained as zero-information bits for code construction; pairwise correlations involving zero-variance sign bits are `NOT_EVALUABLE` and excluded from the mean with the count reported. No imputation.

## Query / retrieval-competition diagnostics

Using the frozen tie convention and the gold mapping only after representation construction:

14. `BOUNDARY_TIE_TOP64_q`: size/existence of the exact-distance tie at the K=3 boundary.
15. `BOUNDARY_TIE_BOT64_q`.
16. `STRICTLY_CLOSER_TOP64_q`: number of non-gold items strictly closer than the relevant gold distance, aggregated with the same per-gold convention already used by the D2 mechanism audit.
17. `STRICTLY_CLOSER_BOT64_q`.
18. Gold-distance tie mass for TOP64 and BOT64 under the D2 definition.

These are explanatory, gold-informed diagnostics, never deployable features.

## Primary tests

Report every benchmark separately. PerLTQA additionally reports profile/social/events/dialogues separately.

A. `rho(Delta_q, P64_q)` Spearman, archive/conv-cluster bootstrap where appropriate. Predicted positive.

B. Archive-level `rho(Delta_archive, PHI_GAP)`. Predicted positive: larger excess TOP redundancy should accompany larger SIGN advantage.

C. Archive-level `rho(Delta_archive, EFFDIM_GAP)`. Predicted positive.

D. Archive-level `rho(Delta_archive, DUP_GAP)`. Predicted positive but explicitly secondary because old LME evidence says duplicate collapse alone is insufficient.

E. Query-level association between `Delta_q` and TOP-vs-BOT strictly-closer / gold-tie-mass gaps. Direction: SIGN advantage should be larger where TOP suffers more ranking competition than BOT.

## Secondary / discriminating tests

F. V1 `VAR_CV` and `EFF_COORD` signs are retained as secondary. Failure does not by itself kill the joint-geometry hypothesis.

G. Marginal-axis sanity check: across 96 axes, correlate archive-averaged variance rank with the pre-existing or freshly recomputed single-axis discrimination. V2 explicitly allows high-variance axes to be individually stronger; the hypothesis concerns joint composition, not marginal signal.

H. Descriptive benchmark-specific model: `Delta_q ~ z(P64_q) + z(PHI_GAP_archive) + z(Q_ABS_CV)`; no deployment claim.

## Falsifiers / licensed conclusions

The joint-geometry hypothesis is weakened if:

- `P64_q` has no positive association with `Delta_q` in all of LME, REALTALK and PerLTQA; or
- both `PHI_GAP` and `EFFDIM_GAP` have wrong/non-positive direction in >=3 benchmark-level analyses; or
- the retrieval-competition gaps fail to distinguish TOP from BOT in the datasets where their FR differs strongly.

If P64 tracks Delta but PHI/EFFDIM/tie metrics do not, the conclusion is limited to:
“variance-tail retrieval polarity tracks SIGN advantage descriptively; the mechanism remains unresolved.”

If redundancy/tie metrics align across the positive and negative benchmark/section cases, the result remains a mechanism candidate, not causal proof. A later unseen fifth benchmark is required for confirmatory generalization.

## Audit requirements

- Persist per-query and per-archive rows.
- Persist exact input-cache SHA256 inventory and analysis-script SHA256.
- Independent recomputation must recreate derived rows without reading the first run's output.
- Preserve LOCAL / NOT PREREGISTERED / NOT FOR CITATION / DISCLOSE-BEFORE-USE labels.
- Task4F1 remains untouched.
