# Start Here — V52 Task 4F1 preregistration-decision handoff

This is the single operational entry point for a new Head Researcher, Compute Expert, or independent auditor resuming the V52 BEAM work.

## Exact starting point

- **Repository state:** canonical branch `main`. Tag pushes are refused by the current environment, so the pushed anchor is branch `state/v52-4f1-v3-audit-blocked-2026-09-01`; use the current `main` head or a descendant explicitly reviewed by the Head Researcher.
- **Current task:** Execution track only. The scientific preregistration is SEALED as of 2026-09-04; the science track is closed. The V6 audit is COMPLETE and returned BLOCKED; do not re-run it.
- **Authoritative operational ledger:** `docs/RESEARCH_PROGRAM_STATUS_2026-08-31.md`.
- **Byte-preservation and provenance rules:** `CHAIN_OF_CUSTODY.md` and `DATASETS_AND_LARGE_ARTIFACTS.md`.
- **Preregistration draft under review:** `docs/v52/task4f1/TASK4F1_PREREGISTRATION_DRAFT_2026-09-03.md`.
- **Audit prompts** under `prompts/` are historical records of completed audits, not pending work.

Read those files in that order. Historical V1/V2 audit reports are evidence, not instructions to execute their candidates.

## Current decision state

| Item | State |
| --- | --- |
| Task 4F0 restricted cohort | Sealed: 1,712 questions across 96 archives |
| 4F1 V1 audit | Preserved, but unusable for sealing because of disclosed auditor-side outcome-capable execution |
| 4F1 V2 audit | `BLOCKED`; synthetic B1/B2/B3 integrity defects reproduced |
| 4F1 V3 candidate | `BLOCKED` by cold-start independent audit 2026-09-01: B1/B2/B3 repaired, but the pinned 100K::12 canary is not reproducible from the declared environment lock |
| 4F1 V4 candidate | Audit evidence accepted (9/9 implementation gates, `641568d8`), but **seal WITHDRAWN**: co-chair REQUEST CHANGES on blocking finding CC-01 |
| 4F1 V5 candidate | `BLOCKED` by independent delta audit: the single-source gate did not establish its own claim |
| 4F1 V6 candidate | `BLOCKED` by independent delta audit 2026-09-03: 31 evasions succeeded against the inverted-burden gate |
| Packaging approach | Scanner strategy ABANDONED by Head Researcher decision. Close by removing restated values from bound documents |
| Preregistration draft | Written, outcome-free, under Head Researcher review; NOT approved for sealing |
| Task 4F1 scientific preregistration | **SEALED** 2026-09-04 (Seal V3; V1 and V2 blocked) |
| Task 4F1 run | **Blocked** |
| Retrieval-quality outcome access | **Forbidden** |

V3 blocked on BLAS-dispatch-dependent float digests. V4 fixed that and passed nine implementation gates, but the co-chair found CC-01: two mutually exclusive normative canary definitions in one bound file, so V4's seal was withdrawn. V5 corrected CC-01 and added a single-source gate — **BLOCKED**, the gate did not establish its own claim. V6 inverted the gate's burden — **BLOCKED**, 31 evasions succeeded, including ones that disarm the gate by editing its own configuration.

**The scanner strategy is abandoned by Head Researcher decision.** Two general contradiction-detectors were built and both were comprehensively defeated; a third is not authorized and must not be built. The packaging question is closed instead by **removing duplicated and restated normative values from bound documents** and reducing the package's claim to what is actually bound. This still blocks execution, but it no longer blocks preregistration design.

**The runner has been byte-identical and audit-confirmed since V4** (`f96cba2c`). B1, B2 and B3 were established repaired by the V4 audit, and nothing since has touched execution behaviour. Everything blocked since then has concerned documentation inside the candidate package, not execution correctness.

**The scientific preregistration is SEALED at Seal V3** (2026-09-04): `docs/v52/task4f1/TASK4F1_PREREGISTRATION_SEAL_V3_2026-09-04.json` (SHA256 `e906c6d2…`, with a `.sha256` sidecar). Verify with `python -B tools/verify_preregistration_seal.py`, and check the verifier itself with `python -B tools/test_verify_preregistration_seal.py` (22 negative controls). **Seal V1 (`c9e06195…`) and Seal V2 (`9ed480f4…`) are BLOCKED and superseded** — V1 carried hand-transcribed tier labels that dropped `500K` and invented a `5M` tier; V2 fixed that but still carried a hand-restated binding-8 implementation condition that no check read. Both are preserved byte-unchanged as historical artifacts and the verifier fails if either is edited; do not edit or delete them. V3 derives every value from bytes, including binding 8, which is extracted verbatim from the Head Researcher re-review artifact and bound by its own fragment digest. The seal binds the approved draft `5e618981…`, approved by the Head Researcher (`hr/rereview-t4f1-prereg-2026-09-04` @ `19d9cbb`) and by an independent exact-byte co-chair (`cochair/exact-byte-approval-t4f1-prereg-2026-09-04` @ `5299cc1`). **Sealing is not a run authorization.** Run stays BLOCKED, no production authorization exists, outcome access stays FORBIDDEN. Any scientific-content change needs both approvals again. The remaining blocker is the execution track: the V7 package audit, plus the pre-run exact-rational `D_t` sign-classification condition.

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

**Stale as written — the V3 audit closed long ago and the science track is now sealed.** The current completion condition is on the **execution track only**: the V7 execution-package audit must return an independently hash-bound verdict, and the pre-run exact-rational `D_t` sign-classification condition must be discharged, before any run authorization may even be considered. Sealing the preregistration completed the science track and authorized nothing else. Do not seal again, do not authorize, do not run or finalize, and do not access outcomes.
