[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# STATUS — TheoryBench LongMemEval (Model-H transfer, exploratory)
- Workspace: /home/mdp/muse-work/theorybench-lme (isolated output only; sources elsewhere READ ONLY)
- Task: user-authorized exploratory benchmark test of Model-H transfer on LongMemEval (470 QA expected, native anchor 0.5419751773049645). NOT preregistered, NOT yet independently audited.
- Constraints: Muse subscription only; no model/API costs, no embeddings, no network/install, no frozen Task4F1/measurement authorization, no main/Git push.
- Protocol: /mnt/c/Users/MDP/dev/llmzip-work/theory_benchmark_test_v1/PLAN.md copied byte-exact to ./PLAN.md (sha256 a0f9e8e6eb214e0129cb5b8e31d35bdb75599eb130332a7eed7780bdc8981a21, 6402 bytes). Do NOT tune protocol after seeing new outcomes.
- Theory: math_discovery_2026_09_13/round3/all_n_ranking/{COORDINATOR_REVIEW.md,REPORT.md} — read narrowly; theoretical t not identified on real data; LOW48 proxy transfer may fail without refuting theorem; sign invariance alone is not evidence.
- Metric: fractional gold recall@3 (not any-hit). Gold is shared — no unconditional multinomial from pair averages.
- Python: /home/mdp/muse-work/ml-python -B (3.14.4/numpy 2.5.3); threads=1 env before imports; PYTHONDONTWRITEBYTECODE=1; no SVD re-embedding if caches suffice; never run historical scripts with hardcoded paths that overwrite source artifacts — copy/adapt producers into this workspace.
- Gates: reproduce ORIGINAL native SIGN96 + centered-float96 fractional R@3 with exact seed/index/tie/exclusion/weight conventions; gate BEFORE intervention; resolve cross-stack gate faithfully, no silent tolerance relaxation.
- Grid: exact t grid {0.25,0.5,1,2,4} and groups {LOW48,HIGH48,FULL96} from shared plan.
- Phase: DONE (complete first pass, ~8 min run time; well inside 25-min target).
- Gate: PASS 5/5 (max diff 1.1e-16): native MC-20 0.5419751773049645; float MC-20 0.44159574468085105; counts 470/470/0/0.
- Interventions: 7050 rows (470 QA × 3 groups × 5 t) + MC-20 at t∈{.25,1,4}; t=1 bitwise identity; sign 0 mismatches; FULL96@t4 bitwise invariant.
- Primary: LOW48 contrast -0.0644 CI [-0.0927,-0.0369] — NEGATIVE result for the proxy transfer (not a theorem refutation). HIGH48 exact mirror +0.0644 (predeclared comparison). FULL96 0.0.
- Verification: 45 checks + 24 manual recomputes PASS; bootstrap reproduced; source hashes before==after.
- Artifacts: run_lme.py, gate.json, per_query.jsonl/csv, groups.json, summary.json, REPORT.md, verification.py, receipts/{run.log,verification.log,source_hashes_after.txt}, checkpoints/, PRE_RUN.json, PLAN.md+sha256.
- Finished: 2026-09-13 UTC.
