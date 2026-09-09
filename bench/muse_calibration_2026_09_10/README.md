# Auditor calibration corpus — DELIBERATELY DEFECTIVE ARTIFACTS

**Nothing in this directory is a decision, a preregistration, or a proposal.**
Every file here is a deliberately flawed artifact kept for one purpose: measuring
what an independent auditor does and does not find.

- `B_DEFECTIVE_v1.md` — an early, **defective** revision of the 12-byte baseline
  preregistration draft. sha256 `40cdf53a706d659c70aecfdb8b7314cf84ac4abfd16e6389189add96beee48b8`.
  The corrected live draft is a different artifact and is not in this directory.
  **This file must never be cited, sealed, executed or treated as current.**

## Answer key

The list of known defects is held **outside this repository** so that an auditor
running in this workspace cannot read it. Only its hash is committed:

    answer key sha256 = aa41327db414a7c572f943779b7f2f7bf8e49ba526e49bffd89fd3249620178c

After a calibration run the plaintext key is disclosed and its hash checked against
this line, which shows the key was fixed before the run rather than written to fit
the result.

## Scoring

Findings are scored in two classes. **Semantic** findings — wrong provenance
attribution, wrong scope, gate mis-mapping, a decision rule that is not exhaustive —
carry more weight than **mechanical** findings — wrong line number, wrong hash, a
miscount, a field that goes stale on push. Inventing a defect where none was planted
counts against the auditor as much as missing one.

## Prohibitions

This directory authorizes nothing. No seal, no pilot, no run. Task 4F1 remains
SEALED / RUN BLOCKED / OUTCOME ACCESS FORBIDDEN.
