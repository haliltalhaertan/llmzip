[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Cache inventory — what the contract names vs what is reachable offline

Method (VERIFIED this session): `git ls-tree -r` on all ten `origin/research/e1-*` + two `origin/audit/e1-*` branches
for `*.pkl|*.npz|*.npy|*.json.gz|*.tar.gz`; local filesystem probes (`/mnt/data` absent, worktree 13 MB, no tarballs
under `/` to depth 4 for `03_regen_caches*`); `git grep` for cache paths. No network used (prohibition).

## Contract-pinned inputs (all ABSENT here)

| # | archive | sha256 pin (contract) | size (auditor-observed, CLAIM) | present? |
|---|---|---|---|---|
| 1 | `03_regen_caches.tar.gz` | `a16bdf95d3a96cb964fd6fd614d3b49d22bb9329c5afaf81cd692214d50f8aad` | 248907436 B | NO |
| 2 | `04_bench3_runs_caches.tar.gz` | `87d6312ef6c195ac6c161a8693ab635c447074c969f6573a0d0b0ca994219ae4` | 39253236 B | NO |
| 3 | `07_drive_frozen.tar.gz` | `370ea40962b078fc2fc09ab5319942b242f1559adeb62765e271f90cc21a9f59` | 173679147 B | NO |
| 4 | R1 package `E1_V2_RAW_CACHE_RECOVERY_2026-09-13.zip` | `b6b7923f2e9623f5e1d46dda523f8f4a2919b62f69e82ba5b2bb679ad9771ae8` | 531261 B | NO |

Pins VERIFIED against two independent branch sources: the contract
(`origin/research/e1-v2-raw-cache-recovery-r2-2026-09-13:.../R2_COMPETITION_RERUN_CONTRACT.md`) and the audit
`EXECUTION_LOG.txt` (`observed == expected`, `match=True`, VERIFIED). Sizes are CLAIM (auditor-observed; the 804 MB
BEAM corpus is a different, sealed artifact and is NOT among these — it must not be fetched regardless).

## Exact cache files the rerun would read (paths VERIFIED from the auditor's `competition_variants.py` bytes)

Inside archives 1–3 after extraction (auditor's `/mnt/data/e1v2_raw_audit/raw`, absent here):

- LME: `regen/lme/cache_repr/*.pkl` — 470 files; keys `question_id, C, qC, gold` (C = archive float matrix, qC = query
  vector, gold = gold row indices).
- REALTALK: `bench3/runs/b3a_realtalk/rt_repr/RT*.pkl` — 10 files; keys `qids, gold_rows, C, QC, chat_no`.
- PerLTQA: `bench3/runs/b3b_perltqa/cache_arch_eval.pkl` (`arch[char]['C']`) + `cache_q_eval.pkl`
  (`qdat[qid]: char, qC, gold, section`) — 8265 queries / 30 archives.
- LoCoMo: `regen/locomo/locomo_*.pkl` — 10 files; keys `id_to_row, qas(question_id, raw_evidence), C, QC, conv_id`,
  PLUS audit-layer corrections `drive/audit_layer/errors_conv_*.json` (audit-clean evidence mapping; 1535 valid queries).
- `Delta_q` per query: auditor Stage-1 `INDEPENDENT_QUERY_ROWS.json` (`/mnt/data/...`, NOT in git — also absent).

## What IS in git (checked, insufficient for the rerun)

- Every E1 branch carries exactly 2 binary files, both small pilot `.npz` matrices
  (`campaign_2026_09_13/pilots_round1/per_axis_matrices.npz`, `campaign_2026_09_13/pilots_round3/deney1_loco_peraxis.npz`;
  VERIFIED via `git ls-tree`). These are per-axis aggregates, NOT C/qC/gold caches — the competition metric cannot be
  computed from them.
- Checked-in JSONs carry pinned scalars and prose (headlines, coefficients, counts) but no per-query C/qC/gold rows.
- The lead's R1 raw-recovery competition script is NOT on any branch (only pilot-era min-gold snippets such as
  `.../pilots_round3/muse_sessions/d2/d2.py:61-66`, which predate the recovery and are not the R1 code). The R1
  package lives only in the Drive ZIP (absent). The auditor's `competition_variants.py` IS in git (auditor branch)
  and was used solely for post-hoc line-by-line comparison, never as an oracle.

## Consequence (decisive, skeptic-proof)

A byte-identical real-data regeneration is IMPOSSIBLE in this environment: 0 of 4 required archives reachable,
no network permitted, no extraction possible, therefore no sha256 re-verification, no headline-gate recomputation,
no per-query competition rows, no real bootstrap. Per the task terms ("a partial execution with an explicit inventory
of what was missing is a valid outcome"), this execution delivers: (a) an independent SPEC-derived implementation,
(b) machine-checked proofs of its correctness on hand-computed fixtures, (c) a deliberate bug reproduction,
(d) machine-rechecked three-reference pin consistency, (e) a runnable real-data-ready script + row schema, and
(f) an explicit BLOCKED ledger. F1 therefore stays OPEN (see `DISPOSITION.md`).
