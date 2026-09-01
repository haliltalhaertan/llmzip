# V52 Task 4F0 — Locked-Environment Representation Self-Test

Date: 2026-08-31  
Status: `PRE-OUTCOME PASS — NOT A RETRIEVAL RESULT`

The exact dependency lock was installed in the isolated venv and verified:

- Python 3.12.13, 64-bit;
- NumPy 2.3.2;
- SciPy 1.16.1;
- scikit-learn 1.7.1;
- psutil 7.0.0;
- `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `NUMEXPR_NUM_THREADS=1`, `PYTHONHASHSEED=0`.

The accepted archive-only representation audit was run without ranking or retrieval metrics. Each run fits word/character TF-IDF, latent-32 and mixed-96 representations, then transforms only a post-fit canary query.

| Tier | Conversation | Archive units | Mixed shape | Rank | Finite | Repeat archive max abs diff | Repeat query max abs diff | Status |
|---|---:|---:|---|---:|---|---:|---:|---|
| 100K | 12 | 392 | 392×96 | 96 | yes | 0.0 | 0.0 | PASS |
| 500K | 12 | 1,120 | 1,120×96 | 96 | yes | 0.0 | 0.0 | PASS |
| 1M | 12 | 2,214 | 2,214×96 | 96 | yes | 0.0 | 0.0 | PASS |
| 10M | 1 | 19,895 | 19,895×96 | 96 | yes | 0.0 | 0.0 | PASS |

Raw input files were copied byte-for-byte from the pinned BEAM checkout into the remediation workspace solely for this pre-outcome self-test. No gold labels, answers, rubrics, source annotations, rankings, Native/Haar arms or retrieval-quality metrics were loaded or produced.

Machine-readable outputs:

- `representation_100K_runtime_check.json`
- `representation_500K_1M_runtime_check.json`
- `representation_10M_runtime_check.json`

This report closes the environment/representation self-test blocker for the candidate audit, but it does not by itself provide the missing byte-bound 4F1 implementation or independent sign-off. The candidate seal must remain `PREPARED_NOT_INDEPENDENTLY_SEALED` until those separate gates are audited.
