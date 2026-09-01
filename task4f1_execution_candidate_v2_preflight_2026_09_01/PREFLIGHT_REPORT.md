# V52 Task 4F1 — V2 Candidate Outcome-Free Preparation Report

Date: 2026-09-01  
Role: Head Researcher preparation only  
Status: `PASS — READY FOR A FRESH COLD-START INDEPENDENT V2 AUDIT`

This report does not preregister or authorize Task 4F1. No Native, Haar, signed-permutation or ITQ retrieval-quality outcome was computed, opened or interpreted during V2 preparation.

## Governance disposition

The V1 candidate and its 2026-08-31 audit remain byte-preserved. The prior audit's technical findings are retained as diagnostic evidence, but Incident A1 prevents using it as the clean outcome-free sign-off for sealing. The incidental fact that an unauthorized partial run reached 26 archives is excluded from every V2 gate and future scientific decision.

V2 remains:

- `TASK 4F1 PREREGISTRATION = BLOCKED`
- `TASK 4F1 RUN = BLOCKED`
- `RETRIEVAL-QUALITY OUTCOME ACCESS = FORBIDDEN`

## Exact V2 bindings

- implementation: 56,142 bytes; SHA256 `c50dfa7130918b8183c51edf68f5e2baac21a419f0d29bf2ec930f9de38e6139`
- recursive payload inventory: 1,180 bytes; SHA256 `9d7429893f50a729e4471684580660461e944e599c43df24172b2c4d1d66e22d`
- candidate execution seal: 6,186 bytes; SHA256 `4cc6313649da9ca4b10e64610a8ff40173c1ccacd663dda9fadabcdf059b996c`
- machine preflight: 3,564 bytes; SHA256 `92618cf3acd3108534f7723126413f7d4664d85970eef7d05bbdc7aa7e2fee5c`
- sealed cohort: SHA256 `9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a`
- sealed Task 4F0 final seal: SHA256 `596c8056342e75110a940ee838cb080e9cd830f269aca0d1d87a0c4d482f859c`

## Remediation evidence

### D1 — recursive namespace closure

`candidate_package_preflight.py` now enumerates every file under the candidate with `ROOT.rglob("*")`. The clean candidate contains exactly the six declared payloads plus the excluded inventory and seal. A temporary nested unbound fixture was inserted, the preflight rejected the exact nested path, and the fixture was then removed. The clean preflight passed again. No `__pycache__` or nested file remains.

### D2 — non-derivable Head Researcher authority

The V2 authorization schema requires an HMAC-SHA256 over an exact, closed field set. The 32-byte key is provided only through `V52_T4F1_AUTH_HMAC_KEY_HEX`, while its SHA256 commitment must be fixed in the accepted candidate seal. The key itself is forbidden from repository, candidate, audit, preregistration, log and output artifacts.

The prepared seal deliberately contains `PENDING_HEAD_RESEARCHER_PREREGISTRATION`, not a valid 64-hex commitment. Consequently V2 is cryptographically fail-closed in its audit state. Both the shipped template and a structurally complete fake authorization were rejected before output-directory creation. The latter stopped at `[BLOCKED - HEAD RESEARCHER AUTHORITY KEY NOT SEALED]`. No valid production authorization or production key was constructed.

### D3 — checkpoint provenance

Archive metadata schema V2 binds:

- `script_sha256`
- `cohort_sha256`
- `run_authorization_sha256`
- `execution_candidate_seal_sha256`

The same exact provenance dictionary is required during resume and finalization. An isolated synthetic checkpoint fixture passed with matching provenance and was rejected after changing only `run_authorization_sha256`.

## Re-run preparation gates

The locked environment matched Python 3.12.13, NumPy 2.3.2, SciPy 1.16.1, scikit-learn 1.7.1, psutil 7.0.0 and the five single-thread variables.

Outcome-free runner preflight passed:

- 2,000 cohort rows / 1,712 eligible questions / 96 archives;
- 192/192 used BEAM files matched pinned Git blob ID and size;
- finite rank-96 synthetic representation;
- exact signed-permutation Hamming/ranking invariance;
- Haar continuous invariance at `1.8735013540549517e-16`;
- ITQ orthogonality error at `1.7763568394002505e-15`;
- structural ALL@3 zero fixture;
- outcome-free `100K::12` representation canary reproduced archive digest `25089a07760a08d816f9ae0c8af2f02b284e1217807af4d0270acbb58f580025` and fixed-query digest `e422490a26d0934f31b06f808391d545e50282642af8997a24cb1d4e94fab869` without opening the question file or gold labels.

## Required next gate

A fresh cold-start auditor must audit these exact V2 bytes in a new namespace. The auditor must never invoke `--mode run` or `--mode finalize`, must never set the HMAC key environment variable, and must never construct a valid production authorization. Only `candidate_package_preflight.py`, `--mode preflight`, static analysis, independent representation reconstruction and synthetic fixtures are permitted.

Even after a clean PASS, Task 4F1 remains unpreregistered and unauthorized. Head Researcher sealing, preregistration, authority-key commitment and run authorization are separate future decisions.
