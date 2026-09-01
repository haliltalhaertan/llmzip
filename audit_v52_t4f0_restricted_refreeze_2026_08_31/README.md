# V52 Task 4F0 — Restricted-Cohort Refreeze Candidate

This directory is a separate preparation namespace for the BEAM restricted-cohort branch.

It binds the accepted outcome-independent cohort, the four excluded archives, the accepted cold-start audit inventory, the proposed representation/metric/seed/tie rules, the dependency/thread lock, and a pre-outcome package verifier. `CANDIDATE_SEAL.json` is a candidate seal only.

The package deliberately does not contain or expose retrieval-quality outputs. Running `v52_t4f0_restricted_preflight.py` verifies the audit inventory and cohort semantics, then reports the remaining blockers. It does not load raw BEAM data, fit representations, rank queries, or calculate Native/Haar/ITQ metrics.

Required before any Task 4F1 preregistration decision:

- independent byte-level audit of this namespace;
- raw-corpus deterministic self-test, no-NaN and dimension checks;
- independent static/runtime leakage audit;
- signed-permutation and centered-continuous invariance checks;
- recorded auditor sign-off;
- a separately byte-bound outcome-bearing 4F1 implementation.

Until then: `TASK 4F1 PREREGISTRATION = BLOCKED` and `TASK 4F1 RUN = BLOCKED`.
