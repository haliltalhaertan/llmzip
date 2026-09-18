[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# REPORT.md -- Attack-the-question session (2026-09-14, ~45-min pilot)
Question: is the programme ("12 bytes beat 384 bytes by 10pp") chasing an artifact?
Method: reimplemented both arms + E[FR@K] tie expectation from the read-only caches; reproduced
all four frozen headlines exactly (VERIFIED controls in ATTACKS.md); then ran attacks 1-4 by
computation and attack 5 by analysis. Full numbers: ATTACKS.md. Code: atk.py, se.py, se2.py,
atk_rt.py; machine-readable means: atk_results.json (LME/PerLTQA/LoCoMo; REALTALK rows live in
console output -- atk.py's RT rows are NaN because 23 empty-gold queries must be skipped first,
as atk_rt.py does). Uncertainty: paired 95% CIs throughout; "n.s." = CI crosses zero.

## Summary verdict
- SURVIVED: the numbers are real (exact reproduction), not tie bookkeeping (~80% survives
  adversarial tie-breaking), not a K=3-only phenomenon (sign holds K=1..10; PerLTQA reversal holds
  at every K), and the dimension interaction plus the PerLTQA profile/events split remain genuine
  unexplained facts.
- DID NOT SURVIVE: the interpretation. A same-storage standardized float beats the published
  baseline by +11.59pp on LongMemEval and beats or ties sign on all four benchmarks; "+10pp" is
  the maximum over K and the value of a rising dimension curve at its arbitrary endpoint (at 32-D
  float wins everywhere); nothing is VERIFIED above N=1548 vs a 100K-10M target where Hamming's
  97 levels make top-3 a tie lottery.
- The single number a reader should be told alongside "+10pp": **+11.59pp (95% CI [8.88,14.29])
  -- the gain of per-axis-standardized cosine over the programme's chosen cosine baseline on the
  same LongMemEval data** (equivalently: sign vs that fair float is -1.53pp, n.s.). The honest
  headline is "variance-equalization beats raw cosine by ~11pp; quantization adds nothing."
- Recommendation: (a) replace the float baseline with standardized cosine going forward and require
  any mechanism to beat IT, not cosine; (b) stop fitting per-query correlational rules (lesson stands);
  (c) the highest-value next experiment is not another mechanism hunt at N~500 but a scale test:
  does Hamming top-3 survive N>=100K, with what re-ranker, at what true byte/compute cost.
