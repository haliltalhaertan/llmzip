# V52 LoCoMo Causal Spectral-Band Haar Result

Preregistered primary regime: `[SPECTRAL-SUBSPACE PRESERVATION LEAD]`

## Integrity / stop rules
- audit-clean denominator: 1535
- native reproduction: 23.654714666441% (frozen 23.654714666441%; abs error 0.000e+00)
- signed permutation exact control: PASS
- continuous norm max abs error: 4.441e-16
- continuous dot max abs error: 1.665e-15

## Primary causal estimand
- Native R@3: 23.654715%
- Frozen Full-Haar mean R@3: 13.770827%
- Within-band Haar mean R@3: 23.009932%
- L_full: 9.883888 pp
- L_band: 0.644782 pp
- rho = L_band/L_full: 0.065236
- verdict: `[SPECTRAL-SUBSPACE PRESERVATION LEAD]`

## Per-seed within-band R@3
- 55001: 23.445228%
- 55002: 24.100558%
- 55003: 22.049886%
- 55004: 23.324018%
- 55005: 22.129971%

## Secondary cross-band arm means
- HAAR_HIGH_MID64: 18.535959%
- HAAR_HIGH_LOW64: 17.011055%
- HAAR_MID_LOW64: 23.355323%

## Interpretation ceiling
This is a preregistered fixed-benchmark causal intervention. Secondary arms and diagnostics do not alter the primary rho decision bands. Cross-benchmark adjudication must wait for the corresponding LongMemEval arm.
