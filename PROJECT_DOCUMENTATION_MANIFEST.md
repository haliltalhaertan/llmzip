# Project Documentation Manifest

Snapshot date: 2026-08-27

This index enumerates the documentation-oriented snapshot assembled from the canonical Google Drive project archive. Large raw datasets and large raw trial tables are intentionally excluded from Git and are indexed separately.

The complete documentation snapshot is committed as `archives/LLMZIP_PROJECT_DOCUMENTATION_SNAPSHOT_2026-08-27.zip`. It contains 104 files including the V51 master checkpoint, V1–V50 compact summaries, frozen/recovered scripts, V52 Task 2/3/4C1/4C2 reports and manifests, current compute/audit prompts, literature review, and recovery records.

## Canonical Drive archive

- Master project folder: https://drive.google.com/drive/folders/1uM2bLBC3XQmvbdkTpjhvR6_N6OO7Qyxv
- Prompt archive: https://drive.google.com/drive/folders/1kLISFbGpKS0IA3MLXLqOE8cgFGiMSNX8
- Literature reviews: https://drive.google.com/drive/folders/10nFwmZTX3HbSszJCW5bnk4H_NTVz8Qhm
- Task 4C2 final outputs: https://drive.google.com/drive/folders/1wDpyMSLHtkEFnql8VMBS_cOhDAQWYzEK
- Task 4C2 audit package: https://drive.google.com/drive/folders/1Jhr3UqcYuBsVtwB3QTfiB6U5GY0bnZU3
- V51 checkpoint: https://drive.google.com/drive/folders/1Dldksm1BERKDqNXUzLVrlNmLHBN5SvEy
- V52 Task 2 raw external audit: https://drive.google.com/drive/folders/1PGUdYDf8b4YsV50QC_U5NOiYgPpUKUjx

## Snapshot inventory by area

### V51
- `LLM_MEMORY_RESEARCH_MASTER_CHECKPOINT_V51.md`
- `NEW_CHAT_START_PROMPT_V51.md`
- `LLM_MEMORY_RESEARCH_FILE_MANIFEST_V51.csv`
- `v51_protocol_manifest.json`
- `v51_full_locomo_benchmark.py`
- `v51_full_locomo_benchmark_patched_v2.py`
- `v51_full_locomo_benchmark_patched_v4.py`
- compact JSON/CSV summaries covering the V1–V50 experimental history.

### V52 Task 2
- compute report, frozen protocol, shortlist-scaling script
- compact external-audit handoff/readme, frontier, bootstrap, decomposition, and code-audit extracts.

### V52 Task 3
- `V52_T3A1_PROTOCOL_PATCH.md`.

### V52 Task 4C1
- prior-art/novelty audit
- blocked-run SHA trail.
- independent Task 4C1 audit already lives in `audit_v52_t4c1/`.

### V52 Task 4C2
- compute report and Head Researcher handoff
- pre-run seal and post-run manifest
- input checks, Task4C1 reproduction, aggregate and W/T/L tables
- archive-size, gold-cardinality, question-type, reuse strata
- bit-balance, collision, tie, feature, distance, and rank-geometry diagnostics
- same-input proof and leakage/sanity checks
- sealed compute script.

Large raw `trial_results.csv`, `question_level.csv`, packed binary-code ZIPs, and the 277 MB benchmark dataset remain in Drive and are indexed in `DATASETS_AND_LARGE_ARTIFACTS.md`.

### Prompts
- current 4C2 takeover prompt
- current 4C2 resume prompt
- Task 4C2 independent adversarial audit prompt
- historical V52 Task 2 audit prompt
- prompt master index.

### Literature / recovery
- deep binary-geometry literature review (2026-08-27)
- File Library synchronization status
- external LLM core context/audit record.

## Scope rule

Git is the canonical review surface for text documentation, code, prompts, manifests and compact diagnostics. Google Drive remains the canonical byte store for benchmark inputs and heavy raw artifacts. Frozen SHA256 values should be used for chain-of-custody verification rather than assuming that same-named files are identical.
