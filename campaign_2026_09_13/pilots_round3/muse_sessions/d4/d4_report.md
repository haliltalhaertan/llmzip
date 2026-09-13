[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

> **ORCHESTRATOR ERRATA (2026-09-13, after D5 adversarial review).** C6: language is CONFIRMATORY-ONLY (n=2 fresh draws); seed-numeral collision flagged (43004/05 are LoCoMo-fresh but LME gate-seed numerals; LME fresh set is 44001/44002); full-5-seed LME contrast noted (strict separation fails on all five, robust on fresh 44001/02 draws). See ERRATA_ROUND3_D5.md §C6.

# DENEY 4: fresh-Q confirmatory check of the mixing-disparity ordering

[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Independent analyst session. Read-only outside /tmp/d4/; no network. Nothing appended to /mnt/c.
Pipeline: `d4.py` (LoCoMo, mirrors `round2/session_scripts/r2c_replicate.py` verbatim),
`d4_lme.py` (LME E4, mirrors `pilot_corrections.py` E4 section verbatim).

## 1. LoCoMo gates (must pass before trusting fresh numbers)

- Native recompute: 0.23654714666441054 vs anchor 0.23654714666441054, diff 0.0 — PASS (<=1e-12).
- Valid audit questions: 1535 (frozen expects 1535). Alignment OK, Q-block identity OK.
- Replication of machinery (MATCHED original seeds, tolerance 1e-12): all diff 0.0 — PASS
  - 43001: 0.23565226250405402 / 43002: 0.23022749129263786 / 43003: 0.24242457144737273

## 2. LoCoMo fresh draws (seeds 43004, 43005), fractional R@3

| seed  | MATCHED (gap pp) | RANDPAIR (gap pp) | ANTIMATCHED (gap pp) |
|-------|------------------|-------------------|----------------------|
| 43004 | 0.23164713997335187 (−0.4900) | 0.21847919136068208 (−1.8068) | 0.18502016649123373 (−5.1527) |
| 43005 | 0.22965980888456458 (−0.6887) | 0.21616614492998860 (−2.0381) | 0.20731888424109157 (−2.9228) |

Means — original (43001-03): MATCHED 0.23610144 (−0.0446pp), RANDPAIR 0.21300568 (−2.3541pp),
ANTIMATCHED 0.19371538 (−4.2832pp).
Means — fresh (43004/05): MATCHED 0.23065347 (−0.5894pp), RANDPAIR 0.21732267 (−1.9224pp),
ANTIMATCHED 0.19616953 (−4.0378pp). Mean ordering matched > randpair > antimatched holds on both.

Strict-separation question on FRESH seeds:
- min(MATCHED_fresh) = 0.22965981 > max(RANDPAIR_fresh) = 0.21847919 → HOLDS
- min(RANDPAIR_fresh) = 0.21616614 > max(ANTIMATCHED_fresh) = 0.20731888 → HOLDS
- min(MATCHED_fresh) > max(ANTIMATCHED_fresh) → HOLDS
- Full strict ordering min(M) > max(R) > min(R) > max(A) holds with margin ~1.1pp / ~0.9pp.
- Original seeds were also strictly separated (min M 0.23023 > max R 0.22029 > max A 0.19937).
- Note: fresh MATCHED mean (−0.59pp) sits slightly below the original mean (−0.04pp) because
  original seed 43003 ran above native (+0.59pp); both fresh MATCHED draws remain within ~0.7pp
  of native, i.e. the "matched ≈ native" character survives. Fresh ANTI seed 43004 (−5.15pp)
  is the most damaging draw in the combined 5-seed set.

Verdict (LoCoMo): the matched > randpair > antimatched ordering SURVIVES new random draws,
with strict per-seed separation on the fresh Q blocks.

## 3. LME mirror (E4 dose-response, fresh pairing/Q seeds 44001/44002; gate: all 15 pilot E4 values diff 0.0 — PASS)

| seed  | matched (gap pp) | random (gap pp) | antimatched (gap pp) |
|-------|------------------|-----------------|----------------------|
| 44001 (fresh) | 0.53882624 (−0.3149) | 0.52149291 (−2.0482) | 0.49287234 (−4.9103) |
| 44002 (fresh) | 0.53832447 (−0.3651) | 0.51085993 (−3.1115) | 0.48492908 (−5.7046) |

Strict-separation on FRESH LME seeds: min(matched)=0.53832 > max(random)=0.52149 → HOLDS;
min(random)=0.51086 > max(anti)=0.49287 → HOLDS. Full strict ordering holds.
Contrast: on ORIGINAL seeds 43001-03 strict separation FAILED (seed 43003 random 0.51878 beat
matched 0.51736; min random 0.49135 < max anti 0.50380). The fresh draws show a cleaner
disparity ordering than the original draws on LME.

## 4. Caveats

- n=2 fresh draws per benchmark: confirmatory signal only, not a claim; no preregistration.
- The R2D confound (pairing derived from same variance ordering as axis assignment) is NOT
  resolved by this session — fresh Q only checks robustness to new random draws.
- LME "matched" pairs ascending-adjacent variances (stable argsort), LoCoMo pairs
  descending-adjacent; pair sets are identical up to pair order, Q-to-pair assignment differs.
  Both pipelines were mirrored bit-for-bit from their respective frozen sources (diff 0.0).

## Artifacts

- /tmp/d4/d4.py, /tmp/d4/d4_lme.py (pipelines)
- /tmp/d4/d4_details.json (LoCoMo + LME numbers), /tmp/d4/d4_lme_details.json (LME extract)
