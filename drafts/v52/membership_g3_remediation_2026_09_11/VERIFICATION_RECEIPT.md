# G-3 delivery verification receipt

**Disposition: reviewable scoped synthetic candidate; independent audit pending.**
This receipt is implementation-team verification. It neither closes G-3 acceptance
nor declares production readiness. The candidate identity is the Git commit
containing this file; the implementation owner reports that exact commit after
commit/push verification, avoiding a self-referential commit hash here.

## Final evidence actually reproduced

| Evidence | Observed result | Receipt |
|---|---|---|
| Complete current G3 suite | **53 test methods; 5,959 subtest observations; 0 failures, 0 errors, 0 skips** | `evidence/final/RESULTS.json`, `stderr.txt`, `COMMAND.json` |
| Raw source/recovery/governance provenance | **73 checks, 0 failed** | `provenance/final/RESULTS.json`, `SOURCE_DOCUMENTS.json`, raw-blob inventories/diffs |
| Historical source regressions | Core **99** checks; runner **68**; v5 adversarial **45** plus **5** old-version controls; preparation **7** unittest methods / **433** observed assertion-method calls | `inherited/final/RESULTS.json`, per-suite stdout/stderr/metrics |
| Same inherited assertions routed to final G3 snapshot | Core **99** checks; runner **68**; adversarial **45** plus **5** old-version controls; preparation **7** methods / **433** assertion-method calls | Same receipt plus `ADAPTATIONS.json`, `ADAPTATIONS.diff` and `CURRENT_SOURCE_SNAPSHOT.json` |
| Final inherited completion and identity stability | **10 suites, all exit 0; no source drift; no launcher-script drift** | `inherited/final/RESULTS.json` and `RECEIPT.md` |
| Original source preservation | HEAD/status/index unchanged; all **11** recovered source-file hashes unchanged | `SOURCE_PRESERVATION.json` vs `RECOVERY_INPUT.json` |

These units are reported separately. A check call, unittest method, subtest,
assertion-method call and mutation variant are not interchangeable counts. The
old-version controls intentionally demonstrate historical behavior; their successes
do not claim that the historical version lacks those defects.

The current suite's runtime is exactly Python 3.13.15 / NumPy 2.3.5 / SciPy 1.17.0 /
scikit-learn 1.8.0 / pandas 2.2.3. The executable is the user-provided
`work/.venvs/g3-lock-20260912/Scripts/python.exe`. Numerical thread variables are 1
and `PYTHONHASHSEED=0`, for these child processes only. No environment packages were
installed or altered. The final delivery Python guard reports 14 allowed synthetic
data-file events and zero denied events; that is an observed scope check, not an
OS-level sandbox or proof against arbitrary native I/O.

## Discrimination, not only happy-path acceptance

- Each of the **97 fixed family members** has its own archive-zero, query-zero and
  jointly-zero negatives, under both IEEE zero signs. The all-96 member is invoked
  directly. Its failure cannot be supplied by an earlier singleton.
- **97 separate assertion-omission mutants**, one for each member, are killed by
  that member's negative. Wrong-sign, wrong-permutation and constant-bit transform
  variants are rejected by the independent expected-image checks.
- The exact adopted centered 96×96 N1 witness with zero columns 0 and 2 passes
  the original reversal/alternating aggregate canary and fails the new certificate.
- Both wrong-block redraw mutations and identity substituted for either actual
  rotation are rejected; identity is separately demonstrated to preserve norm/dot
  invariance, so the embedding check supplies the discrimination.
- Reversing priorities only in the SCALED_NATIVE arm preserves mean recall but is
  caught by the actual selector-input observer at seed 60001. It cannot pass merely
  because `_nuisance_priorities` was called once.
- The historical spoofed-Code broad-`isinstance` mutant now fails the required
  `UnsafeErrorField` assertion. Both related count-gate regressions also fail their
  positive checks when the local exact-type guard is removed/relaxed.
- Source-payload tampering and path-containment negatives are recorded under
  `provenance/negative_payload_001` and `provenance/path_controls_001`.

These are a finite set of discriminating controls, not completeness proofs.

## Recovery and development attempts are not final evidence

The recovered G3 suite was run on the requested lock **before changes**, yielding
**42 checks and exit 0**. Its raw code and output remain available in
`provenance/pre_edit`, `recovery/test_g3_remediation.py` and `recovery_baseline.txt`.
The pass did not establish Decision 2: static review and new negatives exposed the
mismatch-bit versus individual-bit distinction and missing member isolation.

`inherited/DEVELOPMENT_RUNS.md` retains the exact development chronology. Windows
audit-command-line handling and a deeply nested Git working-directory/long-path
issue were **launcher failures**, not failed candidate numeric assertions. Two
early preparation processes timed out at 180 seconds and are recorded as
incomplete/nonzero, never promoted to a pass. Global assertion profiling amplified
the repeated-Fraction cost. The launcher stopped profiling numerical libraries;
the implementation computes exact source bits once, retaining all 97 transported
comparisons. Later development runs passed but remained nonfinal when source or
launcher files changed during execution. The final run has zero such drift.

No inherited assertion was deleted, skipped, marked xfail, or weakened. Changes
are explicit import/path routing and copied G3 source dependencies, recorded in
the adaptation diff. The old preparation certificate's assertions were not
silently redefined; all seven inherited methods pass in the final snapshot, and
Decision 2 has its additional separate suite.

The staged `git diff --check` is not clean for preserved evidence: Windows CRLF
receipts and literal patch-context lines in `.diff` artifacts are reported as
whitespace. These byte-preserving recovery/source/evidence files are retained as
hashed; they are not normalized to manufacture a whitespace pass. This is separate
from the successful executable test suites and raw-byte inventory verification.

The provenance prototype initially classified the side-branch pins' absence from
HEAD ancestry as a failing expectation. The final verifier records that relation
as **false**, checks the Git query succeeded, and independently verifies the real
core → v5 → preparation chain. It does not convert a nonexistent HEAD ancestry
into a claimed true one. The older failed prototype receipt remains diagnostic
history only.

## Filesystem workflow deviation

The integration subagent prepared its two files and narrow runner changes in
`work/llmzip_g3_integration_owned_20260912` rather than directly in the requested
delivery clone. This deviated from the user's source-edit placement instruction.
The lead disclosed it, copied only the two named files, and merged only the four
named runner functions into the delivery clone while retaining the lead's record
guard. `INTEGRATION_TRANSFER.json` records input/output hashes and that boundary.
The full **53-method final suite** and inherited G3 snapshot were then run from the
delivery clone. The subagent's separate 12-test result is not used as final
integrated evidence. Neither workflow touched the original source checkout/index,
whose exact checked preservation state is recorded above.

The initial local clone attempt hit Git's dubious-ownership refusal. A single
command-scoped safe-directory exception allowed the requested local clone; no
global Git configuration was changed. The delivery's origin was then set to the
actual GitHub repository and remote main fetched. Only repo-local line-ending and
commit-author settings were written in the isolated delivery clone.

## What remains open for the user and independent reviewer

The package recommendation is **G3 successor as a scoped synthetic working line**,
not “v5 is production-conforming.” Obligation 4's synthetic integration component
is supplied. Obligation 5 remains partial: real-ingestion integration review,
independent acceptance and pre-run seal remain open. The direct historical mapping
stamp/writer/content-policy limitations are triaged in `TRACEABILITY.md` rather
than hidden or expanded into a new unrequested production project.

Real corrected LoCoMo gold with corrected/raw dual reporting, pinned actual native
anchors/cohort identity and production shard integration remain unresolved here.
No corpus access/scans, frozen outcome replay, experiment, pilot, real retrieval,
seal, finalize, HMAC or production authorization occurred. Main ledger/state,
PR #2, runtime byte-cost replay and Drive inventory remain the user's work.
