[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# REPORT.md — PerLTQA reversal: competition LEVELS measurement

## Bottom line

The levels were measured. **Both surviving pictures are dead.** Within PerLTQA the SIGN-winning
section is the only one with a positive per-gold competition gap — which kills the picture that
required a negative gap there. Across benchmarks, LongMemEval and PerLTQA share a *negative* gap
and have *opposite* Delta signs — which kills the level as a determinant of sign. A new rule
(ALIGN) was frozen before testing and cleanly killed on 3/3 out-of-sample benchmarks.
**The slope is stable across four benchmarks; the level is not. The sign lives in a
per-benchmark offset that no competition statistic sees.**

## Gates (passed before any new number was trusted)

| gate | result |
|---|---|
| PerLTQA frozen headline | float `0.551692074528853` **exact**; Delta `−6.274727836521104` pp; all 4 sections match the coordinator to 6 dp |
| Independent R2 audit Spearman targets | reproduced to **≤1.2e-4** overall and on all 4 sections (a surface I did not build) |
| LME / REALTALK headlines | float exact / 3e-17; Delta +10.053783 / +5.300077 pp = coordinator exact-expectation refs |
| LoCoMo | Delta +6.655046 pp vs frozen +6.82838013 (deviation **0.173 pp**, reported not tuned — see CROSS_CHECK § 4.2) |

Axis statistic: `mean_i(C_ij²)` and `var` are **identical here** (ordering identical 30/30,
max abs difference 2.08e-17) because the cached `C` is already centered (col-mean absmax 4.4e-16).
Not re-centered.

## Key numbers

**Levels (PerLTQA, n=8265):**

| section | Delta pp | STRICT_GAP | TIE_GAP | GAP median | frac>0 |
|---|---:|---:|---:|---:|---:|
| **profile** (SIGN wins) | **+20.355** | **+4.733** | **+3.207** | **+1.00** | **0.5405** |
| dialogues | −1.502 | −74.826 | −3.258 | −74.66 | 0.1754 |
| social_relationship | −0.780 | −25.109 | −6.250 | −1.00 | 0.1114 |
| events | −12.394 | −21.880 | −5.509 | −1.00 | 0.1756 |

Within-archive paired (same matrix): STRICT_GAP profile > events in **25/30**.
Non-gold sensitivity variant identical (multiplicity is not the driver).

**Levels out-of-sample — the kill:**

| benchmark | Delta pp | mean STRICT_GAP | sign match |
|---|---:|---:|---|
| LongMemEval | **+10.054** | **−19.167** | **FAIL** |
| LoCoMo | **+6.655** | **−5.784** | **FAIL** |
| REALTALK | +5.300 | +0.248 | PASS |
| PerLTQA | −6.275 | −38.703 | PASS |

Stratum rule "gap>0 ⇒ Delta>0": **11/24 = 45.8%** vs **79.2%** majority baseline.

**Frozen rule R (ALIGN < 0.4530 ⇒ Delta > 0) — killed:**

| prediction | LME | REALTALK | LoCoMo |
|---|---|---|---|
| whole-benchmark sign | **FAIL** (ALIGN 0.545) | **FAIL** (0.568) | **FAIL** (0.568) |
| P4 decile monotonicity | PASS (−0.588) | **FAIL** (+0.164) | **FAIL** (+0.042) |
| P5 vs majority | 0.200 vs 1.000 | 0.200 vs 1.000 | 0.100 vs 1.000 |

R predicted a negative Delta in 25 of 30 out-of-sample deciles; **none** of the 30 is negative.

**What survived (a lead, not a result)** — per-query `rho(Delta, X)` [LME, RT, PerLTQA, LoCoMo]:
`strict_BOT64` **−0.185 / −0.179 / −0.195 / −0.308** (tightest cross-benchmark statistic yet);
`STRICT_GAP` +0.142 / +0.098 / +0.254 / +0.103; `ALIGN` −0.057 / +0.011 / −0.021 / −0.011 (sign-inconsistent).

## Geometry: profile vs events on the SAME archive (paired, out of 30)

query norm 0.892 vs 0.935 (**0/30**) · qPR 9.14 vs 11.83 (4/30) · ALIGN 0.412 vs 0.530 (**1/30**)
· gold norm ratio 1.075 vs 1.011 (**30/30**) · float margin −0.245 vs +0.006 (**0/30**)
· Hamming near-ties 55.4 vs 12.4. Full percentile distributions in `LEVELS.md` § 4.

A profile query is low-norm, spectrally concentrated, aimed off the archive's high-variance axes,
with long gold vectors that float still mis-ranks. True of PerLTQA, predictively worthless elsewhere.

## Adversarial self-checks (all pre-declared in PREDICTION.md § 7)

- **Gold multiplicity artifact?** No — non-gold variant identical for the single-gold sections.
- **ALIGN = query norm?** No — `rho(ALIGN,qnorm)` −0.283/−0.207/−0.033. ALIGN is distinct and
  genuinely uninformative; R failed on its merits.
- **Most damaging assumption — is my competition code simply wrong, making the null my bug?**
  Tested against an external surface: my rows reproduce the independent R2 audit's published
  targets on PerLTQA (4/4 sections, ≤1.2e-4) and LoCoMo (+0.10327 vs 0.09491957,
  +0.10481 vs 0.10376015). The machinery is correct; the null is real.

## Next decisive measurement

**Stop running correlational per-query rules (six have died identically). Intervene on the
representation with archives held fixed.** Priority: (1) **axis-budget sweep** m ∈ {8…96} for
SIGN vs float on the same m axes, looking for a per-benchmark crossover m\* — the frozen caches
already carry TOP/BOT/SPREAD/RANDOM arms at k=48/64/80, so this is nearly free; (2) **rank-vs-
magnitude decomposition**: score `sign(C)·‖C_i‖` and see whether it tracks SIGN on LME but float
on PerLTQA, which would identify the offset as document-norm informativeness.

## Files (all in `agent_out/perltqa-levels/`, additive only)

`PREDICTION.md` (frozen pre-test, unedited) · `LEVELS.md` · `CROSS_CHECK.md` · `VERDICT.md` ·
`REPORT.md` · `levels.py` · `control.py` · `step0_axis_stat.py` · `step3b.py` · `cross_check.py` ·
`step6_levels_xbench.py` · `step7_slope_vs_level.py` · `step8_locomo.py` · `consolidate.py` ·
`evidence/results.json` (consolidated) + `control.json`, `levels_summary.json`,
`paired_archives.json`, `step6.json`, `step7.json`, `locomo.json`, 2 row pickles.

## Compliance

Read-only on all caches (no write/move/delete outside my output dir) · no git operations beyond
`git show` of blobs · Task4F1 seal untouched, no BEAM corpora, no sealed labels · no network,
no installs · `PREDICTION.md` frozen before step 5 and never edited; the one correction
(LoCoMo testable after all) is recorded in `CROSS_CHECK.md` § 4.

## What I could NOT do

- **LoCoMo float headline is 0.173 pp off** the frozen *candidate* value. Not tuned. Likely my
  `raw_evidence`→`id_to_row` gold resolution differs from `drive/audit_layer/conv_*.json`, which
  I did not use. Does not affect any conclusion (sign of Delta is unambiguous either way).
- **No causal claim.** Everything here is observational on frozen caches; the offset is located,
  not explained. The proposed interventions are the way to fix that and were not run (out of budget).
- **SIGN FR@3 values differ from frozen in the 4th decimal** by design — exact tie expectation
  instead of NT=20 sampled permutations, as the task specified. Float values match exactly.
