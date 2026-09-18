[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# DELIVER 4 — Caveat propagation (PREPARED, NOT ACCEPTED)

Mandatory caveat (VERIFIED `audit_v52_t4c2/AUDIT_REPORT.md:24-26,32-33`):
the SIGN-vs-centered-float lead is concentrated — W/T/L 122/304/44, median
paired gap 0.0 pp, 64.7% ties; removing the 50 largest positive contributors
leaves ~+1.28 pp of +10.04 pp. Condition 3: "The concentration caveat above
must accompany further communication of the SIGN-vs-centered-FLOAT result."
The writer of that caveat is the independent auditor; I only relay it.

## Every quoter found (VERIFIED `grep -rn "10\.037943\|10\.0379\|10\.04"` over HEAD worktree)

| # | Locator (HEAD blob) | Quotes | Caveat travels? (VERIFIED) |
|---|---|---|---|
| 1 | `audit_v52_t4c2/AUDIT_REPORT.md:18` | `G = … = +10.037943 pp` | YES — caveat at lines 24–26, condition at 32–33. Canonical carrier. |
| 2 | `docs/v52/task4c2/V52_T4C2_COMPUTE_REPORT.md:19,23` | `S - Fc = +10.037943 pp` ×2 | PARTIAL — W/T/L + median gap present at lines 39–40, but the 64.7%-tie framing and the top-50-removal → ~+1.28 pp sensitivity are absent. |
| 3 | `docs/PROJECT_STATUS_2026-08-27.md:21` | `S - Fc: +10.037943 pp` | NO — nearest text (lines 29–31) notes fewer duplicate codes/ties vs ITQ but never states concentration, ties share, or top-50 sensitivity. |
| 4 | `prompts/V52_TASK_4C2_INDEPENDENT_ADVERSARIAL_AUDIT_PROMPT_2026-08-27.md:43,141,171,255,261` | `+10.037943` / `+10.04` ×several | YES-in-function — pre-audit prompt that *commissions* the sensitivity probe (lines 171, 261); predates the auditor's caveat, not a downstream communication of the result. No change proposed. |
| 5 | `prompts/V52_TASK_4C2_INDEPENDENT_ADVERSARIAL_AUDIT_PROMPT_V2_2026-08-27.md:115,274` | `+10.037943` / `+10.04` | Same as 4 — commissions the probe. No change proposed. |
| 6 | `prompts/V52_TASK_4C3_COORDINATE_AXIS_CAUSAL_PROBE_2026-08-27.md:36,234` | `+10.037943 pp` + `+10.04 pp … about +1.28 pp` | YES — line 234 carries the top-50 sensitivity explicitly. |
| 7 | `docs/v52/task4c2/V52_T4C2_POST_RUN_MANIFEST.json:14` (`S_minus_Fc_pp: 10.037943262411343`) | exact value | N/A — machine-readable data artifact, not prose communication; caveat lives in the paired compute report + audit report. No change proposed. |
| 8 | `audit_v52_t4c1/AUDIT_REPORT.md:82` (`+10.1869 pp`) | different contrast (vs UNcentered float) | OUT OF SCOPE but consistent (see arithmetic below). The concentration caveat was written for the centered-float contrast; whether it extends to the uncentered contrast is a Head Researcher/auditor question, not answered here. |

Excluded (VERIFIED not a quoter): `docs/v52/task4d/TASK4D_ACCEPTED_CHECKPOINT_2026-08-29.md:79`
`+10.044872 pp` is a LoCoMo cell value, not this LongMemEval result.

## Proposed caveat sentences (minimal, additive)

For `docs/v52/task4c2/V52_T4C2_COMPUTE_REPORT.md` (append to § Question-level
robustness; target carries no sidecar — VERIFIED not in the 20-sidecar list):
```
Concentration caveat (audit-mandated, audit_v52_t4c2/AUDIT_REPORT.md:24-26): the +10.04 pp lead is concentrated — 64.7% of questions tie (W/T/L 122/304/44, median gap 0.0 pp); removing the 50 largest positive contributors leaves about +1.28 pp. Descriptive composition sensitivity only, not population inference.
```
For `docs/PROJECT_STATUS_2026-08-27.md` (append after line 23's gap list; dated
snapshot — Head Researcher may prefer an erratum file instead):
```
Concentration caveat (audit-mandated, audit_v52_t4c2/AUDIT_REPORT.md:24-26): the S–Fc +10.04 pp lead is concentrated — W/T/L 122/304/44, median gap 0.0 pp, 64.7% ties; top-50 removal leaves ~+1.28 pp. Descriptive only, not population inference; no causal mechanism is licensed.
```

## Arithmetic: +10.1869 vs +10.037943 — no contradiction (VERIFIED)

From the compute report's own frozen table (VERIFIED lines 11–13):
SIGN96_CENTERED 54.197518, FLOAT96_CENTERED 44.159574, FLOAT96_UNCENTERED 44.010638.
Receipt `caveat_arithmetic_receipt.txt`, recomputed this session:
- S − Fc = 54.197518 − 44.159574 = 10.037944 → frozen `+10.037943`
  (full-precision manifest value `10.037943262411343`, VERIFIED manifest line 14). ✓
- S − F0 = 54.197518 − 44.010638 = 10.186880 → T4C1 audit's `+10.1869`
  (VERIFIED `audit_v52_t4c1/AUDIT_REPORT.md:82`). ✓
- Consistency: (S−F0) − (S−Fc) = 0.148936 = Fc−F0 (the frozen centering effect). ✓
Different subtrahends (centered vs uncentered float reference), both correct.
