# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# PREDICTION (FROZEN — written before running the whitening sweep; never edit)

## Intervention

Weighted-cosine arm: for per-archive scales `s_j^2 = v_j = mean_i C_ij^2`,
transform `C'_ij = C_ij / s_j^alpha`, `q'_j = q_j / s_j^alpha`, score = cosine
in transformed space = `sum_j w_j C_ij q_j / sqrt(sum_j w_j C_ij^2
sum_j w_j q_j^2)` with `w_j = v_j^{-alpha}`. Sweep `alpha` in
{0, 0.5, 1.0, 1.5, 2.0}. `alpha=0` = ordinary cosine (must reproduce the
FLOAT headline within 1e-9). `alpha=1` = task-spec "uniform" (w=1/sigma in
score form). `alpha=2` = full whitening (cosine on z-scored axes). Epsilon
floor `1e-12` on `v_j`; same FR@3 exact-tie-expectation metric; all 96 axes
kept (no axis dropping — weighting only).

## Frozen predictions (H-W framing)

- P1 (direction): on LongMemEval, LoCoMo, REALTALK (sign WINS), FR(alpha)
  RISES monotonically with alpha, i.e. the sign advantage
  `D(alpha) = FR_sign - FR_weighted(alpha)` SHRINKS toward zero as alpha
  goes 0 -> 2.
- P2 (reversed benchmark): on PerLTQA overall (sign LOSES), FR(alpha) FALLS
  or stays flat with alpha — whitening moves the float arm the WRONG way
  there, because H-W says PerLTQA's support already sits in high-variance
  axes that whitening down-weights. So `D(alpha)` goes MORE negative
  (sign loses by more).
- P3 (sections): the alpha-slope splits PerLTQA sections: profile (sign
  wins +20.36 pp) rises with alpha like LME; events (sign loses -12.39 pp)
  falls with alpha. social/dialogues near-flat or weakly falling.
- P4 (spectral quantity): R = mean_q Pearson(log v, s) satisfies
  R_LME, R_LoCoMo, R_REALTALK < R_PerLTQA, and within PerLTQA
  R_profile < R_social, R_dialogues < R_events with profile-events CIs
  disjoint. (This is F1/F2 of FORMALISATION.md, restated as prediction.)
- P5 (strong/explanatory bar): if at alpha=2, |D(alpha)| <= 1.5 pp on all
  four benchmarks (whitened cosine statistically ties or beats sign
  everywhere), H-W is AFFIRMED as the full mechanism: sign = implicit
  whitening, mechanism question ANSWERED (modulo storage honesty below).
- P6 (kill bar): if FR(alpha) is FLAT (range < 1 pp) on LME, or moves the
  WRONG direction (falls on LME / rises on PerLTQA-events), or P4 fails to
  separate profile from events, H-W is DEAD — report the kill plainly.

## Non-prediction (scope guard)

Whitened cosine costs the full 384 bytes (plus 384 bytes of per-archive
scales amortised). Whatever the outcome, this explains the effect; it does
not produce a cheap method. No storage claim is made.

## Control gate (must pass or nothing else is interpretable)

alpha=0 reproduces FLOAT headlines; sign arm reproduces SIGN headlines:
LME 0.542134/0.441596 (delta +10.053783), PerLTQA -6.274728 delta,
REALTALK +5.300077 delta. VERIFIED for LME pre-freeze (ctl.py); all four
re-checked inside weighting.py run.
