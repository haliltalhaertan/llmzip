# PUSH PLAN (draft) — how to land this session's Task1 completion, when the Head Researcher decides

**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

**Nothing here has been pushed. Repository state is untouched (`main` @ 5ec3db6; no new commits,
no new branches in the repo).** All deliverables live under `C:/Users/MDP/dev/llmzip-work/`.

## Suggested landing (reviewed by the Head Researcher first)

Recommended branch: `research/v52-task1-completion-2026-09-12` (off current `main`), then PR — or a
single push to the research branch if that is the convention at landing time.

Suggested destination paths inside the repo (programme conventions):

```
research/v52/preseal_diagnostics_2026_09_12/task1_extension/
   TASK1_EXTENSION_README.md              <- from llmzip-work/TASK1_COMPLETION_RECEIPT.md
   task1_RESULTS_extended.json            <- from regen/task1_RESULTS_extended.json
   task1_extension_lme.json, .csv         <- from regen/lme/
   certification_report.json              <- from regen/lme/
   code_certification_sign.json           <- from regen/lme/
   code_certification_itq.json            <- from regen/lme/  (when complete)
   task1_locoMo_stats.json                <- from regen/locomo/
   counts_report.json                     <- from regen/locomo/
   harness/                               <- the four harness scripts (lme_regen.py,
                                             locomo_regen.py, task1_extend_lme.py,
                                             code_cert_v2.py, build_extended_results.py)
   muse_independent/                      <- regen/muse_independent/ contents
   HASHES.txt                             <- to be generated at landing (self-excluded), per convention
```

Also suggested (separate locations):
- `prompts/` or `docs/v52/` — the twelve-byte Muse audit report
  (`reports/muse_twelve_byte_audit_2026-09-12.md`), as the commissioned audit's completed result
  (it was `NOT RUN` at L-088; now run, with grades and the F1/F2/F3 notes).
- `docs/CONTINUITY_LEDGER.md` — the draft entry (`DRAFT_LEDGER_ENTRY.md`), amended and numbered at
  landing by the landing session; `ops/CURRENT_STATE.json` updated in the same commit.

## Not to be landed without a Head Researcher decision

- No changes to any sealed artifact, no Task 4F1 paths, no arm/preregistration content.
- The extended RESULTS.json is an **additive local artifact**; if landed, it should live beside (not
  replace) the frozen `task1/RESULTS.json`, whose bytes must not change.

## What is deliberately NOT included

- No Drive uploads (local-only session).
- No claims of audit status; a cold-start review remains a separate step if the programme wants one.
