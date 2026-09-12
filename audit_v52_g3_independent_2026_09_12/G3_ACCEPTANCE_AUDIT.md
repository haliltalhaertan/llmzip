# Independent G-3 acceptance audit: changes required

**Candidate:** `24d3351f068f6982148c14a9e3338c29a2769449`

**Candidate branch:** `codex/g3-remediation-delivery-2026-09-12`

**Audit date:** 2026-09-12

**Audit branch:** `codex/g3-independent-audit-2026-09-12`

**Verdict:** **NOT ACCEPTED — one reproduced defect blocks scoped synthetic acceptance.**

The final candidate suite passes independently: **53 methods, 5,959 subtest observations,
zero failures/errors/skips**, run **once** in the specified interpreter. Nevertheless,
the LongMemEval integration bridge silently assigns each archive's diagnostics to the
wrong question when the incoming cohort is not sorted. The new A1 finding below is
inside the synthetic bridge's own claimed scope. It is not a demand to perform any
forbidden production work before accepting synthetic remediation.

L-081's seven original findings and nine named test gaps have credible, passing
remediation evidence in their stated synthetic surfaces. Decision 2's certificate
and the four related L-080 dispositions are supported. The package as a whole is
not accepted because obligation 4's synthetic provenance bridge is defective.
Obligation 5 and the separate production/native-anchor/gold/cohort gates remain OPEN.
This report changes no canonical ledger or gate label and grants no execution authority.

## Independence, authority and exact scope

This audit used its own GitHub clone at
`C:/Users/MDP/Documents/ChatGPT/LLM_TOKEN_ZIP/work/llmzip_g3_independent_audit_20260912`.
The clone was created with `--no-checkout` and repository-local `core.autocrlf=false`
was set before checkout. The audit branch starts at the exact candidate. No candidate
implementation or test file was edited. No original checkout was used to execute code.
The reviewer did not participate in this candidate's implementation. A short generic
governance-memory lookup preceded the audit; no remembered claim was used as proof.
The user authorized subagents, but the only attempted spawn was refused by the active
agent-thread limit. No sidecar-agent result is claimed.

The following documents were read from their exact raw Git objects, rather than
assumed present in the candidate checkout. Their raw copies and hash records are in
`authority/` and `AUTHORITY_IDENTITIES.json`.

| Authority | Commit | SHA-256 of document bytes |
|---|---|---|
| HR G-3 remediation grant | `b6b06e0c7e51089aa402dcdbddf03f692d690948` | `533bf10ec66fa7ab225a60d43161e129791d0f168f7e0ab520ce0afc7f23548f` |
| Obligation 1 and F3/N1 Decision 2 | `8671128a13877c97754da182421ba615422dd2ec` | `03f5fe7d7ff838936bf8bc3bc4a406836613d611fefd94f79228cb8e2cbd4970` |
| L-081 execution-preparation review | `5126766cac9201bbede178ccb558efa428f9488c` | `aea5d05c220571076b7961afd07cd8356c93e989eb1416e873772349bd62b9bb` |
| L-080 Codex v5 review | `2cf602090a6c4c42dba44f66d95d8dfed0e0f2e8` | `fd10e53324787965e11155cb6cd31952496199f0e8250fe9416c996abf227cea` |
| Delivery-base ledger, including L-080/081/082/083/089/090 | `4f2429b257546d6899f3ed48f605cd18210aeae0` | `3deef4740f0691d109960d659ec636f19ef58b81f04522fb5dabb5cba665180f` |

The grant authorizes one controlled fix-and-test package and specifically forbids an
aggregate-certificate fallback. A passing commit alone is insufficient: the finding,
change and verification matrix, obligations 4/5 and explicit G2 dispositions all matter.
L-082 binds LongMemEval to the sorted global primary-cohort ordinal. Decision 2 leaves
obligations 4/5 open and forbids synthetic anchors replacing actual bound anchors.

No corpus or real gold file was opened, hashed or scanned; no frozen retrieval-quality
outcome was inspected or replayed. No experiment, pilot, production retrieval,
finalization, pre-run seal, HMAC operation or production authorization was performed.
Source-only Git reads and generated synthetic fixtures were the only inputs to execution.
Drive, preregistration, runtime/cost replay and main coordination were not duplicated.

## A1 — [P2, acceptance-blocking] LongMemEval diagnostics are bound to the wrong question

**Locations in the candidate namespace:**

- `pipeline_g3.py:447` enumerates `sorted(ids)` when assembling LongMemEval archives.
- `integration_g3.py:194` builds groups with `enumerate(qs)`, preserving the original
  cohort order; line 200 attaches question IDs using those groups.
- `integration_g3.py:159` validates the resulting ordinal against `qs.index(ids[0])`,
  repeating the same wrong convention instead of checking the sorted global ordinal.
- `corpus_ingest_g3.py:547` returns `cohort_ids=list(bound)`, which does not promise
  sorted mapping insertion order. No bridge precondition rejects an unsorted cohort.

**Trigger:** an otherwise valid two-question LongMemEval synthetic source and mapping
whose insertion/cohort order is `['q_z', 'q_a']`.

| Archive ordinal | Question actually fitted/scored by preparation | Question attached by accepted envelope |
|---|---|---|
| 0 | `q_a` | `q_z` |
| 1 | `q_z` | `q_a` |

`probe_lme_binding.py` reproduced this using newly generated LongMemEval-shaped bytes,
the unchanged ingestion parser, real representation fitting, the full coordinatewise
and geometric controls, real scoring, and the unchanged envelope builder. Only the
source/mapping gates were replaced by exact checks of those generated fixture bytes,
as in the candidate's own integration tests. The `score_archive` observer forwards
to the real function; it does not substitute records or diagnostics. All 120 records
were produced, both diagnostic identities were reversed, and the bridge returned an
accepted envelope with binding SHA-256
`29706bb1c5caaefc1ec0b022dc582f408f989bd14b8a59a7796b846fa2c14d28`.
Evidence: `LME_BINDING_REPRO.json`. The probe exited 0 because it explicitly asserts
that the defect is reproduced; that exit is not a candidate PASS.

**Impact:** the saved preparation metadata misattributes archive diagnostics and
their ordinal to another question. The public hash faithfully binds the incorrect
association. No wrong retrieval score or bootstrap value is established by this
probe: preparation's question-keyed score records are not shown to be wrong, and
the probe does not call bootstrap or a writer. It establishes a concrete violation
of the synthetic provenance contract, sufficient to withhold obligation-4 acceptance.

**Why the final suite misses it:** `test_delivery_pipeline.py:778` checks unsorted
LongMemEval IDs only through preparation. The 12 integration methods in
`test_delivery_integration.py` share a one-conversation LoCoMo fixture created at
line 48; none carries two LongMemEval archives through the bridge. Thus both local
test groups pass while their composition misbinds identities.

**Required disposition:** keep A1 and obligation 4's synthetic bridge OPEN. In an
authorized successor implementation, make the bridge's grouping and validation
agree with the already-bound sorted-global convention, and add a two-archive
LongMemEval integration control that checks actual scored ownership against envelope
diagnostic ownership for both cohort orders. This audit makes no implementation edit
and prescribes no new scientific ordering or cohort policy.

## Original findings: independent disposition matrix

All filenames/line references in the following matrices refer to
`drafts/v52/membership_g3_remediation_2026_09_11/` at the candidate SHA. Named test
methods have their full IDs and observed PASS statuses in `suite_once/RESULTS.json`.
The word **supported** means supported in the named synthetic scope, not a universal
security proof or closure of the full G-3 package.

| L-081 finding | Actual change reviewed | Verification and disposition |
|---|---|---|
| F1, caller IDs in exception surfaces | `pipeline_g3.py:388` validates coverage/ownership before keyed lookup; `:297` and `record_boundary.py:7` protect core validation; runner `:444` guards records before core arithmetic. | `test_gap_05_F1_all_three_identifier_leak_paths_all_surfaces`, both `E_M_043` methods and G2 `test_F1_F2_record_boundary_before_immutable_core` pass. Cause/context, formatted traceback and captured output are checked. **Supported for named wrappers.** |
| F2, successful empty cohort | Nonempty cohort/archives/records required at `pipeline_g3.py:388`, `:433`, `:297`; bridge enforces nonempty exact record coverage. | `test_gap_04_F2_empty_cohorts_archives_and_records_refused` and integration malformed-record negatives pass. **Supported.** |
| F3/N1, partial or canceling canary | Fixed 97-member family, separately transported archive and query bits, independent rational oracle; `pipeline_g3.py:250–284`. | All eight `CertificateTests` pass, including adopted N1 and direct all-96 negatives. **Decision-2 implementation supported; see detailed qualification below.** |
| F4, same-object matched-block check | A second seeded redraw is compared, then actual embedded blocks and cross-block zeros checked at `pipeline_g3.py:325` and `:364–371`. | The three `test_F4_*` methods pass. Wrong redraws and either rotation replaced by identity are rejected; identity is first shown to pass norm/dot invariance. **Supported, non-vacuous discrimination.** |
| F5, E-M-005 swallowed | Feature-count refusal moved outside broad fit exception handling, `pipeline_g3.py:169–175`. | `test_F5_insufficient_features_retains_specific_E_M_005` passes with actual insufficient-feature text. **Supported.** |
| F6, CRLF identity failure | Strict raw-byte hash gate retained; README requires local LF configuration before checkout. | Own clone is byte-faithful; `test_F6_exact_blob_refuses_crlf_and_byte_mutation` passes. **Operational remediation supported; translated bytes still refuse.** |
| F7, missing M3 ingestion-schema checks | Exact consumed container/value types, required keys, coverage, unique ownership/ordinals, valid gold before fit, `pipeline_g3.py:388–430`. | All named gap-02 malformed/missing/type/coverage/gold/duplicate methods pass, with pre-fit instrumentation. **Supported for consumed schema; bridge composition defect A1 remains separately open.** |

| Exact L-081 test gap | Named executable evidence reviewed | Disposition |
|---|---|---|
| 1. Nuisance reuse unasserted | `test_gap_01_every_topks_call_reuses_identical_immutable_priorities`, formula and caller-mutation counterparts. Observer checks all 60 selector calls, same object/bytes and 20 nuisance draws; arm-specific row reversal fails at the observer. | **Supported.** Immutable here describes observed unchanged bytes, not a NumPy write-protection flag. |
| 2. No malformed M3 fixtures | `test_gap_02_F7_all_required_top_level_and_nested_keys_missing`, wrong-types/coverage, duplicate IDs/ordinals, invalid gold tests. | **Supported at M3; new bridge test gap A1 remains.** |
| 3. E-M-026/027/028 untested | `test_gap_03_M3_all_three_declared_refusals`. | **Supported**, exact codes and no fit checked. |
| 4. Empty cohort untested | `test_gap_04_F2_empty_cohorts_archives_and_records_refused`. | **Supported** for both benchmark schemas. |
| 5. Exception suppression untested | Fit/query fault-injection methods and all three ID/core paths. Recursive cause/context and traceback inspection, Python/FD output capture and write guard. | **Supported for injected surfaces.** Not an OS/native-I/O or arbitrary-introspection guarantee. |
| 6. Anchor type/range untested | `test_gap_06_anchor_types_ranges_and_container_refusals`, `test_gap_06_anchor_valid_endpoints_and_tolerance`. | **Supported**, including adjacent floats bracketing 1e-12; actual frozen-anchor provenance remains OPEN. |
| 7. Thin parity fuzz | `test_gap_07_gap_09_4000_exact_order_cases_against_raw_AST_function`; `test_gap_07_semantic_lexsort_set_oracle_unique_priorities`. | **Supported:** 4,000 tie-heavy exact-order cases in all three branches; 1,000 independent unique-priority full-sort set cases. Only the pinned source function is compiled, not its outcome-bearing module. |
| 8. Canary partial coverage untested | Literal family/seed/coverage, every-member positives and member-specific zero negatives in `CertificateTests`. | **Supported**, including all-96 tested directly. |
| 9. Selection ordering unasserted | Exact-order fuzz, `test_gap_09_selection_order_is_not_rank_and_recall_is_set_based`, six-arm ordering and connector ordinal tests. | **Supported at selector/preparation level.** Selection order is not a rank API; A1 concerns downstream metadata. |

## Decision 2: what the certificate establishes

The masks are 96 singleton powers of two plus `2**96-1`, represented as source
literals. The nonidentity permutation and seed `52003107` are also literals;
the test independently redraws that permutation from the declared seed. Nothing
chooses or replaces a family member in response to an archive. The test checks
all 97 family visits on a valid distinguishable input.

The numerical implementation thresholds permuted/signed rows. `exact_oracle.py`
imports neither NumPy nor the transform helper: it obtains rational source signs
and transports bits by the sign mask. `test_certificate.independent_image` uses
a separate rational/integer implementation. The comparison is per archive/query
code bit, rather than XOR-disagreement equality or summed Hamming equality.

Every member is invoked directly with archive-zero, query-zero and jointly-zero
fixtures under both IEEE zero signs. The all-96 negative is therefore not supplied
by an earlier singleton's failure. The 97 assertion-omission variants and the
wrong-sign/wrong-permutation/constant-bit variants are meaningful controls. The
adopted centered 96-by-96 N1 fixture has archive zero columns 0 and 2 and query
entries +1/-1; the old aggregate canary accepts and the new check rejects. Jointly
zero coordinates deliberately fail the required bit-complement contract, while
the underlying `>=0` retrieval rule is unchanged.

`controls()` calls the new certificate for both unscaled and scaled arrays. The
legacy aggregate canary is retained only as a regression function; no success or
fallback path substitutes it for the certificate. Native-distance equality remains
a distinct invariance check, which is consistent with the authority.

These facts support the implementation's finite synthetic assurance. They do not
prove absence of every common-mode bug, occurrence of these zeros in a real fitted
archive, or a scientific mechanism. The single delivery commit does not independently
prove the historical order in which its tests were authored. Preserved recovery
evidence is correctly described as insufficient for Decision 2 rather than promoted
to acceptance. The required failing witness is explicit in the current tested code.

## G2 dispositions and inherited limitations

| L-080 item | Reviewed evidence | Independent disposition |
|---|---|---|
| F-1, int-subclass diagnostic lost | Runner `verify_source_identity` now uses `type(n_declared) is int`; exact diagnostic and former gate mutant tested. | **Supported narrow repair.** A diagnostic defect, not a newly demonstrated leak. |
| F-2, spoofed-code test passes for wrong exception | Test now requires `UnsafeErrorField`; the historical broad-`isinstance` mutant fails that requirement. | **Supported test discrimination.** The old mutant is not relabeled a confidentiality breach. |
| F-3, ingest count without local type gate | `_manifest_n_questions` at `corpus_ingest_g3.py:118` is used at both cohort-count sites; exact-type refusal and removed-helper mutant tested. | **Supported narrow repair.** No new corpus count or policy invented. |
| F-4, overbroad README | README explicitly limits exact-type claim to the manifest-count fields and discloses other surfaces. | **Written disposition supported.** |
| v5 versus v4 working line | README and TRACEABILITY recommend the G3 successor carrying v5 fixes. | **Explicit owner recommendation exists.** Retain that development direction, but do not promote this exact defective candidate to accepted status. HR/parent owns canonical working-line disposition. |

The two recorded-but-not-reopened L-080 limitations stay outside the finding set:
`safe_report.counts` arbitrary key/type-name messages and the immutable core's
path-bearing writer. Mutable accepted-mapping stamps, direct inherited APIs and
structural short-string policies are also disclosed limitations; no universal
confidentiality, provenance authenticity or sandbox claim is accepted here.
Schema closure of the bridge means its envelope/result key sets are closed. M3
validates the fields it consumes and intentionally does not reject every extra
ingestion metadata key.

## Obligations and remaining holds

| Item | What this audit verifies | Remaining disposition |
|---|---|---|
| Obligation 4, synthetic preparation/bootstrap/output | Actual generated LoCoMo ingestion-to-fit-to-score-to-bootstrap-to-output test; shared accepted bootstrap arithmetic, fixed seed/10,000 replicates, exact envelope/result schema, copy isolation, source/code hashes, stale-binding refusal and exclusive `xb` creation including a concurrent sentinel race. | **NOT ACCEPTED as a complete synthetic bridge: A1.** LoCoMo demonstrated path is supported; LongMemEval metadata binding must be corrected. |
| Obligation 4, real provenance/native source | Public fixture hashes bind supplied bytes; they do not authenticate that the fixture corresponds to frozen anchors or actual accepted cohorts. | **OPEN**, real connector and complete production provenance unverified. |
| Obligation 5, negative-control/lock portion | Current 53-method suite independently passed once; inherited final receipts and adaptation/source chain checked without rerunning them. | Synthetic evidence supplied, but **PARTIAL**, A1 adds a missing integration control. |
| Obligation 5, real integration/acceptance/seal chain | This audit supplies an independent acceptance decision, which is negative for this candidate. | Real-ingestion review and pre-run seal remain **OPEN**; no seal action requested or taken. |
| Native anchors | Required per-question float and total-coverage checks retained; synthetic test anchors explicitly fixtures. | Actual bound blob loading and element-wise real cohort identity **OPEN/unverified**. No outcome artifacts opened. |
| LoCoMo gold/cohorts | Candidate preserves v5 raw-evidence behavior and acknowledges L-082 nonconformance. | Corrected 1,535/raw 1,540 mandatory dual-reporting reconciliation **OPEN**, not independently recomputed. |
| LongMemEval global ordinals/shards | Preparation uses sorted IDs; A1 identifies inconsistent downstream binding. | Production global cohort/shard integration **OPEN**. No production sharded runner accepted. |
| G-3/G-4/production | Remediation matrix exists and G2 dispositions are written; scoped acceptance fails on A1. | **G-3 remains OPEN; no G-4 or production-readiness declaration.** |
| Task 4F1 | Authority retains its unchanged prohibition. | **SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN.** |

No atomic-publication guarantee is inferred from the bridge's writer: it protects
existing files from truncation, but a failed new write may leave a partial file,
as its docstring says. The test's source gates are substituted only for generated
fixture bytes; this is synthetic integration evidence, not real-source authorization.
Most pipeline regression methods patch out the separately tested certificate to
isolate their targets. The actual LoCoMo integration test and A1's actual LongMemEval
probe run the full certificate, so those mocks are not hidden end-to-end evidence.

## Reproduction, hashes and preservation

The requested suite was launched exactly once using the unmodified README launcher:

```powershell
$py = 'C:/Users/MDP/Documents/ChatGPT/LLM_TOKEN_ZIP/work/.venvs/g3-lock-20260912/Scripts/python.exe'
$ns = 'C:/Users/MDP/Documents/ChatGPT/LLM_TOKEN_ZIP/work/llmzip_g3_independent_audit_20260912/audit_v52_g3_independent_2026_09_12/v52/membership_g3_remediation_2026_09_11'
$env:PYTHONHASHSEED = '0'
& $py -B "$ns/verify_delivery.py" --output evidence/independent_once
```

The launcher requires output within its own package namespace, while the user
requires audit-only writes. Accordingly, all 21 root/authoritative Python sources
were copied byte-for-byte to the audit scratch path shown above, preserving the
same directory depth for the suite's interpreter/Git path resolution. No assertion,
import, launcher or implementation source was patched. `EXECUTED_SOURCE_BINDING.json`
compares every recorded execution hash with the exact candidate raw Git blob and
both the candidate checkout and scratch bytes. The original candidate namespace
was never used as an output location. Scratch source/fixture directories are ignored
by the audit commit; the full run receipts are committed in `suite_once/`.

Observed interpreter: Python **3.13.15**, NumPy **2.3.5**, SciPy **1.17.0**,
scikit-learn **1.8.0**, pandas **2.2.3**; executable exactly the user-specified path.
All seven launcher numerical thread variables are 1; `PYTHONHASHSEED=0`, `-B`, and
assertions enabled. The independent run took **11.919 seconds** in unittest's
reported timing. There were 8 certificate, 7 G2, 26 pipeline and 12 integration
methods. This count excludes the targeted A1 probe and the static identity checks.
The launcher guard observed 14 allowed synthetic data-file events and zero denied
events. It is a Python-level scope observation, not an OS sandbox. An earlier live
status message misstated the source count as 25; the final verified count is 21.
The candidate launcher's `evidence_kind` text remains unchanged as implementation
wording in the raw receipt; this report supplies the independent execution attribution.

The separate A1 probe ran once after its concrete static discrepancy was found.
It is not a second execution of the 53-method suite. No historical suite was repeated.
Historical/preparation regression receipts report 10 completed suites, each exit 0:
in each historical/G3 lane, core 99 checks, runner 68, adversarial 45, old-version
controls 5, preparation 7 methods. These are inherited implementation observations,
not independent runtime results. `verify_evidence.py` reconstructs their source
adaptations using only an explicit import/path substitution allowlist and verifies
the recorded suite/source hashes. No inherited assertion removal or change was found.

`verify_identity.py` performed **502 checks, zero failed**: exact candidate/branch/LF
identity; 425 manifest entries plus the separately hashed self-excluded manifest;
raw authority documents; 11 recovered pre-edit files; materialized source identities;
source-chain ancestry and current executed-byte binding. The candidate is purely
additive relative to its actual parent/base `4f2429b257546d6899f3ed48f605cd18210aeae0`:
**426 added files, all within its namespace**. This audit does not mistake side-branch
source commits for ancestors of the delivery branch.

`verify_evidence.py` separately performed **193 checks, zero failed**, covering
historical v5/prep manifest bytes, inherited adaptation/receipt/source consistency,
and final evidence/provenance source bindings. These are byte/receipt checks, not
scientific recomputation. The core is unchanged at SHA-256
`bc2282d3fccfe83c3e9fc36a59d7df8e4f748048ff94baebdfa4010584404e72`.
The empty `authoritative/__init__.py` is included in inventories for completeness
and provides no substantive identity evidence.

Read-only current observation of the original `work/llmzip` confirms HEAD
`077474013d95d6f343d31385d8a57d42fb72f721`, index SHA-256
`353d7486ada6314204d94522776162568509b077701f67b3a8db33fc5d65f32a`, Git status,
and all 11 named recovered source hashes match the candidate's recovery/preservation
receipts. Evidence: `ORIGINAL_SOURCE_OBSERVATION.json`. This corroborates current
preservation; it does not reconstruct every historical filesystem operation.
The live original source is never imported or executed.

Origin main observed at clone/audit was `ae9175676b840ae6a80a31eba9836187dc1b7491`.
Main is under parent coordination and may advance independently. This audit's push
targets only its named audit branch. Implementation corrections, later acceptance,
Drive/preregistration updates, ledger edits and cost replay remain with the parent.

The immediate next technical action is a successor fix for A1 with a meaningful
LongMemEval composition regression, followed by scoped re-review. This audit does
not authorize or perform that implementation change.

## Artifact identity convention

`CANDIDATE_FILE_IDENTITIES.json` binds all candidate manifest entries to the exact
candidate SHA; `EXECUTED_SOURCE_BINDING.json` binds the actual run. `SHA256SUMS.json`
binds this report and all delivered audit artifacts and excludes itself, avoiding
self-reference. It is an audit-integrity inventory, not a pre-run seal. The final
Git commit supplies the independent immutable audit identity; no commit hash is
placed inside the content it would recursively identify.

The staged whitespace check flags preserved raw Windows CRLF suite receipts and
one trailing space in the raw predecessor report. Those evidence bytes remain
unchanged intentionally; new audit prose/scripts are checked separately. This
formatting observation is not an executable-test failure or an identity mismatch.
