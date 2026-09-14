# COVARIANCE STRUCTURE AND COORDINATE HET- EROGENEITY GOVERN BINARY QUANTIZATION OF CONTRASTIVE EMBEDDINGS
First, the **full co- variance structure** —not merely its diagonal—determines the absolute level of ranking fidelity, with off-diagonal correlations contributing 30–50% of the sig- nal.

...

# arXiv:2605.17524v2 [cs.LG] 29 May 2026
Arxiv Preprint Ver.

...

correctors require). Concretely, we establish the following:
• An approximate Spearman fidelity formula via Stein’s lemma, revealing that off-diagonal covariance contributes 30–50% of ranking accuracy (§4, Theorem 1).

...

• A phenomenological scaling law that predicts fidelity across models and dimensions from three covariance statistics (§6).

...

In graph-based search, the two-bit advantage is amplified 1.2–4.1 _×_ in local neighborhoods—a phenomenon our framework explains through conditional concentration.

...

Crucially, these results assume isotropic data or analyze worst-case performance; they say nothing about how distributional structure—heterogeneous variances, non-trivial covariance— affects BQ quality.
Our work shows that this structure is not merely present but is the _dominant_ factor: ranking fidelity depends on the full covariance matrix, not just on dimension and angle.

...

QuIVer (Xiao et al., 2026) takes the opposite approach: it preserves coordinate axes and builds the entire graph index—edge selection, pruning, navigation—natively in two-bit space.

...

Our contribution is to show that this residual heterogeneity is not a defect but the _signal_ that BQ exploits.

...

Our analysis targets the extreme 1–2 bit setting where no codebook is needed and distances reduce to hardware-accelerated popcount.

...

3.2 FROM FIDELITY TO RECALL: THE _F_ / _G_ DECOMPOSITION

...

We denote this gap structure _G_ .
The two factors combine through a sub-Gaussian pairwise error bound:
_P_ [pairwise misordering] _≤_ exp

_−_ _γ_ ² _b_ ∆ ²
2 _σ_ ² BQ _,b_

_,_ (3)
where _γ_ _b_ (the calibration slope, a function of _F_ ) controls how faithfully BQ scores track true inner products, and _σ_ ² BQ _,b_ is the BQ score noise variance.
A union bound over _K_ ( _N_ _−_ _K_ ) candidate pairs gives _P_ [top- _K_ error] _≤_ _K_ ( _N_ _−_ _K_ ) exp  _−_ _c_ _b_ ∆ ² min  _._ (4)

...

Assumption H1 (Gaussian)
Betser et al. Covariance Σ
Fidelity _F_ (noise)
Margin _G_ (signal)
§4–§7
data-given
1-bit / 2-bit rotation
Recall

...

H1a is a _finite-dimensional marginal_ Gaussianity condition: it asserts that any fixed _k_ coordinates are approximately joint Gaussian, but does not require the full _D_ -dimensional distribution to be Gaussian. This is justified by Betser et al.

...

Together, H1a provides the distributional structure used in Stein’s lemma and the sign/magnitude analysis, while H1b ensures that L2 normalization does not distort the coordinate-level statistics.

...

Our theorems analyze the _F_ branch; _G_ is treated as given.

...

_In particular,_ _F_ _depends on the full covariance matrix_ Σ _, not just its diagonal._
The off-diagonal contribution to ranking quality is captured by the **Stein squared signal** :
_I_ off := 
_i_ _̸_ = _j_ ( _a_ _i_ Σ _ij_ ) ² = 

...

_(b)_ max _i_ _|_ _q_ _⊤_ _i_ Σ _q_ _i_ _−_ tr(Σ) _/D_ _|_ ≲ _∥_ Σ _∥_ _op_ 
log _D/D_ _._
**Corollary 3** (Rotation harms heterogeneity-aware BQ) **.** _Rotation drives_ CV ² ( _σ_ ) _→_ 0 _(Theo- rem 2b), eliminating the heterogeneity-dependent component_ ∆ _het of the 2-bit advantage (Propo- sition 5b).
The residual gain_ ∆0 _>_ 0 _(the isotropic scalar magnitude advantage) survives, so 2-bit does not fully degrade to 1-bit; however, the data-dependent advantage that QuIVer exploits is de- stroyed._

...

5 WHY 2-BIT BEATS 1-BIT: THE MAGNITUDE INFORMATION GAIN
**Proposition 5** (Per-coordinate magnitude gain and heterogeneity monotonicity) **.** _In a simplified per- coordinate model under Assumption 1:_

...

In words: heterogeneity provides_ additional _magnitude-bit gain beyond the scalar quantization baseline._

...

2 _/π >_ 0, and the strict monotonicity of _g_ ( _t_ ) = 2 _t_ (1 + _e_ _−_ _t_ ² _/_ ² ). Part (b): Taylor-expand _ρ_ 2( _σ_ ) and _ρ_ 1( _σ_ ) around _u_ _i_ = _σ_ _i_ _/_ ¯ _σ_ = 1, yielding _K_ _≈_ 0 _._ 088 _>_ 0. Full proof in Appendix C.

...

_D_ ) _of_ _D_ _magnitude bits are affected, and the resulting fidelity perturbation satisfies_
_|_ _F_ _actual_ _−_ _F_ _per-coord_ _|_ = _O_ ( _D_ _−_ ¹ _/_ ² ) _._ (7)

...

These two paradigms are not competing solutions to the same problem; they are _opposite strategies for handling the same physical quantity_ . Theorem 2 and Corollaries 3–4 make this precise: rotation maps one regime into the other.
This exposes a fundamental tradeoff in BQ design: _universality_ (distribution-free guarantees via rotation, as in RaBitQ) versus _exploitation_ (leveraging coordinate structure for higher fidelity on the distributions that actually arise, as in QuIVer).
RaBitQ provides _O_ (1 _/D_ ) variance bounds that hold for any distribution by treating heterogeneity as noise to be elim- inated; our analysis reveals that this “noise” is in fact exploitable signal.
Neither strategy dominates: the appropriate choice depends on whether the Gaussian prior (Assumption 1) holds.

...

6
Arxiv Preprint Ver.
Table 2: Coordinate Gaussianity verification (Assumption 1). All contrastive models exhibit QQ- plot _R_ ² _>_ 0 _._ 99 and thin-shell CV _<_ 0 _._ 1.
Dataset Model _D_ QQ _R_ ² CV

...

We report representative results here; full tables for all 13 datasets appear in Appendix F.
**Experimental setup.** Embeddings are drawn from seven pretrained models: Cohere embed-v3 (768-d), MiniLM-L6-v2 (384-d), nomic-embed-text (768-d), BGE-M3 (1024-d), Jina-v2 (768-d), DINOv2 (768-d, self-supervised vision), and an i.i.d. Gaussian baseline _N_ (0 _, I_ 768).

...

8.1 IS THE GAUSSIAN PRIOR JUSTIFIED?

...

The answer is unambiguous (Table 2): every contrastive model achieves _R_ ² _≥_ 0 _._ 9959 with norm CV below 0.09.
The non-contrastive GIST-960 fails completely ( _R_ ² _≈_ 0, CV = 0 _._ 36), confirming that the Gaussian prior is specific to contrastive training and not an artifact of high dimensionality.
8.2 DOES THE FULL COVARIANCE MATTER?
With the Gaussian prior confirmed, we can test the fidelity formula. A natural baseline ignores off- diagonal covariance entirely, predicting _F_ from variances alone ( _F_ diag). Our theory (Theorem 1) predicts that the full covariance _F_ full should match the empirical _F_ actual much more closely.
Table 3 confirms this dramatically: the diagonal-only prediction underestimates fidelity by 0.20– 0.36, while the full-Σ prediction matches within _±_ 0 _._ 02 (mean explanation ratio 103%).
The off- diagonal correlations are individually tiny ( _|_ _ρ_ _ij_ _| ≈_ 0 _._ 04–0 _._ 11), but there are _D_ ² of them, and their collective contribution accounts for 30–50% of the ranking signal (§4, _D_ ² accumulation).
This is perhaps the most surprising empirical finding: the information that makes BQ work is predominantly _relational_ (between coordinates), not _marginal_ (within each coordinate).
Notably, this experiment also serves as a stringent _joint_ Gaussianity test: the 103% match would fail catastrophically if the joint distribution deviated substantially from Gaussian, since the full-Σ prediction relies on the com- plete _D_ _×_ _D_ covariance structure, not just marginal fits.
7
Arxiv Preprint Ver.
Table 3: Ranking fidelity _F_ : diagonal-only vs. full-Σ prediction vs. actual. Off-diagonal covariance contributes 30–50% of the signal.
Dataset _F_ actual _F_ full _F_ diag Expl. ratio
Cohere 0.681 0.688 0.474 103% Arxiv 0.897 0.886 0.546 97% CodeSearch 0.823 0.837 0.542 105% Random 0.907 0.899 0.560 98%

...

Doubling the code length from 1 to 2 bits per coordinate doubles storage. Is the information gain worth it? Proposition 5 predicts yes—and that the gain should grow with coordinate heterogeneity.
Table 4 confirms both predictions. The fidelity gain ∆ _F_ is strictly positive on all six datasets (+0.049 to +0.132), and the recall improvement ranges from +0.110 to +0.210.

...

This is the central design puzzle: RaBitQ rotates before binarization; QuIVer explicitly avoids ro- tation. Both succeed.
Our theory predicts that rotation uniformizes variances (Theorem 2), which helps linear correctors (Corollary 4) but destroys the implicit weighting that Hamming distance ex- ploits (Corollary 3).

...

For GIST—a degenerate distribution where all coordinates share the same sign—rotation is trans- formative, injecting the sign entropy that BQ needs to function at all.
For contrastive embeddings, the story reverses: rotation is neutral (MiniLM, already near-isotropic) or slightly harmful (Co- here, which has well-calibrated heterogeneity that 2-bit BQ exploits).

...

Table 5: Effect of Haar-random rotation on sign entropy and BQ recall. The response depends entirely on the initial variance structure.
Dataset Entropy: before _→_ after ∆ Recall Regime
GIST 0.000 _→_ 0.511 **+307%** Degenerate Wolt-CLIP 0.836 _→_ 0.616 +3.2pp Over-spread Cohere 0.747 _→_ 0.563 _−_ 0.5pp Near-optimal MiniLM _≈_ const _≈_ 0 Isotropic

...

Dataset _D_ CV( _σ_ ) _H_ sign AD% _F_ 2bit Mag gain _R_ @10 ∆ _F_ rot

...

To stress-test the framework’s extrapolation limits, we perform a fully blind validation on five datasets never used in any prior experiment or fitting (Table 6).
These span three new embedding families (OpenAI text-embedding-3-large, GloVe, SIFT), dimensions from 100 to 3072, and include two non-contrastive negative controls.
The results are striking.
OpenAI text-embedding-3-large at 3072-d—a model and dimen- sionality never seen during fitting—achieves the highest fidelity of any tested embedding ( _F_ 2bit = 0 _._ 952, _R_ @10 = 0 _._ 841), consistent with its low std( _|_ SNR _|_ ) = 0 _._ 228 and high log _r_ off = +1 _._ 08.

...

confirms that non-Gaussian embeddings fall outside the framework. The scal- ing law thus serves a dual purpose: it predicts fidelity when the prior holds, and _diagnoses_ model suitability when it does not. Full per-dataset statistics appear in Appendix G.

...

Binary quantization is often viewed as a lossy compression technique—a necessary evil for scaling vector search. Our analysis suggests a different perspective: BQ is a _covariance probe_ .

...

When these moments carry meaningful information about inter-point distances—as they do under the Gaussian structure induced by InfoNCE—BQ preserves ranking fidelity; when they do not, BQ fails.
This lens explains the apparent paradox of contradictory system designs. Coordinate-preserving methods (QuIVer) succeed because heterogeneous variances create an implicit importance weighting that Hamming distance inherits.

...

9
Arxiv Preprint Ver.
to choose and how much the magnitude bit adds—rather than the absolute level of fidelity, which is determined by the full covariance structure (Theorem 1 and Appendix H).

...

**Limitations.** Our theory requires approximate coordinate Gaussianity (Assumption 1), a condition met by InfoNCE-trained models but not by supervised or hand-crafted features.

...

Models incorporating Matryoshka Representation Learning (MRL) could in principle compress information into a small number of leading coordinates, causing the shared threshold _α_ _x_ to be dominated by outlier dimensions.

...

Michel X Goemans and David P Williamson. Improved approximation algorithms for maximum cut and satisfiability problems using semidefinite programming. _Journal of the ACM_ , 42(6):1115– 1145, 1995.

...

**Step 3: Monotonicity of** _h_ ( _t_ ) = 2 _t_ (1+ _q_ ( _t_ )) **.** We have _h_ _′_ ( _t_ ) = 2 _{_ 1+ _q_ ( _t_ )(1 _−_ _t_ ² ) _}_ . For 0 _< t_ _≤_ 1: _h_ _′_ ( _t_ ) _>_ 0 trivially.
For _t >_ 1: ( _t_ ² _−_ 1) _q_ ( _t_ ) _≤_ max _t>_ 1( _t_ ² _−_ 1) _e_ _−_ _t_ ² _/_ ² = 2 _e_ _−_ ³ _/_ ² _<_ 1, so _h_ _′_ ( _t_ ) _>_ 0. Hence _h_ is strictly increasing from 0 to _∞_ , and the equation _h_ ( _t_ ) = 3 

...

∆0 = _ρ_ 2 _,_ 0 _−_ _τ_ _≈_ 0 _._ 116 _, K_ = _ρ_ 2 _,_ 0  _C_ _′′_ (1) 2 _C_ (1) _−_ _V_ _′′_ (1)
4 _V_ (1) _−_ ¹
2  + _τ_
2 _≈_ ⁰ _._ ⁰⁸⁸ _>_ ⁰ _._ (22)
14
Arxiv Preprint Ver.
D SHARED-THRESHOLD CONCENTRATION AND FIDELITY PERTURBATION

...

Cohere-768 0.060 0.083 79.5 0.9996 BGE-M3-1024 0.098 0.094 64.0 0.9989 wolt clip-512 0.147 0.177 42.0 0.9963 MiniLM-384 _∼_ 0 _∼_ 0 87.0 0.9222 Random-768 0.032 0.046 89.0 0.9967 GIST-960 1.332 3.408 0.0 _<_ 0
F.2 FULL-Σ FIDELITY VERIFICATION (PROBE 16D)
Table 8: _F_ explained by full covariance Σ vs. diagonal-only. “Cov Expl.” = ( _F_ full _−_ _F_ diag) _/_ ( _F_ real _−_ _F_ diag).
Dataset _F_ real _F_ full _F_ diag Gap Cov Expl. Residual

...

_−_ 0.028 landmark dino 0.735 0.807 0.430 0.304 123.9% _−_ 0.073 random 0.907 0.899 0.560 0.348 97.7% +0.008

...

_†_ Low _R_ 2 due to
near-zero entropy variance (MAE is smallest); see text.
F.8 COORDINATE SIGN VS. RANDOM HYPERPLANE (PROBE 3)
Table 14: Pairwise overlap probabilities: coordinate sign BQ vs. random-hyperplane LSH. GW = Goemans–Williamson theoretical value 1 _−_ arccos(cos _θ_ ) _/π_ .

...

This appendix provides additional detail for the blind validation presented in Table 6 (main text, §8).
**Rotation response and sign entropy.** Across all 12 datasets with rotation data (Table 17), the sign entropy gap 1 _−_ _H_ sign is a far stronger predictor of ∆ _F_ rot than CV( _σ_ ):

...

0.041 +0.011 MiniLM 0.118 0.987 0.013 +0.004 Random 0.070 0.981 0.020 +0.000 Sphere 0.005 1.000 0.000 _−_ 0.000

...

The fidelity change is consistent with the scaling law ( _β_ 2 _<_ 0): amplifying variance dispersion increases std( _|_ SNR _|_ ) and lowers _F_ , while flattening decreases std( _|_ SNR _|_ ) and raises _F_ slightly.

...

50K samples and 10M pairs in Tables 4–10); abso- lute values differ slightly, but the relative trend across interventions is the quantity of interest.
Intervention CV( _σ_ ) std(SNR) log _r F_ 1bit _F_ 2bit ∆ _F_ mag

...

_ρ_ (CV _,_ ∆ _F_ mag) = +1 _._ 00 ( _p <_ 0 _._ 001)
I MEAN-FIELD CLOSURE (S0) FAILURE BOUNDARY
The scaling law (Proposition 6) relies on a mean-field dispersal assumption (S0) that decouples the off-diagonal correlation structure from the per-coordinate SNR ordering.

...

_ij_ _| ≈_ 0 _._ 05).
Table 19 summarizes the results.

...

GIST-960 (+0 _._ 60) and Arxiv-Nomic (+0 _._ 69) show elevated diagnostics, consistent with the scaling law’s higher prediction error on these datasets.