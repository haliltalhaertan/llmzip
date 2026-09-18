[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Coordinator review of reproduction worker — interim

Source: repro/HARD_AUDIT_REPRO.md. Worker reports isolated T1 20/20 exact cells, T3 two-archive reproduction with 0/61056 differing sign bits, and 38/38 seal negative controls. These are worker-run tests, not a complete programme certification. F1/KV/inverse internals remain NOT REVIEWED.

## Direct source checks
- decision_tests.py lines 190–191 tests only FR@3 point difference >=2; lines 197–198 describe a CI-excluding-zero, both-benchmarks requirement. The implementation is incomplete for certification of PASS. Current negative point differences already fail a necessary condition, so adding CI cannot by itself reverse this local failure; no whole-project STOP follows.
- Snapshot rehash: 821 original files, zero changed/missing at this checkpoint.
- Package contains data/RT01.json and audit/audit_baseline_lib.py as well as coordinator/LADDER.json. Thus an absolute read pointing outside the package is NOT proof the input bytes are absent. The worker's table conflates hard-coded destinations with absent equivalents. T1 can plausibly be made portable by path repair; T2/T3 external input completeness still requires explicit inventory.
- No clean-room package-only execution was performed by the worker. Its 'package alone reproduces nothing' verdict is too broad: accept demonstrated hard-coded path/output and missing setup problems, not an executed universal failure claim. Same-machine reruns used external sources and therefore do not establish self-contained reproducibility.
- The correct T3 producer exists (ablation_r2/perltqa/t3_ladder.py); worker correctly confirms the schema match, consistent with our correction of the numbers worker.
- The current ladder script already dropped k=768; treating its full rerun as hours based on historical k=768 timing is unsupported. Preserve NOT RUN scope without that justification.

## Scientific caveats
Candidate recall remains binding at depth 50; a common reranker need not make all first-stage choices equivalent. Best-of-four BM25 is an in-sample maximum; the 3.97 pp difference from textbook parameters is an observed setting difference, NOT an estimated statistical selection-bias magnitude. Universal RealTalk delta and BM25 raw-text requirements are incorrect. Sigma-only causal explanation is unsupported for sym. Local C1 failure does not license closure of the entire research programme.

No source repair or publication performed. Consolidate with remaining claims worker before final disposition.
