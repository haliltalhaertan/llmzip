# Muse session — MISSING-3: c2 ablation package (LARGE-free + gain CIs + formal vs-random)

You are an independent analyst. Implement + run in /tmp/c2x/; report [LOCAL EXPLORATORY]
[NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]. Read-only on /mnt/c; no network.
Numpy only. Context: D5's missing-analysis list REQUIRES these three before any c2
preregistration; c2's LoCoMo leg was vacuous vs random-abstention and its gains depend on
features that require the full budget to compute.

## Read first

- /mnt/c/Users/MDP/dev/llmzip-work/pilots/axis_attack_2026-09-12/round3/muse_sessions/c2/c2_report.md
  + c2.py + c2_details.json (replicate machinery VERBATIM: SMALL=SPREAD48 repaired rank-linspace,
  LARGE=NATIVE96, split sha256('c2|'+qid) parity, logistic IRLS, routing gain(α) with abstain-top-α
  predicted-fail → LARGE, random-abstention baselines).

## Gate (abort if fail)

Reproduce c2's numbers to tolerance: LME gain@0.20 = +3.086pp, LoCoMo +1.481pp; random-abstention
means +1.833 / +1.135; COMBO test AUCs 0.686 / 0.558. (Tol 0.005pp / 0.002 AUC.)

## Tasks (exactly the three D5 items)

1. **LARGE-free ablation.** Refit the predictor WITHOUT any feature derived from the full-budget
   (LARGE) pass — i.e., drop margin34_large and crowd3_large (any other LARGE-derived features
   too; audit the feature list and state it). Report: AUC (LME/LoCoMo), gain@α=0.20 (LME/LoCoMo),
   and which features remain (standardized coefficients). This answers: can the ROUTER work
   without first paying for the full budget?
2. **Gain CIs.** Paired bootstrap over test questions (B=2000) for gain@0.20 of the retained
   model, LME + LoCoMo; report 90% CI. Also for the LARGE-free variant.
3. **Formal vs-random test.** Generate 200 random-abstention draws (same α scheme, same seeds
   protocol) for each benchmark; model's gain percentile/p-value per α∈{0.10,0.20,0.30,0.40};
   state multiplicity handling (e.g. Bonferroni across the 4 α's per benchmark). Verdict per
   benchmark+α: beats-random / inside-noise.

## Output

/tmp/c2x/c2x_report.md + /tmp/c2x/c2x_details.json + c2x.py; stdout ends with
C2X_VERDICT: <LARGE-free AUC & gain per benchmark; CIs; vs-random verdict per α; is c2
prereg-ready (with what binding gate)>. Include honesty section (n, learner, features).
~1-2 hours scale; do not modify anything under /mnt/c.
