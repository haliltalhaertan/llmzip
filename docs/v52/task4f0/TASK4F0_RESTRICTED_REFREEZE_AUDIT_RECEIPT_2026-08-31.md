# V52 Task 4F0 — Restricted-Refreeze Independent Audit Receipt

Date: 2026-08-31  
Source: user-pasted cold-start auditor report  
Candidate: `audit_v52_t4f0_restricted_refreeze_2026_08_31/`

## Receipt status

The independent audit report is received and accepted as a blocking gate result. Its final verdict is:

`BLOCKED — DO NOT SEAL / DO NOT PREREGISTER 4F1`

The report was supplied in the user message rather than as a separately hashable file. This receipt records its substantive findings; it does not claim an exact-byte hash for the pasted message.

## Findings accepted

The auditor independently confirmed:

- candidate payload hashes, sizes and local closure are consistent;
- accepted audit inventory SHA256 is `3b3bb1a25cd9c8b7a56e1c29afbe8b3589f0c5c5f4705c000b7625da6f64fa65`;
- pinned BEAM checkout is at `3e12035532eb85768f1a7cd779832b650c4b2ef9`, with 205 manifest-selected files verified and zero Git blob/size mismatches;
- raw-corpus structural checks pass for 100 `chat.json` files;
- only `1M::5`, `1M::26`, `1M::33`, and `1M::34` contain duplicate raw-message keys;
- cohort checks pass: 2,000 records, 1,712 eligible questions, 587 ALL@3 structural zeros;
- protocol, no-outcome preflight and forbidden-identifier checks are internally consistent.

## Blocking gates

1. The declared environment is not reproducible in the available runtime: Python 3.12.13 is present, but NumPy is 2.3.5 instead of the locked 2.3.2; SciPy, scikit-learn and psutil are unavailable; and the five declared thread/hash environment variables are unset. The representation self-test therefore cannot run.
2. The candidate namespace contains only the no-outcome preflight implementation. The future 4F1 fit/rank implementation is not present, so its executable leakage and invariance gates cannot be independently audited.
3. Independent sign-off remains pending. The candidate seal must remain `PREPARED_NOT_INDEPENDENTLY_SEALED`.

## Head Researcher decision

- Keep `CANDIDATE_SEAL.json` unchanged.
- Keep `TASK 4F1 PREREGISTRATION = BLOCKED`.
- Keep `TASK 4F1 RUN = BLOCKED`.
- Do not expose or compute retrieval-quality outcomes.
- Do not substitute the currently available runtime for the locked environment.
- Open a separate remediation branch for environment recovery and future implementation audit; only after those are independently verified may sealing be reconsidered.

## Remediation gates (new work, not authorized by this receipt)

1. Materialize an isolated environment matching `DEPENDENCY_LOCK.txt` exactly, or record a new pre-outcome lock after an explicit protocol decision; verify versions and thread controls.
2. Add a separately byte-bound, outcome-bearing 4F1 implementation without changing the candidate cohort or protocol.
3. Run an independent static/runtime leakage and invariance audit of that implementation without opening outcomes first.
4. Obtain a new independent sign-off. Until then the candidate remains blocked.

## Remediation attempt on 2026-08-31

An isolated Python 3.12.13 venv was created under `remediation_v52_t4f0_env_2026_08_31/`. The exact package installation could not proceed: the sandbox blocked PyPI access, the escalated install request was rejected by the host usage-limit review, and no matching local wheels were available. No substitute versions were installed.

The user subsequently installed the exact lock successfully. A pre-outcome archive-only representation self-test then passed on 100K, 500K, 1M and 10M samples with 96D/rank-96 finite outputs and zero repeatability differences. This closes the environment/representation remediation gate, but not the missing byte-bound 4F1 implementation or independent sign-off.
