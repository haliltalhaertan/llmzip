# Theory-to-benchmark transfer test v1

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Prospective analysis specification for this exploratory wave, before inspecting NEW intervention outcomes. Existing benchmark outcomes were already known; this is NOT preregistration. Source caches/frozen artifacts are read-only. User authorizes exploratory benchmark analysis, not Task4F1 measurement or rewriting frozen protocols.

## Question and scope

Model H proves an ordering for synthetic signal/nuisance vectors, NOT arbitrary benchmark vectors. Real coordinates do not come labeled signal/nuisance. We test a specified query-only proxy and positive diagonal perturbation; success is compatibility with a proposed transfer hypothesis, failure falsifies that proxy/transfer, not the conditional mathematical theorem.

Four benchmarks independently: LongMemEval, LoCoMo, REALTALK, PerLTQA. Never pool benchmarks or tune choices using PerLTQA section outcomes. No training, embedding/API calls, learned routing, or new codec claim.

## Gate before new experiments

Read the historical producer and cached representations. Recompute ORIGINAL native SIGN96 and centered-float96 fractional R@3 with exact original seed/index/tie/exclusion/weight conventions. Compare per-QA arrays when available, not just averages. Abort new experiments if gate cannot be reproduced. Report expected/evaluated/unresolved/excluded counts explicitly and reproduce source units. Source data is authority over an inconsistent prompt.

Known native anchors: LME 0.5419751773049645 (470 QA); LoCoMo 0.23654714666441054 (1535 valid QA); REALTALK 0.22477507598784194 and FLOAT96 0.17253405381064957 (705 of 728 QA); PerLTQA 8265 QA, 30 archives, native/float rounded 0.488942/0.551692 (do NOT use rounded numbers for 1e-12 gate; derive exact expected arrays from results_rerun.json). Gates tolerance 1e-12 for stored-score replication; any cross-stack difference must be exposed, not silently relaxed. No new score after a failed gate.

## Fixed interventions (gold-free construction)

For each query in the original centered 96-coordinate representation, rank coordinate indices by (abs(q_j), j). LOW48 = first48, HIGH48 = last48. Do not inspect gold labels to choose coordinates. Proxies mean low/high query magnitude, NOT proven nuisance/signal dimensions.

For each group and t in {0.25,0.5,1,2,4}, multiply BOTH document coordinates and query coordinates in that group by positive t. Do not refit/recenter SVD or recompute archive mean. Cosine must recompute full norms after transformation; include exact convention for zero-norm cases inherited from producer. Sign encodings should be byte-identical for all positive t (verify, don't use this tautology as evidence of empirical theory validity). t=1 restores original arrays/scores. FULL96 positive scale t=4 is an additional cosine/sign invariance control.

Primary outcome = expected fractional R@3 under uniform tie priorities. Compute exact tie-bucket expectation from distances/scores, not assume independent pair comparisons or independently redrawn gold per distractor. For float scores use producer's exact equality tie convention; do NOT invent a tolerance to create float ties. Also compute original 20-seed scores at t=1 for gate, and at the endpoint t=.25/4 for sensitivity if feasible. The exact expectation and 20-seed result may differ; report both explicitly rather than gate exact expectation to an MC number.

Store every per-QA/group/t native and float score, delta=sign-float, archive id, QA id, gold count, section, group indices (or reproducible mapping), diagnostic query concentration (sum q^4/(sum q^2)^2), and doc RMS(group)/RMS(complement) (clearly neither is model-H true t).

## Predictions fixed before outcomes

Primary per benchmark: LOW48 endpoint contrast mean[delta(t=4)-delta(t=.25)] > 0. A positive effect with cluster-bootstrap interval excluding zero is 'consistent with this proxy transfer', not causal explanation/confirmation of Model H. Nonpositive effect or uncertainty is negative/inconclusive respectively; never redefine nuisance after seeing it.

Also report full curve and fraction of individual QAs with any decreasing adjacent delta as t increases. Model H pointwise monotonicity is a stronger property than an aggregate trend; violations show it cannot transfer unconditionally. HIGH48 is a predeclared comparison, not guaranteed negative control. Global scaling is the true invariance control.

Use archive-cluster paired bootstrap, 2000 reps, seed 20260913, resample whole archives with replacement and retain within-archive QAs; calculate question-weighted replicate means consistently. Report number of clusters, few-cluster limitations, and raw effects. Four primary comparisons exist (one per benchmark); do not make familywise-significance claims from nominal individual 95% intervals. No benchmark pooling.

PerLTQA sections (profile/social/events/dialogues) and single-gold vs multigold are secondary, explicitly already known strata. Compare curves without choosing t/groups based on their outcomes. No explanation of the reversal without a demonstrated link; distinguishing diagnostic association from intervention behavior is mandatory.

## Outputs and verification

Each worker has its own persistent workspace. Write STATUS.md immediately. Seal this PLAN.md plus benchmark adapter/analysis choices and source hashes in PRE_RUN.json before NEW intervention metrics. Save runner, gate.json, per_query.jsonl/csv, summary.json, REPORT.md, verification.py, and stdout receipts. Hash source files actually read before/after; source content must remain unchanged. Use threads=1. Checkpoint batches and assert total count (no silent subsampling). First-pass ~25 minutes target: if full run cannot finish, persist progress and state INCOMPLETE with exact count; never extrapolate partial output.

Required checks: baseline per-QA reproduction; positive-scale sign invariance; t1 identity; FULL96 cosine invariance (allow explicitly reported floating ulps; measure both scores and resulting ranks); independently manually recompute representative QAs via direct sorting/random permutations; artifact count/schema checks. Reports start with all four labels. All results provisional until separate recompute + adversarial review. Heavy caches remain outside Git. No push by workers.
