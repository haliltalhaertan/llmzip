# Independent recomputation report (read-only; scratch in `/tmp/pilotverify/`)

**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

Stack: system python3, numpy 2.5.3. All values recomputed from the 470 pkls + dataset lex ordinals using the frozen protocol as specified.

## E0 gate — full 470

- RECOMPUTED: FR 0.5419751773049645, ANY 0.7130851063829787, ALL 0.38457446808510637
- PILOT / published: FR 0.5419751773049646, ANY 0.7130851063829787, ALL 0.38457446808510637
- delta: FR 1.1e-16 (last-bit float repr), ANY/ALL 0.0
- Per-question vs frozen CSV: 470/470 compared, max abs diff 1.1e-16. Per-question vs pilot JSON: max abs diff 0.0.
- Verdict: **EXACT**

## E1 budget curve

- RECOMPUTED top-k: k16 0.16931028368794324, k32 0.25454787234042553, k64 0.4324716312056737 — all bit-identical to pilot. Verdict: **EXACT**
- RAND32_s0: 0.3720921985815603, RAND64_s0: 0.47402659574468076 — bit-identical to `extra_arms.json`. Verdict: **EXACT**
- BOT48: 0.4284574468085106 — bit-identical to `E1_bottomk_variance["48"]`. Verdict: **EXACT**
- RAND48 seed-12000-only: RECOMPUTED 0.47292553191489356 vs PILOT `E1_random_subset["48"]` 0.4507086288416076, delta +0.0222. Verdict: **DIFFERS** — explained, not a pilot error: the pilot script accumulates 3 seeds (12000+s, s=0..2) per question into that key. My 3-seed mean is 0.4507086288416076, bit-identical to the pilot. (Same structure confirmed for k16: 3-seed mean 0.20143203309692675, bit-identical.)

## E2 axes 0 / 47 / 95

- Axis 0: alone 0.006539007092198582 (csv 0.0065390071), drop 0.5371276595744681 (csv 0.5371276596)
- Axis 47: alone 0.007342198581560285 (csv 0.0073421986), drop 0.5423226950354609 (csv 0.5423226950)
- Axis 95: alone 0.007462765957446809 (csv 0.0074627660), drop 0.5357482269503546 (csv 0.5357482270)
- Deltas within csv 10dp rounding. Verdict: **EXACT**

## E4 seed 43001, block 2

- Random pairing: RECOMPUTED FR 0.5071312056737588, gap -3.4843971631205672 pp. Pilot identical bit-for-bit. Frozen reference -3.4844 pp: recomputed value rounds to it. Verdict: **EXACT**
- Matched-variance: RECOMPUTED FR 0.5388280141843972, gap -0.3147163120567287 pp — bit-identical to pilot. Verdict: **EXACT**

## Diagnostics, 25 first-sorted pkls vs full-470 pilot values

Sample means (TOP48 / RAND48_s0 / BOT48):

- dup_frac: 0.02177 / 0.00751 / 0.00585 vs full 0.02352 / 0.00786 / 0.00579 — close
- tie rate: 0.40 / 0.48 / 0.40 vs full 0.4596 / 0.4255 / 0.4234 — close
- mean |phi|: 0.05980 / 0.04172 / 0.03779 vs full 0.05926 / 0.04128 / 0.03726 — close
- mean gold rank: 37.16 / 39.38 / 58.31 vs full 18.65 / 20.96 / 31.94 — ~2x higher

The gold-rank gap is sampling noise, not a discrepancy: I recomputed full-470 TOP48 gold_rank with the same code and got 18.654148936170213, bit-identical to `diagnostics2.json`. The per-question distribution is extremely skewed (median 2.38, pstdev 59.2), so the 25-sample mean sitting ~1.6 SE above the full mean is unremarkable. Verdict: **CLOSE** (as expected for sample-vs-full; formulas verified exact at full scale for TOP48).

## Summary

| Check | Verdict |
|---|---|
| E0 gate | EXACT |
| E1 top-k / RAND32 / RAND64 / BOT48 | EXACT |
| E1 RAND48 seed-only vs pilot key | DIFFERS, explained |
| E2 axes 0, 47, 95 | EXACT |
| E4 random + matched, seed 43001 | EXACT |
| Diagnostics sample | CLOSE |

Pilot numbers independently reproduced: **yes, with one clarified comparison** — `E1_random_subset["48"]` (and `["16"]`) are means over three seeds (12000, 12001, 12002), not seed-12000-only as the task text assumed; the seed-12000-only k48 value is 0.47292553191489356 while the 3-seed mean reproduces the pilot bit-for-bit. No other deviation found; nothing was written outside `/tmp/pilotverify/`.
