[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# The sign-quantization advantage is implicit axis equalisation

**Status: VERIFIED by the coordinator, NOT yet independently audited.** This is the
single most consequential measurement produced in this session and it has had no
cold-start adversarial review. Treat accordingly.

## The question

The programme's headline is "a 12-byte binary code beats a 384-byte float vector by
+10 pp". That compares against ONE float baseline: cosine similarity on the centered
96-D vector. Centering, 96 dimensions and cosine are all project choices. If a cheap
variant of the FLOAT arm erases the advantage, the headline describes the baseline,
not quantization.

## The mechanism proposed and tested

Cosine similarity is an inner product, so axes with large magnitude dominate the
score: high-variance axes dominate the FLOAT ranking. Hamming distance on sign bits
treats every axis identically -- each contributes exactly 0 or 1 regardless of
magnitude. **Sign quantization is therefore an implicit UNIFORM axis re-weighting.**

If that is the operative difference, giving the float arm the same property (divide
each axis by its standard deviation = whitening) should reproduce the sign arm's
behaviour.

## Result (VERIFIED; control passed first on all four benchmarks)

Controls reproduce the frozen headlines to <=5e-7 pp before any new arm was trusted:
LME +10.053783, PerLTQA -6.274728, REALTALK +5.300077, LoCoMo +6.655046.

FR@3 by arm (all arms computed from the same cached vectors, no re-embedding):

| benchmark | sign (12 B) | cosine (384 B) | **whitened (384 B)** | softsign (384 B) | rank (384 B) |
|---|---|---|---|---|---|
| LongMemEval | 0.542134 | 0.441596 | **0.557447** | 0.568085 | 0.559043 |
| PerLTQA | 0.488945 | 0.551692 | **0.565755** | 0.562048 | 0.564193 |
| REALTALK | 0.225535 | 0.172534 | **0.229100** | 0.241829 | 0.232846 |
| LoCoMo | 0.237907 | 0.171356 | **0.262499** | 0.280045 | 0.280819 |

**Whitening accounts for the entire sign advantage, and slightly more:**

| benchmark | sign - cosine | whitened - cosine | share explained | 95% CI (whit-cos) |
|---|---|---|---|---|
| LongMemEval | +10.0538 | **+11.5851** | 115% | [+9.042, +14.362] |
| REALTALK | +5.3001 | **+5.6566** | 107% | [+3.157, +7.977] |
| LoCoMo | +6.6550 | **+9.1142** | 137% | [+7.445, +10.629] |
| PerLTQA | **-6.2747** | **+1.4063** | sign flips | [+0.756, +2.152] |

All four CIs exclude zero (paired, cluster-bootstrapped by archive, 2000 resamples;
queries within an archive are not independent, so clustering is required).

**PerLTQA's reversal dissolves.** The benchmark where sign LOSES by 6.27 pp is a
benchmark where whitening WINS by 1.41 pp. So the reversal is not "quantization is
bad on PerLTQA" -- it is that sign's crude, all-or-nothing equalisation is
insufficient there while proper equalisation works.

## What this does and does not license

**Whitened cosine vs sign, paired with cluster CIs:**

| benchmark | whitened - sign | 95% CI | significant? |
|---|---|---|---|
| PerLTQA | +7.6811 | [+6.829, +8.620] | YES |
| LoCoMo | +2.4592 | [+0.306, +4.411] | YES |
| LongMemEval | +1.5313 | [-1.172, +4.250] | no |
| REALTALK | +0.3565 | [-1.188, +2.205] | no |

Whitened cosine matches or beats the sign arm everywhere, but **strictly beats it on
only 2 of 4** benchmarks. On LongMemEval and REALTALK the 12-byte code is
statistically indistinguishable from the 384-byte whitened float.

**That is the defensible version of the programme's claim, and it is stronger than
the original one:** the honest headline is not "12 bytes beats 384 bytes" -- it is

> **A 12-byte code matches whitened 384-byte float retrieval on 2 of 4 benchmarks at
> 1/32 the storage, and the advantage it shows over *unwhitened* cosine is explained
> by implicit axis equalisation rather than by anything unique to binarisation.**

## Robustness

Sigma floors at 0, 1%, 5% and 10% of the mean sigma give **identical** results to six
decimals on all four benchmarks, so whitening is not exploiting near-zero variances.
Two independent alternative equalisers (softsign = cosine on tanh(C/sigma), and a
per-axis rank transform) behave the same way and both also beat plain cosine
everywhere -- the finding is not specific to one normalisation.

## Coordinator error in this run, disclosed

I added a "sign bits of the whitened vector" arm to ask whether whitening also helps
the 12-byte method. It returned exactly +0.0000 pp on all four benchmarks, and my
script reported that as a significant result. **It is a tautology, not a
measurement:** dividing a coordinate by a positive per-axis sigma cannot change its
sign bit, so sign(C/sigma) == sign(C) identically. Verified explicitly in
`research/whitening_2026_09_14/tautology_check.py`. The arm was vacuous by
construction and I should have seen it before running. The correct way to ask that
question is a LEARNED or non-positive per-axis transform, or thresholds other than
zero -- not a positive rescaling. That test has not been run.

This is the third coordinator error caught today (after the ERRATA mis-attribution
and the vacuous within-archive null on LongMemEval).

## Relation to the nine dead mechanism candidates

This is not a tenth per-query correlational rule -- it is an INTERVENTION: the
representation is changed and the metric re-measured, with archives, queries and gold
held fixed. It explains several standing facts at once:

- **the axis-budget curve**: at small m only the highest-variance axes are available,
  so uniform weighting has little to act on; the sign advantage grows as low-variance
  axes enter, exactly as the sweep shows;
- **the low-variance axis effect appearing in BOTH arms**: it is a property of how the
  axes carry signal, which is what this mechanism says;
- **the Haar-rotation collapse (-15.93 pp)**: a random rotation destroys the
  per-axis variance structure that equalisation acts on;
- **the PerLTQA reversal, including its direction**: crude equalisation under-performs
  proper equalisation where the high-variance axes are the informative ones.

It does not explain the within-PerLTQA section split (profile +20.36 vs events
-12.39 pp) and no attempt has been made here to make it do so.

## Required next steps

1. **Independent cold-start audit.** Nothing here has been adversarially reviewed.
2. The section-level test: does whitening also flip the profile/events split?
3. A non-vacuous cheap arm: whitening does not change sign bits, so a 12-byte method
   that captures equalisation needs a different device (learned thresholds, per-axis
   quantisation levels, or more bits on low-variance axes).
4. Storage accounting: whitened cosine remains 384 B/doc. This result explains the
   effect; it does not by itself produce a cheaper method.
