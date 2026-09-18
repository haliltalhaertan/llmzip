# STATUS — 07_kv_inverse

Role: Audit KV continuation and inverse-memory work previously unreviewed.
Started: 2026-09-17. **COMPLETE** — final report written.

## Phase checklist
- [x] P0 setup: STATUS.md, copy originals to own dir, inventory exact searched paths
- [x] P1 read KV line: PROTOCOL/REPORT/run/tests/summary + kv_repair ERRATA/DELTA/REPORT + coordinator_kv CHECK
- [x] P2 read inverse line: PROTOCOL/REPORT/inverse_lib/run/continuation/segment + inverse_repair + coordinator_inverse
- [x] P3 read chat_literature_review_20260915/inverse REPORT + published pilot + audit_hard_r1 KV coverage
- [x] P4 git branch search (read-only, main repo object store): pickaxe 0 hits
- [x] P5 local fixtures: verify_jsons.py + verify_operators.py (direct run; compute.sh lock RO — see REPORT method note)
- [x] P6 REPORT.md + COVERAGE.csv (35 items: 26 reviewed / 3 sampled / 6 NOT RUN) + evidence JSON + scripts/outputs

## Headline
- F1 KV ΔNLL bug + F2 JVP bug: repairs mechanically verified from raw rows.
- New caveats: inverse KV-only probe is full-sequence recompute (not stepwise cache) with unmatched generic4bit scope; real DynamicCache consumption proven only in KV-predictor line.
- No resident savings anywhere; byte math exact. No model re-execution (probe budget).
