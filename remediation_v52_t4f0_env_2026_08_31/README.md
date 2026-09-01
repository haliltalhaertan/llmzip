# V52 Task 4F0 — Locked Environment Remediation

Status: `BLOCKED — EXTERNAL PACKAGE INSTALL NOT AVAILABLE`

This directory is an isolated remediation environment for the independent-audit blocker. It is not the candidate refreeze namespace and is not a scientific run environment.

## Attempt recorded

- Python executable: bundled Python 3.12.13;
- venv: `remediation_v52_t4f0_env_2026_08_31`;
- requested exact packages: NumPy 2.3.2, SciPy 1.16.1, scikit-learn 1.7.1, psutil 7.0.0;
- local pip cache: no matching wheels found;
- sandbox pip attempt: blocked by network policy (`WinError 10013`);
- escalated pip attempt: rejected by the host usage-limit review.

No package was substituted and no candidate seal or outcome-bearing artifact was changed.

## Required next action

Install the four exact locked packages into this venv from an approved network or offline wheel source, then verify package versions and:

`OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `NUMEXPR_NUM_THREADS=1`, `PYTHONHASHSEED=0`.

Until that verification succeeds, the raw-corpus representation self-test remains `BLOCKED`.

## Current result

The exact lock is now installed and verified. Archive-only representation self-tests passed on 100K, 500K, 1M and 10M samples with finite 96D/rank-96 outputs and zero repeatability differences. See `REPRESENTATION_SELFTEST_REPORT.md`.

This closes only the environment/representation gate. It does not authorize sealing or 4F1; the future byte-bound implementation and a new independent sign-off remain required.
