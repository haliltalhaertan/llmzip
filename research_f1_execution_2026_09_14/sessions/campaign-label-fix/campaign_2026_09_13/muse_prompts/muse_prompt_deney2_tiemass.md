# Muse session — DENEY 2 (c1): tie-mass decomposition + flip predictor (LME)

You are an independent analyst. Read the pointers, implement the analysis below in /tmp/d2/,
run it, and report [LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE].
Read-only elsewhere. No network (flag lit-checks). numpy only (no sklearn needed; implement AUC by
rank statistics yourself or use a tiny logistic fit via numpy).

## Context (frozen, verified)

- Per-question frozen matrices: /mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/<qid>.pkl
  with keys C (n_docs x 96), qC (96,), gold (rows). 470 questions.
- Frozen tie protocol (identical to the pilots): for question qid let lx = lexicographic ordinal
  of qid over ALL 500 dataset qids (sorted list of question_id in
  /mnt/c/Users/MDP/dev/llmzip-work/drive/longmemeval_s_cleaned.json). Priorities for trial t:
  np.random.default_rng(5_100_000 + lx*100_000 + t*100 + 99).random(n). 20 trials. Per trial:
  order = np.lexsort((p, d)); top-3; fractional = |top3 ∩ gold|/|gold|; question value = mean
  over 20 trials. Native anchor: mean over 470 = 0.5419751773049645 (reproduce as gate,
  tolerance 1e-12).
- Flips observed (pilot R2A, one seed): TOP48 loses to RAND48 badly, W/T/L 63/250/157 on 470,
  mean gap -12.34 pp; mean-distance statistics point the WRONG way ("separation paradox").
- Read for arm definitions + previous context: /mnt/c/Users/MDP/dev/llmzip-work/pilots/
  axis_attack_2026-09-12/REPORT.md (E1/E2 sections), round2/ROUND2_REPORT.md, and r2a machinery
  in round2/session_scripts/r2a.py.

## Arms (mirror the pilots' definitions)

- TOP48 / BOT48: per-archive variance ordering exactly as RTD/E2 did (read REPORT.md; mirrors
  R2C's `np.argsort(var)` convention).
- RAND48: three fixed seeds 12000/12001/12002 (same as pilot).
- drop64: top-64 axes by full-data drop utility (U_drop = mean over 470 of (native − FR with
  axis a removed); native = stored per-question native FRs from
  pilots/axis_attack_2026-09-12/pilot_results.json, key per_question_native_FR). Declare as
  gold-informed analysis-only.

## Gates (abort if fail)

1. Native recompute = 0.5419751773049645 (<=1e-12).
2. TOP48 = 0.34949468085106383, RAND48_s0 = 0.47292553191489356, BOT48 = 0.4284574468085106
   (all <=1e-12 after recompute; these are pilot-frozen aggregates).

## Features (per question; compute for each arm)

Using the full distance vector d (Hamming, all n docs; sign convention C>=0, qC>=0):
- d_gold = mean Hamming distance of gold rows (if multiple golds, mean; also record min).
- tie_mass_at_dgold = # docs with distance exactly == round(d_gold) for the nearest gold
  (use nearest gold's exact integer distance; if golds multiple, use min-distance gold).
- tie_mass_pm1 = # docs at d_gold−1 and at d_gold+1.
- gold_bucket_size = size of the set of docs sharing the nearest gold's EXACT code (all-96 bits)
  — duplicate-code bucket.
- margin = d(4th ranked) − d(3rd ranked) under the trial-averaged rank (use trial 0's ordering
  or a mean over trials; declare choice) — top-3 boundary margin.
- strictly_closer_than_gold = # docs with distance < d_gold_min.
- top20_entropy = entropy of the distance histogram of the 20 nearest docs (trial 0 / mean).
- mean_nongold = mean distance of non-gold docs; min_nongold = min distance of non-gold docs.

## Flip target + models

- Target: per question, delta = FR(TOP48) − mean FR(RAND48 seeds); flip = TOP beats RAND.
  Define as: win iff delta > 1e-12, tie iff |delta| <= 1e-12, loss iff < -1e-12. Primary binary
  target: loss-vs-win (exclude ties) — or ordinal; declare and justify; n≈470.
- Split: train iff first hex char of sha256('c1|'+qid) is even (declare; ~235/235).
- Model T (tie features): logistic regression on {tie_mass_at_dgold, margin, strictly_closer_
  than_gold} (2-3 features; standardize; numpy gradient descent or IRLS; include bias).
- Model M (mean stats): logistic on {d_gold, mean_nongold, min_nongold(clipped), top20_entropy}.
- Report held-out AUC for T, M, and T∪M. Decision reference (from the roadmap): if AUC(T) < 0.65
  or AUC(T) − AUC(M) < 0.05 → the tie story stays descriptive; no predictor claim. Report
  honestly either way. Also report which features dominate (standardized coefficients) and a
  per-arm feature table (means for wins vs losses).

## Deliverables

- /tmp/d2/d2_report.md (findings; gates; AUC table; feature table; honesty section on what this
  cannot show) + /tmp/d2/d2_details.json (all per-question features + per-arm FRs + model
  outputs). Print the key numbers to stdout at the end (BEGIN/END markers). ~1-2 hours scale.
