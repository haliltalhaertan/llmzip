# Muse session — R2B: train/test-split LEARNED axis selection (LME)

Fresh independent executor. Read-only for /mnt/c; scratch /tmp/r2b/. No network.
Python with numpy: `~/muse-work/ml-python`.

## Context

An exploratory pilot found that selecting the top-48 variance axes is much worse than a random
48-subset, while every axis carries some weak gold signal. Your job: test whether a *learned*
axis ranking (from a TRAIN half of the questions) can beat random/spread selection on a held-out
TEST half. This is the pilot's #1 proposed next experiment; keep it exploratory in labeling.

## Inputs (all under /mnt/c/Users/MDP/dev/llmzip-work)

- per-question per-axis matrices: `pilots/axis_attack_2026-09-12/per_axis_matrices.npz`
  keys: `alone` (470,96), `drop` (470,96), `delta` (470,96), `goldrate` (470,96),
  `var_rank` (470,96 int16; 0 = highest variance), `qids` (array of 470 qid strings)
- per-q natives: `pilots/axis_attack_2026-09-12/pilot_results.json` → `per_question_native_FR`
- matrices: `regen/lme/cache_repr/<qid>.pkl` (keys C, qC, gold) — for the pool term and for the
  test-set FR computations
- dataset for lex ordinals: `drive/longmemeval_s_cleaned.json`
- metadata: `drive/t4c3/V52_T4C3_question_level.csv` (question_type etc.)

## Frozen protocol (verbatim)

- `D=(C>=0)`, `Q=(qC>=0)`, `d=np.count_nonzero(D != Q[None,:], axis=1)`
- trials: `prio_t = default_rng(5_100_000 + lex*100_000 + t*100 + 99).random(N)`, t=0..19;
  lex = ordinal of qid in sorted(all 500 dataset qids)
- `order = lexsort((prio, d))`; fractional = |order[:3] ∩ gold| / |gold|; per-q = mean over trials.

## Design (deterministic, reproducible)

1. **Split:** `train` if first hex char of `sha256(qid.encode()).hexdigest()` is even, else `test`.
   Report counts + question_type balance across halves (acceptable if roughly balanced; report it).
2. **Train utilities** (per axis j; TRAIN questions only):
   - `U_delta[j] = mean over train q of delta[q,j]`
   - `U_drop[j]  = mean over train q of (nat_q − drop[q,j])`  (nat from per_question_native_FR)
   - `U_alone[j] = mean over train q of alone[q,j] * pool[q,j] / 3`, where
     `pool[q,j] = #docs with D==Q on axis j` (compute from the pkls)
   - `U_var[j]   = mean over train q of (−var_rank[q,j])`  (control: prefers high variance)
3. **Arms** (each = one fixed global axis set, applied to every TEST question):
   for k in {32, 48, 64}: selection = `argsort(U)[::-1][:k]` for each U ∈ {delta, drop, alone, var}.
   Controls: `RANDOM` (seeds 12000, 12001, 12002 → `default_rng(s).choice(96,k,replace=False)`),
   `SPREAD` (rank-stride: `rank_desc[::2][:k]` with per-question variance ordering — note this one
   is per-question), `NATIVE96` reference (test mean of stored per-q natives).
4. **Evaluate:** test-set FR (frozen protocol) for every arm; ALSO train-set FR per arm
   (in-sample) to expose the overfit gap. Report W/T/L (tol 1e-12) of the best learned arm vs
   RANDOM-mean on test.
5. **Outputs:** print a full table (arm × {train FR, test FR, gap-vs-random pp}) and a final JSON
   block with every number; save details to /tmp/r2b/details.json and print its size.

Report honestly; if any gate/sanity number is off (e.g., test-set native mean vs stored), state it
exactly. No writes under /mnt/c.
