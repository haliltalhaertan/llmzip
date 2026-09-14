[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# COMPARISON.md — three-way: my numbers vs coordinator vs auditor/contract

Receipts: `evidence/three_way.json`, `evidence/perm_diagnosis.json`, `evidence/decisive_delta_source.json`.

## 1. Me vs the coordinator — BIT-IDENTICAL on all six

| benchmark | arm | mine | coordinator | difference |
|---|---|---|---|---|
| LME | strict | `0.1416251737011647` | `0.1416251737011647` | **exactly 0** |
| LME | tie | `0.14069387548880735` | `0.14069387548880735` | **exactly 0** |
| PerLTQA | strict | `0.25413844391463014` | `0.25413844391463014` | **exactly 0** |
| PerLTQA | tie | `0.27982715404990666` | `0.27982715404990666` | **exactly 0** |
| REALTALK | strict | `0.09793425648573494` | `0.09793425648573494` | **exactly 0** |
| REALTALK | tie | `0.12307477776090332` | `0.12307477776090332` | **exactly 0** |

VERIFIED (`evidence/three_way.json`, `max |mine - coord| = 0.0`). Coordinator values read from
`git show 557fc1e:research_f1_execution_2026_09_14/evidence/f1_results_fr3.json`.

His headline pp values also reproduce bit-for-bit against mine to ~1e-14
(LME `10.053782505910167` vs his `10.053782505910158`; PerLTQA `-6.274727836521104` vs
`-6.274727836521077`; REALTALK `5.300076925963451` vs `5.3000769259634595` — last-digit
summation-order noise only). Multi-gold rates, min-gold control values and section summaries
all agree. **Two independently written implementations (his pure-stdlib, mine numpy) converge
exactly. The arithmetic of the corrected per-gold metric is sound.**

## 2. Me vs the AUDITOR TARGETS IN THE CONTRACT — all six FAIL the contract's stated tolerance

The contract states the targets at full precision with an explicit tolerance:
> "Expected independent-audit targets (tolerance `1e-12` when using the identical rows/rank implementation)"
(`R2_COMPETITION_RERUN_CONTRACT.md`, "Primary corrected summaries")

| benchmark | arm | mine | contract target (full precision) | mine − target | passes 1e-12? |
|---|---|---|---|---|---|
| LME | strict | `0.1416251737011647` | `0.14168629605302735` | `-6.112235e-05` | **FAIL** |
| LME | tie | `0.14069387548880735` | `0.14045379360271315` | `+2.400819e-04` | **FAIL** |
| PerLTQA | strict | `0.25413844391463014` | `0.25416826537535475` | `-2.982146e-05` | **FAIL** |
| PerLTQA | tie | `0.27982715404990666` | `0.2797878341571222` | `+3.931989e-05` | **FAIL** |
| REALTALK | strict | `0.09793425648573494` | `0.097939128891117` | `-4.872405e-06` | **FAIL** |
| REALTALK | tie | `0.12307477776090332` | `0.12281952421315011` | `+2.552535e-04` | **FAIL** |

The coordinator fails these identically, because we produce identical numbers.

## 3. THE CENTRAL FINDING — what the coordinator actually compared against

`coordinator/coord_f1_real_fr3.py:116-117` (VERIFIED, read from the git blob):

```python
AUD = {"LME": (0.1417, 0.1405), "REALTALK": (0.0979, 0.1228),
       "PERLTQA": (0.2542, 0.2798), "LOCOMO": (0.0949, 0.1038)}
```

These are **4-decimal rounded display values**, not the contract's full-precision targets.
His `diff_strict`/`diff_tie` fields in `evidence/f1_results_fr3.json` are therefore differences
against rounded numbers (~1e-5..3e-4), and he read them as success.

His own package restates the correct full-precision targets —
`agent_packages/.../CONTRACT_CHECKLIST.md` C7 lists `0.14168629605302735` etc. and says
"Expected auditor targets at 1e-12". **The execution script does not use them.**
The tightest check the contract asks for is the one that was not run.

Against the contract's real targets, the honest statement is: *the six coefficients agree with the
auditor's published values to 3–4 decimal places, NOT to 1e-12*. "Reproduced all six published
auditor coefficients" overstates this.

## 4. Diagnosis — which side is right, and why

I investigated rather than tuned. Three candidate causes; I tested all three.

### 4a. Axis-ordering convention — RULED OUT
The auditor uses `np.argsort(v)[::-1]`; the contract says stable descending (`argsort(-v)`).
These differ on ties. I measured: across all 480 LME+REALTALK archives, **0 archives have any
tied `v_j`**, and **0 archives** produce a different TOP64/BOT64 set under the two conventions
(`evidence/decisive_delta_source.json:axis_order_check`). Not the cause.

### 4b. Gold de-duplication — RULED OUT
The auditor applies `np.unique` to gold; I did not. Measured: **0 queries** in LME+RT have
duplicate gold indices. Toggling it changes nothing (identical rho to all digits). Not the cause.

### 4c. The Delta_q SOURCE — CONFIRMED as the cause
The contract says (Inputs section):
> "Use the exact per-query `Delta_q = FR_SIGN96 - FR_centered_float96` values **from the
> recovered/frozen evaluation surface**."

The auditor obeyed this literally: `competition_variants.py` loads
`delta = INDEPENDENT_QUERY_ROWS.json` — a *stored* per-query Delta surface. It never recomputes FR@3.

The coordinator and I both **recomputed** Delta_q from the caches with an exact-expectation FR@3.
That is a different quantity: the frozen surface was produced by the NT=20 *seeded permutation*
average (`step2_eval.py:8` `NT = 20`; REALTALK `details.json` protocol string records
`tie_seed=5_100_000+ci*100_000+t*100+99`), which carries sampling noise the exact expectation does not.

**Direct test** (`decisive_delta_source.py`): I held my competition code *exactly fixed* and swapped
only the Delta source to the committed frozen surfaces
(`docs/v52/task4c2/V52_T4C2_question_level.csv` for LME; `bench3/b3a_realtalk/details.json` for RT):

| benchmark | arm | recomputed Delta (mine+coord) | frozen-surface Delta | auditor target | frozen-surface error |
|---|---|---|---|---|---|
| REALTALK | strict | `0.09793425648573494` | `0.0979394409176499` | `0.097939128891117` | **+3.1e-07** |
| REALTALK | tie | `0.12307477776090332` | `0.12281981175104122` | `0.12281952421315011` | **+2.9e-07** |
| LME | strict | `0.1416251737011647` | `0.14182013142373143` | `0.14168629605302735` | +1.3e-04 |
| LME | tie | `0.14069387548880735` | `0.14044429655330729` | `0.14045379360271315` | -9.5e-06 |

REALTALK error drops by **~1000×** (2.6e-04 → 2.9e-07) purely by taking Delta from the frozen
surface. That is decisive: the residual is a Delta-source artefact, not a competition-metric error.
LME does not converge as sharply because the committed LME CSV column
(`sign_minus_centered_float_fractional_pp`) is a *derived pp* column at ~15 significant digits and
is not the same object as the auditor's stage-1 `delta`; the auditor's actual
`INDEPENDENT_QUERY_ROWS.json` is **not committed to any branch I can read** (checked — it lived at
`/mnt/data/e1v2_raw_audit/independent_stage1`, a path off this machine). So exact 1e-12
reproduction of the auditor's LME figure is **impossible from the artefacts available here**.

### 4d. Magnitude sanity — the NT=20 convention alone spans the whole discrepancy
I recomputed the coefficients using NT=20 seeded permutations under six different seed families
(`evidence/perm_diagnosis.json`). Range across seeds:

| benchmark | arm | NT=20 spread across seed families | auditor target inside? |
|---|---|---|---|
| LME | strict | `0.14109972` … `0.14376913` | YES |
| LME | tie | `0.14003954` … `0.14294393` | YES |
| REALTALK | tie | `0.11895796` … `0.12550930` | YES |
| REALTALK | strict | `0.09794698` … `0.10180407` | no (target is 5e-06 below the low end) |
| PerLTQA | both | spread ~1e-04 | (largest n, smallest spread) |

The seed-to-seed spread of the frozen NT=20 convention (up to **2.7e-03** on LME) is **one to two
orders of magnitude larger** than the 1e-12 tolerance the contract demands, and larger than every
discrepancy under discussion. **The contract's own 1e-12 tolerance is unachievable by anyone who
recomputes Delta_q, and is only meaningful against the auditor's exact stored row file.**

## 5. Verdict of the comparison

- The **corrected per-gold competition metric is right** in both implementations — two independent
  codebases agree bit-for-bit, and the qualitative F1 conclusion (min-gold materially distorts the
  coefficients: LME 0.1416→0.0992, REALTALK 0.0979→0.0613, PerLTQA 0.2541→0.2774) is **reproduced
  and survives**. That is a real result and it is the substance of F1.
- The **"reproduced all six published auditor coefficients" claim is not supported** at the
  precision the contract specifies. It is supported at 3–4 decimals. The coordinator's script
  compares against rounded constants and therefore cannot detect the difference.
- The residual is **diagnosed, not mysterious**: recomputed-vs-stored Delta_q under a 20-sample
  permutation tie-break. Neither side is "wrong" arithmetically; the coordinator's substitution of
  the exact expectation is defensible *as a method* but it is a **deviation from the frozen
  convention** and it forfeits the 1e-12 reproduction the contract asked for.
- A **contract gate was skipped**: C3 requires the headline gates to reproduce to <=1e-12 *before*
  Claim-D computation, and the spec says "A failed gate stops that benchmark." See CODE_REVIEW.md
  F-2 — the gate function exists in his package and is never called; had it been called, LME and
  REALTALK would have failed it and stopped.
