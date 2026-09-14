# VERDICT.md — audit opinion (only)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## Verdict: REQUEST_CHANGES

I may not approve, close, seal or ratify anything; this is an opinion only. The
numbers are verified correct, but both claimed INTERPRETATIONS need revision before
they can be relied on. "Request changes" targets the conclusions and labelling, not
a recomputation — every table cell I tested reproduces.

## Why not PASS

1. CLAIM 1's "same curve shape" overclaims: strict monotonicity fails on LoCoMo and
   REALTALK (their own readout code would print False; its docstring says True),
   and LME's gain rate (~21.9 pp) is ~2.4x the others (~9 pp). Correlated rise, yes;
   same shape, no. (INTERPRETATION_REVIEW.md I-1)
2. Crossover precision 47.3/42.5/53.4 is indefensible: 16-wide grid (±8 floor) plus
   sampling SEs giving ~7–14-axis 95% bands; for LME the bracketing pair straddles
   zero only ~57% of the time under resampling. Report intervals, drop decimals.
   (CODE_REVIEW.md (f))
3. CLAIM 2's effect belongs to the AXES, not the sign arm: float_bot − float_top
   matches sign and exceeds its magnitude (LME m48 +21.9 vs +7.8 pp). The 4/4
   "alignment" compares bot−top@48 against Delta@96 (unjustified cross-m) and fails
   same-m on LME/LoCoMo at small m. (I-3, I-4)
4. The BOT-vs-TOP trend toward m=96 is largely overlap dilution (unacknowledged in
   code or text: 32 shared axes at m=64, 64 at m=80, identity at 96), and
   LME m48 rand > bot refutes any low-variance selection rule. (I-5, I-6, Step 3b)
5. PerLTQA "crossover near 243" spans 153–243 across standard windows under a
   linearity the (concave) data already violate — effectively unidentified. (I-2)
6. "Budget-matched" mislabels a 32:1-per-axis storage asymmetry; the sweep's own
   docstring ("isolates quantization, not dimension") must move into the claim.
   (CODE_REVIEW.md (e))

## What survives (credit where due)

- Every recomputed cell agrees (10/10 Step-1 grid + full LoCoMo/REALTALK grids to
  4dp); m=96 matched==full-96 on 4/4; tie expectation proven exact by brute force;
  every semantics-changing mutation moves Delta loudly; largest jump 32→48 is a
  genuine shared feature; overlap-free exclusive contrasts confirm a real per-axis
  variance effect (LME +8.1, PerLTQA −16.4 pp at m=64); the readout flags its
  extrapolation as beyond-range.
- Preamble headline vs sweep discrepancies (LME 0.016, RT 0.076, LoCoMo 0.17 pp)
  are stale-headline vintage, not sweep error — but the two number sets in the
  brief should be reconciled in one place.

## Required changes (explicit)

(a) Replace "monotone on all four / same shape" with correlations + slope ratio +
    the two early dips. (b) Report crossovers as bracketing intervals, no decimals.
(c) Reframe CLAIM 2 as a both-arms axis effect with the float magnitudes shown, or
    drop the sign-centric claim. (d) Disclose TOP/BOT overlap and show exclusive
    contrasts alongside. (e) Replace "near 243" with the 150–250+ window spread and
    concavity warning, or withdraw the point estimate. (f) Rename "budget-matched"
    to "dimension-matched" (or state the 32:1 bit asymmetry next to every use).

## What I could NOT do and why

- Write to the required output dir: /mnt/c is mounted read-only in this session, so
  all deliverables live in /home/mdp/muse-work/audit-axis/ (MY_NUMBERS.md frozen
  there). Nothing was written outside it; caches untouched; no git writes.
- Full-precision (beyond 4dp) comparison: their tables are quoted to 4dp only.
- Exact crossover CIs: no per-query data retained — my bands are approximate
  (likely conservative). A query-level bootstrap by the authors would tighten them
  but cannot recover the dropped decimals.
- LoCoMo frozen-headline reconciliation (+6.82838 vs sweep +6.6550): my recompute
  confirms the sweep; the headline's provenance is outside this audit's data.
- Time budget (~50 min) held: Steps 1–5 complete; no network/installs used.
