# Muse session — INDEPENDENT RECOMPUTATION of the axis-attack pilot key numbers

You are a fresh independent executor. Recompute the key numbers of a local pilot from the raw
matrices yourself, using the frozen evaluation protocol, and compare against the pilot outputs.
Do not read any other session's scratch; work read-only (scratch in /tmp/pilotverify/).

## Context

A local pilot ("axis attack" on the frozen LongMemEval 470 question benchmark) computed exploratory
retrieval outcomes. Its script and results:

- script:  /mnt/c/Users/MDP/dev/llmzip-work/pilots/axis_attack_2026-09-12/pilot_axis_attack.py
- results: /mnt/c/Users/MDP/dev/llmzip-work/pilots/axis_attack_2026-09-12/pilot_results.json
- matrices: /mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/<qid>.pkl  (keys: C (N,96) float64,
            qC (96,), gold (indices))
- frozen reference CSV: /mnt/c/Users/MDP/dev/llmzip-work/drive/t4c3/V52_T4C3_question_level.csv
- dataset (for lex ordinals): /mnt/c/Users/MDP/dev/llmzip-work/drive/longmemeval_s_cleaned.json

**Frozen evaluation protocol (must be replicated exactly):**
- codes: `D = (C >= 0)`, `Q = (qC >= 0)`; distance `d = count_nonzero(D != Q, axis=1)` (int16)
- tie priorities: for t in 0..19: `rng = default_rng(5_100_000 + lex*100_000 + t*100 + 99)`,
  `prio = rng.random(N)`; lex = ordinal of question_id in `sorted()` of ALL qids in the dataset
- ranking: `np.lexsort((prio, d))`; top-3 = first 3; metric "Fractional" = |top3 ∩ gold| / |gold|
- per-question value = mean over the 20 trials; aggregate = mean over questions (equal weight)
- published gate value: native Fractional R@3 = 0.5419751773049646

Note: `numpy.random.default_rng` (PCG64) bit-streams and integer distances are version-stable, so
exact reproduction is expected even cross-stack; report any difference verbatim.

## Environment

`~/muse-work/ml-python` has numpy 2.5.3 (python 3.14.4). System python3 also works if numpy exists.

## Tasks (report each: RECOMPUTED value, PILOT value, delta, verdict EXACT/CLOSE/DIFFERS)

1. **E0 gate — full 470.** Recompute per-question native Fractional R@3 (frozen protocol) for all
   470 pkls; verify (a) aggregate == 0.5419751773049646; (b) per-question values == the frozen
   `native_fractional_r3` column in V52_T4C3_question_level.csv (max abs diff);
   (c) aggregate ANY_R3 == 0.7130851063829787 and ALL_R3 == 0.38457446808510637.

2. **E1 budget curve spot checks.** Recompute top-k-variance-prefix FR for k in {16, 32, 64}
   (per question: `idx = argsort(var, kind="stable")[::-1][:k]`, var = C.var(axis=0); codes and
   protocol as above) → aggregate; compare to `E1_budget_curve_topk_variance` in the pilot JSON.
   Also recompute the random-subset arms: k=48 seed 12000 → compare to `E1_random_subset["48"]`;
   k=32 seed 12000 and k=64 seed 12000 → compare to `extra_arms.json` keys "RAND32_s0"/"RAND64_s0";
   and the bottom-48 arm (`argsort(var)[:48]`) → `E1_bottomk_variance["48"]`.

3. **E2 spot checks.** For axes j in {0, 47, 95}: recompute (a) "alone" FR (1-bit code, only axis j)
   and (b) "drop" FR (96-bit code minus axis j) — aggregates over 470. Compare to `per_axis.csv`
   (alone_FR_mean, drop_FR_mean for those j).

4. **E4 spot check.** For rotation seed 43001, block size 2 only: replicate the frozen block-mixing
   construction (same rng draw order: `perm = rng.permutation(96)`; then per block of 2:
   `Q,R = qr(rng.standard_normal((2,2)))`, sign-correct with `diag(R)`; first permute axes by
   `perm`, then rotate each block) → FR → gap vs native in pp. Compare both (a) to the pilot's
   `E4_block2.random_pairing_gap_pp["43001"]` and (b) to the FROZEN value -3.4844 pp.
   Then the matched-variance arm for the same seed: identical rotations but axes ordered by
   ascending variance (`argsort(C.var(axis=0), kind="stable")`) before block rotation; compare to
   `E4_block2.matched_variance_gap_pp["43001"]`.

5. **Diagnostics spot checks.** The pilot also saved `diagnostics.json` and `diagnostics2.json`
   (in the same dir) with per-axis-set statistics. For a FIXED deterministic sample of 25
   questions (e.g. the 25 pkls whose filenames sort first), recompute for the three sets
   {TOP48 = top-48 variance axes, RAND48_s0 = `default_rng(12000).choice(96,48,replace=False)`,
   BOT48 = bottom-48 variance axes}: (a) duplicate-code fraction of the archive; (b) top-3
   boundary tie indicator; (c) mean pairwise |phi| between the set's axes; (d) mean gold rank
   over the 20 trials. Compare the sample means to the corresponding full-470 values in
   diagnostics.json / diagnostics2.json (expect close, not exact — sample vs full). State the
   comparison numerically.

## Report format

Per task: RECOMPUTED / PILOT / delta / verdict, then a final table and one-paragraph verdict:
"pilot numbers independently reproduced: yes/no/partially" + any deviation details. Read-only;
no repo writes; no network. Do not modify anything under /mnt/c.
