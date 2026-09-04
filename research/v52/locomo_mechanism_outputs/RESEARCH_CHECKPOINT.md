# V52 LoCoMo SIGN Mechanism Replication — Post-hoc Exploratory Checkpoint

Verdict: `[CROSS-BENCHMARK MECHANISM REPLICATION LEAD]`

## Provenance
- Dataset SHA-256: `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4` (exact byte verification PASS)
- Audit manifest SHA-256: `90a4e94c9247d8ace7aaf62acdda7315744b111d84e42658cccfeb0a3c89df06` (20 exact files PASS)
- Frozen 4D script SHA-256 reference: `3f7f091fadc88dfcc1f68f38d6df10607d05d1e416d048fe776929a9a7b185a7`
- Audit-clean evidence-valid denominator: 1535
- Frozen Full96 native R@3 reproduction: 23.655% vs frozen 23.655%; abs error=0.000e+00; PASS

## Spectrum diagnostics
| band | Fractional R@3 | same-sign gold−nongold advantage | pairwise discrimination | unique-code | mean |corr| |
|---|---:|---:|---:|---:|---:|
| High32 | 8.595% | 0.0880 | 0.7269 | 0.9966 | 0.0380 |
| Mid32 | 11.171% | 0.0875 | 0.7221 | 0.9995 | 0.0280 |
| Low32 | 14.046% | 0.0805 | 0.6993 | 0.9993 | 0.0267 |
| HighMid64 | 16.634% | nan | nan | 0.9995 | 0.0310 |
| HighLow64 | 18.620% | nan | nan | 0.9995 | 0.0298 |
| MidLow64 | 21.767% | nan | nan | 0.9995 | 0.0269 |
| Full96 | 23.655% | 0.0853 | 0.7934 | 0.9995 | 0.0287 |

## Hard-negative rescue
- High32 wrong/tie → Full96 correct: 51.396%
- High32 correct → Full96 wrong/tie: 10.407%
- High32 wrong/tie → High+Mid correct: 41.455%
- High32 wrong/tie → High+Low correct: 40.125%
- High+Mid wrong/tie → Full96 correct: 29.999%

## Hard-negative margins
- Native SIGN positive-margin questions: 14.007%
- Centered cosine positive-margin questions: 11.075%
- Centered cosine Fractional R@3 (post-hoc reference): 16.826%

## Epistemic status
This analysis is post-hoc and exploratory. It tests whether the LongMemEval coarse→fine / tail-rescue signature transfers to LoCoMo. It is not preregistered, not a population p-value claim, and does not establish the causal mediator. The next causal experiment must be preregistered before outcome access.
