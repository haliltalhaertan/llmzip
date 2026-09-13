# INDEPENDENT E1 MECHANISM CHECKPOINT AUDIT REPORT

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## Verdict

**PASS_WITH_FINDINGS**

The frozen E1 mechanism checkpoint is internally honest and mechanically reproducible enough to guide the next mechanism experiment. This verdict does **not** upgrade E1 into causal, confirmatory, deployable, publishable, or Task4F1-authorized evidence.

The strongest licensed reading remains: **SIGN advantage behaves like a query–archive regime interaction; BOT−TOP retrieval polarity (P64) is a descriptive regime marker; the underlying cause remains unresolved, with joint binary redundancy and richer ranking-competition geometry as leading candidates.**

## 1. Exact target and audit isolation

Audited repository: `haliltalhaertan/llmzip`

- Frozen target branch: `research/e1-mechanism-checkpoint-frozen-2026-09-13`
- Frozen target commit: `4bfdb820904ead1b6378b00bd5bf71c1ab2fe138`
- Frozen V2 parent: `775a09c1ba6fd8c28f1e98ec1826d31a7f2c3484`
- Campaign evidence base: `8f6e0fab4c2fb2eeb8dcd5087376a6736e1865f1`
- Main observed during audit preparation: `5ec3db60c03edde490374bf9cd7c3e56dd6bcd00`
- Independent audit branch: `audit/e1-mechanism-checkpoint-independent-2026-09-13`
- Successful execution head before report packaging: `87641cad65356f08e7d7ec6867f1a0b622fdb0ab`
- Successful GitHub Actions run: `34764744784`

The V2 parent→frozen-target comparison is 36 commits ahead, 0 behind, and contains **33 added files with no modified/deleted target files**: 10 E1 workflows, 10 E1 analysis scripts, 11 result JSONs, `E1_LME_SECONDARY_REPORT.md`, and `E1_MECHANISM_CHECKPOINT.md`.

The audit branch was created from the exact frozen target. The successful runner's additive-scope gate verified that audit changes were confined to the independent audit workflow/namespace. The frozen target branch and `main` were not modified.

Task4F1 was not accessed or run. Its status remains exactly: `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.

## 2. Source-byte and provenance verification

All seven SHA-256 gates supplied by the audit prompt matched byte-for-byte:

| Input | SHA-256 | Result |
|---|---|---|
| `docs/v52/task4c2/V52_T4C2_question_level.csv` | `69c21b2ffaea1e92923bf3f0e83287e12d07a5f34b4b42afde1752d6b50b3b51` | MATCH |
| `campaign_2026_09_13/regen/lme/task1_extension_lme.json` | `682440a0e3329ebab223d45079455ff3b7f97122244cf077a969ce887dfe25da` | MATCH |
| `campaign_2026_09_13/pilots_round1/per_axis_matrices.npz` | `be8c645d241bac3b913cfcf24f5533c55775a383b46a5f43401d633c873a635a` | MATCH |
| `campaign_2026_09_13/race/rb2/race_sign_details.json` | `87a4d1f2ac3da82ee5593e70d5b5347320349d8d266d895debe4a35698a76375` | MATCH |
| `campaign_2026_09_13/bench3/b3b_perltqa/results.json` | `ec9b8b2c7f384fe2f56c72fdc7a7216930a9db35eda2c4441496c8ad401bf958` | MATCH |
| `campaign_2026_09_13/bench3/b3a_realtalk/details.json` | `8bae1d380240adc856f8a787b142286efc16fd1d30dfc03bed7e5074769d1757` | MATCH |
| `campaign_2026_09_13/bench3/b3a_realtalk/rt_summary.json` | `8e725fca6dff584f853ef9dbf6888b700b12acd1dde42752417f3fa5302bf946` | MATCH |

Where an older manifest/hash ledger was located for the checkpoint's cited inputs, its binding was consistent: the question-level CSV, axis NPZ, RB2 race details, and REALTALK details/summary. No byte mismatch was found.

Commit chronology also matters. The V1 disposition (`12:46:06Z`), V2 spec (`12:46:31Z`), and V2 frozen parent (`12:48:16Z`) predate the first E1 LME secondary result commit (`12:57:05Z`). I found no evidence that V2 thresholds/specification were changed after seeing E1 result files. This **does not** make E1 preregistered: the benchmark outcomes used to narrow the mechanism were already observed.

## 3. Required independent reruns

The clean GitHub runner reran all ten required scripts directly from the audit checkout:

1. `e1_lme_secondary.py`
2. `e1_lme_axis_secondary.py`
3. `e1_lme_contextual_axis.py`
4. `e1_lme_joint_polarity.py`
5. `e1_perltqa_joint_polarity.py`
6. `e1_realtalk_joint_polarity.py`
7. `e1_regime_decompose.py`
8. `e1_perltqa_within_archive_flip.py`
9. `e1_perltqa_tie_section.py`
10. `e1_perltqa_p64_conditioned.py`

All ten completed successfully. Fresh JSON was parsed independently. In the committed-vs-fresh comparison, **no common scalar field differed by more than `1e-12`**, including the manually persisted LME question-type slice. Some committed files intentionally contain compact subsets of the richer stdout schema, so this is not a claim that every wrapper is byte-identical; the separate independent diagnostics recomputed the load-bearing statistics from the underlying committed source surfaces.

The final green workflow also completed output hashing and artifact upload. Artifact ID `10320205400` had SHA-256 `13021267393df051b9dab9ea21b68e0131d07ca6a7d46358250ced03915e56a0` when downloaded for this report.

## 4. Claim-by-claim adversarial assessment

### Claim A — simple scalar archive geometry is null/weak on LME: PASS_WITH_FINDING

The join is exact: 470 question-level rows, 470 geometry rows, no duplicate qids, exact qid-set equality, zero archive-size mismatches, and zero percent-vs-fraction identity error.

Global Spearman coefficients remain weak: `N +0.0084`, `cv_sigma -0.0096`, `top32_share +0.0213`, `sign_entropy +0.0336`, `corr_median_abs -0.0719`, `corr_off_mass -0.0856`, `corr_p95_abs -0.0982`. Removing any one question type does not convert the global result into a strong scalar mechanism; the largest leave-one-type-out magnitude is about `0.147`.

Adversarial finding: post-hoc strata are not uniformly null. For example, `single-session-preference` has `rho(corr_p95_abs, Delta) = -0.3877` at `n=30`, and `single-session-user` has `-0.2766` at `n=64`. Because these arise inside a multi-metric, multi-stratum post-hoc search, they are leads for a future frozen test, not evidence that the global scalar-null has been overturned.

### Claim B — marginal-axis signal concentration is weak: PASS

The NPZ surface contains `delta/alone/drop/var_rank` arrays of shape `470×96`, with exact qid alignment and no nonfinite `delta` values. Source semantics confirm `delta` is the **gold sign-agreement rate minus non-gold sign-agreement rate** for each axis; this is gold-informed explanatory information and therefore cannot be advertised as a deployable predictor.

Correlations with SIGN-minus-float Delta are weak: positive effective dimension `rho=+0.0370`, positive top-32 share `-0.0297`, positive top-16 share `-0.0319`, positive mass `+0.0297`, and negative mass `-0.1144` (largest magnitude).

### Claim C — contextual BOT−TOP drop-gap prediction is practically null: PASS

The implementation uses `drop_loss = native - drop[q,j]`, TOP=`var_rank<48`, BOT=`var_rank>=48`.

The load-bearing correlation is `rho(Delta, drop_loss_BOT - drop_loss_TOP) = +0.02986`, practically null. At the same time, absolute drop losses are not null: mean TOP loss is about `+0.108 pp`, mean BOT loss about `+0.254 pp`, with `rho(Delta, TOP absolute loss)=+0.2496` and `rho(Delta, BOT absolute loss)=+0.2040`.

This distinction matters. The checkpoint correctly says the BOT−TOP *difference* fails as a strong query predictor while TOP/BOT dimensions can still be important in absolute terms.

### Claim D — P64 is weak per query but stronger as a regime marker: PASS_WITH_FINDING

Fresh/independent results:

- LME per query: `rho=+0.1084` (`n=470`).
- PerLTQA per query: `rho=+0.1092` (`n=8265`).
- PerLTQA by character: `rho=+0.3188` (`n=30`); leave-one-character-out range `+0.2626 … +0.4094`.
- REALTALK per query: `rho=+0.0746` (`n=705`).
- REALTALK by chat: `rho=+0.4182` (`n=10`); leave-one-chat-out range `+0.3333 … +0.7500`.

Unequal query counts do not create an obvious sign reversal: PerLTQA character-level unweighted Pearson is `+0.2954` versus query-weighted `+0.2967`; REALTALK chat-level unweighted is `+0.5040` versus query-weighted `+0.4515`. The largest character contributes only `4.95%` of PerLTQA queries; the largest chat `12.06%` of REALTALK. Leave-one-unit-out correlations remain positive.

Adversarial finding: per-query results are sensitive in magnitude to rank ties. REALTALK Spearman is `+0.0746` with average ranks versus `+0.1266` with a dense-rank diagnostic; PerLTQA is `+0.1092` versus `+0.0888`. This reinforces the checkpoint's correct restriction: P64 is **not** an individual-query law or router.

### Claim E — semantic section/category is not the whole regime variable: PASS_WITH_FINDING

PerLTQA character-level within-section P64-vs-Delta correlations remain positive: dialogues `+0.1422`, events `+0.3130`, profile `+0.2617`, social_relationship `+0.2768`. Leave-one-character-out ranges remain positive for all four sections.

REALTALK is weaker because there are only 10 chat units: category 1 `rho=+0.0303` with leave-one-chat range `-0.1667 … +0.2667`; category 2 `+0.3818` with range `+0.25 … +0.60`; category 3 `+0.1914` with range `-0.1197 … +0.3248`.

Thus section/category composition is not a sufficient explanation, but the REALTALK within-category evidence is too small and heterogeneous to support a universal archive-regime claim.

### Claim F — archive-only explanation is insufficient: PASS

The PerLTQA evaluation pipeline keys archive structures by character and loads the document-side matrix `C` from the same `A[char]`; query `qC` varies per query. Therefore profile/events comparisons for a character do use the same underlying archive representation.

The frozen headline counts reproduce exactly:

- events Delta negative: `30/30`
- events P64 negative: `30/30`
- profile Delta positive: `23/30`
- profile P64 positive: `28/30`
- joint profile-positive/events-negative flip for both quantities: `22/30`
- same-sign nonzero character×section pairs: `87/115`

This is strong evidence that archive-only geometry is **insufficient** as a description. It is not a causal identification result because sections are not exchangeable interventions.

### Claim G — simple boundary-tie rate does not cause the core reversal: PASS_WITH_FINDING

Profile native tie rate is `31.23%` and mean Delta `+20.44 pp`; events tie rate is `27.08%` and Delta `-12.41 pp`. Among untied queries, profile remains strongly positive (`+19.65 pp`) and events remains strongly negative (`-9.81 pp`). Their P64 means also preserve opposite signs.

Overall P64-vs-Delta remains positive for untied queries (`rho=+0.1015`) and tied queries (`+0.1270`). So simple boundary ties do not explain the core profile/events reversal.

Guardrail: ties can matter elsewhere. `social_relationship` is `-0.81 pp` overall but `+0.88 pp` among untied queries. Therefore the licensed conclusion is **“simple tie rate is insufficient for the core profile/events reversal,”** not “ties are irrelevant everywhere.”

### Claim H — final licensed hypothesis is narrow enough: PASS

The checkpoint explicitly preserves the noncausal/post-hoc scope, rejects an individual-query/deployable predictor interpretation, keeps Task4F1 blocked, and states the final mechanism as a query–archive regime interaction with P64 as a descriptive marker. I found no language requiring correction to claim that P64 causes SIGN advantage, that variance concentration explains the effect, that boundary ties explain the effect, or that SIGN is universally superior.

## 5. New-finding search

No evidence was found of:

- wrong qid joins or duplicate-qid inflation in the LME scalar analysis;
- percent/fraction scale mistakes in the audited Delta identity;
- silent nonfinite filtering in the audited scalar/axis surfaces;
- E1 result JSONs being reused as computational inputs by the inspected E1 scripts;
- Task4F1 access by the E1 scripts;
- representation refit in the inspected E1 scripts;
- stale committed numbers that fail a fresh script rerun;
- source SHA mismatches;
- a single PerLTQA character or REALTALK chat driving the aggregate P64 direction.

The main epistemic risk is **selection/narrative inflation**, not a mechanical reproducibility defect: E1 is a post-hoc narrowing campaign over already-observed benchmarks, several metrics/strata were examined, and the strongest subgroup/aggregate patterns should be treated as hypothesis generators for a new frozen experiment.

## 6. Required NOT_RUN / NOT_AVAILABLE items

The exact frozen raw C96/qC cache surfaces needed for V2 PHI/EFFDIM/query-magnitude tests were not present in the committed campaign snapshot and were not located by connected Drive search. I did **not** regenerate/refit them.

The LoCoMo per-query centered-float E1 surface also remains unresolved. No value was invented.

Therefore:

- `PHI/EFFDIM/query-magnitude`: **NOT_RUN / NOT_AVAILABLE**
- `LoCoMo per-query centered-float E1`: **NOT_RUN / NOT_AVAILABLE**

## 7. Final decision

**PASS_WITH_FINDINGS** is warranted because the load-bearing checkpoint claims survive independent byte checks, fresh reruns, independent recomputation, aggregation attacks, same-archive checks, tie conditioning, and scope review.

The next mechanism experiment should keep exactly three guardrails:

1. freeze the next hypothesis and analysis before observing its new outcomes;
2. treat P64 as a regime-level descriptive marker, never as a validated per-query router;
3. target the unresolved mechanism directly—joint binary redundancy and richer ranking-competition geometry—rather than expanding post-hoc scalar/section searches.

No authorization for Task4F1 is implied by this verdict.
