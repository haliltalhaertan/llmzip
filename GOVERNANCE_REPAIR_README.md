# Governance repair package — prepared 2026-09-14, NOT ACCEPTED

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Four independently-run repair packages answering an audit of `main` @ `5ec3db6` (ledger L-095). **Everything here is additive and PREPARED, NOT ACCEPTED.** No existing file was modified; `docs/CONTINUITY_LEDGER.md` and `ops/CURRENT_STATE.json` are untouched — the ledger has a sole writer and none of these sessions is it. Task4F1 stays sealed and BLOCKED; no run, finalize, authorization, HMAC, corpus or retrieval outcome was touched.

| Package | Source commit | Answers |
|---|---|---|
| `research_governance_repair_2026_09_14/` | `6266ee9` | L-095 has no schema keys; ledger never mentions 7 research lines; V5/V6 defects never recorded; the 25-vs-31 evasion count |
| `research_stale_pointer_repair_2026_09_14/` | `b7fd8d6` | README/START_HERE/manifest pointers superseded weeks ago; the +10.04 pp caveat does not travel |
| `research_v7_evidence_completion_2026_09_14/` | `b69afec` | V7's audit stopped after 16 evidence files: Gates 4, 5 and the 3.5 synthesis were never run |
| `research_exact_rational_verification_2026_09_14/` | `864fa7c` | Seal V3 binding 8 (exact-rational sign classification) never exercised |

## What was actually established

### Exact-rational condition — behaviour confirmed, binding NOT discharged
31/31 exact checks pass against the vendored implementation on synthetic inputs. The decision path carries no `round`/`tolerance`/`epsilon`; a float value is parsed only for an integrity cross-check and never reaches a sign. A tiny positive `D_t` that float64 renders as `0.000000` still classifies `+1`; exact ties stay ties; summation order changes the float mean (`0.0` vs `0.0333`) but not the exact one (`1/30`).

**Coordinator mutation testing (not the worker's claim):** making the deliberately-float negative control exact ⇒ the suite reports `0 cases expose the float control` and FAILS. Patching the vendored `sign()` to use float ⇒ `26/31`, five checks fall. The tests bite in both directions.

### V7 gate completion — three survival paths demonstrated, not hypothesised
19 synthetic checker fixtures, all re-run by the coordinator, 19/19 agreeing with the worker:

- **Blocked:** extra file, missing file, renamed file, mutated bytes without reseal, stale hash, case-variant name, four post-audit status claims, inventory status field, and all three F5-style acceptance-redirect attempts.
- **Survives:** narrative content planted **under a functional file name** plus a full reseal → checker passes. Name-set equality is name-only; it does not look at content.
- **Survives:** deleting `status_semantics` prose from the seal → checker passes. Unpinned prose and unpinned seal/template values edit freely.
- **Not covered:** nothing inside the package hashes the seal itself. The only root of trust is the six externally pinned hashes.

Gate 3.5 answer: **NOT-YET-FALSIFIED**, established only for file-set integrity against a non-resealing adversary. That is the same distinction the V6 auditor drew and V5 failed to survive.

### Governance record
L-096 drafted to the schema (all 10 keys), status `PREPARED_NOT_ACCEPTED`, one next action. 29 audit defects catalogued as never-recorded, including the missing `REAL_CANARY_QUERY` / `TIERS` concepts — verified as 0 hits in both the ledger and V6's `NORMATIVE_SOURCE_MAP.json`.

**25 vs 31 evasions reconciled, coordinator-verified from the audit's own batch evidence:** batch1 1 + batch2 14 + batch3 11 + batch4 6 = 32 unblocked across 52 fixtures; one of those is `G1`, the positive control whose passing is correct behaviour ⇒ **31** table rows. The report's **25** is batches 2+3 (14+11) out of 36 (15+20+control). Both numbers are right in their own scope; no document said which.

### Stale pointers and integrity
Six tasked items proven stale plus seven more found by sweep; minimal dated "superseded by" corrections proposed, none touching a sidecar-hashed document. Integrity re-verified independently from raw git blobs: **20/20 sidecars, 32/32 anchors, 73/73 geometry manifest, zero mismatches.** `+10.1869` vs `+10.037943` shown to be different subtrahends (uncentered vs centered float), difference `0.148936` = the frozen centering effect — not a contradiction.

## What none of this does

- **No verdict on V7.** Evidence completion by a non-independent session is not an audit. V7 stays without a verdict.
- **Binding 8 is not discharged.** Freeze → cold-start independent audit → governed merge still required.
- **No ledger entry was appended**, no state file patched, nothing accepted, sealed or ratified.
- Every worker read the code it tested and authored its own oracle — partial independence only.

## Verification

`MANIFEST_GOVERNANCE_REPAIR.sha256` covers the **165 files this package adds** (164 package files + this README), built from **git blobs** (not worktree bytes) so it verifies after any CRLF round-trip. Every other file on this branch is inherited unchanged from base `5ec3db6` and is covered by main's own manifests. Each source branch was checked to be purely additive within its own namespace before import; the publish script aborts otherwise.

Base `5ec3db6`; `main` untouched.
