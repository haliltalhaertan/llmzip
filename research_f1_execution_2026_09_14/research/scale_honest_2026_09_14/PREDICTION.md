[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# PREDICTION.md — frozen before step 3 (synthesis comparison) is run

**Written:** 2026-09-14, after step 1 (control) and step 2 (scope facts) completed, and
**BEFORE** any method-(c) code was written or executed. Not edited afterwards.

## What is already known at freeze time (VERIFIED, step 1 this session)

- CONTROL reproduced: LongMemEval FR@3 sign=0.5421335697399526, float=0.4415957446808511,
  Delta=+10.053783 pp (SE 1.6551, n=470). Matches the documented expectation-reproduction
  value +10.053783 pp. [locator: evidence/step1_control_scope.json:control_lme]
- Largest single real archive = **1548** documents (REALTALK). Grand total across all four
  families = 258,720 documents. [locator: evidence/step1_control_scope.json:scope]
- RELAYED from today's earlier session: POOLING raises the K=3 tie rate with N and makes the
  paired LME Delta decline (+10.05 -> +2.67 pp over N~493 -> ~24640); SUBSAMPLING lowers the
  tie rate with N and drives third-nearest distance down 11.8x faster per doubling.

## Predictions (the things that could be falsified by step 3)

**P1 — Method (c) will land between (a) and (b), not outside them.**
A correlation-preserving growth method (same-family, same-character/section pooling) should
produce a tie-rate-vs-N curve bracketed by the pooling curve (rising) and the subsampling
curve (falling). Confidence: MEDIUM. If (c) falls *outside* the bracket, my mental model that
"pooling and subsampling are the two extremes of a single axis" is wrong and the whole
diagnostic framing in step 4 is undermined.

**P2 — The sign of the Delta trend under (c) will be NEGATIVE but shallower than pooling.**
i.e. Delta still declines with N, but at less than half the pooling slope per doubling.
Confidence: LOW-MEDIUM. This is the prediction I most expect to be wrong.

**P3 — Third-nearest Hamming distance is the discriminating axis.**
Pooling drifts slowly (-0.244 bits/doubling), subsampling fast (-2.869 bits/doubling).
I predict method (c) gives an intermediate per-doubling slope, and that this slope is the
best single-number diagnostic for "which synthesis regime does this archive resemble".
Confidence: MEDIUM-HIGH.

**P4 — The four real families will DIFFER measurably on the diagnostic.**
Specifically I predict PerLTQA (the sign-REVERSED benchmark, Delta = -6.27 pp) sits at a
different point on the diagnostic axis than the three sign-positive families. If it does not,
the diagnostic has no explanatory traction. Confidence: LOW. This is a genuine coin-flip and
I am recording it so I cannot claim a hit after the fact.

**P5 — Any log-N linear fit extrapolated to 1M will have an interval so wide it is useless.**
I predict the 95% interval half-width at N=1e6 will exceed the magnitude of the extrapolated
Delta itself, i.e. the extrapolation will not even determine the SIGN at 1M.
Confidence: HIGH. If this is right, the honest deliverable is "unanswerable with these
archives", not a scaling law.

**P6 — The adversarial one.** The assumption most damaging to any conclusion I reach is:
*"the query distribution stays fixed as N grows."* In all three synthesis methods I hold the
470 LME queries fixed and only grow the archive. In a real 100K archive the queries would
also be more numerous and would target a different, larger gold set. I predict that if I
re-run pooling while also growing the gold set proportionally (gold scales with archive), the
Delta decline will SHRINK substantially — meaning most of the observed pooling decline is an
artefact of holding gold fixed while adding distractors. I will test this explicitly.
Confidence: MEDIUM-HIGH that it shrinks; if it does NOT shrink, pooling's decline is a real
distractor-density effect and deserves more weight than I am giving it.

## Pre-committed decision rule

If methods (a), (b), (c) disagree on the SIGN of d(Delta)/d(log N), I will report that the
question is **not answerable** with the archives owned, and will NOT fit or publish a scaling
law. I commit to this now so that a "nice-looking" fit later cannot tempt me.
