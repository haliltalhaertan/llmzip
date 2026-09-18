[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# V52 static-storage V10 — hardened consumption gate (concurrency repair)

Status: **REPAIR CANDIDATE / NOT INDEPENDENTLY AUDITED / NOT FROZEN / NO MEASUREMENT AUTHORIZATION**.

Parent V9: `b300cbf70b158bc075d45e4bfb8e0105a970596b`. V9/V8/V7 files are
unmodified; this directory is an additive repair layer.

## Defect (V9)

`consumption_gate_v9._exec_exact` authenticates source bytes, then executes
them while publishing dependency modules under shared `sys.modules` names
(`v8_runtime`, `v8_snapshot`). `_load_v8_exact` performs three such execs in
sequence (runtime, snapshot, gate), restoring the shared names after each
one. Two concurrent transactions therefore interleave across the global
namespace: the `import v8_runtime` / `import v8_snapshot` statements inside
the snapshot and gate sources can bind a module published by a concurrent
transaction (or any concurrent ambient publisher, of the kind V8 test setup
leaves behind). `sys.modules` is restored afterwards, so the misbinding
persists silently inside the returned module objects. Reproduced: all
exercised rejection controls bypassed (see `V10_RACE_REPRO.md`).

A per-module lock is insufficient: the shared names are released between
module executions, so the race lives in the gaps of the whole chain, not
inside any single exec.

## Repair invariant (V10)

A loading transaction shares no mutable global namespace state:

1. Dependencies are bound through a transaction-local scoped `__import__`
   served from the transaction's own dependency map; every other import
   delegates to the real importer. Nothing is published to `sys.modules`
   at any point, so concurrent publishers (foreign transactions or ambient
   writers) cannot be observed by, and cannot perturb, a transaction.
2. A process-global reentrant lock (`_CHAIN_LOCK`, `threading.RLock`) is
   held across the entire transaction: all pinned execs, dependency wiring,
   and the consuming `gate._fresh_preflight(...)` call. Reentrancy keeps
   nested V10 loads on one thread deadlock-free; the lock additionally
   serializes whole transactions.

Preserved from V9: exact-byte SHA256 authentication of the three pinned V8
sources, O_NOFOLLOW regular-file reads with stat/open identity checks,
pycache avoidance (compile+exec only; the import system is never authority
for pinned bytes), exact per-key `sys.modules` hygiene on success and
exception, no retained snapshot (`V10Context` carries paths/hashes only;
every access reruns the chain).

## Scope

LongMemEval-only. No authorization, seal, run, retrieval, model fit, or
outcome access code exists in this layer. Task4F1 remains
`SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.

## Caveats

- The repair protects consumers that enter through V10. The frozen V9 entry
  points remain vulnerable by design (frozen, documented in
  `V10_RACE_REPRO.md`); in-process callers must migrate to
  `preflight_longmemeval_v10` / `V10Context`.
- The regression harness patches `builtins.exec` to open deterministic
  rendezvous windows; it is test-only instrumentation, restored after each
  test, and is not part of the shipped loader.
- No valid end-to-end LongMemEval fixture set exists in the repo, so
  success-path consumption is verified at the genuine-gate level (loaded
  gates enforce rejection with authenticated semantics); invalid-input
  rejection is verified end-to-end through the public boundary.
