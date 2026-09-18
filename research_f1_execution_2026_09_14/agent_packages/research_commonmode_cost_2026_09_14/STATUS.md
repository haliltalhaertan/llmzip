[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# STATUS — common-mode cost attack (research_commonmode_cost_2026_09_14/)

PREPARED, NOT ACCEPTED. Task 4F1 SEAL in force: no `--mode run/finalize`, no
`run_archives`/`evaluate_archive`/`finalize_results` on real data, never set
`V52_T4F1_AUTH_HMAC_KEY_HEX`, never construct an authorization, never open BEAM
corpora/queries/labels/embeddings. E1 benchmark caches (LongMemEval, LoCoMo,
REALTALK, PerLTQA) on `origin/research/e1-*` MAY be read/computed on.

## Plan
1. STATUS.md (this file) — DONE.
2. Establish what float96 baseline IS: read `audit_v52_t4f0_codex_2026_08_31/audit_representation_transfer.py`, T4C2/T4C3 compute reports + methods, `adapters/`, projector package on `origin/findings/representation-geometry-2026-09-13`.
3. Decompose ~44MB into components; classify COMMON-MODE / SIGN-ONLY / FLOAT-ONLY / QUERY-TIME-ONLY.
4. Recompute comparison table (marginal / index-only effective / full-pipeline effective) at realistic N and break-even N.
5. Answer practical retrieval-footprint question; per-archive vs shared pipeline; cite preregistration prohibition.
6. Deliver COMMON_MODE_CLASSIFICATION.md, RECOMPUTED_COMPARISON.md, verify_commonmode.py + evidence/results.json, VERDICT.md, REPORT.md; commit namespace only.

## Receipts (append continuously)
- 2026-09-14 start: branch `muse/ultra-commonmode` based on main `5ec3db6`; namespace dir created.
- Evidence secured: T4C2 same-Y-same-mu lines (:257-287), adapter fit API + per-archive rule (:147,363-367), T4F0 fit_once (:96-144), E1 one-pair-two-views (e1_geometry_core :1,12), PREREG_DRAFT §2 (:71,79-81) + arm table (:135,150-152), L-088 (docs/CONTINUITY_LEDGER.md:1881), PROJECTOR_BYTES.json medians + per-archive components, 470-N geometry CSV.
- verify_commonmode.py: ALL 14 CHECKS PASSED (A1-A6 source, B1-B3 projector, C1-C2 cohort/panel, D1-D3 break-even/dominance). Fixed 3 own-checker bugs (header comment, f-string quote, annotation split, sharing-formula 470x→1x); corroborated global-share 202.93 = Attack 4 exactly.
- Delivered: COMMON_MODE_CLASSIFICATION.md, RECOMPUTED_COMPARISON.md, VERDICT.md (SPLIT: head-to-head COLLAPSES / absolute-footprint SURVIVES), verify_commonmode.py + evidence/results.json, REPORT.md.
- Seal record: no run/finalize modes, no archive evaluation fns, no HMAC key, no authorizations, no BEAM contact; no network/installs; stdlib python only; purely additive (5 new files + evidence); no checkout of other branches (all branch reads via `git show`).
