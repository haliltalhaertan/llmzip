# E1 V2 raw recovery R2 — Claim-D competition rerun contract

**Labels:** [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Status: **FROZEN R2 REPAIR CONTRACT / NOT YET EXECUTED BY LEAD / RE-AUDIT REQUIRED**.

This contract repairs the only HIGH finding in independent audit commit
`010bcbbe0ade15ed1dc501ce6d2f4e2e5ccd89b7` without changing representation bytes, evidence mapping, headline retrieval scores, or the frozen E1 V2 design.

## Inputs

Use the exact SHA-bound raw cache archives already verified by the audit:

- `03_regen_caches.tar.gz` SHA256 `a16bdf95d3a96cb964fd6fd614d3b49d22bb9329c5afaf81cd692214d50f8aad`
- `04_bench3_runs_caches.tar.gz` SHA256 `87d6312ef6c195ac6c161a8693ab635c447074c969f6573a0d0b0ca994219ae4`
- `07_drive_frozen.tar.gz` SHA256 `370ea40962b078fc2fc09ab5319942b242f1559adeb62765e271f90cc21a9f59`

No refit. No evidence remapping. No new threshold choice. No new benchmark filtering.

Use the exact per-query `Delta_q = FR_SIGN96 - FR_centered_float96` values from the recovered/frozen evaluation surface. Before Claim-D computation, headline gates must reproduce:

- LME SIGN `0.5419751773049645`, centered float `0.4415957446808511`
- REALTALK SIGN `0.22477507598784194`, centered float `0.17253405381064954`
- PerLTQA SIGN `0.488941994930817`, centered float `0.551692074528853`
- LoCoMo SIGN `0.23654714666441054`; centered float frozen-cache candidate `0.16826334541318252`

## TOP64 / BOT64 construction

For each archive independently:

`v_j = mean_i(C_ij^2)`.

Use stable descending sort of `v_j`.

- TOP64 = first 64 axes.
- BOT64 = last 64 axes.

Binary code uses `C >= 0`; query code uses `qC >= 0`.
Distances are ordinary Hamming distances on the selected 64 axes.

## Correct per-gold competition metric

The R1 bug is forbidden: do **not** replace a multi-gold query by `dmin = min(distance[gold])` and count once.

For every gold row `g` separately and for each arm A in {TOP64, BOT64}:

- `strict_all(A,g) = count_i[d_A(i) < d_A(g)]`
- `tie_all(A,g) = count_i[d_A(i) == d_A(g)]`

Aggregate inside the query by arithmetic mean over its gold rows:

- `STRICT_A_q = mean_g strict_all(A,g)`
- `TIE_A_q = mean_g tie_all(A,g)`

Primary gaps:

- `STRICT_GAP_q = STRICT_TOP64_q - STRICT_BOT64_q`
- `TIE_GAP_q = TIE_TOP64_q - TIE_BOT64_q`

This is the exact variant independently used for the audit's corrected headline coefficients.

Also compute a mandatory sensitivity variant with all gold rows excluded from the competitor mask:

- `strict_nongold(A,g)`
- `tie_nongold(A,g)`

Report it separately; it is not allowed to replace the primary after outcomes are seen.

## Primary corrected summaries

Spearman uses average ranks for ties.

Report separately for LME, REALTALK, PerLTQA, LoCoMo:

- `rho(Delta_q, STRICT_GAP_q)`
- `rho(Delta_q, TIE_GAP_q)`
- n, multi-gold n/rate.

Expected independent-audit targets (tolerance `1e-12` when using the identical rows/rank implementation):

| benchmark | strict rho | tie rho |
|---|---:|---:|
| LME | 0.14168629605302735 | 0.14045379360271315 |
| REALTALK | 0.09793912889111700 | 0.12281952421315011 |
| PerLTQA | 0.25416826537535475 | 0.27978783415712220 |
| LoCoMo | 0.09491957131277647 | 0.10376015063205302 |

PerLTQA must additionally persist section summaries. Expected point values:

- dialogues: strict `0.13054126734088975`, tie `0.11123087254360414`
- events: strict `0.39790634780463613`, tie `0.38922832069574037`
- profile: strict `0.0573253028779693`, tie `0.018738683422868593`
- social_relationship: strict `0.30428515802019`, tie `0.2993013213223269`

## Descriptive bootstrap

The old R1 competition bootstrap is superseded and must not be reused.

Regenerate from the corrected per-query rows.

Use the existing recovery convention:

- seed `96013`
- B = 2000
- resample at the archive/conversation cluster level when multiple queries share a cluster;
- LME's one-query-per-archive surface reduces to query/archive resampling;
- for each resample recompute average-rank Spearman from the resampled corrected rows;
- report percentile 2.5% / 97.5% intervals;
- label intervals **descriptive/post-hoc**, not preregistered inference.

Do not silently drop undefined bootstrap replicates; record attempted B, valid B, invalid B and the reason for every invalid class.

## Persisted outputs required before R2 can seek PASS

1. `E1_V2_COMPETITION_PER_QUERY_R2.json.gz` — qid, benchmark, cluster/section where applicable, Delta, gold_n, TOP/BOT per-gold averaged strict/tie values, primary gaps, non-gold sensitivity gaps.
2. `E1_V2_COMPETITION_SUMMARY_R2.json` — primary + sensitivity correlations, multi-gold counts, section summaries.
3. `E1_V2_COMPETITION_BOOTSTRAP_R2.json` — frozen seed/B, valid/invalid replicate ledger, descriptive intervals.
4. exact input archive SHA256 inventory.
5. executable script SHA256 and package manifest.
6. corrected prose that contains none of the R1 min-gold coefficients as current values.

## Other independent-audit dispositions that are binding in R2

- LoCoMo old `~+12pp` is not an anchor. Use centered float `0.16826334541318252` / SIGN-minus-float `+6.828380125122796 pp` only with frozen-cache exploratory wording.
- `Q_EFF = 96/(1+Q_ABS_CV^2)` at fixed dimension 96; Q_EFF and Q_ABS_CV are one algebraically redundant diagnostic family.
- P64 effect size is tied-rank-method sensitive; average-rank Spearman is the frozen descriptive convention.
- say `all 520 recovered archives`, never universal/population-wide.
- causal and deployable-router claims remain forbidden.

Task4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.
