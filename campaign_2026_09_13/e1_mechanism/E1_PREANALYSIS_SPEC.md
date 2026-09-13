# E1 pre-analysis specification — SIGN-vs-float mechanism

Status: **FROZEN DESIGN CANDIDATE / LOCAL EXPLORATORY FOLLOW-UP / NOT YET RUN**.

This specification is written after the bridge pattern was observed, so E1 is mechanism
validation, not a pristine discovery experiment. Any later fifth-benchmark test is the
proper confirmatory test.

## Question

Does coordinate heterogeneity / variance-tail polarity explain when SIGN96 beats centered
float96?

## Inputs

Use only frozen/local representation caches that reproduce the accepted anchors before
analysis. Required surfaces:

- LongMemEval: frozen C96/qC/gold cache used by the race/regen pipeline.
- LoCoMo: frozen per-conversation C96/qC/gold cache used by the race/T4D pipeline.
- REALTALK: the port's frozen representation cache (`rt_repr` surface).
- PerLTQA: `cache_arch_eval.pkl` + `cache_q_eval.pkl` from the verified B3B run.

No refit with changed text, tokenizer, vectorizer, SVD seed, centering rule, query transform,
or evidence mapping is allowed.

## Gate

For every benchmark, reproduce the committed native SIGN96 headline to <=1e-12 where exact
cache equality is available, and reproduce the centered-float headline to <=1e-12 where the
accepted evaluator output exists. If a gate fails, stop that benchmark.

## Per-query outcomes

Using the frozen top-3/tie convention:

- `Delta_q = FR_SIGN96(q) - FR_FLOAT96(q)`.
- `P64_q = FR_BOT64(q) - FR_TOP64(q)` where TOP/BOT are per-archive variance ranks of C96.
- Do not use gold labels to construct TOP/BOT.

## Archive geometry, computed only from document C96

Let `v_j = mean_i(C_ij^2)` (C is centered, so this is the population variance up to numerical
roundoff).

Predeclared geometry metrics:

1. `VAR_CV = std(v) / mean(v)`.
2. `EFF_COORD = (sum(v))^2 / sum(v^2)`; lower means more concentrated coordinates.
3. `TOP64_VAR_SHARE = sum(v[top64]) / sum(v)`.
4. `SIGN_IMBALANCE = mean_j(abs(mean_i(2*1[C_ij>=0]-1)))`.

Per-query geometry:

5. `Q_ABS_CV = std(abs(qC)) / mean(abs(qC))`.
6. `Q_EFF = (sum(abs(qC)))^2 / sum(qC^2)`.

Zero denominators are `NOT_EVALUABLE`, never imputed.

## Primary mechanism tests

Report each benchmark separately; no pooled headline.

A. `rho(Delta_q, P64_q)` using Spearman, with archive/conv clustered bootstrap where multiple
queries share an archive. Direction predicted positive.

B. Archive-level `rho(mean_q Delta_q, VAR_CV)` predicted positive.

C. Archive-level `rho(mean_q Delta_q, EFF_COORD)` predicted negative.

D. Query-level partial/descriptive model:
`Delta_q ~ z(VAR_CV) + z(Q_ABS_CV) + z(P64_q)`
with benchmark-specific coefficients; use it only as descriptive effect decomposition, not
a deployable predictor.

## Mandatory stratification

PerLTQA must report profile/social/events/dialogues separately in addition to aggregate.
REALTALK must report its existing category 1/2/3 strata. LME question type and LoCoMo category
are secondary stratifications.

## Falsifiers

The coordinate-heterogeneity hypothesis is weakened if either:

- the predicted VAR_CV sign is wrong in >=3 of the 4 benchmark-level analyses; or
- EFF_COORD has the wrong sign in >=3 of 4; or
- P64 has no positive association with Delta within any of LME, REALTALK, or PerLTQA despite
  their aggregate/section bridge pattern.

If only P64 works but geometry-only VAR_CV/EFF_COORD does not, the licensed conclusion is:
“variance-tail retrieval polarity tracks SIGN advantage descriptively; the underlying
coordinate-heterogeneity mechanism remains unresolved.”

## Audit requirements

- Save per-query rows and per-archive geometry rows.
- Save exact script SHA256 and input-cache SHA256 inventory.
- Independent recomputation must not read the first run's derived CSV before recreating it.
- All outputs retain LOCAL/NOT-PREREGISTERED/NOT-FOR-CITATION labels.
- Task4F1 remains untouched.
