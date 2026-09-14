> **ORCHESTRATOR ERRATA (2026-09-13, after D5 adversarial review).** C5: the licensed conclusion is "utilities are benchmark-local; transfer ~ chance"; var-row FAV is TAUTOLOGICAL (src==own by construction). See ERRATA_ROUND3_D5.md §C5.

# D3: cross-benchmark utility transfer matrix (LME ⇄ LoCoMo)

[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Question: is the axis-utility structure shared between benchmarks, or benchmark-local?
All utilities here are FULL-DATA (gold-informed; declared). Transfer analysis only.

## 1. Gates (confidence: HIGH — exact recompute from pkls)

- LME native: recomputed mean=0.5419751773049645 vs anchor=0.5419751773049645 (diff=0.000e+00); stored mean=0.5419751773049645; max per-q abs diff recomp-vs-stored=1.110e-16. PASS (tol 1e-12).
- LoCoMo native: recomputed mean=0.23654714666441054 vs anchor=0.23654714666441054 (diff=0.000e+00); valid=1535; npz-native vs recomp max abs diff=0.000e+00. PASS (tol 1e-12).
- Evaluators are the analysts own, following r2b.py `fr_subset` and r2c_replicate.py verbatim.

## 2. Utility structure LME vs LoCoMo (confidence: HIGH — descriptive)

| family | Spearman rho | k=32 inter/Jaccard | k=48 inter/Jaccard | k=64 inter/Jaccard |
|---|---|---|---|---|
| drop | +0.0971 | 13/0.255 | 25/0.352 | 45/0.542 |
| alone | +0.0754 | 11/0.208 | 24/0.333 | 44/0.524 |
| var | +0.9999 | 32/1.000 | 48/1.000 | 64/1.000 |

Chance E[intersection]: k=32 → 10.67, k=48 → 24.00, k=64 → 42.67.

## 3. Transfer LME->LOCO — target LoCoMo (n=1535) (confidence: MEDIUM — full-data, no held-out)

| family,k | native | src→tgt | own | rand_mean | rand_best | spread | src−own | src−rmean | src−rbest | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| drop,32 | 0.2365 | 0.1181 | 0.1368 | 0.1151 | 0.1267 | 0.1231 | -1.87 | +0.30 | -0.86 | FAV/FAIL |
| drop,48 | 0.2365 | 0.1784 | 0.1895 | 0.1644 | 0.1728 | 0.1591 | -1.10 | +1.40 | +0.57 | FAV |
| drop,64 | 0.2365 | 0.2119 | 0.2235 | 0.1989 | 0.2071 | 0.1918 | -1.16 | +1.30 | +0.48 | FAV |
| alone,32 | 0.2365 | 0.1062 | 0.1410 | 0.1151 | 0.1267 | 0.1231 | -3.48 | -0.89 | -2.05 | /FAIL |
| alone,48 | 0.2365 | 0.1403 | 0.1792 | 0.1644 | 0.1728 | 0.1591 | -3.89 | -2.41 | -3.25 | /FAIL |
| alone,64 | 0.2365 | 0.1698 | 0.2204 | 0.1989 | 0.2071 | 0.1918 | -5.06 | -2.91 | -3.73 | /FAIL |
| var,32 | 0.2365 | 0.0860 | 0.0860 | 0.1151 | 0.1267 | 0.1231 | +0.00 | -2.91 | -4.07 | FAV/FAIL |
| var,48 | 0.2365 | 0.1318 | 0.1318 | 0.1644 | 0.1728 | 0.1591 | +0.00 | -3.26 | -4.09 | FAV/FAIL |
| var,64 | 0.2365 | 0.1663 | 0.1663 | 0.1989 | 0.2071 | 0.1918 | +0.00 | -3.25 | -4.07 | FAV/FAIL |

## 3. Transfer LOCO->LME — target LME (n=470) (confidence: MEDIUM — full-data, no held-out)

| family,k | native | src→tgt | own | rand_mean | rand_best | spread | src−own | src−rmean | src−rbest | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| drop,32 | 0.5420 | 0.3501 | 0.3518 | 0.3546 | 0.3774 | 0.3652 | -0.17 | -0.46 | -2.74 | FAV/FAIL |
| drop,48 | 0.5420 | 0.4554 | 0.4694 | 0.4436 | 0.4525 | 0.4578 | -1.40 | +1.18 | +0.29 | FAV |
| drop,64 | 0.5420 | 0.5066 | 0.5257 | 0.4905 | 0.5091 | 0.5021 | -1.90 | +1.61 | -0.25 | FAV |
| alone,32 | 0.5420 | 0.3546 | 0.3720 | 0.3546 | 0.3774 | 0.3652 | -1.74 | -0.01 | -2.29 | /FAIL |
| alone,48 | 0.5420 | 0.4490 | 0.4349 | 0.4436 | 0.4525 | 0.4578 | +1.41 | +0.53 | -0.35 | FAV/FAIL |
| alone,64 | 0.5420 | 0.4937 | 0.4720 | 0.4905 | 0.5091 | 0.5021 | +2.17 | +0.32 | -1.54 | FAV/FAIL |
| var,32 | 0.5420 | 0.2545 | 0.2545 | 0.3546 | 0.3774 | 0.3652 | +0.00 | -10.01 | -12.29 | FAV/FAIL |
| var,48 | 0.5420 | 0.3503 | 0.3503 | 0.4436 | 0.4525 | 0.4578 | +0.00 | -9.33 | -10.21 | FAV/FAIL |
| var,64 | 0.5420 | 0.4351 | 0.4351 | 0.4905 | 0.5091 | 0.5021 | +0.00 | -5.54 | -7.40 | FAV/FAIL |

Reading rule (pre-declared, no kill/promote): FAV = src ≥ min(own, rand_best) − 1.0pp; FAIL = src within ±1.0pp of rand_mean or below.

## 4. Circuity LME→LoCoMo→LME (report only, no claim; confidence: LOW — informational)

| family,k | LME→LoCoMo src−own (pp), verdict | LOCO→LME src−own (pp), verdict | symmetric? |
|---|---|---|---|
| drop,32 | -1.87 FAV/FAIL | -0.17 FAV/FAIL | yes |
| drop,48 | -1.10 FAV | -1.40 FAV | yes |
| drop,64 | -1.16 FAV | -1.90 FAV | yes |
| alone,32 | -3.48 /FAIL | -1.74 /FAIL | yes |
| alone,48 | -3.89 /FAIL | +1.41 FAV/FAIL | NO |
| alone,64 | -5.06 /FAIL | +2.17 FAV/FAIL | NO |
| var,32 | +0.00 FAV/FAIL | +0.00 FAV/FAIL | yes |
| var,48 | +0.00 FAV/FAIL | +0.00 FAV/FAIL | yes |
| var,64 | +0.00 FAV/FAIL | +0.00 FAV/FAIL | yes |

Note: Spearman correlations are directionless scalars, so any directional asymmetry comes from target-side evaluation scale/interactions, not from the correlation itself.

## 5. Verdict counts

- Favorable: 14/18 cells; Fail: 14/18 cells.
- Neither/both flags can co-occur when rand_best ≈ rand_mean (rule overlap); table shows both.

