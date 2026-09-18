# COMMANDS (exact, in order)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Runtime: `PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
MKL_NUM_THREADS=1`, single thread, CPU, repo at
`/mnt/c/Users/MDP/dev/llmzip-work/parallel_ideas_r1/inverse_repair`.
READ-ONLY: `../inverse`, model dir, fixtures. WRITE-ONLY here.

1. `ACCEPT_LIB=original python3 test_acceptance.py > test_acceptance_RED.log 2>&1`
   (before-repair acceptance: 6 failures — identity/affine/segment/FD/Newton.)
2. `cp ../inverse/inverse_lib.py inverse_lib_fixed.py`
   `cp ../inverse/run.py run_fixed.py` (byte copies, then minimal edits per
   PROTOCOL_DELTA.md).
3. `ACCEPT_LIB=fixed python3 test_acceptance.py > test_acceptance_GREEN.log 2>&1`
   (11/11 OK after fix; linearity test branches on ACCEPT_LIB.)
4. `python3 test_mutation.py > test_mutation.log 2>&1`
   (restored-identity mutations in both paths fail correctness as required.)
5. `python3 run_fixed.py` (SAME 12+4 grid; writes per_case.jsonl,
   continuation.json, segment.json, summary.json, *.npz,
   source_hashes_fixed.json HERE, never ../inverse.)
6. `python3 replay_independent.py` (→ replay_residual.json, verdict MATCH.)
7. `python3 reconcile_ledger.py` (→ ledger_storage_reconciled.json.)
8. `python3 kv_continuation.py` (→ kv_continuation.json, 4/4 tested.)

Budgets/tolerances/x0/layers/texts/segments unchanged; no 40×100 run.
