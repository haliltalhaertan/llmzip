# STATUS.md — 02_itq (HARD REVIEW ROUND 2)

Role: Audit ITQ vs rotation rigorously.
Started: 2026-09-17 UTC. Finished: 2026-09-17 UTC, within 40-min budget.
Machine: same-CLI partial independence (disclosed).

## Phase checkpoints
- [x] P0 init: STATUS.md created, REFS_BEFORE read, env located (`~/muse-work/ml-python` = wrapper for /usr/bin/python3; 3.14.4/numpy 2.5.3/scipy 1.18.1/sklearn 1.9.1)
- [x] P1 protocol recovery: quant_math arms/ties/sigma/bootstrap + codex Haar objective scope + published-pilot byte-identity + prior-audit flaws cited (au_c1_itq.py:11-15, HARD_AUDIT_CLAIMS.md:29-32)
- [x] P2 baseline gates: 90/90 FULL per-archive exact (maxdiff 0.0); 36/36 tie-equivalence; published single-fit contrasts verified
- [x] P3 five ITQ inits + paired same-seed RANDs, identical ties/pipeline: RT full cohort 5/5 negative on qscale; PQ 5-arch subset mixed null; 75/75 losses decreased; 330 rows persisted
- [x] P4 REPORT.md + COVERAGE.csv (637 reviewed / 25 NOT RUN, mechanically summed) + evidence_itq.json + scripts/outputs

## Budget / constraint notes
- `compute.sh` unusable as-is in sandbox: lock path outside writable root (RC=73) and `timeout(1)` denied exec (RC=126). Used `compute_local.sh` (flock-only, same env + 180s budget discipline; probes 9.7s + 6.4s). Cross-agent serialization best-effort — disclosed in REPORT.md.
- NO FULL COHORT claim for PerLTQA/overall: deterministic 5-archive subset (first 5 alphabetical), documented in REPORT.md + COVERAGE.csv.
- No refs checked out/fetched/committed/pushed; `git show` reads only. Originals copied before execution with sha256 logged in REPORT.md.
