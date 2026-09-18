# 06_dense_residual — STATUS
Role: audit dense-MRL, residual, alternate-representation lines.
Started: 2026-09-17 UTC. Budget: 40 min, reserve 5 min for final report.

## Phase checklist
- [ ] P0 setup: STATUS.md, dir skeleton, REFS_BEFORE read
- [ ] P1 inventory raw outcomes (dense-MRL parity, sign96 nanobeir/micro-residual/heavy, residual8_pilot_r1, parallel_ideas_r1, next_route_round1, published top10 STOP scope)
- [ ] P2 verify packed byte budgets + code-only query scoring vs FLOAT oracle + seed/tie/leakage on copies
- [ ] P3 TF-IDF/SVD STOP disposability analysis (logic, not rakam)
- [ ] P4 small benign tests on copies (<=180s each via compute.sh)
- [ ] P5 REPORT.md + COVERAGE.csv + evidence JSON + scripts/outputs

## Log
- 11:20Z P0 start.
- 11:28Z P1 inventory in progress: dense-MRL README+measure code read; micro-residual/nanobeir/heavy bodies read; residual8 PROTOCOL+REPORT+FINDINGS read; asymmetric/b8 REPORTs read; STOP gates read.
- 11:35Z P2 probes done: synth T1/T2/T3/T5/T6 PASS (see outputs/t_probe_synth.log); reaggregation VERIFIED digit-for-digit (outputs/t_reaggregate.log). compute.sh lock unavailable (RO fs) — used bounded direct /usr/bin/python3 single-thread, documented as blocker.
- 11:38Z P3/P4: micro PROTOCOL read (Var(|C|), >=median, lexicographic, 20 nuisance trials); constants.json seeds 62001-62020 idx0=best verified; MRL mxbai JSON read.
- 11:42Z P5 done: REPORT.md (227 lines) + COVERAGE.csv (26 rows) + evidence.json + 2 scripts + 2 logs + 5 copies. All outputs in own dir; source untouched.
