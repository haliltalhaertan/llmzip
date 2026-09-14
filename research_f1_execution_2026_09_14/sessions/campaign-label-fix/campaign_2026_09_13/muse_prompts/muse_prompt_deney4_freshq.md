# Muse session — DENEY 4: fresh-Q confirmatory check of the mixing-disparity ordering

You are an independent analyst. Implement + run in /tmp/d4/; report [LOCAL EXPLORATORY]
[NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]. Read-only elsewhere; no network.

## Background (why)

The pilots found that MIXING coordinates with a random orthogonal block destroys retrieval, and
the damage is ordered by variance disparity of the paired coordinates (LoCoMo: MATCHED ≈ native
(0.23610 vs 0.23655), RANDPAIR −2.16 pp, ANTIMATCHED −4.31 pp; LME block-2 dose-response:
random pairing −3.48/−5.06/−2.32 pp vs matched-variance pairing −0.31/−1.95/−2.46 pp). A design
review (R2D) flagged a confound: the current construction derives the pairing from the SAME
variance ordering used to draw... the previous Q blocks (seeds 43001-43003) may interact with
the grouping choice; also the pairing perm is confounded with Q-to-axis assignment.

**This session: re-run the matched / antimatched / randpair contrast with FRESH Q blocks
(seeds 43004, 43005) — same construction logic — and check whether the ordering survives new
random draws.** This is a validity check, not a claim.

## Protocol sources (read these first)

- /mnt/c/Users/MDP/dev/llmzip-work/pilots/axis_attack_2026-09-12/round2/session_scripts/
  r2c_replicate.py — the frozen LoCoMo machinery: norm_evidence, load_audit_corrections,
  stable_archive_seed, topks_by_hamming, hspec/hspec_blocks_for_perm, retrieval_metrics,
  q_fractional, run_method, sign_dist. Mirror its LoCoMo evaluation EXACTLY (top-3, 20 nuisance
  trials, priorities stable_archive_seed(ci,t)+99, audit corrections, Cat1-4 valid 1535,
  fractional R@3, per-question mean over trials then mean over valid questions).
- LoCoMo frozen matrices: /mnt/c/Users/MDP/dev/llmzip-work/regen/locomo/locomo_<ci>.pkl
  (keys C (N x 96), QC (nQ x 96), qas, id_to_row). LoCoMo native anchor = 0.23654714666441054.
- LME side (secondary; if time permits): pilot REPORT.md E4 + round2/ROUND2_REPORT.md; the LME
  block-2 constructions live in pilots/axis_attack_2026-09-12/pilot_corrections.py and
  pilot_results_corrections.json (E4 matched/antimatched/random pairing numbers). Fresh Q
  blocks = new seeds (e.g. 44001/44002) applied to the SAME pairing-permutation scheme.

## Deliverables

1. LoCoMo, seeds 43004 + 43005: MATCHED, ANTIMATCHED, RANDPAIR block-2 arms, each recomputed
   with the fresh draws. Gate: native recompute = 0.23654714666441054 (<=1e-12) and, as
   replication-of-machinery check, re-derive the ORIGINAL seeds 43001-43003 values for one arm
   (MATCHED: 0.23565226250405402 / 0.23022749129263786 / 0.24242457144737273 — tolerance 1e-12)
   to prove your pipeline matches R2C before trusting fresh numbers.
2. Report per-seed values for the fresh draws + the strict-separation question: is
   min(MATCHED_fresh) > max(RANDPAIR_fresh) > ... and max(ANTIMATCHED_fresh) < min(RANDPAIR_fresh)?
   (state exactly what holds / fails; also compare against the ORIGINAL seed values).
3. Optional LME mirror with 2 fresh pairing/Q draws: same ordering question on the E4
   dose-response arms (matched less damage than random than antimatched).
4. /tmp/d4/d4_report.md + /tmp/d4/d4_details.json; print key numbers to stdout (BEGIN/END
   markers). Append nothing to /mnt/c. ~1-2 hours scale.
