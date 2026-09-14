[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Campaign disclosure correction report (distribution-copy labeling)

Provenance: originals at git `84e75cc`; no measurement, datum, assertion, or
raw numeric/log artifact changed. This fix only prepends the standalone banner
above as the first line (plus one blank line) to in-scope narrative
distribution copies inside `campaign_2026_09_13/`. The banner marks campaign
distribution status; it does not change historical event provenance.

## 1. Selection rule (checker: `disclosure_fix/check_campaign_labels.py`)

Basename-only, case-insensitive, over `.md`/`.txt` under the campaign dir.
Scope = union of:

- R1 (independent audit rule): basename matches
  `report|analysis|result|summary|finding|audit|dispo|receipt|campaign|readme|overview`
- NARR_MD (narrative `.md`): basename matches
  `result|review|verification|analysis|certification|summary|disposition|inventory`
- TXT_LIKE (report-like `.txt`): basename matches `receipt|result`

Explicit exclusions (checker counts them): raw logs (`.log`,
`rerun_log.txt`, `stderr/stdout.txt`, `smoke_log.txt`, `environment.txt`,
`run.log`), machine tables/data (`.json/.csv/.npz/.npy/.pkl/.parquet`),
hash files (`HASHES*.txt`, `det_hash_*.txt`, `*.sha256`), code (`.py`),
non-narrative `.md`/`.txt`, other extensions, and `MANIFEST.sha256` itself.
Pass = exact banner bytes present within the first 40 lines.

## 2. Before / after (computed in Python by the checker)

- Before (`84e75cc` worktree): 62 in scope, 28 pass, **34 missing/nonprominent**
  (33 absent + 1 nonprominent: `pilots_round1/muse_pilot_review.md` carried the
  banner only incidentally at line 46 of 49).
- R1 subset before: 47 files, 21 pass, 26 missing — reproduces the audit.
- After: 63 in scope (this report included; it matches R1 via "REPORT" and
  carries the banner on line 1), 63 pass, 0 missing.

## 3. Modified paths (34; additive prefix only)

- campaign_2026_09_13/bench3/b3a_realtalk/report.md
- campaign_2026_09_13/bench3/b3b_fin/report.md
- campaign_2026_09_13/g3_localverify_evidence/inherited/localverify-20260912/g3/membership_execution_prep_v1_2026_09_08/README.md
- campaign_2026_09_13/g3_localverify_evidence/inherited/localverify-20260912/g3/membership_impl_v3_2026_09_07/README_IMPL_V3.md
- campaign_2026_09_13/muse_prompts/muse_prompt_audit1.md
- campaign_2026_09_13/muse_prompts/muse_prompt_audit1_cont.md
- campaign_2026_09_13/muse_prompts/muse_prompt_coldstart_review.md
- campaign_2026_09_13/muse_prompts/muse_prompt_d5_review.md
- campaign_2026_09_13/muse_prompts/muse_prompt_pilot_review.md
- campaign_2026_09_13/muse_prompts/muse_prompt_prereg_review.md
- campaign_2026_09_13/muse_prompts/muse_prompt_r2d_review.md
- campaign_2026_09_13/muse_prompts/muse_prompt_verify_receipts.md
- campaign_2026_09_13/pilots_round1/muse_pilot_review.md
- campaign_2026_09_13/pilots_round2/ROUND2_REPORT.md
- campaign_2026_09_13/pilots_round2/r2a_flip_analysis.md
- campaign_2026_09_13/pilots_round2/r2d_design_review.md
- campaign_2026_09_13/pilots_round3/missing_analyses/m2_d2multi/d2x_report.md
- campaign_2026_09_13/pilots_round3/missing_analyses/m3_c2ablation/c2x_report.md
- campaign_2026_09_13/pilots_round3/muse_sessions/c2/c2_report.md
- campaign_2026_09_13/pilots_round3/muse_sessions/d2/d2_report.md
- campaign_2026_09_13/pilots_round3/muse_sessions/d3/d3_report.md
- campaign_2026_09_13/pilots_round3/muse_sessions/d4/d4_report.md
- campaign_2026_09_13/prereg/math1/math1_report.md
- campaign_2026_09_13/prereg/math2/math2_report.md
- campaign_2026_09_13/race/CAMPAIGN.md
- campaign_2026_09_13/race/cert/cert_report.md
- campaign_2026_09_13/regen/lme/itq_crossstack_sample_result.txt
- campaign_2026_09_13/review/README_review_transfer.txt
- campaign_2026_09_13/review/ed3_docs/02_INDEPENDENT_REVIEW_PROMPT.md
- campaign_2026_09_13/scratch/lv/p1_copy_ns/README.md
- campaign_2026_09_13/scratch/lv/p1_copy_ns/task3/README.md
- campaign_2026_09_13/scratch/lv/p2_copy/itq_haar_objective_comparison_2026_09_12/LEDGER_RECEIPT_BODY.txt
- campaign_2026_09_13/scratch/lv/p2_copy/itq_haar_objective_comparison_2026_09_12/README_TR.md
- campaign_2026_09_13/scratch/t4dzip/V52_T4D_COMPUTE_REPORT.md

New files: `disclosure_fix/check_campaign_labels.py` (checker),
`disclosure_fix/DISCLOSURE_CORRECTION_REPORT.md` (this report),
`disclosure_fix/check_evidence.json` (checker JSON output).

## 4. Original-byte preservation check

For each of the 34 paths: `current_bytes == PREFIX + pristine_bytes` where
`PREFIX` is the exact banner line plus one blank line (LF, no BOM, no CR
introduced — all 34 originals were LF with no BOM) and `pristine_bytes` is
`git show 84e75cc:<path>`. Stripping only the added prefix reproduces the
pristine bytes exactly. No partial warning was deleted; no scientific
assertion rewritten. Frozen originals outside `campaign_2026_09_13/` untouched;
raw `.log`, machine tables (`.json/.csv`), code, and raw numeric evidence
unchanged.

## 5. Embedded-manifest caveat (distribution copy vs original receipt)

Five modified copies are also referenced by hash inside historical embedded
manifests, which are deliberately left untouched (never rehashed):

- `scratch/lv/p2_copy/itq_haar_objective_comparison_2026_09_12/FILE_HASHES.json`
  embeds sha256+bytes of `LEDGER_RECEIPT_BODY.txt` and `README_TR.md`
- `scratch/t4dzip/V52_T4D_POST_RUN_MANIFEST.json` (`atomic_output_hashes`)
  embeds sha256 of `V52_T4D_COMPUTE_REPORT.md`
- `scratch/lv/p1_copy_ns/task3/HASHES.json` embeds sha256+bytes of `README.md`
  (same directory)
- `g3_localverify_evidence/inherited/localverify-20260912/provenance/MATERIALIZED.json`
  and `g3_localverify_evidence/provenance/localverify-20260912/MATERIALIZED.json`
  embed sha256+bytes of the `README_IMPL_V3.md` source blob

Entries for these files in the manifests above no longer match the labeled
distribution copies. Pristine provenance remains accessible at parent commit
`84e75cc` (`git show 84e75cc:<path>` reproduces the hashed bytes exactly).
No immutable/signed artifact blocked labeling; nothing was flagged untouchable.

## 6. Manifest

Only `campaign_2026_09_13/MANIFEST.sha256` was refreshed (same
`{sha256}  {root-relative path}` LF convention, case-insensitive path sort
matching the original file): 581 entries
covering every other campaign file exactly once, including the 3 new
`disclosure_fix/` files. Verified with `sha256sum -c` (all OK), uniqueness,
and full-coverage checks.
