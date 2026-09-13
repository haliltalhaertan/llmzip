# D2X (MISSING-2) — D2 multi-split robustness + fully gold-free tie model (c2 premise)

**[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

Frozen protocol verbatim from D2 (lexsort tie priorities, 20 trials, fractional R@3); numpy only; no network. Read-only on /mnt/c; all writes under /tmp/d2x/.

## 0. Gate (D2 single-split reproduction, sha256("c1|"+qid) parity)

Recomputed AUC(T)=0.7985 (expected 0.798, tol 0.002), AUC(M)=0.6864 (expected 0.686, tol 0.002); binary train n=161 (wins 54), test n=130 (wins 37) — identical to D2 (161/54, 130/37).

**Gate PASS — D2 machinery replicated.**

## 1. Multi-split stability (10 salted splits, s=0..9; held-out = test AUC)

| Model | Mean | SD | Min | Max | Splits detail |
|---|---|---|---|---|---|
| T | 0.821 | 0.020 | 0.782 | 0.856 | 0.812, 0.856, 0.813, 0.806, 0.820, 0.825, 0.782, 0.835, 0.835, 0.826 |
| M | 0.659 | 0.043 | 0.585 | 0.720 | 0.614, 0.706, 0.625, 0.668, 0.700, 0.720, 0.585, 0.664, 0.649, 0.657 |
| TM | 0.800 | 0.034 | 0.757 | 0.854 | 0.770, 0.854, 0.757, 0.783, 0.824, 0.830, 0.758, 0.825, 0.817, 0.781 |
| G | 0.555 | 0.043 | 0.474 | 0.614 | 0.594, 0.590, 0.510, 0.532, 0.574, 0.532, 0.574, 0.614, 0.560, 0.474 |
| GT | 0.783 | 0.044 | 0.713 | 0.852 | 0.812, 0.852, 0.713, 0.756, 0.818, 0.767, 0.792, 0.818, 0.772, 0.728 |
| GM | 0.639 | 0.041 | 0.572 | 0.713 | 0.620, 0.713, 0.594, 0.638, 0.683, 0.635, 0.625, 0.659, 0.655, 0.572 |

T-M delta per split: +0.199, +0.150, +0.188, +0.138, +0.120, +0.106, +0.197, +0.171, +0.186, +0.169.
Delta distribution: mean=+0.162, sd=0.033, range=[+0.106,+0.199], fraction of splits with delta>=0.05: 100.0% (10/10).
Binary n per split (train/test): 0:157/134; 1:162/129; 2:147/144; 3:135/156; 4:143/148; 5:156/135; 6:152/139; 7:141/150; 8:131/160; 9:147/144; wins per split train: 51, 47, 44, 38, 46, 46, 48, 44, 34, 48; test: 40, 44, 47, 53, 45, 45, 43, 47, 57, 43.
Bootstrap (two-stage: resample 10 splits w/ replacement, then resample each split's test binary questions w/ replacement and recompute AUCs from stored fitted scores; B=5000, seed 7): mean AUC(T) 95% CI=[0.796, 0.845]; mean(T-M) 95% CI=[+0.126, +0.199].

## 2. Fully gold-free model G (10 features, no gold at train or inference)

Held-out AUC(G) per split: 0.594, 0.590, 0.510, 0.532, 0.574, 0.532, 0.574, 0.614, 0.560, 0.474; mean=0.555, sd=0.043, range=[0.474, 0.614]; splits above kill-bar 0.65: 0/10.
Context: mean AUC(GT)=0.783, mean AUC(GM)=0.639.
Standardized G coefficients across splits (mean +/- sd; + favors win): margin34=+0.229+/-0.201; crowd3=+0.067+/-0.259; crowd4=+0.086+/-0.258; crowd_pm1=-0.125+/-0.221; top3_tie_share=-0.216+/-0.197; boundary_share=+0.001+/-0.134; dup_top20=-0.063+/-0.236; var_decay=-0.103+/-0.108; N=-0.294+/-0.119; qent=-0.119+/-0.071; bias=-0.911+/-0.123.
Signal carriers (|mean| largest): N (-0.294), margin34 (+0.229), top3_tie_share (-0.216), crowd_pm1 (-0.125).
Declared overlaps: margin34 is EXACTLY D2 margin (same trial-0 s[3]-s[2]); boundary_share=crowd_pm1/N (count vs share pair, L2 absorbs); GT dedups margin34.

## 3. Verdict

AUC(T) across splits: mean=0.821 (D2 single-split 0.798); Delta(T-M): mean=+0.162 (D2 +0.112), frac>=0.05=100%; gold-free AUC(G): mean=0.555, 0/10 splits >0.65.

## 4. Honesty: what this cannot show

- Single benchmark (LME-470), one learner (IRLS logistic, L2=1.0), one target definition (binary loss-vs-win EXCLUDING ties: per-split binary test n≈129-160 only; ties carry no flip direction).
- 10 salted hash splits of the SAME 470 questions: split-to-split variation only, no new data; bootstrap CI reflects resampling, not population sampling.
- G is gold-free at inference but built on the TOP48-variance arm (unsupervised) and validated on the same flip target that T/M were tuned against; margin34 duplicates D2 margin.
- AUC differences near +/-0.03 are noise-scale at this n; G vs M gaps must be read with that ruler.
- Correlation/description only: no causal claim; mechanism stays OPEN. Verdict is LOCAL EXPLORATORY, not preregistered, not for citation.