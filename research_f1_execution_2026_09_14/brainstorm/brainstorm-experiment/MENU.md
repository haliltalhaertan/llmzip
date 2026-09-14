# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# MENU.md — every experiment that could move the mechanism question, ranked by
# decisiveness per unit of compute. Cost basis VERIFIED: full LME rescore (470 archives,
# ~500×96 docs) runs in seconds; PerLTQA section rescore (8265 queries) in ~1–2 min (this session).
# Total real data: 258,720 docs × 96-D — everything fits in RAM. Nothing here costs >30 min.

## TIER 1 — interventions with known ground truth (synthetic; minutes each)
1. Amplifier hunt: correlated-covariance dial. Replace diag(s) with block/spiked covariance
   (e.g. top axes correlated rho=0.5–0.9; or 4 spike directions + diagonal tail) × locus grid.
   ESTABLISHES: whether inter-axis correlation is the missing amplifier/budget-curve variable.
   KILLS: "diagonal generator suffices" if spikes reproduce +10pp and the rising m-curve.
   COST: ~5 min. INTERVENTION. Highest information per minute remaining.
2. Query-noise anisotropy dial: noise concentrated top (sigma_j ∝ s_j^2) vs bottom vs isotropic,
   × locus. ESTABLISHES: whether noise placement, not signal placement, drives Delta.
   KILLS: D2 (matched-noise assumption in GENERATOR.md) if isotropic/top-noise erases the locus gap.
   COST: ~5 min. INTERVENTION.
3. Sealed-scale synthetic: N = 100K–1M, d=96, bot16/alpha2 cell + broad/alpha1 cell; subsampled
   queries. ESTABLISHES: sign of dDelta/dN — does the effect survive the programme's target scale,
   or is everything here a small-N artifact (standing result G)? COST: ~15–30 min (chunked
   Hamming/cosine; no new data needed). INTERVENTION. Only experiment addressing scope.
4. Un-normalized locus + spike-spectrum variants (alpha to 4; 4-axe spike + flat tail).
   ESTABLISHES: robustness of the locus flip; whether extreme spectra reach real magnitudes.
   COST: ~5 min. INTERVENTION.

## TIER 2 — interventions on the real caches (causal, no new data; minutes each)
5. Query-band projection (THE one-hour brief; see NEXT_BRIEF.md): restrict BOTH arms to
   top-16-only vs bot-16-only axes per archive; compare Delta(band) across 4 benchmarks × 4
   PerLTQA sections. ESTABLISHES causally where discriminative signal lives per corpus.
   KILLS: locus hypothesis if Delta(bot16-only) ≤ Delta(top16-only) on LME/profile.
   COST: ~10 min. INTERVENTION on real data.
6. Axis-ablation curve on real data: zero-out top-k (k=8,16,32) archive axes, re-measure Delta;
   mirror with bottom-k. ESTABLISHES: whether top axes actively HURT sign retrieval (distractor
   hypothesis) vs merely carry no signal. KILLS: "top axes are neutral" if ablation RAISES Delta.
   COST: ~10 min. INTERVENTION.
7. Rotation family: Haar (done, −15.9pp LME) vs axis-PERMUTATION vs per-axis SIGN-FLIP vs
   within-top-block rotation. ESTABLISHES what exactly (C) needs: axis identity, order, or
   within-band structure. Permutation preserving Delta would localize the effect to the
   multiset of marginals, killing structural stories. COST: ~10 min. INTERVENTION.

## TIER 3 — decisive negatives / robustness (cheap, worth doing while Tier 1–2 run)
8. AQS variants: doc-side-only magnitude, top-m magnitude restoration, score-level fusion sweep.
   Marginal; standing result (D) already shows full AQS costs −3.56pp. CORRELATION-adjacent.
   COST: ~10 min.
9. Metric-format checks: FR@1/FR@5/FR@10 Delta; K-sweep of the budget curve; seed-robustness of
   the nine deaths. Guards against metric-cherry-picking. COST: ~5 min. CORRELATION (descriptive).

## TIER 4 — correlations: near-worthless here (nine deaths; run only as calibration, never as evidence)
10. Any further per-query statistic (hubness scores, margin distributions, norm rules, alignment
    coefficients) fitted on the suggesting corpus. EXPECTED VALUE ≈ 0 given the failure pattern;
    permitted only with a preregistered held-out benchmark + section-level kill criterion.
    COST: minutes to compute, weeks to be fooled by. CORRELATION — rank last on purpose.
