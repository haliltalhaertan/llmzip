# V52 static-storage probe policy V2

Status: DESIGN CANDIDATE / NOT EXECUTABLE / NO MEASUREMENT AUTHORIZATION.

This is a pre-measurement response to PLANPREP-AUD-001.

Primary panel: every frozen archive gets exactly one `q=1` probe at `N=N_i`.

Secondary batch diagnostic: only the lexicographically first and last archive get `q=8` at `N=N_i`.

Staircase diagnostic: the same two sentinels get `q=1` at `N={0,1,31,32,33,63,64,65,255,256,257,1023,1024,1025}`.

Exact duplicate `(archive_id,N,q)` keys are deduplicated before plan freeze and every collision is recorded.

Maximum counts before collisions:
- LongMemEval: 470 + 2 + 28 = 500 probes, hence 1000 BEFORE/AFTER population rows.
- LoCoMo: 10 + 2 + 28 = 40 probes, hence 80 population rows.

Both fit schema-1 `MAX_ENTITIES=1024` for the population inventory. The binding marginal-storage estimand remains the full-archive add-one panel; q=8 is diagnostic only.

Every frozen point and failure must be reported. Any later point requires a new plan/hash/run and EXPLORATORY label. `N=0` is a BEFORE-snapshot diagnostic only and is never an amortization denominator.