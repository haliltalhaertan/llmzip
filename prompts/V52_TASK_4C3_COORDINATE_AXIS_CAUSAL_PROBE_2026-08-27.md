# V52 TASK 4C3 — COORDINATE-AXIS / ORTHOGONAL-ROTATION CAUSAL PROBE

## ROLE
You are the Mathematical Compute Expert. Execute this task exactly as preregistered. This is a mechanism-falsification experiment, not an optimization sweep.

## MANDATORY FIRST STEP — CHAIN OF CUSTODY
Before interpreting or computing any result, run `python3 tools/verify_frozen_artifacts.py --list` from the canonical `main` branch of:

`https://github.com/haliltalhaertan/llmzip`

Treat any mismatch as blocking until the canonical byte source is independently checked. Do not reformat, regenerate, or overwrite frozen artifacts.

## FROZEN PARENT STATE
Task 4C2 is accepted as:

- `[AUDITED — TASK 4C2 PASS WITH CONDITIONS]`
- `[FROZEN — TASK 4C2 NUMERICAL CHECKPOINT]`
- `[CLOSED — TASK 4C1 CENTERING CONDITION]`
- `[CLOSED — TASK 4C1 ADAPTER / ITQ ORIENTATION CONDITION]`
- `[REAL FIXED-BENCHMARK PHENOMENON — SIGN96]`
- `[OPEN — CAUSAL MECHANISM]`
- `[TASK 4C3 — CLEARED TO RUN]`

Frozen LongMemEval primary cohort: 470 non-`_abs` questions. No population-level CI or p-value is allowed because all 470 primary questions lie in one shared-session connected component.

Canonical dataset SHA256:
`d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`

Adapter v1 SHA256:
`0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722`

Adapter v2 SHA256:
`643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218`

## SCIENTIFIC QUESTION
Task 4C2 established that centered SIGN96 beats centered FLOAT96 by +10.037943 pp and centered ITQ96 by +16.583404 pp on the frozen benchmark. The ITQ rotation is correct, the centered input is identical, and centering does not explain the phenomenon.

Task 4C3 asks one narrower causal question:

> Does binary retrieval quality depend materially on preserving the native coordinate axes, such that orthogonal mixing degrades sign/Hamming retrieval even though the underlying continuous geometry is exactly unchanged?

This task does **not** attempt to prove a full theoretical mechanism. It tests the coordinate-axis / rotation component by an intervention that preserves all continuous pairwise dot products and norms.

## NO-TUNING RULE
Do not add methods, widths, thresholds, metrics, seeds, rotations, whitening, rerankers, block weights, learned transforms, alternate normalizations, or LoCoMo after results are visible. Any follow-up belongs to a new task.

## FROZEN REPRESENTATION
For every question, construct the exact same 96D archive/query representation used by Task 4C2.

Let:
- `Y96` = frozen normalized archive 96D representation before centering
- `QY96` = frozen query representation
- `mu96 = mean(Y96, axis=0)` using archive documents only
- `C96 = Y96 - mu96`
- `qC96 = QY96 - mu96`

No query, answer, gold label, question type, evidence annotation, or answer-session identifier may enter any archive fit or rotation construction.

## METHODS — EXACTLY THESE

### A. NATIVE_SIGN96
`D = (C96 >= 0)`
`Q = (qC96 >= 0)`
Global Hamming ranking with the same frozen independent tie-priority semantics as Task 4C2.

This must reproduce frozen Task 4C2 SIGN96 to rounding.

### B. SIGNED_PERM_CONTROL96 — POSITIVE CONTROL
For each rotation seed, generate a 96D signed permutation matrix `P` using only that frozen seed and no data.

Apply:
`C' = C96 @ P`
`qC' = qC96 @ P`
then sign-threshold at zero and rank by Hamming.

Because a common coordinate permutation and common sign flip preserve Hamming distance exactly, this control MUST produce identical Hamming distances, rankings, top-3 sets, and retrieval metrics to NATIVE_SIGN96 under the same tie priority.

Any mismatch is:
`[BUG — HAMMING-INVARIANT CONTROL FAILED]`

### C. BLOCK_ORTHO_SIGN96
Use block sizes exactly:
`b ∈ {2, 4, 8, 16, 32, 96}`

Rotation seeds exactly:
`{43001, 43002, 43003, 43004, 43005}`

For each seed:
1. Generate one data-independent random permutation of the 96 coordinates.
2. Partition the permuted coordinates into contiguous blocks of size `b` (all listed b divide 96).
3. For each block, generate a Haar-random orthogonal matrix from an IID standard-normal matrix using QR decomposition with deterministic sign correction on `diag(R)` so the construction is reproducible.
4. Assemble the block-diagonal orthogonal transform `R_b` in the permuted basis.
5. Apply the same transform to archive and query:
   `C_b = C96 @ R_b`
   `qC_b = qC96 @ R_b`
6. Threshold at zero and rank globally by Hamming.

The rotation is strictly data-independent and label-independent.

Interpretation of b:
- small b = local coordinate mixing
- b=96 = full orthogonal mixing of all coordinates

### D. ITQ96_CENTERED — FROZEN REFERENCE ONLY
Reproduce the exact frozen Task 4C2 ITQ96 method using the audited adapter implementation and seeds `{101,202,303,404,505}`.

Do not alter ITQ or use it to tune the random-rotation family. ITQ is a reference for whether learned rotation lies inside or outside the data-independent rotation envelope.

### E. FLOAT96_CENTERED — INVARIANCE REFERENCE ONLY
Do not create a new performance branch. Use centered cosine ranking only to verify that orthogonal rotation leaves continuous scores/rankings invariant to numerical tolerance.

## HARD ORTHOGONAL-INVARIANCE GATES
For every question, block size and rotation seed:

1. Verify `R_b.T @ R_b ≈ I`; record maximum absolute orthogonality error.
2. Verify archive and query norms are preserved.
3. Verify all query-document centered dot products/cosines are unchanged relative to unrotated centered FLOAT96.
4. Required maximum absolute score difference: `<= 1e-12` in float64.
5. Verify centered FLOAT top-3 ranking is unchanged under rotation when there is no exact-score tie ambiguity; where exact ties exist, compare score vectors and tie sets rather than arbitrary ordering.

Any failure above is:
`[BUG — CONTINUOUS GEOMETRY NOT PRESERVED]`

The central causal logic of this task is invalid unless this gate passes.

## NUISANCE / TIE PRIORITY
Use the same 20 frozen nuisance/tie-priority trials as Task 4C2. Priority must be independent of corpus order, gold labels, answer sessions, question type, and evidence annotations.

Seeds and nuisance trials are NOT independent statistical units. Collapse within each question first.

## PRIMARY QUALITY METRIC
Fractional Evidence Recall@3.

Secondary:
- ANY Evidence Recall@3
- ALL Evidence Recall@3

Report exact fixed-benchmark means only. No population CI, p-value, superiority test, equivalence test, or non-inferiority claim.

## PRIMARY CAUSAL DECISION VARIABLE
Let:

`S_native` = NATIVE_SIGN96 fractional R@3.

`S_haar96` = question-weighted mean fractional R@3 of full-block `b=96` across the five frozen rotation seeds after proper within-question collapse.

Define:
`D96 = S_haar96 - S_native` in percentage points.

Decision bands:

- if `D96 <= -5.0 pp` AND all 5 full-Haar seeds are below native:
  `[STRONG AXIS-STRUCTURE EFFECT — FULL ORTHOGONAL MIXING HURTS SIGN RETRIEVAL]`

- if `-5.0 < D96 < -1.0 pp`:
  `[PARTIAL AXIS-STRUCTURE EFFECT]`

- if `|D96| <= 1.0 pp`:
  `[NO MATERIAL FULL-ROTATION EFFECT]`

- if `D96 > +1.0 pp`:
  `[FALSIFIED IN THIS DIRECTION — FULL ROTATION IMPROVES SIGN RETRIEVAL]`

These are engineering/fixed-benchmark interpretation bands, not inferential thresholds.

## BLOCK-MIXING GRADIENT — DIAGNOSTIC, NOT A SECOND DECISION RULE
For each `b ∈ {2,4,8,16,32,96}`, report:
- fractional R@3
- gap vs native SIGN
- all five seed-specific gaps
- W/T/L vs native at the question level
- rank Spearman vs native SIGN
- top-3 overlap vs native SIGN

Report whether degradation tends to increase as the block size grows, but do not convert this into a post-hoc significance claim.

## COORDINATE-HETEROGENEITY DIAGNOSTICS
Computed from `C96` archive vectors only, before seeing retrieval outcomes for this task:

For each question, compute native-coordinate:
- per-coordinate variance vector
- variance coefficient of variation `std(var)/mean(var)`
- normalized variance entropy
- variance participation ratio / effective-coordinate count
- max/median variance ratio
- covariance off-diagonal Frobenius-energy ratio
- mean absolute coordinate correlation, excluding diagonal
- sign-bit occupancy mean/min/max
- mean absolute deviation of occupancy from 0.5

For every rotation family/block size, recompute the coordinate-basis diagnostics after rotation.

Do not whiten or rescale coordinates.

## PRE-REGISTERED HETEROGENEITY ALIGNMENT CHECK
Before computing retrieval gaps, partition the 470 questions into quintiles using **native variance-CV only**. Freeze quintile membership before joining retrieval outcomes.

For each quintile report native-minus-full-Haar96 fractional R@3 loss, question-weighted and seed-specific.

Descriptive label:
- if the highest-heterogeneity quintile has a larger loss than the lowest-heterogeneity quintile in all 5 full-Haar seeds:
  `[HETEROGENEITY-ALIGNMENT LEAD]`
- otherwise:
  `[HETEROGENEITY-ALIGNMENT NOT CONSISTENT]`

This is a mechanism diagnostic, not population inference.

## ITQ VS DATA-INDEPENDENT ROTATION ENVELOPE
Compare frozen ITQ96 fractional R@3 with the five full-Haar96 seed results.

Report exactly one:
- `[ITQ BELOW FULL-HAAR ENVELOPE]`
- `[ITQ WITHIN FULL-HAAR ENVELOPE]`
- `[ITQ ABOVE FULL-HAAR ENVELOPE]`

Also report ITQ native-rank Spearman relative to the five Haar values. This is descriptive and does not establish why ITQ differs.

## COLLISION / TIE DIAGNOSTICS
For NATIVE_SIGN96, every block size, full-Haar seeds, and ITQ96 report:
- unique-code fraction
- duplicate-code fraction
- largest collision bucket
- candidates at minimum Hamming distance
- top-3 boundary tie rate
- query exact-code match rate

These remain downstream diagnostics. Do not label collision or tie statistics as causal unless a later intervention isolates them.

## 4C2 CONCENTRATION CAVEAT — MUST BE CARRIED FORWARD
The frozen 4C2 audit found SIGN vs centered FLOAT to be concentrated:
- W/T/L = 122 / 304 / 44
- median paired gap = 0.0 pp
- 64.7% exact ties
- after removing the 50 largest positive contributors, the +10.04 pp lead falls to about +1.28 pp

Do not describe SIGN-vs-FLOAT as uniformly distributed.

The SIGN-vs-ITQ contrast is a different, broader phenomenon and must not be conflated with the concentrated SIGN-vs-FLOAT profile.

## STRATA
Carry the same frozen Task 4C2 strata only:
- 6 question types
- one-gold / multi-gold
- archive-size quartiles
- session-reuse tertiles

No new outcome-defined strata.

The variance-CV quintiles above are allowed because membership is frozen before retrieval outcomes are joined.

## NO RESCUE / NO EXPANSION
Do not run:
- LoCoMo
- alternate bit widths
- alternate thresholds
- learned thresholds
- whitening
- PCA rotations
- variance reweighting
- supervised rotation
- reranking
- shortlist methods
- alternate distance metrics
- alternate block-size sets
- extra random seeds
- post-result parameter tuning

## PRE-RUN SEAL
Before any retrieval-quality result is computed, create an immutable `V52_T4C3_PRE_RUN_SEAL.json` containing at minimum:
- task name/version
- canonical Git commit SHA
- dataset SHA
- adapter v1/v2 SHA
- Task 4C2 parent checkpoint reference
- full method list
- block sizes
- all rotation seeds
- all nuisance seeds/trials
- metric definitions
- decision bands
- heterogeneity metrics
- heterogeneity-quintile rule
- exact script SHA256
- explicit no-rescue list

After sealing, the compute script must not change. Post-run manifest must show pre/final script SHA equality.

## REQUIRED OUTPUTS
At minimum:

- `V52_T4C3_PRE_RUN_SEAL.json`
- `v52_t4c3_coordinate_axis_probe.py`
- `V52_T4C3_INPUT_CHECKS.json`
- `V52_T4C3_trial_results.csv`
- `V52_T4C3_question_level.csv`
- `V52_T4C3_aggregate.csv`
- `V52_T4C3_rotation_seed_results.csv`
- `V52_T4C3_block_gradient.csv`
- `V52_T4C3_continuous_invariance.csv`
- `V52_T4C3_signed_permutation_control.csv`
- `V52_T4C3_native_heterogeneity.csv`
- `V52_T4C3_rotated_heterogeneity.csv`
- `V52_T4C3_heterogeneity_quintiles.csv`
- `V52_T4C3_heterogeneity_alignment.csv`
- `V52_T4C3_rank_geometry.csv`
- `V52_T4C3_collision_diagnostics.csv`
- `V52_T4C3_tie_diagnostics.csv`
- `V52_T4C3_ITQ_HAAR_ENVELOPE.csv`
- frozen-strata CSVs
- `V52_T4C3_sanity_checks.csv`
- `V52_T4C3_leakage_audit.csv`
- `V52_T4C3_POST_RUN_MANIFEST.json`
- `V52_T4C3_COMPUTE_REPORT.md`
- `V52_T4C3_HEAD_RESEARCHER_HANDOFF.txt`
- `V52_T4C3_ALL_OUTPUTS.zip`

## FINAL REPORT MUST ANSWER
1. Did signed-permutation invariance pass exactly?
2. Did continuous orthogonal invariance pass at `<=1e-12`?
3. What is `D96 = S_haar96 - S_native`?
4. Which preregistered axis-structure verdict band applies?
5. Is there a block-size mixing gradient?
6. Does native variance heterogeneity flatten under rotation?
7. Does the preregistered heterogeneity-quintile alignment hold across all five full-Haar seeds?
8. Is ITQ below/within/above the full-Haar envelope?
9. How do rank reordering, collisions and ties move under controlled rotation?
10. Does this task support only an axis-structure effect, or a stronger coordinate-heterogeneity mechanism?

## INTERPRETATION DISCIPLINE
Even a strong positive result licenses only:

> Orthogonal coordinate mixing, while preserving the continuous centered geometry, materially changes sign/Hamming neighborhoods and retrieval quality on this frozen benchmark.

Do **not** automatically conclude:
- ITQ destroys useful semantic coordinates,
- coordinate heterogeneity is the unique cause,
- collision reduction causes recall gains,
- the result generalizes to other benchmarks,
- SIGN is universally better than learned binary rotation.

Any stronger causal statement requires a later explicitly targeted intervention and, if load-bearing, independent adversarial audit.

## STOP RULE
After Task 4C3 completes, stop. Do not launch LoCoMo or any rescue experiment. Return all artifacts to the Head Researcher for interpretation and audit decision.