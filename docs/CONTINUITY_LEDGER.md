# Continuity Ledger

This append-only ledger lets a new agent recover the exact operational state without relying on any prior chat. It is not a scientific-result log and cannot authorize Task 4F1.

## Update rule

For every load-bearing stage transition, append one entry before handing work off. Do not edit or reorder prior entries. A transition is incomplete unless the entry names its predecessor anchor, changed paths, verification evidence, explicit status, hard stops, and exactly one next action.

## Entry schema

```text
L-NNN
timestamp_utc:
actor_role:
predecessor_commit_or_tag:
scope:
changed_or_created_paths:
verification:
outcome_boundary:
status:
next_single_action:
handoff_payload:
```

## Entries

### L-001

```text
timestamp_utc: 2026-09-01T00:00:00Z
actor_role: Head Researcher
predecessor_commit_or_tag: v52-4f1-v3-audit-handoff-2026-09-01-r2 / e1b5731
scope: Establish crash-safe and multi-agent continuity controls for the V52 Task 4F1 V3 audit stage.
changed_or_created_paths: START_HERE_V52_4F1.md; ops/CURRENT_STATE.json; docs/CONTINUITY_PROTOCOL.md; docs/CONTINUITY_LEDGER.md; tools/verify_continuity_state.py; README.md; PROJECT_DOCUMENTATION_MANIFEST.md
verification: python -B tools/verify_continuity_state.py must PASS before an agent acts on this state.
outcome_boundary: No Task 4F1 run/finalize invocation, valid authorization construction, HMAC key, real retrieval ranking, metric or arm outcome access.
status: V52_4F1_V3_INDEPENDENT_AUDIT_PENDING
next_single_action: An isolated cold-start auditor executes only prompts/V52_TASK_4F1_EXECUTION_CANDIDATE_V3_INDEPENDENT_AUDIT_PROMPT_2026-09-01.md.
handoff_payload: commit/tag; verifier output; auditor output namespace; recursive audit manifest; report; gate table; command log; explicit verdict.
```

### L-002

```text
timestamp_utc: 2026-09-01T11:00:00Z
actor_role: Head Researcher / Continuity Lead (claiming stage for isolated independent auditor)
predecessor_commit_or_tag: v52-4f1-v3-continuity-2026-09-01 / 40db3c5 (successor of v52-4f1-v3-audit-handoff-2026-09-01-r2 / e1b5731)
scope: Stage A of the cold-start outcome-free V3 independent audit. Provision the locked Python 3.12.13 environment and the pinned BEAM corpus, create the isolated auditor worktree/branch and the new audit namespace. No audit verdict is issued in this entry.
changed_or_created_paths: ops/CURRENT_STATE.json; docs/CONTINUITY_LEDGER.md
verification: Clean worktree at 40db3c5; python -B tools/verify_continuity_state.py PASS; independent re-hash of all six state anchors 6/6 OK, 0 mismatch; V3 candidate recursive enumeration exactly 8 files, 0 nested dirs, 0 __pycache__; prompt-declared preflight, V2 report, 4F0 seal, restricted protocol, BEAM tree manifest and dependency-lock anchors independently re-hashed and matched.
outcome_boundary: No --mode run, no --mode finalize, no run_archives/evaluate_archive/finalize_results on real BEAM data, no V52_T4F1_AUTH_HMAC_KEY_HEX, no valid authorization/HMAC construction, no real retrieval ID/distance/metric/arm outcome access.
status: IN_PROGRESS
next_single_action: Provision locked environment and pinned corpus, then execute only the outcome-free gates of prompts/V52_TASK_4F1_EXECUTION_CANDIDATE_V3_INDEPENDENT_AUDIT_PROMPT_2026-09-01.md in the isolated auditor namespace.
handoff_payload: branch audit/v52-t4f1-v3-independent-2026-09-01; audit namespace audit_v52_t4f1_execution_candidate_v3_independent_audit_2026_09_01/; report, gate table, command log and recursive hash manifest to follow at stage close.
governance_note: The V3 audit prompt forbids the auditor from committing or pushing. That constraint binds the auditor worker. Continuity commits of state and ledger are made by the Head Researcher role only, and the resulting audit package is carried on an audit/... branch per CHAIN_OF_CUSTODY rule 2; main advances only by a verified state transition. Candidate, seal, manifest, pinned-corpus and historical audit namespaces stay read-only throughout.
environment_findings: Container default python is 3.11.15 and the locked scientific stack is absent; system python3.12 is 3.12.3, and uv offers no prebuilt 3.12.13. CPython 3.12.13 source is reachable upstream and the pinned BEAM repository is reachable over git, so both prerequisites are provisionable rather than blocking.
```

### L-003

```text
timestamp_utc: 2026-09-01T13:00:00Z
actor_role: Independent auditor (isolated worktree/branch), state closed by Head Researcher / Continuity Lead
predecessor_commit_or_tag: v52-4f1-v3-continuity-2026-09-01 / 6c5459c (L-002 IN_PROGRESS claim)
scope: Cold-start, outcome-free independent audit of the exact Task 4F1 V3 execution candidate, per prompts/V52_TASK_4F1_EXECUTION_CANDIDATE_V3_INDEPENDENT_AUDIT_PROMPT_2026-09-01.md.
changed_or_created_paths: audit_v52_t4f1_execution_candidate_v3_independent_audit_2026_09_01/ (on branch audit/v52-t4f1-v3-independent-2026-09-01, commit a590f629); ops/CURRENT_STATE.json; docs/CONTINUITY_LEDGER.md; START_HERE_V52_4F1.md; docs/RESEARCH_PROGRAM_STATUS_2026-08-31.md
verification: Locked environment provisioned exactly (Python 3.12.13 built from python.org source; NumPy 2.3.2; SciPy 1.16.1; scikit-learn 1.7.1; psutil 7.0.0; five single-thread controls). Pinned BEAM corpus materialized at commit 3e12035532eb85768f1a7cd779832b650c4b2ef9; canary archive git blob SHA1 bbabe6fcf7290e34636fe5e25c748ebefbdbbcfa matches the accepted pinned tree manifest. G1 8/8 files and all anchor hashes matched; G2 change isolation proven at AST level; G4/G5/G6/G7 negative-control matrix 29/29; G8 bug hunt 9/9; D2 fail-closed authorization and leakage statics clean.
outcome_boundary: 0 CLI --mode run; 0 CLI --mode finalize; 0 HMAC key environment sets; no valid authorization constructed; no real retrieval ranking; retrieval quality computed/read/reported = false/false/false; candidate bytes unmodified. finalize_results was exercised only on auditor-authored synthetic fixtures, never on real BEAM data. No forbidden outcome computation occurred, so this entry is BLOCKED, not CONTAMINATED.
status: BLOCKED
next_single_action: Head Researcher decides the G3 remediation direction (bind BLAS/LAPACK build and CPU kernel dispatch in the environment lock, or replace bit-exact float canary digests with dispatch-stable quantities such as sign codes and integer Hamming distances), after which a new candidate must be prepared and independently re-audited. Do not seal, preregister or run Task 4F1.
handoff_payload: audit branch audit/v52-t4f1-v3-independent-2026-09-01 at a590f629; INDEPENDENT_V3_EXECUTION_AUDIT_REPORT.md; GATE_TABLE.csv; COMMAND_LOG.txt; evidence/*.json; INDEPENDENT_V3_EXECUTION_AUDIT_HASHES.json binding the exact V3 anchors.
blocking_finding: Gate 3. The pinned 100K::12 representation canary does not reproduce in a fully lock-conformant environment. Structure is correct (392 units; 392x96 and 1x96 shapes) and the code is locally deterministic across three repeat runs, but the bit-exact float digests differ from the sealed values. Holding code, data and all locked versions constant and varying only OPENBLAS_CORETYPE produced four distinct archive digests across six dispatches, none equal to the pinned digest, while the candidate's own verify_environment() accepted every variant. The dependency lock pins package versions and thread counts but not the BLAS/LAPACK build or CPU microarchitecture dispatch that determine those bits, so a load-bearing gate is machine-bound rather than lock-bound.
governance_note: The V3 audit prompt forbids the auditor from committing or pushing, so audit outputs were produced without commit inside the auditor namespace and then carried by the Head Researcher role onto an audit/... branch per CHAIN_OF_CUSTODY rule 2. That package has NOT been merged into main; merging requires an explicit Head Researcher acceptance decision. Disclosure: in this session one agent held both the Head Researcher/Continuity Lead and independent-auditor roles. The auditor did not implement V3 (a prior agent did) and accepted no prior chat, narrative or claimed verdict as evidence, re-deriving every declared hash and behaviour independently; a successor may nevertheless commission a second independent audit of these same bytes if stricter role separation is required.
```

### L-004

```text
timestamp_utc: 2026-09-01T13:20:00Z
actor_role: Head Researcher / Continuity Lead
predecessor_commit_or_tag: L-003 / 531d41b
scope: Record the anchor substitution for the L-003 closed state. No research state, verdict, gate result or artifact changes.
changed_or_created_paths: ops/CURRENT_STATE.json; docs/CONTINUITY_LEDGER.md
verification: git push of refs/tags/v52-4f1-v3-audit-blocked-2026-09-01 was refused with HTTP 403; a lightweight test tag to the same commit was refused identically, while branch pushes to main, audit/... and state/... all succeeded. Branch anchor state/v52-4f1-v3-audit-blocked-2026-09-01 pushed at 531d41bacc3da1670c07b4ea269d4ac34e8624e2.
outcome_boundary: Unchanged. No run/finalize, authorization, HMAC key or retrieval outcome access.
status: PASS
next_single_action: Unchanged from L-003 - Head Researcher decides the Gate 3 remediation direction. An operator with tag-push rights should additionally publish the annotated tag v52-4f1-v3-audit-blocked-2026-09-01 at 531d41b.
handoff_payload: main at 531d41b; pushed branch anchor state/v52-4f1-v3-audit-blocked-2026-09-01; audit package at audit/v52-t4f1-v3-independent-2026-09-01 a590f629.
```

### L-005

```text
timestamp_utc: 2026-09-01T14:00:00Z
actor_role: Head Researcher decision recorded by Continuity Lead; execution by Implementer role in an isolated worktree/branch
predecessor_commit_or_tag: L-004 / 18a7356 (pushed anchor branch state/v52-4f1-v3-audit-blocked-2026-09-01)
scope: Act on the BLOCKED V3 audit. Head Researcher accepted remediation option 2 from the V3 audit report: stop treating bit-exact float digests as a load-bearing gate and replace them with quantities that are stable across BLAS/LAPACK kernel dispatch, plus a tolerance-based invariance check. Prepare a NEW Task 4F1 V4 execution candidate namespace. V3, V2, V1, their seals and manifests, the sealed 4F0 namespace and the pinned corpus remain read-only and unmodified.
changed_or_created_paths: ops/CURRENT_STATE.json; docs/CONTINUITY_LEDGER.md; then task4f1_execution_candidate_v4_2026_09_01/ and its preflight evidence on branch impl/v52-t4f1-v4-2026-09-01
verification: Before any V4 design is fixed, empirically determine which representation quantities are invariant across OPENBLAS_CORETYPE dispatch on the pinned 100K::12 archive. The V4 canary is acceptable only if its declared expectations reproduce identically across every tested dispatch.
outcome_boundary: No --mode run, no --mode finalize, no run_archives/evaluate_archive/finalize_results on real BEAM data, no V52_T4F1_AUTH_HMAC_KEY_HEX, no valid authorization or HMAC construction, no real retrieval top-3 IDs, distances, metrics or arm outcomes. The V4 canary must remain representation-only: no ranking of any query against the archive and no gold access.
status: IN_PROGRESS
next_single_action: Run the dispatch-stability study, then build and validate the V4 candidate and its implementer-side preflight evidence.
handoff_payload: branch impl/v52-t4f1-v4-2026-09-01; new candidate namespace; dispatch-stability evidence; preflight evidence; hashes.
role_constraint: This agent implements V4 and therefore CANNOT audit it. Per docs/CONTINUITY_PROTOCOL.md the Head Researcher cannot call its own implementation work an independent audit. V4 requires a separate cold-start independent audit before any sealing decision, and Task 4F1 remains BLOCKED for preregistration and run regardless of that audit's outcome.
```

### L-006

```text
timestamp_utc: 2026-09-01T15:00:00Z
actor_role: Implementer (isolated worktree/branch), state closed by Head Researcher / Continuity Lead
predecessor_commit_or_tag: L-005 / c56c705
scope: Prepare the Task 4F1 V4 execution candidate remediating the V3 Gate 3 reproducibility defect, under Head Researcher remediation option 2. V3, V2, V1, their seals and manifests, the sealed 4F0 namespace and the pinned corpus were not modified.
changed_or_created_paths: task4f1_execution_candidate_v4_2026_09_01/; task4f1_execution_candidate_v4_preflight_2026_09_01/; prompts/V52_TASK_4F1_EXECUTION_CANDIDATE_V4_INDEPENDENT_AUDIT_PROMPT_2026-09-01.md; ops/CURRENT_STATE.json; docs/CONTINUITY_LEDGER.md; START_HERE_V52_4F1.md; docs/RESEARCH_PROGRAM_STATUS_2026-08-31.md
verification: Dispatch-stability study on the pinned 100K::12 archive across SkylakeX, Haswell, Nehalem, Sandybridge, Zen and Barcelona. Raw float digests gave 4 distinct values; sign-code digests gave exactly 1. Max cross-dispatch absolute difference 1.202e-13 against a minimum absolute value of 4.089e-07 (archive) and 7.036e-04 (query), a margin of roughly 3.4e6, with 0 of 37,632 entries inside the noise band. V4 --mode preflight PASSES on all six dispatches, where V3 passed on none. B1/B2/B3 synthetic regression 29/29 preserved against V4. V3-to-V4 change isolation confirmed at AST level: only the canary body, the sign_code_sha256 and describe_numerical_backend helpers, the canary constants, verify_environment provenance and schema version literals differ; every other function including the whole numerical core is unchanged. Candidate package preflight PASS with recursive closure and fail-closed authorization.
outcome_boundary: 0 CLI --mode run; 0 CLI --mode finalize; 0 HMAC key environment sets; no valid authorization constructed; no real retrieval ranking; retrieval quality computed/read/reported = false/false/false; no V3 or earlier candidate bytes modified. All B1/B2/B3 exercises used auditor/implementer-authored synthetic fixtures, never real BEAM data. The V4 canary remains representation-only: no ranking, no probing questions, no gold.
status: PASS
next_single_action: A separate cold-start independent auditor executes only prompts/V52_TASK_4F1_EXECUTION_CANDIDATE_V4_INDEPENDENT_AUDIT_PROMPT_2026-09-01.md against the exact V4 bytes.
handoff_payload: branch impl/v52-t4f1-v4-2026-09-01 at 809059b, merged to main; V4 runner f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8; inventory fe1de9c7160191f7a001ecadb928057411cc7b560a3f8f8a9130c6d3ceb1ba5e; seal 1bf740f573fc74c6e8aa6e23a3f07a5bcc97a10d1fa7e6e7358560e1598f06e9; preflight manifest 4f78b5c8b184ad0ecfbbf444ffddbbcd076c6b78fa65c4b0d76696259f1c930f.
role_constraint: The agent that prepared V4 CANNOT audit it. Per docs/CONTINUITY_PROTOCOL.md an independent auditor must be cold-start and must not treat any other agent's chat, narrative or claimed verdict as evidence. The V4 preflight package is implementer evidence, not independent sign-off, and its dispatch-stability claims must be independently re-derived. A passing V4 audit would permit only a Head Researcher sealing decision; Task 4F1 preregistration and run remain separately BLOCKED.
```

### L-007

```text
timestamp_utc: 2026-09-01T16:00:00Z
actor_role: Head Researcher / Continuity Lead
predecessor_commit_or_tag: L-006 / 8700098
scope: Record the Head Researcher custody decision requested by the V4 independent auditor, and narrowly authorize persistence of its audit package. No verdict is accepted and nothing is sealed by this entry.
changed_or_created_paths: ops/CURRENT_STATE.json; docs/CONTINUITY_LEDGER.md
decision: The V4 audit package is to be persisted on a NEW branch audit/v52-t4f1-v4-independent-2026-09-01. This follows CHAIN_OF_CUSTODY rule 2 and the V3 precedent (audit/v52-t4f1-v3-independent-2026-09-01 at a590f629). Committing audit output to main is refused: main is canonical ACCEPTED state, and landing an unreviewed audit there would conflate "produced" with "accepted". Leaving it uncommitted is refused: the auditor container is ephemeral and the evidence would be destroyed.
authorization: The V4 audit prompt forbids the auditor from committing or pushing. The Head Researcher, as the owner of that prompt and of this decision, narrowly releases that constraint for one purpose only: pushing the audit namespace to the named audit/... branch. The auditor must not modify any tracked file, must not commit to main, must not merge, and must not open a pull request. The constraint exists to stop an auditor mutating sealed artifacts or self-accepting into canonical state, not to destroy evidence; a fresh audit/... branch touching no tracked file serves that purpose intact.
hashes_file_ruling: INDEPENDENT_V4_EXECUTION_AUDIT_HASHES.json must NOT be rewritten to embed its own commit SHA. A file cannot hash the commit that contains it, and a second commit would break its self-verification. The commit SHA is recorded in this ledger instead, exactly as L-003 recorded the V3 audit commit.
verification: In the Head Researcher container the namespace audit_v52_t4f1_execution_candidate_v4_independent_audit_2026_09_01/ is ABSENT and no V4 audit branch exists on the remote; the package is unreachable and unverified here. Independent arithmetic cross-check of the relayed figures reconciles: 37,728 = 37,632 archive entries + 96 query entries; 4.0888e-07 / 1e-9 = 408.88x the required margin; 4.0888e-07 / 1.2018e-13 = 3.402e6x the measured noise. These agree with the L-006 preparation measurements, but agreement of relayed numbers is not acceptance.
outcome_boundary: Unchanged. Task 4F1 preregistration BLOCKED, run BLOCKED, retrieval-quality outcome access FORBIDDEN. No --mode run, no --mode finalize, no HMAC key, no valid authorization.
status: IN_PROGRESS
next_single_action: Auditor pushes the package to audit/v52-t4f1-v4-independent-2026-09-01; the Head Researcher then re-derives its hashes and boundary declarations independently before any acceptance or sealing entry is written.
role_separation_note: This V4 audit was performed by a different agent from the one that prepared V4, which closes the dual-role weakness disclosed in L-003. That strengthens the audit's standing once its artifacts are actually verifiable.
environment_warning: Tag pushes are refused in this project environment with HTTP 403 for annotated and lightweight tags alike, while branch pushes succeed. If the auditor's push of a tag fails, that is environmental and not a repository-integrity event; the branch is the anchor.
```

### L-008

```text
timestamp_utc: 2026-09-02T13:30:00Z
actor_role: Head Researcher / Continuity Lead
predecessor_commit_or_tag: L-007 / 8abca21
scope: Independently verify the pushed V4 independent-audit package, accept it, seal the V4 implementation, and disposition the four non-blocking observations. No candidate byte is modified.
changed_or_created_paths: docs/v52/task4f1/V4_HEAD_RESEARCHER_ACCEPTANCE_2026-09-02.json; ops/CURRENT_STATE.json; docs/CONTINUITY_LEDGER.md; START_HERE_V52_4F1.md; docs/RESEARCH_PROGRAM_STATUS_2026-08-31.md
verification: Audit commit 641568d8b78af97eb69c9dc4e0434e7b6564a26c matches the declared SHA; its parent is 8700098, the exact tree the audit examined; origin/main untouched at 8abca21; diff versus parent is 31 files, all additions, all inside the audit namespace, 0 deletions, 0 forbidden artifacts staged. INDEPENDENT_V4_EXECUTION_AUDIT_HASHES.json hashes to the declared 8dcb2fb8b23980fd3fe0e65a25834e1af259bdef855ed577ae40ab4a43ee4387 and self-verifies 30/30 with 0 mismatch and 0 missing; reverse coverage shows 0 undeclared files on disk. The audit binds the real V4 bytes: implementation f96cba2c, inventory fe1de9c7, seal 1bf740f5. COMMAND_LOG shows 16 launches, 6 of them candidate --mode preflight, 0 launches carrying --mode run or --mode finalize, and 3 REJECTED_BEFORE_LAUNCH harness self-tests timestamped before any launch; the HMAC environment variable is never set anywhere in the package. Gate 3 raw evidence holds 6 independent reconstructions and 6 candidate preflight outputs: 1 distinct sign digest, 4 distinct raw float digests, and the per-dispatch float digests reproduce the Head Researcher's own V3 measurements exactly (SkylakeX fae4b3c0, Haswell/Zen 5ded9fdd, Nehalem/Barcelona fef061e5, Sandybridge ec3c5f44). The auditor's cohort path differs from the implementer's but the two files are byte-identical at 9b70e16f, equal to the sealed cohort anchor, so it is a path difference and not a cohort difference.
outcome_boundary: Unchanged and independently confirmed in the accepted package: 0 --mode run, 0 --mode finalize, 0 HMAC key environment sets, no valid authorization constructed, no real retrieval ranking, retrieval quality computed/read/reported all false, candidate bytes unmodified, no sealed or historical namespace modified.
status: PASS
next_single_action: Head Researcher decides whether to preregister Task 4F1. A passing audit does not grant that; it is a separate decision.
handoff_payload: acceptance record docs/v52/task4f1/V4_HEAD_RESEARCHER_ACCEPTANCE_2026-09-02.json (sha256 f04eecd5f1b9e81aa2bb90830d3c678deb9dcf80adc335130e54314ac5f6c547); accepted audit branch audit/v52-t4f1-v4-independent-2026-09-01 at 641568d8.
seal_mechanism: V4 is sealed by external record, not by editing the candidate. Flipping the in-file status string would change CANDIDATE_EXECUTION_SEAL.json's SHA256 and break the binding the audit established, so CANDIDATE_EXECUTION_SEAL.json still reads PREPARED_NOT_INDEPENDENTLY_AUDITED while the authoritative status is SEALED_BY_HEAD_RESEARCHER_2026-09-02 as recorded here and in the acceptance record. A reader must treat the acceptance record, not the in-file string, as authoritative.
observation_disposition: Two stale V3 strings (package-preflight docstring, run-authorization template) are accepted as documented conditions because fixing them would change the payload inventory and seal and force a full re-audit for cosmetic text. The canary's inability to distinguish >= from > is accepted as structurally bounded, since CANARY_SIGN_MARGIN fails closed before an exactly-zero entry could matter. The POSIX hard-link dependency of the os.link commit path is accepted as a binding preregistration condition: any future run must execute on a POSIX filesystem supporting hard links, and the preregistration must state this.
role_separation: V4 was implemented by this agent and audited by a different agent that imported no V3 conclusions (v3_conclusions_imported false). This closes the dual-role weakness disclosed in L-003.
```

### L-009

```text
timestamp_utc: 2026-09-02T15:00:00Z
actor_role: Continuity Lead (sole writer) recording the co-chair's REQUEST CHANGES decision
predecessor_commit_or_tag: L-008 / a5ee73fa2df29683a8a68fcb2f17461a607cc011
scope: Record the co-chair review of L-008, independently confirm its blocking finding, withdraw the V4 package seal, and set the V5 remediation route. No candidate byte is modified by this entry.
changed_or_created_paths: ops/CURRENT_STATE.json; docs/CONTINUITY_LEDGER.md; START_HERE_V52_4F1.md; docs/RESEARCH_PROGRAM_STATUS_2026-08-31.md
cochair_decision: REQUEST CHANGES. The V4 independent-audit evidence is accepted as authentic, hash-consistent and valid for its nine implementation gates. The broader L-008 conclusion that the complete V4 execution package may stand sealed is NOT co-signed.
blocking_finding_CC01: task4f1_execution_candidate_v4_2026_09_01/EXECUTION_SPEC.md, a file bound in PAYLOAD_HASHES.json at SHA256 de1d3689f113607c1a7d5425c5795c03faeeeae74e7a4bb75953a57c9691f748, contains two mutually exclusive normative canary definitions. Line 44 still requires the raw array SHA256 values to reproduce the superseded V3 digests 25089a07... and e422490a..., while lines 110-112 require the V4 sign-code digests 7365b6c4... and 5e40a5d1.... Only the latter is implemented and audited. V3 was superseded precisely because those raw-float digests vary across conformant BLAS dispatches, so the line-44 requirement is unsatisfiable on conformant hardware and would mislead a cold-start successor.
independent_confirmation: The Continuity Lead reproduced CC-01 directly by grep on the bound file; both digest pairs are present at the stated lines and the file is listed in PAYLOAD_HASHES.json. The finding is CONFIRMED.
root_cause_and_accountability: This defect was introduced by the Continuity Lead when preparing V4. EXECUTION_SPEC.md was updated by a blanket "V3" -> "V4" label substitution plus an appended canary section, which bumped labels and added the correct specification without removing the superseded normative text. The V4 audit prompt scoped Gate 2 to runner source and AST change isolation and required no semantic contradiction scan across bound prose, so the audit could pass all nine gates while this defect survived. Both the authoring method and the prompt scope are at fault; neither is the auditor's error.
tier_table_verification: The co-chair's frozen tier composition table was independently recomputed from the sealed cohort and matches exactly: 100K 355 questions / 20 archives / 3.08 mean gold / 96 structural ALL@3 zeros; 500K 629 / 35 / 4.26 / 168; 1M 553 / 31 / 8.59 / 253; 10M 175 / 10 / 7.47 / 70; totals 1712 questions and 96 archives.
agreements_reached: (1) Single writer confirmed: the Continuity Lead alone writes CURRENT_STATE.json and the ledger; the co-chair writes only review artifacts on a separate branch and holds approval/veto. (2) Seal mechanism: detached attestation is the agreed correct mechanism; an audited candidate is never edited in place to change its historical submission status. V5 is required for the CONTENT defect, not to mutate the V4 seal. (3) Scientific route: option B. (4) Tier-stratified analysis is the primary scientific interest, bounded as an association across fixed benchmark strata and never as a causal context-length effect.
outcome_boundary: Unchanged. No --mode run, no --mode finalize, no HMAC key, no valid authorization, no real ranking, no retrieval-quality outcome computed, read or reported.
status: BLOCKED
next_single_action: Build the V5 candidate namespace correcting CC-01 and the stale V3 text, keeping the execution runner byte-identical to the accepted V4 runner, and write the V5 independent-audit prompt including a mandatory cross-payload semantic-consistency gate.
open_item_for_cochair: The co-chair review was relayed in chat and is NOT yet a pushed artifact, so it cannot be hash-bound. The same standard applied to the V4 auditor and to the Continuity Lead applies here: the review must be pushed to a co-chair branch so this ledger entry can cite its exact commit and file SHA256. Until then this entry cites the decision content only.
```

### L-010

```text
timestamp_utc: 2026-09-02T16:00:00Z
actor_role: Continuity Lead (sole writer), acting under co-chair approval
predecessor_commit_or_tag: L-009 / cae73045097eb062c4cdc636af92b350b97a95ae
scope: Correct the stale open item in L-009, bind both co-chair review artifacts by commit and file hash, and claim the V5 declarative remediation stage. V1-V4 candidates, preflight packages, seals, manifests, audits and acceptance records remain byte-for-byte untouched.
changed_or_created_paths: ops/CURRENT_STATE.json; docs/CONTINUITY_LEDGER.md; then task4f1_execution_candidate_v5_2026_09_02/ and the V5 audit prompt on branch impl/v52-t4f1-v5-2026-09-02
correction_of_L009: L-009 recorded that the co-chair review was relayed in chat and not pushed. That was wrong. The review was already on GitHub; the Continuity Lead had simply not fetched the review branch before asserting it. L-009 is append-only and is NOT edited; the record is corrected here. Both artifacts are now fetched and independently hash-verified: branch codex/review-v52-t4f1-cochair-2026-09-02; REQUEST CHANGES at commit 776c45f333b262754aa0020e8043db54942d1bea with docs/v52/task4f1/V4_COCHAIR_REVIEW_2026-09-02.md at SHA256 1c85eb06831db742a3c0ab8018c56ea7eb47d60f560afb68fc4a1f457fd3af55; APPROVAL at commit 4bd32782c4148d15a632fb822dae8cab358892c6 with docs/v52/task4f1/V5_REMEDIATION_COCHAIR_APPROVAL_2026-09-02.md at SHA256 33124cb22f057641c8878e34a7b545ac98da5f0092a98a816a49d3e2f7c435d4. Both recomputed from the fetched blobs and matched exactly.
cochair_authorization: APPROVED - PREPARE V5 DECLARATIVE REMEDIATION ONLY. This authorizes V5 preparation and its independent delta audit. It does not authorize preregistration, run, finalize, HMAC-key construction or any outcome access.
binding_constraint: The V5 retrieval runner must be byte-identical to the accepted V4 runner at SHA256 f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8. If it differs, or any execution-affecting semantic change is found, the delta route stops and V5 needs a full cold-start audit scope plus a new co-chair review.
schema_versioning_note: Because the runner is byte-identical, every schema literal it verifies stays at its V4 value (V52_T4F1_RUN_AUTHORIZATION_V4, V52_T4F1_EXECUTION_CANDIDATE_SEAL_V4, V52_T4F1_ARCHIVE_RESULT_META_V4, V52_T4F1_POST_RUN_MANIFEST_V4, V52_T4F1_IMPLEMENTATION_PREFLIGHT_V4). V5 is therefore a PACKAGE version, not a schema version. Relabelling those literals to V5 would either change the runner, breaking the binding constraint, or make the payload fail closed against the runner it ships with. The normative-source map must state this explicitly so no successor "fixes" it.
outcome_boundary: Unchanged. No --mode run, no --mode finalize, no V52_T4F1_AUTH_HMAC_KEY_HEX, no valid authorization, no real ranking, no retrieval-quality outcome computed, read or reported.
status: IN_PROGRESS
next_single_action: Build V5 with the byte-identical runner, the corrected declarative payloads, the machine-readable normative-source map and the single-source preflight gate, then write the V5 delta-audit prompt.
handoff_payload: branch impl/v52-t4f1-v5-2026-09-02; V5 namespace; normative source map; preflight evidence; V5 audit prompt.
```

### L-011

```text
timestamp_utc: 2026-09-02T17:30:00Z
actor_role: Continuity Lead (sole writer), implementing under co-chair approval 4bd32782
predecessor_commit_or_tag: L-010 / 3605f63
scope: Close the V5 declarative remediation stage and hand off to a cold-start delta auditor. V1-V4 candidates, preflight packages, seals, manifests, audits and acceptance records remain byte-for-byte untouched.
changed_or_created_paths: task4f1_execution_candidate_v5_2026_09_02/; task4f1_execution_candidate_v5_preflight_2026_09_02/; prompts/V52_TASK_4F1_EXECUTION_CANDIDATE_V5_INDEPENDENT_DELTA_AUDIT_PROMPT_2026-09-02.md; ops/CURRENT_STATE.json; docs/CONTINUITY_LEDGER.md; START_HERE_V52_4F1.md; docs/RESEARCH_PROGRAM_STATUS_2026-08-31.md
verification: The V5 retrieval runner is byte-identical to the accepted V4 runner at f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8, and its AST is equal with docstrings stripped; DEPENDENCY_LOCK.txt is identical too. The only executable delta is candidate_package_preflight.py, an out-of-band checker the runner never imports. CC-01 is corrected: EXECUTION_SPEC.md now carries exactly one normative canary section and both superseded V3 raw-float digests are enumerated as deprecated literals. NORMATIVE_SOURCE_MAP.json enumerates 18 load-bearing concepts, each with one authoritative path plus locator, with every repetition typed as a derived mirror. The single-source gate passes with 18 concepts, 5 mechanically checked typed mirrors and 0 surviving deprecated literals, and it proves runner byte-identity. Candidate --mode preflight returns PASS. Ten negative fixtures all block, including a direct reintroduction of CC-01, a returning stale V3 authorization label, a truncated signed-fields mirror, a replaced fail-closed commitment, a seal claiming post-audit acceptance, a modified runner, a duplicated normative concept, an untyped mirror and a nested unbound file.
gate_design_note: The first implementation of the deprecated-literal scan exempted the declaring registry with a line-level heuristic and immediately failed against the source map itself. That was a real ambiguity in the design rather than a nuisance: a deprecated literal must live exactly one lawful place, the registry that declares it. The exemption was replaced with an exact rule that re-serialises the map without its deprecated_literals block and scans that, so the exemption cannot be widened by editing prose around a literal.
schema_versioning_decision: V5 is a PACKAGE version, not a schema version. Because the runner is byte-identical, every schema literal it verifies stays at its V4 value. The authorization template therefore declares V52_T4F1_RUN_AUTHORIZATION_V4, the schema the shipped runner actually verifies; naming it V5 would have made the payload fail closed against its own runner. This is recorded in NORMATIVE_SOURCE_MAP.json and EXECUTION_SPEC.md so a successor does not "correct" it.
outcome_boundary: 0 --mode run; 0 --mode finalize; 0 HMAC key environment sets; no valid authorization constructed; no real retrieval ranking; retrieval quality computed/read/reported all false; no V1-V4 candidate, seal, manifest, audit or acceptance record modified; no pinned corpus byte touched.
status: PASS
next_single_action: A cold-start auditor that did not prepare V5 executes only prompts/V52_TASK_4F1_EXECUTION_CANDIDATE_V5_INDEPENDENT_DELTA_AUDIT_PROMPT_2026-09-02.md and must derive the declarative classification from the bytes rather than import it.
handoff_payload: branch impl/v52-t4f1-v5-2026-09-02 at dc17f2c, merged to main; V5 runner f96cba2c (identical to accepted V4); inventory, seal, source map and preflight manifest hashes bound in ops/CURRENT_STATE.json anchors.
role_constraint: The Continuity Lead prepared V5 and cannot audit it. The delta-audit prompt instructs the auditor to treat the implementer package as an untrusted hypothesis, to re-derive the single-source gate rather than accept its output, and to state explicitly which conclusions rest on citing the V4 audit versus its own re-derivation. Any sealing decision requires both the Head Researcher and the co-chair; Task 4F1 preregistration and run remain separately BLOCKED.
```

### L-012

```text
timestamp_utc: 2026-09-02T18:00:00Z
actor_role: Continuity Lead (sole writer)
predecessor_commit_or_tag: L-011 / 2ad3c65
scope: Record that the co-chair is unavailable, and separate what remains authorized from what is now held. No candidate, seal, manifest, audit or corpus byte is touched.
changed_or_created_paths: ops/CURRENT_STATE.json; docs/CONTINUITY_LEDGER.md
situation: The co-chair (Codex) exhausted its usage limit on 2026-09-02 and cannot review further for now.
still_authorized: The standing co-chair approval at commit 4bd32782c4148d15a632fb822dae8cab358892c6 states that "the next permitted stage is V5 preparation followed by a different cold-start auditor". Commissioning the V5 independent delta audit therefore needs no new approval and may proceed. The auditor need not be the same system as the co-chair; it must simply be cold-start and must not have prepared V5.
now_held: Sealing V5 requires both the Head Researcher and the co-chair per L-011 and cannot proceed while the co-chair is unavailable. The Continuity Lead must NOT self-seal. Self-sealing is precisely the role concentration that produced the withdrawn L-008 seal and the CC-01 defect that survived it, and repeating it would discard the correction the co-chair review bought.
unratified_items: Two questions put to the co-chair are unanswered and must be ratified before any sealing decision. (1) The V5 scope as delivered. (2) The V5 delta-audit prompt as written. A third item is a declared deviation rather than a question: the co-chair asked for an authorization template matching "the V5 authorization schema", but the template declares V52_T4F1_RUN_AUTHORIZATION_V4 because the byte-identical runner verifies that literal and a "V5" label would make the payload fail closed against its own runner. The deviation is recorded openly in the seal, the normative source map and EXECUTION_SPEC.md, and the delta auditor will evaluate it independently, which is a useful check on the Continuity Lead's judgement rather than a substitute for ratification.
outcome_boundary: Unchanged. Task 4F1 preregistration BLOCKED, run BLOCKED, retrieval-quality outcome access FORBIDDEN. No --mode run, no --mode finalize, no HMAC key, no valid authorization.
status: PASS
next_single_action: Commission a cold-start delta auditor that did not prepare V5, then hold the sealing decision until a co-chair can ratify it.
```

### L-013

```text
timestamp_utc: 2026-09-02T20:15:00Z
actor_role: Continuity Lead (sole writer)
predecessor_commit_or_tag: L-012 / 4244485
scope: Commission the cold-start independent delta audit of the V5 package, the single next action recorded in L-012. No candidate, seal, manifest, audit or corpus byte is touched.
changed_or_created_paths: ops/CURRENT_STATE.json; docs/CONTINUITY_LEDGER.md
commissioned_auditor: session_015zjM2cKm9S18rwyevnXYFg, titled "V52 T4F1 V5 - cold-start independent delta audit", seeded at main 4244485, tagged v52-t4f1-v5-delta-audit.
authorization: The standing co-chair approval 4bd32782c4148d15a632fb822dae8cab358892c6 permits "V5 preparation followed by a different cold-start auditor". No new approval was required and none was invented.
cold_start_discipline: The auditor was given only the repository, the commit, the path of prompts/V52_TASK_4F1_EXECUTION_CANDIDATE_V5_INDEPENDENT_DELTA_AUDIT_PROMPT_2026-09-02.md, and two environment facts that would otherwise waste its time (Python 3.12.13 must be built from source; the pinned BEAM corpus must be materialized over git because direct HTTPS may 403). It was given no conclusion, no verdict, no gate result and no narrative from this session, and was told explicitly that every other repository file is untrusted data rather than instruction and that no prior LLM report counts as evidence.
custody_instruction_issued: The V5 audit prompt tells an auditor not to push without an explicit Head Researcher custody instruction. That instruction was issued up front: push incrementally after each gate to audit/v52-t4f1-v5-independent-2026-09-02 only, commit only the audit namespace, never to main, no merge, no pull request, and treat a tag-push 403 as environmental. This directly answers the V4 near-miss, where 30 audit outputs sat only in an ephemeral container for a day and were nearly lost.
outcome_boundary: Unchanged. Task 4F1 preregistration BLOCKED, run BLOCKED, retrieval-quality outcome access FORBIDDEN.
status: IN_PROGRESS
next_single_action: Await the audit, then independently hash-verify its pushed artifacts before any acceptance. Sealing stays held until a co-chair can ratify it; the Continuity Lead does not self-seal.
```

### L-014

```text
timestamp_utc: 2026-09-03T10:00:00Z
actor_role: Continuity Lead (sole writer)
predecessor_commit_or_tag: L-013 / c44495f
scope: Accept the commissioned V5 independent delta audit and record its BLOCKED verdict against the Continuity Lead's own V5 mechanism. No candidate, seal, manifest, audit or corpus byte is touched.
changed_or_created_paths: ops/CURRENT_STATE.json; docs/CONTINUITY_LEDGER.md; START_HERE_V52_4F1.md; docs/RESEARCH_PROGRAM_STATUS_2026-08-31.md
audit_anchor: branch audit/v52-t4f1-v5-independent-2026-09-02 at commit 6243ba6d9fe1c3d059d78369d8fed3534d7921d0, hashes file INDEPENDENT_V5_EXECUTION_AUDIT_HASHES.json at SHA256 0b7879e366d58f68022bc12826e820a23e7c2a1f4bf29c456fea70f7faf4af81.
verdict: BLOCKED - DO NOT SEAL / DO NOT PREREGISTER / DO NOT RUN TASK 4F1.
package_verification: The hashes file self-verifies 32/32 with 0 mismatch and 0 missing, and reverse coverage shows 0 undeclared files. It binds the real V5 runner f96cba2c. The boundary tally is clean: 13 guarded launches, 1 permitted --mode preflight, 0 run, 0 finalize, 0 HMAC environment sets, 6 forbidden forms refused before launch, no candidate or sealed namespace modified. The auditor pushed incrementally across four commits, so the V4 near-miss did not repeat.
findings_independently_reproduced: The Continuity Lead re-tested the blocking findings against its own package rather than accepting them. All confirmed. (1) The deprecated-literal scan is defeated by two trivial mechanical variants: the same V3 digest wrapped across two prose lines, and the same digest in uppercase hex. Both reintroduce CC-01 and the gate PASSES. (2) PAYLOAD_HASHES.json carries its own status field valued PREPARED_NOT_INDEPENDENTLY_AUDITED - a second status-shaped field in a second JSON, which is structurally the shape of CC-01 itself. (3) The map names "docs/v52/task4f1/ detached attestation" as the authoritative path for post_audit_acceptance_state, which is not a resolvable file path, and that directory holds only the V4 acceptance record with no V5 record at all, so the declared sole authority is empty for V5. (4) Five constants the runner actually enforces have no declared concept: EXPECTED_BEAM_MANIFEST_SHA256, EXPECTED_RESTRICTED_SEAL_SHA256, EXPECTED_PROTOCOL_SHA256, EXPECTED_PARENT_COMMIT and TIE_PREFIX. Tie priority has no concept of its own.
accountability: These are the Continuity Lead's defects. CC-01 was repaired, but V5's answer to CC-01 was a general mechanism, and the mechanism does not hold. Its root error is structural rather than clerical: the gate trusted a hand-written mirror list, so it could only ever verify what its author remembered to declare, and it compared raw text per line, so any reformatting defeated it. A gate that depends on its author's memory and formatting cannot support the claim "no superseded load-bearing literal survives anywhere".
correct_v6_direction: The burden must be inverted. The gate should DISCOVER every occurrence of every authoritative value across the bound closure and require each discovered occurrence to be declared, failing on any undeclared one, instead of checking a list the author wrote. Text must be normalised before matching, at minimum case-folded with whitespace and line breaks collapsed, so wrapping or casing cannot hide a literal. Missing concepts must be added, the attestation path must be a real resolvable path with an actual V5 record, and the duplicate status field must be removed.
outcome_boundary: Unchanged. Task 4F1 preregistration BLOCKED, run BLOCKED, retrieval-quality outcome access FORBIDDEN. Nothing is sealed.
status: BLOCKED
next_single_action: Decide, with the co-chair when available, whether to prepare V6 on the inverted-burden design. Preparing V6 exceeds the standing approval 4bd32782, which covered V5 preparation and its audit only.
```

### L-015

```text
timestamp_utc: 2026-09-03T11:00:00Z
actor_role: Continuity Lead (sole writer)
predecessor_commit_or_tag: L-014 / 294ec13
scope: Claim the V6 remediation stage answering the BLOCKED V5 delta audit. V1-V5 candidates, preflight packages, seals, manifests, audits and acceptance records remain byte-for-byte untouched; V6 is a new namespace.
changed_or_created_paths: ops/CURRENT_STATE.json; docs/CONTINUITY_LEDGER.md; then task4f1_execution_candidate_v6_2026_09_03/ and the V6 audit prompt on branch impl/v52-t4f1-v6-2026-09-03
authority_disclosure: This EXCEEDS the standing co-chair approval 4bd32782, which covered V5 preparation and its audit only. The co-chair is unavailable. V6 is prepared under Continuity Lead authority alone and is explicitly marked as requiring co-chair ratification before any sealing decision. Preparing it commits nothing irreversible: nothing is sealed, and V6 must itself pass an independent audit.
design_change: V5 failed because its gate trusted a hand-written mirror list and compared raw text per line, so it could only verify what its author declared and any reformatting defeated it. V6 inverts the burden. The gate sweeps every bound payload for value-shaped tokens (64-hex, 40-hex and V52_ identifiers), and every token it discovers must be attributed to a declared concept AND found only at that concept's authoritative path or a declared mirror. An unattributed token fails as a missing concept; an attributed token in an undeclared location fails as an unlabelled second normative source. Matching runs on normalised text with whitespace removed and case folded, so line wrapping and uppercase hex cannot hide a literal.
also_fixed: The duplicate status field in PAYLOAD_HASHES.json is removed; the attestation authoritative path becomes a real resolvable file with an actual V6 record; the five runner-enforced constants and tie priority gain declared concepts.
outcome_boundary: Unchanged. No --mode run, no --mode finalize, no HMAC key, no valid authorization, no real ranking, no retrieval-quality outcome computed, read or reported.
status: IN_PROGRESS
next_single_action: Build V6, prove the gate blocks the exact two variants that defeated V5, then commission an independent audit.
```

### L-016

```text
timestamp_utc: 2026-09-03T12:30:00Z
actor_role: Continuity Lead (sole writer)
predecessor_commit_or_tag: L-015 / 2bc0a98
scope: Close the V6 inverted-burden remediation stage and hand off to a cold-start delta auditor. V1-V5 candidates, preflight packages, seals, manifests, audits and acceptance records remain byte-for-byte untouched.
changed_or_created_paths: task4f1_execution_candidate_v6_2026_09_03/; task4f1_execution_candidate_v6_preflight_2026_09_03/; docs/v52/task4f1/V6_ACCEPTANCE_ATTESTATION_2026-09-03.json; prompts/V52_TASK_4F1_EXECUTION_CANDIDATE_V6_INDEPENDENT_DELTA_AUDIT_PROMPT_2026-09-03.md; ops/CURRENT_STATE.json; docs/CONTINUITY_LEDGER.md; START_HERE_V52_4F1.md; docs/RESEARCH_PROGRAM_STATUS_2026-08-31.md
verification: The V6 runner is byte-identical to the accepted V4 runner f96cba2c and AST-equal with docstrings stripped; DEPENDENCY_LOCK.txt is unchanged. Only five declarative payloads differ from V5, and the sole executable delta is the out-of-band package checker the runner never imports. Candidate --mode preflight returns PASS. The gate passes with 24 concepts, 9 payloads swept, 16 tracked literals, 0 unattributed tokens, 0 undeclared repetitions and 0 surviving deprecated literals. Thirteen negative fixtures all block, including the two that defeated V5 - the same V3 digest wrapped across two lines, and in uppercase hex - plus an undeclared repetition of an authoritative value in a new file, an unattributed new hash, a returning duplicate status field, an unresolvable attestation path, a missing attestation, an attestation claiming acceptance, a seal claiming post-audit state, a modified runner and a nested unbound file.
gate_caught_own_defects: Building the sweep made it audit its author. It found that a 64-hex digest was also matching as its own 40-hex prefix, fixed with lookarounds; and that the seal carried a stale duplicate supersedes block still pointing at V3 alongside the current supersedes_candidate, which was deleted rather than exempted. Where self-describing inventory hashes, historical provenance and file names are genuinely not normative values, they were not silently ignored and the regex was not loosened: each is declared in the map as a typed exempt class, scoped by JSON key path or an enumerated allowlist, with a rationale an auditor can attack.
honest_limit: The sweep tracks 64-hex, 40-hex and V52_ identifier shapes. Short load-bearing values such as 1712, 96, 392, the seeds, thresholds and tolerances are NOT token-shaped and are therefore outside its reach; they remain covered only by declared concepts and by the runner's own constants. The V6 audit prompt names this gap explicitly and asks the auditor to judge whether the gate's claim survives it or overstates itself. The claim should not be read as stronger than the sweep's token shapes allow.
authority: V6 was prepared under Continuity Lead authority alone and EXCEEDS the standing co-chair approval 4bd32782, which covered V5 only. This is recorded in the seal, the preflight manifest and the audit prompt. Even a passing audit leaves sealing conditional on co-chair ratification.
outcome_boundary: 0 --mode run; 0 --mode finalize; 0 HMAC key environment sets; no valid authorization; no real retrieval ranking; retrieval quality computed/read/reported all false; no V1-V5 candidate, seal, manifest, audit or acceptance record modified; no pinned corpus byte touched.
status: PASS
next_single_action: A cold-start auditor that did not prepare V6 executes only the V6 delta-audit prompt and must state whether the gate claim is established or merely not yet falsified.
handoff_payload: branch impl/v52-t4f1-v6-2026-09-03 at fb7fce8, merged to main; V6 runner f96cba2c; inventory, seal, source map, checker, attestation and preflight manifest hashes bound in ops/CURRENT_STATE.json anchors.
```
