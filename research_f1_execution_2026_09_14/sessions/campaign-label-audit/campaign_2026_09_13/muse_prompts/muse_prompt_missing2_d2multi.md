# Muse session — MISSING-2: D2 multi-split robustness + fully-GOLD-FREE tie model (c2 premise)

You are an independent analyst. Implement + run in /tmp/d2x/; report [LOCAL EXPLORATORY]
[NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]. Read-only on /mnt/c; no network.
Numpy only (IRLS logistic as in D2). Context: D5's missing-analysis list says this "determines
whether the tie story survives without gold across splits — the direct premise of c2".

## Read first

- /mnt/c/Users/MDP/dev/llmzip-work/pilots/axis_attack_2026-09-12/round3/muse_sessions/d2/d2_report.md
  + d2.py + d2_details.json (the round-3 tie-mass analysis; replicate its machinery VERBATIM:
  TOP48/BOT48 per-archive variance convention; RAND48 seeds 12000/12001/12002; delta =
  FR(TOP48) − mean(FR RAND48); binary target loss-vs-win excluding ties; IRLS logistic,
  train-standardized, L2=1.0; AUC by rank statistic).
- Frozen protocol: pkls at regen/lme/cache_repr/<qid>.pkl; lex ordinals over the 500 dataset qids
  (drive/longmemeval_s_cleaned.json); tie priorities rng(5_100_000 + lx*100_000 + t*100 + 99),
  20 trials, top-3, fractional; stored natives from per_axis_matrices.npz/pilot_results.json.

## Gate (abort if fail)

Reproduce D2's single-split numbers on its split rule (sha256('c1|'+qid) parity):
AUC(T)=0.798, AUC(M)=0.686 (tol 0.002) and the same n (binary train/test counts).

## Tasks

1. **Multi-split stability.** 10 salted splits: train iff first hex of sha256(f'c1s|{s}|'+qid)
   is even (s=0..9). Per split refit T (D2's 3 tie features), M (4 mean features), T∪M, and
   record held-out AUC; report mean/sd/range per model and the T−M delta distribution
   (mean, sd, fraction of splits with delta ≥ 0.05). Bootstrap CI for mean AUC(T) and mean
   (T−M) across splits (resample splits then questions; state method).
2. **Fully gold-free model G.** Features allowed (all gold-free): margin34 (d4−d3, small arm),
   crowd3 (#docs at d3), crowd4 (#docs at d4), crowd_pm1 (docs within ±1 of d3), top3_tie_share,
   boundary_share, dup_top20 (1 − distinct/20 among top-20 full codes), var_decay (top16/top48
   variance share), N (archive size), qent (query sign-entropy). Fit G on train, report held-out
   AUC per split + mean; also G∪T and G∪M for context. State which features carry the signal
   (standardized coefficients).
3. **Verdict to record:** does AUC(T)≈0.8 / Δ(T−M)≈+0.11 hold across splits; does a strictly
   gold-free model clear a majority of splits above 0.65 (the roadmap kill-bar)? Honest either way.

## Output

/tmp/d2x/d2x_report.md + /tmp/d2x/d2x_details.json + d2x.py; stdout ends with
D2X_VERDICT: <one line: tie story across splits; gold-free AUC mean; does it clear 0.65>.
Label all numbers; include an honesty section (single benchmark, one learner, target definition,
n sizes). ~1-2 hours scale; mirror D2 machinery; do not modify anything under /mnt/c.
