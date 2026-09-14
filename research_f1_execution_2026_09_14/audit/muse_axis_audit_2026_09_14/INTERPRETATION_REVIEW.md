# INTERPRETATION_REVIEW.md — Step 5: attacking the conclusions, not the code

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

All numbers below are VERIFIED (locator: interp.py tests S1–S7 + evidence JSON dump;
S6 recomputed with my own code). The Step-2/3 numbers stand; what falls is what the
numbers are claimed to MEAN.

## I-1. "All four share a curve shape" — GENEROUS, partly FALSE (major)

- Their coord_readout.py docstring asserts "Delta is monotone increasing in m on all
  four". VERIFIED FALSE on 2/4: LoCoMo dips m8→m12 (−1.43 pp, ~2σ given SE≈0.5–0.7)
  and m24→m32 (−0.41); REALTALK dips m8→m12 (−1.20) and is flat m12→m16 (−0.02).
  Their own code would print monotone=False for both. The docstring overclaims what
  the readout computes.
- Pairwise correlations of the 9-point Delta curves are high (0.82–0.98), so
  "correlated rising curves" is fair. But total rise 8→96: LME +21.9 pp vs LoCoMo
  +8.9 / REALTALK +8.9 / PerLTQA +10.1 — LME's gain rate is ~2.4x the others.
  "Same shape" papers over a 2x slope difference and two non-monotone curves.
- Strongest genuine shared feature (unremarked): the largest single jump on ALL FOUR
  curves is 32→48 (LME +6.59, LoCoMo +3.39, RT +2.51, PLTQA +2.23). If a shared
  mechanism exists, it lives there — not in the crossover framing.
- "PerLTQA is not a different phenomenon, its crossover just sits beyond budget":
  with correlations 0.82–0.96 this is a defensible READING, but it is one reading —
  PerLTQA is also the only curve that never crosses, has the most negative level at
  every m, and the flattest late slope. The data do not compel the single-phenomenon
  story over "three crossers + one non-crosser".

## I-2. PerLTQA extrapolation "near m=243" — UNSTABLE (major)

Linear-implied crossover by fitting window (VERIFIED): 80..96 → 243; 64..96 → 195;
48..96 → 186; all nine points → 153. Spread: 90 axes (1.6x–2.5x the 96 budget).
The reported 243 uses the shallowest last-segment slope and is the LARGEST of the
four standard choices — window-picked, whether or not intentionally. Worse, the
increments (…, +1.31, +0.68) show diminishing gains (concave curve); linear
extrapolation of a concave curve is misspecified, and under concavity the true
crossing — if the trend continues at all — lies FARTHER out than any linear guess.
Credit: coord_readout.py flags the extrapolation as beyond-range. But CLAIM 1's
"its crossover just sits beyond the available budget" inherits none of that caution
and no uncertainty band. Honest form: "linear extrapolation gives 150–250+ depending
on window, under a linearity assumption the data already violate; effectively
unidentified."

## I-3. CLAIM 2 is confounded with an axis effect — the float arm shows it MORE (kill)

BOT-vs-TOP sign contrasts (VERIFIED from their evidence): the FLOAT arm's
float_bot − float_top has the same sign as the sign arm's bot − top almost
everywhere, with LARGER magnitude — LME m48: float +21.88 pp vs sign +7.75;
LoCoMo m48: +15.46 vs +4.81; REALTALK m48: +9.00 vs +0.18; PerLTQA m48: −8.56 vs
−12.73 (same sign). The single exception is REALTALK at m24/m32, where the arms
disagree in sign — the only place the two arms genuinely diverge on this contrast.
So "low-variance axes retrieve better (on LME/LoCoMo)" is an AXES phenomenon both
retrieval modes agree on — if anything a float-arm phenomenon — not evidence about
where or why SIGN wins. CLAIM 2's framing ("counter-intuitive… where sign wins")
misattributes a shared axis effect to the sign arm.

## I-4. The "4/4 alignment" mixes measurement budgets (kill)

The reported 4/4 match compares (bot − top) at m=48 against Delta at m=96 — a
cross-m comparison the text never justifies. Same-m alignment (VERIFIED, test S5
table: LME 8:Y 12:Y 16:n 24:n 32:n 48:Y 64:Y 80:Y 96:n; LoCoMo 8:n 12:Y 16:n 24:n
32:n 48:n 64:Y 80:Y 96:n): LME mismatches at 16/24/32, LoCoMo at 8/16/24/32/48,
e.g. LoCoMo m48 bot−top = +4.81 pp while Delta48 = −0.78 pp (opposite signs!). At m=96 the comparison is degenerate
(bot−top = 0 exactly vs Delta ≠ 0; PerLTQA "aligns" only vacuously since neither
0>0 nor Delta>0). The alignment exists for one (m-selection, Delta-selection)
pair, not as a general correspondence.

## I-5. The m→96 trend IS partly mechanical — but the per-axis effect is REAL (mixed)

- Mechanical part (VERIFIED, test S6): overlap dilution. At m=64/80 the TOP and BOT
  sets share 32/64 axes (Step 3b). Overlap-free exclusive contrasts are much larger:
  PerLTQA m80 bot16−top16 = −16.74 pp vs overlapping −6.90; LME m64 bot32−top32 =
  +8.10 vs +6.81. The observed decline of |bot−top| toward 0 is therefore largely
  dilution + the m=96 identity (both = same 96 axes ⇒ 0 by construction), not a
  retrieval phenomenon. Any trend-reading that ignores overlap is void.
- Real part: the exclusive (overlap-free) contrasts keep the CLAIM-2 sign on both
  benchmarks (LME +8.10/+1.14, PerLTQA −16.39/−16.74 at m=64/80). The "purely
  mechanical" counter-hypothesis FAILS — a per-axis variance effect survives with
  no shared axes. (I-3 stands regardless: the surviving effect is shared by both
  arms.)

## I-6. The random referee undercuts the prescription (major qualifier)

Reported orderings check out (VERIFIED): LME m48 rand (44.70) > bot (42.96) > top
(35.21); PerLTQA m48 top (41.88) > rand (37.20) > bot (29.15). Consequence the text
omits: on LME, mixed-variance (random) axes beat low-variance-only axes — so
"low-variance axes retrieve better" is false as a selection rule; BOT beats TOP yet
loses to RAND. At most: high-variance axes contribute less per axis to the sign arm
on LME/LoCoMo, while full-96 (all axes) still wins overall (LME sign 54.2 > rand-48
44.7). No axis-selection recommendation follows from CLAIM 2.
