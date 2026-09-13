**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

> **ORCHESTRATOR ERRATA (2026-09-13, after D5 adversarial review).** F3: cannot-check items 1–2 were oversights, not limits. RE-CHECKED (f3_rechecks.txt): LoCoMo split counts/balance verified for all 10 splits; 5 nonzero-FR test qids recomputed EXACT (membership aligned); r2c_replicate.py located at round2/session_scripts/. HASHES_ROUND3.txt: 6/6 OK; delta64 cols EXACT. See ERRATA_ROUND3_D5.md §F3.

# D1V — Independent recompute of Deney 1 (round3) numbers

[VERIFICATION] [READ-ONLY EVIDENCE] — all values below were recomputed FROM RAW
ARTIFACTS by an independent script (`/tmp/d1v/d1v_verify.py`, no imports from
`harness/`; logic reimplemented from reading `deney1_lme.py` / `deney1_loco.py`).
`/mnt/c` was only read; writes only under `/tmp/d1v/`. No network.
Machine details: numpy 2.5.3, python 3.14.4.

## Verdict table (tolerances: FR/utility/split logic exact or ≤1e-12; JSON float round-trip ≤1e-9)

| # | Check | Result | Numbers |
|---|---|---|---|
| 1 | Split reconstruction s=0, s=7 (sha256 `deney1\|s\|qid`, alternate within question_type) | EXACT, EXACT | s=0: train 236 / test 234, lists identical; s=7: 236/234, identical; disjoint+complete both |
| 2 | Utility top-64 (s=0, s=7): U_drop=mean(native−drop), U_alone=mean(alone·pool/3, pool from pkls), U_var=mean(−var_rank) | 6× EXACT | drop64/alone64/var64 cols identical incl. first5 (s=0 drop [0,3,4,6,8], alone [1,2,3,4,5]) |
| 3 | SPREAD64 s=0 = sort(order_desc[round(linspace(0,95,64))]) | EXACT | identical, 64/64 positions distinct |
| 4 | RANDOM64_s91000 s=0 = sorted(rng(91000).choice(96,64,False)) | EXACT | identical |
| 5 | FR spot-check: 30q (first 30 of s=0 test) × {drop64, alone64, RANDOM64_s91000, native} | EXACT | max_abs_diff = 1.11e-16 ≤ 1e-12 |
| 5b | GATE1 native recompute, all 470 | EXACT | max_abs_diff = 1.11e-16 (report: 1.11e-16); mean 0.5419751773049645 both |
| 6 | Summary recompute (per-split gap = mean(drop64) − max seed mean; mean/median/range/wins) | EXACT | per-split gaps ok; max summary diff 0.0; drop −1.2460826210826181pp 2/10; alone −3.1452635327635305pp 0/10 |
| 6-mean | Secondary vs-mean (recompute only) | INFO | drop +0.4292pp 7/10 (report +0.43pp 7/10 ✓); alone −1.4700pp 3/10 (report −1.47pp ✓) |
| 6b | s=0 bootstrap CI90 (rng 777000, B=2000) / WTL / var-worst-k64 | 3× EXACT | CI [−5.286681,−0.333903] ✓; WTL [6,129,99] ✓; var worst (0.4317 < delta 0.4416) ✓ |
| 7 | LoCoMo valid count | EXACT | 1535 = 1535 = 1535 |
| 7 | LoCoMo native mean vs anchor | EXACT | 0.23654714666441054, diff 0.0 |
| 7 | peraxis.npz qids == valid set | EXACT | 1535 qids match |
| 7 | peraxis.npz 15 random (qid,axis) cells drop/alone from pkls+audit gold | EXACT | max_abs_diff = 0.0 |
| 7 | LoCoMo s=3 gap vs best-of-10 | EXACT | n_test 767 ✓; gap drop −0.46608617371329264 ✓; alone −0.5068758924691164 ✓ |
| 7 | LoCoMo summary recompute | EXACT | max diff 0.0; drop −0.14953631584987523pp 2/10; alone −0.09175066237628539pp 5/10 |
| 8 | Kill arithmetic | EXACT | LME mean −1.246083 < +1.0 ✓; wins 2/10 < 7/10 ✓; LoCoMo −0.149536 ≤ 0 ✓; rounded (−1.25, 2/10, −0.15) = report ✓ |
| 9 | JSON self-consistency | EXACT | 10/10 LME train+test=470, disjoint; all arms (LME 45 + LoCoMo 42 per split) cols ∈ 0..95, unique, len==k (SPREAD eff_k ✓); no NaN; per_q lens ok |

Extra corroboration (stored-array arithmetic, second method): LoCoMo vs-mean
drop +1.1058pp 10/10 and alone +1.1636pp 9/10 (report: +1.11pp 10/10, +1.16pp 9/10 ✓);
per-split gap columns reproduce the report tables to rounding
(LME [−1.89,−1.85,+0.78,−3.11,−2.18,+1.14,−0.74,−0.87,−2.26,−1.48];
LoCoMo [−0.42,−0.36,−0.18,−0.47,−0.79,+0.73,−0.25,−1.17,+1.87,−0.47]).

NOTE: one transient DIFF appeared mid-session on `LME-6b-VARW` and was traced to a
bug in MY check script (compared argmin key `'var'` against arm-name dict keyed
`'var64'`), not the data — var64 test_FR 0.4317 is the family minimum, stored
`var_worst=true` is correct. Fixed, full suite re-run: 24 EXACT + 1 INFO, 0 DIFF.

## Cannot-check list

1. LoCoMo split membership lists — `deney1_loco_details.json` stores no
   train/test qids (only `run.n_test` + `per_q_test`); only reconstructed counts
   vs `n_test` (s=3: 767 ✓) could be checked.
2. `r2c_replicate.py` not found in repo — LoCoMo protocol checked against
   `harness/deney1_loco.py` text only, not an independent R2C source.
3. Train-side per-question FR (`per_q_tr`) is computed but not persisted in either
   JSON — cannot be checked.
4. Bootstrap CIs for the other 9+10 splits not re-executed (same code path
   verified once on LME s=0); LoCoMo CI seed path (778000+s) not re-executed.
5. LME `delta64` utility cols not directly checked (only drop/alone/var per spec).
6. `HASHES_ROUND3.txt` hashes not re-verified (out of scope); no network used.

## Bottom line

Nothing is off by >1e-12 anywhere I could check from raw artifacts. All three
KILL triggers recompute exactly as reported (−1.246pp→−1.25pp, 2/10, −0.150pp→−0.15pp).
The KILL verdict's numbers are verified.
