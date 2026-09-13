# Coordinator review — LongMemEval transfer pilot

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Reran worker verification.py successfully (reported 45 gate/artifact checks plus 24 manual outcome recomputes; these reported categories include overlapping checks, not an independent total count). Independently parsed 7050 unique (qa_id,group,t) rows for 470 QA, rebuilt paired LOW48 endpoint differences and the seeded 2000-replicate archive bootstrap. Stored COORDINATOR_AGGREGATE.json contains results.

Confirmed primary effect = -6.443262411347517 percentage points; nominal cluster-bootstrap 95% interval [-9.273404255319148,-3.687056737588658] pp, matching worker. Unlike REALTALK's original report, this point estimate is the actual mean paired contrast, not mean bootstrap estimate. Native/float baseline replication gate within 1e-12 is supported by per-QA checks. Worker final stdout contains a stray '0.541595...' typo; actual float baseline 0.44159574468085105 governs.

Interpretation: clear observed opposite direction for this predeclared LOW48 query-magnitude proxy on evaluated LME data, not support for the proposed mapping to synthetic nuisance coordinates. Do not infer which real coordinates are intrinsically irrelevant/relevant from this intervention alone. Positive scaling affects BOTH query and document; it changes effective score weighting and normalized geometry, not just Model H's one latent nuisance parameter. This does not disprove the conditional synthetic theorem.

Float exact means at LOW48 t=.25,1,4 are 42.52836879432624%,44.15957446808511%,48.97163120567375%; native expected mean remains fixed. This is reweighted float retrieval, not a new compressed codec or proof of lower total storage. HIGH48 reciprocal curve equals LOW48 per QA exactly and is not independent corroboration. 114/470 QAs violate claimed increasing adjacent delta monotonicity for this proxy.

Nominal intervals are exploratory, unadjusted across four benchmark primaries; benchmark is not an independent sample of every real-world setting. Archive-cluster bootstrap uses one QA per supplied LME archive; shared upstream sources could add dependence. Source report's '18 files unchanged' is not by itself proof all 470 cache bytes were included in before/after hashes; inspect checkpoint pkl manifest before broader read-only coverage assertions.

All source worker files preserved with this note. No external independent review complete, no preregistration, no literature priority or deployment claim.
