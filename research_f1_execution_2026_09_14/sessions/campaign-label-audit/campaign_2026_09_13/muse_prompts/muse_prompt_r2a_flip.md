# Muse session — R2A: per-question FLIP analysis (why does the top-48-variance arm lose?)

Fresh independent executor session. Read-only for /mnt/c; scratch in /tmp/r2a/. No network.
Python with numpy: `~/muse-work/ml-python` (numpy 2.5.3, python 3.14.4).

## Context

An exploratory pilot ("axis attack") on the frozen LongMemEval 470-question benchmark found that
selecting the top-48 variance axes loses ~10 pp retrieval vs a random 48-subset, despite winning
every mean-distance statistic. Your job: dissect that per question — WHICH questions flip, and
what distinguishes them.

## Inputs (all under /mnt/c/Users/MDP/dev/llmzip-work)

- matrices: `regen/lme/cache_repr/<qid>.pkl` (470; keys `C` (N,96) float64, `qC` (96,), `gold` (doc indices))
- stored per-question natives: `pilots/axis_attack_2026-09-12/pilot_results.json` → `per_question_native_FR`
- metadata: `drive/t4c3/V52_T4C3_question_level.csv` (columns: question_type, N_archive, gold_count,
  gold_stratum, archive_quartile, reuse_tertile, reuse_count, variance_cv, heterogeneity_quintile…)
- dataset for lex ordinals: `drive/longmemeval_s_cleaned.json`

## Frozen protocol (verbatim; must match exactly)

- `D=(C>=0)`, `Q=(qC>=0)`, `d=np.count_nonzero(D != Q[None,:], axis=1)` (int16)
- trials t=0..19: `prio = np.random.default_rng(5_100_000 + lex*100_000 + t*100 + 99).random(N)`;
  `lex` = ordinal of qid in `sorted()` of ALL 500 dataset qids
- `order = np.lexsort((prio, d))`; top3 = order[:3]; fractional = |top3 ∩ gold| / |gold|;
  per-question value = mean over 20 trials.

## Tasks

1. **Self-gate.** For all 470 questions compute per-q FR for: `TOP48` (per-archive top-48 variance
   axes), `RAND48_s0` (`np.random.default_rng(12000).choice(96,48,replace=False)` — same subset for
   all questions), `BOT48` (bottom-48 variance). Aggregates must match the pilot:
   TOP48 = 0.34949468085106383, RAND48_s0 = 0.47292553191489356, BOT48 = 0.4284574468085106
   (report exact diffs; investigate anything > 1e-12).
2. **Tie metrics** for TOP48 and RAND48_s0, per question (mean over the 20 trials):
   (a) gold rank (min over golds of position in `order`);
   (b) count of docs strictly closer than the gold;
   (c) tie-cluster size at the gold's distance (docs with d == d_gold);
   (d) top-3 boundary tie indicator (docs at the 3rd-smallest distance exceed remaining slots).
3. **Flip analysis.** Join metadata; report:
   - W/T/L of TOP48 vs RAND48_s0 (gap = TOP48 − RAND48_s0, tol 1e-12) overall AND per
     `question_type` (sorted by mean gap), with mean/median gap per type.
   - Pearson correlations of per-q gap with: N_archive, gold_count, RAND48_s0 gold rank,
     TOP48 tie-cluster size, TOP48 dup fraction (unique-code fraction complement).
   - 10 largest losers + 5 largest winners (qid, type, N_archive, gap).
4. **Outputs.** Save `/tmp/r2a/per_q.json` (all per-question arrays) and PRINT to stdout:
   the gate diffs, the per-type table, the correlations, the winner/loser lists, and a compact
   final JSON block with all of the above. Also print the file size of per_q.json.

Report honestly; if anything fails to reproduce, state it exactly. No writes under /mnt/c.
