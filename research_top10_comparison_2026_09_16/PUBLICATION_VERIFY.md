[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Publication verification — 2026-09-16

Branch `findings/top10-comparison-2026-09-15`, commit of this round.
`main` NOT touched (last verified `59b891efda7b6c06f44da7fa0ae4fe3c13f79a2e`).

## Clean-clone readback

A fresh `git clone --single-branch` of the published branch was checked against
`FILE_MANIFEST.json` (sha256 of every original file, computed before publication).

    manifest entries          756
    content-verified OK       732
    actively-being-written      3
    not tracked by git         21

**No file was lost or corrupted.**

### The 684-file scare, and what it actually was

The first readback reported 684 hash mismatches. Cause: git's `autocrlf` rewrote LF to
CRLF on checkout, so a 4011-byte file returned as 4023 bytes — 12 line endings changed,
content identical (`a.replace(CRLF,LF) == b.replace(CRLF,LF)` → True). Recording this
because a raw "684 BAD" line in a log is exactly the kind of thing that later gets
misread as data loss.

Fixed permanently by `.gitattributes` (`research_top10_comparison_2026_09_16/** -text`)
so future clones are byte-exact and the manifest verifies without normalization.

### The 3 "bad" files

`ablation_r2/lme/{ARCHIVE_CACHE.jsonl, PARTIAL_archive_results.jsonl, run_coord2.log}`

The LME channel-ablation job was **still running** when the snapshot was taken; these
files grew between hashing and commit. Expected, not corruption. The published LME
directory is therefore a **partial run** — its `REPORT.md` states this, and no LME
ablation numbers appear in the round's REPORT.md conclusions.

### The 21 "missing" files

All `.pytest_cache/` and `__pycache__/*.pyc`. Correctly ignored by git; no research
content. They are listed in the manifest only because the manifest walks the working
directory indiscriminately.

## What is NOT in this publication

- `model/` — 2.4 GB of HuggingFace `pplx-embed-v1-0.6B` weights. Excluded by size.
  Recoverable exactly: `MODEL_DOWNLOAD.json` records revision
  `2c4d510dd4a732063c31a0f70193e35067b51fd8` and the sha256 of all 14 files
  (`model.safetensors` = `2c8d2f64f8268ccd5383b7f9bea8e660349aa6a151bd68a5a47f4c129f2a4974`,
  matched against the server value at download time).
- `*.npz` — regenerable binary intermediates.
- Files over 3 MB are stored gzipped; the manifest records the sha256 of the **original
  uncompressed** bytes, and the readback decompresses before hashing.

Published size: 45.0 MB (from 2565.8 MB on disk).

## Scope of this verification

This confirms that what is on GitHub is what was on disk. It is **not** an independent
audit of the research claims, and it is not a certification. The numbers in REPORT.md
were re-derived by the coordinator from stored per-query ids; that is self-audit by a
different code path, which is weaker than an outside replication and is labelled as such
throughout.
