# Muse session — DENEY 5 (c2): gold-free failure predictor → adaptive budget routing

You are an independent analyst. Implement + run in /tmp/c2/; report [LOCAL EXPLORATORY]
[NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]. Read-only on /mnt/c; no network.
Numpy only (logistic via IRLS; AUC by rank statistic). Context: D2 (deney2, ties) cleared its AUC
gate (T=0.798 held-out, gold-informed features — the mechanism is "tie competition at the gold
distance, not mean distance"). This session tests the GOLD-FREE version: can we PREDICT which
questions fail at a small budget (and would succeed at the full budget) using only gold-free
features, and does selective budget routing buy measurable FR — beyond random abstention?

## Frozen materials

- LME: pkls regen/lme/cache_repr/<qid>.pkl (C, qC, gold); tie protocol as always
  (priorities 5_100_000+lx*100_000+t*100+99, 20 trials, top-3, fractional). Native anchor
  0.5419751773049645. qids list: pilots/axis_attack_2026-09-12/per_axis_matrices.npz['qids'].
- LoCoMo: regen/locomo/locomo_<ci>.pkl + audit corrections (mirror r2c_replicate.py verbatim:
  stable_archive_seed(ci,t)+99, valid=1535, anchor 0.23654714666441054).
- Arm definitions (fixed, construction equals round3 deney1):
  SMALL = SPREAD48 on the repaired rank-linspace (order = descending train... use FULL-data
  variance ordering for this analysis; note: variance is gold-free so full-data ordering is fine;
  cols = order_desc[round(linspace(0,95,48))]); LARGE = NATIVE96 (all axes).
  Secondary: SMALL2 = SPREAD64 (8B). Declare exactly.
- Split: train iff first hex char of sha256('c2|'+qid) even; STRATIFY identical to before is not
  required; declare and report counts. (LME 470; LoCoMo 1535 separately.)

## Per-question quantities

1. FR_small, FR_large (fractional R@3, both arms) — labels.
2. Failure label: fail iff FR_small < FR_large − 1e-12 (small strictly worse). Report base rates.
3. GOLD-FREE features (no gold; computed from small-arm geometry + archive stats only):
   - margin34 = d(4th) − d(3rd) (trial-0 ordering of small arm); crowd3 = #docs at d3;
     crowd4 = #docs at d4; crowd_pm1 = #docs within ±1 of d3.
   - top3_tie_share = crowd3 / N; boundary_share = (crowd3+crowd4)/N.
   - dup_top20 = 1 − (#distinct full codes among top-20)/20 (small arm).
   - var_decay = sum(largest 16 var)/sum(largest 48 var) (archive variance only).
   - N = archive size; qent = sign-entropy of qC (query only).
   - ALSO the LARGE-arm margin34_large, crowd3_large (geometry of the full budget).
4. Model: logistic (IRLS, train-standardized, L2=1.0) on features → P(fail). Report train/test
   AUC per feature and for the combo (LME and LoCoMo).
5. Selective routing evaluation (test split only): abstention rate α in {0.10,0.20,0.30,0.40};
   route top-α by predicted fail to LARGE, rest use SMALL. Gain(α) = mean FR(routed) − mean
   FR(SMALL alone). Baselines: random abstention (10 draws, report mean/range), oracle
   abstention (top-α true fails), and constant-routing sanity. Report gain curves in pp.
6. PRE-DECLARED promote gate (from the roadmap): promote to a preregistered adaptive
   experiment ONLY if gain ≥ +1.0pp at α=0.20 on held-out AND replicates on LoCoMo (same
   sign, ≥ +0.5pp). Otherwise the null is the mechanism result: state it plainly.

## Gates (abort on fail)

Native anchors reproduce (LME 0.5419751773049645; LoCoMo 0.23654714666441054) ≤1e-12; SMALL arm
mean matches round3 replays: LME SPREAD48 mean over all-470 — recompute; sanity check vs
round3 splits (mean over splits ≈ 0.46-0.47); LoCoMo SPREAD48 similar. Also spot check
dup/variance features for NaN-freeness.

## Output

/tmp/c2/c2_report.md + /tmp/c2/c2_details.json + c2.py; stdout ends with
C2_VERDICT: <gain@0.20 LME, gain@0.20 LoCoMo, vs random-abstain, promote/kill>.
Include an honesty section (single learner, n sizes, feature-set choice, "no causal claim").
~1-2 hours scale. Mirror machines from round2/session_scripts and round3 scripts; do not modify
anything under /mnt/c.
