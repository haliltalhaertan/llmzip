# Project Documentation Manifest

Snapshot date: 2026-08-27

This index records the documentation-oriented snapshot assembled from the canonical Google Drive project archive and the material that has been migrated into this GitHub repository. Large raw datasets, multi-megabyte raw trial tables, compressed benchmark packages, and packed binary-code payloads are intentionally kept in Drive and indexed separately.

A 104-file documentation snapshot was assembled from the Drive archive during migration. The repository exposes the load-bearing/current documents directly for review, while the historical exact-byte archive and heavy artifacts remain linked through the canonical Drive folders below. This avoids replacing provenance-sensitive files with reconstructed or truncated copies.

## Canonical Drive archive

- Master project folder: https://drive.google.com/drive/folders/1uM2bLBC3XQmvbdkTpjhvR6_N6OO7Qyxv
- Prompt archive: https://drive.google.com/drive/folders/1kLISFbGpKS0IA3MLXLqOE8cgFGiMSNX8
- Literature reviews: https://drive.google.com/drive/folders/10nFwmZTX3HbSszJCW5bnk4H_NTVz8Qhm
- Task 4C2 final outputs: https://drive.google.com/drive/folders/1wDpyMSLHtkEFnql8VMBS_cOhDAQWYzEK
- Task 4C2 audit package: https://drive.google.com/drive/folders/1Jhr3UqcYuBsVtwB3QTfiB6U5GY0bnZU3
- V51 checkpoint: https://drive.google.com/drive/folders/1Dldksm1BERKDqNXUzLVrlNmLHBN5SvEy
- V52 Task 2 raw external audit: https://drive.google.com/drive/folders/1PGUdYDf8b4YsV50QC_U5NOiYgPpUKUjx

## GitHub documents migrated directly

### Project-level
- `README.md`
- `docs/PROJECT_STATUS_2026-08-27.md`
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
