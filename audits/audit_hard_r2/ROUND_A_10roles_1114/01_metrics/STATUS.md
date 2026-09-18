# 01_metrics — STATUS (HARD REVIEW ROUND 2)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Role: audit recent metric implementations and joins (tie contract, expected ties vs seeded estimates, Hit@10 vs FR@3, denominator/gold mapping, bootstrap cluster unit, CI + multiple comparisons). Cover RealTalk + ≥1 other dataset. Recompute load-bearing selected comparisons with exact source tie rules; harmless numeric fixtures for test/gate mismatch. Do NOT redo all prior 101 checks.

- Phase 0 (setup): DONE — STATUS.md created; sources inventoried.
- Phase 1 (contracts): DONE — PROTOCOL/REFEREE/DECISION_TESTS/REPORT + tie lib + decision_tests.py + firststage G6 note + lexical_summary expected-hit read.
- Phase 2 (tie/expected-ties probes): DONE — P1 fixtures separate (F1 exact-10, F2 0.7 vs 0.4 + brute oracle, F3 1.0 vs 0.25, F4 point-PASS vs CI-FAIL).
- Phase 3 (Hit@10 vs FR@3 + denominator/gold): DONE — P2 RealTalk 705 + per-archive ns + 54.75% multi-gold + tokenizer gap 10.35 Hit@10 vs 6.12 FR@3; expected-hit quantification (129/705 differ, mean corrected == det hit).
- Phase 4 (bootstrap/CI/multiplicity): DONE — P3 T2 all-3-dataset levels/ests EXACT, CIs CLOSE (seed-stable); cluster units 470x1 / 10 / 30; multiplicity 13 SIG/23 ns, no correction.
- Phase 5 (ledger + report): DONE — COVERAGE.csv (62 rows), out/evidence_metrics.json, REPORT.md.

Deviation: compute.sh unusable (lock path read-only FS); light probes ran directly with identical single-thread env. Noted in REPORT.md limits.

Deliverables in this dir: REPORT.md, COVERAGE.csv, STATUS.md, orig/, scripts/, out/.
Started/Finished: 2026-09-17 (UTC).
