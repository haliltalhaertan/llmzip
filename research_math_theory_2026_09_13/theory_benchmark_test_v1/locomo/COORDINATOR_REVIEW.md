# Coordinator review — LoCoMo transfer pilot (CONDITIONAL)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Reran verification.py: 33/33 worker checks pass. Independently parsed 1535 unique QA rows (each nests all group/t outcomes), ten archive clusters; recomputed observed LOW48 paired contrast -2.5829067783465174 pp, seeded2000 cluster-bootstrap nominal95% CI [-3.776758909603851,-1.3132051635781277] pp, and 151 decreasing-adjacent QA. Raw recompute in COORDINATOR_AGGREGATE.json.

CRITICAL GATE DEVIATION: Shared PLAN required both native AND historical float replication before new interventions and abort on missing/unreproducible gate. Worker reproduced native but could not locate historical float arrays, substituted a fresh float baseline, and continued. Disclosure is appreciated, but sealing a new baseline does NOT satisfy the original replication criterion. Status must be CONDITIONAL/PROTOCOL-DEVIATION, not fully gated PASS. Subsequent computation can be preserved as exploratory output, not full acceptance.

Earlier programme prose repeatedly stated LoCoMo SIGN-minus-float about +12pp. Current exact-cache run instead gives MC native .23654714666441054 minus float .16826334541318252 = +6.828380125122796pp. Coordinator source search finds b3a_realtalk/report.md repeats +12pp explicitly as 'programme-reported; not recomputed here'. Historical +12pp is therefore not independently grounded by that report. Do NOT silently treat the current measurement as historical reproduction or continue quoting +12pp as established. Resolve baseline provenance with a separate independent recompute/audit.

Conditional result: tested query-magnitude proxy intervention moves opposite to prespecified direction in these arrays. No general theorem refutation or universal causal claim. The HIGH48 contrast is a reciprocal algebraic mirror, not independent support. Separate bootstrap draws explain non-mirrored numerical CIs; no independent sample gained. Only ten archive clusters, exploratory nominal intervals unadjusted across four primaries.

Verification includes a 'primary_not_positive' outcome assertion: this is not a correctness invariant and should not be reused as an acceptance criterion for other data. Worker raw files are preserved unchanged with this note. No storage measurements, improved codec, or new embeddings; not preregistered/not independently audited.
