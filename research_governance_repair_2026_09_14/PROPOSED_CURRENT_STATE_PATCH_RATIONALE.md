[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Rationale for PROPOSED_CURRENT_STATE_PATCH.json (PREPARED, NOT ACCEPTED)

## Edit 1 — top-level `next_single_action: null` → proposed review action

VERIFIED current state: `"next_single_action": null` at `ops/CURRENT_STATE.json:2080`; the only live direction text is `task_state.next_single_action` at `ops/CURRENT_STATE.json:25` (a long paragraph ending "Task4F1 run BLOCKED / outcome access FORBIDDEN."). CLAIM (governance rule the project set for itself): `docs/CONTINUITY_LEDGER.md:7` requires every transition to name "exactly one next action", and the schema at `docs/CONTINUITY_LEDGER.md:12-24` makes `next_single_action` load-bearing. A null at top level means a successor reading only head keys finds no action, while a paragraph buried one level down is doing that job — the exact de-staling the Head Researcher's 2026-09-03 item 6 demanded (`ops/CURRENT_STATE.json:383-395`). The proposed text names the single pending governance step (review this repair namespace) and re-states BLOCKED/FORBIDDEN so the edit implies no new authority. No seal, run, or outcome access is proposed or implied.

## Edit 2 — `authority_order[5]` (V6 delta-audit prompt) → remove or mark historical

VERIFIED current state: the 6th `authority_order` element is the V6 independent delta-audit prompt (`ops/CURRENT_STATE.json:20`). VERIFIED closure before proposing: the V6 audit returned BLOCKED — `docs/CONTINUITY_LEDGER.md:330` (verdict DO NOT SEAL / DO NOT PREREGISTER / DO NOT RUN TASK 4F1), `docs/CONTINUITY_LEDGER.md:337` (`status: BLOCKED`), `ops/CURRENT_STATE.json:36` (`v6_candidate` BLOCKED, 31 evasions). A prompt is an instruction; keeping a completed audit's prompt in the live authority list risks a cold-start successor treating it as pending work. The entry points already say otherwise — VERIFIED: `START_HERE_V52_4F1.md:12` ("Audit prompts under `prompts/` are historical records of completed audits, not pending work") and `START_HERE_V52_4F1.md:8` ("The V6 audit is COMPLETE and returned BLOCKED; do not re-run it"). This edit only aligns the state file with those docs. Either deletion or an explicit `(HISTORICAL …)` marker achieves it; both are offered so the sole writer picks the smaller diff.

## Minimality

Two edits, no other key touched (no `task_state` text change, no anchors, no seals, no `ledger_entry`, no hard stops). If the writer prefers, Edit 1 could instead copy the `task_state` paragraph verbatim to top level — recorded here as a considered alternative, not proposed, because a pointer to the pending review is more actionable than duplicating a paragraph.
