# Coordinator review — PerLTQA transfer pilot

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Worker verification.py rerun: 32/32 checks pass. Independently parsed 90915 unique (qid,group,t) cells for 8265 QA in 30 archives, recomputed paired LOW48 endpoints and clustered bootstrap from per-archive sums/counts (2000 draws, seed20260913). Confirmed raw contrast +2.464151118446995 pp, nominal 95% CI [1.5540102909721127,3.442841180708553] pp. Section contrasts in independent COORDINATOR_AGGREGATE.json reproduce the report: events +4.94708, social +8.64929, profile -18.61862, dialogues -0.81466 pp.

This supports ONLY the prespecified positive aggregate endpoint direction for the chosen proxy in this exploratory dataset. Model-H's stronger pointwise/aggregate monotonic law does not transfer: 961 QAs have a decreasing adjacent contrast, and the overall curve decreases then increases. Real intervention t=1 is unmodified embeddings, NOT the synthetic law's identified signal/nuisance balance point. No causal account of the baseline reversal follows.

Interpretation caution: native codes/recall are invariant, so the positive contrast comes from perturbing/degrading float relative to sign; this is not a newly improved compressed method or absolute sign recall gain. Overall sign still trails float at the tested upper endpoint. Profile moves strongly opposite to events/social, and section comparisons are exploratory pre-known strata without separate adjusted significance tests.

HIGH48 endpoints are algebraic negatives of LOW48 endpoints. Report prose 'CIs mirror likewise' is not literally true of stored sampled CIs because separate bootstrap samples were used; with identical archive draws they must mirror. This is no independent replication. Likewise baseline is within floating tolerance, not bit-identical: explicit nonzero max differences override 'bit-for-bit in practice'.

FULL96 only t4 control (11 rows per QA) is sufficient for the stated PLAN control; REALTALK/LME ran extra global-scale values (15 rows per QA). Different row counts are not missing primary arms. Archive-cluster nominal intervals are unadjusted across four benchmark primaries; no familywise or universal applicability claim. Worker verification asserts positive-CI as a check: that is an observed outcome, not a general correctness invariant; don't turn null/negative results in other datasets into test failures.

Source files and raw worker outputs preserved unchanged. Separate adversarial audit/recompute role remains pending. No preregistration, no literature novelty, no frozen storage measurement authorization.
