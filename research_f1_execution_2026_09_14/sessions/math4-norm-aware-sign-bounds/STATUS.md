# STATUS.md — math4 norm-aware sign bounds

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## Current status (updated live)

- 2026-09-13 ~21:55 UTC: started. Mandatory context read (3 coordinator reviews + LME witness JSON + mapping REPORT skim).
- Plan: ONE result — sharp sign-pattern cosine extrema (open-boundary correct) + one scalar-tightened margin certificate. Stdlib Fraction math + numpy cross-check only.
- Constraints honored: workspace-only writes under this dir; old sources read-only; no sweeps/new arms; no push; no Task4F1 measurement; no installs/network/model APIs.

## Governing corrections applied

- LME15745da0 t4: gold dot 1.02997959496 < rival 1.04672119662 yet gold cosine .54573812 > rival .53902568 — numerator alone does NOT explain the flip; norms essential.
- t-vs-t² alone does not explain opposite Model-H dominance (monotone reparameterization keeps crossover in exact toy).
- Query magnitude NOT a proved nuisance label. +12pp LoCoMo claim retracted (same-cache MC diff +6.82838pp only). No literature novelty claim.

## Deliverables

- [ ] STATUS.md (this file)
- [ ] verify.py (exact rational checks + independent second formulation + seeded false variant)
- [ ] results.json (observed run output)
- [ ] REPORT.md (theorem / witness / conjecture / illustration separated)
- [ ] checker (fold into verify.py second route; separate file only if budget allows)

## Verification log

- `PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /home/mdp/muse-work/ml-python -B verify.py` → **272/272 checks passed**, exit 0, wrote `results.json` (exec-6). First run (exec-5) caught 3 worker-side errors (checker sign typo, wrong flip pattern, bisection bracket outside feasible range); fixed, re-greened.
- Negative-control probe (exec-7): naive closed membership `True` vs exact open-boundary `False`; broken Hamming claim `False`. Checker discriminates.
- Deliverables: STATUS.md ✓, verify.py ✓, results.json ✓, REPORT.md ✓. Done; honest scope in REPORT §§8–10 + Conjecture.
