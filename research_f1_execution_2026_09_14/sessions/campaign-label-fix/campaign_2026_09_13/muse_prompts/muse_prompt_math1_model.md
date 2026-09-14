# Muse session — MATH-1: analytic model of top-3 sign-code retrieval + validation on frozen data

You are a mathematical modeler. Build an ANALYTIC (probability-theoretic) model of the frozen
retrieval protocol, derive closed/DP-computable expressions, and VALIDATE the model against the
frozen data. Read-only /mnt/c; write only /tmp/math1/. No network (flag LIT-CHECK items).
Label all output [LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION].

## The protocol (frozen, verbatim)

Docs and query have 96-bit sign codes (C>=0, qC>=0). Distance = Hamming. Top-3 by distance;
ties broken by a per-question seeded random priority permutation (20 nuisance trials, mean =
fractional evidence recall over trials; gold rows per question). Aggregate = mean over questions.
Anchors: LME 470 q (0.5419751773049645), LoCoMo 1535 q (0.23654714666441054). Full detail:
/mnt/c/Users/MDP/dev/llmzip-work/review_transfer/EXTERNAL_LLM_REVIEW_AXIS_PILOT_ED3_2026-09-13/
protocol_sources/ + round3_sources/harness/deney1_lme.py.

## Phenomena the model must explain (measured, frozen)

1. Budget curve: FR vs subset size b for spread/random selections (LME: 10B≈−2.7pp, 8B≈−5.9,
   6B≈−9.2 vs native); near-linear-ish degradation.
2. **TOP48 collapse**: top-variance subset wins EVERY mean-distance statistic yet loses FR by
   ~10pp vs RAND48 (mean gold distance 13.4 vs 14.4!). Tie-mass at the gold distance is the
   empirical mediator (strictly-closer-than-gold 0.55 vs 5.51 between wins/losses).
3. Mixing dose-response: block-2 pairing with variance-matched pairs ≈ native (LoCoMo −0.04pp),
   antimatched −4.3pp, random −2.2pp.

## Deliverable

1. **Model.** Given, for one question: N docs; a gold set; the distribution of non-gold distances
   (histogram) and gold distance(s); and random tie-breaking — derive the exact probability that
   a gold doc lands in top-3 (fractional-R@3 expectation). Give an exact combinatorial/DP formula
   (handle ties + multiple golds; the 20-trial tie scheme = conditional-uniform tie resolution).
   State ALL independence assumptions explicitly and which are suspect for sign codes
   (bits correlated; distances not independent across docs — say what this costs).
2. **Validation on frozen data (LME-470).** For a panel of arms — NATIVE96, SPREAD48, TOP48,
   RAND48 (seed 12000), BOT48 — compute per question: input histograms from the frozen pkls,
   model-predicted FR, measured FR (recompute with the frozen tie scheme). Report per-arm:
   mean predicted vs measured, per-question correlation, MAE; and crucially: **does the model
   reproduce the TOP48 collapse from distance-profile inputs alone?** If not, quantify the misfit
   and where it lives (which questions/regimes).
3. **Second-order test (if time).** The variance-disparity dose-response is about CORRELATED bit
   flips within pairs — derive what pairing structure does to the non-gold distance histogram
   width, and check qualitatively against the measured matched/anti gaps.
4. **Verdict + limits.** What the model does/doesn't explain; what assumption is the most likely
   culprit for misfits; what data would discriminate.

Deliverables: /tmp/math1/math1_report.md + math1_details.json + math1.py. Print MATH1_VERDICT:
one line. ~2-3 hours scale.
