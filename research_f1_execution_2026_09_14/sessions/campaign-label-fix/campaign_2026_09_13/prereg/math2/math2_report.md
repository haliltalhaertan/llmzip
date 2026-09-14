[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# MATH-2: theory framing for the bit-budget floor

[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION] [LIT-CHECK: no network — all "established results" below are from knowledge, flag before citing]

**A note on deliverables:** this session is read-only on files (write tools disabled), so I could not create `/tmp/math2/math2_report.md` + `math2_details.json` on disk. The full report content and the JSON are given below — copy-paste ready. All numbers tagged [E] were re-read from your frozen artefacts this session (paths at bottom); everything else is [SPEC]/conjecture.

**Empirical anchors used [E]:** native SIGN96 LME FR@3 54.20%, LoCoMo 23.65%; subset curve LME 10B −2.7pp / 8B −5.9 / 6B −9.2 / 4B −17 / 2B −34; random≈spread≈best; TOP48 −10pp vs random-mean (W/T/L 91/179/200); BOT48 beats TOP48 both benchmarks (+7.9pp LME, +4.9pp LoCoMo); mixing damage monotone in variance disparity; learned selection killed (m1: drop64 at null 57th/89th pct); D2 tie model T AUC 0.798 (m2: 10/10 splits, mean 0.821) vs mean-model 0.686, but gold-informed (F1); gold-free G AUC 0.555, 0/10 ≥0.65 (m2); c2 LARGE-free AUC 0.670/0.568, gain@0.20 inside 200-draw noise both benchmarks after Bonferroni (m3); utilities benchmark-local (Spearman ~0.1, D3/C5).

---

## 1. Framework survey: what each body of theory gives us, and what it cannot

| # | Body | One-line gives-us | One-line cannot |
|---|---|---|---|
| T1 | SimHash / 1-bit embedding (Charikar; Goemans–Williamson rounding): per-coordinate disagreement `P[sign_q ≠ sign_d] = θ/π`, Hamming/k unbiased for θ/π, `Var ≈ θ(π−θ)/(kπ²)`-scale | Quantifies per-pair angle noise as a function of k, and why spread (near-orthogonal axes) beats concentrated subsets | Pairwise only — says nothing about top-k order, ties, or which subset S preserves rank; per-axis deltas here are tiny (min 0.066 [E]) so the asymptotic regime over-promises |
| T2 | Order statistics of discrete (Binomial/lattice) scores: exact-tie probability at the top-k boundary, `E[#tied at cutoff]`, duplicate-bucket occupancy | The only machinery that predicts your actual decision variable: tie-mass and bucket collisions as a function of k, N, margin | Needs the true score law as input — it does not supply the margin distribution; must be calibrated on frozen data, not assumed Binomial |
| T3 | Rate–distortion / JL lower bounds (Johnson–Lindenstrauss; Larsen–Nelson / Alon-type (1+ε)-distance lower bounds) | Lower-bounds bits needed to preserve *all pairwise distances* to (1+ε) — a sufficient but wildly over-strong condition | **Does NOT transfer to top-k retrieval.** Retrieval needs only the order at one boundary per query, not ε-geometry everywhere. Citing a JL floor here is a category error; your separation paradox (TOP48 wins all means, loses 10pp [E]) is the exhibit |
| T4 | Ranking-preserving / top-k compression (e.g., "quantize to preserve order, not distances"; learning-to-hash ranking losses) | Right objective: bounds on `P[gold falls out of top-k]` in terms of score gaps (margins), not mean distortion | Existing bounds assume i.i.d. scores or known gap laws and gold-free thresholds rarely match; your margins are query-dependent and benchmark-local (C5) |
| T5 | Quantized-kNN sketching bounds (binary/multi-table codes; recall vs code-length trade-offs) | Predicts the *shape* you see: graceful-then-cliff degradation (each halving of k costs superlinearly once tie-mass ~ O(1)) | Bounds are archive-averaged and learner-specific; they do not predict per-question flips or which S is best — and yours differ by benchmark [E] |
| T6 | Randomized tie-breaking / conformal-style exchangeability | Justifies your 20/100-trial protocol: with frozen random priorities, trial-averaged FR is an unbiased estimate of "random tie-break" risk, and trial-std measures boundary contestedness | Cannot turn a bad code into a good one — it only measures the tie lottery your code already bought (m3's random-abstention +1.1–1.8pp shows how much "free" gain any lottery ticket gets) |
| T7 | Selection-bias / max-of-k (E[max] bounds: for standardized variables, `E[max_k] ≤ √(2 log k)`-scale; exact values only via normal order-statistic integrals) | Quantifies your kill-rule and seed-noise corrections: why vs-best-of-10 sits ~1.2–1.7pp below the null mean (m1 [E]) and why 5-seed random range is 3.5pp [E] | No elementary closed form for E[max] exists even for Gaussians (Mills-ratio integrals only); with correlated splits/overlapping questions only bootstrap/simulation is honest (your C1 approach was correct) |

**Traps named explicitly:** (i) JL→retrieval transfer (T3); (ii) mean-separation as objective — your paradox falsifies it [E]; (iii) vs-best without null correction (m1/C1); (iv) gold-informed features dressed as predictors (F1); (v) single-split + small-n AUC/pp claims inside seed noise (m3 lesson: 10-draw "win" → p_bonf 0.18 at 200 draws).

---

## 2. Candidate statements S1–S5

### S1 — Boundary-informativeness monotonicity
**Statement.** Fix benchmark + protocol. For subset S define
`BI(S) = E_q[ σ( −a·tie_q(S) − b·strict_q(S) + c·margin_q(S) ) ]`
with (a,b,c) the frozen D2 T-model coefficients (bias −1.87, tie −1.21, strict −3.12, margin +0.21 [E]) evaluated with TOP48-arm geometry replaced by S-arm geometry. Claim: `E[FR@3(S)]` is nondecreasing in `BI(S)` across gold-free subsets S at fixed |S|.
**Why it earns its place:** compresses D2/m2 (your strongest mechanism result: T−M Δ +0.162, 10/10 [E]) into a portable, computable functional; directly tests "ties explain selection ranking."
**Proof strategy/tools:** no proof from first principles — it is a *conjectured monotone transport*: T2 order statistics (tie-mass as sufficient statistic of boundary lottery) + T6 (trial win-rate = BI's target). Formal content is thin; value is predictive.
**Difficulty:** low (analysis-only).
**ONE frozen-data check:** on LME+LoCoMo, for all frozen arms (native/spread/TOP/BOT/RAND seeds/drop at 32/48/64/80): compute BI(S) on train-half questions with frozen coefficients, rank arms, Spearman vs test-half FR. Prespecify ρ≥0.7 as pass.
**Falsifier:** ρ<0.4 on either benchmark, or TOP48 outranks spread on BI yet loses on FR (replays the paradox inside the functional).

### S2 — Effective-floor formula (tie-mass version)
**Statement (conjecture, calibratable).** Let N = archive size, k = bits, τ = tolerable expected #docs tied with gold at its distance. Approx per-query Hamming law as Binomial(k, p̄) with p̄ from archive marginals; worst-case tie density `ρ_max = max_d P(D=d) ≈ √(2/(πk·4p̄(1−p̄)))` (de Moivre–Laplace peak). Floor conjecture:
`k* ≈ (2/(π·4p̄(1−p̄))) · (N_eff/τ)²`— i.e. keep `N_eff·ρ_max ≤ τ`,
where `N_eff` = #docs within ±1 of gold distance (the *margin-truncated* archive, not full N — this is the load-bearing refinement vs naive N).
**Why:** turns "graceful-then-cliff" into a formula with two measurable inputs (N_eff distribution, p̄); explains LoCoMo-flat-at-top (BOT80≈native [E]) vs LME cliff via different N_eff.
**Proof strategy:** T2 local-limit theorem + union bound over the ±1 shell; calibration replaces Binomial with empirical margin histogram (frozen distances verbatim).
**Difficulty:** medium (derivation is standard; calibration is the work).
**ONE check:** fit N_eff per question on native96 frozen distances; predict per-question k-at-collapse along nested spread ordering (B3-style); report rank correlation predicted-vs-actual collapse-k. Pass: ρ≥0.5 both benchmarks.
**Falsifier:** collapse-k uncorrelated with N_eff (|r|<0.2 both benchmarks — same kill-bar as your B3), or Binomial ρ_max off by >3× from empirical tie rates (then the Binomial shell must be dropped for the empirical histogram).

### S3 — Selection-lift lemma (kill-rule null)
**Statement.** Let X₁..X_k be exchangeable null arm gains with marginal mean μ, sd σ. Then `E[max X_i] − μ ≤ σ·√(2 log k)` (Gaussian/exchangeable upper envelope; exact equality for no elementary law). Your m1 numbers *are* the calibrated instance: LME null mean −1.62pp sd 1.38 (k=10); LoCoMo −1.20pp sd 0.93 [E].
**Why:** formalizes the R2D/m1/C1 correction you already apply; kills future "vs-best" fooling analytically.
**Proof strategy/tools:** standard Gaussian-max bound (Mills ratio + union bound) or generic sub-Gaussian maximal inequality; no new math. **No clean closed form for E[max] exists** — the honest formalization is the *upper bound*, plus the numerical null (m1) as the tight instance.
**Difficulty:** low (textbook).
**ONE check:** already done (m1) — re-derive the bound's prediction (σ√(2log10) ≈ 1.38·2.15 ≈ 2.97pp wide envelope containing observed lift) and confirm drop64 sits inside it (57th/89th pct [E]).
**Falsifier (of usefulness, not truth):** if a future null shows lift ≫ σ√(2log k), the sub-Gaussian envelope is vacuous for this data and only bootstrap (C1) may be cited.

### S4 — DISCRIMINATING test: tie-crowding vs boundary-noise [RECOMMENDED]
**Statement.** Rival theories make opposite *conditional* predictions at fixed margins: (H_tie) flip-rate varies with tie-mass/strict-count **holding margin fixed**; (H_noise) flip-rate varies with margin/query-magnitude reliability **holding tie-mass fixed**. Concretely: stratify frozen decisive questions (TOP48-loss vs RAND-win and reverse) into margin terciles; within each tercile, H_tie predicts `P(flip|high tie) − P(flip|low tie) ≥ 15pp` while H_noise predicts ≈0; symmetrically within tie-mass terciles, H_noise predicts a margin gradient ≥15pp while H_tie predicts ≈0.
**Why:** the single cheapest analysis that can kill a theory — uses only frozen distances + D2 features, no new arms, no gold at *decision* time beyond the validation labels you already use (tag gold-informed analysis-only per F1).
**Proof strategy:** T2 (ties as the lottery) vs T1-per-axis reliability (small-|q| signs are noisier); adjudicated by stratified conditional rates, i.e., a finite-sample conditional-independence test.
**Difficulty:** low (one Muse session; pure recomputation).
**ONE check:** run the double stratification on LME-470 TOP48-vs-RANDmean flips (W/T/L 91/179/200 [E]) + LoCoMo; report the four conditional gaps with paired-bootstrap CIs.
**Falsifier (either direction is informative):** if *both* conditional gaps are <5pp → neither theory operates at this margin scale (pivot to B2/B3 influence/PR); if only the margin gradient survives → tie-centric codecs (A4/A5-fallback, deadzone) are de-licensed and reliability codecs (A3/A5-mask) inherit the budget.

### S5 — No-concentration corollary (spread optimality among oblivious subsets)
**Statement.** Among data-oblivious (query/archive-independent) subsets at fixed k, uniform-spectrum (spread) maximizes worst-case retained angle information `min_θ Var(θ̂)` under the SimHash law, because any concentrated S inflates the worst axis-gap. Predicts spread ≥ random-mean −1pp and spread ≫ TOP-k on *both* benchmarks.
**Why:** gives your most replicated regularity (spread≈random≈best [E]) a one-paragraph theoretical home without overclaiming per-question optimality.
**Difficulty:** low-medium. **ONE check:** verify the inequality's prediction against the frozen budget table (spread vs 5-seed random band at 32/48/64 [E]). **Falsifier:** any benchmark where TOP-k or BOT-k beats spread by >seed-range on 2+ budgets (LoCoMo BOT already nibbles — so scope the claim to "spread never catastrophic," not "spread always best").

---

## 3. Top recommendations (value/cost; cost = Muse sessions, no paid APIs)

1. **S4 first (1 session, highest information-per-cost).** It is the only candidate that can *kill* a mechanism direction before you spend codec sessions on A3/A4/A5. Prerequisite to everything else; feeds directly into your B1 decomposition.
2. **S2-calibration second (1–2 sessions, decision instrument).** It produces the artefact the programme actually needs for the 12/8/6/4B Pareto call (C4): a per-question collapse-k predictor from N_eff. S1 is folded into S4+S2 as the scoring functional — do not pursue S1 standalone. S3 is already empirically done (m1); formalize only the bound sentence, no sessions needed.

**Lean/Mathlib sketch (cleanest = S3 bound; statement shape only, Muse-only, no paid prover APIs):**
```lean
-- S3 envelope: max of k sub-Gaussian draws. Mathlib has measure/probability
-- foundations; Gaussian-max needs Mills-ratio integral (not in Mathlib as a
-- ready lemma) so formalize the generic sub-Gaussian maximal inequality instead:
-- variables {X : Fin k → Ω → ℝ} [IsSubGaussian σ X] ...
-- theorem max_le_sqrt_two_log (k) : E[max_i X_i] - μ ≤ σ * Real.sqrt (2 * Real.log k)
-- Proof ingredients: Chernoff bound per arm + union bound + optimize Chernoff
-- parameter (all available: MeasureTheory, Real.exp/log). S4's conditional-rate
-- claim is statistics, not a Lean target — keep it as a preregistered analysis spec.
```
Cost rule note: full Lean formalization is out of scope for the 2–3h MATH-2 budget; the above is the statement shape to hand a future Muse-only formalization session. Do not attempt S2's local-limit approximation in Lean (needs Fourier/characteristic-function machinery — poor value/cost).

---

## 4. Beyond reach (honest list)

1. **"No ≤b-bit code beats native"** — ill-posed as stated: native is itself a 96-bit code, and heterogeneous 2-bit arms at matched bytes are outside the subset family; any theorem must fix the family (oblivious 1-bit subsets, say) and even then is false per-benchmark without distributional assumptions (BOT80≈native on LoCoMo [E]).
2. **Universal data-independent bit floor** — out of reach: floors depend on (N_eff, margin law), which are benchmark-local by your own C5 result. Only *conditional* floors (given margin distribution) are well-posed — that is S2.
3. **Optimal-subset guarantees** — subset selection for retrieval is combinatorial (max-coverage-like); expect NP-hardness for exact optima and only greedy/approximate guarantees that will be vacuous at n=96 with 3.5pp seed noise. Your C3 harness (resplit + seed sweep) dominates any such bound in practice.
4. **Causal tie theory from observational flips** — D2/m2 AUCs are correlational by their own honesty sections; ties are consequences of S as well as causes. Causality needs the dither intervention (A4 dose-response), not more theorems.
5. **Transferable utility theory** — D3/C5 killed it empirically (ρ~0.1); no theorem will resurrect cross-benchmark utilities without a shared generative model you do not have.

---

## math2_details.json (copy-paste)

```json
{
  "labels": ["LOCAL EXPLORATORY", "NOT PREREGISTERED", "NOT FOR CITATION", "LIT-CHECK"],
  "anchors_E": {
    "LME_native_FR3": 0.542, "LoCoMo_native_FR3": 0.2365,
    "subset_curve_LME_pp": {"10B": -2.7, "8B": -5.9, "6B": -9.2, "4B": -17, "2B": -34},
    "TOP48 deficit_vs_randmean_pp": -10.0, "TOP48 WTL": [91, 179, 200],
    "D2_T_AUC": 0.798, "D2_M_AUC": 0.686, "m2_T_mean": 0.821, "m2_G_mean": 0.555,
    "m1_null_LME": {"mean_pp": -1.62, "sd": 1.38}, "m1_null_LoCoMo": {"mean_pp": -1.2, "sd": 0.93},
    "m3_LME_a20_pbonf": 0.18, "transfer_Spearman": 0.1
  },
  "candidates": ["S1_BI_monotone", "S2_floor_formula", "S3_selection_lift", "S4_discriminating_stratification", "S5_spread_maximin"],
  "recommend": ["S4", "S2-calibration"],
  "frozen_checks": {
    "S1": "BI-rank vs test-FR Spearman, prespec rho>=0.7",
    "S2": "N_eff predicted vs actual collapse-k rank corr, prespec rho>=0.5",
    "S3": "already done (m1); confirm inside sigma*sqrt(2 log k) envelope",
    "S4": "double stratification margin x tie-mass, 15pp gap rule with bootstrap CI",
    "S5": "spread vs 5-seed random band at 32/48/64"
  },
  "sources_reread": [
    "/mnt/c/Users/MDP/dev/llmzip-work/pilots/axis_attack_2026-09-12/REPORT.md",
    "/mnt/c/Users/MDP/dev/llmzip-work/pilots/axis_attack_2026-09-12/round3/ROUND3_REPORT.md",
    "/mnt/c/Users/MDP/dev/llmzip-work/pilots/axis_attack_2026-09-12/round3/muse_sessions/ERRATA_ROUND3_D5.md",
    "/mnt/c/Users/MDP/dev/llmzip-work/pilots/axis_attack_2026-09-12/round3/muse_sessions/d2/d2_report.md",
    "/mnt/c/Users/MDP/dev/llmzip-work/pilots/axis_attack_2026-09-12/round3/missing_analyses/m1_kill_null/missing1_kill_null.md",
    "/mnt/c/Users/MDP/dev/llmzip-work/pilots/axis_attack_2026-09-12/round3/missing_analyses/m2_d2multi/d2x_report.md",
    "/mnt/c/Users/MDP/dev/llmzip-work/pilots/axis_attack_2026-09-12/round3/missing_analyses/m3_c2ablation/c2x_report.md",
    "/mnt/c/Users/MDP/dev/llmzip-work/strategy/roadmap_2026-09-13/muse_ideas_technical.md"
  ]
}
```

MATH2_VERDICT: Pursue S4 stratification first then S2 floor calibration; formalize only the S3 sub-Gaussian max bound; universal-floor and no-code-beats-native theorems are out of reach.

