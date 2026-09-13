# Muse session — R2D: ADVERSARIAL DESIGN REVIEW of round-2 outputs

Fresh adversarial reviewer. Read-only; scratch /tmp/r2d/. No network. Do not read /tmp/r2a|r2b|r2c.

## Read

- `pilots/axis_attack_2026-09-12/round2/r2a_flip_analysis.md`, `r2b_learned_selection.md`,
  `r2c_loco_replication.md` (under /mnt/c/Users/MDP/dev/llmzip-work)
- their `wsl_details/*.json`
- context: `pilots/axis_attack_2026-09-12/REPORT.md` (round-1 pilot) and
  `review_transfer/EXTERNAL_LLM_REVIEW_AXIS_PILOT_2026-09-12/01_CANONICAL_STATUS.md` (round-1 status)
- frozen protocol sources: `drive/v52_t4c3_coordinate_axis_probe.py`,
  `drive/v52_t4d_locomo_frozen_cross_benchmark.py`

## Questions (each: FINDING / OK / CAVEAT with evidence)

1. **R2B design hygiene.** The drop/delta/alone utilities are computed on TRAIN questions only and
   evaluated on TEST — verify no test information enters selection (read the described procedure;
   spot-check against `r2b_details.json` if it exposes the utilities/columns). Also: is the
   sha256-parity split defensible? Any cross-half contamination via per-axis matrices
   (`per_axis_matrices.npz` is per-question, so train-only aggregation is possible — confirm the
   reported utilities could only come from train)? Flag the overfit gap reporting (present?).
2. **R2B statistical claims.** drop64 test 0.4838 vs random seeds {0.4342, 0.4676, 0.4477} — is
   "+3.39pp vs mean" the right headline, or should it be "beats best seed by +1.6pp"? Check the
   claim language against seed dispersion; also check the honest disclosure of SPREAD64≡SPREAD48.
3. **R2C protocol fidelity.** The gate reproduced exactly (0.23654714666441054, diff 0.0) — strong.
   Now check the ARM implementations against the T4D script: were the block-2 constructions
   (matched/antimatched) built with the same rng draw order and QR+sign-fix as the script? Were the
   budget arms' variance rankings per-conversation (archive-local)? Any deviation = finding.
4. **R2A mechanism claims.** "The discriminative signal lived in low-variance axes (for the
   decisive subset)" — is that supported by the provided data (losers/winners stats, correlations)?
   Which claims are descriptive vs causal; flag any causal overreach. Also check the W/T/L baseline
   caveat (vs RAND48_s0 single seed vs vs 3-seed mean — consistent reporting?).
5. **Cross-document consistency.** Numbers in the three md files vs `wsl_details/*.json` vs each
   other (e.g. R2A overall W/T/L in md vs json; R2B test FRs in md vs json). List any mismatch.
6. **Label/limits hygiene.** All three outputs must carry exploratory labels and state limits
   (single benchmark per finding, seed dispersion, no causal claims). Check for missing labels,
   missing limits, or any citation-ready overclaim.
7. **Free hunt** (anything misleading/unsupported) + "what cannot be checked from these files".

## Report format

FINDINGS table (ID / area / verdict / evidence), then "Required corrections" (may be empty),
then "Before any preregistration" carry-over list. Read-only; no /mnt/c writes; no network.
