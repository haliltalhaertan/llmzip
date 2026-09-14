[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# PROPOSED ledger entry L-096 (PREPARED_NOT_ACCEPTED — NOT appended to the real ledger)

Schema source VERIFIED: `docs/CONTINUITY_LEDGER.md:12-24` (```text fence; keys below match the well-formed entry L-003 at `docs/CONTINUITY_LEDGER.md:59-74`). The sole-writer rule (`ops/CURRENT_STATE.json:186-191`, concurrency.state_writer = Continuity Lead only; ledger authorship rule at `ops/CURRENT_STATE.json:200-205`) reserves appending for the Head Researcher/Continuity Lead — this session is neither, so this entry is PREPARED as a separate file and the real ledger is untouched.

```text
L-096
timestamp_utc: UNAVAILABLE-UNDER-SEAL (to be set by the sole writer at append time; this draft prepared 2026-09-14)
actor_role: Continuity Lead (sole writer) — PROPOSED, not acted
predecessor_commit_or_tag: L-095 / 5ec3db60c03edde490374bf9cd7c3e56dd6bcd00
scope: Repair three classes of governance-record gaps without touching any sealed, audited or historical byte: (a) head entry L-095 carries no schema keys; (b) ops/CURRENT_STATE.json top-level next_single_action is null while task_state.next_single_action carries the live direction; (c) seven existing research lines have zero ledger/state mentions; (d) V5/V6 audit findings missing from L-014/L-018 are registered in a separate defect register; (e) the 25-vs-31 evasion count scope is fixed in a separate note. No candidate, seal, manifest, audit namespace, corpus byte or historical record is modified by this proposal.
changed_or_created_paths: research_governance_repair_2026_09_14/PROPOSED_LEDGER_ENTRY_L096.md; research_governance_repair_2026_09_14/PROPOSED_CURRENT_STATE_PATCH.json; research_governance_repair_2026_09_14/PROPOSED_CURRENT_STATE_PATCH_RATIONALE.md; research_governance_repair_2026_09_14/VANISHED_DEFECT_REGISTER.md; research_governance_repair_2026_09_14/EVASION_COUNT_SCOPE_NOTE.md (all PROPOSED, none landed in canonical paths)
verification: L-095 key count re-derived 0 (grep of docs/CONTINUITY_LEDGER.md:2025-2045 for ^(timestamp_utc|actor_role|predecessor_commit_or_tag|scope|changed_or_created_paths|verification|outcome_boundary|status|next_single_action|handoff_payload): returns 0). CURRENT_STATE top-level next_single_action is null (ops/CURRENT_STATE.json:2080) while task_state.next_single_action carries text (ops/CURRENT_STATE.json:25). Slug census re-run: grep -c over docs/CONTINUITY_LEDGER.md and ops/CURRENT_STATE.json returns 0 for each of e1-, static-storage, rank-cert, representation-geometry, campaign-2026, preseal-cost, coldstart-continuity; branch identities below re-derived from git for-each-ref over 137 refs/remotes/origin/* entries. V6 audit closed BLOCKED (L-018 status BLOCKED at docs/CONTINUITY_LEDGER.md:337; ops/CURRENT_STATE.json:36 v6_candidate BLOCKED). Existence-only record below: no scientific result from any listed branch is endorsed, accepted or restated.
outcome_boundary: No --mode run, no --mode finalize, no run_archives/evaluate_archive/finalize_results on real data, no V52_T4F1_AUTH_HMAC_KEY_HEX, no valid authorization, no real retrieval ID/distance/metric/arm-outcome access, no corpus/query/label/embedding opened, no sealed or historical byte modified. Task4F1 run stays BLOCKED; outcome access stays FORBIDDEN.
status: PREPARED_NOT_ACCEPTED
next_single_action: Head Researcher reviews research_governance_repair_2026_09_14/ (this proposal, the state patch, the defect register and the evasion-count note) and issues adopt-as-L-096, adopt-with-edits, or reject; until then no ledger append, seal, run authorization or outcome access occurs.
handoff_payload: This file; PROPOSED_CURRENT_STATE_PATCH.json + rationale; VANISHED_DEFECT_REGISTER.md; EVASION_COUNT_SCOPE_NOTE.md; receipts/ (for-each-ref.txt, V5/V6 GATE_TABLE.csv copies, slug-zero-hits.txt).
```

## Evidence annex (VERIFIED; existence and branch identity ONLY — no scientific endorsement)

Head-entry gap (VERIFIED): L-095 at `docs/CONTINUITY_LEDGER.md:2025-2045` consists of a prose published-package paragraph plus a reproduced independent-executor receipt body (`docs/CONTINUITY_LEDGER.md:2029-2045`). Schema-key count found: **0** of the 11 schema keys (`L-NNN` + the 10 keys at `docs/CONTINUITY_LEDGER.md:12-24`).

State-file gap (VERIFIED): top-level `"next_single_action": null` at `ops/CURRENT_STATE.json:2080`; live direction text lives one level down at `task_state.next_single_action`, locator `ops/CURRENT_STATE.json:25` (starts "Recover exact mechanism-track frozen C arrays … Task4F1 run BLOCKED / outcome access FORBIDDEN.").

Unmentioned research lines (VERIFIED zero-hit census; counts are grep -c hits in ledger / state; branch sha+date from `git for-each-ref` over `refs/remotes/origin/`):

| slug | ledger hits | state hits | branches (short sha, date) — existence only |
|---|---|---|---|
| `e1-` | 0 | 0 | origin/audit/e1-mechanism-checkpoint-independent-2026-09-13 (ec40dc3, 2026-09-13); origin/audit/e1-v2-raw-cache-recovery-independent-2026-09-13 (010bcbb, 2026-09-13); origin/research/e1-lme-secondary-run-2026-09-13 (4bfdb82, 2026-09-13); origin/research/e1-mechanism-checkpoint-frozen-2026-09-13 (4bfdb82, 2026-09-13); origin/research/e1-sign-float-mechanism-2026-09-13 (3444fa9, 2026-09-13); origin/research/e1-sign-float-mechanism-frozen-2026-09-13 (d1e429c, 2026-09-13); origin/research/e1-sign-float-mechanism-v2-2026-09-13 (775a09c, 2026-09-13); origin/research/e1-sign-float-mechanism-v2-frozen-2026-09-13 (775a09c, 2026-09-13); origin/research/e1-v2-raw-cache-recovery-2026-09-13 (d544169, 2026-09-13); origin/research/e1-v2-raw-cache-recovery-r2-2026-09-13 (d5edeb3, 2026-09-13) |
| `static-storage` | 0 | 0 | origin/audit/v52-static-storage-integrated-v10-independent-2026-09-13 (9802b49, 2026-09-13); origin/audit/v52-static-storage-inventory-independent-2026-09-12 (22b58b6, 2026-09-12); origin/audit/v52-static-storage-plan-prep-v2-independent-2026-09-12 (1165453, 2026-09-12); origin/audit/v52-static-storage-plan-prep-v3-independent-2026-09-12 (b06247d, 2026-09-12); origin/codex/v52-static-storage-contract-2026-09-12 (552088a, 2026-09-12); origin/codex/v52-static-storage-plan-prep-2026-09-12 (74455f8, 2026-09-12); origin/codex/v52-static-storage-plan-prep-v2-2026-09-12 (ecd839b, 2026-09-12); origin/codex/v52-static-storage-plan-prep-v3-2026-09-12 (3fab24b, 2026-09-12); origin/fix/v52-static-storage-integration-v8-2026-09-13 (0cb4aba, 2026-09-13); origin/fix/v52-static-storage-integration-v9-2026-09-13 (b300cbf, 2026-09-13); origin/fix/v52-static-storage-plan-prep-v4-2026-09-12 (695e3c7, 2026-09-12/13); origin/fix/v52-static-storage-plan-prep-v7-2026-09-13 (5eac888, 2026-09-13); related different-slug branches NOT counted in this line: origin/findings/static-concurrency-v10-2026-09-13, static-denominator-v10, static-integrated-v10, static-security-tests (all 2026-09-13) |
| `rank-cert` | 0 | 0 | origin/findings/rank-cert-repair-2026-09-14 (dbb3ee0, 2026-09-14) |
| `representation-geometry` | 0 | 0 | origin/findings/representation-geometry-2026-09-13 (75b7e05, 2026-09-13) |
| `campaign-2026` | 0 | 0 | origin/findings/campaign-2026-09-13 (493f173, 2026-09-13) |
| `preseal-cost` | 0 | 0 | origin/codex/v52-preseal-cost-worker-2026-09-12 (44ae95a, 2026-09-12); related different-slug branches NOT counted: origin/codex/v52-preseal-itq-worker-2026-09-12, origin/research/v52-preseal-diagnostics-2026-09-12 |
| `coldstart-continuity` | 0 | 0 | origin/audit/coldstart-continuity-claims-2026-09-09 (72a691e, 2026-09-10) |

Receipts: `receipts/for-each-ref.txt` (137 refs with full sha), `receipts/slug-zero-hits.txt`.
