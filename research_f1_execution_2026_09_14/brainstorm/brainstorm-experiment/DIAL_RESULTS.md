# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# DIAL_RESULTS.md — which dials flip Delta = FR@3(sign) − FR@3(cosine), in pp.
# All cells VERIFIED this session: 5 seeds × 400 queries × N=500 docs unless noted.
# Rule of thumb: per-cell sd across seeds ≈ 0.3–1.5pp; treat |Delta|<1pp as noise-adjacent.

## CONTROL (VERIFIED): control.py reproduces frozen LME SIGN=0.542134 FLOAT=0.441596 Delta=+10.053783.

## DIAL B — signal locus × spectrum (THE SIGN-FLIPPER; one dial moves Delta across zero)
alpha=0.5:  top16 −1.29±0.35 | mid16 −0.33±0.12 | bot16 +0.14±0.42 | rand16 −0.31±0.74 | broad −2.14±1.52
alpha=1.0:  top16 −1.23±0.43 | mid16 +0.41±0.77 | bot16 +1.21±0.70 | rand16 −0.26±0.68 | broad +0.56±1.02
alpha=2.0:  top16 −0.35±0.53 | mid16 +5.70±0.66 | bot16 +8.79±1.24 | rand16 +0.69±1.14 | broad +1.86±1.05
VERIFIED: moving ONLY the locus (top16→bot16) flips the sign at alpha=1.0 (gap 2.44pp,
pooled se≈0.37, significant) and alpha=2.0 (gap 9.14pp). The locus gap grows with alpha:
flat spectra (0.5) mute it, steep spectra amplify it. rand16 ≈ 0 throughout — a narrow signal
band must sit systematically high or low in the spectrum to matter. mid16 joins bot16 at
alpha=2 (+5.70): the bottom HALF of axes, not a freak 16, carries the effect when steep.

## DIAL A — spectrum alpha alone (modulator, weak flipper): locus=broad
0.0: −3.69±0.62 | 0.5: −2.14±1.52 | 1.0: +0.56±1.02 | 1.5: +1.56±1.17 | 2.0: +1.86±1.05 | 2.5: +2.26±1.33
VERIFIED: ~6pp swing, crosses zero near alpha≈0.7. Steeper spectra mildly favor sign even with
broadband signal (cosine increasingly distracted by top-axis noise). Small vs real ±5–12pp.

## DIAL C — coordinate shape (DOES NOT FLIP; kills tail-shape as sufficient cause here)
broad: gauss +0.56±1.02 | heavy +0.36±1.36 | skew −0.01±0.96
bot16: gauss +1.21±0.70 | heavy +0.89±0.83 | skew +0.71±0.84
VERIFIED: heavy tails and skew move Delta by <0.5pp. RELAYED context: real median excess
kurtosis is 0.93 (LME VERIFIED 0.98 this session) — and it is causally inert in this regime.

## DIAL D — archive size N (DOES NOT FLIP): 100: +1.61±1.85 | 400: −0.28±1.50 | 1500: −0.04±0.59 | 5000: +0.25±0.32
VERIFIED: no trend; note variance SHRINKS with N (sd 1.85→0.32). No evidence for an N-driven
reversal in 100–5000. The sealed 100K–10M scale remains untested (see MENU.md).

## DIAL E — golds per query (DOES NOT FLIP): 1: +0.56±1.02 | 2: −0.51±0.50 | 4: +0.10±0.30
VERIFIED: null. (Caveat: averaging gold rows is a crude multi-gold model.)

## DIAL F — query noise sigma (modulator, no flip): 0.5: +1.59±2.02 | 1.0: +0.56±1.02 | 2.0: −0.07±0.93
VERIFIED: cleaner queries mildly favor sign; no sign flip in 0.5–2.0.

## FOLLOW-UP cm_test.py — shared background on top-16 axes (KILLED as implemented)
gamma 0→3 at broad: +0.08→+0.43 | bot16: +1.19→+0.89 | top16: −1.29→−0.68. All shifts <0.7pp.
VERIFIED: common-mode background with fresh query loadings does not amplify Delta and does not
bend the budget curve (broad_g2 curve: m8=+0.30 … m96=+1.27, flat — real curve rises −12→+10).
Do not resurrect in this form.

## BUDGET-CURVE CHECK (dimension-matched, programme convention; VERIFIED gap)
Synthetic curves are flat (broad_a1: m8 −0.23 … m96 +1.17; bot16_a1 similar; top16_a2 similar).
The real rising curve (standing result A) is NOT reproduced — the generator is missing the
variable that makes real low-variance axes cumulatively valuable. Honest regime mismatch, L2.

## Bottom line
FLIP Delta: locus (top16↔bot16, sufficient cause, alpha-amplified); alpha (weakly, ~6pp).
DO NOT flip Delta: shape, N (100–5000), ngold, sigma, common-mode background as implemented.
MISSING: an amplifier (real ±5–12pp vs synthetic ±1–2pp at alpha≈0.9) and the budget-curve
mechanism. Candidates ranked in MENU.md.
