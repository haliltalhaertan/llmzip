Exploratory benchmark test of Model-H transfer — PerLTQA en_v2: COMPLETE, NOT preregistered, NOT independently audited.
Independent audit: NOT YET INDEPENDENTLY AUDITED.
Preregistration: THIS IS NOT PREREGISTERED.
Muse subscription only: no model/API costs, no embeddings, no network/install. Sources read-only, unchanged (17/17 hashes match before/after). No Git push.

Gate: PASS at 1e-12 (per-QA max diff native 2.220e-16, float 1.110e-16; 0 violations; 8265 QAs / 30 archives).
Full run: 90,915 rows (8265 x 11, no subsampling). Sign invariant (0/82,650 mismatches); t=1 exact; FULL96 t=4 drift 0.0.
Primary LOW48 endpoint contrast (exact): +0.02464, bootstrap 95% CI [0.01554, 0.03443] -> 'consistent with this proxy transfer' (compatibility only).
Qualifications: aggregate curve non-monotone; 11.6% QA pointwise violations; profile section reverses (-0.186); HIGH48 is exact algebraic mirror (no independent information).
Artifacts: runner.py, gate.json, PRE_RUN.json, per_query.jsonl, run_diag.json, summary.json, REPORT.md, verification.py (32/32 PASS), receipts, ckpt_*.jsonl, PLAN.md, source_hashes_after.txt — workspace only.
