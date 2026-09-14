[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# DELIVER 1 — EVIDENCE_INVENTORY.md (PREPARED, NOT ACCEPTED)

Branch audited: `origin/audit/v52-t4f1-v7-independent-2026-09-03` = `16dc61313acd0e9086c852eccb9100023898fd27` (VERIFIED `git rev-parse`, 2026-09-14).
Namespace on branch: `audit_v52_t4f1_execution_candidate_v7_independent_audit_2026_09_03/`.
Prompt controlling gates: `prompts/V52_TASK_4F1_EXECUTION_CANDIDATE_V7_INDEPENDENT_AUDIT_PROMPT_2026-09-03.md` lines 76-131 (VERIFIED read).
This inventory is PREPARED by a non-independent session, NOT an independent audit verdict.

## All 16 files (sha256 VERIFIED by `git show | sha256sum`, 2026-09-14)

| # | path (branch namespace) | bytes | sha256 | serves gate |
|---|---|---|---|---|
| 1 | `COMMAND_LOG.txt` | 79363 | `364a30814708026da67b282ee2241854fe88d6019b669da2dab828712109b46a` | all (provenance receipt) |
| 2 | `evidence/g1_closure_and_bindings.json` | 2118 | `9afced0d2606a4dce5ce775ced81cc870e0cf75db0278af6d0c7304fd3bae5d4` | G1 closure/bindings |
| 3 | `evidence/g1_corpus_verification.json` | 324 | `f1e63fe84bf0f2c75db9b47e891448872f80078fc549bc196641ddba92380680` | G1/PRE corpus check |
| 4 | `evidence/g2_change_isolation.json` | 1653 | `7a92b62cbea1caba587dbca30fa5e432dbe6d5fbbe4809717b0ffb2031982805` | G2 change isolation |
| 5 | `evidence/g32_evasion_replay.json` | 22006 | `212f747f9b3b9af91db38a891b6f56a6f8636dd25a39557b4fb40d73831aa892` | G3.2 evasion replay (9 classes x 5 sites = 45 rows) |
| 6 | `evidence/g34_cross_document_consistency.json` | 11102 | `a76d2f1bd0d5aed83a3da6532d97ceee15117b68ca59779b0b356265c8bb7656` | G3.4 unbound-doc consistency |
| 7 | `evidence/g35_fixture_results.json` | 15728 | `934d78df18ec96d7a540dd4f0bd6c5840141cce74a18dcf1da039413654c5b67` | G3.5/G5/G1 fixture set (29 rows; 1 disagreement F15) |
| 8 | `evidence/g6_preflight_guardrails.json` | 1235 | `d778d9d2b4c332841ce1512a1da21afd6f6742e661f12d3c66723bdd5b971600` | G6 preserved gates |
| 9 | `evidence/g7_bound_payload_restatements.json` | 11400 | `a7326406096ca4970c5b3800545cbe5e372c6781b233cc4bb04379a0703c6d03` | G7 restatement scan (21 pairs, 0 disagreements CLAIM) |
| 10 | `evidence/g7_failclosed_authorization.json` | 2337 | `b4656a365845c147206b648e7a00a04cc444e2f6758c47347543028b73b07399` | G7 fail-closed authorization |
| 11 | `scripts/g1_verify_corpus.py` | 1960 | `b8db6f1f2fc224407199b660bcfd80977e2426a45a8e9fe44324a63b66a57942` | G1 method |
| 12 | `scripts/g32_evasion_replay.py` | 6548 | `2cd7ffeda9f67fbdcc66eba9d9dfda46ab6b9e334a20013e62d64d9cfd188a77` | G3.2 method |
| 13 | `scripts/g34_cross_document_consistency.py` | 5768 | `dd69782b38b71bbddfaab6e2ad893f26e12257f70de4859a3e561f6a911c7f2c` | G3.4 method |
| 14 | `scripts/g35_fixtures.py` | 12502 | `7f91ba1659fc86a042ef846a1942480278773b5a874165c57c0de3285aeb58a1` | G3.5/G5 method |
| 15 | `scripts/g7_bound_payload_restatements.py` | 7898 | `7cba4f8f324127dd78893d825e12856679229c5cf83534ceff770a4ed3b80c27` | G7 method |
| 16 | `scripts/safe_harness.py` | 3315 | `f885ef52bc692066f091c90f3d318a6c4499c5b0ea9c6c41b7b474ae61672289` | all (run/finalize refusal harness) |

Machine-readable copy: `V7_BRANCH_EVIDENCE_MANIFEST.json` in this namespace (16 entries; banner carried as first JSON key because a bare text line would invalidate JSON — see REPORT.md).

## Prompt-mandated outputs with NO evidence (all VERIFIED `git cat-file -e`, 2026-09-14)
- `INDEPENDENT_V7_EXECUTION_AUDIT_REPORT.md`: ABSENT.
- `GATE_TABLE.csv`: ABSENT.
- `INDEPENDENT_V7_EXECUTION_AUDIT_HASHES.json`: ABSENT. Consequence: the branch carries NO hash manifest, so the 16 pushed files cannot be completeness-checked as a package; the manifest in this deliverable is prepared by a non-independent session and does not cure that.
- Verdict (either `PASS — V7 ...` or `BLOCKED — ...` per prompt lines 150-160): ABSENT — full `git ls-tree -r` of the audit namespace lists only the 16 files above; no report/verdict file exists.

## Prompt-mandated gates with NO dedicated evidence file
- **Gate 4** (prompt lines 111-114: seal submission-status-only, no status/acceptance/sealed field, inventory status-free, no redirectable acceptance pointer): NO `evidence/g4*` file (VERIFIED absent). Partial overlap only: branch `g35_fixture_results.json` rows F16-F19 exercise seal/inventory status mutations (RELAYED, not re-run here).
- **Gate 5** (prompt lines 116-118: positive + negative fixtures of own construction against the V7 checker): NO `evidence/g5*` file (VERIFIED absent). Branch `g35_fixture_results.json` (29 fixtures, incl. F00 positive control) is Gate 1/3/5-mixed coverage, not the prompt's Gate 5 set; implementer fixtures were read for coverage only per the prompt and are not independent evidence.
- **Gate 3.1 / 3.3** (set-equality confirmation; attacking set equality: rename/embed/symlink/case/unicode/declared-vs-disk): no dedicated `g31`/`g33` files (VERIFIED absent), but branch `g35_fixture_results.json` F05-F14 covers rename/embed/case/unicode/symlink/declared-mismatch/empty-inventory/duplicate-entry (RELAYED).
- **Gate 3.5 synthesis** (prompt line 109: ESTABLISHED vs NOT-YET-FALSIFIED): NO `evidence/g35_synthesis.json` (VERIFIED absent). Branch `g35_fixture_results.json` holds fixture rows, not the synthesis judgment.
- Gates 1, 2, 3.2, 3.4, 6, 7 have branch evidence files (rows 2-10 above); their contents are CLAIMs relayed here, re-verifiable only by an independent session.

## Gates affected by the missing manifest
All of them: without `INDEPENDENT_V7_EXECUTION_AUDIT_HASHES.json` binding exact V7 anchors (prompt lines 131-136), no downstream consumer can check that the 16 files are the complete, unaltered audit package.
