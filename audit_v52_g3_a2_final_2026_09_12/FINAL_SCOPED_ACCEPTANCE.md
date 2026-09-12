# G-3 final independent scoped acceptance — PASS

**Exact accepted candidate:** `7266160ac03bdd064fe75f058eae3430fbe14496`

**Candidate branch:** `codex/g3-remediation-delivery-2026-09-12`

**Date:** 2026-09-12

**Decision: PASS — accept this exact G-3 remediation delivery in its authorized
synthetic implementation, testing and evidence scope. A1 and A2 are CLOSED.
No unresolved acceptance-blocking finding remains within that audited scope.**

This is the external independent audit disposition for the exact commit above.
It supplies the scoped acceptance result the parent requested before its separate
Head Researcher acceptance/state recording. This audit does not author the HR
decision, update main/L-094, grant production authorization or close the remaining
real-data and pre-run gate chain.

## Acceptance chain and preservation

| Candidate | Independent audit | Historical disposition |
|---|---|---|
| `24d3351f068f6982148c14a9e3338c29a2769449` | `2a025ee3b85f25af80e1b939f85f23c6cf06af30` | NOT ACCEPTED: A1, LongMemEval diagnostics bound to the wrong question. |
| `23fb505ae47d06b34a75a97955e5d1a3d8586de1` | `214afbda06a93e083f1357c25fc40cd023701ee4` | A1 CLOSED; delivery held on A2, manifest ordering rejected by the existing package verifier. |
| `7266160ac03bdd064fe75f058eae3430fbe14496` | This report and its containing audit commit | **PASS: A2 CLOSED; scoped synthetic delivery accepted.** |

Both prior reports and all their evidence remain byte-unchanged. Their rejections
remain correct for their own exact candidate commits. This additive acceptance does
not rewrite or retroactively relabel either prior finding.

## Byte-only delta verification

The accepted commit is a direct child of `23fb505...`. Its entire repository diff
contains exactly one modified path:

`drafts/v52/membership_g3_remediation_2026_09_11/FILE_HASHES.json`

There are no added or deleted paths and no implementation, source, test, README,
traceability, provenance, inherited-evidence or runtime-evidence changes. The 432
nonmanifest payload Git object IDs are identical between the two candidate commits.
The manifest's per-path records also remain identical; their order is now the
canonical sorted order required by the unchanged verifier.

All 432 declared payload paths were checked for exact coverage, uniqueness and
ordering. Their raw Git bytes independently match every declared byte count and
SHA-256. All 21 source hashes bound by the prior independent A1 execution still
match the final candidate. `VERIFICATION_RESULTS.json` records 900 checks, zero
failures. These are byte/identity assertions, not 900 scientific tests.

The raw manifest SHA-256 is exactly:

`9508d1257e0adb515f48c616e67dd410b640fd93d4d472eb54afbffcd148f33d`

The unchanged `package_integrity.py` was verified against the final candidate's
raw Git blob before execution. It was then run read-only with the exact requested
locked interpreter and an explicit candidate reference:

```powershell
& 'C:/Users/MDP/Documents/ChatGPT/LLM_TOKEN_ZIP/work/.venvs/g3-lock-20260912/Scripts/python.exe' -B `
  drafts/v52/membership_g3_remediation_2026_09_11/package_integrity.py `
  --ref 7266160ac03bdd064fe75f058eae3430fbe14496
```

**Observed:** exit 0, status PASS, files 432, exact candidate reference and manifest
SHA-256 matching the value above. Raw stdout/stderr and the command receipt are
included. The prior `file inventory mismatch` no longer occurs. **A2 is closed.**

## Evidence retained without another suite run

No test suite, historical suite, numerical probe or bootstrap was rerun in this
final byte-only turn. The unchanged source chain retains the established evidence:

- Original independent suite execution: 53 methods / 5,959 subtest observations,
  zero failures/errors/skips, under the exact lock.
- Independent A1 delta: the original generated LongMemEval counterexample now
  gives zero diagnostic-owner mismatches; record and input question order remain
  preserved; diagnostic CV matches the actual forwarding score observer.
- Independently rehashed swapped diagnostic IDs are rejected with E-G3-I05 both
  by the validator and public computation entry, before numerical computation.
- New A1 regression independently passes one method / two subtests, including
  sorted and unsorted input cohorts.
- Implementation's full updated receipt: 54 methods / 5,961 subtest observations,
  zero failures/errors/skips, source-hash-bound in the prior delta audit. This
  remains implementation evidence, not a newly claimed independent full-suite run.

The only intervening change is the manifest. There is no new execution concern
requiring repetition of those suites. **A1 remains closed.**

## Exact scope of PASS and remaining holds

This PASS accepts the controlled G-3 synthetic remediation package, combining
the original seven L-081 finding dispositions, nine named test-gap dispositions,
Decision 2 coordinatewise certificate/all-96/exact-oracle/negative-control review,
the four related L-080 G2 dispositions, and the subsequently corrected synthetic
integration/evidence delivery. The original audit's finite and surface-specific
qualifications remain applicable; this is not a completeness or universal privacy proof.

Obligation 4's **synthetic preparation/bootstrap/output bridge** is accepted within
that scope. Obligation 5's supplied synthetic negatives, accepted-lock evidence and
independent scoped acceptance are supported. **Obligation 5 as a whole remains
PARTIAL/OPEN:** real-ingestion-to-computation review and pre-run sealing are separate
unperformed requirements. They are not demanded as conditions for this synthetic PASS.

Actual native-anchor loading/binding, real cohort identity, LoCoMo corrected 1,535/raw
1,540 gold reconciliation and dual reporting, real-source provenance, production
shard integration, and production readiness remain **OPEN/unverified**. No real
outcome data was accessed and no assertion about a real retrieval result is added.

Canonical G-3/G-4 labels, the scoped Head Researcher acceptance and main ledger/state
recording remain with the parent/authorized authority. No experiment, pilot, production
retrieval, seal, finalize, HMAC or production authorization was performed or granted.
Task 4F1 retains **SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN**.
Drive, preregistration, cost replay and parent Task 3 integration were not duplicated.

## Manifest status and artifact binding

The canonical writer's manifest status remains
`SCOPED_SYNTHETIC_CANDIDATE_AWAITING_INDEPENDENT_AUDIT`. That generic writer metadata
is not an acceptance oracle and is not a new finding. **This external, exact-SHA
report and `SCOPED_ACCEPTANCE.json` supply the independent acceptance disposition.**
Changing the manifest label to accepted is neither required nor requested.

All new audit artifacts are confined to
`audit_v52_g3_a2_final_2026_09_12/` on the existing audit branch. No candidate bytes,
prior audit artifacts or main files were modified. `SHA256SUMS.json` binds the report
and delivered audit evidence and excludes itself; it is an audit-integrity inventory,
not a scientific pre-run seal. The containing Git commit supplies the immutable audit
identity without embedding a recursively self-referential commit hash in this report.
