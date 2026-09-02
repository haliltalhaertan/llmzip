# Start Here — V52 Task 4F1 preregistration-decision handoff

This is the single operational entry point for a new Head Researcher, Compute Expert, or independent auditor resuming the V52 BEAM work.

## Exact starting point

- **Repository state:** canonical branch `main`. Tag pushes are refused by the current environment, so the pushed anchor is branch `state/v52-4f1-v3-audit-blocked-2026-09-01`; use the current `main` head or a descendant explicitly reviewed by the Head Researcher.
- **Current task:** build the V5 candidate remediating co-chair blocking finding CC-01, then have it independently audited. The V4 audit evidence stands, but the V4 package is NOT co-signed as sealed.
- **Authoritative operational ledger:** `docs/RESEARCH_PROGRAM_STATUS_2026-08-31.md`.
- **Byte-preservation and provenance rules:** `CHAIN_OF_CUSTODY.md` and `DATASETS_AND_LARGE_ARTIFACTS.md`.
- **Executable audit instructions:** `prompts/V52_TASK_4F1_EXECUTION_CANDIDATE_V4_INDEPENDENT_AUDIT_PROMPT_2026-09-01.md`.

Read those files in that order. Historical V1/V2 audit reports are evidence, not instructions to execute their candidates.

## Current decision state

| Item | State |
| --- | --- |
| Task 4F0 restricted cohort | Sealed: 1,712 questions across 96 archives |
| 4F1 V1 audit | Preserved, but unusable for sealing because of disclosed auditor-side outcome-capable execution |
| 4F1 V2 audit | `BLOCKED`; synthetic B1/B2/B3 integrity defects reproduced |
| 4F1 V3 candidate | `BLOCKED` by cold-start independent audit 2026-09-01: B1/B2/B3 repaired, but the pinned 100K::12 canary is not reproducible from the declared environment lock |
| 4F1 V4 candidate | Audit evidence accepted (9/9 implementation gates, `641568d8`), but **seal WITHDRAWN**: co-chair REQUEST CHANGES on blocking finding CC-01 |
| 4F1 V5 candidate | Required; must correct CC-01 and stale V3 text with the runner byte-identical to V4 |
| Task 4F1 preregistration / run | **Blocked** |
| Retrieval-quality outcome access | **Forbidden** |

The V3 audit blocked on Gate 3 (BLAS-dispatch-dependent float digests). V4 remediated that by binding sign codes plus a stability margin, and a separate cold-start auditor returned `PASS` on all nine implementation gates.

**That seal has since been withdrawn.** The co-chair review of 2026-09-02 returned `REQUEST CHANGES` on blocking finding **CC-01**: the bound `EXECUTION_SPEC.md` carries two mutually exclusive normative canary definitions — line 44 still demands the superseded V3 raw-float digests, while lines 110-112 demand the V4 sign-code digests. Only the latter is implemented and audited, and the former is unsatisfiable on conformant hardware. The Continuity Lead independently reproduced this and accepts it as its own authoring error: V4's spec was updated by a blanket label substitution plus an appended section, which never removed the superseded text. The audit's Gate 2 was scoped to runner source and AST, so no gate looked for contradictions across bound prose.

The V4 audit evidence remains valid for what it covered. The package is not sealed.

Next: a V5 candidate correcting CC-01 and the stale V3 text, with the execution runner byte-identical to the accepted V4 runner so the change set stays declarative, plus a V5 audit prompt carrying a mandatory cross-payload semantic-consistency gate. Scientific route is option B: freeze the outcome-free justification and the tier-stratified estimands before any preregistration. Task 4F1 stays BLOCKED for preregistration and run.

## Non-negotiable boundary

Do **not** invoke `--mode run` or `--mode finalize`. Do **not** call `run_archives`, `evaluate_archive`, or `finalize_results` on real BEAM data. Do **not** create a production authorization or set `V52_T4F1_AUTH_HMAC_KEY_HEX`. Do not open, calculate, print, infer, or compare real retrieval top-3 IDs, distances, metrics, or arm outcomes.

If any real retrieval-quality computation occurs, stop. Record only containment facts; do not interpret the outcome.

## Exact V4 objects to audit

- Candidate: `task4f1_execution_candidate_v4_2026_09_01/`
  - runner SHA256: `f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8`
  - payload inventory SHA256: `fe1de9c7160191f7a001ecadb928057411cc7b560a3f8f8a9130c6d3ceb1ba5e`
  - candidate seal SHA256: `1bf740f573fc74c6e8aa6e23a3f07a5bcc97a10d1fa7e6e7358560e1598f06e9`
- Implementer-side, outcome-free evidence: `task4f1_execution_candidate_v4_preflight_2026_09_01/`
  - evidence manifest SHA256: `4f78b5c8b184ad0ecfbbf444ffddbbcd076c6b78fa65c4b0d76696259f1c930f`
- Superseded but preserved: `task4f1_execution_candidate_v3_2026_09_01/`
  - runner SHA256: `0c1c1cc2bcf23296f0559daa98d936ed605fd7068ef376aa26bed69f6e66b07c`
  - BLOCKED audit: branch `audit/v52-t4f1-v3-independent-2026-09-01` at `a590f629`
- Triggering V2 blocked audit: `audit_v52_t4f1_execution_candidate_v2_independent_audit_2026_09_01/`
  - audit manifest SHA256: `9942a531647b95d3ded7ca069a13ca70f51ab51868ad6835321e59601ba05395`
- Sealed 4F0 restricted cohort: `audit_v52_t4f0_restricted_refreeze_2026_08_31/`
  - final seal SHA256: `596c8056342e75110a940ee838cb080e9cd830f269aca0d1d87a0c4d482f859c`
  - cohort SHA256: `9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a`

The V3 prompt enumerates mandatory gates, allowed synthetic fixtures, expected audit namespace, locked environment, and permitted verdict vocabulary. Follow it verbatim after independently verifying the listed hashes.

## Required external input

The 804 MB raw BEAM corpus is deliberately not in Git. Materialize it from `https://github.com/mohammadtavakoli78/BEAM`, pinned to commit `3e12035532eb85768f1a7cd779832b650c4b2ef9`, then verify it against the committed manifest before use. Do not substitute a newer checkout or repair its four excluded archives.

Use Python 3.12.13, NumPy 2.3.2, SciPy 1.16.1, scikit-learn 1.7.1, and psutil 7.0.0, with the five declared single-thread controls. Use `python -B` (or `PYTHONDONTWRITEBYTECODE=1`) so auditing does not add `__pycache__` files to a candidate namespace.

## Safe resumption procedure

1. Clone or fetch the explicit branch above; do not infer current state from GitHub's default branch.
2. Confirm a clean worktree and record `git rev-parse HEAD`.
3. Re-hash V3, its preflight package, V2 audit, and sealed 4F0 payload before executing any check.
4. Create only the audit namespace named by the V3 prompt. Do not modify any candidate, seal, manifest, or pinned corpus.
5. Run only outcome-free gates and synthetic tests permitted by the prompt.
6. Emit the required report, gate table, evidence, command log, and recursive hash manifest. Do not seal, preregister, or run Task 4F1.
7. Return the audit result to the Head Researcher for an explicit next decision.

## Completion condition for this handoff

A resuming LLM has completed the immediate task only when it has produced a fresh, independently hash-bound V3 audit package with either a clean `PASS — V3 EXECUTION CANDIDATE MAY BE SEALED BY HEAD RESEARCHER; TASK 4F1 STILL NOT PREREGISTERED OR AUTHORIZED` verdict or the prompt's `BLOCKED` verdict. Any other state remains incomplete.
