# E1 V2 raw-cache recovery R2 — independent-audit findings disposition

**Labels:** [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Status: **R2 REPAIR CANDIDATE / NOT YET RE-AUDITED / NOT FOR CLAIM UPGRADE**.

Parent lead target: `d5441698fa8fb8404873af47233569803b887376`.
Independent audit: `010bcbbe0ade15ed1dc501ce6d2f4e2e5ccd89b7`.
Audit verdict: `REQUEST_CHANGES`.
Frozen V2 design: `775a09c1ba6fd8c28f1e98ec1826d31a7f2c3484`.

Task4F1 remains exactly:
`SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.

## Disposition

### F1 HIGH — competition metric used min-gold collapse instead of per-gold aggregation

**ACCEPTED. BLOCKING FOR R1 CLAIM D.**

R1 collapsed all gold rows to `dmin=min(distance[gold])` and counted ranking competition once per query. That is not the frozen V2 metric for multi-gold queries. The corrected computation is per gold, then aggregated within query.

Independent raw-cache recomputation at `010bcbbe...` gives the corrected average-rank Spearman coefficients:

| benchmark | per-gold strict rho | per-gold gold-distance tie rho |
|---|---:|---:|
| LongMemEval | +0.14168629605302735 | +0.14045379360271315 |
| REALTALK | +0.09793912889111700 | +0.12281952421315011 |
| PerLTQA | +0.25416826537535475 | +0.27978783415712220 |
| LoCoMo | +0.09491957131277647 | +0.10376015063205302 |

The qualitative predicted direction remains positive on all four benchmarks, but all R1 Claim-D numeric values and any R1 competition-derived bootstrap/prose are superseded.

Multi-gold prevalence explains why this is material: LME 296/470, REALTALK 386/705, PerLTQA 2322/8265, LoCoMo 432/1535. PerLTQA events/profile/social are single-gold in the recovered surface; dialogues exposes the bug.

The audit also computed a non-gold-only sensitivity variant. Its strict/tie coefficients remain positive on all four. R2 therefore treats the positive direction as robust descriptive evidence, not as a causal or deployable result.

**Required before PASS:** regenerate the full competition per-query rows and the descriptive cluster bootstrap with the per-gold implementation. Until that executable rerun is persisted, R2 Claim D is `CORRECTED_SUMMARY_FROM_INDEPENDENT_AUDIT / FULL_PAYLOAD_PENDING`.

### F2 MEDIUM — old LoCoMo ~+12pp is not an anchor

**ACCEPTED / CLOSED IN WORDING.**

Keep the independently confirmed frozen-cache centered-float value:
`0.16826334541318252`.

With SIGN `0.23654714666441054`, the descriptive SIGN-minus-float gap is:
`+6.828380125122796 pp`.

The historical `~+12pp` line remains `PROGRAMME_REPORTED_NOT_RECOMPUTED / NOT_AN_ANCHOR` and must not be promoted to a measurement.

### F3 MEDIUM — Q_ABS_CV and Q_EFF are algebraically redundant

**ACCEPTED / CLOSED IN INTERPRETATION.**

At fixed dimension 96 under the frozen definitions:
`Q_EFF = 96 / (1 + Q_ABS_CV^2)`.

The audit verified max residual <= `2.842170943040401e-14` and rank correlation -1 on all four benchmarks. They are one degree of evidence, not two independent mechanistic signals.

### F4 MEDIUM — P64 Spearman magnitude is tie-rank-method sensitive

**ACCEPTED / CLOSED IN SCOPE.**

Average-rank Spearman remains the frozen/descriptive convention and reproduces the R1 point estimates. Alternative tied-rank conventions can materially change magnitude. P64 is therefore licensed only as a descriptive regime marker, never as a router or stable effect-size claim.

### F5 LOW — 520/520 is sample-wide, not universal

**ACCEPTED / CLOSED IN WORDING.**

Replace universal wording with:

> In all 520 recovered archives, high-variance TOP64 sign bits are more redundant and BOT64 sign bits have higher binary effective dimension under the frozen metrics.

No population-universal law is claimed.

### F6 LOW — imperfect cold-start blinding

**ACCEPTED / DISCLOSED.**

The audit saw target diff prose during mandatory Git scope verification before freezing its raw-only table. It did not intentionally inspect lead result JSON/per-query/archive outputs before Stage-1 freeze. Treat the audit as independently recomputed, not perfectly blind.

## Licensed R2 interpretation

The strongest allowed interpretation after the audit is:

> Across all 520 recovered archives, TOP64 sign bits are structurally more redundant and BOT64 bits have higher binary effective dimension, but this structural asymmetry does not determine SIGN-vs-float direction. P64 and correctly computed per-gold TOP-vs-BOT ranking competition are weak-to-moderate descriptive markers of a query–archive ranking regime. The underlying cause remains unresolved; causal, universal, and deployable-router claims are rejected.

The working `signal-versus-redundancy tradeoff` remains a mechanism hypothesis only.

## State

R2 is not PASS yet. The only remaining blocking repair is executable regeneration of Claim-D per-query competition rows + descriptive bootstrap under the frozen per-gold definition, followed by independent re-audit. No E2/new-codec promotion occurs before that gate.
