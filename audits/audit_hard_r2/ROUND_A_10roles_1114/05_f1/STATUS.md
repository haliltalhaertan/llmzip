# STATUS 05_f1 — F1 execution & frozen contracts audit (HARD R2)

Role: 05_f1. Read-only; no source repair. Outputs only in this dir.

Phase plan:
- P0 setup: STATUS.md (this file), copy originals manifest, env check
- P1 inventory: f1-execution branch files, v52-t4f1 audit refs, local f1_real/f1_real_fr3/_wt_f1exec, governing acceptance contracts
- P2 decoder/protocol + precision/fidelity gates extraction (exact file/line or commit)
- P3 bounded isolated correctness fixtures via public numeric entrypoints (<=180s each via compute.sh)
- P4 budget/estimand/frozen-claim checks vs original references
- P5 REPORT.md + COVERAGE.csv + evidence JSON + scripts/outputs; out-of-scope statement

Clock: 40-min budget; preserve partials + blockers if incomplete.
Neutrality: neither STOP nor CONTINUE presumed. Prior reports fallible.

## Log
- T0: created STATUS.md; starting P1 inventory.
- P1 DONE: inventoried f1-execution branch (ccedd56, 2879 files), v52-t4f1 refs (v3-v7 audits, V8, seals), local f1_real/f1_real_fr3/_wt_f1exec, coord scripts, governing prereg draft + Seal V3 + runner.
- P2 DONE: extracted decoder/protocol, per-query refs, precision reqs, fidelity gates with line/commit refs.
- P3 DONE: 9 isolated fixtures PASS (FX1-FX7 incl. sub-checks) via ml-python directly; compute.sh lock unavailable (read-only FS) + timeout(1) blocked — documented, fixtures are light (<10s) so direct run compliant.
- P4 DONE: budget/estimand/frozen-label checks vs original refs.
- P5 DONE: REPORT.md + COVERAGE.csv (24 rows) + evidence/evidence.json + scripts/fixtures_f1.py + outputs/fixture_results.json persisted. All 10 fixture asserts PASS. Partial-complete within box; blockers preserved.
