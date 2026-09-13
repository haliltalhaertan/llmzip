# E1 V2 implementer test receipt

Status: **IMPLEMENTER / SYNTHETIC METRIC CHECK ONLY — NOT INDEPENDENT REVIEW, NOT E1 OUTCOME**.

Before any frozen benchmark E1 run, the V2 joint-geometry core was exercised on a synthetic 1000×96 matrix in which 32 high-variance coordinates were generated from four shared latent variables, 32 middle coordinates were independent moderate-variance variables, and 32 low coordinates were independent low-variance variables.

Observed from the candidate metric definitions:

- `PHI_GAP = +0.0500669191`;
- `SIGN_EFFDIM_TOP64 = 14.3421`;
- `SIGN_EFFDIM_BOT64 = 60.1197`;
- `EFFDIM_GAP = +45.7777`.

Thus the metrics point in the intended direction when TOP contains deliberately redundant high-variance sign structure. A separate shape/zero-query check confirms malformed C dimensions are rejected and zero qC yields `NOT_EVALUABLE` (`None`) query geometry rather than division by zero.

This does not test the scientific hypothesis and contains no benchmark outcomes.

Task4F1 untouched.
