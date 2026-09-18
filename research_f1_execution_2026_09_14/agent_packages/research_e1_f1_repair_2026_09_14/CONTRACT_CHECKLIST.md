[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# F1 contract checklist — restated from the frozen bytes

Source: `origin/research/e1-v2-raw-cache-recovery-r2-2026-09-13:campaign_2026_09_13/e1_v2_raw_recovery_r2_2026_09_13/R2_COMPETITION_RERUN_CONTRACT.md`
(VERIFIED — read in full via `git show`, this session).
Design: `origin/research/e1-v2-raw-cache-recovery-r2-2026-09-13:campaign_2026_09_13/e1_mechanism/E1_PREANALYSIS_SPEC_V2.md`
(VERIFIED — read in full, this session).
Auditor F1: `origin/audit/e1-v2-raw-cache-recovery-independent-2026-09-13:audit_e1_v2_raw_cache_recovery_2026_09_13/FINDINGS.json`
(VERIFIED) + `INDEPENDENT_E1_V2_RAW_AUDIT_REPORT.md` (VERIFIED) + `EXECUTION_LOG.txt` (VERIFIED).
Auditor method: `.../competition_variants.py` (VERIFIED — read in full; consulted only AFTER my implementation was
specified from the contract text, for the comparison in `F1_EXECUTION_REPORT.md`).

## F1's exact statement (auditor, VERIFIED bytes)

- id `F1`, severity HIGH, status CONFIRMED. Title: "Claim D competition implementation violates frozen per-gold D2 convention".
- Lead behavior: "collapse all gold rows to dmin=min(distance[gold]) and count once".
- Required behavior: "compute strictly-closer/tie mass per gold and aggregate within query using D2 convention".
- Impact: "Lead competition coefficients are not licensed as frozen-V2 metric values. Qualitative positive direction
  survives corrected per-gold recomputation on all four benchmarks, but numerical Claim D must be regenerated."
- Row-mismatch scale (lead vs independent, VERIFIED from FINDINGS.json): LME strict 265 rows / max-abs 221.5;
  REALTALK 385 / 482.0; PerLTQA 2315 / 286.83; LoCoMo 425 / 272.5. Multi-gold rates: LME 0.6298, REALTALK 0.5475,
  PerLTQA 0.2809, LoCoMo 0.2814.

## Contract requirements (each box is independently executable)

- [ ] C1. Inputs are the three SHA-bound archives, verified BEFORE computation (contract pins):
  - `03_regen_caches.tar.gz` sha256 `a16bdf95...50f8aad` (full: `a16bdf95d3a96cb964fd6fd614d3b49d22bb9329c5afaf81cd692214d50f8aad`)
  - `04_bench3_runs_caches.tar.gz` sha256 `87d6312e...4219ae4` (full: `87d6312ef6c195ac6c161a8693ab635c447074c969f6573a0d0b0ca994219ae4`)
  - `07_drive_frozen.tar.gz` sha256 `370ea409...21a9f59` (full: `370ea40962b078fc2fc09ab5319942b242f1559adeb62765e271f90cc21a9f59`)
  - STATUS HERE: ABSENT (see `CACHE_INVENTORY.md`). No network. No fetch. → real-data boxes below are BLOCKED.
- [ ] C2. No refit, no evidence remapping, no new thresholds, no new benchmark filtering.
- [ ] C3. Headline gates reproduce to <=1e-12 BEFORE Claim-D computation:
  - LME SIGN `0.5419751773049645`, float `0.4415957446808511`
  - REALTALK SIGN `0.22477507598784194`, float `0.17253405381064954`
  - PerLTQA SIGN `0.488941994930817`, float `0.551692074528853`
  - LoCoMo SIGN `0.23654714666441054`, centered float (frozen-cache candidate) `0.16826334541318252`
  - STATUS HERE: gate-check function implemented + unit-tested (`verify_f1.py`); real-data application BLOCKED (no caches).
- [ ] C4. TOP64/BOT64 per archive: `v_j = mean_i(C_ij^2)`; STABLE DESCENDING sort of `v_j`; TOP64 = first 64 axes,
  BOT64 = last 64 axes. Binary code `C >= 0`, query code `qC >= 0`. Ordinary Hamming distances on the 64 axes.
- [ ] C5. CORRECT per-gold metric (the min-gold variant is FORBIDDEN): for every gold row `g` separately, per arm
  A in {TOP64, BOT64}: `strict_all(A,g) = count_i[d_A(i) < d_A(g)]`, `tie_all(A,g) = count_i[d_A(i) == d_A(g)]`
  (counts run over ALL rows `i`, including `g` itself — self contributes 0 to strict, 1 to tie, identically per arm).
  Aggregate INSIDE the query by ARITHMETIC MEAN over gold rows: `STRICT_A_q`, `TIE_A_q`.
  Primary gaps: `STRICT_GAP_q = STRICT_TOP64_q − STRICT_BOT64_q`; `TIE_GAP_q` likewise.
- [ ] C6. Mandatory sensitivity variant (reported separately, must NOT replace the primary after seeing outcomes):
  same but competitors exclude ALL gold rows (`strict_nongold`, `tie_nongold`, mean over golds, TOP−BOT gaps).
- [ ] C7. Summaries per benchmark (LME, REALTALK, PerLTQA, LoCoMo): average-rank Spearman `rho(Delta_q, STRICT_GAP_q)`
  and `rho(Delta_q, TIE_GAP_q)`; report n and multi-gold n/rate. PerLTQA additionally per section
  (dialogues/events/profile/social_relationship). Expected auditor targets at 1e-12 (CLAIM — rechecked byte-identical
  across FINDINGS.json / CORRECTED_RESULT.json / contract / EXECUTION_LOG.txt by `verify_f1.py`):
  LME 0.14168629605302735 / 0.14045379360271315; REALTALK 0.097939128891117 / 0.12281952421315011;
  PerLTQA 0.25416826537535475 / 0.2797878341571222; LoCoMo 0.09491957131277647 / 0.10376015063205302.
- [ ] C8. Descriptive bootstrap (R1 bootstrap SUPERSEDED, must not be reused): seed 96013, B=2000, resample at
  archive/conversation cluster level (LME one-query-per-archive reduces to query resampling), recompute average-rank
  Spearman per resample, percentile 2.5/97.5 intervals labeled descriptive/post-hoc. Record attempted/valid/invalid
  + reason for every invalid class. Never silently drop undefined replicates.
- [ ] C9. Persisted outputs: per-query `*.json.gz` rows; summary JSON; bootstrap JSON; input-SHA inventory; script SHA +
  manifest; corrected prose containing NONE of the R1 min-gold coefficients as current values.
- [ ] C10. Binding side-conditions: LoCoMo `+6.828380125122796 pp` exploratory wording only; `Q_EFF = 96/(1+Q_ABS_CV^2)`
  redundancy disclosed; average-rank Spearman frozen; "all 520 recovered archives" (never universal); no causal or
  deployable-router claims; Task4F1 untouched.

## What THIS execution delivers against the checklist

- C1: inventory + absence proof (`CACHE_INVENTORY.md`). Real-data rerun BLOCKED — stated, not worked around.
- C2: honored (no caches touched; synthetic fixtures only, clearly labeled).
- C3: gate function implemented + tested; real application BLOCKED.
- C4–C6: implemented from the SPEC text in `f1_competition.py`; proven against HAND-COMPUTED fixtures in `verify_f1.py`
  (oracle = arithmetic by hand, plus theorem: single-gold ⇒ per-gold ≡ min-gold). Min-gold bug ALSO implemented
  deliberately to demonstrate the correction (contract C5 forbids its USE as the metric, not its implementation as a
  bug-reproduction control).
- C7: Spearman + aggregation implemented; real-data targets NOT reproduced (BLOCKED); three-reference pin consistency
  machine-rechecked to full precision (`verify_f1.py`).
- C8: bootstrap implemented per spec; demonstrated on synthetic multi-cluster data (determinism + ledger); real-data
  intervals NOT generated (BLOCKED).
- C9: synthetic-schema analogues persisted under `evidence/` (explicitly NOT the contract's real payloads);
  script hashed at commit time in `REPORT.md`.
- C10: honored throughout; prose contains no R1 coefficient presented as current (R1 values appear ONLY in
  bug-demonstration tables labeled as superseded).
