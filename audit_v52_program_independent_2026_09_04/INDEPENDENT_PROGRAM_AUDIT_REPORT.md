# V52 Program — Cold-Start Independent Continuity and Readiness Audit

Date: 2026-09-04  
Role: independent program auditor; not the Continuity Lead, state writer, scientific co-chair, or execution auditor  
Audited canonical ref: `main`  
Audited commit: `c54013611fb6bbda6187d7dfc0b60ae1126e9cef`  
Audit branch: `codex/v52-program-independent-audit-2026-09-04`

## Final verdict

`BLOCKED — DO NOT AUTHORIZE, RUN, OR FINALIZE TASK 4F1`

The approved scientific draft and its two approval artifacts are byte-consistent and scientifically usable as the frozen preregistration design. The exact current Seal V3 blob is also internally consistent on direct inspection. However, the repository is not execution-ready and is not yet a clean handoff for another model:

1. the Seal V3 verifier still overstates the scope of its independent semantic verification outside binding 8;
2. the V7 execution-package audit has no final report, gate table, or hash manifest, and its own partial evidence challenges the package's central consistency claim;
3. the operational handoff documents contain stale and mutually inconsistent directions; and
4. GitHub's default branch still points away from canonical `main`.

This audit does not invalidate the approved scientific design. It does prevent treating the current repository as ready for authorization or outcome-bearing execution.

## Scope and independence

I fetched GitHub immediately before closing the audit and moved the audit base twice as `main` advanced: `bae7be2` to `df9b0f5` to the final audited `c540136`. Findings below therefore apply to the newest `main` visible at closure, not to an older local snapshot.

The audit inspected repository bytes, Git objects, remote branch heads, committed audit evidence, candidate preflights, seal/state verifiers, and negative controls. It did not accept commit messages, `CURRENT_STATE.json`, ledger prose, or prior chat summaries as proof without checking the referenced bytes or behavior.

No candidate, seal, manifest, cohort, pinned corpus, state file, ledger, or historical audit namespace was modified. The only persistent artifact created by this work is this report on a separate branch.

## Evidence that passed

### Scientific preregistration bytes

- Approved draft at commit `c0133fce9b755d13d9be3016e8e06f493d6b275b`: 14,688 bytes, SHA256 `5e61898193421a3a18791202668c0974f23d2fb4080a107069e7b7127e35ea44`.
- Head Researcher re-review artifact at `19d9cbbfcbc48f80dc63ac179f2aa67e7eed490d`: SHA256 `8795abc7b58b3bae8f2333ba630f95642e9d2e653a31478d221ceb9d71272f3f`; verdict in the source artifact is approval for sealing only, not execution.
- Exact-byte scientific co-chair approval at `5299cc12d899a918504110b4faf1734713f607cc`: SHA256 `3aaa90bf2714afa662548c32bba0ae165c4f6a4d84f2af84f1a2659fa25abdca`; the source artifact approves the exact draft bytes with notes that require no amendment.
- Authorization-schema ratification artifact at `6f1de9eb1dfb8557e4ebc3fa2a1130214c6b228b`: SHA256 `e2cc9a8b207be7b21d2b8759a1a2c6c86186522c7102f0d39313172530ebbc41`; it ratifies the V4 authorization schema while the runner remains byte-identical to V4 and creates no authorization.
- Seal V3 and its sidecar agree at SHA256 `e906c6d2b68b103c6c21906cbdf44acba10e31b7e5e17ffd2c7d1bbfb7a95cf4`.
- The sealed cohort recomputes to the exact tier set `100K / 500K / 1M / 10M`, question counts `355 / 629 / 553 / 175`, 1,712 eligible questions, 96 eligible archives, and excluded archives `1M::5`, `1M::26`, `1M::33`, and `1M::34`.
- Seal V1 and Seal V2 remain preserved at their declared historical hashes and remain correctly classified as blocked/superseded.

### Current automated controls

- `tools/verify_continuity_state.py`: `PASS`.
- `tools/verify_preregistration_seal.py`: `PASS` on the exact Seal V3 identity and current semantics.
- `tools/test_verify_preregistration_seal.py`: 38/38 controls behaved as expected, including identity-layer mutations, the historical V1/V2 defects, exact binding-8 rule equality, and nested binding-8 metadata controls.
- The V7 package preflight passed recursive four-file payload closure, current payload hashes, fail-closed authorization state, accepted-V4 runner identity, and its limited AST boundary; it correctly ended with independent audit and Head Researcher authorization still required.
- The V7 runner hashes to `f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8`, byte-identical to the accepted V4 runner.

These passes establish the listed narrow properties only. They do not by themselves establish execution readiness.

## Blocking finding B1 — Seal V3 semantic-verifier coverage is still incomplete

Commit `c540136` correctly added a pinned Seal V3 identity layer, exact equality for the Section 6 rule, a pinned extraction rule, and 38 controls. The identity layer prevents a modified seal file from passing the production entry point. It does not prove that every assertion already present in the accepted exact blob was derived from its cited source.

I exercised the verifier's semantic layer directly, exactly as the committed semantic negative-control suite does. Six materially relevant mutations produced zero semantic failures:

| Mutation | `verify_semantics` result |
| --- | ---: |
| binding 4 Head Researcher verdict changed to `REJECTED` | 0 failures |
| binding 5 co-chair verdict changed to `REJECTED` | 0 failures |
| binding 6 ratification text inverted | 0 failures |
| binding 7 `all_four_must_be_bound` changed to `false` | 0 failures |
| binding 1 source commit changed to an unavailable all-zero commit | 0 failures |
| binding 2 normativity statement inverted | 0 failures |

The control mutation changing binding-8 `owner` produced one failure, confirming that the probe reached the hardened semantic layer and that the new binding-8 checks work.

Direct inspection of the actual current source artifacts found that the six real values in the exact accepted blob are presently consistent with their sources or stated policy. Therefore this is not evidence that the current draft or approvals are false. It is evidence that the verifier's module-level claim — that every binding is re-derived from source bytes — remains too broad, and that the negative-control suite is concentrated on binding 8 rather than the complete seal schema.

Disposition: Seal V3's exact scientific content is substantively verified by this audit, but the repository must not describe the automated verifier as a complete semantic proof until every load-bearing field is either derived/checked, pinned and explicitly classified, or removed from that claim. A new scientific draft or new scientific review is not implied by this finding.

## Blocking finding B2 — V7 remains unsettled and its partial evidence challenges its central claim

The remote V7 audit branch is still:

`audit/v52-t4f1-v7-independent-2026-09-03 @ 16dc61313acd0e9086c852eccb9100023898fd27`

It contains command logs, scripts, and Gates 1-7 evidence, but no final audit report, gate table, recursive audit hash manifest, or final verdict. It therefore cannot be accepted or used to authorize execution.

More importantly, its partial `g7_bound_payload_restatements.json` evidence reports:

- 21 restatement pairs;
- 17 pairs where both sites are bound;
- 13 pairs listed as reconciled by nothing;
- a dependency-lock task label that does not match the Task 4F1 runner; and
- stale V5/V6/V4 labels in the shipped candidate seal.

That evidence conflicts with the candidate's central prose claim that a bound functional file cannot state a requirement and therefore there is nothing to restate or reconcile. The bound dependency lock and authorization template demonstrably contain concrete requirements or control values; being "functional" does not make their statements semantically empty.

No final V7 verdict is issued here because that commissioned audit is a separate unfinished task. Its final auditor must explicitly resolve this central-claim problem. Until then V7 is `PREPARED_NOT_INDEPENDENTLY_AUDITED`, not accepted.

## Blocking finding B3 — the GitHub handoff is not internally coherent

The repository is recoverable, but a new model cannot safely continue by following the entry documents literally:

- `ops/CURRENT_STATE.json` names the obsolete V6 delta-audit prompt in `authority_order`, while the live execution candidate is V7 and the V7 audit is still pending.
- `ops/CURRENT_STATE.json.pushed_state_anchor` still points to `state/v52-4f1-v3-audit-blocked-2026-09-01 @ 531d41b...`, even though GitHub has later state branches through `state/v52-t4f1-seal-v3-verifier-hardened-2026-09-04 @ c540136...`.
- `START_HERE_V52_4F1.md` simultaneously labels the preregistration draft "under review" and "NOT approved for sealing" while later lines state that the scientific preregistration is sealed at Seal V3.
- The same entry document still presents "Exact V4 objects to audit" and a V3 safe-resumption procedure as if they were current, despite later text calling that completion condition stale and identifying V7 as the live execution track.
- The continuity checker passes because it checks local anchor hashes, basic hard stops, and ledger-entry presence; it does not check authority-order freshness, pushed-anchor freshness, cross-document state agreement, or remote default-branch configuration.
- GitHub's default branch still resolves to `claude/itq-frontier-audit-wfrz6a @ 78b4fdfa...`, not canonical `main`.

These are governance and handoff defects, not evidence of a scientific-result defect. They are nevertheless load-bearing for the stated goal that another model should resume from GitHub alone without ambiguity.

## Historical boundary event — disclosed and contained, but must not be erased

The first Task 4F1 execution-candidate audit records Incident A1: auditor-authored negative fixtures accidentally formed valid V1 authorizations, triggering a real single-archive run and a partial full-list run that produced 26 archive result files before termination. The files were reportedly enumerated by name only and deleted; no metric value was read, printed, summarized, or carried into the audit package.

The repository correctly marks that V1 audit unusable as an outcome-free sealing sign-off. Later stages report zero run/finalize activity for their own stages. Program-level wording should preserve this distinction: later clean stages do not make the historical execution event disappear, even though no retrieval-quality value was reportedly inspected.

## Verified historical disposition

- The restricted 4F0 refreeze audit is recorded as `PASS WITH CONDITIONS`, with 1,712 questions / 96 archives and no retrieval-quality computation.
- The V4 execution implementation audit is hash-bound at `641568d8...` and passed its nine implementation gates, but V4 was not validly sealed because CC-01 survived in bound prose.
- V5 is independently `BLOCKED` at `6243ba6d...`.
- V6 is independently `BLOCKED` at `c88455ba...`.
- V7 is still running at `16dc613...`; it has no final result.

The remote audit branch heads matched the above commits at audit closure.

## Required disposition by the state writer / Head Researcher

This report changes no state. The sole state writer and reviewing authority should evaluate it and, if accepted, record a new state transition that does all of the following before any execution decision:

1. classify B1 and either harden the full seal semantic schema or narrow the verifier's claim explicitly;
2. require the V7 auditor to finish and directly resolve the central consistency claim;
3. reconcile `START_HERE`, `CURRENT_STATE.authority_order`, and `pushed_state_anchor` to one current route;
4. change GitHub's default branch to canonical `main`, or make the non-canonical default an explicit unresolved P0 in the first screen of the handoff; and
5. implement and independently audit the exact-rational `D_t` sign classification required before run authorization.

None of these steps authorizes a run. A later execution decision still requires a separately valid production authorization and all standing gates.

## Outcome-boundary declaration for this audit

- candidate `--mode run` invocations: 0
- candidate `--mode finalize` invocations: 0
- calls to `run_archives`, `evaluate_archive`, or `finalize_results` on real BEAM data: 0
- valid production authorizations constructed: 0
- HMAC key set, read, inspected, or sought: 0
- real BEAM retrieval performed in this audit: false
- retrieval IDs, distances, metric values, or arm outcomes computed/read/reported in this audit: false/false/false
- candidate, seal, manifest, cohort, corpus, state, ledger, or historical audit bytes modified: false
- persistent files added: exactly this report

The current audit is outcome-free. Its verdict concerns governance, reproducibility, semantic verification, and readiness only.
