# V52 Causal Head-vs-Tail Two-Subspace Haar Test — Preregistration

**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

Date: 2026-09-04
Status: `[PREREGISTERED — NO TWO-SUBSPACE OUTCOME ACCESS YET]`
Branch: `research/v52-sign-mechanism-locomo-2026-09-04`

## 1. Why this is a new experiment

The preceding preregistered spectral-band intervention produced the same benchmark-level regime on both frozen benchmarks:

- LoCoMo: `rho = 0.06523571501071657` -> `[SPECTRAL-SUBSPACE PRESERVATION LEAD]`.
- LongMemEval: `rho = 0.14282724238436822` -> `[SPECTRAL-SUBSPACE PRESERVATION LEAD]`.

Those outcomes were observed before this preregistration and generated the present hypothesis. Therefore this document does **not** retroactively treat the head-vs-tail hypothesis as preregistered in the previous experiment.

The previous secondary `HAAR_MID_LOW64` arm also suggested that mixing Mid32 and Low32 while leaving High32 fixed is comparatively mild on both benchmarks. That observation is hypothesis-generating only.

## 2. Scientific question

Is the three-way High32 / Mid32 / Low32 separation itself required, or is a simpler two-subspace decomposition sufficient?

> Does preserving only the boundary between the leading 32-dimensional spectral subspace and the remaining 64-dimensional tail preserve most of the native SIGN96 advantage over unrestricted Full-Haar mixing?

This experiment tests **Head32 vs Tail64 separation**, not individual-axis preservation.

## 3. Frozen sources

Use exactly the same accepted/frozen benchmark cohorts, representation recipes, centering, sign threshold, top-k, evidence semantics, and independent tie-priority/nuisance schemes already used by the preceding causal spectral-band experiment.

LongMemEval identity:
- dataset SHA-256: `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`
- dataset bytes: `277383467`
- adapter v1 SHA-256: `0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722`
- adapter v2 SHA-256: `643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218`
- accepted primary cohort: `470`
- frozen native R@3: `0.5419751773049646`
- frozen Full-Haar96 mean R@3: `0.38271666666667`

LoCoMo identity:
- dataset SHA-256: `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4`
- audit-layer manifest SHA-256: `90a4e94c9247d8ace7aaf62acdda7315744b111d84e42658cccfeb0a3c89df06`
- accepted evidence-valid denominator: `1535`
- frozen native R@3: `0.23654714666441054`
- frozen Full-Haar96 mean R@3: `0.13770827054136`

Do not touch Task 4F1 execution candidates, seals, authorization state, or outcomes.

## 4. Frozen two-subspace partition

The 96 archive-local SVD coordinates retain their existing order.

- `Head32 = indices 0..31`
- `Tail64 = indices 32..95`

No variance resorting, boundary search, outcome-dependent coordinate selection, or alternate split may be introduced in the primary experiment.

## 5. Primary intervention

### `HEAD32_TAIL64_HAAR`

For each new seed construct

`R_2 = diag(Q_head32, Q_tail64)`

where:
- `Q_head32` is a 32x32 Haar-orthogonal matrix;
- `Q_tail64` is an independent 64x64 Haar-orthogonal matrix;
- both are generated sequentially from one frozen RNG seed using IID standard-normal matrices, QR, and deterministic diagonal-sign correction;
- the same `R_2` is applied to the archive and query after the frozen centering step and before zero-threshold sign quantization.

No Head coordinate may mix with a Tail coordinate.

## 6. Frozen new seeds

Use exactly:

`56001, 56002, 56003, 56004, 56005`

For each seed, generate the Head32 Gaussian matrix first and the Tail64 Gaussian matrix second from one RNG stream.

No replacement/additional seeds after outcome access.

## 7. Controls

Mandatory before interpretation on each benchmark:

1. source hashes and cohort identity match frozen values;
2. native R@3 reproduces to the accepted `1e-12` tolerance;
3. each `R_2` is orthogonal to `1e-12`;
4. common archive/query transform preserves continuous norms and dot products to `1e-12`;
5. signed-permutation Hamming invariance control passes exactly;
6. frozen tie-priority/nuisance scheme is unchanged.

Any failure -> `[INVALID / CAUSAL VERDICT WITHHELD]`.

## 8. Primary estimand

For each benchmark independently:

- `L_full = R_native - R_fullhaar_frozen`
- `L_2 = R_native - mean_seed(R_HEAD32_TAIL64_HAAR)`
- `rho_2 = L_2 / L_full`

Frozen interpretation bands:

- `rho_2 <= 0.25` -> `[HEAD-TAIL TWO-SUBSPACE SUFFICIENCY LEAD]`
  - preserving only Head32 vs Tail64 separation retains at least 75% of the native-vs-full-Haar advantage;
  - the Mid32/Low32 boundary is not a main requirement under this intervention.

- `rho_2 >= 0.75` -> `[THREE-BAND OR FINER STRUCTURE REQUIRED LEAD]`
  - collapsing Mid32 and Low32 into a single rotatable Tail64 loses at least 75% as much as unrestricted Full-Haar mixing.

- `0.25 < rho_2 < 0.75` -> `[MIXED TWO-SUBSPACE / FINER-STRUCTURE REGIME]`.

These are fixed-benchmark engineering/causal bands, not population hypothesis tests.

## 9. Cross-benchmark rule

- Same primary two-subspace regime on LongMemEval and LoCoMo -> `[CROSS-BENCHMARK HEAD-TAIL CAUSAL LEAD]`, with the shared regime stated explicitly.
- Different regimes -> `[HETEROGENEOUS HEAD-TAIL MECHANISM — UNIVERSAL CLAIM REJECTED]`.

## 10. Secondary diagnostics

Pre-specified, non-decision-changing diagnostics:

- per-seed Fractional R@3;
- native-minus-intervention loss in percentage points;
- Head32-only and Tail64-only R@3 after the common intervention;
- High32 wrong/tie -> full96 rescue;
- Head32-correct -> full96 degradation;
- pairwise gold-vs-nongold discrimination for Head32, Tail64, and Full96;
- comparison to the already observed previous experiment's `WITHIN_SPECTRAL_BAND_HAAR` and `HAAR_MID_LOW64` means as frozen descriptive references only.

## 11. No-rescue / no-tuning rule

Do not add after outcome access:

- alternate Head/Tail boundary sizes;
- learned boundary location;
- variance-based resorting;
- whitening or variance reweighting;
- learned thresholds;
- supervised rotations;
- alternate top-k or distance metrics;
- extra/replacement random seeds;
- reranking or shortlist methods.

A boundary-location experiment, if warranted later, must be a separate preregistration.

## 12. Interpretation ceiling

A positive result would support only the claim that a two-subspace Head32-vs-Tail64 separation is sufficient to preserve most of the native SIGN96-vs-Full-Haar advantage on these frozen benchmarks.

It would not establish a universal binary-retrieval theorem, production superiority, or correspondence between archive-local SVD coordinates and neural-network neuron axes.
