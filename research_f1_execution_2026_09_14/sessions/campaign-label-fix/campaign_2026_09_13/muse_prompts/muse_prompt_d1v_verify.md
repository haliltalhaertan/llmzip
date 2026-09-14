# Muse session — D1V: INDEPENDENT RECOMPUTE of Deney 1 (round3) numbers

You are an independent verifier. Recompute the flagged numbers FROM RAW ARTIFACTS; do not trust
stored values. Read-only on /mnt/c; write only /tmp/d1v/. No network. Report [VERIFICATION]
[READ-ONLY EVIDENCE]. Goal: every check labelled EXACT or DIFF with numbers; a "cannot check"
list at the end.

## Materials

- Scripts (read to understand exact rules; do NOT execute their outputs as authority):
  /mnt/c/Users/MDP/dev/llmzip-work/harness/deney1_lme.py, harness/deney1_loco.py
- LME raw: pilots/axis_attack_2026-09-12/per_axis_matrices.npz (alone/drop/delta/var_rank, 470x96;
  qids); regen/lme/cache_repr/<qid>.pkl (C, qC, gold); drive/t4c3/V52_T4C3_question_level.csv
  (question_type); drive/longmemeval_s_cleaned.json (for lex ordinals over 500 qids);
  pilots/axis_attack_2026-09-12/pilot_results.json (per_question_native_FR).
- LME results: pilots/axis_attack_2026-09-12/round3/deney1_lme_details.json
- LoCoMo raw: regen/locomo/locomo_<ci>.pkl; drive/locomo10.json; drive/audit_layer/errors_conv_*.json;
  round3/deney1_loco_peraxis.npz; round3/deney1_loco_details.json
- Tie protocol: priorities = np.random.default_rng(5_100_000 + lex*100_000 + t*100 + 99).random(n),
  20 trials, order = np.lexsort((p, d)), top-3, fractional R@3. LoCoMo: priorities =
  default_rng(stable_archive_seed(ci,t)+99).random(N) with stable_archive_seed = 5_100_000 +
  ci*100_000 + t*100 (see r2c_replicate.py). Sign convention C>=0, qC>=0.

## Checks (all on LME unless stated)

1. Split reconstruction: split s uses sha256(f'deney1|{s}|{qid}') dealt alternately within each
   question_type (sort by digest; even->train). For s=0 and s=7 verify the stored train_qids/
   test_qids lists match your reconstruction; disjoint+complete.
2. Utility recompute (s=0, s=7): from raw npz + stored natives compute U_drop = mean_train(native −
   drop_a), U_alone = mean_train(alone*pool/3) [pool computed from pkls], U_var = mean_train(−var_rank);
   verify the top-64 cols equal the stored arms['drop64'/'alone64'/'var64'].cols exactly.
3. SPREAD64 cols (s=0): verify = order_desc[round(linspace(0,95,64))], order_desc = argsort(U_var)[::-1];
   compare with stored SPREAD64 cols.
4. Random cols: RANDOM64_s91000 for s=0: verify = sorted(default_rng(91000).choice(96,64,False)).
5. FR spot-check: pick 30 questions from s=0 test; independently recompute per-question FR for
   arms {drop64, alone64, RANDOM64_s91000} and native; compare vs stored per_q_test values
   (tolerance 1e-12; state max diff).
6. Summary recompute: from stored per_q_test[arm] arrays recompute per-split gap64_vs_best =
   mean(drop64) − max_over_seeds mean(RANDOM64_s*); the 10-split mean/median/range/wins for
   drop64 and alone64; compare with deney1_lme_details.json['summary']. Also recompute the
   vs-mean secondary (mean panel) and its wins.
7. LoCoMo: verify peraxis.npz: for 15 random (qid, axis) cells recompute drop/alone FR directly
   from locomo pkls + audit gold (protocol as r2c) and compare; verify native array mean equals
   0.23654714666441054 (1e-12); verify split s=3 gap vs best-of-10 from stored per_q_test vs
   summary (recompute gap/mean like step 6 for LoCoMo); verify valid count 1535.
8. Kill-criteria arithmetic: from recomputed values, confirm (a) LME mean-vs-best < +1.0 (state
   value), (b) LME wins < 7/10, (c) LoCoMo mean-vs-best ≤ 0; and that the report's claimed
   trigger values (−1.25pp, 2/10, −0.15pp) match recomputation to rounding.
9. JSON self-consistency: split counts (train+test=470 / 1535), arms cols within 0..95, eff_k
   of SPREAD sets, no NaN in per_q arrays.

## Output

/tmp/d1v/d1v_report.md + /tmp/d1v/d1v_details.json; end stdout with
D1V_VERDICT: <n_exact>/<n_checks> EXACT, diffs list, cannot-check list. Harsh honesty: if anything
is off by >1e-12 or logic disagrees with the scripts, say so loudly with the counter-numbers.
