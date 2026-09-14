[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# DELIVER 1 — Staleness evidence (PREPARED, NOT ACCEPTED)

All statements below are VERIFIED (read from bytes on HEAD `5ec3db6` or the named
`origin/` branch via `git show`/`git cat-file`, no checkout) unless marked CLAIM
(a document asserts it) or RELAYED (quoted from a commit message).

## Item 1 — `README.md:46`: "A fresh cold-start V3 audit is still required"

Stale. VERIFIED: `README.md:46` (HEAD blob) says V3 "has passed only
implementer-side outcome-free preflight and synthetic regressions. A fresh
cold-start V3 audit is still required".

Superseding fact 1 — the V3 audit closed with verdict BLOCKED on 2026-09-01.
VERIFIED: `origin/audit/v52-t4f1-v3-independent-2026-09-01:audit_v52_t4f1_execution_candidate_v3_independent_audit_2026_09_01/INDEPENDENT_V3_EXECUTION_AUDIT_REPORT.md:11`
quotes the verdict verbatim:

> `BLOCKED — DO NOT SEAL / DO NOT PREREGISTER / DO NOT RUN TASK 4F1`

Commit VERIFIED: `a590f623a2b9b6c211068692d60f0e515e7166c0`
("audit(v52): cold-start independent V3 execution-candidate audit — BLOCKED").

Superseding fact 2 — the ledger closed the audit at L-003.
VERIFIED: `docs/CONTINUITY_LEDGER.md:59-73` (HEAD blob), `### L-003`,
`timestamp_utc: 2026-09-01T13:00:00Z`, `status: BLOCKED`, handoff payload cites
audit branch `audit/v52-t4f1-v3-independent-2026-09-01` at `a590f629`.
L-005 (VERIFIED, `docs/CONTINUITY_LEDGER.md:91-104`) then acted on the BLOCKED
audit (remediation option 2 accepted; V4 preparation). The programme has since
run through V4/V5/V6 audits and sealed the preregistration (Seal V3,
2026-09-04; see Item 3).

## Item 2 — `README.md:11`: heading "Current research state — 2026-09-01" vs ledger L-095 of 09-12

Stale by date. VERIFIED: `README.md:11` heads the section "Current research
state — 2026-09-01". VERIFIED: the ledger runs to `### L-095` at
`docs/CONTINUITY_LEDGER.md:2025`, with `timestamp_utc: 2026-09-12T14:15:06.227617Z`
(line 2003) and receipt landed `2026-09-12T14:52:03.160952+00:00` (line 2027).
The section also omits everything after V3 preflight (V4/V5/V6 audits, Seal V3,
L-093–L-095). A new collaborator reading "current … 2026-09-01" misses ~11 days
of decided state.

## Item 3 — `START_HERE_V52_4F1.md:9`: names `docs/RESEARCH_PROGRAM_STATUS_2026-08-31.md` the "authoritative operational ledger"

Misdirecting. VERIFIED: `START_HERE_V52_4F1.md:9` (HEAD blob) lists that file
as "Authoritative operational ledger". VERIFIED: its last content commit is
`6ed812fbd1d122cc94b6b149a532fe900ca9ebbd` dated 2026-09-03
(`git log -1 --format='%H %ad' --date=short` — VERIFIED output `2026-09-03`).

Pre-seal statements still inside it (VERIFIED, HEAD blob):
- `docs/RESEARCH_PROGRAM_STATUS_2026-08-31.md:24`: `[TASK 4F1 PREREGISTRATION DRAFT WRITTEN — OUTCOME-FREE; UNDER HEAD RESEARCHER REVIEW; NOT SEALED]`
- `docs/RESEARCH_PROGRAM_STATUS_2026-08-31.md:25`: `[TASK 4F1 PREREGISTRATION DECISION PENDING — STILL NOT AUTHORIZED TO RUN]`

Against: Seal V3 applied 2026-09-04. VERIFIED: `START_HERE_V52_4F1.md:39`
(HEAD blob) records "The scientific preregistration is SEALED at Seal V3
(2026-09-04)"; ledger Seal-V3 entries at `docs/CONTINUITY_LEDGER.md:600-605`
(`seal_applied`, SHA256 `c9e06195…` for V1 shown alongside; V3 `e906c6d2…`
per START_HERE). So the file START_HERE crowns as authoritative still says the
preregistration is NOT SEALED — directly contradicted by the seal the same
START_HERE reports. The live authoritative state is `ops/CURRENT_STATE.json`
(issued 2026-09-12, VERIFIED `state_id:
V52_4F1_SCIENTIFIC_PREREGISTRATION_SEALED_V3`) plus the append-only
`docs/CONTINUITY_LEDGER.md` (sole writer: Head Researcher).

## Item 4 — `START_HERE_V52_4F1.md:7`: pushed anchor at L-004-era `state/v52-4f1-v3-audit-blocked-2026-09-01`

Outdated anchor. VERIFIED: `START_HERE_V52_4F1.md:7` names branch
`state/v52-4f1-v3-audit-blocked-2026-09-01` (the L-004 anchor substitution,
VERIFIED `docs/CONTINUITY_LEDGER.md:76-89`, pushed at `531d41b` on 2026-09-01).
Later state anchors exist (VERIFIED `git branch -r` listing), including:
`origin/state/v52-4f1-v4-audit-pending-2026-09-01`,
`origin/state/v52-4f1-v4-sealed-2026-09-02`,
`origin/state/v52-4f1-v5-audit-pending-2026-09-02`,
`origin/state/v52-4f1-v6-audit-pending-2026-09-03`,
`origin/state/v52-t4f1-prereg-SEALED-V3-2026-09-04`,
plus boundary/head-tail audit state branches of 2026-09-04/05.
A cold-start collaborator pointed only at the 09-01 anchor reconstructs a
superseded world (V3-blocked, pre-V4-remediation).

## Item 5 — `PROJECT_DOCUMENTATION_MANIFEST.md:25`: START_HERE "defines the current V3 independent-audit task"

Stale description. VERIFIED: `PROJECT_DOCUMENTATION_MANIFEST.md:25` (HEAD blob)
says START_HERE "defines the current V3 independent-audit task, byte anchors,
required external corpus, safety boundary and completion condition." The V3
audit closed 2026-09-01 (Item 1); START_HERE itself (HEAD blob, lines 22–39)
now describes V3/V4/V5/V6 outcomes, the abandoned scanner strategy, and the
SEALED preregistration, with completion condition "on the execution track
only" (line 84). "Current V3 independent-audit task" has been false for ~11 days.

## Item 6 — `ops/CURRENT_STATE.json` `authority_order` still lists the V6 delta-audit prompt

Stale-by-supersession (low risk, flagged for completeness). VERIFIED:
`ops/CURRENT_STATE.json:14-21` (HEAD blob) lists in `authority_order`:
`prompts/V52_TASK_4F1_EXECUTION_CANDIDATE_V6_INDEPENDENT_DELTA_AUDIT_PROMPT_2026-09-03.md`.
The V6 audit it prompted is COMPLETE with verdict BLOCKED. VERIFIED:
`origin/audit/v52-t4f1-v6-independent-2026-09-03:audit_v52_t4f1_execution_candidate_v6_independent_audit_2026_09_03/INDEPENDENT_V6_EXECUTION_AUDIT_REPORT.md:3`:
"Verdict: `BLOCKED — DO NOT SEAL / DO NOT PREREGISTER / DO NOT RUN TASK 4F1`"
(commit `c88455bad145e0e8b26e26545d1050e1ac67ba52`, message "verdict BLOCKED").
The prompt remains correctly preserved as a historical record, but its
position in a live `authority_order` reads as a pending instruction; the
ledger (L-016ff) and CURRENT_STATE's own `task_state.v6_candidate` ("BLOCKED
… 31 evasions succeeded") already record its closure. Proposed fix is a
one-line annotation, not removal (see PROPOSED_CORRECTIONS.md).

## SEARCH FOR MORE — further ledger-superseded statements (all VERIFIED from HEAD blobs)

1. `PROJECT_DOCUMENTATION_MANIFEST.md:80` — "V3 remediation candidate and
   outcome-free synthetic preparation evidence; independent audit pending."
   Superseded by Item 1 evidence (audit closed `a590f629`, L-003).
2. `PROJECT_DOCUMENTATION_MANIFEST.md:3` — "Snapshot date: 2026-09-01".
   Superseded by ledger through L-095 (2026-09-12); the manifest never mentions
   V4/V5/V6, Seal V3, or any September post-09-01 decision.
3. `docs/CONTINUITY_PROTOCOL.md:44` — "The active state is V3 independent audit
   pending. Permitted work is limited to the V3 prompt's … checks."
   Superseded by L-003 closure and the entire V4→V7 chain; as a live protocol
   rule it mis-scopes permitted work to a closed audit's prompt.
4. `docs/RESEARCH_PROGRAM_STATUS_2026-08-31.md:18` —
   `[TASK 4F1 EXECUTION IMPLEMENTATION PREPARED — INDEPENDENT CODE AUDIT PENDING]`.
   Superseded: four independent audits (V3 `a590f629`, V4 `641568d8`, V5, V6
   `c88455b`) have since reported; the bare "pending" line predates all of them.
5. `docs/RESEARCH_PROGRAM_STATUS_2026-08-31.md:77` — "The next gate is a
   cold-start independent audit of these exact execution bytes."
   ("these" = the 08-31 V1 candidate, SHA `28735991…`, line 73.) Superseded by
   the V1→V6 chain and Seal V3; the 08-31 bytes are long superseded.
6. `docs/PROJECT_STATUS_2026-08-27.md:37-39` ("Next gate: Task 4C2 must receive
   independent adversarial audit before it is frozen as a checkpoint").
   Superseded: T4C2 audit returned `PASS WITH CONDITIONS` 2026-08-27
   (VERIFIED `audit_v52_t4c2/AUDIT_REPORT.md:3`) and the checkpoint is FROZEN
   (VERIFIED `docs/PROJECT_STATUS_2026-08-28.md:9-10`).
7. `docs/RESEARCH_PROGRAM_STATUS_2026-08-31.md:5` — "This document is the
   current operational research ledger." Superseded by its own last-commit date
   (2026-09-03) and by L-020→L-095, which never updated it; the live ledger is
   `docs/CONTINUITY_LEDGER.md` + `ops/CURRENT_STATE.json`.

Scope note: only top-level entry docs (`README.md`, `START_HERE_V52_4F1.md`,
`PROJECT_DOCUMENTATION_MANIFEST.md`, `ops/CURRENT_STATE.json`) and `docs/`
top-level status/protocol files were swept, per the task. Historical
namespace-local docs (audit reports, dated checkpoints, prompts) intentionally
describe their own moment and were not flagged.
