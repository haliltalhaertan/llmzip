# User-authorized bounded LoCoMo reproduction audit

2026-09-07. This is a receipt of the user's authorization, not a canonical state transition or a scientific acceptance.

The parent asked explicitly whether to launch a separate cold-start auditor to reproduce ONLY the sealed LoCoMo coordinate-scale experiment once, using the original frozen code and seed panel; the user replied **"evet"**. The described scope requires code, dataset hash and locked-environment verification before any fit/retrieval. This receipt binds that approval to the concrete package below. It does not claim to be a user cryptographic signature.

## Authorized scope

- Research snapshot `591e5d0fd7af8c265ac12a6176761475a19b2f02`; original trigger `680b10b8a3ef3dd55a5a05fe47f6fb5fa6d931d0`.
- Sealed LoCoMo runner `research/v52/locomo_coordinate_scale.py`; seal `research/v52/V52_COORDINATE_SCALE_PRERUN_SEAL_2026-09-05.json`, blob `52605626a403bc385cc6e1f0e3fe43970099d76c`.
- Original six arms, rotation seeds59001..59010, no changes to method, thresholds or tolerances.
- Python3.13; NumPy2.3.5, pandas2.2.3, SciPy1.17.0, scikit-learn1.8.0. No substitute environment for real computation. Verify pinned source data and correction bytes before fitting/ranking.
- One real reproduction invocation after passing gates. Independent comparison against persisted LoCoMo records; additional read-only comparisons and synthetic controls allowed. Failed gates mean BLOCKED before real computation. A failed real invocation is recorded, not silently retried.
- Cold-context subagent receives only scope and artifact pointers, not parent conclusions. Isolated worktree/branch `codex/v52-locomo-reproduction-audit-2026-09-07`; audit namespace `audit_v52_locomo_reproduction_2026_09_07/`.
- No raw corpus, virtual environment or secrets committed. Preserve frozen artifact bytes; results written separately. No GitHub Actions trigger, LongMemEval rerun, new bootstrap, additional rotations, new method, Task4F1/BEAM/HMAC, main or ledger changes.

Remote main remains `a0944522d122cfc3edb36b1d54bca3a1ade6661f` at this receipt; the separately commissioned coordinate-scale audit branch was absent from the readback. This receipt does not cancel that commission or claim its agent has stopped. Avoid duplicate live computations; the current audit is a separately identified one-time local reproduction authorized here.

The parent publishes this scope before approving the auditor's preflight readiness. No claim of completion is made by this document. Scientific acceptance remains separate from a successful numerical reproduction.
