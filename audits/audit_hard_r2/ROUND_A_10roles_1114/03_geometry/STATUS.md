# 03_geometry — STATUS
Role: Audit geometry/sigma/sign-float claims and older representation/E1 theory.
Started: 2026-09-17 UTC. Budget: 40 min, reserve >=5 min for final report.

## Phase checklist
- [x] P0 setup: STATUS.md, dirs, env check
- [x] P1 inventory representation-geometry branch + standardized-float correction (file/line/commit)
- [x] P2 inventory E1 / theory_benchmark_test_v1 / representation_geometry_fix
- [x] P3 algebraic invariant probes (20/20 PASS via /home/mdp/muse-work/ml-python, direct run; compute.sh lock read-only)
- [x] P4 published-reference normalization + counterexample check (F4 label error confirmed from source)
- [x] P5 REPORT.md + COVERAGE.csv (30 rows) + evidence JSON + scripts/outputs

## Totals (mechanical)
- COVERAGE.csv: 30 rows = 20 REVIEWED + 2 SAMPLED + 2 VERIFIED-PROBE + 6 NOT RUN
- Probe: 20/20 checks PASS; sigma scan: 10 archives.

## Blockers
- compute.sh unusable (lock path read-only); used direct runs for kilobyte-scale probes. No heavy jobs run.
