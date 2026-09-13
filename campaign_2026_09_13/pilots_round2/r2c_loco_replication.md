> **ORCHESTRATOR ERRATA (2026-09-13, after adversarial review R2D).** Labels/limits: [LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION]. "Replicates strictly" is qualified: n=3 seeds (matched-seed range 1.2 pp; anti range 1.7 pp; means −0.04 / −2.35 / −4.28 pp). The per-category table compares native vs `MATCHED_seed43003` = the best-on-aggregate matched seed (selection step disclosed). The matched/antimatched constructions are NOVEL (not in the frozen T4D script, which has only random pairing) — the gate validates the shared pipeline, not the new pairings; construction code: `session_scripts/r2c_replicate.py`.

## R2C LoCoMo replication — done, gate exact

**GATE:** Native fractional R@3 = `0.23654714666441054`, diff vs anchor **0.0**. Full-Haar96 mean = `0.13770827054135715`, diff **-2.9e-15** (anchor has 14 decimals; rounding only). Seeds: 43001 `.12991972305653085`, 43002 `.13805874420587866`, 43003 `.14360296073813988`, 43004 `.13537524120298597`, 43005 `.14158468350325026`. Cohort: 1540 Cat1–4 questions, 1535 audit-valid, pkl order verified == raw order. No re-fit; script `/tmp/r2c/replicate.py`, log `/tmp/r2c/r2c_run.log`.

### Bit-budget arms (Fractional R@3; gap pp vs native 0.236547)

| k | TOP | RANDOM s0/s1/s2 | BOT | SPREAD |
|---|---|---|---|---|
| 16 | .065300 (-17.12) | .058975/.057412/.063504 (-17.76/-17.91/-17.30) | .074165 (-16.24) | .049081 (-18.75) |
| 32 | .087020 (-14.95) | .117333/.121874/.121927 (-11.92/-11.47/-11.46) | .140395 (-9.62) | .109560 (-12.70) |
| 48 | .131826 (-10.47) | .159121/.159828/.168345 (-7.74/-7.67/-6.82) | .181122 (-5.54) | .160270 (-7.63) |
| 64 | .165291 (-7.13) | .188625/.202501/.197651 (-4.79/-3.40/-3.89) | .217183 (-1.94) | .160270* (-7.63) |
| 80 | .200362 (-3.62) | .227676/.210761/.225740 (-0.89/-2.58/-1.08) | .235461 (-0.11) | .160270* (-7.63) |

\* SPREAD formula caps at 48 axes; k=64/80 reported with eff_k=48.

### Block-2 pairing at 96 bits (per-seed; gap pp)

- RANDPAIR: .204914 (-3.16) / .220293 (-1.63) / .213811 (-2.27), mean .213006 (-2.35)
- MATCHED: .235652 (-0.09) / .230227 (-0.63) / .242425 (+0.59), mean .236101 (-0.04)
- ANTIMATCHED: .199056 (-3.75) / .182718 (-5.38) / .199372 (-3.72), mean .193715 (-4.28)
- Strict separation on every seed: min MATCHED (.2302) > max RANDPAIR (.2203) > max ANTI (.1994).

### Per-category, native vs best arm (MATCHED_seed43003) vs Haar mean

Cat1 (n=282): .108717 / .099604 / .066003. Cat2 (n=320): .255208 / .260156 / .115979. Cat3 (n=92): .095109 / .090308 / .078960. Cat4 (n=841): .287782 / .300208 / .176447.

### Reading vs pilot

- (b) replicates for k≥32: TOP is far worse than RANDOM and BOT (e.g. k48 TOP .132 vs BOT .181). Nuance: at k16 TOP beats RANDOM but loses to BOT, and SPREAD is worst — "spread beats top" does not hold at k16 on LoCoMo.
- (c) replicates strictly: mixing damage monotone in variance disparity (MATCHED ≈ native > RANDPAIR > ANTIMATCHED).

### Deviations declared

RANDOM subsets drawn once globally per (k,seed), shared across archives; TOP/BOT/SPREAD per-archive from `C.var(axis=0)`. Block seeds 43001–43003; MATCHED/ANTIMATCHED use deterministic variance-pairing perms with Q-blocks bit-identical to RANDPAIR (same rng draw order). No writes under /mnt/c.

### Final JSON (every number; full copy in `/tmp/r2c/details.json`, 11554 bytes)

```json
{"best_arm": "MATCHED_seed43003",
"block_means": {"ANTIMATCHED": 0.1937153820894001, "MATCHED": 0.23610144174802153, "RANDPAIR": 0.2130056848653323},
"gate": {"haar_diff": -2.858824288409778e-15, "haar_mean": 0.13770827054135715,
"haar_seeds": {"43001": 0.12991972305653085, "43002": 0.13805874420587866, "43003": 0.14360296073813988, "43004": 0.13537524120298597, "43005": 0.14158468350325026},
"native": 0.23654714666441054, "native_diff": 0.0},
"arms": {"TOP_k16": 0.06529993755472774, "BOT_k16": 0.07416534822398015, "SPREAD_k16": 0.049081124523642244,
"TOP_k32": 0.08701952019579919, "BOT_k32": 0.14039496641613905, "SPREAD_k32": 0.10955977645228461,
"TOP_k48": 0.13182630371268042, "BOT_k48": 0.18112226499522918, "SPREAD_k48": 0.16026999873091077,
"TOP_k64": 0.16529145781301366, "BOT_k64": 0.21718346329746985,
"TOP_k80": 0.20036214725748164, "BOT_k80": 0.23546142203796927,
"RANDOM_k16": [0.05897478155214312, 0.05741240464204634, 0.06350363598208013],
"RANDOM_k32": [0.11733295378165086, 0.12187402644405902, 0.12192741044695442],
"RANDOM_k48": [0.15912137829171744, 0.15982848141724365, 0.16834543640770885],
"RANDOM_k64": [0.18862519440704917, 0.20250092140300993, 0.1976514610977152],
"RANDOM_k80": [0.22767557849316805, 0.21076096704598332, 0.22573982260952946],
"RANDPAIR": [0.2049137886128689, 0.22029271542789455, 0.21381055055523346],
"MATCHED": [0.23565226250405402, 0.23022749129263786, 0.24242457144737273],
"ANTIMATCHED": [0.1990562579784653, 0.182717620045748, 0.19937226824398696]},
"per_category": [{"cat": 1, "n": 282, "native": 0.10871703355745908, "best": 0.09960419800845334, "haar": 0.06600295225491193},
{"cat": 2, "n": 320, "native": 0.2552083333333333, "best": 0.26015625, "haar": 0.11597916666666667},
{"cat": 3, "n": 92, "native": 0.09510869565217392, "best": 0.09030797101449275, "haar": 0.07896046462063087},
{"cat": 4, "n": 841, "native": 0.28778240190249704, "best": 0.3002080856123663, "haar": 0.1764466904478795}]}
```
