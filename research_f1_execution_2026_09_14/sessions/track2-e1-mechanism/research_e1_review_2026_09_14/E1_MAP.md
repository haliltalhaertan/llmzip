[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# E1_MAP — what each E1 branch is, and which supersedes which

Work is PREPARED, NOT ACCEPTED. Nothing here is sealed, ratified, or closed.
Locator convention: `origin/<branch>:<path>` for branch content; bare `path:line`
for files in this namespace. VERIFIED = I ran/read the bytes. CLAIM = a document
says it. RELAYED = second-hand.

## The ten refs are eight commits

`git for-each-ref` output (VERIFIED, run 2026-09-14) shows 10 refs sharing shas pairwise:

| # | ref (`origin/…`) | sha | commit date (iso) | subject |
|---|---|---|---|---|
| 1 | `research/e1-sign-float-mechanism-2026-09-13` | `3444fa9` | 2026-09-13 15:37:31 +0300 | research(e1): restore exact bridge report bytes |
| 2 | `research/e1-sign-float-mechanism-frozen-2026-09-13` | `d1e429c` | 2026-09-13 15:38:41 +0300 | research(e1): freeze bridge and mechanism pre-analysis package |
| 3 | `research/e1-sign-float-mechanism-v2-2026-09-13` | `775a09c` | 2026-09-13 15:48:16 +0300 | research(e1): record V2 synthetic metric check |
| 4 | `research/e1-sign-float-mechanism-v2-frozen-2026-09-13` | `775a09c` | (same commit as 3) | (same) |
| 5 | `research/e1-mechanism-checkpoint-frozen-2026-09-13` | `4bfdb82` | 2026-09-13 16:23:49 +0300 | research(e1): freeze mechanism checkpoint synthesis |
| 6 | `research/e1-lme-secondary-run-2026-09-13` | `4bfdb82` | (same commit as 5) | (same) |
| 7 | `research/e1-v2-raw-cache-recovery-2026-09-13` | `d544169` | 2026-09-13 19:07:25 +0300 | research(e1): recover frozen C96 mechanism surfaces from SHA-bound backup |
| 8 | `research/e1-v2-raw-cache-recovery-r2-2026-09-13` | `d5edeb3` | 2026-09-13 20:45:38 +0300 | research(e1-v2): add exact R2 raw-cache rerun prompt |
| 9 | `audit/e1-mechanism-checkpoint-independent-2026-09-13` | `ec40dc3` | 2026-09-13 18:25:44 +0300 | audit(e1): publish independent checkpoint verdict |
| 10 | `audit/e1-v2-raw-cache-recovery-independent-2026-09-13` | `010bcbb` | 2026-09-13 20:17:49 +0300 | audit(e1-v2): independent raw-cache recovery verdict |

New-file counts vs main `5ec3db60` (VERIFIED, `git diff --name-only … | wc -l`):
551 / 554 / 560 / 560 / 593 / 593 / 599 / 604 / 609 / 601 — in the order above.

## What each branch IS (read the spine docs first, code second)

- **#1 v1 (`3444fa9`, 551 files).** Bridge-pattern discovery package. Core document:
  `origin/research/e1-sign-float-mechanism-2026-09-13:campaign_2026_09_13/e1_mechanism/E1_BRIDGE_REPORT.md`
  (66 lines, VERIFIED read). It publishes the 6/6 sign-concordance table (SIGN−float vs
  BOT−TOP across LME / REALTALK / 4 PerLTQA sections) and the first verbal mechanism
  hypothesis ("SIGN helps when lower-variance coordinates carry the discrimination").
  Bulk of the 551 files is inherited campaign material (`g3_localverify_evidence`,
  `bench3`, `audits/audit1`, pilots, race) — context, not new E1 science.
- **#2 v1-frozen (`d1e429c`, 554 files).** v1 plus the frozen design: exactly 3 files added
  (VERIFIED, pairwise `git diff --name-only` #1→#2):
  `campaign_2026_09_13/e1_mechanism/E1_PREANALYSIS_SPEC.md`,
  `campaign_2026_09_13/e1_mechanism/HASHES.json`, `…/HASHES.json.sha256`.
  The SPEC is the variance-heterogeneity test design (Delta_q vs P64_q, VAR_CV, EFF_COORD…).
- **#3/#4 v2 and v2-frozen (`775a09c`, 560 files).** v1-frozen plus the V2 refinement, 9 files
  (VERIFIED #1→#3 diff filtered to non-inherited paths):
  `E1_PREANALYSIS_SPEC_V2.md`, `E1_V1_DISPOSITION.md`, `E1_V2_TEST_RECEIPT.md`,
  `LME_PREEXISTING_REDUNDANCY_CHECK.json`, `e1_geometry_core_v2.py`,
  `test_e1_geometry_core_v2.py`, updated SPEC/HASHES. The disposition (CLAIM, read in full)
  says the V1 verbal mechanism was already contradicted pre-run by round-1 LME evidence and
  re-licenses E1 as a *joint-geometry* (redundancy/tie-competition) test. The receipt records
  only a synthetic-matrix metric check (no benchmark outcomes).
- **#5/#6 checkpoint-frozen and lme-secondary (`4bfdb82`, 593 files).** v2 plus the executed
  checkpoint: 10 GitHub workflows (`e1_*`), 10 analysis scripts (`e1_lme_*`, `e1_perltqa_*`,
  `e1_realtalk_*`, `e1_regime_decompose.py`), 11 result JSONs, `E1_LME_SECONDARY_REPORT.md`,
  `E1_MECHANISM_CHECKPOINT.md` (VERIFIED: independent audit at `ec40dc3` confirms "33 added
  files… 10 workflows, 10 scripts, 11 result JSONs" plus the two reports —
  `origin/audit/e1-mechanism-checkpoint-independent-2026-09-13:audit_e1_mechanism_checkpoint_2026_09_13/INDEPENDENT_E1_AUDIT_REPORT.md`,
  §1, CLAIM corroborating my file listing).
- **#7 raw-cache recovery (`d544169`, 599 files).** Checkpoint plus
  `campaign_2026_09_13/e1_v2_raw_recovery_2026_09_13/` (report + disposition) executing the
  frozen V2 metrics on SHA-bound recovered C96/qC caches (470 LME, 10 LoCoMo, 10 REALTALK,
  30-archive + 8,265-query PerLTQA). Parent is `4bfdb82` (CLAIM in the recovery report;
  corroborated by the audit's "parent `4bfdb82…`, one additive commit", VERIFIED as stated
  in `origin/audit/e1-v2-raw-cache-recovery-independent-2026-09-13:…/INDEPENDENT_E1_V2_RAW_AUDIT_REPORT.md` §Integrity).
- **#8 r2 (`d5edeb3`, 604 files).** Recovery plus exactly 5 files (VERIFIED pairwise diff):
  `campaign_2026_09_13/e1_v2_raw_recovery_r2_2026_09_13/` with `AUDIT_FINDINGS_DISPOSITION_R2.md`,
  `E1_V2_RAW_CACHE_RECOVERY_REPORT_R2.md`, `E1_V2_COMPETITION_CORRECTED_RESULT.json`,
  `R2_COMPETITION_RERUN_CONTRACT.md`, `R2_EXECUTOR_PROMPT.md`. Accepts the audit's HIGH
  finding (min-gold bug), publishes corrected Claim-D coefficients from the audit's rows,
  and freezes the rerun contract. Full corrected payload + re-audit still pending (CLAIM,
  R2 report status line).
- **#9 checkpoint audit (`ec40dc3`, 601 files).** Independent rerun of all 10 checkpoint
  scripts + byte-gate checks. Verdict: **PASS_WITH_FINDINGS** (CLAIM, audit report §Verdict;
  I read §§1–7 in full). Raw-cache V2 metrics explicitly NOT_RUN/NOT_AVAILABLE in its
  environment (CLAIM, §6).
- **#10 raw-cache audit (`010bcbb`, 609 files).** Independent recomputation from the
  SHA-bound archives. Verdict: **REQUEST_CHANGES** on one HIGH finding — the lead's
  competition metric collapsed multi-gold queries to min-gold instead of the frozen per-gold
  D2 aggregation (CLAIM, audit report §§D, Required-changes; I read it in full). Everything
  else (gates, P64, PHI/EFFDIM/DUP, non-competition rows) matched exactly (CLAIM, §Lead cross-check).

## Dependency ordering (which supersedes which)

```
#1 v1 (3444fa9, 15:37)
 └─> #2 v1-frozen (d1e429c, 15:38)  SUPERSEDES #1 as design (adds SPEC/HASHES)
       └─> #3/#4 v2 = v2-frozen (775a09c, 15:48)  SUPERSEDES #2 as design (V1 disposition + V2 spec)
             └─> #5/#6 checkpoint = lme-secondary (4bfdb82, 16:23)  SUPERSEDES #3 as evidence
                   ├─> #9 checkpoint audit (ec40dc3, 18:25): PASS_WITH_FINDINGS on #5
                   └─> #7 raw-cache recovery (d544169, 19:07)  SUPERSEDES #5 as evidence (V2 metrics run)
                         ├─> #10 raw-cache audit (010bcbb, 20:17): REQUEST_CHANGES on #7 (Claim D bug)
                         └─> #8 r2 (d5edeb3, 20:45)  SUPERSEDES #7 on Claim D wording/contract;
                              full rerun + re-audit PENDING — #8 is the current tip, not a PASS.
```

Supersede rule used: a branch supersedes another when its own documents declare the
predecessor's design/numbers superseded *and* it adds the replacing artifact. R2 does not
yet supersede the audit's corrected rows with lead-produced rows — that rerun is unexecuted
(CLAIM, `R2_COMPETITION_RERUN_CONTRACT.md` status: "NOT YET EXECUTED BY LEAD").

## Frozen twins at identical shas — bookkeeping finding (VERIFIED)

- `e1-sign-float-mechanism-v2-2026-09-13` vs `…-v2-frozen-2026-09-13`: `git diff --name-only`
  between the two refs is **empty**; both resolve to `775a09c` (VERIFIED).
- `e1-mechanism-checkpoint-frozen-2026-09-13` vs `e1-lme-secondary-run-2026-09-13`:
  `git diff --name-only` is **empty**; both resolve to `4bfdb82` (VERIFIED).

FINDING: two of the "ten branches" are pure alias pairs — same commit under a working name
and a `-frozen` name. That is benign freeze-by-extra-ref bookkeeping, but it means the line
is **8 commits, not 10 lines of work**, and any file-count or "independent replication"
narrative must not double-count the twins. v1 vs v1-frozen is by contrast a real (3-file)
step, so "frozen" does not consistently mean "identical" in this line's naming.
