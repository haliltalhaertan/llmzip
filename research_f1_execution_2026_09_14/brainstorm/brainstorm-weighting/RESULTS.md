# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# RESULTS — weighting framing (all VERIFIED this run by weighting.py/posthoc.py)

## Control gate (must pass; PASSED on all four)

alpha=0 reproduces FLOAT exactly; sign arm reproduces SIGN headlines:

| benchmark | sign (VERIFIED) | float (VERIFIED) | Delta (VERIFIED) | frozen CLAIM |
|---|---|---|---|---|
| LongMemEval (n=470) | 0.542134 | 0.441596 | +10.0538 pp | +10.053783 PASS |
| LoCoMo (n=1535) | 0.237907 | 0.171356 | +6.6550 pp | +6.655046 PASS |
| REALTALK (n=705) | 0.225535 | 0.172534 | +5.3001 pp | +5.300077 PASS |
| PerLTQA (n=8265) | 0.488945 | 0.551692 | -6.2747 pp | -6.274728 PASS |
| PerLTQA profile (333) | 0.506857 | 0.303303 | +20.3554 pp | +20.36 PASS |
| PerLTQA social (844) | 0.749309 | 0.757109 | -0.7800 pp | -0.780 PASS |
| PerLTQA dialogues (2742) | 0.085179 | 0.100195 | -1.5017 pp | -1.502 PASS |
| PerLTQA events (4346) | 0.691755 | 0.815693 | -12.3937 pp | -12.394 PASS |

## 1. Spectral quantity R = mean_q Pearson(log v, s), s = q*gold-centroid (FROZEN primary)

| group | R +/- 95%CI | Rabs | Rgold | cent |
|---|---|---|---|---|
| LME | +0.3630 +/- 0.0108 | +0.4332 | +0.3917 | 18.21 |
| LoCoMo | +0.2035 +/- 0.0083 | +0.4923 | +0.4381 | 22.23 |
| REALTALK | +0.2472 +/- 0.0137 | +0.4812 | +0.4385 | 20.48 |
| PerLTQA | +0.3398 +/- 0.0031 | +0.4353 | +0.3851 | 18.96 |
| profile | +0.1808 +/- 0.0122 | +0.3562 | +0.3144 | 21.86 |
| social | +0.3786 +/- 0.0069 | +0.4174 | +0.3302 | 21.56 |
| dialogues | +0.2579 +/- 0.0063 | +0.4612 | +0.4166 | 15.02 |
| events | +0.3960 +/- 0.0028 | +0.4286 | +0.3814 | 20.72 |

Note (VERIFIED): R is positive EVERYWHERE — signed support always leans
high-variance in absolute terms. Only relative order was ever interpretable.

## 2. Whitening sweep FR@3, alpha = 0, 0.5, 1, 1.5, 2 (FROZEN intervention)

| group | a0.0 | a0.5 | a1.0 | a1.5 | a2.0 | sign |
|---|---|---|---|---|---|---|
| LME | 0.4416 | 0.5152 | 0.5574 | 0.5735 | 0.5895 | 0.5421 |
| LoCoMo | 0.1714 | 0.2188 | 0.2625 | 0.3095 | 0.3218 | 0.2379 |
| REALTALK | 0.1725 | 0.1991 | 0.2291 | 0.2537 | 0.2556 | 0.2255 |
| PerLTQA | 0.5517 | 0.5708 | 0.5658 | 0.5355 | 0.4976 | 0.4889 |
| profile | 0.3033 | 0.3964 | 0.4745 | 0.5225 | 0.5556 | 0.5069 |
| social | 0.7571 | 0.7903 | 0.7938 | 0.7773 | 0.7216 | 0.7493 |
| dialogues | 0.1002 | 0.1048 | 0.1050 | 0.1003 | 0.0909 | 0.0852 |
| events | 0.8157 | 0.8355 | 0.8191 | 0.7642 | 0.7062 | 0.6918 |

Sign advantage D(alpha) = sign - whitened, in pp:

| group | D0.0 | D0.5 | D1.0 | D1.5 | D2.0 |
|---|---|---|---|---|---|
| LME | +10.05 | +2.69 | -1.53 | -3.14 | -4.73 |
| LoCoMo | +6.66 | +1.91 | -2.46 | -7.16 | -8.39 |
| REALTALK | +5.30 | +2.64 | -0.36 | -2.82 | -3.01 |
| PerLTQA | -6.27 | -8.18 | -7.68 | -4.66 | -0.86 |
| profile | +20.36 | +11.05 | +3.24 | -1.57 | -4.87 |
| social | -0.78 | -4.10 | -4.45 | -2.79 | +2.77 |
| dialogues | -1.50 | -1.96 | -1.98 | -1.51 | -0.58 |
| events | -12.39 | -14.37 | -12.74 | -7.24 | -1.44 |

Two universal facts (VERIFIED): (i) a0 -> a0.5 RISES in all 8 rows (mild
de-weighting of top axes helps everywhere, +0.5 to +9.3 pp); the separation
emerges at alpha >= 1. (ii) |D(alpha)| SHRINKS from alpha=1 to alpha=2 in all
8 rows — whitening makes the two arms agree more, from whichever side.

## 3. Post-hoc Q-WHITE = Pearson(log v, s/v) + alignment confound (EXPLORATORY, not frozen)

| group | Q-WHITE | align(q,gold cos) |
|---|---|---|
| LME | +0.1657 +/- 0.0134 | +0.7067 |
| LoCoMo | +0.0450 +/- 0.0065 | +0.3166 |
| REALTALK | +0.0650 +/- 0.0116 | +0.3536 |
| PerLTQA | +0.1718 +/- 0.0029 | +0.5624 |
| profile | +0.0131 +/- 0.0112 | +0.3010 |
| social | +0.1572 +/- 0.0078 | +0.6535 |
| dialogues | +0.2040 +/- 0.0057 | +0.3525 |
| events | +0.1665 +/- 0.0033 | +0.6972 |

align tracks Rraw nearly perfectly (LME/events high, profile/LoCoMo low):
raw R is largely an alignment-STRENGTH artefact, not a pure location
measure. Q-WHITE fixes LME only to a tie with PerLTQA (0.166 vs 0.172,
CIs touching) and misorders dialogues highest — the observational quantity
does not cleanly determine Delta in either form.
