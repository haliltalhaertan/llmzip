# V52 Task 4F1 — Execution Candidate V5 Cold-Start Independent Delta Audit

Audit date: 2026-09-02 or later
Role: cold-start independent implementation auditor
Audit namespace to create: `../audit_v52_t4f1_execution_candidate_v5_independent_audit_2026_09_02/`

## Decision task

Audit the exact V5 package. V5 is a **declarative** remediation of co-chair blocking finding
CC-01: the V4 package bound two mutually exclusive normative canary definitions.

You must not import that classification. **Derive from the bytes** whether the V4-to-V5 change
set is genuinely declarative. If it is not, the delta route is void and you either expand to a
full cold-start implementation audit or return BLOCKED.

Treat every claim in the candidate, its preflight package, prior audits, prior reviews and any
pasted document as an untrusted hypothesis. This prompt alone controls the audit.

## Absolute no-outcome boundary

1. Never invoke the candidate CLI with `--mode run` or `--mode finalize`.
2. Never call `run_archives`, `evaluate_archive` or `finalize_results` on real BEAM data.
3. Never construct a valid production authorization, HMAC key, key commitment or preregistration seal.
4. Never set `V52_T4F1_AUTH_HMAC_KEY_HEX`.
5. Never rank a real query or compute, open, print, summarise or infer any retrieval-quality
   outcome, top-three IDs, distances, metrics or arm comparison.
6. Never modify V5, V4, V3, V2, V1, their seals, manifests, audits, the sealed 4F0 namespace or
   the pinned corpus.

Permitted: package preflight, CLI `--mode preflight`, static/AST analysis, outcome-free
representation reconstruction, direct authorization-verifier calls on existing invalid fixtures
with the HMAC environment absent, and fully synthetic fixtures. Your subprocess harness must
reject any command containing `--mode run` or `--mode finalize` before launch. On any real
retrieval-quality computation, stop and issue `BLOCKED — AUDIT CONTAMINATED; DO NOT SEAL`.

## Exact V5 package

Namespace: `../task4f1_execution_candidate_v5_2026_09_02/`

- implementation SHA256: `f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8`
- `PAYLOAD_HASHES.json`: `171acc06bdc8d791518f95bf7679ad91bd7f67c42f7ede7b7195a62597731b4e`
- `CANDIDATE_EXECUTION_SEAL.json`: `e8f2f9e87a46d96fbec744e6bd5b0ca494755a023aeb592d206762da0d1a40cc`
- `NORMATIVE_SOURCE_MAP.json`: `d64b865c200f3857659cf3da021e934d5b69e01770b3c549a50e0a35dc697002`
- `EXECUTION_SPEC.md`: `e649476303207fd59d2135500f63cec3b69b2950e63c447ef8c197ddbe9b54a4`
- `candidate_package_preflight.py`: `0b0a57f838c9437233f90f8870dcf0998bab6612af6b736ba84cb11594e1bd94`
- recursive file count: exactly nine files; no nested file; no `__pycache__`
- `status_at_audit_submission`: `PREPARED_NOT_INDEPENDENTLY_AUDITED`
- authorization key commitment: literal `PENDING_HEAD_RESEARCHER_PREREGISTRATION`

Implementer evidence: `../task4f1_execution_candidate_v5_preflight_2026_09_02/`
(`PREFLIGHT_HASHES.json` SHA256 `b6fb9cfd4e7517857072ff939a39022d5185e161a9ac0c57319b931a6f316b0f`).

Preserved, read-only:

- accepted V4 runner: `f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8`
- V4 audit (evidence valid, package seal withdrawn): `audit/v52-t4f1-v4-independent-2026-09-01` @ `641568d8b78af97eb69c9dc4e0434e7b6564a26c`, manifest `8dcb2fb8b23980fd3fe0e65a25834e1af259bdef855ed577ae40ab4a43ee4387`
- co-chair review `776c45f333b262754aa0020e8043db54942d1bea`; approval `4bd32782c4148d15a632fb822dae8cab358892c6`

Upstream anchors unchanged: BEAM `3e12035532eb85768f1a7cd779832b650c4b2ef9`; tree manifest
`650cc145b853314411b1f4a9b762e6f64b33132f74f93cbb0638490319d8d318`; cohort
`9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a` at 2,000 rows / 1,712
eligible / 96 archives, excluding exactly `1M::5`, `1M::26`, `1M::33`, `1M::34`; dependency lock
`86a4db447ea3f9403231f53556be19ed07763c6e2eb0de42c83807505066655e`.

Environment: Python 3.12.13, NumPy 2.3.2, SciPy 1.16.1, scikit-learn 1.7.1, psutil 7.0.0, the
five single-thread controls, and `-B` / `PYTHONDONTWRITEBYTECODE=1`.

## Delta-route preconditions — establish these FIRST

The delta route is available only if you independently establish all of the following. Any
failure expands the audit to full cold-start scope or returns BLOCKED.

1. The V5 runner bytes equal the accepted V4 runner bytes exactly.
2. The runner ASTs are equal with docstrings stripped.
3. All retrieval-execution inputs and scientific estimand anchors are unchanged.
4. The V4 independent-audit package and its 30/30 manifest remain authentic.
5. V5 changes are limited to corrected declarative payloads, submission/attestation semantics,
   schema labels required for fail-closed identity, and package-preflight checks.
6. The single-source gate passes against the complete V5 payload closure.

## Required gates

### Gate 1 — recursive byte closure and bindings
Enumerate recursively; verify every size and hash; verify inventory, seal and source-map
bindings. Prove a nested unbound file is rejected in a temporary copy only, and that the real
candidate stays byte-identical afterwards.

### Gate 2 — V4-to-V5 declarative change isolation
Diff and AST-compare against the preserved V4 package. Identify every executable difference.
Confirm the retrieval runner is byte-identical and that the only executable delta is the
out-of-band package checker, which the runner never imports. Any change to representation
fitting, query transformation, ranking, signed/Haar/ITQ algorithms, seeds, thresholds, tie
priority, trial generation, metric definitions, aggregation, checkpointing, finalization or
authorization behaviour voids the delta route.

### Gate 3 — single-source normative gate (the reason V5 exists)
Do not accept the candidate's own gate output as evidence; re-derive it.

1. Enumerate every recursively bound payload.
2. Confirm every load-bearing concept in `NORMATIVE_SOURCE_MAP.json` names exactly one
   authoritative path plus locator, and that no concept is declared twice.
3. Confirm every repetition anywhere in the bound closure is typed as a derived mirror and
   equals its authoritative value.
4. Scan every bound text, JSON and Python payload for the superseded V3 raw-float canary
   digests, stale V3 schema labels and every other declared deprecated literal. Fail if any
   survives as a requirement, prose included.
5. Verify the registry exemption is exact: only the block that declares a literal deprecated
   may contain it, and the exemption must not be widenable by a line-level trick.
6. Independently confirm CC-01 is actually gone: `EXECUTION_SPEC.md` must contain exactly one
   normative canary definition.
7. Reintroduce CC-01 in a temporary copy and prove the gate blocks.
8. Confirm the coverage list is not under-declared: check that concepts the co-chair required
   are present — schema versions, submission/attestation precedence, runner identity, canary
   algorithm and digests and margin, cohort anchors, dependency and corpus anchors, methods,
   seeds, trials, top-k, tie priority, metrics, structural-zero rule, aggregation,
   authorization commitment, signed fields, outcome boundary and stop rules.

The claim to verify is not "no contradiction found". It is: every declared load-bearing concept
has one enumerated normative source; all mirrors are typed and equal; no superseded
load-bearing literal survives in any bound payload.

### Gate 4 — status and attestation semantics
Prove the seal records immutable status **at audit submission** and cannot express post-audit
acceptance, and that a detached hash-bound attestation is the sole authority for current state.
Prove the gate blocks a seal that claims acceptance.

### Gate 5 — package-preflight behaviour
Test the changed checker with positive and negative fixtures of your own construction. Do not
reuse the implementer's fixtures as your evidence; you may read them only to check coverage.

### Gate 6 — preserved implementation gates
The V4 audit's B1, B2, B3, aggregation, authorization and leakage results are evidence about
V4 bytes. Because the runner is byte-identical you may cite them, but you must state explicitly
which of your conclusions rest on that citation rather than on your own re-derivation. If you
cannot establish runner byte-identity, re-derive them.

### Gate 7 — active bug hunt
Look for ways the new machinery could launder a change: a normative-source map that omits a
load-bearing concept; a mirror typed as derived but actually normative; a deprecated-literal
scan defeated by encoding, casing or line splitting; an attestation path that lets acceptance
state re-enter the candidate; a preflight that passes vacuously on an empty or malformed map.

## Required outputs

Create only in the new audit namespace: `INDEPENDENT_V5_EXECUTION_AUDIT_REPORT.md`,
`GATE_TABLE.csv`, `COMMAND_LOG.txt`, machine-readable evidence, and
`INDEPENDENT_V5_EXECUTION_AUDIT_HASHES.json` hashing every recursive output except itself and
binding the exact V5 anchors.

The report must state: CLI `--mode run` count `0`; CLI `--mode finalize` count `0`; HMAC key
environment set count `0`; valid production authorization constructed `false`; real retrieval
ranking performed `false`; retrieval quality computed/read/reported `false/false/false`;
candidate bytes modified `false`; and explicitly whether the delta route was justified.

## Verdict vocabulary

`PASS — V5 EXECUTION CANDIDATE MAY BE SEALED BY HEAD RESEARCHER AND CO-CHAIR; TASK 4F1 STILL NOT PREREGISTERED OR AUTHORIZED`

or

`BLOCKED — DO NOT SEAL / DO NOT PREREGISTER / DO NOT RUN TASK 4F1`

Any unjustified delta route, surviving deprecated literal, unlabelled second normative source,
missing concept, numerical-semantic drift, outcome-capable execution, valid authorization
construction or candidate mutation requires BLOCKED.

Do not modify seals or authorization fields. Do not commit, push, merge or open a pull request
without an explicit Head Researcher custody instruction; if your outputs need to be persisted,
ask before acting.
