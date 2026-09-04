# V52 Task 4F1 — V8 Single-Authority Execution Design

Date: 2026-09-04
Role: Head Researcher / Research Manager
Status: DESIGN AUTHORIZATION FOR NEXT EXECUTION CANDIDATE; NOT A RUN AUTHORIZATION

## Decision

V7 is BLOCKED. The next execution candidate SHALL NOT attempt to prove that a file is non-narrative from its filename and SHALL NOT introduce another generalized scanner.

V8 will close the packaging problem by reducing the normative execution authority to the exact accepted runner bytes.

Accepted runner SHA256:
`f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8`

The runner is already independently audited at V4 and is byte-identical through V7. V8 must preserve those bytes exactly.

## Core invariant

**There is one normative execution-code authority: the exact accepted runner bytes.**

No claim is made that some filename class is inherently "functional" or incapable of carrying prose. No package checker is asked to infer semantics from names. No scan for requirement-shaped text, hashes, literals, encodings, markup, or prose is authorized.

The V8 acceptance claim is exact-byte specific, not universal:

> The candidate binds the accepted runner at SHA256 `f96cba2c...`. The audit judges the exact submitted metadata and external-input bindings. Any change to any accepted byte produces a different candidate and voids the prior acceptance for those changed bytes.

A resealed mutation is not something the checker must classify as safe or unsafe. It is simply a different candidate requiring a fresh audit/acceptance decision.

## Candidate surface

### Normative payload

Exactly one executable artifact:

- `v52_t4f1_beam_retrieval.py` — SHA256 `f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8`

No `DEPENDENCY_LOCK.txt`, authorization template, package checker, README, execution specification, normative source map, or narrative document is part of the normative payload.

### Submission metadata

The candidate may carry minimal machine-readable submission metadata outside the normative payload, but that metadata must not restate scientific or algorithmic values except where the runner actually consumes/checks them.

Permitted metadata should be reduced to the minimum needed to bind:

- candidate schema/version;
- submission status `PREPARED_NOT_INDEPENDENTLY_AUDITED`;
- exact runner SHA256 and byte count;
- explicit run boundary `BLOCKED` / outcome access `FORBIDDEN`;
- the exact authorization-control fields the runner consumes;
- exact hashes/identities of external runtime inputs that the runner itself already checks, where provenance is useful.

Free-form rationale, protocol prose, consistency claims, acceptance claims, and restated numerical/algorithmic requirements do not belong in the candidate metadata.

## External runtime inputs

The following are not V8 normative payload files merely because the runner consumes them. They are external inputs with identities/checks defined by the runner bytes.

### Dependency lock

The accepted runner hard-codes:

`EXPECTED_DEPENDENCY_LOCK_SHA256 = 86a4db447ea3f9403231f53556be19ed07763c6e2eb0de42c83807505066655e`

It also independently hard-codes and verifies the environment versions and thread-control values. Therefore `DEPENDENCY_LOCK.txt` should remain a canonical external input at the exact expected digest, not a second normative source inside the V8 payload.

### Cohort, restricted seal/protocol and BEAM manifest

These are likewise external frozen inputs whose hashes/identities are checked by the accepted runner. V8 does not duplicate their contents or restate their semantics.

### Run authorization

`RUN_AUTHORIZATION_TEMPLATE.json` is not part of V8 normative payload. The accepted runner consumes an actual authorization document only at run/finalize time and verifies its exact schema/field set, candidate-seal hash, runner hash, cohort hash, output namespace, HMAC and other required fields.

No production authorization exists at V8 preparation time.

### Package/preflight checker

A checker is an audit tool, not a normative payload artifact. It must live outside the candidate payload. It may verify exact-byte closure and fail-closed status, but it must make no generalized claim that its checks cover all possible future mutations.

## Candidate execution seal

The runner consumes a candidate execution seal, so V8 requires a minimal machine-readable seal/profile. That seal is an external runtime gate artifact, not a source of scientific methodology.

The V8 seal/profile must contain no load-bearing free-form prose. Its executable semantics must be limited to fields the runner actually checks or to immutable provenance identifiers. Any additional field must have an explicit consumer and an explicit reason; otherwise omit it.

Before production authorization, the seal/profile must remain fail-closed: no valid HMAC key commitment may be inferred or fabricated, and `task_4f1_run` remains `BLOCKED`.

A later production seal/profile containing a real Head Researcher key commitment is a distinct, explicitly authorized artifact and must bind the exact accepted runner and the already-sealed scientific preregistration. It is not created by this design decision.

## Exact-rational outcome condition remains separate and mandatory

Scientific preregistration requires final `D_t` sign classification using exact rational arithmetic, not rounded floating aggregates.

The accepted runner may emit floating convenience fields, but those fields MUST NOT be used as the authoritative sign-classification input.

Before any run authorization, a separate frozen outcome-analysis implementation must exist that reconstructs the required fractions from discrete retrieval/gold data and computes the preregistered `D_t` signs exactly. This is an execution/analysis gate, not a reason to modify the accepted runner.

No Task 4F1 production authorization may be issued until this exact-rational implementation condition is closed.

## V8 audit target

A future independent audit, when independent model capacity is available, should be narrow and exact-byte based:

1. Verify runner SHA256 and byte identity to accepted V4.
2. Verify V8 normative payload contains only that runner.
3. Verify submission metadata is minimal, machine-readable and carries no contradictory/restated scientific or algorithmic requirement.
4. Verify external dependency lock and other frozen inputs are referenced through identities already enforced by runner bytes, not duplicated as second authorities.
5. Verify the authorization boundary is fail-closed and no valid production authorization/HMAC is constructed.
6. Verify any audit/preflight tool is outside the normative payload and cannot be imported/invoked by the runner.
7. Verify no outcome access occurred.

Do NOT replay V6 text-encoding evasions against a claim V8 does not make. The relevant attack is instead: can any exact submitted metadata byte alter execution semantics while escaping the runner/authorization binding? If yes, BLOCK. If no, the exact-byte candidate may proceed.

## Stop rule

No `--mode run` or `--mode finalize`.
No production authorization.
No HMAC key creation or inspection.
No real retrieval ranking or metric access.
No scientific-preregistration changes.
No generalized scanner.

## Next implementation step

Prepare V8 as a fresh candidate/profile without modifying V7. Preserve the accepted runner bytes exactly. Keep audit tools and human documentation outside the normative payload. Then implement/freeze the exact-rational outcome analyzer before any run authorization.
