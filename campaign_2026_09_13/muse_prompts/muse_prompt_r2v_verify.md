# Muse session — R2V: INDEPENDENT RECOMPUTATION of round-2 headline numbers

Fresh independent executor. Read-only for /mnt/c; scratch /tmp/r2v/. No network.
Python with numpy: `~/muse-work/ml-python`. Do NOT read other sessions' scratch (`/tmp/r2a|r2b|r2c`)
— recompute from the raw inputs and the frozen protocol sources only.

## Round-2 outputs to verify (read for the CLAIMS; recompute independently)

- reports: `/mnt/c/Users/MDP/dev/llmzip-work/pilots/axis_attack_2026-09-12/round2/r2a_flip_analysis.md`,
  `r2b_learned_selection.md`, `r2c_loco_replication.md`
- details: same dir `wsl_details/r2a_per_q.json`, `r2b_details.json`, `r2c_details.json`

## Raw inputs

- LME matrices: `/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/<qid>.pkl` (keys C, qC, gold)
- LME per-axis matrices: `.../pilots/axis_attack_2026-09-12/per_axis_matrices.npz`
  (alone, drop, delta, goldrate, var_rank, qids)
- LME per-q natives: `.../pilots/axis_attack_2026-09-12/pilot_results.json` → per_question_native_FR
- LME dataset (lex): `.../drive/longmemeval_s_cleaned.json`
- LoCoMo matrices: `.../regen/locomo/locomo_0..9.pkl` (keys conv_id, C, QC, qas, id_to_row)
- LoCoMo frozen protocol source: `.../drive/v52_t4d_locomo_frozen_cross_benchmark.py`
- LoCoMo raw+audit: `.../drive/locomo10.json`, `.../drive/audit_layer/`

## Frozen LME protocol (verbatim)

codes `D=(C>=0)`, `Q=(qC>=0)`; `d=count_nonzero(D!=Q,axis=1)`; trials t=0..19 with
`prio=default_rng(5_100_000+lex*100_000+t*100+99).random(N)`, lex = ordinal in sorted 500 qids;
`order=lexsort((prio,d))`; fractional=|order[:3]∩gold|/|gold|; per-q mean over trials.

## Tasks (report RECOMPUTED vs CLAIMED vs delta per item)

1. **R2B drop64 (the headline).** Recompute from scratch:
   (a) split: train = qids with even first hex of `sha256(qid.encode()).hexdigest()` (expect 239/231);
   (b) `U_drop[j] = mean over train of (nat_q − drop[q,j])` using the npz `drop` matrix and the
   stored natives — recompute the top-64 axes (claim: top-5 = [23,72,88,2,58]);
   (c) test-set FR for that top-64 selection (claim: 0.4837806638) and for RANDOM64 seeds
   12000/12001/12002 (claims: 0.4342 / 0.4676 / 0.4477); (d) W/T/L of drop64 vs RANDOM64-mean on
   test (claim: 63/124/44, tol 1e-12).
   For (c) you may use the npz `drop`/pkls as needed — but recompute distances from the pkls.
2. **R2A flip aggregate.** Recompute overall W/T/L TOP48 vs RAND48_s0 (claim: 63/250/157, mean gap
   −0.12343085106382978) and the `single-session-user` row (claim: n=64, 3/36/25, mean −0.300391).
3. **R2C LoCoMo.** Extract the protocol from the T4D script yourself (do NOT trust r2c details as
   spec) and recompute: (a) the GATE: native fractional R@3 = 0.23654714666441054 (report exact
   diff); (b) the block-2 MATCHED mean (claim .236101, gaps −0.09/−0.63/+0.59 per seeds
   43001/2/3) and ANTIMATCHED mean (claim .193715, −3.75/−5.38/−3.72); (c) one budget cell: k=48
   BOT = 0.181122 (gap −5.54).
4. **Spot-check one per-question value** from R2A's `wsl_details/r2a_per_q.json` (e.g. the loser
   `001be529`: claim TOP48 rank 18.2/cluster 11 vs RAND rank 0.0/cluster 1.0) — recompute from the
   pkl directly.

## Report format

Per item: RECOMPUTED / CLAIMED / delta / verdict EXACT|CLOSE|DIFFERS (+ notes). End with a summary
table and a one-paragraph verdict: "round-2 numbers independently reproduced: yes/no/partially" +
any deviation verbatim. Read-only; no /mnt/c writes; no network.
