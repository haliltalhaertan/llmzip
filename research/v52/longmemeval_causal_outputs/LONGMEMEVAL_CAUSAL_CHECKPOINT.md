# V52 LongMemEval Causal Spectral-Band Haar Result (Sharded Exact Execution)

Preregistered primary regime: `[SPECTRAL-SUBSPACE PRESERVATION LEAD]`

## Integrity / stop rules
- primary questions: 470 / 470 unique
- shards: 5 complete
- dataset SHA-256: `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`
- native reproduction: 54.197517730496% (frozen 54.197517730496%; abs error 0.000e+00)
- signed permutation exact control: PASS (per question before each shard result)
- continuous norm max abs error: 5.551e-16
- continuous dot max abs error: 8.882e-16

## Primary causal estimand
- Native R@3: 54.197518%
- Frozen Full-Haar mean R@3: 38.271667%
- Within-band Haar mean R@3: 51.922872%
- L_full: 15.925851 pp
- L_band: 2.274645 pp
- rho: 0.142827
- verdict: `[SPECTRAL-SUBSPACE PRESERVATION LEAD]`

## Per-seed within-band R@3
- 55001: 53.019504%
- 55002: 51.446099%
- 55003: 51.525532%
- 55004: 51.780496%
- 55005: 51.842730%

## Secondary cross-band arm means
- HAAR_HIGH_MID64: 49.239858%
- HAAR_HIGH_LOW64: 45.097163%
- HAAR_MID_LOW64: 51.385426%

## Interpretation ceiling
This sharded execution is mathematically identical to the preregistered single-runner execution; shard assignment changes only scheduling. Secondary arms do not alter the primary rho decision bands.
