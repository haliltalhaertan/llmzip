[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

> **ORCHESTRATOR ERRATA (2026-09-13, after adversarial review R2D).** Labels/limits: [LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION]; single benchmark (LME-470); baseline is the SINGLE seed RAND48_s0 (round-1 five-seed spread at k=48 was 3.5 pp — flip counts inherit that noise); findings are descriptive. "The discriminative signal lived in low-variance axes" is demoted to subset-level description (no causal mechanism licensed; round-1 REPORT leaves the mechanism OPEN). "Hard losers average" refers to all 34 hard-loss questions (the 10 largest shown have higher TOP48 ranks, ~21.4 average).

All gates reproduce exactly. Results below; details saved in [/tmp/r2a/per_q.json](/tmp/r2a/per_q.json) (211,088 bytes).

## 1. Self-gate (exact diffs)

| Arm | Recomputed | Expected | Diff |
|---|---|---|---|
| TOP48 | 0.34949468085106383 | 0.34949468085106383 | 0.0 |
| RAND48_s0 | 0.47292553191489356 | 0.47292553191489356 | 0.0 |
| BOT48 | 0.4284574468085106 | 0.4284574468085106 | 0.0 |

No investigation needed — all diffs are exactly 0.0 (well under 1e-12). Cross-checks: per-question native FR vs stored `per_question_native_FR` max abs diff = 0.0 (470/470); pkl N/gold vs metadata N_archive/gold_count mismatches = 0. Protocol matched verbatim, including `np.argsort(var, kind="stable")[::-1]` ordering and seed-12000 single shared random subset.

## 2. Tie metrics

Saved per question in `per_q.json` for TOP48 and RAND48_s0 (means over 20 trials). Conventions: gold rank = 0-based min position in `order`; (b)–(d) keyed off the best gold (min distance) and are trial-invariant. Aggregate means:

- gold rank: TOP48 18.65 vs RAND48 20.96 (TOP48 *better* on average)
- docs strictly closer: 16.03 vs 18.13 (TOP48 better)
- tie-cluster at gold distance: 6.40 vs 6.98; boundary-tie rate: 0.460 vs 0.426 (TOP48 slightly worse)
- TOP48 mean dup fraction: 0.0235

So TOP48 wins the mean-distance statistics yet loses retrieval — the pilot paradox, confirmed.

## 3. Flip analysis (gap = TOP48 − RAND48_s0, tol 1e-12)

Overall W/T/L = 63/250/157; mean gap −0.1234, median 0.0 (ties dominate).

Per `question_type`, sorted by mean gap:

| type | n | W/T/L | mean | median |
|---|---|---|---|---|
| single-session-user | 64 | 3/36/25 | −0.300391 | 0.0 |
| knowledge-update | 72 | 13/26/33 | −0.165162 | 0.0 |
| single-session-assistant | 56 | 4/39/13 | −0.147321 | 0.0 |
| temporal-reasoning | 127 | 24/63/40 | −0.074934 | 0.0 |
| single-session-preference | 30 | 3/21/6 | −0.062778 | 0.0 |
| multi-session | 121 | 16/65/40 | −0.059883 | 0.0 |

Pearson correlations of gap with: N_archive −0.1273, gold_count +0.1486, RAND48 gold rank +0.1353, TOP48 tie-cluster +0.0198, TOP48 dup fraction −0.0369. All weak; notably tie-cluster size and dup fraction are ~zero, so no single one of these variables explains the flip.

10 largest losers (all gap −1.0, top 0.0 / rand 1.0; 34 such questions exist, gold_counts {1,2}):

001be529, 18dcd5a5, 195a1a1b, 36580ce8, 3e321797, 3f1e9474, 4100d0a0, 57f827a0, 5d3d2817, 60d45044 — types single-session-user ×5 (N 510–545), single-session-assistant ×2, single-session-preference ×2.

5 largest winners: gpt4_468eb063 (temporal, N=498, +1.0), 76d63226 (ss-user, +1.0), 3249768e (ss-assistant, +1.0), gpt4_e414231f (temporal, +0.9), e48988bc (ss-assistant, +0.85).

What distinguishes flips (spot check): loser 001be529 — RAND puts the gold uniquely closest every trial (rank 0.0, cluster 1.0) while TOP48 buries it (rank 18.2, 14 docs closer, cluster 11). Winner gpt4_468eb063 is the mirror image (TOP48 rank 0.95/cluster 3; RAND rank 8.5, 6 closer, boundary-tied). Hard losers average: TOP48 rank 10.8/cluster 6.1 vs RAND rank 0.6/cluster 1.3. Mechanism: on the decisive subset, the discriminative signal lived in low-variance axes — TOP48 collapses those golds into tie clusters outside top-3 while RAND keeps them uniquely closest.

## 4. Final JSON block

```json
{"gate_diffs": {"TOP48": 0.0, "RAND48_s0": 0.0, "BOT48": 0.0},
 "native_max_abs_diff_vs_stored": 0.0, "meta_mismatch_count": 0,
 "aggregates": {"TOP48": 0.34949468085106383, "RAND48_s0": 0.47292553191489356, "BOT48": 0.4284574468085106},
 "WTL_overall": {"W": 63, "T": 250, "L": 157}, "mean_gap": -0.12343085106382978, "median_gap": 0.0,
 "per_type": [
  {"type": "single-session-user", "n": 64, "W": 3, "T": 36, "L": 25, "mean_gap": -0.300391, "median_gap": 0.0},
  {"type": "knowledge-update", "n": 72, "W": 13, "T": 26, "L": 33, "mean_gap": -0.165162, "median_gap": 0.0},
  {"type": "single-session-assistant", "n": 56, "W": 4, "T": 39, "L": 13, "mean_gap": -0.147321, "median_gap": 0.0},
  {"type": "temporal-reasoning", "n": 127, "W": 24, "T": 63, "L": 40, "mean_gap": -0.074934, "median_gap": 0.0},
  {"type": "single-session-preference", "n": 30, "W": 3, "T": 21, "L": 6, "mean_gap": -0.062778, "median_gap": 0.0},
  {"type": "multi-session", "n": 121, "W": 16, "T": 65, "L": 40, "mean_gap": -0.059883, "median_gap": 0.0}],
 "correlations": {"N_archive": -0.12727, "gold_count": 0.14861, "RAND48_gold_rank": 0.13529, "TOP48_tie_cluster": 0.01980, "TOP48_dup_frac": -0.03688},
 "losers": ["001be529", "18dcd5a5", "195a1a1b", "36580ce8", "3e321797", "3f1e9474", "4100d0a0", "57f827a0", "5d3d2817", "60d45044"],
 "winners": ["gpt4_468eb063", "76d63226", "3249768e", "gpt4_e414231f", "e48988bc"],
 "per_q_json": "/tmp/r2a/per_q.json", "per_q_json_bytes": 211088}
```

Nothing failed to reproduce. Script kept at `/tmp/r2a/r2a.py` for re-runs; no writes under /mnt/c.
