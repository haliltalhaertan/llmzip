[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# ATTACKS on the llmzip programme question (computed 2026-09-14)
Assertion labels: VERIFIED = computed this session (code: atk.py, se.py, se2.py, atk_rt.py).
CLAIM = programme document statement, not recomputed. RELAYED = second-hand.

## Controls (VERIFIED, exact reproduction of frozen headlines, FR@3 expectation accounting)
| bench | SIGN | FLOAT-cosine | Delta | programme frozen | match |
|---|---|---|---|---|---|
| LongMemEval (n=470) | 0.542134 | 0.441596 | +10.0538pp | +10.053783 | exact |
| PerLTQA (n=8265) | 0.488945 | 0.551692 | -6.2747pp | -6.274728 | exact |
| LoCoMo (n=1535) | 0.237907 | 0.171356 | +6.6550pp | +6.655046 | exact |
| REALTALK (n=705; 23 empty-gold queries skipped) | 0.225535 | 0.172534 | +5.3001pp | +5.300077 | exact |
All four controls reproduce to 4dp. The apparatus (Hamming on (C>=0), cosine on raw C,
E[FR@K] tie expectation) is correctly implemented. Attacks below strike the same apparatus.

## Attack 1 — IS THE FLOAT BASELINE WEAK? VERDICT: YES, fatally for the headline.
Cheap float variants computable from the same caches, same 384-byte storage, no gold/query
leakage (per-axis std uses the archive doc matrix only):
FR@3 (VERIFIED):
| bench | sign | cosine (published) | dot | euclid-raw | zcos (stdzd cosine) | spearman |
|---|---|---|---|---|---|---|
| LME | 0.5421 | 0.4416 | 0.4563 | 0.4401 | 0.5574 | 0.5505 |
| REALTALK | 0.2255 | 0.1725 | 0.1709 | 0.1733 | 0.2291 | 0.2153 |
| LoCoMo | 0.2379 | 0.1714 | 0.1633 | 0.1736 | 0.2625 | 0.2419 |
| PerLTQA | 0.4889 | 0.5517 | 0.5541 | 0.5461 | 0.5658 | 0.5689 |
Paired differences, pp with 95% CI (VERIFIED):
- Standardized cosine vs published cosine: LME +11.5851 [8.8761,14.2942]; RT +5.6566
  [3.6885,7.6248]; LoCoMo +9.1142 [7.4850,10.7435]; PerLTQA +1.4063 [0.7821,2.0306].
  The baseline loses to a no-extra-storage float fix on all four benchmarks, significantly.
- Sign vs standardized cosine (the fair 384-byte fight): LME -1.5313 [-4.2591,+1.1964]
  (float wins nominally, n.s.); RT -0.3565 [-2.3757,+1.6626] (n.s.); LoCoMo -2.4592
  [-3.9673,-0.9511] (float wins SIGNIFICANTLY); PerLTQA -7.6811 [-8.3892,-6.9730]
  (float wins overwhelmingly). Sign significantly beats the best cheap float on 0 of 4.
- Dot and raw-Euclidean (which preserve doc-norm information) do NOT beat cosine, so the
  baseline's weakness is specifically its sensitivity to per-axis variance scale, not norms.
Constructive note (interpretation of VERIFIED numbers): sign-thresholding gives every axis one
vote, i.e. it implicitly variance-equalizes; zcos does so explicitly and matches/beats it.
This reframes CLAIM facts (A)/(B): high-variance axes hurt raw cosine more than sign, and the
"quantization wins" story is largely a "variance-equalization wins" story achievable in float.
Uncentered-cosine variant could not be tested (VERIFIED: caches are pre-centered, means lost).

## Attack 2 — IS FR@3 LOAD-BEARING? VERDICT: sign of Delta survives; magnitude does not.
Delta SIGN-minus-cosine in pp at K (VERIFIED):
| K | LME | REALTALK | LoCoMo | PerLTQA |
|---|---|---|---|---|
| 1 | +5.28 | +0.67 | +3.50 | -6.03 |
| 2 | +7.33 | +4.01 | +5.99 | -6.10 |
| 3 | +10.05 | +5.30 | +6.66 | -6.27 |
| 5 | +10.01 | +6.48 | +7.93 | -6.49 |
| 10 | +6.93 | +6.67 | +8.76 | -9.05 |
| 20 | -1.71 | +5.59 | +6.22 | -12.08 |
- PerLTQA's reversal survives at every K and deepens with K. Not a K=3 artifact.
- The positive effect peaks near K=3-5 and on LME it VANISHES by K=20 (-1.71pp): the "+10pp"
  is the maximum over K, not a typical value. A reader told only FR@3 sees the effect's best
  angle. (RT K=1 is weak, +0.67pp: at K=1 the sign advantage nearly disappears there too.)

## Attack 3 — TIE-ACCOUNTING ARTIFACT? VERDICT: no; hedging is ~20% of the margin, real.
K=3 sign arm worst-case / expectation / best-case vs float expectation (VERIFIED):
| bench | worst | exp | best | band | float | worst-case Delta |
|---|---|---|---|---|---|---|
| LME | 0.5208 | 0.5421 | 0.5655 | 4.47pp | 0.4416 | +7.92pp |
| REALTALK | 0.2151 | 0.2255 | 0.2390 | 2.39pp | 0.1725 | +4.26pp |
| LoCoMo | 0.2229 | 0.2379 | 0.2549 | 3.20pp | 0.1714 | +5.15pp |
| PerLTQA | 0.4737 | 0.4889 | 0.5058 | 3.21pp | 0.5517 | -7.80pp |
Boundary-tie rates (fraction of queries with a tie at the K=3 cutoff, VERIFIED): LME 0.234,
PerLTQA 0.292, LoCoMo 0.345, REALTALK 0.355 (0.143/0.484/0.698/0.841 at K=1/5/10/20 on RT).
- Expectation-minus-worst (the maximum bookkeeping contribution): LME 2.13pp of 10.05 (~21%),
  RT 1.04 of 5.30 (~20%), LoCoMo 1.50 of 6.66 (~22%). ~80% of every positive Delta is real rank
  movement, present even under adversarial tie-breaking. Consistent with CLAIM fact (D): actively
  resolving ties by restoring query magnitude COSTS 3.56pp -- ties broken at random beat ties
  broken by a bad rule, but the expectation accounting itself is fair and conservative-ish.
- The attack fails: the effect is not tie bookkeeping.

## Attack 4 — IS "96 DIMENSIONS" THE REAL VARIABLE? VERDICT: yes, the headline is 96's artifact.
Numbers are CLAIM fact (A), not recomputed (single-cell check only: m=96 endpoint = controls above).
Dimension-matched Delta (pp): at m=8: LME -11.85, LoCoMo -2.29, RT -3.58, PerLTQA -16.40;
at m=32: -6.30/-4.16/-1.64/-11.70; at m=48: +0.29/-0.78/+0.87/-9.47; at m=64: LME +3.68,
LoCoMo +1.52, RT +1.90, PerLTQA -8.27; at m=96: +10.05/+6.66/+5.30/-6.27.
- Had the programme chosen 32-D, the honest headline would be "float wins on all four
  benchmarks"; at 64-D it would be "+3.7pp on LME". The "+10pp" is the value of a rising curve
  sampled at its (arbitrary) right endpoint; the curve is still rising at 96 on 3/4 benches, so
  128-D is extrapolative and no claim is made about it.
- Terminology correction stands (CLAIM): "dimension-matched" compares m BITS against m FLOAT32
  = 32m bits -- a 32:1 storage asymmetry in sign's disfavor, which makes Attack 1's result
  (float still wins when well-built) stronger, not weaker.

## Attack 5 — WHAT WOULD MAKE THIS USELESS IN PRACTICE? (analysis; labels per bullet)
- Scale (CLAIM fact G + arithmetic): no archive exceeds N=1548; target is 100K-10M. Hamming on
  96 bits takes 97 values: at N=10M each distance level holds ~100K docs, so top-3 by Hamming is
  a pure tie lottery and the expectation accounting of Attack 3 becomes the whole method. There
  is zero VERIFIED evidence at even 10x current scale.
- Deployment math: "12 bytes vs 384" omits the query-time embedder, the 96-float centering vector,
  and full-vector index build; at scale ties force a re-rank stage that needs the floats anyway.
- Query-dependence (CLAIM fact F): profile +20.36pp vs events -12.39pp on the SAME archives --
  a deployer cannot pick the method per query without an oracle for query type.
- Baseline dependence (VERIFIED Attack 1): best 384-byte float >= 12-byte sign on all 4 benches.
- Metric narrowness (VERIFIED Attack 2): LME advantage gone by K=20; RT advantage ~0 at K=1.
