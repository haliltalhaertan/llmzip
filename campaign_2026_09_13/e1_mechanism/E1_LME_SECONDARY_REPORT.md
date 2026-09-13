# E1 LME secondary result — scalar archive geometry does not explain the SIGN advantage

Labels: **[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**.

Execution: GitHub Actions run `34758390297`, head `9cef2a044acc79258d901c5d9d95b6df1d4131ff`, conclusion SUCCESS.

This is a **secondary** E1 analysis using two already-committed surfaces. It is not the frozen raw-cache V2 E1 run.

## Input identity

- canonical T4C2 `V52_T4C2_question_level.csv` SHA256: `69c21b2ffaea1e92923bf3f0e83287e12d07a5f34b4b42afde1752d6b50b3b51`, matching the T4C2 post-run manifest;
- campaign `task1_extension_lme.json` SHA256: `682440a0e3329ebab223d45079455ff3b7f97122244cf077a969ce887dfe25da`, matching the campaign manifest.

Join coverage: 470/470 question IDs exact; all archive N values matched.
The joined mean SIGN-minus-centered-float delta reproduced the accepted LME headline: `+10.037943262411346 pp`.

## Result

Spearman association with per-question SIGN−float delta:

| pre-existing archive metric | rho |
|---|---:|
| `cv_sigma` | **−0.0096** |
| `top32_share` | **+0.0213** |
| `corr_off_mass` | −0.0856 |
| `corr_median_abs` | −0.0719 |
| `corr_p95_abs` | −0.0982 |
| sign entropy | +0.0336 |
| archive N | +0.0084 |

Pearson results tell the same qualitative story: no useful association for `cv_sigma`, top-32 variance share, entropy or N; continuous-coordinate correlation summaries are only weakly negative.

## Interpretation

The simple scalar story is not supported inside LongMemEval:

> “archives with more coordinate heterogeneity/concentration are the archives where SIGN gains more over float.”

That explanation would predict a visible association of SIGN−float delta with `cv_sigma` or top-variance share. It is essentially absent.

This **does not refute E1 V2**, because V2 was explicitly refined before this run to test a different object: subset-specific **joint sign-bit redundancy and ranking competition**. Existing round-1 evidence already showed why this distinction matters: high-variance axes are individually informative, yet the TOP subset is jointly more correlated, more duplicated, more tied, and retrieves worse.

Therefore the research bottleneck narrows to:

1. `TOP−BOT` sign-bit redundancy (`PHI_GAP`, binary effective-dimension gap);
2. query-specific strictly-closer-rival and gold-distance tie-mass gaps;
3. whether these quantities flip coherently in PerLTQA profile vs events, where SIGN advantage itself flips.

A global archive-wide variance CV is no longer a serious candidate mechanism.

## Epistemic limit

This is post-hoc/exploratory correlation analysis and is not causal evidence. No p-value or confirmatory claim is licensed. The raw-cache V2 E1 design remains unexecuted because the required frozen C96/qC cache surfaces are not currently available through the connected Drive/GitHub interfaces.

Task4F1 untouched.
