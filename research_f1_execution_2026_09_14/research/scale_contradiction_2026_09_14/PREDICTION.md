[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# PREDICTION — SIGN96 tie-rate vs archive size N

Written BEFORE running any scale measurement (step 2). Frozen (never edited after the fact).
Corrections, if any, go into VERDICT.md §"Prediction post-mortem".

Written at: after step-1 control only. What I already knew when writing this:

VERIFIED (this session, `control.py` → `evidence/control.json`):
- LME   sign FR@3 0.5421335697399526 / float 0.4415957446808511 → **+10.053783 pp** (frozen +10.037943)
- PerLTQA sign 0.48894479616364206 / float 0.551692074528853 → **-6.274728 pp** (frozen -6.275)
- REALTALK sign 0.22553482307028402 / float 0.17253405381064957 → **+5.300077 pp** (frozen +5.2241)
- Caches are already centered: col-mean abs max 7.10e-16 (LME), 4.41e-16 (PerLTQA).
- **Natural N ranges** (this is a hard constraint on what step 2c can even see):
  - LME 470 archives: N ∈ [396, 616], mean 492.8, median 490
  - PerLTQA 30 archives: N ∈ [293, 546], mean 409.6
  - LoCoMo 10 conversations: N ∈ [369, 689]
  - REALTALK 10 archives: N ∈ [410, 1548]  ← the only family with >3x span

## P0 — algebraic identity (stated before computing)

The frozen tie flag is `bc > slots` with `slots = K - strictly`, `strictly = #{d < d_(K)}`,
`bc = #{d == d_(K)}`. Since `strictly + bc >= K` always,
`bc > K - strictly  ⟺  strictly + bc > K  ⟺  #{d <= d_(K)} > K  ⟺  d_(K+1) == d_(K)  ⟺  gap == 0`.
**I predict `tie(bc>slots)` and `gap==0` are the SAME event, always, with zero disagreements.**
If so, that candidate explanation for the contradiction is dead on arrival.

## P1 — direction of the tie rate under the frozen definition

I predict the tie rate **RISES** with N and **saturates**, i.e. the coordinator is right and the
relayed 54%→26% is not the frozen `bc>slots` statistic on these caches.

Reason (order-statistics sketch, to be checked numerically): Hamming distances live on the integer
support 0..96. The K-th order statistic sits where `N·F(d) ≈ K`. The expected multiplicity at that
value is `N·p(d) = K · p(d)/F(d)`. For a binomial-like left tail the step ratio
`p(d-1)/p(d) = d/(97-d)` DECREASES as d moves left, so `p(d)/F(d) = 1 - ratio` INCREASES, so the
expected boundary multiplicity `N·p(d_(K))` grows slowly with N. More mass exactly at the
threshold ⇒ more overflow ⇒ higher `P(d_(K+1) == d_(K))`. The relayed mechanism story ("moves into
the sparse tail") gets the sign of this ratio backwards: the tail is sparser in absolute
probability but *relatively steeper*, which concentrates MORE of the K candidates onto the single
threshold integer, not fewer.

Quantitative guess for the frozen definition on real archives: ~0.20–0.25 at N≈500 rising to
~0.35–0.45 at N≈25000, saturating (it cannot reach 1).

## P2 — is pooling an artifact?

I predict **NO**. Subsampling rows inside one real archive (method b) will agree with pooling
(method a) in the overlap region, because the tie rate is a property of the distance distribution's
discreteness, and both operations change only the number of draws from a similar-shaped
distribution. Correlated turns in a real archive will make the distance distribution slightly
WIDER (more near-duplicates at small distance), which if anything raises the tie rate further.
Risk: pooled archives are mutually unrelated, so pooling adds only far-tail (d≈48) mass and cannot
push d_(3) as far left as real added mass would. That means pooling could UNDER-state the rise —
a direction that still contradicts the relayed claim.

## P3 — where the relayed 54%→26% could be TRUE

Ranked guesses, to be tested:
1. **`bc > 1` instead of `bc > slots`** ("is the K-th distance value shared at all") — a strictly
   weaker event. This is the statistic the relayed *mechanism story* actually describes ("the 3rd
   nearest sits inside the concentrated mass"). MOST LIKELY CANDIDATE. Predicted ~0.5 at small N.
2. **Synthetic / uncorrelated codes** rather than these real archives — if the relayed run used
   random ±1 96-bit codes, the mass really is a clean Binomial(96,1/2) at 48 and the behaviour can
   differ from real correlated archives.
3. Larger K (K=20 shortlist / K=50 two-stage): the tie rate at the K-th boundary for large K is
   dominated by a different region of the distribution.
4. The float arm: essentially zero tie rate at every N (continuous scores) — cannot produce 54%.
5. Per-archive vs per-query averaging: a weighting effect only; predicted to change numbers by
   <2 pp and NOT to flip a monotone direction.

## P4 — SIGN-minus-float delta vs N

I predict the delta shows **no measurable N trend** at the sample sizes available. At n=120 queries
per bin, the per-query FR@3 sd is ≈0.4, so SE(mean) ≈ 0.037 and SE(paired delta) ≈ 0.02–0.03, i.e.
±4–6 pp at 2 SE. The coordinator's 10.0 / 7.0 / 14.3 / 2.6 / 7.6 / 3.6 pp spread (range 11.7 pp) is
within what a constant delta produces at that n. **I predict I will have to state that the sample
sizes do not permit any claim about the delta's N-dependence**, and that the only way to get power
is to use all 470 LME queries per bin (paired, same queries across N), which I will do.

## P5 — what would falsify P1

A subsampling curve inside one real archive that FALLS with N under the frozen `bc>slots`
definition. If (b) falls while (a) rises, pooling IS the artifact and the coordinator's six numbers
are an artifact of stacking unrelated archives.
