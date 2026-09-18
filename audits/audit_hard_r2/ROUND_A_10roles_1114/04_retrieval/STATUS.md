# 04_retrieval — STATUS

Role: audit comparator fairness (T1 BM25 best-of-4 vs textbook) and cascade claims
(T2 rerank dissolution incl. _rrf60, candidate recall / rerank ceiling, RRF fusion,
text/index dependencies). STOP scope: local vs project-wide.

Phase plan:
- [x] P0 setup: read REFS_BEFORE, ROUND_PLAN, pilot REPORT/FINAL_STATE/DECISION_TESTS, prior audit claims/numbers
- [x] P1 T1 fairness: tokenization x scoring grid, tie rule, denominator + query identities, in-sample selection vs preselected textbook
- [x] P2 T2 cascade: CSV row counts, method inventory incl _rrf60, level/contrast/inversion recomputation, denominator + query identities
- [x] P3 ceiling/recall: rerank_ceiling.json vs firststage RESULTS.json, 172/705 + 49/67 checks, candidate depth dependence
- [ ] P4 fusion/text deps: RRF k=60 preselection, index-only scoring vs text display/rerank storage, RealTalk-offset non-transfer
- [x] P5 REPORT.md + COVERAGE.csv + evidence JSON + scripts/outputs (COMPLETE; partials: sym-pair 328 NOT RUN, T1 rescore cited-verification, fusion pool stored-arithmetic)

Constraints: read-only sources; no checkout/commits; heavy jobs via compute.sh (<=180s each);
PYTHONDONTWRITEBYTECODE=1, single-thread BLAS; outputs only in this dir.
Started: 2026-09-17 UTC.
