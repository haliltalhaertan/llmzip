# V52 Task 4F1 — Execution Candidate V6 Cold-Start Independent Delta Audit

Audit date: 2026-09-03 or later
Role: cold-start independent implementation auditor
Audit namespace to create: `../audit_v52_t4f1_execution_candidate_v6_independent_audit_2026_09_03/`

## Decision task

V6 answers a BLOCKED V5 audit. V5's single-source gate trusted a hand-written mirror list and
matched raw text per line, so it verified only what its author declared and was defeated by
line wrapping and uppercase hex. V6 claims to invert that burden.

**Derive everything from the bytes.** Do not import the claim that the change set is
declarative, and do not accept the gate's own output as evidence that its claim holds. Your
central question is whether the sweep actually establishes what it asserts, or merely appears to.

Treat every claim in the candidate, its preflight package, prior audits and prior co-chair
reviews as an untrusted hypothesis. This prompt alone controls the audit.

## Absolute no-outcome boundary

1. Never invoke the candidate CLI with `--mode run` or `--mode finalize`.
2. Never call `run_archives`, `evaluate_archive` or `finalize_results` on real BEAM data.
3. Never construct a valid production authorization, HMAC key, key commitment or preregistration seal.
4. Never set `V52_T4F1_AUTH_HMAC_KEY_HEX`.
5. Never rank a real query or compute, open, print, summarise or infer any retrieval-quality
   outcome, top-three IDs, distances, metrics or arm comparison.
6. Never modify V6, V5, V4, V3, V2, V1, their seals, manifests, audits, the sealed 4F0 namespace
   or the pinned corpus.

Permitted: package preflight, CLI `--mode preflight`, static/AST analysis, outcome-free
representation reconstruction, direct authorization-verifier calls on existing invalid fixtures
with the HMAC environment absent, and fully synthetic fixtures. Your subprocess harness must
refuse any command containing `--mode run` or `--mode finalize` before launch. On any real
retrieval-quality computation, stop and issue `BLOCKED — AUDIT CONTAMINATED; DO NOT SEAL`.

## Exact V6 package

Namespace: `../task4f1_execution_candidate_v6_2026_09_03/`

- implementation SHA256: `f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8`
- `PAYLOAD_HASHES.json`: `794322114c44d14de352b3decc6d80c795a9706eeaa77419d0f30200c0beabab`
- `CANDIDATE_EXECUTION_SEAL.json`: `ac85bbf04dd3f8502763432a9b51d7b0c92b06349fcd755fc1072af78710ebf3`
- `NORMATIVE_SOURCE_MAP.json`: `2795ff176df7e465955ed407ef66514c425ccf255b831cea5d71421136df5924`
- `candidate_package_preflight.py`: `97978dda6dbd35fc12109d51cc0cb0a83bda929f2e268da0a7ef085d3953796a`
- `EXECUTION_SPEC.md`: `e649476303207fd59d2135500f63cec3b69b2950e63c447ef8c197ddbe9b54a4`
- detached attestation (outside the candidate): `docs/v52/task4f1/V6_ACCEPTANCE_ATTESTATION_2026-09-03.json`,
  SHA256 `3eed58e1a6fbd6754cdc6582209010cc2d2db08a84004f4ca55a45281cc4919a`
- recursive candidate file count: exactly nine files; no nested file; no `__pycache__`

Implementer evidence: `../task4f1_execution_candidate_v6_preflight_2026_09_03/`
(`PREFLIGHT_HASHES.json` SHA256 `4f6abc15917ea5d8ae7d06f69c7b223234d9a8123b0a1713bd1ec0dac63b73ad`).

Preserved, read-only: accepted V4 runner `f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8`;
V4 audit `audit/v52-t4f1-v4-independent-2026-09-01` @ `641568d8b78af97eb69c9dc4e0434e7b6564a26c`;
BLOCKED V5 audit `audit/v52-t4f1-v5-independent-2026-09-02` @ `6243ba6d9fe1c3d059d78369d8fed3534d7921d0`,
manifest `0b7879e366d58f68022bc12826e820a23e7c2a1f4bf29c456fea70f7faf4af81`; co-chair review
`776c45f333b262754aa0020e8043db54942d1bea` and approval `4bd32782c4148d15a632fb822dae8cab358892c6`.

Upstream anchors unchanged: BEAM `3e12035532eb85768f1a7cd779832b650c4b2ef9`; tree manifest
`650cc145b853314411b1f4a9b762e6f64b33132f74f93cbb0638490319d8d318`; cohort
`9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a` at 2,000 rows / 1,712
eligible / 96 archives, excluding exactly `1M::5`, `1M::26`, `1M::33`, `1M::34`.

Environment: Python 3.12.13 (not available prebuilt; build from the python.org source tarball),
NumPy 2.3.2, SciPy 1.16.1, scikit-learn 1.7.1, psutil 7.0.0, the five single-thread controls,
`-B` / `PYTHONDONTWRITEBYTECODE=1`. The pinned corpus is not in Git and must be materialized
over the git protocol, then verified against the committed pinned-tree manifest before use.

## Delta-route preconditions — establish these FIRST

1. V6 runner bytes equal the accepted V4 runner bytes exactly.
2. Runner ASTs equal with docstrings stripped.
3. Retrieval-execution inputs and estimand anchors unchanged.
4. The V4 and V5 audit packages remain authentic.
5. V6 changes are limited to declarative payloads, attestation semantics and the package checker.
6. The inverted-burden gate passes against the complete V6 payload closure.

Any failure expands the audit to full cold-start scope or returns BLOCKED.

## Required gates

### Gate 1 — recursive byte closure and bindings
Enumerate recursively; verify sizes, hashes and the inventory/seal/source-map bindings. Prove a
nested unbound file is rejected in a temporary copy, and that the real candidate is byte-identical
afterwards.

### Gate 2 — V5-to-V6 declarative change isolation
Diff and AST-compare against the preserved V5 and V4 packages. Confirm the runner is
byte-identical and that the only executable delta is the out-of-band checker, which the runner
never imports. Any change to representation fitting, query transformation, ranking, algorithms,
seeds, thresholds, tie priority, trial generation, metrics, aggregation, checkpointing,
finalization or authorization behaviour voids the delta route.

### Gate 3 — the inverted-burden sweep (the reason V6 exists)
Re-derive; do not accept the gate's output.

1. Confirm the sweep genuinely discovers tokens rather than reading a declared list: construct
   your own value-shaped tokens in fresh locations and confirm each is caught.
2. Confirm normalisation defeats the exact V5 escapes — the same digest wrapped across lines and
   in uppercase — and probe further evasions of your own devising: interleaved markup, zero-width
   or unicode look-alike characters, base64 or decimal re-encoding, splitting across JSON keys,
   comments, or a payload the closure does not bind.
3. Assess the token patterns for blind spots. They cover 64-hex, 40-hex and `v52_t4f*`
   identifiers. Determine what load-bearing values they would MISS — short numerics such as
   `1712`, `96`, `392`, seeds, thresholds, tolerances, arm names, file names — and judge
   whether the gate's claim survives those gaps or overstates itself.
4. Audit the three declared exempt classes (`inventory_self_hashes`, `historical_provenance`,
   `artifact_identifiers`). For each, determine whether its scope is exactly as narrow as its
   rationale claims, and try to smuggle a normative literal through it.
5. Confirm the declaration-site exemption is exact: only the map's `fields` and
   `deprecated_literals` blocks are exempt, and the exemption cannot be widened by editing prose.
6. Confirm every concept resolves to an existing path and no concept is declared twice.
7. Assess coverage: is any load-bearing concept still missing? The V5 audit found five. Look for
   more, and say plainly whether 24 concepts is now complete or merely larger.

State explicitly whether the gate's claim — one source per concept, mirrors declared, no
superseded literal anywhere, no unattributed value-shaped token — is **established** or merely
**not yet falsified**.

### Gate 4 — attestation and submission-status semantics
Prove the seal records submission status only, the inventory carries no status field, the
attestation path resolves to a real file holding a real record, and the gate blocks a missing,
unresolvable or disagreeing attestation.

### Gate 5 — package-preflight behaviour
Test with positive and negative fixtures of your own construction. You may read the implementer's
fixtures only to check coverage, never as your evidence.

### Gate 6 — preserved implementation gates
The V4 audit's B1/B2/B3, aggregation, authorization and leakage results concern bytes that are
byte-identical here. You may cite them, but state exactly which conclusions rest on that citation
rather than your own re-derivation.

### Gate 7 — active bug hunt
Hunt for ways the new machinery could launder a change: a concept whose scannable literals omit
its real value; an exempt class wider than its rationale; a token pattern that misses a
load-bearing constant; an attestation that can be satisfied by a file the candidate itself writes;
a gate that passes vacuously on an empty or malformed map.

## Required outputs

Create only in the new audit namespace: `INDEPENDENT_V6_EXECUTION_AUDIT_REPORT.md`,
`GATE_TABLE.csv`, `COMMAND_LOG.txt`, machine-readable evidence, and
`INDEPENDENT_V6_EXECUTION_AUDIT_HASHES.json` hashing every recursive output except itself and
binding the exact V6 anchors.

State: CLI `--mode run` count `0`; `--mode finalize` count `0`; HMAC key environment set count
`0`; valid production authorization constructed `false`; real retrieval ranking performed
`false`; retrieval quality computed/read/reported `false/false/false`; candidate bytes modified
`false`; and whether the delta route was justified.

## Custody

You ARE authorized and required to push your outputs, to branch
`audit/v52-t4f1-v6-independent-2026-09-03` only, created fresh from the commit you audited.
Push incrementally after each gate; do not hold outputs to the end. Commit only your own audit
namespace, never to main, no merge, no pull request. Tag pushes are refused in this environment
with HTTP 403; that is environmental, not an integrity event.

## Verdict vocabulary

`PASS — V6 EXECUTION CANDIDATE MAY BE SEALED BY HEAD RESEARCHER AND CO-CHAIR; TASK 4F1 STILL NOT PREREGISTERED OR AUTHORIZED`

or

`BLOCKED — DO NOT SEAL / DO NOT PREREGISTER / DO NOT RUN TASK 4F1`

Any unjustified delta route, surviving deprecated literal, unattributed or undeclared token, an
exempt class wider than its rationale, a missing load-bearing concept, numerical-semantic drift,
outcome-capable execution, valid authorization construction or candidate mutation requires BLOCKED.

Note for the record: V6 was prepared under Continuity Lead authority alone and exceeds the
standing co-chair approval, which covered V5 only. Even a PASS leaves sealing conditional on
co-chair ratification.
