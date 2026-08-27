# LLM Token Zip — File Library ↔ Google Drive Sync Status

Date: 2026-08-25
Master Drive folder: `LLM_TOKEN_ZIP_RESEARCH_MASTER`
Master folder ID: `1uM2bLBC3XQmvbdkTpjhvR6_N6OO7Qyxv`

## Already consolidated in Drive

- `LLM_Memory_Research_Checkpoint_2026-08-23_V51/`
- `LLM_Memory_Research_V52_T2_RAW_EXTERNAL_AUDIT/`
- `LLM_Memory_Research_V52_T2_External_AUDIT/` / external audit material
- `longmemeval_s_cleaned.json` — 277,383,467 bytes
- `longmemeval_s_cleaned.rar` — 53,574,473 bytes

## Recovered from File Library and added to Drive

Under `RECOVERED_FROM_FILE_LIBRARY/`:
- `EXTERNAL_LLM_CORE_CONTEXT_AND_AUDIT.md`

Under `RECOVERED_FROM_FILE_LIBRARY/01_V51_T1_RECOVERED/`:
- `V52_T1_COMPUTE_INPUT_BUNDLE.zip`
- `LLM_MEMORY_RESEARCH_FULL_ARCHIVE_V51.zip`
- `locomo-audit-main.zip`
- `EXTERNAL_LLM_HANDOFF_BUNDLE.zip`
- `v51_full_locomo_benchmark_patched_v4.py`
- `v51_full_locomo_benchmark_patched_v2.py`

Under `RECOVERED_FROM_FILE_LIBRARY/03_T3_T4_RECOVERED/`:
- `V52_T3A1_PROTOCOL_PATCH.md`

Under `RECOVERED_FROM_FILE_LIBRARY/04_T4C0_T4C1_RECOVERED/`:
- `V52_T4C1_BLOCKED_SHA256.txt`
- `V52_T4C1_PRIOR_ART_NOVELTY_AUDIT_20260825.md`

## Relevant File Library artifacts found, but raw bytes are not exposed by File Library search

These artifacts are visible/searchable in ChatGPT File Library, but the connector returns references/snippets rather than a downloadable byte stream. They were therefore NOT recreated from partial snippets, because doing so would destroy provenance and SHA integrity.

### Task 3A / 3A.1
- `V52_T3A_COMPUTE_REPORT.md`
- `V52_T3A_dataset_diagnostics.csv`
- `V52_T3A1_COMPUTE_REPORT.md`
- `V52_T3A1_question_component_map.csv`
- `V52_T3A1_memory_id_diagnostics.csv`
- `V52_T3A1_dependency_components.csv`
- `V52_T3A1_question_strata.csv`
- `longmemeval_v52_adapter.py` (v1; frozen SHA `0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722`)
- `longmemeval_v52_adapter_v2.py` (frozen SHA `643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218`)

### Task 3B
- `V52_T3B_ALL_OUTPUTS.zip`
- `V52_T3B_COMPUTE_REPORT.md`
- `V52_T3B_OUTPUT_MANIFEST.json`
- `V52_T3B_protocol.json`
- `V52_T3B_trial_results.csv`
- `V52_T3B_question_level.csv`
- Task 3B aggregate/seed/type/reuse/archive/capture/decomposition/sanity/resampling/W-T-L diagnostics
- `v52_t3b_external_validation.py`
- original pre-performance Task 3B instruction (`Yapıştırılan metin.txt`, created 2026-08-24 16:40:28)

### Task 4A
- `V52_T4A_ALL_OUTPUTS.zip`
- `V52_T4A_COMPUTE_REPORT.md`
- `V52_T4A_trial_results.csv`
- `V52_T4A_question_level.csv`
- Task 4A pre-run seal, post-run manifest, aggregate, seed, strata, rank-disagreement, warm-damage/rescue, memory-touch, sanity and leakage files
- `v52_t4a_direct_itq24.py`

### Task 4B
- `V52_T4B_COMPUTE_REPORT.md`
- `V52_T4B_PRE_RUN_SEAL.json`
- `V52_T4B_POST_RUN_MANIFEST.json`
- `V52_T4B_trial_results.csv`
- `V52_T4B_question_level.csv`
- Task 4B aggregate/seed/type/gold/archive/reuse/rank-overlap/feature-geometry/memory-touch/sanity/leakage files
- `v52_t4b_encoder_matched_controls.py`

### Task 4C0 / 4C1
- `PRIOR_ART_GUARD_V1.md`
- `PRIOR_ART_REGISTRY.csv`
- `CLAIM_NOVELTY_MAP.csv`
- `MODERN_BASELINE_FEASIBILITY.md`
- `TASK_4C1_PREREGISTRATION.md`
- `TASK_4C1_METHOD_SPECS.json`
- `TASK_4C0_COMPUTE_REPORT.md`
- `TASK_4C0_ALL_OUTPUTS.zip`
- `V52_T4C1_PRE_RUN_BLOCKER.json`
- `v52_t4c1_pre_run_guard.py`
- `V52_T4C1_COMPUTE_REPORT.md`
- `V52_T4C1_HEAD_RESEARCHER_HANDOFF.txt`

## Integrity policy

For sealed/provenance-sensitive artifacts, a partial snippet is NOT used to manufacture a replacement file. A file is copied only when its exact bytes are available in the active runtime or full text is available without truncation. This prevents a same-name but hash-different reconstruction from being mistaken for the canonical artifact.

## Next sync rule

Whenever one of the Library-only artifacts is materialized in a compute/audit chat or uploaded directly, copy its exact bytes into `LLM_TOKEN_ZIP_RESEARCH_MASTER/RECOVERED_FROM_FILE_LIBRARY/` and update this manifest.
