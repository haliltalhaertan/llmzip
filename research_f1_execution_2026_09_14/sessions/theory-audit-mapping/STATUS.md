[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# STATUS.md — theorem-to-intervention fidelity audit (first pass)

Workspace: /home/mdp/muse-work/theory-audit-mapping (writes ONLY here).
Sources (READ ONLY): /mnt/c/Users/MDP/dev/llmzip-work/theory_benchmark_test_v1,
/mnt/c/Users/MDP/dev/llmzip-work/math_discovery_2026_09_13. No edits, no push,
no installs, no network, no new empirical arms, no Task4F1 measurement.

## State

- [x] STATUS.md written first (this file).
- [x] Read Model H all-N proof (REPORT.md + COORDINATOR_REVIEW.md).
- [x] Read shared benchmark PLAN.md.
- [x] Read sign_mechanism REPORT.md + COORDINATOR_REVIEW.md (transport correction).
- [x] Read scaling kernels of all 4 runners (joint doc+query scaling confirmed).
- [x] Read all 4 benchmark COORDINATOR_REVIEW.md files (supersede worker prose).
- [ ] Finish synthetic counterexample search (1+1-dim question open; 2+2-dim nonmonotone found).
- [x] Wrote verify.py (87/87 PASS, exit 0) + results.json (ALL-PASS).
- [x] Wrote REPORT.md with ranked error ledger (R1–R7).
- [x] Recorded source hashes (after-read; before-hash gap disclosed) + exact commands/counts.
- [ ] UNRESOLVED (budget): 1+1-dim monotonicity sweep unfinished — no claim made.

## Early evidence (all from read-only sources, not new claims)

1. Parameter mismatch (algebra, pre-execution): Model H varies document-only
   nuisance scale t with query q=(1,1,1) FIXED. All four runners scale BOTH
   document AND query group coords by t (LME run_lme.py; REALTALK
   transfer_runner.py; PerLTQA runner.py; LoCoMo run_locomo.py). Different
   mathematical parameter. Joint scaling gives numerator (a_i + t^2 b_i),
   not Model H's (a + t b)-type dot law, plus unequal doc norms.
2. Sign arm is invariant by construction under positive diagonal scaling
   (all runners assert/check it); every observed delta movement is float-arm
   movement. No new codec signal.
3. HIGH48(1/t) == LOW48(t) up to a global positive scale (cosine-invariant);
   REALTALK coordinator verified per-QA exact match (max diff 0). No
   independent evidence from HIGH48.
4. Coordinators confirm: LME -6.44pp (opposite), REALTALK -0.094pp
   (inconclusive, worker estimator bug corrected), PerLTQA +2.46pp
   (aggregate direction only; 961/8265 pointwise violations, nonmonotone
   curve, sections diverge), LoCoMo -2.58pp CONDITIONAL (float gate not met).
5. "Theorem remains true" needs scoping: all-N Model H theorem stands
   (strictness wording corrected); sign_mechanism Theorem 2(iii) transport
   numbers were WRONG (shared-gold dependence ignored) and replaced by
   coordinator-corrected values. Two code paths by one author are not
   independent review (stated in coordinator notes).

## Blockers / limits

- ~20-minute first-pass budget: partial results preferred over fabrication.
- No 'proven cause' from correlation; counterexamples are synthetic only.
- Background 1+1-dim monotonicity sweep still running; will report as
  unresolved if unfinished rather than assert.
