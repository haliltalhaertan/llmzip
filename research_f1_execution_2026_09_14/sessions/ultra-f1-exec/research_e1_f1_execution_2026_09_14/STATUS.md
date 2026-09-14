[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# STATUS — research_e1_f1_execution_2026_09_14 (F1 real-data execution)

Branch: `muse/ultra-f1-exec` (own branch; based on main `5ec3db60c03edde490374bf9cd7c3e56dd6bcd00`). VERIFIED via `git log` this session.
Task4F1 SEAL: in force. No `--mode run`, no `run_archives`/`evaluate_archive`/`finalize_results` on real data, no HMAC key, no authorization, no BEAM corpora/queries/labels/embeddings. E1/campaign caches (LME/LoCoMo/REALTALK/PerLTQA) are NOT under seal — readable per task.
Additive-only: all output inside `research_e1_f1_execution_2026_09_14/`. No existing file touched. `docs/CONTINUITY_LEDGER.md`, `ops/CURRENT_STATE.json` untouched.
Read-only on `/mnt/c/Users/MDP/dev/llmzip-work/` — never write there; read in place; copy nothing large.

## Progress receipts
- 2026-09-14: namespace created; STATUS.md written; `f1_competition.py`+`verify_f1.py` copied from `muse/ultra-f1-repair` bytes; oracle re-run in this env: 27 PASS / 0 FAIL (E0 BLOCKED is the stale absent-cache probe, superseded by real-data work). D1–D6 pin consistency re-verified live.
- FR convention recovered from branch+host code bytes (all VERIFIED reads): K=3, NT=20, fractional R@3, lexsort tie-break, seeds 5_100_000+ord*100_000+t*100+99; ord = LME lex qid ordinal / REALTALK chat ordinal / PerLTQA char ordinal / LoCoMo conv index. LME needs 500-universe ordinals -> brute-force recovery vs stored pilot FR (derived numbers only, seal-safe) with 1e-12 headline gates as independent check.
- NEXT: cache manifest + schema probe, then LME ordinal recovery + headline gates.
- Open questions: (a) exact Delta_q + headline-gate spec from frozen bytes; (b) auditor corrected full-precision pins; (c) cache manifest + structural cross-checks; (d) real-data rerun + comparison; (e) min-gold variant at scale; (f) REPORT.md + commit.

## Commit log (this namespace only)
- (none yet)
