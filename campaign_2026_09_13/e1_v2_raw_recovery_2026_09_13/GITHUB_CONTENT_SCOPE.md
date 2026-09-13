# GitHub content scope — E1 V2 raw-cache recovery

Status: **LOCAL EXPLORATORY FOLLOW-UP / NOT INDEPENDENTLY AUDITED / NOT FOR CITATION**.

Parent frozen checkpoint: `4bfdb820904ead1b6378b00bd5bf71c1ab2fe138`.
Target namespace: `campaign_2026_09_13/e1_v2_raw_recovery_2026_09_13/`.

GitHub intentionally carries only the compact review/provenance surface: the lead report,
disposition, LoCoMo conflict note, run receipt, Drive binding, and this scope note. The executable
analysis script, result JSON, input-cache inventory, bootstrap outputs, per-query rows, archive
geometry, and their `HASHES.json`/sidecar remain inside the immutable SHA-bound Drive ZIP.

Drive package:
- folder ID: `15v4kB230kKx2tRq-GGVz2XsoJdMInDlM`
- package file ID: `1qP5ZtCnC-seOQIWDPkEYEGdISQooT0r0`
- package SHA256: `b6b7923f2e9623f5e1d46dda523f8f4a2919b62f69e82ba5b2bb679ad9771ae8`

The ZIP's internal manifest binds the analysis payload at packaging time. `DRIVE_BINDING.json`
was created afterwards and points to that immutable ZIP; it is intentionally not inside it.

Raw source caches remain in the independently SHA-verified heavy-backup folder and are not copied
into Git. No representation refit was used in the recovery analysis.

Task4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.
