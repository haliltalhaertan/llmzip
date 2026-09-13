# STATUS — math2 sharp full-profile deletion bounds (2nd pass)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

- Workspace: /home/mdp/muse-work/math2-sharp-bounds (dedicated; only writable location this pass).
- Sources elsewhere (incl. /mnt/c/.../math_discovery_2026_09_13/*): READ ONLY, never overwritten.
- Constraints: no benchmark runs, no Task4F1 outcome access, no external model APIs,
  no installs, no web fetch. Muse subscription only. Bounded ~20 min pass.
- Mandatory reads done: COORDINATOR_REVIEW.md (ranking_bounds, sign_mechanism,
  bit_allocation) + ranking_bounds REPORT.md. Worker reports treated as fallible;
  coordinator notes govern until independently resolved.

## Plan
1. [x] Mandatory reads.
2. [in_progress] Prove/refute joint realizability of interval retained-distance choices
   (fixed subset, duplicate docs allowed, incl. s=0 / r=0); derive sharp per-gold
   min/max expected inclusion (K=3 explicit); counterexample-first search.
3. [pending] Multi-gold joint attainability: conflict witness + computable gap bound
   (no hardness claims).
4. [pending] Artifacts: REPORT.md, verify.py, results.json, STATUS.md (this file),
   independent checker; exact Fraction/integer arithmetic; fail-closed + broken variant.
5. [pending] Contrast vs old T3/T4 coarse bound with strictly-improved nonzero witness;
   note what a real-data read-only eval would measure (not run).

## Findings (final)
- Theorem R PROVED + machine-checked: every interval-profile choice jointly realizable
  (per-doc independent construction after XOR query to 0; duplicates allowed).
  s=0 / r=0 / b=0 degeneracies checked.
- Theorem P PROVED + machine-checked: sharp per-gold min/max at opposite corners
  (6,492 K=3 cells corner==brute-force; dominance over old T3/T4 indicators).
- Theorem J PROVED + machine-checked: avg-of-per-gold-max NOT jointly sharp
  (witness b=4,s=2,r=2,d=(2,2,0,0), avgmax=1 vs best-joint=3/4, Gamma=1/4 envelope).
- Strict improvements over T4: 0 -> 1/2 (lower), 1 -> 1/3 (upper), K=3, genuine deletion.
- Both executables exit 0; deliberately false variant rejected by both (fail-closed).
- Preserved failures: shared-coupling obstruction (refuted), separate S/T monotonicity
  (false; salvaged via transitions), joint-attainability of averaged maxima (refuted).
