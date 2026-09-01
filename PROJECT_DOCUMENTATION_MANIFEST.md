# Project Documentation Manifest

Snapshot date: 2026-09-01

This index records the documentation-oriented snapshot assembled from the canonical Google Drive project archive and the material that has been migrated into this GitHub repository. Large raw datasets, multi-megabyte raw trial tables, compressed benchmark packages, and packed binary-code payloads are intentionally kept in Drive and indexed separately.

A 104-file documentation snapshot was assembled from the Drive archive during migration. The repository exposes the load-bearing/current documents directly for review, while the historical exact-byte archive and heavy artifacts remain linked through the canonical Drive folders below. This avoids replacing provenance-sensitive files with reconstructed or truncated copies.

## Canonical Drive archive

- Master project folder: https://drive.google.com/drive/folders/1uM2bLBC3XQmvbdkTpjhvR6_N6OO7Qyxv
- Prompt archive: https://drive.google.com/drive/folders/1kLISFbGpKS0IA3MLXLqOE8cgFGiMSNX8
- Head Researcher handoff: https://docs.google.com/document/d/1QXV2fKQL0TnWEBcm3ke2poph8yaWmqNuWm38TPYswP8/edit
- Literature reviews: https://drive.google.com/drive/folders/10nFwmZTX3HbSszJCW5bnk4H_NTVz8Qhm
- Task 4F0 original output package: https://drive.google.com/drive/folders/1nxDNk78sfTUqAPPNhOeGi-cyKscI-c3c
- Task 4E0 current received package: https://drive.google.com/drive/folders/1z_70bzjdMZ_NlS92PRxP_i_CbaWqoNj8
- Task 4C2 final outputs: https://drive.google.com/drive/folders/1wDpyMSLHtkEFnql8VMBS_cOhDAQWYzEK
- Task 4C2 audit package: https://drive.google.com/drive/folders/1Jhr3UqcYuBsVtwB3QTfiB6U5GY0bnZU3
- V51 checkpoint: https://drive.google.com/drive/folders/1Dldksm1BERKDqNXUzLVrlNmLHBN5SvEy
- V52 Task 2 raw external audit: https://drive.google.com/drive/folders/1PGUdYDf8b4YsV50QC_U5NOiYgPpUKUjx

## GitHub documents migrated directly

### Project-level
- `START_HERE_V52_4F1.md` — single operational handoff for a cold-start researcher/LLM; defines the current V3 independent-audit task, byte anchors, required external corpus, safety boundary and completion condition.
- `ops/CURRENT_STATE.json`, `docs/CONTINUITY_PROTOCOL.md`, `docs/CONTINUITY_LEDGER.md`, and `tools/verify_continuity_state.py` — crash-safe, hash-checked operational state and append-only multi-agent handoff controls.
- `README.md`
- `docs/PROJECT_STATUS_2026-08-27.md`
- `docs/PROJECT_STATUS_2026-08-28.md`
- `docs/RESEARCH_PROGRAM_STATUS_2026-08-31.md`
- `docs/DRIVE_MASTER_ROOT_INVENTORY_2026-08-31.md`
- `PROJECT_DOCUMENTATION_MANIFEST.md`
- `DATASETS_AND_LARGE_ARTIFACTS.md`

### V51
- `docs/v51/LLM_MEMORY_RESEARCH_MASTER_CHECKPOINT_V51.md` — the full V1–V50 research narrative and V51 transition checkpoint.

The canonical V51 Drive archive additionally contains `NEW_CHAT_START_PROMPT_V51.md`, the V51 file manifest, protocol manifest, scripts, and compact JSON/CSV summaries of the historical experiments.

### V52 Task 3
- `docs/v52/task3/V52_T3A1_PROTOCOL_PATCH.md`

### V52 Task 4C1
- independent Task 4C1 audit already lives in `audit_v52_t4c1/`.
- the canonical Drive archive contains Task 4C1 prior-art/novelty material, blocked-run SHA trail, preregistration/method-spec artifacts where exact bytes are available.

### V52 Task 4C2
- `docs/v52/task4c2/V52_T4C2_COMPUTE_REPORT.md`
- `docs/v52/task4c2/V52_T4C2_PRE_RUN_SEAL.json`
- `docs/v52/task4c2/V52_T4C2_POST_RUN_MANIFEST.json`
- exact/current audit prompt under `prompts/`.

The canonical Task 4C2 Drive folder additionally contains the raw trial table, question-level table, same-input proof, bit-balance/collision/tie/distance/rank diagnostics, strata tables, sealed source, packed binary-code bundle, and complete output ZIP. Hashes for these outputs are frozen in `V52_T4C2_POST_RUN_MANIFEST.json`.

### V52 Task 4C3 / 4D

- `docs/v52/task4c3/TASK4C3_ACCEPTED_CHECKPOINT_2026-08-28.md`
- `audit_v52_t4c3/`
- `docs/v52/task4d/TASK4D_ACCEPTED_CHECKPOINT_2026-08-29.md`

### V52 Task 4F0

- `prompts/V52_TASK_4F0_BEAM_LARGE_SCALE_ADAPTER_EVIDENCE_FREEZE_2026-08-29.md`
- `prompts/V52_TASK_4F0_CODEX_COLD_START_INDEPENDENT_AUDIT_PROMPT_2026-08-31.md`
- `prompts/V52_TASK_4F0_RESTRICTED_COHORT_REFREEZE_DRAFT_2026-08-31.md` — preparation draft; not a seal.
- `prompts/V52_TASK_4F0_RESTRICTED_REFREEZE_INDEPENDENT_AUDIT_PROMPT_2026-08-31.md` — prompt for the separate cold-start auditor.
- `audit_v52_t4f0_codex_2026_08_31/` — 34-file complete independent-audit package, including its self-excluding hash inventory.
- `docs/v52/task4f0/TASK4F0_AUDIT_ACCEPTANCE_AND_REFREEZE_DECISION_2026-08-31.md`
- `docs/v52/task4f0/TASK4F0_INCOMING_AUDIT_REPORT_RECEIPT_2026-08-31.md`
- `docs/v52/task4f0/TASK4F0_REFREEZE_PREPARATION_LOG_2026-08-31.md` — preparation-only gate record; not a sealed protocol.
- `docs/v52/task4f0/TASK4F0_RESTRICTED_REFREEZE_AUDIT_RECEIPT_2026-08-31.md` — historical receipt for the superseded blocked audit attempt.
- `docs/v52/task4f0/TASK4F0_RESTRICTED_REFREEZE_FINAL_SEAL_DECISION_2026-08-31.md` — Head Researcher acceptance and restricted-cohort seal decision; Task 4F1 remains blocked.
- `docs/v52/task4f0/TASK4F0_AUDIT_SUMMARY_RECONCILIATION_2026-08-31.md` — reconciles 1,743 annotation-exact, 41 ambiguous, 31 excluded-exact and the accepted 1,712 denominator.
- `audit_v52_t4f0_restricted_refreeze_independent_audit_2026_08_31/` — superseding 22-gate independent audit package; verdict `PASS WITH CONDITIONS — CANDIDATE MAY BE SEALED BY HEAD RESEARCHER`.
- `task4f1_execution_candidate_2026_08_31/` — guarded, byte-bound outcome-capable implementation candidate; not independently audited and not authorized to run.
- `task4f1_execution_candidate_preflight_2026_08_31/` — outcome-free implementer preflight evidence; not independent sign-off.
- `prompts/V52_TASK_4F1_EXECUTION_CANDIDATE_INDEPENDENT_AUDIT_PROMPT_2026-08-31.md` — cold-start audit prompt for the exact execution-candidate bytes.
- `audit_v52_t4f1_execution_candidate_independent_audit_2026_08_31/` — V1 technical audit; its disclosed A1 outcome-capable execution prevents using it as a clean seal sign-off.
- `task4f1_execution_candidate_v2_2026_09_01/` and `audit_v52_t4f1_execution_candidate_v2_independent_audit_2026_09_01/` — V2 candidate and outcome-free independent `BLOCKED` audit; B1–B3 finalization/checkpoint defects are preserved as evidence.
- `task4f1_execution_candidate_v3_2026_09_01/` and `task4f1_execution_candidate_v3_preflight_2026_09_01/` — V3 remediation candidate and outcome-free synthetic preparation evidence; independent audit pending.
- `prompts/V52_TASK_4F1_EXECUTION_CANDIDATE_V2_INDEPENDENT_AUDIT_PROMPT_2026-09-01.md` and `prompts/V52_TASK_4F1_EXECUTION_CANDIDATE_V3_INDEPENDENT_AUDIT_PROMPT_2026-09-01.md` — fresh cold-start audit prompts; both forbid execution and outcome access.
- `remediation_v52_t4f0_env_2026_08_31/` — isolated environment recovery record; only small human-readable reports are versioned, while its local runtime and copied corpus are ignored.
- `remediation_v52_t4f0_env_2026_08_31/REPRESENTATION_SELFTEST_REPORT.md` — exact-lock pre-outcome 100K/500K/1M/10M representation self-test results.

### Prompts
- `prompts/PROMPT_ARCHIVE_MASTER_INDEX_2026-08-27.md`
- `prompts/V52_TASK_4C2_INDEPENDENT_ADVERSARIAL_AUDIT_PROMPT_2026-08-27.md`
- canonical Drive links in the prompt index preserve the exact current takeover/resume prompts and historical prompt lineage.

### Literature / recovery
- `literature/V52_T4C2_DEEP_LITERATURE_REVIEW_BINARY_GEOMETRY_2026-08-27.md`
- `recovery/FILE_LIBRARY_SYNC_STATUS_2026-08-25.md`

## Heavy artifacts deliberately not duplicated into ordinary Git history

- canonical `longmemeval_s_cleaned.json` (277,383,467 bytes)
- compressed dataset RAR
- Task 4C2 raw trial/question tables and binary geometry ZIP
- Task 2 multi-megabyte raw tables
- V51/V52 ZIP handoff and audit bundles.

Their exact Drive URLs and canonical hashes are recorded in `DATASETS_AND_LARGE_ARTIFACTS.md`, frozen manifests, and audit records.

## Provenance rule

A partial File Library snippet is never promoted into a replacement file with the canonical filename. Exact-byte artifacts are migrated only when their full bytes are available; otherwise the repository records the canonical Drive/File Library source and expected hash. This is necessary because same-name, hash-different reconstructions would corrupt the audit trail.

## Scope rule

GitHub is the review surface for the research narrative, current checkpoints, prompts, audit records, literature guards, seals/manifests, and directly reviewable documentation. Google Drive remains the canonical byte store for benchmark inputs and heavy/raw artifacts. Frozen SHA256 values are the chain-of-custody authority.
