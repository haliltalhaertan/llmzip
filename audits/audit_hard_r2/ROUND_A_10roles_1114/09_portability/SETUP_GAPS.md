# SETUP_GAPS.md — what a stranger needs that the package does not supply

Source: clean-room exercise in `cleanroom/` (package files only, zero symlinks —
verified `find cleanroom -type l | wc -l` = 0; copies sha-verified against originals).
Original manifests/sources untouched; every output redirected to this dir.

## 1. No setup documentation at all (verified by search)

- `find <package> -maxdepth 2 -iname '*setup*' -o -iname '*require*' -o -iname
  '*install*' -o -iname '*environment*'` returns nothing except
  `audit/README_COUNTEREXAMPLE.txt` (a mechanism note, not setup).
- Top-level `*.md` present: COORDINATOR_NOTES, DECISION_TESTS, EXTERNAL_AUDIT3_RESPONSE,
  FINAL_STATE, LADDER_REALTALK, MODEL_DOWNLOAD, MODEL_README, MODEL_SOURCE, PROTOCOL,
  PUBLICATION_VERIFY, REPORT — none gives an environment, install, path-remapping, or
  hardware/time procedure. FINAL_STATE "Layout" lists directories only.
- The only environment hint anywhere is inside task briefs (`$HOME/muse-work/ml-python`,
  numpy/sklearn/scipy) and one code comment (`coordinator/ladder.py:56-62`: k=768 dropped
  after a 3000 s timeout). A stranger cannot derive install or runtime expectations.
- Measured dependency floor for the portable subset (T1): numpy 2.5.3, scipy 1.18.1,
  scikit-learn 1.9.1 present in `~/muse-work/ml-python`; `sentence_transformers` absent
  and NOT needed for T1 (proven: clean-room T1 ran without it). See
  `outputs/T2_T3_blockers.json` → `deps`.

## 2. Absolute machine paths (exact lines)

- `coordinator/decision_tests.py`: `W = "/mnt/c/Users/MDP/dev/llmzip-work"` (line 33);
  `RERANK_CSV`, `PERLTQA_CACHE`, `PERLTQA_Q`, `STEP2` built from `W` (lines 34-38);
  `t1()` reads `{W}/top10_comparison_r1/data` + `{W}/.../audit_baseline_lib.py` (lines ~104-110).
- `coordinator/ladder.py`: `W` (line 40); `FROZEN`, `LIB`, `RT`, `CACHE` all from `W` (lines 42-45).
- `ablation_r2/perltqa/t3_ladder.py`: `sys.path.insert(0, "/mnt/c/.../top10_comparison_r1/audit")`
  (line 19); `BASE`/`ARCH_PKL`/`Q_PKL` absolute (lines 22-24); final `json.dump(open("/mnt/c/...",
  "w"))` absolute write target (line 235).
- `coordinator/t3_perltqa_kltn.py`: `W` (line 34); `B3 = {W}/bench3/runs/b3b_perltqa` (line 37).
- `audit/audit_baseline_lib.py`: `R = "/mnt/c/Users/MDP/dev/llmzip-work"` (line 30) with
  `PERLTQA_ARCH/Q`, `LME_GLOB`, `RT_GLOB` under it — but the `det_top10` function used by T1
  is path-free (pure hashlib/numpy), which is why T1 is salvageable path-only.

## 3. Per-tier gaps

- **T1 (PORTABLE after 3-line path-only patch):** gaps were exactly the two `W`-based
  resolutions (RT dir + lib file). In-package byte-identical equivalents exist for both
  (INPUT_INVENTORY rows 1-3). Patch diff: `outputs/T1_path_patch.diff` (3 lines, comments
  marked CLEANROOM). No numeric logic touched.
- **T2 (BLOCKED):** 13.3 MB / 164,256-row CSV lives only at the absolute
  `incoming_20260916b/.../results/text_rerank_per_query.csv`; package holds no relative
  equivalent (only `inventory/*.csv` ledgers). Clean-room `t2()` raises `FileNotFoundError`
  at the first `open()` (trace in `outputs/T2_T3_blockers.json`).
- **T3 / full ladder (BLOCKED):** ~37 MB of PerLTQA JSONs + pickles plus 7.6 MB of RT repr
  caches plus two loader `.py` files, all outside the package (INPUT_INVENTORY rows 5-11).
  Clean-room opens raise `FileNotFoundError` for all four probed paths; as-shipped scripts
  embed 4-5 absolute path lines each (recorded verbatim in `outputs/T2_T3_blockers.json`).
- **Manifest gap:** `FILE_MANIFEST.json` (16:36 snapshot, 756 entries) does not cover any of
  the 70 evening decision-layer files (`coordinator/decision_tests.py`, `LADDER.json`,
  `DECISION_TESTS.json`, `T3_PERLTQA_KLTN.json`, `ladder.py`, `t3_perltqa_kltn.py`,
  `t3_ladder.py`, `REFEREE.md`, `REPORT.md`, `FINAL_STATE.md`, …). Full list:
  `outputs/git_minus_manifest_full.txt`. Git itself is faithful (workdir↔blob 12/12 byte-equal
  on samples) — the gap is manifest staleness, not corruption.
- **ZIP gap:** no top-10 pilot ZIP exists locally (only
  `LLMZIP_TWELVE_BYTE_PILOT_2026-09-16.zip`, a different pilot). The 5 files >3 MB are
  stored gzipped in Git; gunzip→sha256 verified for 1/5 samples
  (`ablation_r2/perltqa/per_query.jsonl`, match=True).

## 4. Minimal fix list (no source changes made)

1. Add `SETUP.md`: interpreter + `pip` list (numpy/scipy/sklearn floor above), path-remapping
   (one `DATA_ROOT` env var replacing `W`), per-tier commands with expected wall times
   (T1 ~4 s; T2 seconds + 20000-rep bootstrap; T3 minutes; ladder hours/k=768 caveat).
2. Replace `W = "/mnt/…"` with `os.environ.get("DATA_ROOT", HERE-relative-default)` in the four
   scripts; make `t3_ladder.py:235` write relative to `HERE`.
3. Vendor the 13 MB T2 CSV (or document its exact drop location + sha256) and either vendor or
   document-and-hash the ~45 MB T3/ladder inputs; or ship the path-only T1 as the standalone
   reproducible unit and label T2/T3 machine-bound.
4. Re-run the manifest hasher at publication time so the 70 decision-layer files are covered;
   keep the `.gitattributes` `-text` rule (it is what makes byte-exact verification possible).
