# R2V: independent recomputation of round-2 headline numbers

**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

Method: recomputed from raw inputs only (LME pkls + `per_axis_matrices.npz` + `pilot_results.json` + `longmemeval_s_cleaned.json`; LoCoMo pkls + `locomo10.json` + `audit_layer/`), with protocols taken from the frozen sources (`pilot_axis_attack.py` for LME tie/lex rules, `v52_t4d_locomo_frozen_cross_benchmark.py` for LoCoMo — functions copied verbatim). Never read `/tmp/r2a|r2b|r2c`. Scripts kept at `/tmp/r2v/r2v_lme.py`, `/tmp/r2v/r2v_locomo.py`. No `/mnt/c` writes, no network.

## 1. R2B drop64 headline

| Item | RECOMPUTED | CLAIMED | delta | Verdict |
|---|---|---|---|---|
| (a) split train/test | 239 / 231 | 239 / 231 | 0 | EXACT |
| (b) drop top-5 | [23, 72, 88, 2, 58] | [23, 72, 88, 2, 58] | — | EXACT (full 64/64 cols also identical) |
| (c) drop64 test FR | 0.48378066378066376 | 0.4837806638 (md) / …6376 (details) | 0.0 | EXACT |
| (c) drop64 train FR | 0.5622907949790794 | 0.5622907949790794 | 0.0 | EXACT |
| (c) RANDOM64 s12000 test | 0.4342352092352092 | 0.4342 (md) / …092 (details) | 0.0 vs details | EXACT |
| (c) RANDOM64 s12001 test | 0.4676046176046176 | 0.4676 / …176 | 0.0 | EXACT |
| (c) RANDOM64 s12002 test | 0.44767316017316017 | 0.4477 / …017 | 0.0 | EXACT |
| (d) W/T/L vs RANDOM-mean | 63 / 124 / 44 | 63 / 124 / 44 | — | EXACT |

Notes: md's 4-decimal random values (0.4342/0.4676/0.4477) are correct roundings of the exact recomputed values. Distances recomputed from the pkls per the frozen protocol (lex = ordinal over all 500 dataset qids).

## 2. R2A flip aggregate

| Item | RECOMPUTED | CLAIMED | delta | Verdict |
|---|---|---|---|---|
| W/T/L TOP48−RAND48_s0 | 63 / 250 / 157 | 63 / 250 / 157 | — | EXACT |
| mean gap | −0.1234308510638298 | −0.12343085106382978 | −1.4e-17 | CLOSE (fp summation order; identical to 16 decimals) |
| TOP48 / RAND48 / BOT48 means | 0.34949468085106383 / 0.47292553191489356 / 0.4284574468085106 | same | 0.0 | EXACT |
| `single-session-user` row | n=64, 3/36/25, mean −0.300390625, median 0.0 | n=64, 3/36/25, mean −0.300391, median 0.0 | 0 (md value is the 6-dp rounding) | EXACT |

All six per-type rows also match (n, W/T/L, and means to md rounding; medians all 0.0).

## 3. R2C LoCoMo (protocol extracted from T4D script, not from r2c details)

| Item | RECOMPUTED | CLAIMED | delta | Verdict |
|---|---|---|---|---|
| (a) GATE native frac R@3 | 0.23654714666441054 | 0.23654714666441054 | 0.0 | EXACT |
| Haar96 mean (corroboration) | 0.13770827054135712 | 0.13770827054135715 | −2.8e-17 | CLOSE |
| Haar seeds 43001–43005 | .12991972305653088 / .13805874420587866 / .14360296073813988 / .13537524120298597 / .14158468350325026 | same (…085→…088 at 1e-17) | ≤2.8e-17 | CLOSE/EXACT |
| (b) MATCHED mean | 0.23610144174802153 | 0.23610144174802153 | 0.0 | EXACT |
| MATCHED per-seed | 0.23565226250405405 / 0.23022749129263786 / 0.24242457144737276 | …05402 / …63786 / …37273 | ≤2.8e-17 | CLOSE |
| MATCHED gaps pp | −0.0895 / −0.6320 / +0.5877 | −0.09 / −0.63 / +0.59 | rounding | EXACT |
| ANTIMATCHED mean | 0.1937153820894001 | 0.1937153820894001 | 0.0 | EXACT |
| ANTIMATCHED per-seed | 0.19905625797846532 / 0.182717620045748 / 0.19937226824398696 | same | ≤2.8e-17 | CLOSE/EXACT |
| ANTI gaps pp | −3.7491 / −5.3830 / −3.7175 | −3.75 / −5.38 / −3.72 | rounding | EXACT |
| (c) k=48 BOT | 0.18112226499522918, gap −5.5425pp | 0.181122 (gap −5.54) | 0.0 | EXACT |

Cohort independently confirmed: 1540 Cat1–4 questions, 1535 audit-valid; all 156 audit corrections verified by question-text agreement (156/156) against pkl indexing. Block-2 reconstruction used: RANDPAIR = `hspec(seed,2)` verbatim; MATCHED perm = descending stable `argsort(var)` with identical Q-blocks; ANTIMATCHED = interleaved top/bottom pairs — all three seeds reproduce, confirming the arm semantics.

## 4. Spot-check `001be529` (recomputed from the pkl directly)

| Field | RECOMPUTED | CLAIMED | delta | Verdict |
|---|---|---|---|---|
| fr_top / fr_rand | 0.0 / 1.0 | 0.0 / 1.0 | 0 | EXACT |
| TOP48 rank / n_closer / cluster / boundary | 18.15 / 14 / 11 / 0 | 18.15 / 14.0 / 11.0 / 0.0 | 0 | EXACT |
| RAND rank / n_closer / cluster / boundary | 0.0 / 0 / 1 / 0 | 0.0 / 0.0 / 1.0 / 0.0 | 0 | EXACT |
| TOP48 dup frac | 0.029182879377431914 | 0.029182879377431914 | 0 | EXACT |
| N / ngold / lex | 514 / 1 / 0 | 514 / 1 / 0 | — | EXACT |

Note: the task text says "rank 18.2" but the details file verbatim claims 18.15 — recomputed value is exactly 18.15, so the "18.2" is just a 1-dp rounding in the task description.

## Summary table

| # | Check | Verdict |
|---|---|---|
| 1a | R2B split 239/231 | EXACT |
| 1b | R2B drop top-64 (top-5 [23,72,88,2,58], all 64 cols) | EXACT |
| 1c | R2B drop64 test 0.4837806638; RANDOM64 0.4342/0.4676/0.4477 | EXACT |
| 1d | R2B W/T/L 63/124/44 | EXACT |
| 2 | R2A W/T/L 63/250/157, mean gap −0.1234…, ss-user row | EXACT (gap CLOSE at 1e-17) |
| 3a | R2C GATE native 0.23654714666441054 | EXACT |
| 3b | R2C MATCHED .236101 / ANTIMATCHED .193715 + per-seed gaps | EXACT (≤3e-17) |
| 3c | R2C k=48 BOT 0.181122, gap −5.54 | EXACT |
| 4 | Spot 001be529 (rank 18.15/cluster 11 vs 0.0/1.0) | EXACT |

## Verdict

Round-2 numbers independently reproduced: **yes** — every headline number recomputed from raw inputs matches its claim exactly (bit-for-bit in almost all cases; worst deviation 5.6e-17 from floating-point reduction order, far below any reported precision). Two non-numeric imprecisions noted, neither affecting any number: (i) the task text's "rank 18.2" vs the verbatim claimed/recomputed 18.15 (rounding); (ii) the r2c "pkl order == raw order" gloss — pkls hold the Cat1–4 subsequence (raw has 1986 incl. Cat5; conv 1 interleaves a Cat5), but priorities are conversation-level so ordering is immaterial, and correction-to-question mapping was verified 156/156 by text.
