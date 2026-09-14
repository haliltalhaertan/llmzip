[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Task 3 — finite synthetic ITQ diagnostic

Base: `ae9175676b840ae6a80a31eba9836187dc1b7491`. This report changes no preregistration, root report, ledger, or G3 artifact.

20 fixed initializations per fixed matrix; d=96. All three distributions were selected before execution.
ITQ uses sign>=0 and alternating orthogonal Procrustes. Cap=250; relative tolerance=1e-8; stable steps=5.
Objectives are training mean squared quantization residuals per matrix entry (sum/(n*d)).

| Distribution | n | Converged / 20 | Iterations min/median/max | Initial → final objective mean | Fit SP median | Haar–Haar SP median |
|---|---:|---:|---|---|---:|---:|
| gaussian | 100 | 20 | 9/12.0/16 | 0.403171 → 0.150117 | 1.208465 | 1.210181 |
| heterogeneous | 100 | 20 | 9/12.5/16 | 0.405956 → 0.169814 | 1.208505 | 1.210181 |
| rotated_heterogeneous | 100 | 20 | 9/12.0/17 | 0.404682 → 0.171517 | 1.208051 | 1.210181 |
| gaussian | 250 | 20 | 20/29.5/34 | 0.399592 → 0.211210 | 1.208190 | 1.210181 |
| heterogeneous | 250 | 20 | 21/27.5/44 | 0.402462 → 0.225467 | 1.208167 | 1.210181 |
| rotated_heterogeneous | 250 | 20 | 20/26.5/38 | 0.401477 → 0.225638 | 1.207710 | 1.210181 |
| gaussian | 500 | 20 | 41/57.5/114 | 0.403113 → 0.254419 | 1.207765 | 1.210181 |
| heterogeneous | 500 | 20 | 36/52.0/95 | 0.408864 → 0.266277 | 1.207440 | 1.210181 |
| rotated_heterogeneous | 500 | 20 | 34/52.0/88 | 0.408751 → 0.267172 | 1.207596 | 1.210181 |
| gaussian | 1000 | 20 | 75/99.0/141 | 0.403258 → 0.290042 | 1.207681 | 1.210181 |
| heterogeneous | 1000 | 20 | 66/89.0/117 | 0.408176 → 0.299034 | 1.207312 | 1.210181 |
| rotated_heterogeneous | 1000 | 20 | 62/97.5/140 | 0.408185 → 0.298511 | 1.206850 | 1.210181 |

Distances divide Frobenius norm by sqrt(96); CSV also retains unnormalized and raw values.
Signed-permutation alignment maximizes abs(R1.T@R2) using linear_sum_assignment. No principal angles or arbitrary orthogonal alignment.
The Haar null is one separate, fixed 20-rotation panel reused at every n/distribution, with 190 dependent pairs.
Each ITQ panel likewise has 190 dependent fit pairs; quantiles and differences are descriptive, not a hypothesis test.

## Data and provenance

For each n a literal-seeded standard Gaussian matrix is generated. Coordinate means are subtracted.
Heterogeneous population variances are geomspace(16,1/16,96), divided by their arithmetic mean (variance ratio 256).
This is fixed population-energy scaling, not sample whitening or per-row normalization. The rotated variant is the same centered heterogeneous matrix right-multiplied by one literal-seeded Haar matrix.
Each panel has one data realization, not twenty independently generated data samples. Initialization and null seeds are separate fixed panels.
PLAN.json was written before controls/fits and pins source bytes, seeds, dtype, shape and stopping rules.
RESULTS.json carries matrix hashes and per-fit metadata; fits.csv, objective_history.csv and pairwise_distances.csv retain the individual observations.
Run with the locked interpreter: `python -B itq_feasibility_synthetic.py --output task3/review-new` (fresh directory).

## Limits

- One generated data realization per n, paired across distributions; twenty initializations per fixed matrix.
- This measures conditional optimizer variability, not sampling stability across independent datasets.
- The 190 pairwise distances share twenty fits and are dependent; the Haar pairs are also dependent.
- The same initial and null rotations are reused across panels; panels are not independent replications.
- Distribution differences are descriptive only: no p-values, significance, equivalence margin, or power claim.
- This finite panel cannot determine a universal minimum n, equivalence, or statistical indistinguishability.
- Objective convergence under the declared rule does not imply a unique/stable rotation or a global optimum.
- An isotropic Gaussian population has no preferred orientation; different fits alone do not establish failure.
- Training quantization error is measured; no held-out loss, real representation or retrieval outcome is measured.
- No preregistration arm selection, seal, main ledger/state update, or G3 modification is authorized here.

Elapsed wall time: 45.973 seconds; fitting subtotal: 44.212 seconds.
Controls: signed-permutation zero distance, raw-distance discrimination, unrelated-Haar nonzero distance, exhaustive 3-D assignment oracle, exact-zero sign convention, nonincreasing objective, Procrustes closed-form optimum and wrong-sign negative.
These measurements supply a finite feasibility/stability description. They do not determine at what n ITQ becomes statistically indistinguishable from random rotation.

## Actual fitted state supplement

`measure_fitted_state.py` reproduces exactly the existing Gaussian n=100 fit with data seed 5212100 and initialization seed 7312001. Input matrix, initial/final rotation, final binary codes, objectives and stopping metadata match the recorded fit exactly. The main ITQ source and PLAN remain byte-identical. `FITTED_STATE.json` binds the supplement's own source hash and locked environment to those identities. This is an actual NumPy/SciPy fitted R; it is not an actual Faiss ITQ fit. It complements Task 2's explicitly float32 matrix surrogate.

| Stored state | dtype | Raw matrix bytes | `.npy` bytes | Interpretation |
|---|---|---:|---:|---|
| `actual_binary_artifacts/R_fitted_float64.npy` | float64 (`<f8`) | 73,728 | 73,856 | Actual fitted rotation |
| `actual_binary_artifacts/R_converted_float32.npy` | float32 (`<f4`) | 36,864 | 36,992 | Explicit conversion of fitted rotation; not refitted |

Both files use `np.save(..., allow_pickle=False)` and pass exact dtype/shape/raw-byte roundtrip checks. The float32 cast changes entries: maximum absolute difference, measured back in float64, is **1.486746448176035e-08**. Its values and hashes therefore differ from the actual float64 fit. Raw-matrix and `.npy` SHA-256 hashes are in `FITTED_STATE.json`; `HASHES.json` covers the source, receipt and binary artifacts. These byte counts describe the learned rotation and its array container, not a full index/deployment footprint. No code-stability, objective, or retrieval claim is made for the converted state.

Reproduce this single-fit supplement from the clone root with a fresh output directory:

```powershell
$env:PYTHONHASHSEED = '0'
& 'C:/Users/MDP/Documents/ChatGPT/LLM_TOKEN_ZIP/work/.venvs/g3-lock-20260912/Scripts/python.exe' -B research/v52/preseal_diagnostics_2026_09_12/task3/measure_fitted_state.py --output task3/state-review
```

The original panel receipt is `VERIFICATION.json`: all 240 stopping traces (11,776 iterations) and 2,470 pair rows checked; the first initialization in each of the 12 panels reproduced identical data, fitted-rotation and binary-code hashes. This same-implementation reproduction is distinct from the independent small-dimensional mathematical controls in `CONTROL_RESULTS.json`. No full-panel rerun was performed for the fitted-state supplement. Wall-clock values and timestamps are observational and need not reproduce byte-for-byte.
