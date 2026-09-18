# REPORT 09_portability — clean-room portability audit

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Branch under audit: `findings/top10-comparison-2026-09-15` @ `e672192` (tip; REFS_BEFORE.txt line 18).
Package (READ-ONLY): `/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10/research_top10_comparison_2026_09_16`.
Own dir (only writable): `audit_hard_r2/09_portability`. Method: copy package files into
`cleanroom/` (zero symlinks, sha-verified), run with `~/muse-work/ml-python`,
`PYTHONDONTWRITEBYTECODE=1`, single-thread BLAS. No checkout/fetch/commit/push; original
manifests and sources unchanged; every output redirected here.

## Verdict (neutral, evidence-bound)

- **As-shipped, the package reproduces nothing on a stranger machine**: all four entry scripts
  hard-code `/mnt/c/Users/MDP/dev/llmzip-work` paths and there is no setup doc. Confirmed by
  execution, not assertion.
- **Refinement over the prior round**: T1 is fully salvageable with a 3-line path-only patch —
  clean-room rerun reproduces the published T1 **35/35 cells bit-identical**. T2/T3/full-ladder
  are genuinely blocked by heavy inputs absent from the package (13–45 MB, enumerated with
  sizes). So "nothing is portable" would be false; "T1 portable, T2/T3 machine-bound" is the
  measured outcome.

## Findings (severity-ranked; file/line + test + result + interpretation + limits each)

### 1. HIGH — as-shipped entry points are machine-bound; no setup docs exist

- Files/lines: `coordinator/decision_tests.py:33-38,104-110`; `coordinator/ladder.py:40-45`;
  `ablation_r2/perltqa/t3_ladder.py:19-24,235`; `coordinator/t3_perltqa_kltn.py:34-37`;
  setup-doc search over package maxdepth 2 returns no SETUP/REQUIREMENTS/INSTALL/ENVIRONMENT file.
- Test: staged package-only `cleanroom/` (copies sha-verified: decision_tests 8979bf39…,
  audit lib 673cb430…, RT01 d653e0f3…; `find cleanroom -type l` = 0) and executed each tier's
  first `open()` against stranger-equivalent relative paths.
- Result: T2 `t2()` → `FileNotFoundError` (trace captured, `outputs/T2_T3_blockers.json`);
  T3 four probed opens → `FileNotFoundError`; T1 as-shipped resolves RT+lib to absolute
  `/mnt/c/…` paths (T0 ambient run succeeds here in 3.6 s only via those ambient paths).
- Interpretation: a stranger with only the 45 MB package can run none of T1/T2/T3/ladder
  unmodified. This confirms prior-round §8 item 1 as-shipped, with the T1 refinement in §2 below.
- Limits: same-machine exercise; stranger failure is demonstrated by relative-path opens plus
  static absolute-path lines, not by a second physical machine.

### 2. HIGH (positive) — T1 is portable after an explicit 3-line path-only adaptation

- Files: adapted `cleanroom/coordinator/decision_tests_clean.py`; diff `outputs/T1_path_patch.diff`
  (exactly 3 changed lines: RT dir → `../data`, two lib loads → `../audit/audit_baseline_lib.py`;
  LADDER.json load was already HERE-relative, untouched; no numeric logic touched).
- Test: `scripts/run_t1_cleanroom.py` — runs adapted `t1()` with a guard sweeping `sys.modules`
  for any `top10_comparison_r1 / _wt_top10 / bench3 / incoming_20260916b / drive` import, then
  compares every published T1 cell with exact float diff.
- Result: **35/35 cells absdiff 0.0** (`outputs/T1_cleanroom_compare.json`): 8 BM25 variant cells,
  24 code-arm cells (6 arms × hit10/fr3/2 deltas), 2 verdict flags (C1 FAIL preserved), strongest
  variant `frozen_idfonly` (Hit@10 65.6738 / FR@3 40.0230). Elapsed 3.5 s. Deps floor: numpy
  2.5.3 / scipy 1.18.1 / sklearn 1.9.1; `sentence_transformers` absent and unneeded.
- Interpretation: T1's in-package relative equivalents are complete and byte-identical to raw
  inputs (all 10 RT JSONs + lib verified sha-identical, INPUT_INVENTORY rows 1-3). The
  portability defect for T1 is trivially fixable and the numbers reproduce exactly.
- Limits: determinism expected (no RNG in T1); rerun agreement validates the code path, not
  robustness. Bootstrap CIs for T1 are out of scope (T1 gate is point-only per prior round).

### 3. MEDIUM — T2 blocked by one 13 MB CSV with no in-package equivalent

- File/line: `decision_tests.py:34-36` RERANK_CSV; package CSV search yields only
  `inventory/literature/LIT_LEDGER.csv` and `inventory/results/ledger.csv` (neither is rerank data).
- Test: clean-room `t2()` with RERANK_CSV remapped to cleanroom-relative → `FileNotFoundError`
  at line 58 first `open()`; ambient file stat (read-only): 13,255,069 B, 164,256 data rows,
  12-column header (dataset…fr10) — so data exists, packaging omits it.
- Interpretation: T2 cannot run package-only; vendoring the CSV (or pinning its drop path + sha256)
  would unblock it — its deps are otherwise stdlib+numpy (bootstrap) only.
- Limits: T2 numbers (C3 verdicts per dataset) NOT recomputed here; inherited from
  `evidence/DECISION_TESTS_published.json`. No claim about T2 correctness is made.

### 4. MEDIUM — T3/full-ladder blocked by ~45 MB of external inputs; one absolute write target

- Files/lines: `t3_ladder.py:22-24` (BASE/ARCH_PKL/Q_PKL), `:235` absolute `json.dump(open("/mnt/c/…"))`;
  `t3_perltqa_kltn.py:37` B3; `ladder.py:42-45` (FROZEN/LIB/RT/CACHE); `audit_baseline_lib.py:30`
  (R, path-ful but `det_top10` itself path-free).
- Test: four clean-room opens → all `FileNotFoundError`; verbatim absolute lines recorded
  (`outputs/T2_T3_blockers.json`); ambient stats: perltqa 6,975,743 B, perltmem 12,988,820 B,
  arch pkl 9,439,420 B, q pkl 7,211,278 B, rt_repr dir 7,620,619 B, step2_build.py 9,275 B,
  frozen loader 63,381 B. Package walk finds zero hits for all four T3 filenames.
- Interpretation: T3/ladder are machine-bound as-shipped. Additionally `t3_ladder.py:235`
  would overwrite the RAW work-dir file on any rerun — a write-outside-package hazard worth
  fixing alongside paths (make it HERE-relative).
- Limits: T3 direction/shape NOT re-probed here (prior round's 2-archive probe stands as the
  execution evidence); model-weight arms (2.4 GB, MODEL_DOWNLOAD.json-pinned) untouched per
  no-download rule.

### 5. MEDIUM — FILE_MANIFEST.json (756 entries) covers none of the 70 decision-layer files

- Files: manifest `FILE_MANIFEST.json` (16:36 snapshot) vs workdir/Git (800 files each, 0 diff
  either way); full uncovered list `outputs/git_minus_manifest_full.txt` (70 paths) includes every
  load-bearing decision artifact: `decision_tests.py`, `LADDER.json`, `DECISION_TESTS.json`,
  `T3_PERLTQA_KLTN.json`, `ladder.py`, `t3_perltqa_kltn.py`, `t3_ladder.py`, `REFEREE.md`,
  `REPORT.md`, `FINAL_STATE.md`, `DECISION_TESTS.md`, incoming audits, lit maps.
- Test: `scripts/verify_manifest.py` — set diffs (full, mechanical) + 12-file sample: workdir-sha
  vs manifest (5/12 match; 7/12 absent-from-manifest by construction) and Git-blob vs workdir
  bytes via `git show REF:path` (**12/12 byte-equal**); gzip round-trip for 1/5 `.gz` entries
  (`ablation_r2/perltqa/per_query.jsonl`: decompressed-sha == manifest-sha, True, 16,461,495 B).
  The 26 manifest-minus-git entries decompose exactly into 21 ignored cache/pyc + 5 uncompressed
  `.jsonl` aliases of `.gz` stored files — matching PUBLICATION_VERIFY's accounting.
- Interpretation: Git faithfully stores current bytes; the manifest is a stale mid-day snapshot,
  not evidence of corruption. But integrity coverage for the decision layer — the files a
  replicator actually needs to trust — is absent. Re-running the hasher at publication time
  (keeping the root `.gitattributes` `-text` rule, verified present) closes it.
- Limits: full 756-hash re-verification NOT RUN (bounded 12-file sample + 1/5 gzip); mtimes used
  only to explain snapshot staleness, never as preregistration evidence. No hashes are presented
  as write-prevention.

### 6. LOW — procedural: shared compute.sh lock unusable; no top-10 ZIP

- `bash compute.sh …` fails with `flock: cannot open lock file …/compute.lock: Read-only file
  system` (root dir read-only; own dir writable — verified). All probes ran direct with identical
  bounds (single-thread BLAS env, ≤180 s each; observed 3-4 s). No top-10 pilot ZIP exists locally
  (only `LLMZIP_TWELVE_BYTE_PILOT_2026-09-16.zip`, a different pilot); large-file distribution
  relies on Git-stored `.gz` (5 files, 1 verified).

## Totals (mechanically counted)

- T1 cell comparisons: 35 rows, 35 exact matches (`outputs/T1_cleanroom_compare.json`).
- Manifest sample: 12 files × 2 checks = 24 + 1 gzip = 25 checks (17 match / 8 absent-from-manifest,
  0 byte-mismatches workdir↔Git).
- Input inventory: 13 rows (`INPUT_INVENTORY.csv`): 3 IN_PACKAGE, 6 MISSING_HEAVY,
  2 MISSING_OUTSIDE_PACKAGE, 1 EXCLUDED_BY_DESIGN, 1 WRITE_OUTSIDE_PACKAGE.
- Blocker probes: 2 relative opens + 1 remapped `t2()` + 4 T3 opens + 3 absolute-line greps + 6
  ambient stats, all captured (`outputs/T2_T3_blockers.json`).
- RT/lib identity: 10/10 RT JSONs + 1 lib sha-identical package-vs-raw.

## Whole-project scope remaining OUTSIDE this role

This role covers **top-10 pilot portability only**. NOT reviewed here (other roles' scope):
metric/tie-contract recomputation (01), ITQ-vs-rotation multi-seed (02), geometry/σ theory (03),
comparator fairness/cascade (04), F1 execution contracts (05), dense-MRL/residual lines (06),
KV/inverse-memory (07), storage/rank certificates (08), governance/meta coverage (10). Within the
pilot: T2/T3 numeric correctness, seed sensitivity, full-ladder rerun, model-weight arms, and
second-machine replication are NOT RUN (stated as such, never as passes).

## Artifacts

- `STATUS.md` (phased log) · `REPORT.md` (this file) · `COVERAGE.csv` · `SETUP_GAPS.md` ·
  `INPUT_INVENTORY.csv` · `outputs/T1_path_patch.diff` · `outputs/T0_ambient_T1.json` ·
  `outputs/T1_cleanroom_T1.json` · `outputs/T1_cleanroom_compare.json` ·
  `outputs/T2_T3_blockers.json` · `outputs/manifest_verify.json` ·
  `outputs/git_minus_manifest_full.txt` · `evidence/` (published DECISION_TESTS + manifest copy)
  · `scripts/` (4 rerunnable probes) · `cleanroom/` (package-only copies, no symlinks).
