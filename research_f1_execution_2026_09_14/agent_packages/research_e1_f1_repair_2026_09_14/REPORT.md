[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# REPORT — E1 F1 independent contract execution (partial, honest)

## What I produced (all inside `research_e1_f1_repair_2026_09_14/`)

- `f1_competition.py` — independent SPEC-derived implementation (geometry, per-gold primary + non-gold
  sensitivity + min-gold bug control, average-rank Spearman, headline-gate check, cluster bootstrap). Stdlib only.
- `verify_f1.py` — runnable verifier, prints PASS/FAIL/SKIP/BLOCKED. Result: **27 PASS / 0 FAIL / 1 BLOCKED**.
- `evidence/make_evidence.py`, `evidence/per_query_rows.json`, `evidence/per_query_rows.csv` (27 synthetic rows),
  `evidence/results.json` (three-reference table + synthetic demo + bootstrap intervals).
- `CONTRACT_CHECKLIST.md` (C1–C10 box-by-box), `CACHE_INVENTORY.md` (pins + absence proof),
  `F1_EXECUTION_REPORT.md` (full analysis incl. hand-oracle §3, comparison §4–§5, skeptic §6),
  `DISPOSITION.md` (still OPEN, with re-audit entry conditions), `STATUS.md`, this `REPORT.md`.

## What I verified (first-hand)

- Contract, SPEC V2, FINDINGS F1, audit report, EXECUTION_LOG, CORRECTED_RESULT, CLAIM_MATRIX, auditor
  `competition_variants.py` — all read in full from branch bytes.
- My implementation vs hand arithmetic: exact (A1–A9, B1–B2); vs scipy Spearman: maxdiff 5.6e-17 (B6);
  single-gold theorem over 300 randomized 96-D trials (A9); bootstrap determinism + invalid ledger (C3–C5).
- Three-reference pin consistency to full precision across five branch sources (D1–D5) + R1-prose rounding (D6).
- Bug deliberately reproduced: correct vs min-gold gaps differ on multi-gold fixtures (A6/A7); single-gold sections
  provably hide it (D4: lead==d2 exactly in events/profile/social_relationship).
- Overlap subtlety: contract's first-64/last-64 of 96 overlap by 32 — corroborated by auditor's overlap [32].

## What I could NOT do and why

- **Real-data rerun (the blocking item): BLOCKED.** The three tarballs + R1 ZIP exist only on Drive; absent from
  all branches and local disk; network fetch prohibited. My eight real-data numbers are therefore
  UNAVAILABLE-UNDER-MISSING-CACHES, and every quoted Claim-D coefficient remains an auditor intermediate —
  unchanged by this execution. `DISPOSITION.md`: F1 still OPEN.
- Lead's actual R1 competition module could not be read (on no branch; Drive-only) — lead-code comparison is
  RELAYED via the auditor's recorded behavior + mismatch counts.

## Seal / discipline compliance

- Task4F1 seal: no run/finalize modes, no authorization, no BEAM material opened, no key set; E1 caches only.
- Purely additive: 10 new files in the namespace, zero modifications elsewhere; `main` untouched.
- No push; commit (below) only to the own branch.

## Local commit

sha: `d2c1e1c38ee2a8aab739df14608457685fed66a8` (namespace commit; branch `muse/ultra-f1-repair`)
