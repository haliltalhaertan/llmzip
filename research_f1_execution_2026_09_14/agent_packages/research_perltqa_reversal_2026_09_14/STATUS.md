[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# STATUS — PerLTQA reversal characterisation (PREPARED, NOT ACCEPTED)

Namespace: `research_perltqa_reversal_2026_09_14/` — all output inside this directory only.
Base: `5ec3db60c03edde490374bf9cd7c3e56dd6bcd00` on own branch `muse/ultra-perltqa-mechanism` (VERIFIED: `git log -1` this session).
Seal posture: Task4F1 SEAL in force. No BEAM corpus/queries/labels/embeddings opened, fetched, or constructed. No `--mode run/finalize`, no `run_archives`/`evaluate_archive`/`finalize_results`, no HMAC key. E1/campaign caches on `origin/research/e1-*` MAY be read (explicit carve-out) — all computation below uses ONLY those caches via `git show origin/<branch>:<path>`, never checkout. VERIFIED: worktree branch unchanged throughout.
Additive-only: no existing file modified/deleted/renamed. `docs/CONTINUITY_LEDGER.md` and `ops/CURRENT_STATE.json` untouched (sole writer is Head Researcher).
Workflow choice: considered `Workflow` fan-out; proceeding INLINE in one session to keep seal/additive discipline and because the task brief prefers one decisive analysis over many shallow ones. No subagents spawned.

## Plan (todo)
1. [IN PROGRESS] Inventory E1 branches + PerLTQA caches first-hand.
2. [PENDING] Re-derive 4 section deltas + composition sum (REVERSAL_FACTS.md).
3. [PENDING] Geometry: profile vs events on SAME archive (distributions, not just means).
4. [PENDING] Falsifiable hypothesis, stated BEFORE cross-benchmark test (HYPOTHESIS.md frozen).
5. [PENDING] Adversarial test vs LongMemEval/REALTALK/LoCoMo (CROSS_BENCHMARK_TEST.md).
6. [PENDING] VERDICT.md + REPORT.md + analysis.py + evidence/results.json, then commit namespace only.

## Receipts (append continuously)
- 2026-09-14: namespace dir created; branch VERIFIED `muse/ultra-perltqa-mechanism`; base sha VERIFIED `5ec3db6`; identity for commit if needed VERIFIED `Codex <codex@openai.com>` from `git log -1 --format='%an <%ae>' 5ec3db60`; remote count VERIFIED 140 `git branch -r | wc -l` (task text says 137 — minor drift noted, not load-bearing); E1-relevant refs VERIFIED 8× `origin/research/e1-*` + 2× `origin/audit/e1-*` (task text says ten research/e1-* — observed 8; discrepancy recorded in REVERSAL_FACTS.md §6, non-load-bearing).
- 2026-09-14: PerLTQA bytes VERIFIED identical (SHA256 `ec9b8b2c…958` matches E1 claim); all 4 section deltas + composition (residual -1.15e-14) + 8 within-archive counts CONFIRMED (`REVERSAL_FACTS.md`).
- 2026-09-14: geometry distributions computed (tie_bc/gap quantiles identical-shaped across sections; gold singletons except dialogues) — vector-level properties UNAVAILABLE-UNDER-CACHE-GAP (`/tmp/b3b` pkls never committed; E1 §8 + R2 confirm V2 rows pending).
- 2026-09-14: H1 (boundary-competition density) + H0 (gold multiplicity, killed immediately) + P64 baseline FROZEN in `HYPOTHESIS.md` before xbench leg.
- 2026-09-14: xbench run — REALTALK (sha match, Delta +5.224102217719238) + LME (470/470 join, Delta +10.037943262411346) kill H1 on F1+F2+F3; LoCoMo per-query UNAVAILABLE in git (5-arm files lack FLOAT). H1 dead as regime explanation (`CROSS_BENCHMARK_TEST.md`).
- 2026-09-14: `VERDICT.md` written (closer by elimination; next decisive measurement = R2 per-query competition LEVELS by section). Evidence consolidated to `evidence/results.json` (single bundle, stdlib-only `analysis.py --parts all`).
- Seal/additive check pre-commit: no checkout performed (branch still `muse/ultra-perltqa-mechanism`); no BEAM/4F1 material touched; `git status` shows only new files under `research_perltqa_reversal_2026_09_14/`.
