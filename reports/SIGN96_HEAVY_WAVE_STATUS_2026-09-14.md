# SIGN96 heavy retrieval wave — status report (2026-09-14)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

This report consolidates completed heavy-benchmark evidence without changing any benchmark protocol or result artifact.

## Completed wave: BRIGHT reasoning-intensive retrieval

GitHub Actions run `34872308761` completed successfully for all eight frozen tasks, covering 861 queries and 519,391 documents across task corpora.

- Recall@3: SIGN96 W/T/L = 4/0/4; macro delta = **-0.205 pp**; median delta = -0.014 pp.
- nDCG@10: SIGN96 W/T/L = 2/0/6; macro delta = **-0.166 pp**; median delta = -0.106 pp.
- Largest Recall@3 movement: Biology **-1.699 pp**.
- Other Recall@3 deltas are close to zero: Earth Science -0.080, Economics +0.000, Psychology -0.029, Robotics +0.163, StackOverflow +0.073, Sustainable Living +0.050, Pony -0.114 pp.

Interpretation: the large positive NanoBEIR effects do not generalize as an average advantage to the BRIGHT reasoning-intensive distribution. The average effect is near zero/slightly harmful.

## Completed wave: BIRCO complex-objective retrieval

GitHub Actions run `34872867443` completed successfully for all five frozen task families, covering 410 queries and 25,331 query-specific candidate rows.

- Recall@3: SIGN96 W/T/L = 1/1/3; macro delta = **-0.818 pp**; median delta = -1.092 pp.
- nDCG@10: SIGN96 W/T/L = 1/0/4; macro delta = **-1.106 pp**; median delta = -2.045 pp.
- WTB is the clear exception: Recall@3 **+2.600 pp**, nDCG@10 **+5.739 pp**.
- Relic: -3.300 / -2.045 pp.
- Clinical Trial: -1.092 / -2.598 pp.
- ArguAna: -2.300 / -1.572 pp.
- Doris-Mae: Recall@3 +0.000 pp; nDCG@10 -5.053 pp.

Interpretation: complex, query-specific retrieval objectives mostly favor FLOAT96, but the WTB reversal shows that difficulty alone does not determine the sign of the effect.

## Full BEIR wave 1: completed scientific results

Corrected full-BEIR run `34872583699` preserves blind ranking freeze and scores only query IDs belonging to the requested test split after qrels are opened.

Completed scientific results so far:

| Task | Full corpus docs | Evaluated queries | Δ Recall@3 pp | Δ nDCG@10 pp |
|---|---:|---:|---:|---:|
| SciFact | 5,183 | 300 | **+1.924** | **+2.704** |
| ArguAna | 8,674 | 1,401 | **-2.405** | **-1.625** |
| SCIDOCS | 25,657 | 1,000 | **-0.103** | **-0.276** |
| NFCorpus | 3,633 | 323 | **+0.079** | **+0.159** |

Important comparison with NanoBEIR: the very large NanoSciFact +18.1 pp Recall@3 gain shrinks to +1.924 pp on the full SciFact corpus while preserving direction. Nano effects can therefore substantially overstate effect magnitude, even when the qualitative direction survives.

## Full BEIR infrastructure-only incomplete tasks

No scientific result is licensed yet for these tasks:

- FiQA: first attempt failed during dataset download with a connection-refused network error before representation/ranking outcomes. It has been re-run without changing the scientific protocol.
- TREC-COVID: first attempt loaded 171,332 documents, then its hosted runner received SIGTERM / exit 143 during representation work before rankings/qrels/results. It has been re-run with the unchanged scientific protocol. If the same resource failure repeats, any subsequent memory engineering must preserve the exact mathematical transformation and must be disclosed separately.

These infrastructure failures must not be counted as wins, losses, or null results.

## Current scientific picture

The accumulated evidence does not support universal SIGN96 superiority. It supports a **regime-dependent binarization effect**:

1. Some ordinary retrieval tasks show substantial SIGN96 gains, especially in NanoBEIR.
2. Full-corpus replication can preserve direction while sharply reducing magnitude.
3. BRIGHT reasoning-intensive retrieval is approximately neutral to slightly unfavorable on average.
4. BIRCO complex-objective retrieval is unfavorable on average, with a strong WTB exception.

The highest-value next research target is a relevance-free, pre-outcome predictor of whether a corpus/query geometry lies in a SIGN-helpful or SIGN-harmful regime. Candidate geometric variables include coordinate-margin distribution around zero, sign-code entropy, collision/tie structure, anisotropy, hubness, and centered cosine-vs-Hamming neighborhood stability.

`96 bits = 12 active SIGN code bytes` remains an active-code statement only and is not a whole-system storage-cost claim. None of these repository runs is an external independent reproduction.
