# V52 — Proposed L-088: Muse budget audit disposition and PQ archive-local training adequacy

**Date:** 2026-09-11
**Prepared by:** ChatGPT continuity/research session, from canonical `main` at `489e5f94c344c9cee02aa357ff3d59c2029f5846` (L-087).
**Status:** PROPOSED / HASH-BOUND DRAFT. This file is **not** a canonical ledger entry and does not advance `ops/CURRENT_STATE.json`. It is prepared for byte-level review before any append to `docs/CONTINUITY_LEDGER.md`.
**Branch:** `hr/l088-muse-pq-disposition-2026-09-11`

## Why this is a draft rather than a direct L-088 append

The programme's ledger-authorship rule binds a verification claim to the session that actually ran the verification. This session can independently verify repository bytes and the Faiss v1.15.0 source-level clustering rule, but it cannot access or rerun the operator-local Muse report, raw Muse JSONL, Windows Faiss probes, serialization measurements, or archive-size measurements described in chat. Those observations are therefore recorded below as **RELAYED / NOT LOAD-BEARING UNTIL THEIR BYTES ARE PUSHED AND VERIFIED**, never as this session's reproduced evidence.

## Independently verified here

### V1 — canonical state before this draft

- `refs/heads/main` resolves to `489e5f94c344c9cee02aa357ff3d59c2029f5846`.
- L-087 is the newest canonical ledger entry on that commit.
- Task 4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.

### V2 — the Muse task has a stale canonical-context anchor

The pushed task file `prompts/V52_TWELVE_BYTE_BUDGET_MUSE_AUDIT_TASK_2026-09-11.md`, present on L-087, tells the auditor that repository `main` is `7e1de3af60b237766e21bf45d97018add8fe2eb1`. The task itself is introduced one commit later, at L-087 / `489e5f94...`.

This makes three refs logically distinct and they must never again be collapsed:

1. **object-under-audit ref** — the exact artifact being graded;
2. **audit-task ref** — the commit containing the audit instructions themselves;
3. **canonical-context ref** — the actual `refs/heads/main` at audit start.

A future audit must resolve and record all three before grading. A historical object may intentionally be old; the canonical context may not be silently pinned to the same old tree unless the task explicitly says that current errata/governance are to be ignored.

### V3 — L-087 already corrects L-086's Faiss/RaBitQ availability error

L-086 says `faiss-cpu` does not supply RaBitQ. L-087 explicitly records this as an error and states that `faiss-cpu 1.15.0` does supply RaBitQ. Therefore an auditor restricted to the stale `7e1de3a` context can rediscover a defect already closed additively at L-087. That is a task-context defect, not a new programme finding.

### V4 — the 12-byte preregistration is archive-local by construction

The pushed preregistration at `draft/v52-twelve-byte-baseline-prereg-2026-09-10` / `d2cfbaacdfc52af2ac2077ffa1d87b719a7d0779` says every arm consumes the same frozen 96-dimensional centered representation and that all fitting — rotations, codebooks and centroids — is **archive-only**, on the per-question `C / qC` pair.

Consequences:

- panel question count is not the amortization denominator for archive-local method state;
- if method-specific state is fitted separately per archive, its descriptive effective storage is `marginal_bytes + shared_bytes / N_archive`, where `N_archive` is the number of stored vectors in that archive;
- a target-scale `N*=10,000,000` may be used only as a **storage projection** if preregistered as such; it is not evidence that retrieval quality at 10M is measured by this stage;
- Task 4F1 remains the separate sealed scale experiment and is not approached by this baseline stage.

### V5 — Faiss v1.15.0's default clustering warning threshold

Official Faiss v1.15.0 source defines `ClusteringParameters::min_points_per_centroid = 39` and documents that if fewer than this number of training vectors per centroid are supplied, Faiss emits a warning; fewer than one training point per centroid is the hard error case.

Therefore for a PQ subquantizer with `nbits=b`, `k=2^b` and the default warning threshold is `39*k` training vectors:

| 12-byte PQ layout | k | Faiss default warning threshold |
|---|---:|---:|
| `m=12, nbits=8` | 256 | 9,984 |
| `m=16, nbits=6` | 64 | 2,496 |
| `m=24, nbits=4` | 16 | 624 |
| `m=48, nbits=2` | 4 | 156 |

**Important wording correction:** crossing this threshold is not the definition of “trainable.” Falling below it produces Faiss's own reliability warning; training can still run when `n >= k`. The scientifically defensible statement is therefore:

> Under the operator-reported archive-size range 396–616, `m=48, nbits=2` is the only listed 12-byte configuration that clears Faiss's default `39 points/centroid` recommendation across the entire range. `m=24, nbits=4` falls just below the recommendation even at the reported maximum archive size; the higher-cardinality configurations are much farther below it.

The archive-size range itself is **not independently verified in this session** and must not become load-bearing until its source bytes or a reproducible measurement are pushed.

### V6 — PQ result interpretation must separate method quality from the archive-local training regime

Because the preregistration requires archive-only fitting, any PQ arm is being tested under a small-sample, per-archive codebook-learning regime. A weak result from `m=12, nbits=8` cannot by itself justify the general statement “PQ is weak.” At most it establishes performance of that PQ configuration under the programme's archive-local fitting rule and observed archive sizes.

Conversely, changing to pooled/global PQ training would change the estimand and violate the current preregistration's archive-only fitting rule unless a new preregistered arm explicitly permits it.

## Relayed operator-local evidence — not independently reproduced here

The following are useful evidence claims reported by the operator, but this session did not run them and cannot inspect their local files. They are **not canonical evidence until the corresponding bytes are pushed and independently verified**:

1. Muse completed successfully under `--approval-mode never --user-input-auto-resolve --disable-write`, with 28 model turns, 27 bash calls and exit 0.
2. Muse grades and the operator's counter-checks for C1–C12, including the C7 Linux/Windows stage difference, C9 seedability finding, C10 functional version boundary, and C11 source-location issue.
3. Serialization measurements for `SIGN96`, `TOP32_RABITQ32`, `RABITQ96`, `PQ96`, and `OPQ_PQ96`, including marginal/shared decompositions.
4. Operator-reported archive sizes 396–616, mean 492.78.
5. The observation that `m=12x8`, `m=16x6`, and `m=24x4` trigger the Faiss low-training-count warning in the measured archives while `m=48x2` clears the default recommendation.
6. Distinct-code fraction measurements.

Required evidence package before any of these become load-bearing: the Muse report, answer key, hash of the raw Muse JSONL, exact Faiss/package/platform record, serialization measurement script and machine-readable output, PQ training-adequacy script and machine-readable output, and hashes for each file.

## Scientific disposition proposed for the twelve-byte baseline revision

No retrieval outcome should be computed before a single new preregistration revision fixes all of the following together:

1. **Primary budget definition:** `marginal persistent bytes per stored memory <= 12` including all per-vector auxiliary data.
2. **Shared-state reporting:** report absolute serialized method-specific shared bytes separately; archive-local descriptive amortization uses `N_archive`, never benchmark question count. Any `N*=10M` value is labelled a target-scale storage projection only.
3. **Arm naming:** if RaBitQ reaches the cap through deterministic 96→32 truncation, call the arm `TOP32_RABITQ32`, not `RABITQ96`.
4. **PQ training regime:** bind the 12-byte PQ configuration before outcomes. If `m=12x8` is retained, the preregistration must explicitly state that it operates far below Faiss's default points-per-centroid recommendation in these archive-local fits. If a lower-cardinality 12-byte PQ layout is added, its scientific role must be declared prospectively rather than chosen after outcomes.
5. **No false “only trainable” language:** Faiss's `39*k` threshold is a warning/reliability recommendation, not a hard trainability boundary.
6. **Actual-size gate:** every arm must assert its actual code/serialized marginal size against the declared cap before any retrieval metric is computed.
7. **Seed scope:** only genuinely seed-controllable stochastic training receives a declared seed panel. Do not invent seeds for deterministic arms or for training components whose randomness is not exposed by the pinned implementation.
8. **Positive-control provenance:** frozen controls are derived from named, hash-pinned source artifacts; rounded decimals copied into prose are not themselves the authority.
9. **Decision rule over the cap set:** no result may be framed as “SIGN96 competitive” merely because it beats one chosen comparator while another legal <=12-byte arm beats SIGN96 materially. The competitive-set rule and delta/CI criterion must be written before outcome access.
10. **Task separation:** mechanism-track interpretation corrections (`frac_block`, `[MOST]`) remain in that track's deviation record and are not smuggled into the baseline preregistration.

## Proposed L-088 ledger text

```text
### L-088

timestamp_utc: 2026-09-11T[SET_AT_CANONICAL_APPEND]Z
actor_role: Continuity Lead / research verifier session
predecessor_commit_or_tag: L-087 / 489e5f94c344c9cee02aa357ff3d59c2029f5846
scope: Disposition the twelve-byte Muse audit context defect and the archive-local PQ training-adequacy issue before any baseline retrieval run. Verification/recording only. No experiment, no seal, no pilot, no retrieval outcome access, no Task 4F1 contact.
changed_or_created_paths: [THIS HASH-BOUND DISPOSITION ARTIFACT]; docs/CONTINUITY_LEDGER.md; ops/CURRENT_STATE.json
verification: Canonical main ref re-read as 489e5f94...; the Muse task's embedded canonical-context anchor verified stale at 7e1de3a; L-087 verified to already correct L-086's false Faiss/RaBitQ availability claim; the pushed twelve-byte preregistration verified to require per-question-archive, archive-only fitting on the frozen 96D representation; official Faiss v1.15.0 source verified `min_points_per_centroid=39`, yielding default warning thresholds 9984 / 2496 / 624 / 156 for the listed 12-byte PQ layouts. Operator-local Muse, serialization, platform and archive-size measurements are explicitly NOT claimed as independently reproduced by this entry and remain non-load-bearing until their bytes are pushed and verified.
audit_context_rule: Future audits bind three separate refs at start: object-under-audit, audit-task, and live canonical context. A stale object ref does not silently freeze the canonical errata/governance context.
pq_training_rule: Faiss's 39*k threshold is a warning/reliability recommendation, not a hard trainability boundary. Under the relayed 396–616 archive-size range, m=48x2 is the only listed 12-byte PQ layout that would clear the default recommendation throughout; this numerical range remains provisional until source evidence is pushed.
baseline_revision_requirements: one prospective revision must bind marginal persistent <=12 B/vector, archive-local shared-state accounting, honest arm names including TOP32_RABITQ32 if adopted, actual-size aborts, true seed scope, hash-derived positive controls, a prospectively chosen PQ layout/training interpretation, and a competitive-set decision rule before any retrieval outcome is computed.
outcome_boundary: Unchanged. Task 4F1 scientific preregistration SEALED at Seal V3; run BLOCKED; production authorization NONE; retrieval-quality outcome access FORBIDDEN. No baseline retrieval metric is authorized by this entry.
status: PASS WITH FINDINGS — source-level/control disposition only; NOT baseline execution readiness.
next_single_action: Push and independently verify the Muse/storage/PQ evidence package, then issue one revised twelve-byte preregistration digest incorporating the already identified budget, cost-accounting, seed, positive-control and PQ-training rules before any new retrieval run.
```

## Explicit non-claims

- This draft does **not** claim the operator-local Muse run was independently reproduced here.
- It does **not** claim `m=48x2` is necessarily the best PQ arm; it only clears the Faiss default points-per-centroid recommendation under the relayed archive-size range.
- It does **not** claim unique-code fraction diagnoses centroid quality.
- It does **not** authorize the proposed two-arm retrieval run.
- It does **not** modify or reinterpret Task 4F1.
