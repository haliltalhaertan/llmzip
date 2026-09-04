# V52 Causal Spectral-Band Haar Test — Preregistration

Date: 2026-09-04
Status: `[PREREGISTERED — NO CAUSAL OUTCOME ACCESS YET]`
Branch: `research/v52-sign-mechanism-locomo-2026-09-04`

## 1. Scientific question

The post-hoc LongMemEval and LoCoMo diagnostics suggest a coarse-to-fine binary retrieval mechanism: early archive-local SVD directions are stronger on average but more redundant, while mid/tail directions provide complementary information that rescues hard negatives.

This experiment tests the unresolved causal distinction:

> Are the exact individual archive-local principal-axis orientations necessary, or is preservation of the three spectral subspaces (High32 / Mid32 / Low32) sufficient?

This preregistration is written after observing the exploratory mechanism diagnostics but before any outcome from the new within-band-Haar interventions.

## 2. Frozen source state

Use only the already frozen/audited benchmark semantics and representations for:

- LongMemEval Task 4C2/4C3 accepted cohort and representation recipe.
- LoCoMo Task 4D accepted audit-clean cohort and representation recipe.

LoCoMo source identity remains:

- dataset SHA-256 `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4`
- audit-layer manifest SHA-256 `90a4e94c9247d8ace7aaf62acdda7315744b111d84e42658cccfeb0a3c89df06`
- frozen Task-4D script SHA-256 `3f7f091fadc88dfcc1f68f38d6df10607d05d1e416d048fe776929a9a7b185a7`
- accepted audit-clean evidence-valid denominator `1535`.

Do not alter 4F1 execution candidates, seals, authorization state, or outcome files.

## 3. Frozen spectral partition

Coordinates are partitioned by the existing archive-local 96D SVD order:

- High32 = indices 0..31
- Mid32 = indices 32..63
- Low32 = indices 64..95

No outcome-dependent reordering, variance sorting, coordinate selection, or band-boundary change is allowed.

## 4. Interventions

For every archive, apply the same orthogonal transform to archive vectors and query vectors after the already frozen archive-only centering step and before zero-threshold sign quantization.

### A. NATIVE_SIGN96

Identity transform. Existing frozen native result is the reference.

### B. WITHIN_SPECTRAL_BAND_HAAR

Construct a block-diagonal 96x96 orthogonal matrix:

`R_band = diag(Q_high32, Q_mid32, Q_low32)`

where each Q is an independently generated 32x32 Haar-orthogonal matrix from IID standard-normal entries followed by QR and the same deterministic diagonal-sign correction convention used in Task 4C3/4D.

No coordinate from one spectral band may mix with another.

### C. FULL_HAAR96_REFERENCE

Use the existing accepted full-Haar intervention as the reference for total loss under unrestricted cross-band mixing. The primary normalized decision may use the already frozen accepted mean Full-Haar result; a rerun is only a reconstruction/control and may not change the frozen reference by seed selection.

### D. Secondary controlled cross-band interventions

If computationally practical, run these as secondary mechanistic diagnostics using the same frozen seeds:

- HAAR_HIGH_MID64: Haar-mix coordinates 0..63, leave Low32 unchanged.
- HAAR_HIGH_LOW64: Haar-mix High32+Low32 as a 64D block, leave Mid32 unchanged.
- HAAR_MID_LOW64: leave High32 unchanged, Haar-mix coordinates 32..95.

These secondary arms may refine interpretation but may not override the primary WITHIN_SPECTRAL_BAND_HAAR decision rule.

## 5. Frozen rotation seeds

New causal-intervention seeds, fixed before outcome access:

`55001, 55002, 55003, 55004, 55005`

For WITHIN_SPECTRAL_BAND_HAAR, each seed initializes one RNG and generates the High32, Mid32, and Low32 Gaussian matrices sequentially in that order.

For each secondary 64D intervention, the same seed initializes a fresh RNG for that intervention's 64x64 Gaussian matrix.

No additional/replacement seeds after outcome access.

## 6. Tie handling and nuisance trials

Reuse each benchmark's already frozen independent tie-priority/nuisance-trial scheme exactly. Do not add nuisance seeds, change top-k, or choose tie realizations after seeing results.

Top-k remains `k=3`.

Primary retrieval metric remains the benchmark's accepted Fractional Evidence Recall@3 semantics.

## 7. Primary causal estimand

For each benchmark independently define:

- `L_full = R_native - R_fullhaar_frozen`
- `L_band = R_native - mean_seed(R_within_band_haar)`
- `rho = L_band / L_full`

The known accepted full-Haar losses are used only as frozen denominators; they are not retuned.

Interpretation per benchmark:

- `rho <= 0.25`: `[SPECTRAL-SUBSPACE PRESERVATION LEAD]` — keeping High/Mid/Low separated preserves at least 75% of the native-vs-full-Haar advantage; exact individual axes are not the main requirement.
- `rho >= 0.75`: `[INDIVIDUAL-AXIS ORIENTATION LEAD]` — within-band mixing loses at least 75% as much as unrestricted full mixing; exact axes inside bands appear important.
- `0.25 < rho < 0.75`: `[MIXED / BOTH LEVELS MATTER]`.

If numerical reconstruction of the frozen native result fails its benchmark-specific accepted tolerance, stop and withhold the causal verdict.

## 8. Cross-benchmark decision

- Same primary regime on both LongMemEval and LoCoMo: `[CROSS-BENCHMARK CAUSAL MECHANISM LEAD]` with the shared regime stated explicitly.
- Different primary regimes: `[HETEROGENEOUS CAUSAL MECHANISM — UNIVERSAL CLAIM REJECTED]`.

This is still fixed-benchmark causal-intervention evidence, not population-level generalization.

## 9. Secondary diagnostics

Pre-specified secondary outputs:

- per-seed Fractional R@3;
- native-minus-intervention loss in percentage points;
- High/Mid/Low and 64-bit-combination R@3 under each intervention where defined;
- pairwise gold-vs-nongold discrimination;
- High32 wrong/tie hard-negative rescue and High32-correct degradation;
- positive hard-negative-margin question fraction;
- signed-permutation invariance sanity control;
- continuous orthogonal invariance sanity control.

Secondary diagnostics do not alter the primary rho decision bands.

## 10. Stop / falsification rules

Stop and classify the run invalid if any of the following occurs:

- source dataset/audit hash mismatch;
- archive/query receive different transforms;
- transform is not orthogonal to the accepted numerical tolerance;
- continuous geometry is not preserved under a common transform;
- frozen cohort/gold semantics change;
- native reference cannot be reproduced;
- new seeds, bands, thresholds, top-k, or metrics are introduced after outcome access.

## 11. Interpretation ceiling

Do not claim that archive-local SVD axes are LLM neuron axes. Do not claim universal superiority of sign hashing. Do not infer a production advantage. Do not call the exploratory coarse-to-fine mechanism proven merely because this experiment is preregistered.

The purpose of this experiment is narrowly causal: distinguish exact-axis dependence from spectral-subspace separation under the already observed native-vs-full-Haar effect.
