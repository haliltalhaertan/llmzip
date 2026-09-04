# V52 MATCHED RANDOM-PARTITION NULL — COLD-START INDEPENDENT AUDIT

Repository: `haliltalhaertan/llmzip`

Audit target commit (immutable scientific package before this prompt):

`410bcf59e29c64096bfb988d6d95e89658f50f6e`

Research branch for navigation only:

`research/v52-sign-mechanism-locomo-2026-09-04`

Primary claim requiring independent adjudication:

**`[CROSS-BENCHMARK SPECTRAL POSITION CAUSAL LEAD]`**

Benchmark-level producer claim on both LoCoMo and LongMemEval:

**`[SPECTRAL POSITION LOAD-BEARING LEAD]`**

This is a ZERO-TRUST audit. Do not accept producer summaries, checkpoint prose, provenance manifests, CI green status, or this prompt's quoted numbers as evidence by themselves. Reconstruct the claim from repository bytes and immutable artifacts.

Do not modify `main`.
Do not execute, inspect, infer, or reveal any Task 4F1 outcome.
Task 4F1 is out of scope and remains blocked unless an independently valid authorization says otherwise.
Do not start boundary localization.

==================================================
1. AUTHORITATIVE INPUTS TO LOCATE AND HASH
==================================================

At audit target commit `410bcf59e29c64096bfb988d6d95e89658f50f6e`, independently locate and hash:

Preregistration:
`research/v52/V52_MATCHED_RANDOM_PARTITION_NULL_PREREG_2026-09-04.md`
expected Git blob only as a producer claim: `2d6a14f254399327f59db1958a0b5c0dfb9ea8e0`

Pre-run seal:
`research/v52/V52_MATCHED_RANDOM_PARTITION_NULL_PRERUN_SEAL_2026-09-04.json`
producer-claimed blob: `df309826982504c5ea0ff3917d67cf2da632bac4`

LoCoMo runner:
`research/v52/locomo_matched_random_partition_null.py`
producer-claimed blob: `ebf76908c73bbf266c04f6ae05537a03e70c7526`

LongMemEval runner:
`research/v52/longmemeval_matched_random_partition_null_shard.py`
producer-claimed blob: `277c06e8be87fa1c3322b829b780b1375f7ca0c4`

LoCoMo workflow:
`.github/workflows/v52-locomo-matched-random-partition-null.yml`
producer-claimed blob: `f5673def52076905b56c9991a41e78e89b4f22ad`

LongMemEval workflow:
`.github/workflows/v52-longmemeval-matched-random-partition-null.yml`
producer-claimed blob: `e8c0d91ec70e0d2ca0973fcc5ae4b7ed4989f054`

Trigger:
`research/v52/TRIGGER_MATCHED_RANDOM_PARTITION_NULL_2026-09-04.txt`
producer-claimed trigger commit: `9fd60f60f3ecb407f9a0547853d88e487dabd05b`

Persisted LoCoMo output directory:
`research/v52/locomo_random_partition_outputs/`

Persisted LongMemEval output directory:
`research/v52/longmemeval_random_partition_outputs/`

Cross-benchmark checkpoint:
`research/v52/CROSS_BENCHMARK_MATCHED_RANDOM_PARTITION_NULL_CHECKPOINT_2026-09-04.md`
producer-claimed blob: `60031b16b1440e8c5e6c59b84ce35104c912db88`

Producer provenance manifest:
`research/v52/V52_MATCHED_RANDOM_PARTITION_NULL_PROVENANCE_MANIFEST_2026-09-04.json`
producer-claimed blob: `aeebcf1263afeccb96f63313a40752b2d1eb1b8b`

The provenance manifest is an index, not an authority. Any mismatch must be reported, not silently repaired.

==================================================
2. TEMPORAL / PREREGISTRATION AUDIT
==================================================

Independently reconstruct Git ancestry and timing.

Verify all of the following:

A. The scientific preregistration existed before either matched-null outcome was computed or persisted.

B. The two runners and two workflows were frozen before trigger.

C. The pre-run seal was committed before the trigger file existed.

D. The pre-run seal binds the exact preregistration, runner, and workflow blobs that the triggered Actions runs actually used.

E. The workflow's first scientific gate recomputed Git blob hashes and would have failed on drift.

F. No post-outcome change altered:
- seeds;
- random subset generation;
- coordinate split size;
- rotation RNG mapping;
- decision thresholds;
- top-k;
- tie/nuisance semantics;
- representation;
- source cohort.

G. The Stage-B matched-null hypothesis is honestly post-Head/Tail and not retroactively represented as preregistered before the Head/Tail result.

Return a temporal verdict:

`[PREREGISTRATION ORDER VALID]`
or
`[PREREGISTRATION ORDER INVALID]`
or
`[PREREGISTRATION ORDER INCONCLUSIVE]`

==================================================
3. DESIGN / MATCHED-CONTROL AUDIT
==================================================

Read the preregistration first, then inspect runner code independently.

Verify exact implementation of the frozen design:

For every seed `s` in exactly:
`57001,57002,57003,57004,57005,57006,57007,57008,57009,57010`

Random partition must be:

`perm = numpy.random.default_rng(s).permutation(96)`
`S = sort(perm[:32])`
`T = sort(perm[32:])`

Verify:
- `|S|=32`;
- `|T|=64`;
- no overlap;
- union exactly `0..95`;
- no redraw or outcome-conditioned selection;
- all ten actual partitions are logged.

Rotation must be generated from:

`rotation_rng = numpy.random.default_rng(1_000_000 + s)`

Then:
- Q32 drawn first from a 32x32 standard-normal matrix -> QR -> deterministic diagonal-sign correction;
- Q64 drawn second from the same RNG stream from a 64x64 standard-normal matrix -> QR -> same sign correction.

CRITICAL MATCHED-CONTROL CHECK:

Independently verify that for each seed the **same numeric Q32 and Q64 matrices** are embedded into both arms:

Arm A:
`SPECTRAL_HEAD32_TAIL64_HAAR_NEW`
- Q32 on coordinates `0..31`
- Q64 on `32..95`

Arm B:
`RANDOM32_COMPLEMENT64_HAAR`
- identical Q32 on sorted S
- identical Q64 on sorted T

Check orientation/indexing carefully. A transpose, re-ordering mismatch, independent redraw, or embedding bug invalidates the matched-control interpretation.

Return:

`[MATCHED INTERVENTION VALID]`
or
`[MATCHED INTERVENTION INVALID]`

==================================================
4. SOURCE / REPRESENTATION IDENTITY AUDIT
==================================================

Independently verify source hashes and cohorts.

LoCoMo producer claims:
- dataset SHA-256 `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4`
- audit manifest SHA-256 `90a4e94c9247d8ace7aaf62acdda7315744b111d84e42658cccfeb0a3c89df06`
- evidence-valid questions `1535`

LongMemEval producer claims:
- dataset bytes `277383467`
- dataset SHA-256 `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`
- adapter v1 SHA-256 `0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722`
- adapter v2 SHA-256 `643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218`
- primary questions `470`

Verify that the representation pipeline is inherited unchanged from the frozen causal base and that query/gold/outcome metadata does not enter the archive representation fit in a way forbidden by the frozen design.

Check centering, transform application point, sign threshold, Hamming distance, top-k, and nuisance/tie priorities.

==================================================
5. LONGMEMEVAL SHARD-EQUIVALENCE AUDIT
==================================================

Do not assume sharding is harmless.

Verify:
- deterministic partition of exactly 470 primary questions;
- all 10 shards disjoint/exhaustive;
- aggregator requires 10/10 shard indices;
- exactly 470 unique qids after aggregation;
- global lexicographic question ordinal, not shard-local ordinal, controls tie RNG;
- spectral and random arms use the same per-question nuisance priorities;
- result is invariant to shard ordering except normal floating aggregation tolerance;
- partition definitions are identical across all shard payloads and checked by aggregator.

Return:

`[SHARDING SEMANTICS PRESERVED]`
or
`[SHARDING CHANGES ESTIMAND]`

==================================================
6. CONTROL AUDIT
==================================================

Independently confirm, rather than merely copy, the following controls:

- frozen native reproduction;
- signed-permutation Hamming invariance;
- every Q/R matrix orthogonality;
- common archive/query transform continuous norm preservation;
- continuous query-archive dot-product preservation;
- partition cardinality/disjointness/exhaustiveness;
- frozen cohort size.

Producer-reported values to challenge:

LoCoMo:
- native reproduction error `0.0`
- continuous norm max `4.440892098500626e-16`
- continuous dot max `1.7763568394002505e-15`

LongMemEval:
- native reproduction error `0.0`
- continuous norm max `6.661338147750939e-16`
- continuous dot max `7.771561172376096e-16`

Any failed load-bearing control must force `[FAIL]` unless you can prove it is a reporting-only defect with no effect on the estimand.

==================================================
7. INDEPENDENT NUMERICAL RE-DERIVATION
==================================================

Do not use the producer's summary JSON arithmetic as authority.

Recompute from the committed per-seed CSVs and, where feasible, from lower-level question/shard records or an independent rerun.

For each benchmark independently derive:

`R_spec = mean of the ten spectral arm R@3 values`
`R_rand = mean of the ten matched-random arm R@3 values`
`L_full = R_native - R_fullhaar_frozen`
`rho_spec = (R_native - R_spec)/L_full`
`rho_rand = (R_native - R_rand)/L_full`
`Delta = rho_rand - rho_spec`

Also derive:
- sample SD of spectral R@3;
- sample SD of random R@3;
- sample SD of rho_spec;
- sample SD of rho_rand;
- sample SD of Delta;
- min/max of all primary paired quantities;
- every per-seed Delta.

Producer claims to verify, not assume:

LoCoMo:
- R_spec `0.2301279412463207`
- R_rand `0.14298280722884044`
- rho_spec `0.06494615954655526`
- rho_rand `0.9466349993608402`
- Delta `0.8816888398142849`
- Delta sample SD `0.12128537114222615`
- Delta min `0.613784339009036`
- Delta max `1.0465011549547585`

LongMemEval:
- R_spec `0.5148030141843971`
- R_rand `0.38202482269503546`
- rho_spec `0.1706167099746428`
- rho_rand `1.0043441569864096`
- Delta `0.8337274470117668`
- Delta sample SD `0.09614763309727813`
- Delta min `0.6893760757410925`
- Delta max `0.9759768786642199`

Check the inherited Full-Haar constants and quantify any rounding difference from their original accepted values. Decide explicitly whether it can change a decision threshold.

==================================================
8. MANDATORY INDEPENDENT RERUN
==================================================

At minimum, rerun **one full benchmark end-to-end** from the frozen source bytes using an isolated environment and the audited runner bytes.

Preferred: LoCoMo because it is smaller and therefore the cheapest cold-start reproduction.

The rerun must:
- verify source hashes;
- use the audited preregistered seed panel;
- regenerate all ten random partitions;
- regenerate all paired Q32/Q64 matrices;
- reproduce native R@3 within the frozen tolerance;
- independently derive R_spec, R_rand, rho_spec, rho_rand and Delta;
- compare every per-seed result against the committed package.

If computationally feasible, independently rerun LongMemEval as well. Otherwise independently reaggregate its immutable shard outputs and fully audit the sharding code.

Do not alter code or thresholds to obtain agreement.

==================================================
9. IMMUTABLE ARTIFACT / PROVENANCE AUDIT
==================================================

Producer claims:

LoCoMo Actions run `33907122988`
job `101134570493`
artifact ID `9949936324`
artifact digest `sha256:5b306f7874fe5bd441a3fb045bc776de8e538fb0507dff8fe4317180d26bd1e3`
Drive artifact ID `19zuaMJeF32BAdG7dSKOmovjGzhSmvzT7`

LongMemEval Actions run `33907122993`
aggregate job `101135639725`
artifact ID `9950032044`
artifact digest `sha256:87069e0f6dfe2f47833518ef8bf719b1bb692f7c71c3664e3c6cca808cee124e`
Drive artifact ID `1YHi5QT1cX4T_qXHzaXRtxNUw5m5DP7R4`

Where your tools permit, fetch artifact metadata/bytes independently and compare identities. Verify that repository-persisted outputs correspond to the same scientific run rather than a later manual reconstruction.

Drive copies are redundancy, not scientific authority.

==================================================
10. PREREGISTERED DECISION AUDIT
==================================================

Verify the decision rule was frozen before outcome access:

Replication gate:
`rho_spec <= 0.25`

After passing:
- `Delta <= 0.05` -> generic block structure / spectral-position falsified
- `Delta >= 0.25` -> spectral-position load-bearing lead
- otherwise mixed

Cross-benchmark:
- both load-bearing -> `[CROSS-BENCHMARK SPECTRAL POSITION CAUSAL LEAD]`
- both generic/falsified -> cross-benchmark generic-block lead / spectral position falsified
- disagreement/mixed/replication failure -> heterogeneous/mixed; universal spectral-position claim withheld

Determine whether the producer verdict follows mechanically with no discretionary reinterpretation.

==================================================
11. INTERPRETATION / OVERCLAIM AUDIT
==================================================

Separate what the experiment establishes from what it does not.

The strongest producer statement permitted for audit is approximately:

> On the two frozen memory-retrieval benchmarks, preserving the separation between the leading 32-dimensional archive-local SVD subspace and the remaining 64-dimensional tail retains most of Native SIGN96's advantage over unrestricted Full-Haar, while matched-size arbitrary 32/64 partitions lose approximately as much as Full-Haar. This supports a cross-benchmark causal lead that spectral coordinate position matters more than generic 32/64 block structure.

Challenge all stronger formulations.

In particular the experiment does NOT by itself prove:
- coordinate 32 is uniquely optimal;
- the 32/64 split is necessary;
- a sharp spectral phase boundary exists;
- individual Head32 axes are necessary;
- universal generalization;
- production superiority;
- neuron-axis correspondence;
- transfer to Task 4F1.

Classify the producer's phrase `SPECTRAL POSITION LOAD-BEARING LEAD` as acceptable or too strong, with reasoning.

==================================================
12. ADVERSARIAL CHECKS
==================================================

Actively search for counterexplanations or implementation defects, including:

- random partition accidentally not uniform;
- Q32/Q64 not actually matched across arms;
- sorted-index embedding causing a hidden orientation mismatch;
- spectral and random arms receiving different nuisance priorities;
- random arm unintentionally mixing Q32/Q64 blocks;
- sign threshold differences;
- query/archive transform asymmetry;
- per-seed selection or missing seeds;
- outcome-driven retries;
- artifact/result commits from a different workflow attempt;
- hidden difference in representation fit;
- denominator drift;
- aggregation-weighting errors;
- use of rounded Full-Haar constants capable of crossing thresholds;
- treating two benchmarks sharing the same representation family as population-independent evidence.

If you find a defect, construct the smallest concrete reproducer/counterexample possible.

==================================================
13. REQUIRED AUDIT OUTPUT
==================================================

Return exactly one primary verdict:

`[VALID — LOAD-BEARING CROSS-BENCHMARK CAUSAL LEAD]`

or

`[VALID WITH CAVEATS — LOAD-BEARING LEAD SURVIVES]`

or

`[FAIL — LOAD-BEARING CLAIM INVALID]`

or

`[INCONCLUSIVE — REQUIRED EVIDENCE MISSING]`

Then provide:

1. exact audited commit / blob identities;
2. preregistration-order verdict;
3. matched-intervention verdict;
4. source/representation verdict;
5. sharding verdict;
6. independent arithmetic table;
7. independent rerun result;
8. artifact/provenance verdict;
9. interpretation-limit verdict;
10. every discrepancy found, even if decision-irrelevant;
11. whether the cross-benchmark verdict mechanically follows;
12. whether boundary localization may now proceed.

Final line must be exactly one of:

`NEXT: AUTHORIZE SEPARATE PREREGISTERED BOUNDARY LOCALIZATION`

or

`NEXT: REPAIR AND RE-AUDIT BEFORE ANY BOUNDARY LOCALIZATION`

or

`NEXT: ABANDON SPECTRAL-POSITION MECHANISM CLAIM`

Do not execute boundary localization during this audit.
Do not touch Task 4F1.
