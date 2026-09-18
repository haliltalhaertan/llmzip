[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Round 2: results recovered after all four sessions died on a rate limit

## What happened, and why these results exist anyway

Four research sessions were dispatched in parallel. All four were killed by
`HTTP 429: rate limit` after 5-6 API calls each. Zero sessions delivered a report.

But three of them had already written their measurement code before dying, and one
had already produced its control + scope results. The expensive part (deciding the
method) was done; execution is free numpy. The coordinator therefore ran the dead
sessions' own code unchanged, wrote only the missing drivers, and analysed the output.

**Provenance, stated precisely:**

| package | method + code authored by | driver | analysis |
|---|---|---|---|
| axis-budget | subagent (`axis_budget_core.py`) | coordinator (`run_sweep.py`) | coordinator |
| norm-info | subagent (`norm_info.py`, complete) | subagent | coordinator (`coord_analysis.py`) |
| bot64-survivor | subagent (`bot64.py`, complete) | subagent | coordinator (`artifact_tests.py`, `coord_correction.py`) |
| scale-honest | subagent (control + scope + PREDICTION.md) | subagent | incomplete - synthesis comparison never ran |

**Discipline cost of the crash, disclosed:** `norm-info` and `bot64-survivor` died
before writing PREDICTION.md. Their hypotheses are on the record in the dispatch
briefs, but were NOT frozen by the measuring party before the numbers were seen.
Those two results are therefore EXPLORATORY, not tests. Only `scale-honest` froze a
prediction (before its step 3, which never ran). `axis-budget` has no frozen
prediction either.

## Controls passed before any new number was trusted

All four benchmarks reproduced, independently, in three separate packages:

| benchmark | SIGN FR@3 | FLOAT FR@3 | Delta | frozen ref |
|---|---|---|---|---|
| LongMemEval | 0.542133569740 | 0.441595744681 | +10.053783 pp | +10.037943 |
| PerLTQA | 0.488944796164 | 0.551692074529 | -6.274728 pp | -6.275 |
| REALTALK | 0.225534823070 | 0.172534053811 | +5.300077 pp | +5.2241 |
| LoCoMo | 0.237906719592 | 0.171356256845 | +6.655046 pp | +6.82838 (candidate) |

## CORRECTION NOTICE (appended after independent audit, 2026-09-14)

An independent cold-start audit (Muse Code 1.2.1, `audit/muse_axis_audit_2026_09_14/`)
returned **REQUEST_CHANGES** on the two axis-budget findings below. It wrote its own
implementation before reading any of this code and reproduced **all six of its
frozen step-1 numbers exactly** (LME and PerLTQA at m=8/32/48/64/96, matching to 6
decimals), plus the full LoCoMo and REALTALK grids to 4 dp. It also proved the FR@3
tie expectation exact by brute-force enumeration, confirmed m=96 matched == full-96
on 4/4 benchmarks, and confirmed every semantics-changing mutation moves the numbers.

**The arithmetic is not in dispute. The interpretations were wrong, and the
coordinator has verified each finding against his own stored data
(`research/axis_budget_2026_09_14/coord_audit_check.py`).** Dispositions:

**C-1 (MAJOR, ACCEPTED) - FINDING 2 was mis-attributed to the sign arm.**
The audit checked `float_bot - float_top`, a column the coordinator stored in the
sweep and never examined. The same effect is present in the FLOAT arm and is
*larger* in **9 of 12** cells:

| benchmark | m | sign bot-top | float bot-top | ratio |
|---|---|---|---|---|
| LME | 48 | +7.7511 | **+21.8794** | 2.82 |
| LoCoMo | 48 | +4.8137 | **+15.4642** | 3.21 |
| REALTALK | 48 | +0.1786 | **+9.0020** | 50.41 |
| PerLTQA | 48 | -12.7279 | -8.5551 | 0.67 |

So "low-variance axes retrieve better" is a property of **the axes**, which both
arms agree on - not a fact about sign quantization. FINDING 2's framing is
withdrawn. The underlying axis effect is real (it survives on the overlap-free
m=48 contrast) but it is not sign-specific.

**C-2 (MAJOR, ACCEPTED) - the "4/4 alignment" compared different budgets.**
It set `bot-top` at m=48 against Delta at m=96. Compared at the SAME m it fails:

| benchmark | m=24 | m=32 | m=48 | m=64 | m=80 |
|---|---|---|---|---|---|
| LME | MISMATCH | MISMATCH | OK | OK | OK |
| LoCoMo | MISMATCH | MISMATCH | MISMATCH | OK | OK |
| REALTALK | OK | OK | OK | OK | OK |
| PerLTQA | OK | OK | OK | OK | OK |

5 of 20 same-budget cells mismatch. "4/4 aligned" is withdrawn.

**C-3 (MAJOR, ACCEPTED) - TOP/BOT overlap was never disclosed.**
TOP-m and BOT-m are disjoint only while 2m <= 96. At m=64 they share **32** axes,
at m=80 **64**, and at m=96 they are the identical set, so `bot - top = 0` by
construction. The apparent decline of the bot-top gap toward m=96 is therefore
substantially **dilution**, not a finding. Only m<=48 is a clean contrast. Neither
the code nor the writeup said so.

**C-4 (MAJOR, ACCEPTED) - "same curve shape" contradicted the coordinator's own output.**
The readout script computes monotonicity and prints it. LoCoMo and REALTALK are
**not** monotone (LoCoMo dips at 8->12, 12->16, 24->32; REALTALK at 8->12, 12->16),
and LME's total rise (+21.90 pp) is ~2.4x LoCoMo's (+8.95) and REALTALK's (+8.88).
The published sentence "all four show the SAME qualitative shape" overstated a
correlated rise. Withdrawn; the shared feature that does survive is that all four
rise overall and share their largest jump around m=32->48.

**C-5 (MAJOR, ACCEPTED) - the PerLTQA crossover estimate is unidentified.**
"~243 axes" came from the m=80..96 window alone. Across standard windows:

| window | slope pp/axis | implied m* |
|---|---|---|
| 8..96 | +0.09668 | 153 |
| 24..96 | +0.08341 | 166 |
| 48..96 | +0.06809 | 186 |
| 64..96 | +0.06224 | 195 |
| 80..96 | +0.04265 | **243** |

Segment slopes run +0.776, +0.340, +0.010, +0.020, +0.140, +0.075, +0.082, +0.043 -
clearly non-constant and concave, so a linear crossover is not identified at all.
The point estimate is **withdrawn**; the honest statement is "beyond 96, not
estimable from these data".

**C-6 (MAJOR, ACCEPTED) - crossover precision is indefensible.**
47.3 / 42.5 / 53.4 were linear interpolations on a grid whose spacing at the crossing
is **16** (48->64), giving a +-8 floor before sampling error; the audit's resampling
put LME's bracketing pair on opposite sides of zero only ~57% of the time. Correct
reporting: LME and REALTALK cross **between m=32 and m=48**, LoCoMo **between m=48
and m=64**, PerLTQA **not within 96**. Decimals withdrawn.

**C-7 (ACCEPTED, terminology) - "budget-matched" is wrong.** The sign arm uses m
BITS, the float arm m FLOAT32 = 32m bits: a **32:1** storage asymmetry per axis. The
correct term is **dimension-matched**. It isolates quantization at equal
dimensionality, which is the intended contrast, but it is not a storage-matched
comparison and must not be read as one.

**C-8 (ACCEPTED, no rule survives).** At m=48, RANDOM-48 beats BOT-48 on LongMemEval
(0.446970 vs 0.429568) and on REALTALK (0.166890 vs 0.162415). So "select the
low-variance axes" is not a usable retrieval rule even where the contrast is clean.

### What survives the audit

- Every number: the audit's independent implementation reproduced all six frozen
  step-1 values exactly and the remaining grids to 4 dp.
- **FINDING 1's core**: sign quantization loses at small dimension and gains at large
  on all four benchmarks, with PerLTQA crossing (if at all) beyond the available 96.
  The crossover ORDER and the existence of a per-benchmark offset stand; only the
  precision, the extrapolation and the "same shape" wording were wrong.
- A real per-axis variance effect, confirmed on the overlap-free m=48 contrast -
  but as a property of the representation that both arms share.

### What this costs the programme

FINDING 2 as published is withdrawn. It is not a tenth dead mechanism candidate -
it was never a mechanism, it was a mis-attribution. The axis effect it pointed at is
real and now correctly located in the geometry rather than in the quantizer.

### Audit independence, stated by the auditor

Not fully independent: same commissioning party, and the brief quoted the
coordinator's numbers before the auditor computed its own. The auditor recorded this
in MY_NUMBERS.md and VERDICT.md. It could not write into the shared output directory
(/mnt/c mounted read-only in that session), so its deliverables were produced in the
WSL home and copied here unmodified.

---

## FINDING 1 (axis budget): the per-benchmark offset is a POSITION ON A SHARED CURVE

Budget-matched sweep: at each budget m, SIGN on the top-m axes vs FLOAT cosine on
**the same m axes** (so the contrast isolates quantization, not dimension).

| m | LME | LoCoMo | REALTALK | PerLTQA |
|---|---|---|---|---|
| 8 | -11.848 | -2.294 | -3.576 | -16.401 |
| 16 | -9.290 | -4.002 | -4.795 | -11.938 |
| 32 | -6.301 | -4.162 | -1.642 | -11.701 |
| 48 | **+0.291** | -0.776 | **+0.871** | -9.470 |
| 64 | +3.678 | +1.520 | +1.895 | -8.267 |
| 80 | +6.900 | +4.286 | +3.554 | -6.957 |
| 96 | +10.054 | +6.655 | +5.300 | -6.275 |

**Crossover m\***: LME **47.3**, REALTALK **42.5**, LoCoMo **53.4**, PerLTQA **none
within 96**.

All four benchmarks show the SAME qualitative shape: sign quantization LOSES at small
axis budgets and GAINS at large ones. PerLTQA is not a different phenomenon - its
crossover simply sits beyond the available budget. Linear extrapolation from the
m=80..96 slope (+0.04265 pp/axis) puts it near **m ~ 243**, i.e. 2.5x the 96 axes
that exist. That number is an EXTRAPOLATION 2.5x beyond the measured range and is
not measurable with 96-D vectors; it is reported as a magnitude, not a prediction.

This is the first result in the programme that converts the unexplained per-benchmark
offset into a position on a measured curve rather than a constant.

Internal consistency check: at m=96 the budget-matched and full-96 comparisons
coincide exactly on all four benchmarks (they must).

## FINDING 2 (axis identity): LOW-variance axes retrieve BETTER where sign wins

`sign_bot - sign_top` = FR@3 using the m LOWEST-variance axes minus the m HIGHEST.

| benchmark | m=24 | m=32 | m=48 | m=64 | m=80 | Delta(96) |
|---|---|---|---|---|---|---|
| LME | +5.145 | +8.103 | +7.751 | +6.813 | +3.049 | +10.054 |
| LoCoMo | +2.509 | +5.062 | +4.814 | +4.783 | +3.330 | +6.655 |
| REALTALK | -2.795 | -1.842 | +0.179 | +2.261 | +1.501 | +5.300 |
| PerLTQA | -17.721 | -16.386 | -12.728 | -11.388 | -6.902 | -6.275 |

At m=48 the sign of (bot - top) matches the sign of Delta on **4/4** benchmarks.
This is counter-intuitive: the conventional expectation is that high-variance axes
carry more information. On the three benchmarks where binary codes win, the
lowest-variance half of the coordinate space retrieves BETTER than the highest.

Random-m subsets act as referee and show axis IDENTITY matters, not just count:
LME m=48 gives `rand > bot > top`; PerLTQA m=48 gives `top > rand > bot` - a full
reversal of the ordering between benchmarks.

This arrives at the same place as the BOT64 survivor statistic by a completely
independent route (an intervention rather than a correlation).

## FINDING 3 (norm informativeness): HYPOTHESIS DEAD - ninth kill

Hypothesis: the per-benchmark offset is document-norm informativeness (norm helps
where sign loses, is noise where sign wins).

At benchmark level it looked perfect - 4/4:

| benchmark | Delta | norm AUC | AUC 95% CI |
|---|---|---|---|
| LongMemEval | +10.054 | 0.4310 | [0.412, 0.449] |
| REALTALK | +5.300 | 0.4832 | [0.466, 0.499] |
| LoCoMo | +6.655 | 0.3751 | [0.363, 0.388] |
| PerLTQA | -6.275 | 0.6553 | [0.649, 0.661] |

Every sign-winning benchmark has AUC < 0.5; the sign-losing one has AUC > 0.5.
Four data points, consistent.

**The section level kills it.** Inside PerLTQA:

| section | Delta | norm AUC | norm-only FR@3 | random FR@3 |
|---|---|---|---|---|
| profile | **+20.355** | **0.9828** | 0.198198 | 0.007342 |
| social_relationship | -0.780 | 0.9293 | 0.008294 | 0.007323 |
| dialogues | -1.502 | 0.4698 | 0.000000 | 0.007313 |
| events | -12.394 | 0.6940 | 0.000000 | 0.007414 |

`profile` is a direct counterexample: document norm is extremely informative
(AUC 0.983, norm-only retrieval 27x random) and sign nevertheless WINS by twenty
points. The hypothesis forbids exactly this. It is dead.

**Storage verdict** (the arm must earn its bytes): adding a float32 norm takes the
code from 12 B to 16 B, +33%.

| benchmark | sign (12 B) | sign x norm (16 B) | gain | 95% CI |
|---|---|---|---|---|
| LongMemEval | 0.542134 | 0.547021 | +0.489 pp | [-0.453, +1.377] |
| PerLTQA | 0.488945 | 0.494328 | +0.538 pp | [+0.328, +0.741] |
| REALTALK | 0.225535 | 0.220780 | -0.476 pp | [-1.129, +0.132] |
| LoCoMo | 0.237907 | 0.234365 | -0.354 pp | [-0.813, +0.087] |

One benchmark gains significantly, two lose (CIs cross zero), and the only
significant gain is +0.54 pp for +33% storage. Not worth paying.

Consistency check that did pass: the float family (rawdot - cosine) and the sign
family (signxnorm - sign) agree on the direction of the norm effect on 4/4
benchmarks. The lambda sweep's "best" values are IN-SAMPLE (chosen on the evaluation
data) and are labelled as such in the evidence file, not used as results.

## FINDING 4 (BOT64 survivor): SURVIVES the null, FAILS to be independent on 2/4

Control reproduced: LME -0.2019 (published -0.185, diff -0.017), REALTALK -0.1798
(-0.179), PerLTQA -0.1966 (-0.195), LoCoMo -0.3094 (-0.308). The LME gap of 0.017
is larger than the other three combined and is reported, not tuned away.

**(a) Random-64 test** - BOT64 vs 24 random 64-axis subsets:

| benchmark | BOT64 | random-64 mean +- sd | BOT64 inside random range? |
|---|---|---|---|
| LME | -0.2019 | -0.1765 +- 0.0192 | YES (not distinguishable) |
| REALTALK | -0.1798 | -0.1520 +- 0.0094 | no |
| PerLTQA | -0.1966 | -0.1282 +- 0.0037 | no |
| LoCoMo | -0.3094 | -0.2484 +- 0.0083 | no |

Axis identity matters on 3/4, but random-64 recovers 63-85% of the effect
everywhere. BOT64 is not special so much as *stronger*.

**(d) Mechanical null - CORRECTED.** The first run shuffled Delta within archive;
LongMemEval has 470 archives with exactly ONE query each, so that permutation was
the identity and its LME row was vacuous (sd=0.0000). Coordinator bug, disclosed.
Re-run with a global permutation and an ngold-stratified permutation:

| benchmark | null (global) | observed | z |
|---|---|---|---|
| LME | -0.0011 +- 0.0448 | -0.2019 | -4.5 |
| REALTALK | +0.0011 +- 0.0378 | -0.1798 | -4.8 |
| PerLTQA | +0.0002 +- 0.0107 | -0.1966 | -18.3 |
| LoCoMo | -0.0010 +- 0.0255 | -0.3094 | -12.1 |

Not a mechanical artifact on any benchmark.

**(c/F1) But is it just competition?** `strict_TOP96` is the full sign arm's rival
count. Partial correlation controlling for it:

| benchmark | raw | controlling TOP96 | 95% CI | independent? |
|---|---|---|---|---|
| LME | -0.2019 | +0.0517 | [-0.040, +0.151] | **NO** |
| REALTALK | -0.1798 | -0.0550 | [-0.129, +0.022] | **NO** |
| PerLTQA | -0.1966 | -0.1335 | [-0.155, -0.113] | yes |
| LoCoMo | -0.3094 | -0.1428 | [-0.186, -0.094] | yes |

On the two smallest benchmarks the survivor is fully absorbed by plain competition.
It carries independent information only on the two largest. Downgraded accordingly:
it is not a clean handle on the mechanism.

**(e/F2) The asymmetry that is new.** Restricting to queries where SIGN and FLOAT
actually differ:

| benchmark | all | nonzero-Delta | 95% CI | n | Delta(96) |
|---|---|---|---|---|---|
| LME | -0.2019 | -0.4509 | [-0.560, -0.338] | 166 | +10.054 |
| REALTALK | -0.1798 | -0.5739 | [-0.678, -0.449] | 147 | +5.300 |
| LoCoMo | -0.3094 | -0.7418 | [-0.789, -0.686] | 295 | +6.655 |
| PerLTQA | -0.1966 | -0.1709 | [-0.217, -0.122] | 2230 | **-6.275** |

On the three sign-POSITIVE benchmarks the correlation roughly triples once the
Delta==0 mass (65-81% of queries) is removed. On the sign-REVERSED benchmark it does
not move. PerLTQA's CI is **disjoint from all three** sign-positive benchmarks.
This is the cleanest separation yet found between the reversed benchmark and the
rest, and it was not fitted - it falls out of a restriction applied identically to
all four.

## Coordinator errors in this round, disclosed

1. **Vacuous null on LongMemEval** (above): within-archive shuffling is the identity
   when every archive holds one query. Corrected with a global permutation; the
   other three benchmarks were unaffected. Original output retained in
   `evidence/survivor_tests.json`, correction in `evidence/survivor_corrected.json`.
2. **No frozen prediction for two of four packages.** Rather than write predictions
   after seeing results, both are labelled EXPLORATORY. The dispatch briefs (which
   contain the hypotheses) predate the measurements and are the only freeze available.

## Not done

- `scale-honest` synthesis comparison (its steps 3-6) never ran: the session died
  after step 2. Its control, scope table and frozen PREDICTION.md are included; the
  synthesis comparison remains open.
- No causal claim. Findings 1 and 2 are interventions on the representation and are
  therefore stronger than the eight dead correlational stories, but "sign
  quantization behaves differently at different axis budgets" is a description, not
  a mechanism.
- Dead mechanism candidates now number **nine** (norm informativeness joins the
  list); the BOT64 survivor is downgraded from "survivor" to "partly redundant with
  competition on 2/4 benchmarks".
