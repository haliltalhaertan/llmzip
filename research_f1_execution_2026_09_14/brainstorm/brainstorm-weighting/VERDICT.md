# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# VERDICT: framing ALIVE — as a causal mechanism, not as an observational quantity

## Frozen-prediction scoreboard (from PREDICTION.md, unedited)

- P1 (FR rises with alpha on LME/LoCoMo/REALTALK): PASS, strongly.
  Monotone rises: LME +14.8 pp, LoCoMo +15.0 pp, RT +8.3 pp, 0 -> 2.
- P2 (PerLTQA FR falls/flat; D more negative): MIXED. Net fall 0.5517 ->
  0.4976 as predicted, but non-monotone (peak 0.5708 at a0.5) and D goes
  LESS negative (-6.27 -> -0.86), opposite to the frozen letter. The deeper
  claim (whitening moves float toward sign) holds; the frozen D-sign
  reasoning was muddled. Scored as P2-literal FAIL, P2-spirit PASS.
- P3 (section alpha-slope split): PASS. profile rises +25.2 pp monotone and
  crosses sign; events net -10.9 pp; social/dialogues intermediate and
  near-flat. The 33 pp profile/events flip is reproduced causally by one
  knob. Caveat: universal a0.5 bump in all 8 rows (mild whitening helps
  even events, +2.0 pp).
- P4 (R ordering: 3 sign-win < PerLTQA; profile < ... < events, CIs
  disjoint): HALF-PASS. Section extremes PASS (profile 0.181 < events 0.396,
  CIs far disjoint; F1 satisfied). Benchmark F2 FAILS: LME 0.3630 +/- 0.0108
  sits ABOVE PerLTQA 0.3398 +/- 0.0031 with disjoint CIs — the flagship
  sign-win benchmark has the most high-variance support by this measure.
  Middle sections also swap (social 0.379 > dialogues 0.258).
- P5 (whitened ties sign, |D| <= 1.5 pp everywhere): tie-bar FAILS, beats-bar
  PASSES. At a2.0 whitened cosine BEATS sign on all four benchmarks
  (LME -4.73, LoCoMo -8.39, RT -3.01, PerLTQA -0.86, all in whitened's
  favour). The frozen tie-bar contradicts its own beats-bar; the result
  satisfies "matches or beats the sign arm everywhere" literally.
- P6 (kill bar: flat/wrong-direction sweep): NOT TRIGGERED. LME range 14.8
  pp in the predicted direction.
- F1 (profile vs events separation): PASS for R extremes; PASS decisively
  for the alpha-slope. F2 (benchmark order): FAIL for R. F3 (whitening moves
  float toward sign): PASS on all four benchmarks plus sections.

## What the numbers mean (VERIFIED claims only)

1. The sign arm's advantage is implicit whitening — directionally proven by
   intervention, not correlation. Turning the explicit whitening knob moves
   the float arm onto and past the sign arm on every benchmark where sign
   wins, reproduces the profile/events split from shared documents, and
   closes 86% of the PerLTQA gap from above. This is the programme's first
   mechanism to survive a same-day interventional test across all four
   benchmarks AND the section split.
2. It OVERSHOOTS: full whitening beats sign by 3-8 pp on sign-win benches.
   Sign is therefore a LOSSY 12-byte approximation of whitening, not the
   full effect. Fraction of the float->whitened gain captured by sign
   (derived from verified FR values): LME 68%, REALTALK 64%, LoCoMo 44%,
   PerLTQA 86% convergence from above. The residual (quantization coarseness?
   tie-conservatism per fact D?) is a new open sub-question, not a refutation.
3. The frozen observational quantity R is WOUNDED and demoted: it separates
   profile from events but misorders LME, and post-hoc analysis shows it
   tracks query-gold alignment strength (LME 0.707/events 0.697 vs profile
   0.301), i.e. it confounds strength with location. The whitened variant
   Q-WHITE does not repair ordering (dialogues highest). Per the programme's
   failure pattern, another correlational patch is unwarranted. The durable
   transferable measure of "where the signal sits" is the INTERVENTIONAL
   alpha-slope itself (positive slope = low-variance signal), which orders
   all 8 groups correctly.
4. Storage honesty (per frozen scope guard): whitened cosine costs full
   384 B/doc plus amortised per-archive scales. This result EXPLAINS the
   12-byte effect; it does not compress anything. A cheap method would need
   the whitening gain in ~12 bytes — sign itself, capturing 44-86% of it,
   remains the practical artefact.

## Verdict

H-W framing: ALIVE, promoted from hypothesis to intervention-confirmed
mechanism-direction; frozen observational formalisation (raw R) PARTLY
FALSIFIED at benchmark level (LME) and superseded by the alpha-slope.
Recommended next step (not taken here): preregister the alpha-slope
ordering on a held-out benchmark BEFORE running it, since this pilot fitted
its slope reading on the same four benchmarks.
