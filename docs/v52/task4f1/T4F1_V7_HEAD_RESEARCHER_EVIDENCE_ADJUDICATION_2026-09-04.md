# V52 Task 4F1 — Head Researcher V7 Evidence Adjudication

Date: 2026-09-04
Role: Head Researcher / Research Manager
Nature: Head Researcher adjudication of already-pushed independent-auditor evidence. This is NOT a new independent audit.

## Exact evidence reviewed

Independent-auditor branch:
`audit/v52-t4f1-v7-independent-2026-09-03`

Evidence commit:
`16dc61313acd0e9086c852eccb9100023898fd27`

Controlling audit prompt:
`prompts/V52_TASK_4F1_EXECUTION_CANDIDATE_V7_INDEPENDENT_AUDIT_PROMPT_2026-09-03.md`

V7 checker:
`task4f1_execution_candidate_v7_2026_09_03/candidate_package_preflight.py`

Load-bearing independent evidence:
`audit_v52_t4f1_execution_candidate_v7_independent_audit_2026_09_03/evidence/g32_evasion_replay.json`

Reproduction script:
`audit_v52_t4f1_execution_candidate_v7_independent_audit_2026_09_03/scripts/g32_evasion_replay.py`

## Verdict

**BLOCKED — DO NOT SEAL / DO NOT RUN TASK 4F1.**

The independent auditor did not finish its final report, gate table, or hash manifest. However, the already-pushed independent evidence contains a load-bearing counterexample to the central structural claim for which V7 exists. Completing later gates cannot repair that counterexample without changing V7 bytes and starting a new candidate/audit cycle.

## Why V7 fails

V7's central claim is that the bound payload contains only four "functional files" and therefore no bound document can state a requirement or carry a contradictory restatement.

The checker establishes "functional-only" by exact set equality over these four names:

- `v52_t4f1_beam_retrieval.py`
- `DEPENDENCY_LOCK.txt`
- `RUN_AUTHORIZATION_TEMPLATE.json`
- `candidate_package_preflight.py`

The checker does not establish that the contents of those files are incapable of carrying narrative or normative text.

The independent Gate 3.2 replay explicitly attacks an existing BOUND functional file. For every V6 evasion class, it appends the test payload to `DEPENDENCY_LOCK.txt`. Without resealing, the hash check blocks. After recomputing the inventory and seal, the same modified bound functional file passes the V7 checker.

The pushed evidence reports `survivor_count = 18`. Nine survivors are the resealed-bound-functional-file cases and nine are unbound-seal cases. The bound-file survivors alone are sufficient to defeat the inference from filename class to semantic content.

This is not merely "coverage V7 intentionally gives up." It falsifies the stronger sentence in V7's checker that, because the payload names are functional, "there is no bound document in which a requirement could be restated at all."

A file called `DEPENDENCY_LOCK.txt` remains a text file and can carry arbitrary requirement-like prose. A Python or JSON file can likewise carry comments, strings, docstrings, fields, or inert data that a human or later tool may treat as normative. Filename set equality proves package shape, not semantic non-narrativity.

## Prompt stop rule

The controlling audit prompt requires BLOCKED for any surviving evasion, defeated set-equality check, coverage loss materially reproducing the CC-01 risk, semantic drift, outcome-capable execution, valid authorization construction, or candidate mutation.

The independent evidence contains surviving bound-file evasions. Therefore the audit verdict is forced to BLOCKED. There is no scientific or governance value in spending additional effort completing Gates 1, 4, or 5 for V7 as if a PASS remained reachable.

## Accepted facts carried forward

The following evidence remains useful and is not invalidated by this verdict:

- V7 runner is byte- and AST-identical to accepted V4 runner.
- The runner does not import or name the V7 checker.
- V7 removed the three V6 narrative files from the candidate namespace.
- Preflight/authorization guard evidence remains outcome-free.
- No Task 4F1 run/finalize invocation is authorized by this adjudication.
- No HMAC key or valid production authorization is created.
- Retrieval-quality outcome access remains FORBIDDEN.
- Scientific preregistration bytes and approvals are unaffected.

## Consequence

Do not seal V7 as an accepted execution package.

Do not build another generalized scanner.

Do not reopen the already-frozen scientific preregistration.

The next execution candidate must solve the packaging problem structurally without making the invalid implication "approved filename => incapable of carrying normative content."

A viable next target should be narrower: bind only bytes whose executable interpretation is already authoritative, and make any non-executable configuration/template bytes either (a) machine-derived from that authority, or (b) explicitly schema-constrained to a minimal typed data structure whose semantics are checked by the consumer. Do not claim that a file is non-narrative merely because of its name.

## Independence accounting

The counterexample evidence was created and pushed by the prior independent-auditor session at commit `16dc613...`.

This Head Researcher decision only adjudicates that existing evidence against the controlling prompt. It does not relabel Head Researcher work as an independent audit.

## Outcome boundary

- `--mode run` invoked by this adjudication: 0
- `--mode finalize` invoked by this adjudication: 0
- HMAC key set/inspected: false
- valid production authorization constructed: false
- real BEAM retrieval performed: false
- retrieval-quality outcome computed/read/reported: false
- V7 candidate bytes modified: false
