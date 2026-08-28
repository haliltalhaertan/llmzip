# Datasets and Large Artifacts

Large datasets, raw trial tables, compressed packages, and binary diagnostic payloads remain in Google Drive. Git is the canonical review surface for code, prompts, accepted audits, governance, compact diagnostics, and provenance metadata.

## Canonical LongMemEval input

- `longmemeval_s_cleaned.json` — 277,383,467 bytes
  - SHA256: `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`
  - Drive: https://drive.google.com/file/d/1npoK4DuxR-Gz2zXMVwKpIsfkssZFnghI/view
- `longmemeval_s_cleaned.rar` — 53,574,473 bytes
  - Drive: https://drive.google.com/file/d/14nY-deHuK5wBPzQfJFyZB_Z-7X35Ywky/view

## Frozen LongMemEval adapters — RECOVERED / IN GIT

The former adapter provenance gap is closed. Exact-byte source files are committed under `adapters/`:

- `adapters/longmemeval_v52_adapter.py`
  - SHA256: `0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722`
- `adapters/longmemeval_v52_adapter_v2.py`
  - SHA256: `643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218`

The independent Task 4C2 audit verified the ITQ orientation and archive-only fitting path after recovery.

## V52 Task 4C2

Compact 4C2 artifacts are committed under `docs/v52/task4c2/`.

Drive-only heavy artifacts:

- `V52_T4C2_trial_results.csv` — 5,371,479 bytes
  - SHA256: `c6d58cdd6c4bfad63801a2adaec41e82a449d7dde109f02e797edfde2663d64e`
  - Drive: https://drive.google.com/file/d/1g8_vCbmA63aDOQVZvIDmxpD6leJ6TjES/view
- `V52_T4C2_BINARY_GEOMETRY.zip` — 13,012,706 bytes
  - SHA256: `40026fe6e773c20b284e926efda6e5e72f9193b5a4c98710687e1a162913c96d`
  - Drive: https://drive.google.com/file/d/1ggaSk2TyhVVNil7UOk2Dai2UDcgIZY9r/view
- `V52_T4C2_same_input_proof.csv` — 22,378 bytes, compact but still Drive-only
  - SHA256: `16a6c4a66be6f5cb4ac81157588c9e735cb1b31d122e83c68f14fbf77dd57e57`
  - Drive: https://drive.google.com/file/d/1mH_w-RkgtPcfPHG6qnFfx8g35zPBuMTL/view

Canonical 4C2 final folder:
https://drive.google.com/drive/folders/1rXeSGN0__wXTYVzvJy1wVulTY0gFTUaP

## V52 Task 4C3 — accepted numerical checkpoint

Canonical Drive result folder:
https://drive.google.com/drive/folders/1ABFEBsp7KfNxtIRkdaqU-6ImTFbsXAnv

Accepted independent audit is in Git under `audit_v52_t4c3/` and was merged to `main` through PR #1 with verdict `PASS WITH CONDITIONS`.

Frozen chain anchors:

- `V52_T4C3_PRE_RUN_SEAL.json`
  - SHA256: `c7cf7aa028a80464561dcc020e54a50c029935382463110bd1df0b8ae50f4a97`
  - Drive: https://drive.google.com/file/d/1aTBPjXnxl4XUJIYs6QlGgpWDPx0bZwAO/view
- `v52_t4c3_coordinate_axis_probe.py`
  - SHA256: `8dce37b1611ba6257570beea559630208f67ffb93697015e95656858a3c7d996`
  - Drive: https://drive.google.com/file/d/1Mvd54Y3LjSbZClrADOHHvVBDifses74o/view
- `V52_T4C3_POST_RUN_MANIFEST.json`
  - SHA256: `7bfeae589ffdf86012c04eec02017918cae92c3fa20a699c8d342f4baa39c00c`
  - Drive: https://drive.google.com/file/d/1DXvUT_bfks2gKlOaTZJqkfOVKi7nCMvU/view

Heavy Task 4C3 artifacts include:

- `V52_T4C3_trial_results.csv` — 21,723,081 bytes
  - Drive: https://drive.google.com/file/d/1dHAZ1wV9kem7BM87OwpW86BS6GAj3Fx3/view
- `V52_T4C3_rotated_heterogeneity.csv` — 78,405,429 bytes
  - Drive: https://drive.google.com/file/d/1sMbkfQvdH2yX3uKREb-gM37nIYh_83ko/view
- `V52_T4C3_ALL_OUTPUTS.zip` — 24,756,509 bytes
  - Drive: https://drive.google.com/file/d/1KoDZx0h88JMUfJsAgd_rUtAyeS5_3ESm/view

The independent audit re-hashed the 26 manifest-declared files in the output archive: 26/26 matched, 0 mismatches. Remaining audit condition: the full 277 MB dataset was not independently re-downloaded/re-hashed in that audit environment, although the sealed runtime input gate reports the pinned dataset hash matched.

## V52 Task 2

- `V52_T2_question_level.csv` — ~23.9 MB raw question-level table
  - Drive: https://drive.google.com/file/d/1d8CjM8BHEDRuEQ8HMNbOHa3LMWWl1opZ/view
- Raw Task 2 folder:
  - https://drive.google.com/drive/folders/1PGUdYDf8b4YsV50QC_U5NOiYgPpUKUjx

## V51 / recovered packages

- `LLM_MEMORY_RESEARCH_FULL_ARCHIVE_V51.zip`
  - Drive: https://drive.google.com/file/d/1hkaGKHcaq9nspssi8cH-3eKRM2sVbe84/view
- recovery folder:
  - https://drive.google.com/drive/folders/1jaM44E1bxVVIzh7OI6mJJO_K3E564Z7v

## Policy

Never reconstruct a frozen artifact from snippets or paraphrase. A same-named file is not canonical unless its bytes match the pinned SHA256. When a frozen artifact is moved from Drive to Git, preserve bytes exactly; do not re-serialize or normalize line endings.
