# V52 Cross-Benchmark Causal Spectral-Subspace Checkpoint

Date: 2026-09-04
Branch: `research/v52-sign-mechanism-locomo-2026-09-04`
Preregistration blob: `02aa91a12b4052bbb2f0a6617167c8851e4f71f7`

## Preregistered cross-benchmark verdict

**`[CROSS-BENCHMARK CAUSAL MECHANISM LEAD]`**

Shared benchmark-level regime:

**`[SPECTRAL-SUBSPACE PRESERVATION LEAD]`**

The preregistration fixed the cross-benchmark rule before causal outcome access: the same primary regime on both LongMemEval and LoCoMo yields `[CROSS-BENCHMARK CAUSAL MECHANISM LEAD]`; different regimes reject a universal shared mechanism.

## Primary results

| Benchmark | Native R@3 | Frozen Full-Haar R@3 | Within-band Haar R@3 | L_full | L_band | rho | Regime |
|---|---:|---:|---:|---:|---:|---:|---|
| LoCoMo | 0.23654714666441054 | 0.13770827054136000 | 0.23009932190966770 | 0.09883887612305053 | 0.006447824754742842 | **0.06523571501071657** | SPECTRAL-SUBSPACE PRESERVATION LEAD |
| LongMemEval | 0.54197517730496450 | 0.38271666666667000 | 0.51922872340425530 | 0.15925851063829450 | 0.022746453900709174 | **0.14282724238436822** | SPECTRAL-SUBSPACE PRESERVATION LEAD |

Both `rho` values are below the preregistered `0.25` boundary.

## Controls

LoCoMo:
- frozen native reproduction error: `0.0`
- signed-permutation exact control: `PASS`
- continuous norm max abs error: `4.440892098500626e-16`
- continuous dot max abs error: `1.6653345369377348e-15`

LongMemEval:
- frozen native reproduction error: `1.1102230246251565e-16`
- signed-permutation exact control: `PASS`
- continuous norm max abs error: `5.551115123125783e-16`
- continuous dot max abs error: `8.881784197001252e-16`

## Secondary cross-band pattern

The secondary arms are directionally consistent across the two benchmarks:

| Secondary arm | LoCoMo R@3 | LongMemEval R@3 |
|---|---:|---:|
| HAAR_HIGH_MID64 | 0.1853595921993316 | 0.4923985815602837 |
| HAAR_HIGH_LOW64 | 0.1701105465104754 | 0.4509716312056738 |
| HAAR_MID_LOW64 | 0.23355322743969084 | 0.5138542553191490 |

In both benchmarks, mixing Mid+Low while leaving High32 intact is much less damaging than interventions that mix High32 with another spectral band. This is secondary evidence only and does not alter the preregistered rho verdict.

## Licensed interpretation

The causal evidence now supports the narrower mechanism that the native SIGN96 advantage is not primarily dependent on preserving exact individual principal-axis directions inside each 32D spectral band. Most of the loss caused by unrestricted orthogonal mixing is avoided when High32, Mid32, and Low32 remain separate subspaces.

This supports **spectral-scale segregation / spectral-subspace preservation** as a cross-benchmark causal mechanism lead for the two frozen benchmarks.

It does **not** establish:
- a universal population-level mechanism;
- production superiority of SIGN hashing;
- that archive-local SVD coordinates correspond to LLM neuron axes;
- a unique explanation for all SIGN-vs-float or SIGN-vs-ITQ gaps.

## Provenance note

LoCoMo outputs are persisted normally on this branch. The first LongMemEval full run completed its compute step successfully but its output commit was rejected by Git because this research branch advanced concurrently. The exact primary JSON was recovered from the immutable Actions job log and persisted separately. A sharded exact-equivalent rerun is used as redundant artifact-level verification and must match the primary values before the LongMemEval artifact package is considered fully closed.
