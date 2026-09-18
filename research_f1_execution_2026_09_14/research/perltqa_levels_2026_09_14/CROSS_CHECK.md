[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# CROSS_CHECK.md — mandatory out-of-sample test of the frozen rule R

Rule R was frozen in `PREDICTION.md` **before** any number in this file was computed.
`PREDICTION.md` has not been edited since. All corrections are in § 5 below.

**R (frozen):** for a stratum S, predict `sign(Delta_S) = +1` iff
`mean_{q∈S} ALIGN(q) < 0.4530`, where `ALIGN(q) = cos(qC², v)`, `v_j = mean_i(C_ij²)`.

## 1. Gates on the test benchmarks (VERIFIED, `cross_check.py`, `step8_locomo.py`)

| benchmark | n | my SIGN | frozen SIGN | my float | frozen float | my Delta pp | frozen Delta pp |
|---|---:|---|---|---|---|---:|---|
| LongMemEval | 470 | `0.5421335697399526` | `0.5419751773049645` | `0.4415957446808511` | `0.4415957446808511` | **+10.053783** | +10.037943 (exact-expectation ref +10.053783) |
| REALTALK | 705 | `0.22553482307028402` | `0.22477507598784194` | `0.17253405381064957` | `0.17253405381064954` | **+5.300077** | +5.2241 (exact-expectation ref +5.300077) |
| LoCoMo | 1535 | `0.23790671959238732` | `0.23654714666441054` | `0.17135625684485617` | `0.16826334541318252` (frozen *candidate*) | **+6.655046** | +6.82838013 |

LME float matches to the last digit; REALTALK float to 3e-17. SIGN differs in the 4th decimal
exactly as expected when replacing NT=20 sampled tie-breaks with the exact expectation, and both
reproduce the coordinator's exact-expectation references to 6 dp. LoCoMo deviates more
(+6.655 vs +6.828, magnitude **0.173 pp**); I report it rather than tune it — see § 4.

## 2. THE RESULT: rule R is DEAD

### P2 — LongMemEval (Delta observed **+10.054 pp**)
mean ALIGN = **0.5447** > THETA 0.4530 → R predicts Delta **< 0**. Observed **> 0**. **FAILED.**

### P3 — REALTALK (Delta observed **+5.300 pp**)
mean ALIGN = **0.5679** > THETA → R predicts Delta **< 0**. Observed **> 0**. **FAILED.**

### P7 — LoCoMo (testable after all; Delta observed **+6.655 pp**)
mean ALIGN = **0.5681** > THETA → R predicts Delta **< 0**. Observed **> 0**. **FAILED.**

### P4 — decile monotonicity (R requires rho < 0)
| benchmark | Spearman(decile ALIGN, decile Delta) | verdict |
|---|---:|---|
| LongMemEval | **−0.58788** | PASS |
| REALTALK | **+0.16364** | **FAIL** |
| LoCoMo | **+0.04242** | **FAIL** |

Passes on one benchmark out of three; on the two it fails, the sign is the wrong one.

### P5 — decile accuracy vs majority baseline (the pre-declared honest scoring)
| benchmark | R accuracy | majority baseline | verdict |
|---|---:|---:|---|
| LongMemEval | 2/10 = 0.200 | 10/10 = 1.000 | **DOES NOT BEAT** |
| REALTALK | 2/10 = 0.200 | 10/10 = 1.000 | **DOES NOT BEAT** |
| LoCoMo | 1/10 = 0.100 | 10/10 = 1.000 | **DOES NOT BEAT** |

R is far *worse* than "always predict positive". It manufactures reversals that do not exist:
of 30 out-of-sample deciles it predicted negative Delta in 25, and **not one of the 30 deciles
has a negative Delta**. This is the exact failure mode the task named — "if your rule predicts a
reversal where none occurs, it is WRONG".

### P6 — REALTALK per-chat strata (R requires rho < 0)
Spearman = **+0.01818** → **FAILED**. Accuracy 2/10 vs majority 8/10.
(Chats 3 and 4 are genuinely negative, −1.005 and −5.094 pp; R gets them right only because it
predicts negative for all ten.)

### In-sample PerLTQA (for the record, NOT evidence)
4/4 sections correct — which is exactly what "fitted on one benchmark" looks like.
Per-query `rho(Delta, ALIGN)` within PerLTQA is **−0.0208**: R had essentially no per-query
signal even where it was built, as § 4 of `PREDICTION.md` predicted in advance.

## 3. Verdict on R

**R is KILLED.** It fails the whole-benchmark prediction on all three out-of-sample
benchmarks (3/3), fails P4 on 2/3, fails P5 on 3/3 against the majority baseline, and fails P6.
Per `PREDICTION.md` § 6.1 I committed in advance not to rescale THETA to rescue it, and I do not.
The ordinal form fails too (P4/P6), so nothing is salvaged by retreating to it.

The mechanism story in `LEVELS.md` § 4 — profile queries are low-ALIGN, spectrally concentrated,
with float mis-ranking their golds — is **descriptively true of PerLTQA and predictively
worthless elsewhere.** Sixth story killed.

## 4. Post-freeze corrections (PREDICTION.md itself untouched)

1. **LoCoMo was declared "untestable" in error during the run.** `cross_check.py:88-96` looked
   for `evidence` / `gold` / `evidence_ids` keys in `qas[i]`; the committed caches use
   **`raw_evidence`**, resolved through `id_to_row` (VERIFIED, `step0_axis_stat.py` output:
   `qas[0] keys: ['answer','category','question','question_id','raw_evidence']`). Corrected in
   `step8_locomo.py`; 1535 queries scored. P7 is therefore **testable and FAILED**, not untestable.
   This correction makes the evidence against R *stronger*, not weaker.
2. **LoCoMo float headline deviates by 0.173 pp** from the frozen candidate
   (`0.17135625684485617` vs `0.16826334541318252`). Reported, not tuned. Most likely cause:
   the frozen value is labelled a *"centered-float frozen-cache candidate"* in
   `R2_COMPETITION_RERUN_CONTRACT.md` (not an accepted headline), and my gold-row resolution
   from `raw_evidence` may differ from the audit-layer evidence maps in
   `drive/audit_layer/conv_*.json`, which I did not use. Flagged for follow-up; it does not
   affect the sign of Delta (+6.66 vs +6.83, both clearly positive), which is all R's
   predictions depend on.

## 5. Adversarial self-checks (both pre-declared in `PREDICTION.md` § 7)

**(a) Is profile's positive STRICT_GAP an artifact of gold multiplicity / the all-competitor
convention?** Tested with the R2 contract's mandatory non-gold sensitivity variant.
VERIFIED (`evidence/levels_summary.json`): `STRICT_GAP_ng` = profile **+4.733**, events −21.880,
social −25.109, dialogues −74.795. Identical to the primary for the three single-gold sections
(profile/events/social are 100% single-gold, mean `gold_n` = 1.0000) and within 0.03 for
dialogues (mean `gold_n` = 9.92). **Multiplicity is not the driver.** The § 3 level result in
`LEVELS.md` stands on its own terms — it just does not generalise.

**(b) Is ALIGN merely a proxy for query norm?** VERIFIED: `rho(ALIGN, qnorm)` = −0.283 (LME),
−0.207 (REALTALK), −0.033 (PerLTQA). ALIGN is not a norm proxy — it is a genuinely distinct
statistic that is *genuinely uninformative* about Delta: `rho(Delta, ALIGN)` = −0.057 / +0.011 /
−0.021 / −0.011, sign-**inconsistent** across the four benchmarks. R did not fail because I
measured the wrong thing; it failed because ALIGN carries no cross-benchmark signal at all.

**(c) The assumption whose failure would most damage my conclusion**, and its test: *that my
competition rows are computed correctly, so that "the level does not set the sign" is a real
finding and not my bug.* This is the dangerous one — a wrong TOP64/BOT64 or a wrong per-gold
convention would produce exactly this kind of null. Tested against a surface I did not build:
my rows reproduce the **independent R2 audit's** published Spearman targets to ≤1.2e-4 overall
and on all four PerLTQA sections, and LoCoMo `rho(Delta,STRICT_GAP)` = +0.10327 vs audit target
`0.09491957131277647`, `rho(Delta,TIE_GAP)` = +0.10481 vs target `0.10376015063205302`
(`LEVELS.md` § 0, `step8_locomo.py` output). The competition machinery is correct; the null is real.

## 6. What survived (reported as a lead, not as a result)

Per-query `rho(Delta, X)`, all four benchmarks [LME, REALTALK, PerLTQA, LoCoMo]:

| statistic | LME | REALTALK | PerLTQA | LoCoMo | sign-consistent |
|---|---:|---:|---:|---:|---|
| **strict_BOT64** | −0.185 | −0.179 | −0.195 | **−0.308** | **YES** |
| TIE_GAP | +0.141 | +0.123 | +0.280 | +0.105 | YES |
| STRICT_GAP | +0.142 | +0.098 | +0.254 | +0.103 | YES |
| strict_TOP64 | −0.129 | −0.113 | −0.073 | — | YES |
| float_margin | −0.178 | −0.044 | −0.202 | — | YES |
| ALIGN (R's statistic) | −0.057 | +0.011 | −0.021 | −0.011 | **no** |
| gold_norm_rel | −0.094 | +0.003 | +0.040 | — | no |

The **slope** is stable and the **level** is not. Benchmark-mean gap ranks do not track
benchmark-mean Delta (LME and PerLTQA share a negative gap and have opposite Delta signs).
Even granting an oracle that centers the gap within its own benchmark — which requires knowing
the very offset that is unknown — stratum accuracy is 14/24 = 58.3% against a 79.2% majority
baseline (`step7_slope_vs_level.py`). **The per-benchmark offset, not the competition geometry,
is where the sign lives.** That is a target, not an explanation.
