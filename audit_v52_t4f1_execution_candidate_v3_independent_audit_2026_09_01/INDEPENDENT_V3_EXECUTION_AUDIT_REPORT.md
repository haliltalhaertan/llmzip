# V52 Task 4F1 — Execution Candidate V3 Cold-Start Independent Audit Report

Audit date: 2026-09-01
Role: cold-start independent implementation auditor
Repository anchor: `main` at commit `6c5459cd63443e5b58adb1b7e3391745368ffafd`
(descendant of tag `v52-4f1-v3-continuity-2026-09-01` / `40db3c5`, whose recorded
predecessor is `v52-4f1-v3-audit-handoff-2026-09-01-r2` / `e1b5731`)
Audit branch: `audit/v52-t4f1-v3-independent-2026-09-01` (isolated worktree)

## Verdict

`BLOCKED — DO NOT SEAL / DO NOT PREREGISTER / DO NOT RUN TASK 4F1`

The three V2 sealing blockers (B1, B2, B3) are correctly and durably repaired.
This audit nevertheless blocks on Gate 3: the mandated outcome-free `100K::12`
representation canary does not reproduce its pinned digests in an environment
that fully satisfies the candidate's own declared dependency lock.

## Mandatory boundary declarations

- CLI `--mode run` invocation count: `0`
- CLI `--mode finalize` invocation count: `0`
- HMAC key environment-variable set count: `0`
- valid production authorization constructed: `false`
- real retrieval ranking performed: `false`
- retrieval quality computed / read / reported: `false / false / false`
- candidate bytes modified: `false`

`finalize_results` was exercised **only** on fully synthetic fixtures authored by
this auditor (invented question IDs `SQ1`–`SQ4`, invented retrieved IDs, invented
distances and invented gold sets). It was never called on real BEAM data, and the
subprocess harness rejects any command containing `--mode run` or `--mode finalize`
before launch (self-test recorded in `COMMAND_LOG.txt`). No real retrieval ID,
distance, metric or arm outcome was computed, opened, printed, inferred or compared.

## What passed

**Gate 1 — recursive byte closure.** The candidate is exactly eight files with no
nested directory and no `__pycache__`. Runner (59,110 B), payload inventory
(1,180 B) and execution seal (6,598 B) match their declared SHA256 values byte for
byte. Payload closure is exact, the inventory-to-seal binding holds, and a nested
unbound file added to a temporary copy is rejected by the recursive preflight. The
real candidate remained byte-identical after every test.

**Gate 2 — change isolation.** Relative to V2, only `write_csv`, the new
`write_json_no_replace`, `finalize_results`, `verify_execution_seal` and `preflight`
changed. `evaluate_archive` and `verify_existing_archive` were initially flagged by a
conservative classifier; a token-level proof shows their sole delta is the
`ARCHIVE_RESULT_META_V2` → `_V3` schema literal, and they are AST-identical after
normalizing it. Representation fitting, query transformation, ranking, signed/Haar/ITQ
algorithms, seeds, thresholds, tie priority, trial generation, metric definitions and
aggregation formulas are unchanged. The schema bump additionally causes V3 to reject
stale V2-schema checkpoints, which is a defensive improvement.

**Gate 4 — B1 repaired.** Each of the four derived destinations and each of the four
corresponding `.tmp` paths blocks finalization before any byte is changed; sentinel
bytes at every tested destination and temp path were byte-identical afterwards. A
partial/crash-left derived set blocks rather than being repaired or replaced, and a
rerun after a successful finalization blocks with all outputs unchanged. Commit is
exclusive at commit time via `os.link`, not merely an early `exists()` check: a
destination created *after* the upfront check and *before* the commit still blocks,
and the racing writer's bytes survive intact.

**Gate 5 — B2 repaired.** Metrics are recomputed exactly from canonical retrieved IDs
and frozen gold. Changing retrieved IDs without changing stored metrics blocks;
changing each stored metric without changing IDs blocks; NaN, infinite and
out-of-range metrics block; duplicate, non-string, noncanonical (`"007"`), Boolean and
malformed IDs block; gold-cardinality inconsistency blocks. Zero, partial and complete
overlap, and the structural ALL@3 zero for a question with more than three gold units,
all finalize correctly when exact.

**Gate 6 — B3 repaired.** Signed-permutation control cells must carry exactly the
Native ordered top-three IDs and exact distances. Divergence in ID membership, ID order
or a single distance each block even when all stored metrics remain equal. Missing and
duplicate cells block, including a duplicate injected at constant row count. Trial
replication identity covers both IDs and distances for every method and seed, and the
Native/control question-level metric equality remains as a redundant final guard.

**Gate 7 — aggregation and schema.** 320 trial rows per eligible question, 16
question-seed rows and 4 question-method rows per question, 4 aggregate rows, fixed
denominator, equal question weighting, sorted integer Hamming distances and retained
structural zeros. Trials behave as deterministic replication identities, never as
independent statistical units.

**Gate 8 — bug hunt.** Nine substitution and bypass attempts were all blocked:
duplicate cell at constant row count, TOCTOU destination race, symlinked destination
pointing outside the namespace (target left intact), dangling-symlink destination,
stale V2-schema checkpoint, checkpoint provenance substitution, CSV mutated after the
meta stamp, cross-archive question mixing, and archive checkpoint re-write. One
earlier "no error" observation was a defect in this auditor's own test fixture — the
byte pattern never matched the CSV-quoted JSON, so nothing was mutated; the corrected
mutation is correctly blocked. That correction is recorded rather than removed.

**Authorization and leakage.** With the HMAC environment variable absent, the shipped
`RUN_AUTHORIZATION_TEMPLATE.json` and a structurally complete but unsigned fixture are
both refused. The sealed key commitment is the literal
`PENDING_HEAD_RESEARCHER_PREREGISTRATION`, so no valid authorization is constructible
without altering sealed candidate bytes. `fit_archive_representation` accepts only
`memory_texts` and contains no forbidden label token; the canary provably never calls
`rank_hamming`, `load_questions` or `metrics_at_3`.

## Why this audit blocks — Gate 3

The candidate's own `--mode preflight` **fails in this environment**, raising
`[BLOCKED - REAL ARCHIVE REPRESENTATION CANARY]`.

Diagnosis, performed outcome-free by reconstructing only the representation:

- Corpus provenance is correct. `chats/100K/12/chat.json` has git blob SHA1
  `bbabe6fcf7290e34636fe5e25c748ebefbdbbcfa`, exactly matching the accepted pinned
  tree manifest at BEAM commit `3e12035532eb85768f1a7cd779832b650c4b2ef9`.
- Structure is correct: 392 archive units, `centered96` shape `[392, 96]`, query
  shape `[1, 96]` — all as the canary expects.
- The bit-exact float digests differ:
  - observed archive digest `fae4b3c0bcc1c8dbb74a9b6867fab814ee39ed9c50fc85af56fb6bb03a8d013d`
  - pinned archive digest `25089a07760a08d816f9ae0c8af2f02b284e1217807af4d0270acbb58f580025`
- The divergence is **not** code nondeterminism: three repeat runs in this
  environment produced identical digests.
- The environment satisfies the lock exactly: Python 3.12.13, NumPy 2.3.2,
  SciPy 1.16.1, scikit-learn 1.7.1, psutil 7.0.0, with all five single-thread
  controls set. `verify_environment()` accepted it.

Root cause: `fit_archive_representation` uses `TruncatedSVD` with the randomized
solver, whose results depend on BLAS/LAPACK kernels. Holding code, data and all
locked package versions constant and varying only `OPENBLAS_CORETYPE` produced
**four distinct archive digests across six kernel dispatches** (Haswell and Zen
agree; Nehalem and Barcelona agree; SkylakeX and Sandybridge each differ), and
none equals the pinned value. `verify_environment()` passed in every variant.

The declared dependency lock pins package versions and thread counts but does not
pin the BLAS/LAPACK build or the CPU microarchitecture dispatch that actually
determine these bits. A load-bearing gate is therefore machine-bound rather than
lock-bound. Consequences if Task 4F1 were later authorized on this basis:

1. The candidate cannot pass its own preflight on conformant hardware that differs
   from the implementer's, so it cannot start.
2. Checkpoint provenance and the B3 exact top-three-plus-distance replication assume
   bit-reproducibility; a run resumed on different hardware, or after a wheel or BLAS
   refresh, would block or become non-cross-verifiable.
3. The sealed digests cannot be independently reproduced by a future auditor from the
   sealed artifacts alone, which is precisely what the chain-of-custody protocol
   requires.

This is a reproducibility and environment-binding defect in the candidate as sealed,
not merely an auditor-side environment deviation: the candidate asserts an
environment lock that is insufficient to reproduce its own pinned expectations, and
cannot detect the difference.

## Required remediation before a re-audit

1. Extend the environment lock and `verify_environment()` to bind the BLAS/LAPACK
   implementation and version and the effective CPU kernel dispatch (for example by
   pinning `OPENBLAS_CORETYPE` and recording the BLAS build), or
2. Remove bit-exact float digests as a load-bearing gate and replace them with a
   tolerance-based invariance check plus digests over quantities that are stable
   across conformant environments (for example the sign codes and integer Hamming
   distances rather than raw float matrices), and
3. Re-derive and re-seal the canary expectations under the tightened lock, then
   submit the exact bytes for a fresh cold-start audit.

Option 2 is the more robust direction: the downstream estimand depends on sign codes
and integer Hamming distances, which are far less fragile than raw float digests.

## Scope and standing

This verdict concerns only whether these exact V3 bytes may be sealed. It does not
seal, preregister, authorize, execute or interpret Task 4F1. Task 4F1 preregistration
and run remain `BLOCKED` and retrieval-quality outcome access remains `FORBIDDEN`.
No prior LLM chat, narrative or claimed verdict was accepted as evidence; every
declared hash and behaviour in this report was independently re-derived.
