[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# STATUS — exact-rational binding-8 verification pilot (PREPARED, NOT ACCEPTED)
Namespace: `research_exact_rational_verification_2026_09_14/`
Branch (VERIFIED via `git branch --show-current` this session): `muse/fix-exact-rational`
Base (RELAYED from task text): `5ec3db60c03edde490374bf9cd7c3e56dd6bcd00`
Role: PREPARED, NOT ACCEPTED. Independent-auditor requirements NOT met by this run (author is not independent; see DISPOSITION.md when written).

## Plan
- [x] STATUS.md written
- [x] DELIVER 1: BINDING8_READING.md (verbatim quotes + restatement)
- [x] DELIVER 2: vendored copy of implementation + provenance note
- [x] DELIVER 3: ADVERSARIAL_TESTS.md + test_exact_rational.py + evidence/results.json (synthetic only) — 31/31 pass, exit 0
- [x] DELIVER 4: DISPOSITION.md (SATISFIED on synthetics; NOT discharged)
- [x] REPORT.md written; committing namespace to own branch

## Seal compliance log
- No `--mode run`/`finalize`; no `run_archives`/`evaluate_archive`/`finalize_results`; no HMAC key; no real IDs/distances/metrics/recall; no corpora/queries/gold/evidence/embeddings opened (to be re-confirmed at finish).
- Additive-only: all writes inside namespace. No existing file touched.
- Synthetic inputs only, authored by me, using fractions.Fraction oracle.

## Receipts
- `git branch --show-current` → `muse/fix-exact-rational` (VERIFIED 2026-09-14 session output).
- Base identity for commit (VERIFIED via `git log -1 --format='%an <%ae>' 5ec3db60`): `Codex <codex@openai.com>`.
