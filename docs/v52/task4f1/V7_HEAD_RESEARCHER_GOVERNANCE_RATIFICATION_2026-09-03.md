# V52 Task 4F1 — Head Researcher Governance Ratification

Date: 2026-09-03  
Role: Head Researcher  
Reviewed repository state: `main @ 1dec1212d6326c6d40552d65a8a17aae368de3fd`

## Decision summary

This artifact resolves three governance questions only. It does **not** approve the Task 4F1
scientific preregistration, does **not** accept the in-flight V7 independent audit, does **not**
seal any execution package, and does **not** authorize any retrieval-quality execution.

Task 4F1 remains:

- preregistration: `BLOCKED`
- run: `BLOCKED`
- retrieval-quality outcome access: `FORBIDDEN`

### G-1 — V7 packaging direction

**RATIFIED IN PRINCIPLE, WITH A PRE-SEAL DOCUMENTATION CONDITION.**

The governance direction is accepted: do not build a third generalized scanner. After the V5 and
V6 failures, the package may reduce its claim to a small, recursively closed set of functional
files and remove narrative prose from the bound payload. A structural file-set/closure claim is
preferable to another textual consistency mechanism that claims more than it can establish.

The current V7 functional closure is consistent with that direction: the declared bound payload is
the runner, dependency lock, inert authorization template, and package checker; the inventory and
seal are metadata around that closure.

However, this ratification does **not** ratify the current operator-facing documentation as safe for
sealing. The unbound V7 documents are outside the candidate closure, but their present wording can
still reproduce the human-operator risk that motivated CC-01:

- `docs/v52/task4f1/V7_EXECUTION_SPEC_NON_NORMATIVE.md` is named non-normative but its body still
  calls itself a "Byte-Bound Execution Specification", says that it "binds implementation
  details", and uses "sole normative source" language.
- `docs/v52/task4f1/V7_CANDIDATE_README_NON_NORMATIVE.md` still directs the reader to an
  `EXECUTION_SPEC.md` for "exact implementation interpretations that require independent
  acceptance" and its V7 section describes a prior narrative-literal prohibition/scanner-style
  design rather than the present functional-only set-equality design.

A filename suffix alone is not a sufficient governance control when the document body tells a human
reader that the document is binding or normative.

Therefore, before any V7 sealing decision, the operator-facing V7 documents must be made
unambiguously explanatory-only. The smallest acceptable remediation is:

1. Put a prominent first-screen declaration on each V7 operator-facing document:
   `NON-NORMATIVE / EXPLANATORY ONLY — MUST NOT BE USED AS AN EXECUTION AUTHORITY`.
2. Remove or rewrite language claiming that those documents are byte-bound, binding, normative, a
   sole normative source, or required for independent acceptance.
3. Remove stale V5/V6/V7 mechanism descriptions that could cause an operator to infer a requirement
   absent from the bound functional artifacts.
4. State the execution-authority precedence explicitly: the accepted runner bytes and their module
   constants, the bound dependency lock, the future sealed preregistration, and the future signed
   run authorization control execution. Explanatory docs cannot override them; on conflict, the
   explanatory document is wrong.
5. Do not add another scanner or make these explanatory documents part of the V7 bound payload merely
   to police their prose.

This condition is a governance/documentation repair, not a rejection of the reduced V7 package
architecture. Do not mutate the exact V7 candidate or the commit currently under independent audit
while that audit is in flight.

The in-flight independent auditor remains responsible for deciding whether the exact V7 package
claim is technically established and whether the coverage reduction is acceptable on the audited
bytes. Even a technical PASS does not waive the documentation condition above.

### G-2 — authorization-template schema deviation

**RATIFIED.**

The standing use of the V4 authorization schema is correct and is no longer an unratified deviation.

The retrieval runner is intentionally byte-identical to the independently accepted V4 runner and
verifies the literal runtime schema:

`V52_T4F1_RUN_AUTHORIZATION_V4`

The V7 inert template therefore correctly identifies itself as:

`V52_T4F1_RUN_AUTHORIZATION_V4_TEMPLATE_ONLY`

Package version and authorization-schema version are different version domains. Renaming the schema
to V5, V6, or V7 without changing the runner would create an authorization artifact the shipped
runner rejects. Conversely, changing the runner only to advance a label would destroy the
byte-identity basis of the accepted implementation evidence and require a new implementation audit.

Standing rule: while the accepted runner remains byte-identical to V4, any real future Task 4F1 run
authorization must use the exact schema and signed-field contract that this runner verifies. A
package-version rename is forbidden unless accompanied by an intentional runner/schema change and
the corresponding fresh audit.

This ratification does not create an authorization. The current template remains inert,
`NOT_AUTHORIZED`, unsigned, and incapable of permitting Task 4F1 execution.

### G-3 — current co-chair seat

**ESTABLISHED BY HEAD RESEARCHER AUTHORITY: CLAUDE HOLDS THE CURRENT CO-CHAIR SEAT EFFECTIVE
2026-09-03.**

The historical Codex co-chair artifacts of 2026-09-02 remain valid, hash-bound historical governance
decisions. They are not revoked or rewritten. They do not, however, define the current occupant
after this artifact.

From this decision forward, the research-program co-chair role is assigned to **Claude** unless a
later Head Researcher governance artifact explicitly changes that assignment.

Role identity does not waive independence requirements. A Claude session that prepared or authored
an artifact cannot independently audit or independently co-chair-review that same artifact. When
cold-start independence is required, the reviewing session must be distinct from the preparing
session and must derive its evidence from the exact repository bytes rather than from another
session's narrative.

The Continuity Lead remains a preparation/state-writing role and does not acquire sealing authority
merely because the current co-chair seat is held by Claude. Head Researcher final approval/veto,
co-chair review, independent audit, and Continuity Lead preparation remain distinct authorities.

## Effect on work already in flight

This artifact does not pre-judge either running review:

- the scientific review of the preregistration draft;
- the cold-start independent audit of V7.

Both must finish on their commissioned exact targets and return pushed, hash-verifiable artifacts.
Their evidence must be evaluated separately.

The next sealing decision, if any, requires at minimum:

1. an acceptable scientific preregistration review and subsequent Head Researcher decision;
2. an acceptable independent V7 audit;
3. satisfaction of the V7 explanatory-document condition in G-1;
4. continued adherence to the V4 authorization-schema ruling in G-2; and
5. no violation of the outcome boundary.

## Outcome-boundary declaration

This governance review performed no Task 4F1 retrieval-quality run, no finalize operation, no valid
production authorization construction, no HMAC-key setup, no real query ranking, and no inspection,
calculation, inference, or comparison of BEAM retrieval-quality outcomes.

Nothing is sealed, preregistered, or authorized by this artifact.
