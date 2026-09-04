# V52 Head/Tail Spectral Boundary Localization — Preregistration

Date: 2026-09-04
Status: `[PREREGISTERED — NO BOUNDARY-LOCALIZATION OUTCOME ACCESS YET]`
Branch: `research/v52-sign-mechanism-locomo-2026-09-04`

Binding post-audit interpretation addendum Git blob:
`456b3b51f49a0238cd936bc3f639988fb0d673af`

Independent Head/Tail audit:
- branch: `audit/v52-head-tail-causal-independent-2026-09-04`
- commit: `f939db0238f1c348c37851aeda9958700bb06d53`
- audited target: `7799502bc3a157f874b4b1aa76f803ec2bf6432f`
- audit report SHA-256: `e804936ed59ab1005d2087d171969a2d19fd437f498d29ad00b24543d1094851`
- verdict: `AUDIT PASS WITH CAVEATS`

## 1. Why this is a new experiment

The audited Head32/Tail64 experiment established that, on two frozen datasets evaluated through one shared pipeline, arbitrary Haar rotation *within* the leading 32-dimensional archive-local SVD subspace and *within* the remaining 64-dimensional tail preserves most of the Native SIGN96-vs-Full-Haar advantage.

The independent auditor additionally supplied a matched-size random 32/64 partition control on LoCoMo. A random coordinate partition lost almost all of the advantage while the spectral Head32/Tail64 partition preserved most of it. Thus generic 32/64 block-diagonality is not an adequate explanation on LoCoMo.

What remains unresolved is the location and uniqueness of the spectral boundary. The previous 32/64 split was inherited from the earlier three-band diagnostic and was never selected by a preregistered boundary scan.

This experiment asks whether the preservation effect is localized near the tested PC32 boundary, forms a broader plateau, shifts to another tested boundary, or fails to replicate under a new seed panel.

The experiment also repeats a matched random 32/64 partition control on **both** frozen datasets under new seeds. This is mandatory because the independent auditor's own random-partition control was run on LoCoMo only.

## 2. Binding interpretation narrowings inherited from audit

All reporting from this experiment must obey the post-audit addendum:

1. narrative `rho` values are reported approximately, with seed-panel standard errors;
2. per-seed sign inversions/ranges are disclosed rather than hidden by the mean;
3. results are described as consistency across two frozen datasets under one shared pipeline, not as independent methodological replication;
4. LongMemEval sharding is described as deterministic and semantics-invariant, not generically as bitwise `EXACT`;
5. uncertainty in the inherited frozen Full-Haar denominator is not identified here, so reported `rho` standard errors are conditional on that denominator.

Machine-readable outputs retain full float precision for reproducibility. Headline prose must not present those digits as measurement precision.

## 3. Frozen source identities and cohorts

### LoCoMo

- dataset SHA-256: `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4`
- audit-manifest SHA-256: `90a4e94c9247d8ace7aaf62acdda7315744b111d84e42658cccfeb0a3c89df06`
- evidence-valid denominator: `1535`
- frozen Native R@3: `0.23654714666441054`
- frozen Full-Haar96 R@3: `0.13770827054136`

### LongMemEval

- dataset SHA-256: `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`
- dataset bytes: `277383467`
- adapter v1 SHA-256: `0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722`
- adapter v2 SHA-256: `643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218`
- frozen primary cohort: `470`
- frozen Native R@3: `0.5419751773049646`
- frozen Full-Haar96 R@3: `0.38271666666667`

No source, evidence rule, representation recipe, archive/query centering, sign threshold, top-k, fractional evidence rule, nuisance/tie schedule, or cohort definition may change.

Task 4F1 execution candidates, authorization state, seals, HMAC material, and outcomes are outside this experiment and must not be touched.

## 4. Frozen boundary grid

The 96 archive-local SVD coordinates retain their existing order.

The only tested contiguous leading-vs-tail boundaries are:

`B = {16, 24, 32, 48, 64}`

For a boundary `b`:

- `Head_b = indices 0..b-1`
- `Tail_(96-b) = indices b..95`

No additional boundary, adaptive refinement, interpolated boundary, variance-based reordering, or outcome-dependent second-stage scan is permitted in this experiment.

The grid is deliberately coarse. A positive `b=32` result can localize only relative to this tested grid; it cannot establish that coordinate 32 is mathematically unique or globally optimal.

## 5. Primary spectral intervention for every boundary

For each `b in B` and frozen rotation seed `s`, construct

`R_b(s) = diag(Q_b(s), Q_(96-b)(s))`

in the native SVD coordinate order.

Exact construction:

1. `rng = numpy.random.default_rng(s)`
2. draw an IID standard-normal `b x b` matrix;
3. compute QR;
4. apply deterministic diagonal-sign correction exactly as in the audited Head/Tail runners;
5. this produces `Q_b`;
6. using the **same RNG stream**, then draw the IID standard-normal `(96-b) x (96-b)` matrix;
7. QR + the same deterministic sign correction produces `Q_(96-b)`;
8. place the two matrices on the leading and trailing coordinate blocks;
9. apply the identical `R_b(s)` to archive and query after the frozen archive-mean centering step and before zero-threshold sign quantization.

This preserves the audited intervention family while varying only the preregistered contiguous boundary.

## 6. New frozen rotation seeds

Use exactly ten new rotation seeds:

`58001, 58002, 58003, 58004, 58005, 58006, 58007, 58008, 58009, 58010`

The same ten seed labels are used for all five boundaries and both frozen datasets.

No seed replacement, extension, dropping, or rerun selection after outcome access.

The seed-panel size is increased from five to ten in direct response to the independent audit's finding that the five-draw Head/Tail magnitude was noisy relative to the LoCoMo intervention loss.

## 7. Fresh matched random-32/64 null control

A fresh matched random-partition arm is mandatory on **both** datasets.

Use exactly ten frozen partition seeds:

`68001, 68002, 68003, 68004, 68005, 68006, 68007, 68008, 68009, 68010`

Pair rotation seed `5800i` with partition seed `6800i` for `i=1..10`.

For each pair:

1. construct `Q32` and `Q64` using rotation seed `5800i` exactly as the spectral `b=32` arm;
2. therefore the spectral-32 and random-32 arms use the **same numeric Q32 and Q64 matrices** for that paired seed;
3. `perm = numpy.random.default_rng(6800i).permutation(96)`;
4. `S32 = perm[:32]` and `T64 = perm[32:]`, preserving permutation order;
5. require `S32` and `T64` to be disjoint, exhaustive, unique, in range `0..95`, and of cardinality 32/64;
6. place the same `Q32` on coordinates ordered by `S32` and the same `Q64` on coordinates ordered by `T64`;
7. apply the identical transform to archive and query at the same frozen pipeline location as every spectral arm.

Every `S32` and `T64` array must be persisted verbatim in the result package.

This matched construction isolates coordinate partition from the numeric Haar matrices.

## 8. Primary estimands

For each dataset `D` and each boundary `b`:

- `R_native(D)` = frozen/reproduced Native Fractional R@3
- `R_full(D)` = frozen Full-Haar96 Fractional R@3
- `R_b(D)` = mean over the ten frozen seeds of spectral-boundary Fractional R@3
- `L_full(D) = R_native(D) - R_full(D)`
- `L_b(D) = R_native(D) - R_b(D)`
- `rho_b(D) = L_b(D) / L_full(D)`

For the matched random 32/64 control:

- `R_rand32(D)` = ten-seed mean random-partition Fractional R@3
- `rho_rand32(D) = (R_native(D)-R_rand32(D))/L_full(D)`
- `Delta32(D) = rho_rand32(D) - rho_32(D)`

The machine-readable package stores exact float64 values. Narrative summaries report `rho_b` and `Delta32` to approximately three decimals plus conditional standard errors over the ten frozen draws.

For each arm, the following must also be reported:

- ten individual seed values;
- sample standard deviation;
- standard error of the mean;
- per-seed `rho` range;
- count and identity of any seeds for which `L_b` changes sign.

No uncertainty claim may imply that the frozen Full-Haar denominator is itself noise-free; its inherited sampling uncertainty is not quantified by this experiment.

## 9. Boundary sufficiency sets — primary localization object

For each dataset independently define the preregistered sufficiency set:

`S_D = { b in B : rho_b(D) <= 0.25 }`

The threshold `0.25` is inherited from the previously preregistered sufficiency criterion and is not re-tuned for this experiment.

Define:

`S_common = S_LoCoMo intersection S_LongMemEval`

The **sets**, not a visually chosen knee or winning boundary, are the primary localization result.

The boundary with numerically smallest mean `rho_b` may be reported as a secondary descriptive statistic only. It does not establish a unique optimum.

## 10. Mandatory premise-replication gates

Boundary interpretation is licensed only after these two gates are evaluated.

### Gate P1 — spectral 32/64 replication

For each dataset independently:

`rho_32 <= 0.25`

If P1 fails on a dataset, the historical PC32 sufficiency result did not replicate under the new seed panel. All boundary outcomes remain reportable, but no localization claim may silently assume the previous PC32 result.

### Gate P2 — matched position-dependence control

For each dataset independently:

- `Delta32 >= 0.25` -> `[SPECTRAL POSITION CONFIRMED UNDER NEW PANEL]`
- `Delta32 <= 0.05` -> `[GENERIC 32/64 BLOCK EXPLANATION NOT REJECTED — SPECTRAL POSITION LEAD FALSIFIED FOR THIS DATASET]`
- `0.05 < Delta32 < 0.25` -> `[MIXED / PARTIAL POSITION DEPENDENCE]`

These bands are frozen before localization outcomes.

A cross-dataset spectral-position statement requires `Delta32 >= 0.25` on **both** frozen datasets. The existing auditor-supplied LoCoMo null and later researcher-produced null results are historical evidence only and do not substitute for this fresh gate.

## 11. Frozen localization verdicts

After reporting P1 and P2, classify the tested-grid boundary pattern mechanically.

### L1 — unique tested-grid PC32 sufficiency

If:

- P1 passes on both datasets;
- P2 is `Delta32 >= 0.25` on both datasets; and
- `S_common == {32}`

then:

`[PC32-LOCALIZED SUFFICIENCY LEAD — ON TESTED GRID]`

This means only the 32/64 boundary is jointly sufficient among the five preregistered boundaries. It does **not** mean 32 is globally optimal or uniquely causal between untested coordinates.

### L2 — broader shared plateau containing 32

If the two gates pass on both datasets, `32 in S_common`, and `1 < |S_common| < 5`, then:

`[BROAD CONTIGUOUS SUFFICIENCY PLATEAU — NO UNIQUE PC32]`

The exact members of `S_common` must be printed. No post-hoc knee may be declared.

### L3 — all tested contiguous boundaries sufficient

If the two gates pass and:

`S_common == {16,24,32,48,64}`

then:

`[NO BOUNDARY LOCALIZATION — ALL TESTED CONTIGUOUS SPLITS SUFFICIENT]`

This weakens any claim that the spectral mechanism is localized near PC32.

### L4 — shared boundary exists but does not include 32

If the position gate passes on both datasets, `S_common` is nonempty, and `32 not in S_common`, then:

`[BOUNDARY SHIFT — PC32 NOT REPLICATED AS SHARED SUFFICIENT SPLIT]`

The exact shared set must be reported without selecting one member post hoc.

### L5 — no shared sufficient boundary

If:

`S_common` is empty

then:

`[NO SHARED SUFFICIENT BOUNDARY — DATASET HETEROGENEITY]`

### Heterogeneity flag

Regardless of L1-L5, if:

`S_LoCoMo != S_LongMemEval`

then append:

`[BOUNDARY-SET HETEROGENEITY PRESENT]`

The two frozen datasets must not be silently collapsed into one boundary profile.

## 12. No-knee rule

There is no authorized visual or post-hoc `knee`, elbow, changepoint, spline optimum, interpolated optimum, or local search in this experiment.

If multiple preregistered boundaries satisfy the same sufficiency criterion, the result is a plateau on this grid. If no sharp pattern appears, the report must say that no sharp pattern appeared.

Any finer localization requires a later, separately preregistered experiment.

## 13. Mandatory integrity controls

Before interpreting either dataset:

1. exact frozen dataset/source/adaptor identities match §3;
2. frozen cohort identity and denominator match exactly (`1535`, `470/470 unique`);
3. Native R@3 reproduces within `1e-12` and its exact error is reported;
4. every intervention matrix satisfies orthogonality to `1e-12`;
5. common archive/query transforms preserve continuous norms and dot products to `1e-12`;
6. signed-permutation Hamming invariance passes exactly;
7. zero-threshold sign semantics remain `>= 0`;
8. top-k remains 3;
9. fractional evidence semantics and all nuisance/tie seeds are unchanged;
10. random partitions satisfy exact cardinality/disjointness/exhaustiveness/range checks;
11. the same numeric `Q32/Q64` pair is verified between each spectral-32 and matched-random-32 paired arm;
12. no outcome metadata enters representation fitting;
13. no boundary, seed, partition, threshold, distance metric, or cohort is altered after outcome access.

Any load-bearing control failure yields:

`[INVALID / LOCALIZATION VERDICT WITHHELD]`

for that dataset.

## 14. Per-question persistence — new auditability requirement

Unlike the prior Head/Tail package, this experiment must persist enough per-question output to independently reconstruct every primary aggregate without rerunning the representation pipeline.

At minimum, for every valid question, seed, and primary arm persist:

- dataset name;
- stable question id;
- boundary or random-null arm name;
- rotation seed;
- partition seed when applicable;
- fractional R@3 contribution;
- Native fractional R@3 contribution;
- frozen tie/nuisance identity needed to verify the aggregation path.

The package must also persist the exact random partitions.

The aggregator must verify expected row counts, question uniqueness at the appropriate level, complete seed/arm coverage, and absence of duplicate primary records.

Raw/per-question outputs may be compressed for artifact storage but must be hash-bound in the final provenance manifest.

## 15. Execution and sharding

LoCoMo may run monolithically or deterministically sharded, provided per-question semantics are unchanged.

LongMemEval may use deterministic sharding for resource efficiency. The scientific claim is only that sharding is semantics-invariant under the frozen per-question construction; no generic claim of bitwise equality under arbitrary floating-point aggregation order is permitted.

Final aggregation should use a deterministic globally sorted `(question_id, seed, arm)` order before computing means to reduce unnecessary order dependence.

The exact Python and numerical-stack versions used by CI must be recorded in the result package.

## 16. Pre-run sealing requirement

No localization outcome may be accessed until all of the following are committed:

- this exact preregistration;
- LoCoMo localization runner;
- LongMemEval localization runner/shard wrapper;
- both workflow definitions;
- the post-audit interpretation addendum.

A pre-run seal must bind the Git blob identities of all five artifact classes above before any trigger commit exists.

The preregistration and pre-run seal must be copied to Google Drive before outcome-triggering execution.

Both workflows must independently verify the preregistration and frozen runner/workflow/source identities before computation.

## 17. Stop / no-rescue rule

Once the pre-run seal exists and any localization outcome is accessed:

Do not add or replace:

- boundaries;
- seeds;
- random partitions;
- decision thresholds;
- top-k values;
- distance metrics;
- thresholds;
- cohort filters;
- representation features;
- post-hoc weighting;
- extra reranking;
- alternate nuisance/tie schemes;
- knee-finding procedures.

If an execution-only bug occurs before scientific output is produced, a corrected runner requires a new pre-run seal and a transparent incident note. If any scientific output was already exposed, the original preregistered results remain reportable and may not be silently replaced.

## 18. Interpretation ceiling

A positive result can establish only a fixed-grid, fixed-dataset causal lead about which **tested contiguous archive-local SVD boundary constraints** preserve the observed Native SIGN96-vs-Full-Haar advantage under this shared pipeline.

It cannot establish:

- a universal binary-retrieval theorem;
- a globally optimal or mathematically unique PC boundary;
- transfer to arbitrary encoders, corpora, bit widths, or retrieval metrics;
- production superiority;
- correspondence to neural-network neuron axes;
- any Task 4F1 outcome or execution decision.

## 19. Required final reporting

The final checkpoint must include, whether favorable or unfavorable:

- P1/P2 status for each dataset;
- `S_LoCoMo`, `S_LongMemEval`, and `S_common`;
- mechanical L1-L5 verdict and heterogeneity flag;
- all five boundary means with conditional SEs and seed ranges;
- all ten per-seed results for every boundary;
- matched random-null results and exact partitions;
- any sign-inverting seeds;
- Native and Full-Haar anchors;
- all integrity-control maxima/errors;
- per-question artifact hashes;
- exact runner/workflow/prereg/seal/provenance identities;
- a plain statement that the two datasets share one pipeline and are not independent methodological replications;
- every negative or non-localizing result.

No favorable-result-only summary is permitted.
