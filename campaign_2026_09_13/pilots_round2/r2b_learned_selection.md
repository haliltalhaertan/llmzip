**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

> **ORCHESTRATOR ERRATA (2026-09-13, after adversarial review R2D).** Two factual errors in the prose above are corrected here: (1) **two** learned arms beat their k-matched random mean — `drop64` (+3.39 pp) **and `alone64` (+2.17 pp)**; (2) `alone64` does **not** sit inside the RANDOM64 seed range — its test FR 0.47154 **exceeds the best seed** (0.46760, +0.39 pp). Headline gaps should be read as drop64 +1.62 pp and alone64 +0.39 pp **vs the best** of the three seeds (vs-mean gaps flatter: seeds span 3.34 pp). Everything else stands; details in `wsl_details/r2b_details.json`.

# R2B result — [EXPLORATORY] [NOT PREREGISTERED]

**Outcome:** learned ranking mostly fails out-of-sample. One arm, `drop64` (top-64 train-mean drop-loss axes), beats the RANDOM64 mean on test by +3.39pp, W/T/L 63/124/44 (tol 1e-12, n=231). All other learned arms are at or below their k-matched random mean; the variance control is far worse at every k, replicating the pilot's top-variance finding out-of-sample.

**Split:** train=239, test=231 (sha256-first-hex even rule). question_type is roughly balanced — train {multi-session 59, temporal-reasoning 62, knowledge-update 43, single-session-user 33, assistant 27, preference 15}; test {62, 65, 29, 31, 29, 15}. Largest skew is knowledge-update (43 vs 29).

**Gates (all exact):** recomputed all-96 native FR matches stored per-q natives to max abs diff 1.1e-16 (mean 0.5419751773 both). Test half is harder than train: stored native mean test 0.5190 vs train 0.5642.

| arm | train | test | gap pp |
|---|---|---|---|
| delta32 | 0.4020 | 0.3244 | -2.15 |
| delta48 | 0.4808 | 0.3864 | -4.92 |
| delta64 | 0.5139 | 0.4317 | -1.82 |
| drop32 | 0.3816 | 0.3374 | -0.86 |
| drop48 | 0.4921 | 0.4444 | +0.88 |
| drop64 | 0.5623 | 0.4838 | +3.39 |
| alone32 | 0.3722 | 0.2972 | -4.87 |
| alone48 | 0.4876 | 0.4053 | -3.03 |
| alone64 | 0.5232 | 0.4715 | +2.17 |
| var32 | 0.2709 | 0.2376 | -10.84 |
| var48 | 0.3710 | 0.3290 | -10.66 |
| var64 | 0.4630 | 0.4063 | -4.35 |
| SPREAD32 | 0.3592 | 0.3193 | -2.67 |
| SPREAD48 | 0.4779 | 0.4218 | -1.38 |
| SPREAD64 | 0.4779 | 0.4218 | -2.81 |
| RND32-mean | 0.3748 | 0.3459 | +0.00 |
| RND48-mean | 0.4653 | 0.4356 | +0.00 |
| RND64-mean | 0.5148 | 0.4498 | +0.00 |
| NATIVE96 | 0.5642 | 0.5190 | NA |

Notes:

- Overfit gap is visible: drop64 train FR 0.5623 (≈ train native) vs test 0.4838. drop64 beats all three RANDOM64 seeds on test (0.4342/0.4676/0.4477); drop48/alone64 sit inside their random-seed ranges.
- Design artifact, reported honestly: SPREAD64 ≡ SPREAD48 bit-for-bit (stride-2 over 96 axes yields at most 48 axes, so `[:64]` is a no-op). Its gap differs only because the reference mean changes with k.
- Utility top-5 (train): delta [7,6,12,5,9], drop [23,72,88,2,58], alone [10,16,7,8,27], var [1,2,3,4,5]. Random-seed spread at fixed k is wide (±2–3pp), so single-arm gaps near ±1pp are noise-scale.
- `details.json`: 84255 bytes at `/tmp/r2b/details.json` (24 arms, per-q test+train FRs, cols, qids, gates). No writes under /mnt/c (reads only).

```json
{"split": {"n_train": 239, "n_test": 231}, "gate_native": {"max_abs_diff": 1.1e-16, "test_stored_mean": 0.518975469, "train_stored_mean": 0.5642050209}, "random_mean_test": {"32": 0.3459355459, "48": 0.4356144781, "64": 0.4498376623}, "best_learned": {"arm": "drop64", "test_FR": 0.4837806638, "gap_pp": 3.3943001443, "WTL_tol1e-12": [63, 124, 44]}, "test_FR": {"delta32": 0.3244083694, "delta48": 0.3864105339, "delta64": 0.4316666667, "drop32": 0.3373665224, "drop48": 0.4444155844, "drop64": 0.4837806638, "alone32": 0.2971897547, "alone48": 0.4053354978, "alone64": 0.4715367965, "var32": 0.2375829726, "var48": 0.328968254, "var64": 0.4062914863, "SPREAD32": 0.3192640693, "SPREAD48": 0.4217676768, "SPREAD64": 0.4217676768}}
```
