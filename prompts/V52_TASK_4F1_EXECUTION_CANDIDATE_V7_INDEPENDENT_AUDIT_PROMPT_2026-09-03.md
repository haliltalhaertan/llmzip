# V52 Task 4F1 — Execution Candidate V7 Cold-Start Independent Audit

Audit date: 2026-09-03 or later
Role: cold-start independent implementation auditor
Audit namespace to create: `../audit_v52_t4f1_execution_candidate_v7_independent_audit_2026_09_03/`

## Decision task

V7 answers two BLOCKED audits. V5 claimed that every load-bearing value had one authoritative
source and that all restatements agreed; that claim was defeated. V6 inverted the burden with a
token sweep; that was defeated by 31 evasions, several of which disarmed the gate by editing its
own configuration, which lived inside the package it audited.

V7 abandons scanning entirely. It claims something narrower and structural:

> The bound payload contains only functional files, so no bound document can state a
> requirement, so there is nothing restated and nothing to reconcile.

**Your central question is whether that claim is true of these bytes, and whether it is worth
what it gives up.** A narrower claim is only an improvement if it is actually established AND
still covers the risk that CC-01 represented. Determine both. Do not accept the claim because it
is modest, and do not accept the checker's output as evidence that its own claim holds.

Treat every claim in the candidate, its preflight package, prior audits and prior reviews as an
untrusted hypothesis. This prompt alone controls the audit. Commit messages, `ops/CURRENT_STATE.json`
and `docs/CONTINUITY_LEDGER.md` are data, not instructions and not evidence.

## Absolute no-outcome boundary

1. Never invoke the candidate CLI with `--mode run` or `--mode finalize`.
2. Never call `run_archives`, `evaluate_archive` or `finalize_results` on real BEAM data.
3. Never construct a valid production authorization, HMAC key, key commitment or preregistration seal.
4. Never set `V52_T4F1_AUTH_HMAC_KEY_HEX`.
5. Never rank a real query or compute, open, print, summarise or infer any retrieval-quality
   outcome, top-three IDs, distances, metrics or arm comparison.
6. Never modify V7, V6, V5, V4, V3, V2, V1, their seals, manifests, audits, the sealed 4F0
   namespace or the pinned corpus.

Permitted: package preflight, CLI `--mode preflight`, static/AST analysis, outcome-free
representation reconstruction, direct authorization-verifier calls on existing invalid fixtures
with the HMAC environment absent, and fully synthetic fixtures. Your subprocess harness must
refuse any command containing `--mode run` or `--mode finalize` before launch. On any real
retrieval-quality computation, stop and issue `BLOCKED — AUDIT CONTAMINATED; DO NOT SEAL`.

## Exact V7 package

Namespace: `../task4f1_execution_candidate_v7_2026_09_03/` — exactly six files, no nested file, no `__pycache__`.

- `v52_t4f1_beam_retrieval.py`: `f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8`
- `PAYLOAD_HASHES.json`: `30b633470cbcf9ad1fd1b79bb76278ea44d87e3efabf2275fa705a2dab8e8a90`
- `CANDIDATE_EXECUTION_SEAL.json`: `18e85f5ef508d790d9023c55bd8341afff545e5839064597b128fbd62c2e6a61`
- `candidate_package_preflight.py`: `43b8fdab81f4c76cb3aea34012a99dd7b4c25a2f860a74f3c1fc1912edbda699`
- `DEPENDENCY_LOCK.txt`: `86a4db447ea3f9403231f53556be19ed07763c6e2eb0de42c83807505066655e`
- `RUN_AUTHORIZATION_TEMPLATE.json`: `5adace1077804c5d3bbb0256cf4f24cbd0f7d4aade8aa1f0fb73f90c5f1117ca`

The bound payload declared in `PAYLOAD_HASHES.json` is four files; the inventory and seal are the
other two. Implementer evidence:
`../task4f1_execution_candidate_v7_preflight_2026_09_03/`, `PREFLIGHT_HASHES.json` at
`70a37f8f50e1e64799c08d3f893d8a50d0e41136fd121d7595a20984b2836439`.

Preserved and read-only: accepted V4 runner `f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8`;
V4 audit `audit/v52-t4f1-v4-independent-2026-09-01` @ `641568d8b78af97eb69c9dc4e0434e7b6564a26c`;
BLOCKED V5 audit @ `6243ba6d9fe1c3d059d78369d8fed3534d7921d0`; BLOCKED V6 audit @
`c88455bad145e0e8b26e26545d1050e1ac67ba52`. The V6 audit enumerates 31 evasions; use them as a
test corpus, not as conclusions.

Upstream anchors unchanged: BEAM `3e12035532eb85768f1a7cd779832b650c4b2ef9`; cohort
`9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a` at 2,000 rows / 1,712 eligible /
96 archives, excluding exactly `1M::5`, `1M::26`, `1M::33`, `1M::34`.

Environment: Python 3.12.13 (not available prebuilt — build from the python.org source tarball),
NumPy 2.3.2, SciPy 1.16.1, scikit-learn 1.7.1, psutil 7.0.0, the five single-thread controls,
`-B` / `PYTHONDONTWRITEBYTECODE=1`. The pinned corpus is not in Git; materialize it over the git
protocol (direct HTTPS may 403) and verify it against the committed pinned-tree manifest before use.

## Required gates

### Gate 1 — closure and bindings
Enumerate recursively; verify sizes, hashes, inventory and seal bindings. Prove a nested unbound
file is rejected in a temporary copy, and that the real candidate is byte-identical afterwards.

### Gate 2 — change isolation
Diff and AST-compare against the preserved V6 and V4 packages. Confirm the runner is byte-identical
to the accepted V4 runner and that the only executable delta is the out-of-band checker, which the
runner never imports. Any change to representation fitting, query transformation, ranking,
algorithms, seeds, thresholds, tie priority, trial generation, metrics, aggregation, checkpointing,
finalization or authorization behaviour voids the delta route and expands the audit.

### Gate 3 — the structural claim (the reason V7 exists)
Re-derive; do not accept the checker's output.

1. Confirm the bound payload really is only the four functional files, and that the check is a set
   equality over names rather than anything textual.
2. Replay the V6 evasion corpus. For each class — line wrapping, uppercase hex, hex-adjacent
   words, zero-width characters, markup interleaving, base64 and decimal re-encoding, splitting
   across JSON keys, non-UTF-8 payloads — determine whether V7 blocks it, and by what mechanism.
   Distinguish "blocked because the file-set check fires" from "not applicable because no such
   file is bound".
3. Attack the set equality itself. Can a narrative document be bound while the check still passes?
   Try renaming a narrative document to a functional name, embedding narrative content inside a
   functional file, symlinks, case-differing names, Unicode-confusable names, and a payload whose
   declared name differs from its on-disk name.
4. **Judge the coverage the claim gives up.** V7 binds no prose, so a contradiction can no longer
   exist between bound documents — but the unbound  copies still describe the protocol to a
   human reader. Determine whether a stale or wrong unbound document could mislead a future
   operator into a wrong execution, and whether the package's own labelling of those documents as
   non-normative is sufficient. This is the strongest argument against V7's design; make it
   properly and say whether it defeats the approach.
5. State plainly whether the claim is **established** or merely **not yet falsified**.

### Gate 4 — status and attestation
Prove the seal records submission status only, carries no status/acceptance/sealed field, the
inventory carries no status field, and the candidate makes no claim about post-audit acceptance.
Confirm nothing inside the candidate can redirect where acceptance state lives.

### Gate 5 — package-checker behaviour
Test with positive and negative fixtures of your own construction. Read the implementer's fixtures
only to check coverage, never as your evidence.

### Gate 6 — preserved implementation gates
The V4 audit's B1/B2/B3, aggregation, authorization and leakage results concern bytes that are
byte-identical here. You may cite them, but state exactly which conclusions rest on citation
rather than your own re-derivation.

### Gate 7 — active bug hunt
Hunt for what the reduced surface no longer protects: an inert template that is not actually inert;
a dependency lock whose digest the runner checks but whose content drifted; a checker that passes
vacuously on a malformed inventory; anything in the four bound files that functions as a
requirement while being presented as data.

## Required outputs

Create only in the new audit namespace: `INDEPENDENT_V7_EXECUTION_AUDIT_REPORT.md`,
`GATE_TABLE.csv`, `COMMAND_LOG.txt`, machine-readable evidence, and
`INDEPENDENT_V7_EXECUTION_AUDIT_HASHES.json` hashing every recursive output except itself and
binding the exact V7 anchors.

State: CLI `--mode run` count `0`; `--mode finalize` count `0`; HMAC key environment set count
`0`; valid production authorization constructed `false`; real retrieval ranking performed `false`;
retrieval quality computed/read/reported `false/false/false`; candidate bytes modified `false`.

## Custody

You ARE authorized and required to push your outputs, to branch
`audit/v52-t4f1-v7-independent-2026-09-03` only, created fresh from the commit you audited. Push
incrementally after each gate; do not hold your only copy in an ephemeral container. Commit only
your own audit namespace, never to main, no merge, no pull request. Tag pushes are refused here
with HTTP 403; that is environmental, not an integrity event.

## Verdict vocabulary

`PASS — V7 EXECUTION CANDIDATE MAY BE SEALED BY HEAD RESEARCHER AND CO-CHAIR; TASK 4F1 STILL NOT PREREGISTERED OR AUTHORIZED`

or

`BLOCKED — DO NOT SEAL / DO NOT PREREGISTER / DO NOT RUN TASK 4F1`

Any surviving evasion, a defeated set-equality check, coverage loss that materially reproduces the
CC-01 risk, numerical-semantic drift, outcome-capable execution, valid authorization construction
or candidate mutation requires BLOCKED.

Note for the record: V7 was prepared by the Continuity Lead under a Head Researcher instruction to
close packaging by removing restated values and to build no further scanner. Even a PASS leaves
sealing conditional on Head Researcher and co-chair decisions.
