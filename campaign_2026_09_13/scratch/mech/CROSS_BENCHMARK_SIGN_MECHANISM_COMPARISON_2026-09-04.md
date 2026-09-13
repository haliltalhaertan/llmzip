# V52 SIGN Mechanism — LongMemEval vs LoCoMo Comparison

**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

Date: 2026-09-04
Status: `[POST-HOC EXPLORATORY — CROSS-BENCHMARK MECHANISM REPLICATION LEAD]`

## Core comparison

| Diagnostic | LongMemEval | LoCoMo | Cross-benchmark reading |
|---|---:|---:|---|
| High32 gold−nongold same-sign advantage | ~0.230 | 0.0880 | same direction; much weaker absolute separation on LoCoMo |
| Mid32 advantage | ~0.187 | 0.0875 | same direction; High/Mid nearly tied on LoCoMo |
| Low32 advantage | ~0.164 | 0.0805 | lowest band-average relevance separation on both |
| High32 pairwise discrimination | ~0.911 | 0.7269 | strongest third on both |
| Mid32 pairwise discrimination | ~0.865 | 0.7221 | middle on both |
| Low32 pairwise discrimination | ~0.834 | 0.6993 | weakest third on both |
| High32 mean abs bit correlation | ~0.067 | 0.0380 | most redundant third on both |
| Mid32 mean abs bit correlation | ~0.046 | 0.0280 | intermediate on both |
| Low32 mean abs bit correlation | ~0.036 | 0.0267 | least correlated third on both |
| High32 unique-code fraction | ~0.892 | 0.9966 | head less unique on both; effect far smaller on LoCoMo |
| Mid32 unique-code fraction | ~0.981 | 0.9995 | high uniqueness |
| Low32 unique-code fraction | ~0.992 | 0.9993 | high uniqueness; Mid/Low ordering nearly saturated on LoCoMo |
| High32 Fractional R@3 | ~25.3% | 8.595% | poor top-k despite strongest pairwise separation |
| Mid32 Fractional R@3 | ~34.3% | 11.171% | tailward improvement |
| Low32 Fractional R@3 | ~33.4% | 14.046% | tailward improvement; Low exceeds Mid on LoCoMo |
| High+Mid64 Fractional R@3 | ~43.2% | 16.634% | substantial complementarity |
| Mid+Low64 Fractional R@3 | ~50.0% | 21.767% | beats High+Mid on both |
| Full96 Fractional R@3 | ~54.2% | 23.655% | best configuration on both |
| High wrong/tie → Full rescue | ~55.6% | 51.396% | strong replication |
| High correct → Full degrade | ~4.4% | 10.407% | same asymmetry, but degradation larger on LoCoMo |
| High wrong/tie → High+Mid rescue | ~46.3% | 41.455% | strong directional replication |
| High wrong/tie → High+Low rescue | ~46.0% | 40.125% | strong directional replication |
| High+Mid wrong/tie → Full rescue | ~30.7% | 29.999% | strikingly close replication |
| SIGN positive hard-negative margin questions | ~41.6% | 14.007% | same advantage direction vs cosine, very different absolute regime |
| centered cosine positive-margin questions | ~36.5% | 11.075% | same relative ordering, much lower on LoCoMo |

## What replicated

1. The first spectral third is strongest for average gold-vs-nongold discrimination but is also the most redundant.
2. Mid/tail thirds are individually weaker in pairwise discrimination yet improve top-k retrieval when combined.
3. Mid+Low outperforms High+Mid in Fractional R@3 on both benchmarks.
4. Adding the remaining bits rescues a large fraction of pairs that High32 cannot resolve, while destroying a much smaller fraction of High32-correct pairs.
5. The strongest quantitative replication is the final-tail rescue: when High+Mid is still wrong/tied, adding Low32 rescues ~30.7% on LongMemEval and 29.999% on LoCoMo.

## What did not replicate cleanly

1. The scale of head redundancy is much smaller on LoCoMo because 32-bit codes are already almost unique.
2. LongMemEval Mid32 slightly beats Low32 in top-3 R@3, while LoCoMo Low32 clearly beats Mid32.
3. LoCoMo High32-to-Full degradation (~10.4%) is materially larger than LongMemEval (~4.4%).
4. Hard-negative positive-margin fractions are much lower on LoCoMo. The LongMemEval-specific observation that SIGN-winning questions can move the average SIGN margin positive should not be promoted to a cross-benchmark claim without a dedicated reproduction.

## Current mechanism statement

`[CROSS-BENCHMARK MECHANISM REPLICATION LEAD — CAUSAL TEST PENDING]`

The best-supported common mechanism is narrower than a generic 'anisotropy helps' story:

> Archive-local SVD-ordered sign hashing appears to combine a stronger but more redundant spectral head with weaker, less-correlated mid/tail binary information. The mid/tail bits disproportionately repair hard gold-vs-nongold comparisons that the head cannot resolve, so equal-weight Full96 Hamming can outperform schemes that emphasize average pairwise separation.

This remains a post-hoc exploratory mechanism. It does not establish that exact individual PC axes are causal. The preregistered next experiment is the within-spectral-band Haar intervention, which separates exact-axis dependence from preservation of High/Mid/Low subspaces.
