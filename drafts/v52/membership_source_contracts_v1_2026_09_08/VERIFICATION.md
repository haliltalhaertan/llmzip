# Implementation-author verification (not independent audit)

Run date: 2026-09-08. Ten unittest methods PASS, 0.008 seconds reported by unittest.
Interpreter: ../locomo_reproduction_tmp_20260907/venv/Scripts/python.exe
Measured Python: 3.13.15, tags/v3.13.15:4061bc4, MSC v.1944 64 bit AMD64.
PYTHONHASHSEED=0; OMP/OPENBLAS/MKL/NUMEXPR_NUM_THREADS=1.
Only standard-library helpers are tested; no claim of numerical-stack regression.

Replay from repository root:

    <accepted-python> -B drafts/v52/membership_source_contracts_v1_2026_09_08/test_contracts.py

Coverage: replacement versus raw-only/union outputs; empty correction rejection;
missing-field fallback; out-of-cohort corrections do not select questions; partial
and total unresolved references stop; duplicate reference normalization; no input
mutation; all-source lexical ordinal versus primary-only/cohort-order outputs;
manifest-order invariance; synthetic 500/470 coverage and 47 items per shard;
invalid IDs/counts/coverage; named error surfaces; unconditional real-entry refusal.

The mutant-output comparisons are fixture discrimination checks, NOT execution of
mutated implementation modules. No claim that the prior audit findings are closed.
No real corpus, correction inventory or outcome opened. No fitting/scoring/bootstrap,
pilot, HMAC, seal, production driver or source acquisition. git diff --check passed.
