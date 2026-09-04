# V52 Cross-Benchmark Head32-vs-Tail64 Causal Checkpoint

Date: 2026-09-04
Branch: `research/v52-sign-mechanism-locomo-2026-09-04`
Preregistration Git blob: `0d34207be55a75194b585789c7139cbc8aeb264d`

## Preregistered cross-benchmark verdict

**`[CROSS-BENCHMARK HEAD-TAIL CAUSAL LEAD]`**

Shared benchmark-level regime:

**`[HEAD-TAIL TWO-SUBSPACE SUFFICIENCY LEAD]`**

The cross-benchmark rule and rho_2 bands were frozen before any Head32-vs-Tail64 outcome access. Both frozen benchmarks independently landed in the same preregistered regime.

## Primary causal results

| Benchmark | Native R@3 | Frozen Full-Haar R@3 | Head32⊕Tail64 Haar mean R@3 | L_full | L_2 | rho_2 | Regime |
|---|---:|---:|---:|---:|---:|---:|---|
| LoCoMo | 0.23654714666441054 | 0.13770827054136000 | 0.22592744129014436 | 0.09883887612305053 | 0.01061970537426618 | **0.10744461886682183** | HEAD-TAIL TWO-SUBSPACE SUFFICIENCY LEAD |
| LongMemEval | 0.54197517730496460 | 0.38271666666667000 | 0.51702092198581560 | 0.15925851063829460 | 0.024954255319148966 | **0.15669024668844653** | HEAD-TAIL TWO-SUBSPACE SUFFICIENCY LEAD |

Both rho_2 values are below the preregistered `0.25` sufficiency boundary.

## Frozen controls

LoCoMo:
- evidence-valid denominator: `1535`
- native reproduction error: `0.0`
- signed-permutation exact Hamming control: `PASS`
- continuous norm max abs error: `4.440892098500626e-16`
- continuous dot max abs error: `1.6653345369377348e-15`

LongMemEval:
- primary cohort: `470`, executed as `5/5` deterministic shards
- native reproduction error: `0.0`
- signed-permutation exact Hamming control: `PASS`
- continuous norm max abs error: `5.551115123125783e-16`
- continuous dot max abs error: `6.661338147750939e-16`

## Per-seed primary results

LoCoMo:
- 56001: `0.24319099434005997`
- 56002: `0.21927062124820315`
- 56003: `0.21937244243270300`
- 56004: `0.22784642362989693`
- 56005: `0.21995672479985867`

LongMemEval:
- 56001: `0.51064007092198570`
- 56002: `0.51315602836879440`
- 56003: `0.50950531914893620`
- 56004: `0.53027127659574470`
- 56005: `0.52153191489361700`

## Secondary diagnostic pattern

After the common Head32⊕Tail64 intervention, the Tail64 subset alone retained much more retrieval quality than Head32 alone on both benchmarks.

LoCoMo five-seed means (descriptive):
- Head32-only R@3 ≈ `0.0828743`
- Tail64-only R@3 ≈ `0.2150381`
- Full96 R@3 = `0.2259274`

LongMemEval five-seed means (descriptive):
- Head32-only R@3 ≈ `0.2467617`
- Tail64-only R@3 ≈ `0.4763869`
- Full96 R@3 = `0.5170209`

This subset observation is secondary and does not change the preregistered rho_2 verdict. It is consistent with, but does not by itself prove, the earlier hypothesis that the spectral tail supplies complementary fine discrimination while the head is comparatively coarse/redundant.

Pairwise discrimination remains a different quantity from top-3 retrieval. On LongMemEval, Head32 pairwise discrimination remains very high (~0.924 on average) despite substantially lower Head32-only R@3 than Tail64-only R@3. This reinforces the distinction between average pairwise separation and hard-negative top-k retrieval.

## Licensed interpretation

The previous three-band causal experiment established that preserving High32/Mid32/Low32 spectral subspaces avoids most of the loss caused by unrestricted 96D orthogonal mixing. This new, independently preregistered experiment narrows that mechanism further: on both frozen benchmarks, preserving only the boundary between the leading 32-dimensional spectral subspace and the remaining 64-dimensional tail is sufficient to preserve at least 75% of the native-vs-Full-Haar advantage under the frozen decision rule.

Therefore the current strongest causal mechanism lead is:

> **Head-vs-tail spectral separation, rather than exact individual principal axes or the Mid32/Low32 boundary, is load-bearing for the observed SIGN96 retrieval advantage on these two frozen memory-retrieval benchmarks.**

This does not establish that the split at exactly 32 is uniquely optimal or causal. The 32/64 boundary was inherited from the prior spectral-band analysis. Boundary localization requires a separate preregistration.

## Interpretation ceiling

This checkpoint supports a cross-benchmark fixed-benchmark causal mechanism lead only. It does not establish:
- a universal theorem about binary retrieval;
- production superiority of SIGN hashing;
- a unique optimal Head/Tail split;
- correspondence between these archive-local SVD coordinates and neural-network neuron axes;
- that the same mechanism will generalize to arbitrary encoders, corpora, bit widths, or retrieval metrics.

## Provenance

The Head32-vs-Tail64 preregistration was committed and physically copied to Google Drive before outcome access. LoCoMo executed in one sealed Actions job and persisted an immutable artifact plus branch outputs. LongMemEval independently re-downloaded and hash-verified the frozen 277,383,467-byte dataset in five deterministic shards, then aggregated 470/470 unique questions; all five shard jobs and the aggregate/persist steps completed successfully.

Task 4F1 execution state was not touched by this branch.
