# Research Program Status — 2026-08-31

Decision authority: Head Researcher

This document is the current operational research ledger. It distinguishes accepted scientific evidence, feasibility evidence, blocked branches and required next gates.

## Executive state

- `[FROZEN — TASK 4C3 LONGMEMEVAL NUMERICAL CHECKPOINT]`
- `[FROZEN — TASK 4D LOCOMO NUMERICAL CHECKPOINT]`
- `[CROSS-BENCHMARK REPLICATION ESTABLISHED — LONGMEMEVAL + LOCOMO]`
- `[NOT ESTABLISHED — GENERALIZATION BEYOND LONGMEMEVAL + LOCOMO]`
- `[NOT ESTABLISHED — CAUSAL MEDIATOR]`
- `[TASK 4E0 BLOCKED — LONGMEMEVAL-V2 PUBLIC DATA/METHOD INCOMPATIBILITY]`
- `[TASK 4F0 AUDIT ACCEPTED WITH CONDITIONS — RESTRICTED BEAM COHORT IS REFREEZEABLE]`
- `[TASK 4F1 BLOCKED — DO NOT PREREGISTER OR RUN]`
- `[TASK 4F0 RESTRICTED-COHORT PROTOCOL SEALED — 22/22 INDEPENDENT GATES PASS]`
- `[TASK 4F1 EXECUTION IMPLEMENTATION PREPARED — INDEPENDENT CODE AUDIT PENDING]`
- `[TASK 4F1 V2 INDEPENDENT AUDIT BLOCKED — B1/B2/B3 FINALIZATION INTEGRITY DEFECTS]`
- `[TASK 4F1 V3 INDEPENDENT AUDIT BLOCKED — CANARY NOT REPRODUCIBLE FROM DECLARED ENVIRONMENT LOCK]`
- `[TASK 4F1 V4 AUDIT EVIDENCE ACCEPTED — 9/9 GATES; PACKAGE SEAL WITHDRAWN BY CO-CHAIR CC-01]`
- `[TASK 4F1 V5 INDEPENDENT AUDIT BLOCKED — SINGLE-SOURCE GATE DID NOT ESTABLISH ITS CLAIM]`
- `[TASK 4F1 V6 PREPARED — INVERTED-BURDEN SWEEP; INDEPENDENT DELTA AUDIT PENDING]`
- `[TASK 4F1 PREREGISTRATION DECISION PENDING — STILL NOT AUTHORIZED TO RUN]`

## Accepted scientific evidence

Task 4C3 established a fixed-benchmark native-axis effect on the frozen 470-question LongMemEval cohort: Native SIGN96 `54.197517730496%`, mean Full-Haar96 `38.271666666667%`, `D96 = -15.925851063830 pp`.

Task 4D independently replicated the direction on the frozen 1,535-question evidence-valid LoCoMo cohort: Native SIGN96 `23.654714666441%`, mean Full-Haar96 `13.770827054136%`, `D_LoCoMo = -9.883887612305 pp`.

These are benchmark-level paired results. They do not establish a universal theorem, population-level generalization, a causal mediator, or production superiority.

## Task 4F0 decision

The independent BEAM audit is accepted as a feasibility and governance result with verdict:

`[PASS WITH CONDITIONS — ORIGINAL BLOCKED VERDICT CORRECT BUT RESOLVABLE]`

Verified audit facts:

- upstream BEAM commit `3e12035532eb85768f1a7cd779832b650c4b2ef9`;
- 100 conversations, 2,000 probing questions and 327,116 raw message units;
- 1,743 exact-source questions, 200 abstentions, 55 ambiguous/missing, one coarse and one malformed record;
- 1,720 divergent duplicate message keys in `1M::5`, `1M::26`, `1M::33`, and `1M::34`;
- outcome-independent restricted primary cohort: 1,712 questions;
- representation transfer: pass on clean archives;
- scale feasibility: pass at 100K, 500K, restricted-clean 1M and 10M;
- Native-vs-Haar retrieval-quality outcome inspected: no.

The full-cohort BEAM estimand is rejected. The restricted cohort is eligible for a new pre-outcome refreeze, not for immediate scientific execution.

## Mandatory gate to Task 4F1

Task 4F1 remains closed until a new 4F0 restricted-cohort refreeze locks all of the following before any outcome access:

1. exact prompt bytes and a reproducible prompt SHA256;
2. `estimand_primary_cohort.csv` SHA256 `9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a`;
3. exclusion of the four defective 1M archives and the exact 1,712-row denominator;
4. formulas for Fractional Source Evidence R@3, ANY@3 and ALL@3, with ALL@3 structural zeros retained for the 587 questions having more than three gold units;
5. memory-unit key/text, dependency versions, single-thread environment and random states;
6. exact frozen adapter/compute script bytes and hashes;
7. pre-run leakage, non-vacuity, representation-repeatability and resource gates;
8. a stop rule forbidding post-outcome cohort repair, rescue seeds, extra rotations, threshold tuning or metric substitution.

The initial restricted-refreeze audit attempt blocked on the unavailable dependency lock. After the exact isolated environment was installed, the superseding independent audit passed 22/22 byte, cohort, raw-corpus, determinism, leakage and invariance gates and returned `PASS WITH CONDITIONS — CANDIDATE MAY BE SEALED BY HEAD RESEARCHER`. The Head Researcher accepted that sign-off and sealed the 1,712-question restricted-cohort protocol. The remaining blocker is a separately byte-bound outcome-bearing 4F1 implementation and an independent audit of that implementation. This is an execution-governance gate, not a scientific outcome.

Only after the future 4F1 implementation is byte-bound and independently accepted may the Head Researcher decide whether to preregister Task 4F1.

## Task 4F1 implementation preparation

A separate guarded execution candidate now exists at `task4f1_execution_candidate_2026_08_31/`. It binds the outcome-capable runner SHA256 `28735991a3d54144ec1268693e233f2fc45278049f8df7fb177d74b852bf5428` and candidate seal SHA256 `a1277e4665936ea691505a2d386c1d6a4824c2ebc5e5e56d6a94aba1f58876cd` while retaining blocked authorization.

The outcome-free preparation preflight passed exact environment, 1,712-question/96-archive cohort structure, 192 pinned corpus blob checks, synthetic method/invariance checks, a raw `100K::12` representation digest canary and a negative run-authorization probe. No retrieval-quality result was computed. This is implementer evidence, not independent sign-off.

The next gate is a cold-start independent audit of these exact execution bytes. Even a passing code audit will only permit sealing the implementation; a separate Task 4F1 preregistration and Head Researcher run authorization will still be required.

## 2026-09-01 — Task 4F1 audit/remediation chain

The V1 execution-code audit supplied useful technical checks but disclosed Incident A1: an auditor-side negative-test error triggered outcome-capable execution before containment. No metric value was reported, but that audit cannot serve as the clean outcome-free seal sign-off.

The subsequent clean V2 audit was `BLOCKED — DO NOT SEAL / DO NOT PREREGISTER / DO NOT RUN TASK 4F1`. Its synthetic-only tests reproduced three load-bearing defects: derived finalization CSV overwrite when no manifest exists; acceptance of stored metrics not recomputed from frozen gold; and acceptance of Native/signed-control top-three divergence when metrics remain equal.

V3 preserves V2 and its audit unchanged, adds exclusive no-replace derived-output commits, exact frozen-gold metric recomputation, and exact Native/signed-control ID-plus-distance validation. V3 passed outcome-free implementer preflight and synthetic B1–B3 regressions only.

The cold-start independent audit of the exact V3 bytes completed on 2026-09-01 with verdict `BLOCKED — DO NOT SEAL / DO NOT PREREGISTER / DO NOT RUN TASK 4F1` (branch `audit/v52-t4f1-v3-independent-2026-09-01`, commit `a590f629`).

The audit confirms the three V2 blockers are genuinely repaired: B1 destinations and temp paths block before any byte changes with exclusive `os.link` commit; B2 recomputes metrics exactly from frozen gold; B3 requires exact Native/signed-control top-three IDs and distances. Gates G1, G2, G4, G5, G6, G7 and G8 passed, including a 29/29 negative-control matrix and a 9/9 substitution and bypass hunt, with fail-closed authorization and clean leakage statics.

Gate 3 blocks. In an environment satisfying the declared lock exactly, the pinned `100K::12` representation canary fails, so the candidate cannot pass its own `--mode preflight`. Corpus provenance and structure are correct and the code is locally deterministic, but the bit-exact float digests differ from the sealed values. Varying only `OPENBLAS_CORETYPE` while holding code, data and all locked versions constant produced four distinct archive digests across six dispatches, none matching the pinned digest, while `verify_environment()` accepted every variant. `TruncatedSVD` with the randomized solver depends on BLAS/LAPACK kernels, and the lock pins package versions and thread counts but not the BLAS build or CPU microarchitecture dispatch. A load-bearing reproducibility gate is therefore machine-bound rather than lock-bound, and the sealed digests cannot be independently reproduced from the sealed artifacts alone.

Remediation is a Head Researcher decision: either bind the BLAS/LAPACK build and effective CPU kernel dispatch in the lock and in `verify_environment()`, or replace bit-exact float digests as a load-bearing gate with dispatch-stable quantities such as sign codes and integer Hamming distances plus a tolerance-based invariance check. Either way the canary expectations must be re-derived, re-sealed and independently re-audited on the exact new bytes.

## Operational governance defect

Remote `main` was verified at `d3c7aa09c9553cd5ac100e668923abab602e4257`, but GitHub's remote `HEAD` currently points to `claude/itq-frontier-audit-wfrz6a` at `78b4fdfa7234fb545dbf9eb51ebce90a794a0d6b`. This conflicts with `CHAIN_OF_CUSTODY.md`, which defines `main` as canonical.

Before opening or merging further research work:

1. restore the GitHub default branch to `main`;
2. require PR bases to be explicit;
3. verify remote `main` commit immediately before branch creation and merge;
4. never infer canonical state from remote `HEAD` until the setting is repaired.

## Priority queue

1. P0 — repair GitHub default branch to `main`.
2. P0 — review and merge the accepted 4F0 audit/governance package without modifying frozen artifacts.
3. P0 — preserve the sealed 4F0 restricted-cohort payload and audit chain; do not run Task 4F1.
4. P0 — independently audit the byte-bound 4F1 execution candidate without running retrieval quality.
5. P1 — seal or reject that implementation and close or retain each execution gate explicitly.
6. P1 — only then make a Head Researcher decision on Task 4F1 preregistration.
7. P1 — recover `V52_T4C2_same_input_proof.csv` only from its canonical byte source and accept it only if SHA256 equals `16a6c4a66be6f5cb4ac81157588c9e735cb1b31d122e83c68f14fbf77dd57e57`.
8. P1 — independently materialize and hash the four currently external Task 4C3/dataset pins when resources permit.
9. P2 — defer mediator studies, alternate representations and production claims to separately justified branches.

## 2026-09-01 — Task 4F1 V4 remediation

The Head Researcher accepted remediation option 2 from the V3 audit. V4 is a new
candidate namespace; V3 and every sealed artifact are preserved byte-for-byte.

V4 changes only the canary and environment provenance. The canary now binds sign-code
digests, `sha256(packbits(centered >= 0))`, which are the quantities that actually drive
Hamming retrieval, instead of raw float bytes. It adds `CANARY_SIGN_MARGIN = 1e-9`, which
fails closed if the representation ever drifts close enough to zero for a sign code to
flip between conformant environments. `verify_environment` additionally records the
BLAS/LAPACK build and coretype as provenance without gating on it.

Measured on the pinned `100K::12` archive across six kernel dispatches: raw float digests
gave four distinct values, sign-code digests gave exactly one, the maximum cross-dispatch
absolute difference was 1.202e-13 against a minimum absolute value of 4.089e-07, a margin
of roughly 3.4e6, with none of the 37,632 entries inside the noise band. V4
`--mode preflight` passes on all six dispatches, where V3 passed on none. The B1/B2/B3
synthetic regression is 29/29 against V4, and V3-to-V4 change isolation is confined to the
canary, two new helpers, environment provenance and schema literals.

This is implementer evidence, not independent sign-off. V4 is
`PREPARED_NOT_INDEPENDENTLY_AUDITED` and the agent that prepared it cannot audit it. The
next gate is a cold-start independent audit of the exact V4 bytes under
`prompts/V52_TASK_4F1_EXECUTION_CANDIDATE_V4_INDEPENDENT_AUDIT_PROMPT_2026-09-01.md`. Even
a passing audit permits only a sealing decision; Task 4F1 preregistration and run remain
blocked.

## 2026-09-02 — Task 4F1 V4 audit accepted; implementation sealed

A cold-start independent auditor, a different agent from the one that prepared V4 and
importing no V3 conclusions, audited the exact V4 bytes and returned
`PASS — V4 EXECUTION CANDIDATE MAY BE SEALED BY HEAD RESEARCHER; TASK 4F1 STILL NOT
PREREGISTERED OR AUTHORIZED`, with all nine gates passing.

The Head Researcher independently verified the pushed package rather than accepting the
relayed verdict. The audit commit matches its declared SHA and its parent is the exact
tree audited; `main` was untouched; the diff is 31 additions confined to the audit
namespace. The hashes file matches its declared digest and self-verifies 30/30 with
complete two-way coverage, and it binds the real V4 bytes. The command log shows 16
launches, six of them `--mode preflight`, zero carrying `--mode run` or `--mode
finalize`, and three harness rejections logged before any launch. Gate 3's raw evidence
holds six independent reconstructions giving one sign digest against four raw float
digests, and those per-dispatch float digests reproduce the earlier V3 measurements
exactly. A cohort path difference between auditor and implementer resolved to
byte-identical files at the sealed anchor.

The audit is accepted and the V4 implementation is sealed as of 2026-09-02. The seal is
recorded in `docs/v52/task4f1/V4_HEAD_RESEARCHER_ACCEPTANCE_2026-09-02.json` and ledger
L-008 rather than by editing the candidate, because changing
`CANDIDATE_EXECUTION_SEAL.json` would break the binding the audit established.

Four non-blocking observations were dispositioned: two stale V3 strings accepted as
documented conditions, since correcting cosmetic text would change the payload inventory
and seal and force a re-audit; the canary's `>=` versus `>` scope limit accepted as
structurally bounded by the sign margin; and the POSIX hard-link dependency of the
commit path accepted as a binding preregistration condition.

This seals the implementation only. Task 4F1 preregistration and run remain blocked and
retrieval-quality outcome access remains forbidden. Whether to preregister is a separate
Head Researcher decision.

## 2026-09-02 — Co-chair review: V4 seal withdrawn, V5 required

The research co-chair reviewed the L-008 acceptance and returned `REQUEST CHANGES`. The V4
independent-audit evidence is accepted as authentic, hash-consistent and valid for its nine
implementation gates. The conclusion that the whole V4 execution package may stand sealed is
not co-signed.

Blocking finding CC-01: `EXECUTION_SPEC.md`, bound in `PAYLOAD_HASHES.json`, contains two
mutually exclusive normative canary definitions. Line 44 requires the raw array digests to
reproduce the superseded V3 values, while lines 110-112 require the V4 sign-code digests.
Only the latter is implemented and audited, and the V3 requirement is unsatisfiable on
conformant hardware — that is exactly why V3 was superseded. The Continuity Lead reproduced
the contradiction directly and accepts it as its own error: V4's spec was produced by a
blanket label substitution plus an appended section, which added the correct specification
without deleting the superseded one. The V4 audit prompt scoped its change-isolation gate to
runner source and AST, so no gate examined bound prose for contradictions.

A V5 candidate is required. Its execution runner must be byte-identical to the accepted V4
runner so the change set is purely declarative, allowing a delta-scoped audit; any executable
change forces a full cold-start audit. V5 must also correct the stale V3 docstring and
authorization-template text, separate "status at audit submission" from the detached
authoritative acceptance record, and its audit prompt must add a mandatory cross-payload
semantic-consistency gate covering canary digests, schema names, authorization status, cohort
anchors and precedence.

Scientific route: option B. Before preregistration the outcome-free justification for the
restricted cohort and the exact tier-stratified estimands are frozen. The primary interest is
a scale-stratified heterogeneity profile over the four tiers, whose frozen composition was
independently recomputed and confirmed: 100K 355 questions across 20 archives with 3.08 mean
gold units and 96 structural ALL@3 zeros; 500K 629/35/4.26/168; 1M 553/31/8.59/253; 10M
175/10/7.47/70. Because the tiers are neither paired nor randomized and their gold cardinality
varies from 3.08 to 8.59, any ordered trend is an association across fixed benchmark strata
and must never be reported as a causal effect of context length or as a degradation law.
ALL@3 is reported under its structural-zero rule but is not the main scale claim.

Governance: the Continuity Lead remains sole writer of the state file and the ledger; the
co-chair writes only review artifacts on a separate branch and holds approval and veto. Task
4F1 remains blocked for preregistration and execution.

## 2026-09-02 — Task 4F1 V5 prepared (declarative CC-01 remediation)

Under the co-chair approval at `4bd32782`, V5 was prepared as a purely declarative remediation
of CC-01. The retrieval runner is byte-identical to the accepted V4 runner `f96cba2c` and its
AST is equal with docstrings stripped, so no representation, method, seed, threshold, priority,
metric, aggregation, checkpoint, finalization or authorization behaviour changes. The only
executable delta is the out-of-band package checker, which the runner never imports.

`EXECUTION_SPEC.md` now carries exactly one normative canary section and both superseded V3
raw-float digests are enumerated as deprecated literals. `NORMATIVE_SOURCE_MAP.json` enumerates
18 load-bearing concepts with one authoritative source each and types every repetition as a
derived mirror. The preflight gate proves one source per concept, equal typed mirrors, zero
surviving deprecated literals across the whole bound closure including prose, and runner
byte-identity. Ten negative fixtures block, including a direct reintroduction of CC-01.

Two design decisions are recorded so they are not later "corrected". First, V5 is a package
version rather than a schema version: because the runner is byte-identical, the schema literals
it verifies stay at V4, and the authorization template names the schema the shipped runner
actually verifies. Second, the deprecated-literal scan exempts only the registry block that
declares a literal, by re-serialising the map without it rather than by any line-level
heuristic — the first attempt used such a heuristic and failed against the map itself.

This is implementer evidence, not independent sign-off. A cold-start delta audit is required and
must derive the declarative classification from the bytes. Sealing requires both the Head
Researcher and the co-chair. Task 4F1 remains blocked for preregistration and execution, and the
scientific route remains option B with tier-stratified estimands frozen beforehand.

## 2026-09-03 — V5 blocked, V6 prepared on an inverted burden

The V5 delta audit confirmed CC-01 was repaired and the change set was declarative, but returned
BLOCKED: the single-source gate did not establish its own claim. It trusted a hand-written mirror
list, so it could verify only what its author declared, and it matched raw text line by line, so
the same digest wrapped across two lines or written in uppercase defeated it. The Continuity Lead
reproduced every blocking finding against its own package before accepting the verdict.

V6 inverts the burden. The gate sweeps every bound payload for value-shaped tokens and requires
each discovered token to be attributed to a declared concept and found only where that concept
permits. Matching runs on normalised text. Concepts rose from 18 to 24, adding the BEAM tree
manifest, restricted seal, restricted protocol and parent-commit anchors, tie priority and the arm
identifiers. The duplicate status field is removed and the attestation is a resolvable file holding
a real record.

Building the sweep made it audit its author: it caught a 64-hex digest matching as its own 40-hex
prefix, and a stale duplicate supersedes block in the seal still pointing at V3, which was deleted
rather than exempted. Genuinely non-normative tokens were not silently ignored — each exempt class
is declared with its scope and rationale.

One limit is stated rather than glossed: the sweep tracks 64-hex, 40-hex and V52_ identifier
shapes, so short load-bearing values such as 1712, 96, 392, the seeds and the tolerances are
outside its reach and remain covered only by declared concepts and the runner's constants. The
audit prompt asks the auditor to judge whether the claim survives that gap.

The runner has been byte-identical to the accepted V4 runner since V5, so no execution behaviour
changed. V6 was prepared under Continuity Lead authority alone while the co-chair is unavailable,
exceeding the standing approval; sealing remains conditional on co-chair ratification. Task 4F1
remains blocked for preregistration and execution.
