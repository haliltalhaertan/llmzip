# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# NEXT_BRIEF.md — the one-hour experiment (self-contained brief for another session).

## Goal
Settle causally where discriminative signal lives per corpus by INTERVENING on the real caches:
restrict BOTH arms to top-16-only vs bot-16-only variance axes and compare Delta(band). A
synthetic pilot (this session, synth.py) VERIFIED that moving signal locus top16→bot16 flips
Delta sign (−1.23→+1.21pp at alpha=1, −0.35→+8.79pp at alpha=2); calibration (calibrate.py)
showed PerLTQA-profile (Delta +20.36) reads bottom-loaded (rho_norm −0.314) while events
(Delta −12.39) reads top-loaded (+0.596) on IDENTICAL archives. This experiment tests whether
that pattern is causal.

## Controls first (do not skip)
Reproduce the frozen LongMemEval headline with the exact tie expectation
E[FR@3]=(g_strict+g_tied*slots/bc)/|gold|: SIGN=0.542134 FLOAT=0.441596 Delta=+10.053783.
Reference implementation: control.py in this folder. Cached C is PRE-CENTERED — do not re-center.
Sign arm = Hamming((C>=0),(qC>=0)); float arm = cosine on raw C. FR@3 is FRACTIONAL recall.

## Data (READ-ONLY; never write under /mnt/c; write outputs to $HOME/muse-work/band-test/)
- LME: /mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/*.pkl (470: question_id,C,qC,gold)
- PerLTQA archives: .../bench3/runs/b3b_perltqa/cache_arch_eval.pkl; queries+sections: cache_q_eval.pkl
- REALTALK: .../bench3/runs/b3a_realtalk/rt_repr/RT*.pkl (C,QC,qids,gold_rows; SKIP the 23/728
  queries with empty gold_rows — they produce NaNs)
- LoCoMo: .../regen/locomo/locomo_*.pkl (C,QC,qas[].raw_evidence via id_to_row; skip unmapped)

## Procedure (30–40 min)
1. Per archive, rank axes by mean_i(C_ij^2) descending (equals variance; C pre-centered).
2. For band in {top16, bot16}: restrict docs AND queries to that band, run both arms, FR@3,
   Delta(band) = sign − float in pp. Also record full-96 Delta as reference.
3. Aggregate: 4 benchmarks + 4 PerLTQA sections (profile/social/dialogues/events); report
   Delta(top16), Delta(bot16), and their difference with seed-free exactness (deterministic —
   no error bars needed; the statistic is exact given the caches).
4. If time remains: k-ablation (zero-out top-8/top-16, re-measure full-96 Delta) on LME + PerLTQA
   events/profile (~15 min).

## Reading the result (preregister these kill criteria)
- PREDICTION (locus hypothesis): Delta(bot16) − Delta(top16) > 0 on ALL benchmarks/sections,
  largest on LME and PerLTQA-profile, smallest-or-negative on events.
- KILL: if Delta(bot16) ≤ Delta(top16) on LME or on profile, the locus hypothesis is dead as a
  sufficient cause — report it dead and run MENU.md item 1 (correlated-covariance amplifier hunt).
- PARTIAL: if the band gap is positive but small (<3pp) while full-96 Deltas are ±10–20pp, the
  locus is real but not the amplifier — same next step.
- Do NOT compute any per-query correlational statistic. Do NOT fit thresholds. Band-level
  aggregates only.
