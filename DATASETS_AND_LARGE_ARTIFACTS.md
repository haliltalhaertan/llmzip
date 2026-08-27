# Datasets and Large Artifacts

These files are part of the research record but are intentionally not duplicated as ordinary Git text files because they are raw datasets, large trial tables, compressed packages, or binary diagnostic payloads.

## Canonical LongMemEval input

- `longmemeval_s_cleaned.json` — 277,383,467 bytes
  - SHA256: `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`
  - Drive: https://drive.google.com/file/d/1npoK4DuxR-Gz2zXMVwKpIsfkssZFnghI/view
- `longmemeval_s_cleaned.rar` — 53,574,473 bytes
  - Drive: https://drive.google.com/file/d/14nY-deHuK5wBPzQfJFyZB_Z-7X35Ywky/view

## V52 Task 4C2

All **compact** 4C2 artifacts are now committed under `docs/v52/task4c2/` and each one
hashes byte-exactly to its entry in `V52_T4C2_POST_RUN_MANIFEST.json` (22/25 verified,
0 mismatches). A GitHub-only auditor can therefore run the full 4C2 mechanism audit —
sealed script, seal, manifest, leakage audit, same-input status, bit balance, collisions,
ties, distance/rank geometry, strata, W/T/L — without touching Drive.

Still Drive-only (too heavy for ordinary Git text history):

- `V52_T4C2_trial_results.csv` — raw 4C2 trial table (5,371,479 bytes)
  - SHA256: `c6d58cdd6c4bfad63801a2adaec41e82a449d7dde109f02e797edfde2663d64e`
  - Drive: https://drive.google.com/file/d/1g8_vCbmA63aDOQVZvIDmxpD6leJ6TjES/view
- `V52_T4C2_BINARY_GEOMETRY.zip` — packed binary-code / geometry payload (13,012,706 bytes)
  - SHA256: `40026fe6e773c20b284e926efda6e5e72f9193b5a4c98710687e1a162913c96d`
  - Drive: https://drive.google.com/file/d/1ggaSk2TyhVVNil7UOk2Dai2UDcgIZY9r/view

Pending (compact, **should** be committed — not yet in Git):

- `V52_T4C2_same_input_proof.csv` — 22,378 bytes, per-question same-input proof
  - SHA256: `16a6c4a66be6f5cb4ac81157588c9e735cb1b31d122e83c68f14fbf77dd57e57`
  - Drive: https://drive.google.com/file/d/1mH_w-RkgtPcfPHG6qnFfx8g35zPBuMTL/view
  - Its conclusion (max abs diff = 0.0 across all 470 questions) is already captured in
    the committed `V52_T4C2_sanity_checks.csv` and `V52_T4C2_HEAD_RESEARCHER_HANDOFF.txt`.

Full bundles and the canonical final folder:

- `V52_T4C2_ALL_OUTPUTS.zip`
  - Drive: https://drive.google.com/file/d/1axb1ZQpo7bdN92blVl3eHWe3nME1mwlR/view
- canonical final artifact folder:
  - https://drive.google.com/drive/folders/1rXeSGN0__wXTYVzvJy1wVulTY0gFTUaP
- Task 4C2 audit-package copy:
  - https://drive.google.com/file/d/1XkcdVYZTOzDXxq1RMDbnVT46_biGBGxa/view

## Missing frozen adapters — OPEN GAP

`longmemeval_v52_adapter.py` and `longmemeval_v52_adapter_v2.py` are pinned by SHA256 in
both the 4C1 and 4C2 seals but are in **neither** Git nor Drive under a discoverable name.
They are small text files. Their absence is what forced the independent Task 4C1 audit to
return NOT VERIFIABLE for archive-only fitting and for the ITQ encode orientation, and it
will force the same verdict on every future audit until they are committed.

- `longmemeval_v52_adapter.py` SHA256: `0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722`
- `longmemeval_v52_adapter_v2.py` SHA256: `643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218`

## V52 Task 2

- `V52_T2_question_level.csv` — ~23.9 MB raw question-level table
  - Drive: https://drive.google.com/file/d/1d8CjM8BHEDRuEQ8HMNbOHa3LMWWl1opZ/view
- Raw Task 2 folder:
  - https://drive.google.com/drive/folders/1PGUdYDf8b4YsV50QC_U5NOiYgPpUKUjx

## V51 / recovered packages

- `LLM_MEMORY_RESEARCH_FULL_ARCHIVE_V51.zip`
  - Drive: https://drive.google.com/file/d/1hkaGKHcaq9nspssi8cH-3eKRM2sVbe84/view
- `V52_T1_COMPUTE_INPUT_BUNDLE.zip`, `locomo-audit-main.zip`, `EXTERNAL_LLM_HANDOFF_BUNDLE.zip`
  - recovery folder: https://drive.google.com/drive/folders/1jaM44E1bxVVIzh7OI6mJJO_K3E564Z7v

## Policy

Git is the canonical review surface for text documentation, code, prompts, manifests and compact diagnostics. Google Drive remains the canonical byte store for large benchmark inputs and heavy raw artifacts. Hashes in frozen manifests/seals should be used for chain-of-custody validation rather than assuming a same-named file is identical.

## Adapter recovery — search log (2026-08-27)

The frozen adapters were searched for by an independent auditor. Result: **not yet
materializable as raw bytes.** Checked and confirmed absent:

- Drive title search `longmemeval` — only the dataset `.json` / `.rar`
- Drive title search `adapter` — only unrelated `engine_adapter.py`, `adapters.py`, `adapter.py`
- Drive fullText search `fit_itq` — only 4C1/4C2 output ZIPs and a LoCoMo script
- `V52_T1_COMPUTE_INPUT_BUNDLE.zip` (35 files) — no adapter
- `LLM_MEMORY_RESEARCH_FULL_ARCHIVE_V51.zip` — no adapter
- `V52_T4C1_FINAL_CANONICAL_PACKAGE_20260826.zip` — no adapter
- `V52_T4C1_CHECKPOINT_042_FINAL_...zip` — no adapter
- `EXTERNAL_LLM_HANDOFF_BUNDLE.zip` — **NOT CHECKED**, Drive connector session expired

`recovery/FILE_LIBRARY_SYNC_STATUS_2026-08-25.md` already records both adapters under
*"Relevant File Library artifacts found, but raw bytes are not exposed by File Library
search"* — visible and searchable, but the connector returns references/snippets rather
than a downloadable byte stream. That remains the status.

Do **not** reconstruct them from snippets. A reconstructed adapter would not hash to the
pinned SHA256 and would silently invalidate the seals of Tasks 4B, 4C1 and 4C2.

Next actions, in order of preference:
1. check `EXTERNAL_LLM_HANDOFF_BUNDLE.zip` (the one unchecked bundle);
2. export the raw bytes from the File Library by any route that preserves them and
   upload to the Drive research master folder;
3. verify with `python3 tools/verify_frozen_artifacts.py` and commit under `adapters/`.
