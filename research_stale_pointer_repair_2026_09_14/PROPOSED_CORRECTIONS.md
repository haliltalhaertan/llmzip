[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# DELIVER 2 — Proposed corrections (PREPARED, NOT ACCEPTED)

Rule: MINIMAL, history-preserving — add a dated "superseded by" line, never
rewrite narrative. None of the targets below carries a `.sha256` sidecar
(VERIFIED: the 20 sidecars on HEAD cover only `docs/v52/*`, preregistration
seals, and four `prompts/*` files — see SIDECAR_AND_ANCHOR_RECHECK.md), so
direct minimal amendment is *proposable*. If the Head Researcher prefers, the
same lines can ship as an additive erratum file instead. The additive-only rule
for sidecar-hashed documents is cited at the end, per
`docs/CONTINUITY_LEDGER.md:1249` ("any document carrying a .sha256 sidecar or
whose hash has been recorded in the ledger is additive-only").

## C1 — `README.md:11` heading

BEFORE:
```
## Current research state — 2026-09-01
```
AFTER:
```
## Current research state — 2026-09-01 (section frozen at that date; superseded by ledger L-003→L-095, 2026-09-01→2026-09-12 — see docs/CONTINUITY_LEDGER.md and ops/CURRENT_STATE.json)
```

## C2 — `README.md:46` V3-audit sentence

BEFORE:
```
…V3 repairs those defects and has passed only implementer-side outcome-free preflight and synthetic regressions. A fresh cold-start V3 audit is still required; no Task 4F1 result has been accessed.
```
AFTER:
```
…V3 repairs those defects and had, at the time of writing, passed only implementer-side outcome-free preflight and synthetic regressions. [SUPERSEDED 2026-09-01: the cold-start V3 independent audit closed the same day with verdict BLOCKED (branch audit/v52-t4f1-v3-independent-2026-09-01, commit a590f629; ledger L-003); the programme has since proceeded through V4/V5/V6 audits and Seal V3 (2026-09-04).] No Task 4F1 result has been accessed.
```

## C3 — `START_HERE_V52_4F1.md:9` authoritative-ledger pointer

BEFORE:
```
- **Authoritative operational ledger:** `docs/RESEARCH_PROGRAM_STATUS_2026-08-31.md`.
```
AFTER:
```
- **Authoritative operational ledger:** `docs/CONTINUITY_LEDGER.md` with live state `ops/CURRENT_STATE.json` (both sole-writer, Head Researcher). `docs/RESEARCH_PROGRAM_STATUS_2026-08-31.md` is a frozen 2026-09-03 snapshot — historical context only, not authoritative.
```

## C4 — `START_HERE_V52_4F1.md:7` pushed anchor

BEFORE:
```
- **Repository state:** canonical branch `main`. Tag pushes are refused by the current environment, so the pushed anchor is branch `state/v52-4f1-v3-audit-blocked-2026-09-01`; use the current `main` head or a descendant explicitly reviewed by the Head Researcher.
```
AFTER:
```
- **Repository state:** canonical branch `main` (ledger L-095, 2026-09-12). Tag pushes are refused by the current environment; the L-004-era pushed anchor `state/v52-4f1-v3-audit-blocked-2026-09-01` is HISTORICAL. Later state anchors exist (e.g. state/v52-4f1-v6-audit-pending-2026-09-03, state/v52-t4f1-prereg-SEALED-V3-2026-09-04); use the current `main` head or a descendant explicitly reviewed by the Head Researcher.
```

## C5 — `PROJECT_DOCUMENTATION_MANIFEST.md:25` START_HERE description

BEFORE:
```
- `START_HERE_V52_4F1.md` — single operational handoff for a cold-start researcher/LLM; defines the current V3 independent-audit task, byte anchors, required external corpus, safety boundary and completion condition.
```
AFTER:
```
- `START_HERE_V52_4F1.md` — single operational handoff for a cold-start researcher/LLM; [SUPERSEDED 2026-09-01: the V3 independent audit it was written to define has closed (BLOCKED, L-003). The file now tracks the V4→V6 chain and the sealed preregistration;] byte anchors, required external corpus, safety boundary and completion condition.
```

## C6 — `PROJECT_DOCUMENTATION_MANIFEST.md:80` "independent audit pending"

BEFORE:
```
- `task4f1_execution_candidate_v3_2026_09_01/` and `task4f1_execution_candidate_v3_preflight_2026_09_01/` — V3 remediation candidate and outcome-free synthetic preparation evidence; independent audit pending.
```
AFTER:
```
- `task4f1_execution_candidate_v3_2026_09_01/` and `task4f1_execution_candidate_v3_preflight_2026_09_01/` — V3 remediation candidate and outcome-free synthetic preparation evidence; [SUPERSEDED 2026-09-01: independent audit closed BLOCKED (a590f629; L-003). Preserved byte-unchanged as evidence.]
```

## C7 — `ops/CURRENT_STATE.json` `authority_order` V6 prompt entry

BEFORE (element 6 of `authority_order`):
```
"prompts/V52_TASK_4F1_EXECUTION_CANDIDATE_V6_INDEPENDENT_DELTA_AUDIT_PROMPT_2026-09-03.md"
```
AFTER — annotate in place (key order and membership unchanged; prompt preserved as historical record):
```json
"authority_order": [
  "START_HERE_V52_4F1.md",
  "ops/CURRENT_STATE.json",
  "docs/CONTINUITY_LEDGER.md",
  "docs/RESEARCH_PROGRAM_STATUS_2026-08-31.md",
  "CHAIN_OF_CUSTODY.md",
  "prompts/V52_TASK_4F1_EXECUTION_CANDIDATE_V6_INDEPENDENT_DELTA_AUDIT_PROMPT_2026-09-03.md [CLOSED — audit returned BLOCKED 2026-09-03; retained as historical record, not pending work]"
]
```
NOTE: `ops/CURRENT_STATE.json` is the live single-writer state file (rewritten
every entry by the Head Researcher), not a sidecar-hashed publication — the
ledger's forward rule (L-062, `docs/CONTINUITY_LEDGER.md:1249`) explicitly keeps
in-place revision available for it. This annotation is therefore proposed as a
direct state-file update by the sole writer, not as contributor-side editing.

## C8 — sweep findings (same minimal pattern)

- `PROJECT_DOCUMENTATION_MANIFEST.md:3`: append "— snapshot frozen 2026-09-01;
  superseded by ledger L-003→L-095" to the snapshot-date line.
- `docs/CONTINUITY_PROTOCOL.md:44`: prefix "The active state is V3 independent
  audit pending." with "[SUPERSEDED 2026-09-01 by L-003 — retained as the
  historical boundary that governed the V3 audit window.]" (protocol body
  otherwise untouched; any live boundary update is a Head Researcher decision).
- `docs/RESEARCH_PROGRAM_STATUS_2026-08-31.md:5,18,24-25,77`: no line edits
  proposed — the whole file is a frozen-dated snapshot. One additive header
  line under the title: "[FROZEN SNAPSHOT — last updated 2026-09-03 (commit
  6ed812f); superseded by docs/CONTINUITY_LEDGER.md L-020→L-095 and
  ops/CURRENT_STATE.json. Pre-seal lines 24–25 retained as history.]"
- `docs/PROJECT_STATUS_2026-08-27.md:37-39`: no edit — dated checkpoint whose
  "Next gate" was discharged by the 2026-08-27 T4C2 audit. If cross-linked,
  add: "[DISCHARGED 2026-08-27: T4C2 audit PASS WITH CONDITIONS.]"

## Additive-only rule citation

VERIFIED `docs/CONTINUITY_LEDGER.md:1249` region (L-062 forward rule): "on main,
any document carrying a .sha256 sidecar or whose hash has been recorded in the
ledger is additive-only — supersede it with a new file and record both hashes;
in-place revision stays available for unpublished drafts on draft branches and
for the live state file." Had any needed correction landed in a sidecar-hashed
document, the proposal would have been an additive erratum file beside it (new
file + both hashes recorded), never an in-place edit. No such case arose: none
of C1–C8's targets carries a sidecar. Caveat-adding fixes in DELIVER 4 fall
under the same test — see CAVEAT_PROPAGATION.md for the per-target sidecar
check.
