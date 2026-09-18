# STATUS 08_storage_contracts — HARD REVIEW R2

Role: audit static-storage and rank/membership contracts for mathematical/cost correctness.
Mode: read-only source; outputs only in this dir. No exploit construction.

## Phases
- [x] P0 init: read REFS_BEFORE, ROUND_PLAN, prompt; create STATUS.md
- [x] P1 inventory: branch stats/diffs for 9802b49, 5ff0ab0, 35b50581, dbb3ee0, 8ed1351, 6e764b1; none merged to main (merge-base verified)
- [x] P2 denominator/copy/physical-vs-logical audit: probe_denom.py 7/7 PASS; pins PIN-OK x2; inlined math 5/5 IDENTICAL; same-id refusal path NOT located (NOT RUN)
- [x] P3 certificate inequalities + acceptance: probe_rankcert.py 5/5 PASS (v2 bug reproduced, v3 VARIES/scale/robustness); validator independence verified; 0 obligations closed by acceptance
- [x] P4 sampled-vs-exhaustive: finite-sample evidence itemized; no general proof; different-family review open
- [x] P5 REPORT.md + COVERAGE.csv (35 rows: 21 verified / 5 sampled / 9 NOT RUN) + evidence.json + probe outputs

## Constraints
- compute.sh for heavy jobs; one probe <=180s; finish <40min, reserve 5min for report.
- Mechanically counted rows; never present not-run as pass.

## Log
- 2026-09-17 init.
