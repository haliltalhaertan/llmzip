[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# RECOMPUTED COMPARISON — marginal / index-only / full-pipeline

PREPARED, NOT ACCEPTED. All numbers recomputed in `verify_commonmode.py`
(ALL CHECKS PASSED); machine receipts in `evidence/results.json`.
Conventions: P = 44,220,235 B (median per-archive shared projector,
format (a) f32+structured vocab); N = archive size; S0 = arm-specific index
shared bytes (33 / 98,390 / 135,325). Panel means are mean-of-per-archive-costs
over the frozen 470 N (min 396, max 616, mean 492.78, total 231,606 vectors —
VERIFIED C1 from `docs/v52/task4c2/V52_T4C2_feature_geometry.csv`).

Formulas: index-only eff = marginal + S0/N; full-pipeline eff = marginal +
(P + S0)/N. FLOAT-full uses S0 = 0 and marginal 384.

## (a) Marginal bytes/vector (L-088 cap definition)

| Arm | Marginal | Note |
|-----|---:|------|
| SIGN96 | 12 | within cap |
| PQ96 / OPQ_PQ96 | 12 | within cap (S0 outside cap, reported separately) |
| FLOAT96_CENTERED | 384 | reference only, outside matched set (prereg draft :135) |

VERIFIED source: EVIDENCE.json `serialization_S_of_N` slopes (prior session).

## (b) Index-only effective (arm-specific shared ONLY — pipeline excluded)

| Arm | Formula | @N=500 | Panel mean (470) | Range over 470 |
|-----|---------|-------:|-----------------:|---------------:|
| SIGN96 | 12+33/N | 12.07 | 12.067 | 12.05–12.08 |
| PQ96 | 12+98390/N | 208.78 | 212.44 | 171.72–260.46 |
| OPQ_PQ96 | 12+135325/N | 282.65 | 287.69 | 231.68–353.73 |
| FLOAT96 | 384 | 384.00 | 384.00 | 384.00 |

Conclusion under (b): SIGN96 is the cheapest arm at EVERY N ≥ 1 (12.07 vs 384
vs ~209 vs ~283 at N=500). No break-even needed; SIGN dominates.

## (c) Full-pipeline effective (pipeline INCLUDED, per-archive fit as measured)

| Arm | Formula | @N=500 | @N*=118,872 |
|-----|---------|-------:|------------:|
| SIGN96 | 12+(P+33)/N | 88,452.54 | 384.00 |
| FLOAT96_CENTERED | 384+P/N | 88,824.47 | 756.00 |
| PQ96 | 12+(P+98390)/N | 88,649.25 | 384.83 |
| OPQ_PQ96 | 12+(P+135325)/N | 88,723.12 | 385.14 |

Conclusion under (c): SIGN96 is STILL the cheapest arm at every N ≥ 1 —
by exactly 372 − 33/N bytes/vector over FLOAT (VERIFIED D2: holds at
N ∈ {1, 396, 500, 616, N*, 3685020}), ~197 B over PQ and ~271 B over OPQ at
N=500 (VERIFIED D3). The pipeline dominates every arm equally; the residual
ordering is just the arm-specific delta.

## Where the brief's headline numbers come from (and their conventions)

| Brief claim | Recomputed here | Convention note |
|-------------|----------------:|-----------------|
| median eff ~88,886 B/vec | 88,886.36235 (VERIFIED B1) | median-of-per-archive-effective; ratio-of-medians gives 90,257 (+1.5% — Attack 2's caveat stands) |
| range 80,267–104,464 | 80,266.51–104,463.62 (VERIFIED B1) | rounding only |
| break-even ~118,900 | 118,872 = ceil(P/372) (VERIFIED D1) | solves SIGN-full = FLOAT-**bare**; baseline unobtainable (see verdict) |
| ~234× MORE than raw float32 | 231.47 = 88886.36/384 | median convention; immaterial spread, same order |
| codes ~0.013% of bytes | 12/88886 = 0.0135% | exact |

## Which conclusions survive each accounting, and which flip

1. "SIGN96 stores 234× MORE than raw float32" — FLIPS. The comparator
   (bare 384 B vectors with no pipeline) cannot exist in this programme: a
   float96 vector for a document is obtainable ONLY via the fitted pipeline
   (§1). Against the obtainable baseline the sign is reversed at every N.
2. "Break-even needs ~118,900 vectors/archive" — REINTERPRETED. As
   SIGN-full vs FLOAT-bare it is arithmetically correct and practically
   vacuous. The same integer reappears with honest meaning: N ≳ 118,872 is
   where P/N ≲ 372, i.e. where the shared cost stops dominating and the 32×
   payload ratio becomes visible. Versus the programme float baseline there
   is NO break-even: SIGN is cheaper ∀ N ≥ 1.
3. "Index-only: 12.07 (SIGN) vs ~288 (OPQ)" — SURVIVES and EXTENDS: full
   panel means are SIGN 12.067 / PQ 212.44 / OPQ 287.69 / FLOAT 384.
4. "Codes are ~0.013% of persisted bytes; system stores ~89 kB/vector" —
   SURVIVES UNCHANGED. This was never a comparison claim; common-mode status
   does not shrink an absolute footprint. Every pipeline arm stores ~89 kB
   (f32) per vector at N≈500.
5. "Marginal-qualified 12-byte accounting is honest" (L-088) — SURVIVES.
   Nothing here changes the cap definition; it sharpens what "reported
   separately" must contain (the whole P, for every arm equally).
