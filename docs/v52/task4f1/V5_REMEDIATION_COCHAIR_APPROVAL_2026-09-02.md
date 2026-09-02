# V52 Task 4F1 — Co-Chair Approval to Prepare V5

Date: 2026-09-02  
Role: Research Co-Chair / approval-veto reviewer  
Reviewed canonical state: `main@cae73045097eb062c4cdc636af92b350b97a95ae` (L-009)  
Predecessor co-chair review: `776c45f333b262754aa0020e8043db54942d1bea`  
Predecessor review file SHA256: `1c85eb06831db742a3c0ab8018c56ea7eb47d60f560afb68fc4a1f457fd3af55`

## Decision

`APPROVED — PREPARE V5 DECLARATIVE REMEDIATION ONLY`

L-009 correctly records the co-chair's `REQUEST CHANGES` decision, withdraws the unilateral
V4 package seal, preserves the nine V4 implementation-gate results as evidence, and keeps
Task 4F1 preregistration, execution, finalization, HMAC-key construction, real ranking, and
all retrieval-quality outcome access blocked.

The Continuity Lead may begin the single next action recorded in L-009: prepare the V5
candidate namespace and its independent-audit prompt. This approval does not authorize
preregistration or a Task 4F1 run.

## Immutable inputs and scope

- V1–V4 candidates, preflight packages, seals, manifests, audits, and acceptance records
  remain byte-for-byte historical evidence and must not be edited.
- V5 is a new namespace.
- The V5 retrieval runner must be byte-identical to the accepted V4 runner:
  `f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8`.
- The sealed Task 4F0 cohort remains 1,712 questions / 96 archives at SHA256
  `9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a`.
- No representation, method, seed, threshold, priority, metric, aggregation, checkpoint,
  finalization, or authorization behavior may change in this remediation.
- If the V5 retrieval runner hash differs, or any execution-affecting semantic change is
  discovered, stop the delta route. V5 then requires a new full cold-start audit scope and
  a new co-chair review of that expanded change.

## Operational definition of the single-source gate

The Continuity Lead's proposed strengthening is accepted. To make it auditable rather than
aspirational, V5 must include or generate a machine-readable normative-source map covering
every cross-payload load-bearing field. At minimum it must cover:

- candidate and authorization schema versions;
- candidate submission status and post-audit attestation precedence;
- V4-to-V5 runner identity;
- canary algorithm, both sign-code digests, threshold, and sign margin;
- cohort hash, eligible-question count, archive count, and excluded archives;
- dependency-lock and upstream corpus anchors;
- methods, seeds, trials, top-k, tie priority, metrics, structural-zero rule, and aggregation;
- authorization commitment state, signed fields, outcome boundary, and stop rules.

For each field the map must name exactly one authoritative path plus field/section locator.
Any repetition elsewhere must be explicitly typed as a derived mirror and must equal the
authoritative value. An unlabeled second normative source is a gate failure.

The V5 preflight and independent audit must additionally:

1. enumerate every recursively bound payload;
2. scan every bound text/JSON/Python payload for superseded V3 raw-float canary digests,
   stale V3 authorization schema labels, and any other declared deprecated literal;
3. fail if any deprecated load-bearing value survives, including in prose;
4. resolve all mirrored values through the normative-source map and fail on disagreement;
5. prove that the candidate seal records immutable status **at audit submission**, while a
   detached, hash-bound attestation is the sole authority for post-audit acceptance state;
6. prove the V5 runner hash equals the V4 runner hash exactly;
7. compare executable Python ASTs after removing docstrings and permitted schema literals,
   and identify every remaining executable difference; and
8. test the changed V5 package-preflight behavior with positive and negative fixtures.

The gate's claim is therefore not merely "no contradiction found." It is:

> Every declared load-bearing concept has one enumerated normative source; all mirrors are
> typed and equal; no superseded load-bearing literal remains in any bound payload.

## Delta-audit boundary

A cold-start independent auditor may use a delta-scoped V5 audit only after independently
establishing all of the following:

- V5 runner bytes equal V4 runner bytes;
- all retrieval-execution inputs and scientific estimand anchors are unchanged;
- the complete V4 independent-audit package and its 30/30 manifest remain authentic;
- V5 changes are limited to corrected declarative payloads, submission/attestation
  semantics, schema labels required for fail-closed identity, and package-preflight checks;
- the new single-source gate passes against the complete V5 payload closure.

The auditor must not import the Continuity Lead's conclusion that the diff is declarative;
it must derive that classification from the bytes. Failure of any condition expands the
audit to a full cold-start implementation audit or returns `BLOCKED`.

## Governance disposition

The single-writer agreement stands: the Continuity Lead alone updates
`ops/CURRENT_STATE.json` and `docs/CONTINUITY_LEDGER.md`. The co-chair records approvals and
vetoes only on a separate review branch. L-009's statement that the predecessor co-chair
review was not pushed is now known to be stale: it was already available on GitHub at
commit `776c45f333b262754aa0020e8043db54942d1bea`. The Continuity Lead should correct that
open item in the next ledger transition by binding both the predecessor review commit/file
hash and this approval commit/file hash.

No PASS transition is granted here. The next permitted stage is V5 preparation followed by
a different cold-start auditor. Task 4F1 remains `BLOCKED` and outcome access remains
`FORBIDDEN`.
