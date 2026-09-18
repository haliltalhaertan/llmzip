[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# STATUS — E1 F1 Repair Execution (independent lead-regeneration)

- Namespace: `research_e1_f1_repair_2026_09_14/`
- Base: `main 5ec3db60c03edde490374bf9cd7c3e56dd6bcd00` (VERIFIED — `git log -1` on own branch tip equals base).
- Branch: `muse/ultra-f1-repair` (own branch; VERIFIED via `git branch --show-current`. No checkout of other
  branches — all remote reads via `git show origin/<branch>:<path>`. No push.)
- Seal: Task4F1 SEAL honored throughout — no `--mode run/finalize`, no `run_archives`/`evaluate_archive`/
  `finalize_results`, no `V52_T4F1_AUTH_HMAC_KEY_HEX`, no authorization, no BEAM corpora/queries/labels/embeddings
  opened; 804MB BEAM corpus not fetched. Only E1/campaign caches referenced (all absent; documented).
- Additive-only: 10 new files in the namespace, zero existing files touched (VERIFIED via `git status --short`:
  only `?? research_e1_f1_repair_2026_09_14/` before commit).
- Progress: DONE (implementation + verification + evidence + reports). Verifier: 27 PASS / 0 FAIL / 1 BLOCKED(E0).
- Outcome: PARTIAL execution — real-data rerun BLOCKED (caches absent, no network). F1 still OPEN
  (`DISPOSITION.md`). Work is PREPARED, NOT ACCEPTED.
- Receipts: `verify_f1.py` output + `make_evidence.py` output observed in-session 2026-09-14; branch reads logged
  in `F1_EXECUTION_REPORT.md` §8 with exact `origin/<branch>:<path>` locators.
