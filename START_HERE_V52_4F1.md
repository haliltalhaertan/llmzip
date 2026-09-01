# Start Here — V52 Task 4F1 V3 independent-audit handoff

This is the single operational entry point for a new Head Researcher, Compute Expert, or independent auditor resuming the V52 BEAM work.

## Exact starting point

- **Repository state:** canonical branch `main`, at release tag `v52-4f1-v3-audit-handoff-2026-09-01-r2`; use that tagged commit or a descendant explicitly reviewed by the Head Researcher.
- **Current task:** independently audit the exact V3 execution candidate. This is code/integrity audit only; it is not a Task 4F1 preregistration, execution, or result-interpretation task.
- **Authoritative operational ledger:** `docs/RESEARCH_PROGRAM_STATUS_2026-08-31.md`.
- **Byte-preservation and provenance rules:** `CHAIN_OF_CUSTODY.md` and `DATASETS_AND_LARGE_ARTIFACTS.md`.
- **Executable audit instructions:** `prompts/V52_TASK_4F1_EXECUTION_CANDIDATE_V3_INDEPENDENT_AUDIT_PROMPT_2026-09-01.md`.

Read those files in that order. Historical V1/V2 audit reports are evidence, not instructions to execute their candidates.

## Current decision state

| Item | State |
| --- | --- |
| Task 4F0 restricted cohort | Sealed: 1,712 questions across 96 archives |
| 4F1 V1 audit | Preserved, but unusable for sealing because of disclosed auditor-side outcome-capable execution |
| 4F1 V2 audit | `BLOCKED`; synthetic B1/B2/B3 integrity defects reproduced |
| 4F1 V3 candidate | Prepared and preflighted; independent audit pending |
| Task 4F1 preregistration / run | **Blocked** |
| Retrieval-quality outcome access | **Forbidden** |

The only next technical action is a cold-start, outcome-free audit of V3. A passing audit may permit a later Head Researcher sealing decision; it does not authorize a preregistration or run.

## Non-negotiable boundary

Do **not** invoke `--mode run` or `--mode finalize`. Do **not** call `run_archives`, `evaluate_archive`, or `finalize_results` on real BEAM data. Do **not** create a production authorization or set `V52_T4F1_AUTH_HMAC_KEY_HEX`. Do not open, calculate, print, infer, or compare real retrieval top-3 IDs, distances, metrics, or arm outcomes.

If any real retrieval-quality computation occurs, stop. Record only containment facts; do not interpret the outcome.

## Exact V3 objects to audit

- Candidate: `task4f1_execution_candidate_v3_2026_09_01/`
  - runner SHA256: `0c1c1cc2bcf23296f0559daa98d936ed605fd7068ef376aa26bed69f6e66b07c`
  - payload inventory SHA256: `c7b53e55aff9206be8f70779bb781813e2c177120db1a4fb2826dde699df4199`
  - candidate seal SHA256: `9d35192ecc20fbe0a01254278857f656027b71e1f04947267c67e4d379a868de`
- Implementer-side, outcome-free evidence: `task4f1_execution_candidate_v3_preflight_2026_09_01/`
  - evidence manifest SHA256: `ccb0b815d5d8f251e136b8f4e8e2a04d6368f3cb5bab3d84fc467c206ccba2e9`
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
