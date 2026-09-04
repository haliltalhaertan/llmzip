# V52 Matched-Size Random-Partition Null Control — Preregistration

Date: 2026-09-04
Status: `[PREREGISTERED — NO RANDOM-PARTITION OUTCOME ACCESS YET]`
Branch: `research/v52-sign-mechanism-locomo-2026-09-04`

## 1. Why this experiment exists

The preceding preregistered Head32-vs-Tail64 experiment produced the same fixed-benchmark regime on both frozen benchmarks:

- LoCoMo: `rho_2 = 0.10744461886682183` -> `[HEAD-TAIL TWO-SUBSPACE SUFFICIENCY LEAD]`.
- LongMemEval: `rho_2 = 0.15669024668844653` -> `[HEAD-TAIL TWO-SUBSPACE SUFFICIENCY LEAD]`.

Those outcomes were observed before this preregistration. They motivate, but do not answer, the present question.

Independent co-chair reviews identified the key unresolved confound: the prior experiment compared a spectral Head32/Tail64 partition with unrestricted Full-Haar mixing, but did not compare it with an equally sized non-spectral 32/64 block partition. Therefore the prior result establishes a two-subspace sufficiency lead, but does not yet establish that *spectral position* is what makes the partition special.

This experiment is designed as a falsification/null control before any boundary-localization scan.

## 2. Scientific question

Does the observed Head32/Tail64 preservation effect depend on selecting the leading 32 archive-local SVD coordinates as one block, or would an arbitrary 32-coordinate block and its 64-coordinate complement preserve the native SIGN96 advantage equally well?

The two candidate explanations are:

1. **Spectral-position explanation:** keeping the leading 32-dimensional spectral subspace separate from the remaining tail is materially better than a matched-size random 32/64 partition.
2. **Generic block-structure explanation:** most of the benefit comes from imposing any 32/64 block-diagonal orthogonal structure, regardless of spectral coordinate position.

The experiment is intentionally capable of falsifying the stronger spectral-position interpretation.

## 3. Frozen benchmark identities and inherited references

All representation, centering, sign-threshold, top-k, evidence, tie-priority, nuisance-trial, and source semantics remain exactly those used by the accepted preceding causal stages.

### LongMemEval

- dataset SHA-256: `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`
- dataset bytes: `277383467`
- adapter v1 SHA-256: `0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722`
- adapter v2 SHA-256: `643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218`
- accepted primary cohort: `470`
- frozen native R@3: `0.5419751773049646`
- inherited frozen Full-Haar96 reference R@3: `0.38271666666667`
- prior Head32/Tail64 result, descriptive only: `0.5170209219858156`

### LoCoMo

- dataset SHA-256: `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4`
- audit-layer manifest SHA-256: `90a4e94c9247d8ace7aaf62acdda7315744b111d84e42658cccfeb0a3c89df06`
- accepted evidence-valid denominator: `1535`
- frozen native R@3: `0.23654714666441054`
- inherited frozen Full-Haar96 reference R@3: `0.13770827054136`
- prior Head32/Tail64 result, descriptive only: `0.22592744129014436`

The inherited Full-Haar constants are intentionally reused exactly as frozen in the prior causal preregistrations; they are not re-estimated after outcome access.

Task 4F1 execution candidates, seals, authorization state, and outcomes are out of scope and must not be touched.

## 4. Frozen paired seed panel

Use exactly ten seeds:

`57001, 57002, 57003, 57004, 57005, 57006, 57007, 57008, 57009, 57010`

No seed may be replaced or added after any outcome access.

Each seed defines one paired comparison between a spectral 32/64 partition and a random 32/64 partition. The same two Haar matrices are used in both arms for that seed so that the coordinate partition, rather than rotation randomness, is the principal experimental difference.

## 5. Frozen random partition construction

For each seed `s`:

1. Initialize `partition_rng = numpy.random.default_rng(s)`.
2. Compute `perm = partition_rng.permutation(96)`.
3. Define `S_s = sort(perm[:32])`.
4. Define `T_s = sort(perm[32:])`.
5. Require exactly 32 unique coordinates in `S_s`, 64 unique coordinates in `T_s`, empty intersection, and union exactly `{0,...,95}`.
6. Log `S_s` and `T_s` in the result package before aggregate interpretation.

No redraw is permitted for any reason other than a deterministic implementation failure that prevents the frozen permutation algorithm from executing. An apparently unusual or contiguous draw must still be retained.

## 6. Frozen paired Haar construction

For each seed `s`:

1. Initialize `rotation_rng = numpy.random.default_rng(1_000_000 + s)`.
2. Draw a 32x32 IID standard-normal matrix, perform QR, and apply deterministic diagonal-sign correction to obtain `Q32_s`.
3. Continue the same RNG stream, draw a 64x64 IID standard-normal matrix, perform QR, and apply the same sign correction to obtain `Q64_s`.

The same numeric `Q32_s` and `Q64_s` matrices must be used in both primary arms below.

## 7. Primary paired interventions

### Arm A — `SPECTRAL_HEAD32_TAIL64_HAAR_NEW`

Construct a 96x96 orthogonal matrix with:

- `Q32_s` on coordinates `0..31`;
- `Q64_s` on coordinates `32..95`;
- no cross-block mixing.

This is a new-seed replication of the prior spectral Head32/Tail64 intervention.

### Arm B — `RANDOM32_COMPLEMENT64_HAAR`

Construct a 96x96 orthogonal matrix with:

- `Q32_s` embedded on the sorted coordinate set `S_s`;
- `Q64_s` embedded on the sorted complement `T_s`;
- no mixing between `S_s` and `T_s`.

Within each block, matrix row/column order follows the ascending order of the corresponding coordinate set. This convention is frozen and must not be changed after outcomes are observed.

For both arms, apply the same common archive/query transform after the frozen centering step and before zero-threshold sign quantization.

## 8. Primary estimands

For each benchmark independently define:

`L_full = R_native - R_fullhaar_frozen`

`R_spec = mean_seed(R@3 under SPECTRAL_HEAD32_TAIL64_HAAR_NEW)`

`R_rand = mean_seed(R@3 under RANDOM32_COMPLEMENT64_HAAR)`

`rho_spec = (R_native - R_spec) / L_full`

`rho_rand = (R_native - R_rand) / L_full`

Primary contrast:

`Delta = rho_rand - rho_spec`

Interpretation: larger positive `Delta` means the random 32/64 partition loses materially more of the native-vs-Full-Haar advantage than the matched spectral 32/64 partition.

## 9. Frozen decision rule

The prior spectral Head/Tail lead must first replicate on the new seed panel.

### Replication gate

If `rho_spec > 0.25` on a benchmark:

`[HEAD-TAIL REPLICATION FAILURE — SPECTRAL POSITION CLAIM NOT ADVANCED]`

The benchmark receives no stronger spectral-position verdict regardless of `Delta`.

If `rho_spec <= 0.25`, classify the matched random-partition contrast as:

- `Delta <= 0.05` -> `[GENERIC BLOCK-STRUCTURE SUFFICIENCY LEAD — SPECTRAL POSITION CLAIM FALSIFIED]`
- `Delta >= 0.25` -> `[SPECTRAL POSITION LOAD-BEARING LEAD]`
- `0.05 < Delta < 0.25` -> `[MIXED / PARTIAL SPECTRAL POSITION CONTRIBUTION]`

These thresholds are fixed engineering/causal decision bands for these benchmarks, not population-level hypothesis-test significance thresholds.

## 10. Cross-benchmark rule

After both benchmark-level verdicts are determined:

- Both benchmarks pass the replication gate and both give `[SPECTRAL POSITION LOAD-BEARING LEAD]` -> `[CROSS-BENCHMARK SPECTRAL POSITION CAUSAL LEAD]`.
- Both benchmarks pass the replication gate and both give `[GENERIC BLOCK-STRUCTURE SUFFICIENCY LEAD — SPECTRAL POSITION CLAIM FALSIFIED]` -> `[CROSS-BENCHMARK GENERIC BLOCK-STRUCTURE LEAD — SPECTRAL POSITION FALSIFIED]`.
- Any replication failure, mixed regime, or disagreement across benchmarks -> `[HETEROGENEOUS / MIXED NULL-CONTROL RESULT — UNIVERSAL SPECTRAL POSITION CLAIM WITHHELD]`.

No cross-benchmark verdict may be promoted beyond these exact rules.

## 11. Mandatory controls and stop rules

Before interpreting a benchmark, all of the following must pass:

1. frozen source hashes and cohort identity match the values above;
2. native R@3 reproduces within absolute tolerance `1e-12` of the frozen accepted value;
3. every random partition has cardinalities 32 and 64, is disjoint, exhaustive, and logged;
4. every `Q32_s`, `Q64_s`, spectral matrix, and random-partition matrix is orthogonal to max absolute error `<=1e-12`;
5. common archive/query transforms preserve continuous vector norms and query-archive dot products to max absolute error `<=1e-12`;
6. signed-permutation Hamming invariance control passes exactly;
7. tie-priority and nuisance semantics are unchanged from the preceding frozen benchmark pipeline;
8. the same per-question nuisance priorities are used for Arm A and Arm B;
9. LongMemEval sharding, if used, must preserve the global lexicographic question ordinal for tie seeds and must aggregate exactly 470/470 unique primary question IDs;
10. LoCoMo must retain exactly 1535 evidence-valid questions;
11. the pre-run provenance seal must bind the exact preregistration, runner, and workflow blobs before the trigger commit that starts outcome computation.

Any failure -> `[INVALID / NULL-CONTROL VERDICT WITHHELD]` for that benchmark. Do not relax a gate after seeing outcomes.

## 12. Required reporting

For each benchmark report at minimum:

- native R@3 and reproduction error;
- frozen Full-Haar reference;
- `R_spec`, `R_rand`, `rho_spec`, `rho_rand`, and `Delta`;
- all ten per-seed spectral and random R@3 values;
- all ten per-seed `rho_spec`, `rho_rand`, and paired `Delta` values;
- mean, standard deviation, minimum, and maximum across seeds for the primary paired quantities;
- the exact 32-coordinate random subset for every seed;
- all integrity-control maxima and PASS/FAIL states;
- artifact/environment/provenance identifiers sufficient for cold-start audit.

Seed dispersion must be reported explicitly. Decimal output may retain machine precision for reproducibility, but scientific interpretation must not imply that all printed digits represent physical precision.

## 13. Secondary diagnostics

Pre-specified and non-decision-changing:

- Head32-only, random32-only, corresponding 64-complement-only, and Full96 R@3 under the paired transforms;
- gold-vs-nongold pairwise discrimination for the same subsets;
- hard-negative rescue/degradation diagnostics;
- comparison with the already observed Stage-A three-band and prior Head32/Tail64 results as descriptive frozen references only.

No secondary diagnostic may override the primary `rho_spec` / `Delta` decision rule.

## 14. No-rescue / no-tuning rule

After any outcome access, do not add or change:

- coordinate split sizes;
- random subset generation rule;
- random seeds;
- number of seeds;
- transform RNG mapping;
- decision thresholds;
- top-k;
- distance metric;
- sign threshold;
- variance weighting, whitening, learned thresholds, learned rotations, reranking, or shortlist methods;
- alternative aggregation intended to rescue the claim.

Boundary localization (for example 16/80, 24/72, 32/64, 48/48, 64/32) is explicitly deferred. It requires a separate preregistration after this null-control result is closed.

## 15. Falsification meaning

If the matched random 32/64 partitions preserve performance essentially as well as the spectral Head32/Tail64 split (`Delta <= 0.05` under the frozen rule), the stronger claim that *spectral position* is load-bearing is considered falsified for that benchmark. The surviving explanation would be a more generic two-block structural effect.

A positive spectral-position result requires both new-seed replication of the Head32/Tail64 sufficiency (`rho_spec <= 0.25`) and a materially larger loss under the matched random partition (`Delta >= 0.25`).

## 16. Interpretation ceiling

A positive result would support only the fixed-benchmark causal claim that selecting the leading 32 archive-local SVD coordinates as a block is materially more protective than a matched-size arbitrary 32-coordinate block under these exact SIGN96 pipelines.

It would not establish:

- that coordinate 32 is the unique or optimal boundary;
- a universal binary-retrieval theorem;
- production superiority;
- population-level generalization;
- correspondence between archive-local SVD coordinates and neural-network neuron axes;
- transfer to Task 4F1 or any unauthorized outcome-bearing pipeline.
