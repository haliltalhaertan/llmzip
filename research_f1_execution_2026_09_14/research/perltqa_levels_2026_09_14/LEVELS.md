[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# LEVELS.md — per-gold competition levels, PerLTQA

Everything below is **VERIFIED** (computed first-hand this session) unless marked CLAIM/RELAYED.
Code: `levels.py`, `step3b.py`, `step0_axis_stat.py`. Raw numbers: `evidence/levels_summary.json`,
`evidence/results.json`, `evidence/paired_archives.json`.

## 0. Gates — passed BEFORE any new number was trusted

**Gate 1 (frozen headline control).** VERIFIED, `control.py`, output of run 1:

| quantity | recomputed | frozen reference | match |
|---|---|---|---|
| PerLTQA float FR@3 | `0.551692074528853` | `0.551692074528853` | exact |
| PerLTQA SIGN FR@3 | `0.48894479616364206` | `0.488941994930817` | 2.8e-6 (exact tie-expectation vs NT=20 sampling) |
| PerLTQA Delta | `-6.274727836521104` pp | `-6.275` / coordinator `-6.274728` | exact |
| profile / social / events / dialogues | `+20.355355 / -0.780016 / -12.393717 / -1.501652` | coordinator identical | exact to 6 dp |

**Gate 2 (independent R2 audit targets).** VERIFIED, `step3b.py:30-44`. My per-gold competition
rows reproduce the Spearman targets published in
`R2_COMPETITION_RERUN_CONTRACT.md` § "Expected independent-audit targets" — a surface I did
not build and could not have tuned to:

| stratum | my strict rho | audit target | my tie rho | audit target |
|---|---:|---:|---:|---:|
| overall | 0.254138443914630 | 0.25416826537535475 | 0.279827154049907 | 0.27978783415712220 |
| dialogues | 0.130594370386 | 0.130541267341 | 0.111238631131 | 0.111230872544 |
| events | 0.398023560493 | 0.397906347805 | 0.389259732336 | 0.389228320696 |
| profile | 0.057497403356 | 0.057325302878 | 0.018965472076 | 0.018738683423 |
| social_relationship | 0.304228181417 | 0.304285158020 | 0.299166990868 | 0.299301321322 |

Max deviation 1.2e-4, consistent with the audit using the NT=20 sampled Delta surface where I
use the exact tie expectation. Both gates pass, so the levels below are trustworthy.

## 1. Axis ordering statistic — mean of squares vs variance

VERIFIED (`step0_axis_stat.py`): they **coincide exactly** here, as the task anticipated.

- Full 96-axis ordering identical in **30/30** archives; TOP64 set identical in **30/30**.
- `max |mean_i(C_ij^2) - var_j| = 2.082e-17` across all axes and archives.
- Reason: the cached `C` is already centered (`max |column mean| = 4.41e-16`), and numpy's
  default `ddof=0` variance of a centered matrix *is* the mean of squares.

**Decision recorded:** I used the spec statistic `v_j = mean_i(C_ij^2)`
(`R2_COMPETITION_RERUN_CONTRACT.md` § "TOP64 / BOT64 construction"), stable descending sort,
TOP64 = first 64, BOT64 = last 64. `step2_eval.py:29` uses `C.var(axis=0)`; on this data the
two are the same object to 2e-17, so no choice was forced. **I did not re-center anything.**

## 2. THE LEVELS (the decisive numbers)

Per gold row `g`, arm `A`: `strict_all = #{i: d_A(i) < d_A(g)}`, `tie_all = #{i: d_A(i) == d_A(g)}`
(tie includes `g`), averaged arithmetically over the query's gold rows; `GAP = TOP64 - BOT64`.
Exactly the R2 contract's primary definition. n=8265, 30 archives, N ranges 293..546.

| section | n | **Delta pp** | strict_TOP64 | strict_BOT64 | **STRICT_GAP** | tie_TOP64 | tie_BOT64 | **TIE_GAP** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **profile** | 333 | **+20.355** | 59.460 | 54.727 | **+4.733** | 14.598 | 11.390 | **+3.207** |
| dialogues | 2742 | −1.502 | 115.418 | 190.244 | **−74.826** | 22.234 | 25.492 | −3.258 |
| social_relationship | 844 | −0.780 | 6.992 | 32.101 | **−25.109** | 3.557 | 9.807 | −6.250 |
| events | 4346 | −12.394 | 11.137 | 33.017 | **−21.880** | 4.532 | 10.041 | −5.509 |

### Distributions (not just means)

| section | GAP median | p5 | p25 | p75 | p95 | frac>0 | frac<0 | frac=0 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| profile | **+1.00** | −122.40 | −1.00 | +19.00 | +125.80 | **0.5405** | 0.2553 | 0.2042 |
| dialogues | −74.66 | −214.99 | −131.18 | −13.61 | +57.57 | 0.1754 | 0.8158 | 0.0088 |
| events | −1.00 | −154.75 | −16.00 | 0.00 | +8.00 | 0.1756 | 0.5350 | 0.2895 |
| social_relationship | −1.00 | −174.20 | −19.00 | 0.00 | +3.85 | 0.1114 | 0.5391 | 0.3495 |

TIE_GAP frac>0: profile 0.5405, dialogues 0.3673, events 0.1457, social 0.1078.

**Within-archive paired test** (same `C`, same `v`, same TOP64/BOT64 — the only clean contrast;
`evidence/paired_archives.json`): `STRICT_GAP(profile) > STRICT_GAP(events)` in **25/30**
archives; mean profile +6.35 vs events −22.71. `strict_TOP64(profile) > strict_TOP64(events)`
in **30/30**.

## 3. Which surviving picture the levels kill

The two pictures made opposite predictions about the **level** of the gap in the SIGN-winning
section. The measurement is unambiguous **within PerLTQA**:

> **Profile — the only section where SIGN wins (+20.355 pp) — is the only section with a
> POSITIVE STRICT_GAP (+4.733) and the only one with a POSITIVE TIE_GAP (+3.207).
> All three losing sections have negative gaps.** The ordering holds on medians and on
> frac>0, and survives the within-archive paired contrast (25/30).

So **the picture predicting that SIGN wins when gold faces MORE competition on the
high-variance arm than on the low-variance arm (positive gap) is the one consistent with
PerLTQA levels**; the picture requiring a negative gap in the SIGN-winning section is
**killed on PerLTQA levels**.

**That verdict does not survive contact with the other benchmarks — see § 5.** I state both
here rather than reporting only the flattering half.

## 4. Geometry: what makes a PROFILE query different from an EVENTS query on the SAME archive

Distributions by section (mean, and p5/p25/med/p75/p95); within-archive paired counts out of 30.

| statistic | profile | events | dialogues | social | paired profile>events |
|---|---:|---:|---:|---:|---:|
| query norm | **0.8915** | 0.9351 | 0.9234 | 0.9288 | **0/30** |
| qPR (participation ratio, eff. dim of q) | **9.141** | 11.835 | 11.619 | 11.126 | 4/30 |
| q_top_share (energy on TOP64 axes) | 0.9422 | 0.9469 | 0.9456 | 0.9553 | 11/30 |
| q_absmax_share (largest single axis) | **0.2798** | 0.2129 | 0.2213 | 0.2216 | — |
| ALIGN = cos(q², v) | **0.4119** | 0.5301 | 0.4941 | 0.5290 | **1/30** |
| gold norm / mean doc norm | **1.0754** | 1.0110 | 0.9961 | 1.0413 | **30/30** |
| float margin (gold − best non-gold cos) | **−0.2449** | +0.0055 | −0.2005 | −0.0014 | **0/30** |
| Hamming margin | −4.556 | −1.717 | −7.763 | +1.396 | 5/30 |
| Hamming near-ties | **55.37** | 12.37 | 38.04 | 9.82 | — |
| Hamming exact ties at gold distance | 7.75 | 2.51 | 6.68 | 2.06 | — |
| gold Hamming distance | 34.30 | 28.93 | 35.04 | 27.97 | — |

Percentile detail (p5 / p25 / med / p75 / p95):

- `qPR` profile 3.85 / 5.84 / 8.45 / 11.61 / 17.14 vs events 5.95 / 9.07 / 11.64 / 14.33 / 18.38
  — profile's distribution is shifted low and is **wider at the bottom**, but the ranges overlap
  heavily. This is a distributional shift, not a separation.
- `ALIGN` profile 0.257 / 0.331 / 0.410 / 0.489 / 0.569 vs events 0.341 / 0.463 / 0.538 / 0.609 /
  0.688 — the cleanest single separator, still with substantial overlap.
- `float_margin` profile −0.557 / −0.365 / −0.256 / −0.120 / +0.087 vs events −0.206 / −0.057 /
  +0.015 / +0.083 / +0.179. Profile gold is **usually not the float-nearest document**; events
  gold usually is.
- `ham_neartie` profile 0 / 0 / 3 / 53 / 286 vs events 0 / 0 / 1 / 4 / 69.

**Geometric characterisation (VERIFIED):** a profile query is *lower-norm, spectrally more
concentrated* (qPR 9.1 vs 11.8; one axis carries 28% of its energy vs 21%), and its energy sits
**off** the archive's high-variance directions (ALIGN 0.412 vs 0.530, paired 29/30). Its gold
documents are **unusually long vectors** (1.075x mean doc norm, paired 30/30) yet the float
cosine still ranks a non-gold document first (margin −0.245, paired 30/30). Float's
magnitude weighting is actively mis-ranking profile golds; SIGN's equal-weight bits are not.
This is a coherent story — and § 5 shows it still does not generalise.

## 5. The level cannot set the sign (out-of-sample, VERIFIED)

Same definitions, same code path, all four benchmarks (`step6_levels_xbench.py`, `step8_locomo.py`):

| benchmark | n | mean Delta pp | mean STRICT_GAP | mean TIE_GAP | sign(gap)==sign(Delta)? |
|---|---:|---:|---:|---:|---|
| LongMemEval | 470 | **+10.054** | **−19.167** | −2.461 | **FAIL** |
| REALTALK | 705 | +5.300 | +0.248 | +0.107 | PASS |
| LoCoMo | 1535 | **+6.655** | **−5.784** | — | **FAIL** |
| PerLTQA | 8265 | −6.275 | −38.703 | −4.487 | PASS |

**LongMemEval and PerLTQA have gaps of the SAME sign (both negative) and Deltas of OPPOSITE
sign.** One counterexample is enough: the *level* of the per-gold competition gap does not
determine the sign of Delta. The PerLTQA-internal verdict in § 3 is therefore a
**within-benchmark regularity, not a mechanism.**

A stratum-level rule "mean STRICT_GAP > 0 ⇒ Delta > 0" scores **11/24 = 45.8%** across 24 strata
(4 PerLTQA sections, 10 REALTALK chats, 10 LME archive-size deciles) against a **79.2%** majority
baseline — worse than chance, the same failure mode that killed boundary-competition density.

What *is* stable is the **slope**, not the level: per-query `rho(Delta, STRICT_GAP)` is positive
in all four benchmarks (LME +0.1416, REALTALK +0.0979, PerLTQA +0.2541, LoCoMo +0.1033 — the last
two of which match published audit targets), and `rho(Delta, strict_BOT64)` is the most stable
statistic measured: **−0.185 / −0.179 / −0.195 / −0.308**. Each benchmark carries its own
unexplained offset that the gap cannot see.
