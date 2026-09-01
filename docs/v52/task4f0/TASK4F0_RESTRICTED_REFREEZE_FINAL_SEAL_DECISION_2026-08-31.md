# V52 Task 4F0 — Restricted-Refreeze Final Seal Decision

Date: 2026-08-31  
Decision owner: Head Researcher / Codex  
Candidate namespace: `audit_v52_t4f0_restricted_refreeze_2026_08_31/`  
Independent audit namespace: `audit_v52_t4f0_restricted_refreeze_independent_audit_2026_08_31/`

## Decision

The independent verdict `PASS WITH CONDITIONS — CANDIDATE MAY BE SEALED BY HEAD RESEARCHER` is accepted.

The restricted-cohort protocol is sealed with status:

`INDEPENDENTLY_AUDITED_RESTRICTED_COHORT_SEALED`

This seal freezes the 1,712-question primary cohort, the four excluded archives, the memory-unit and representation specification, the planned arms and seeds, the metric formulas and denominator, the dependency/thread lock, deterministic tie priority, and the stop rule.

This is not a Task 4F1 preregistration or run authorization.

## Exact-byte chain

- Repository parent commit: `d3c7aa09c9553cd5ac100e668923abab602e4257`
- Pinned BEAM commit: `3e12035532eb85768f1a7cd779832b650c4b2ef9`
- Restricted cohort SHA256: `9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a`
- Accepted original audit inventory SHA256: `3b3bb1a25cd9c8b7a56e1c29afbe8b3589f0c5c5f4705c000b7625da6f64fa65`
- Independent audit report SHA256: `0a9fbbe72015f8e7b8439fcd0f188375e1fbab0a1772d685050801e192681790`
- Independent audit inventory SHA256: `b7f951419c0f56da432ebd9b50d7ddf447d818d43ab1879e10b2311d8de0563c`
- Pre-decision candidate seal SHA256: `ccefe9264e63b2f1d02eb485fa37c474a80e50e484d9d06dfdf8e4557383f076`

The nine independently audited payload files and `PAYLOAD_HASHES.json` were not rewritten during the sealing act. Only `CANDIDATE_SEAL.json`, which the auditor explicitly left for the Head Researcher to change, records the state transition and audit binding. The final seal SHA256 is recorded below after serialization and verification.

## Closed gates

- 22/22 independent audit gates passed.
- The exact dependency lock was satisfied in the isolated environment.
- Four raw-corpus representation self-tests passed with 96-dimensional, rank-96, finite and repeat-identical outputs.
- Signed-permutation, tie-priority and centered-continuous invariance checks passed.
- Candidate preflight leakage audit passed.
- No retrieval-quality outcome was opened or computed.

## Remaining mandatory gate

Before Task 4F1 can be preregistered, its outcome-bearing fitting/ranking implementation must be created in a separate namespace, byte-bound, and independently audited for static/runtime leakage, invariance, deterministic ranking, output schema, environment enforcement and stop-rule compliance.

Until that audit is accepted:

- `TASK 4F1 PREREGISTRATION = BLOCKED`
- `TASK 4F1 RUN = BLOCKED`
- `RETRIEVAL-QUALITY OUTCOME ACCESS = FORBIDDEN`

## Final seal digest

`CANDIDATE_SEAL.json` SHA256: `596c8056342e75110a940ee838cb080e9cd830f269aca0d1d87a0c4d482f859c`
