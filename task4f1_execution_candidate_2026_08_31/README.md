# V52 Task 4F1 — Execution Implementation Candidate

This namespace contains a guarded, outcome-capable implementation candidate for the sealed 1,712-question BEAM restricted cohort.

It is prepared for independent code audit only. It is not a Task 4F1 preregistration, run authorization, or permission to inspect retrieval-quality outcomes.

The implementation has three modes:

- `preflight`: verifies exact byte/environment/corpus/cohort bindings and runs synthetic invariance tests without computing BEAM retrieval quality;
- `run`: processes authorized archives with atomic per-archive checkpoints but refuses to start without a separate Head Researcher run-authorization file bound to the final audited script and seal hashes;
- `finalize`: refuses partial finalization and requires all 96 eligible archives before producing aggregate files.

The candidate seal must remain `PREPARED_NOT_INDEPENDENTLY_AUDITED`. No `RUN_AUTHORIZATION.json` exists in this namespace.

Current authorization:

- `TASK 4F1 PREREGISTRATION = BLOCKED`
- `TASK 4F1 RUN = BLOCKED`
- `RETRIEVAL-QUALITY OUTCOME ACCESS = FORBIDDEN`

See `EXECUTION_SPEC.md` for exact implementation interpretations that require independent acceptance.
