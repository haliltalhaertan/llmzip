# COMPARISON.md — Step 2: my numbers vs theirs

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Independence caveat (honest): I am NOT fully independent — commissioned by the party
whose work I audit; my brief quoted their numbers before I computed mine. Mitigation:
MY_NUMBERS.md was frozen from my own implementation (my_axis.py) before I opened their
code, and I never tuned my code to match (first run already agreed).

## Result: AGREEMENT on every tested cell (VERIFIED)

Budget-matched Delta (sign − float, pp). Mine (6 decimals) vs theirs (4 decimals).
All differences are at the 5th decimal — i.e. inside their display rounding.

| bench   | m  | mine        | theirs    | \|diff\| |
|---------|----|-------------|-----------|--------|
| LME     | 8  | -11.847912  | -11.8479  | 0.000012 |
| LME     | 32 | -6.300827   | -6.3008   | 0.000027 |
| LME     | 48 | +0.290780   | +0.2908   | 0.000020 |
| LME     | 64 | +3.678093   | +3.6781   | 0.000007 |
| LME     | 96 | +10.053783  | +10.0538  | 0.000017 |
| PerLTQA | 8  | -16.400634  | -16.4006  | 0.000034 |
| PerLTQA | 32 | -11.701487  | -11.7015  | 0.000013 |
| PerLTQA | 48 | -9.469667   | -9.4697   | 0.000033 |
| PerLTQA | 64 | -8.266459   | -8.2665   | 0.000041 |
| PerLTQA | 96 | -6.274728   | -6.2747   | 0.000028 |

Extension (my own code, VERIFIED, locator: verify_rt_loc.py) — LoCoMo + REALTALK,
Delta and CLAIM-2 bot-top, m in {24,32,48,64,80,96}: all agree to 4dp
(max |diff| 0.00005). Controls reproduced: REALTALK m96 +5.300077 (brief control:
+5.300077, exact); LoCoMo m96 +6.655046 (no control was quoted for LoCoMo).

## Consequence

No Step-2 finding against the numbers. The comparison step produced ZERO
disagreements, so per the audit brief there is no "which side is right" diagnosis
to make. All kills below come from Steps 3–5 (code semantics, guard analysis,
and interpretation), not from recomputation mismatch.

Locators: MY_NUMBERS.md, my_axis.py, verify_rt_loc.py (all in this directory);
their evidence: /mnt/c/.../axis-budget/evidence/axis_budget_results.json (read-only).
