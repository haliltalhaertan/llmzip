# V52 — Coordinate-Scale Participation: Preregistered Result Checkpoint

Date: 2026-09-07
Status: `[PREREGISTERED RESULT — RECORDED AS COMPUTED, NOT YET INDEPENDENTLY AUDITED]`
Author: Continuity Lead / co-chair. This document records; it does not audit. Nothing below is
established until a cold-start independent audit has reproduced it from the persisted bytes.

Labels that must travel together whenever this stage is cited:

> `[COORDINATE-SCALE PARTICIPATION LEAD — MOST (LoCoMo) / PARTIAL (LongMemEval) FOR FULL MIXING]`
> `[BLOCK-ARM FRACTION NOT INTERPRETABLE ON LoCoMo — DENOMINATOR NEAR ZERO]`
> `[NOT INDEPENDENTLY AUDITED]`

## 1. Provenance

| item | value |
|---|---|
| preregistration (verbatim v3) | `research/v52/V52_COORDINATE_SCALE_PARTICIPATION_PREREG_2026-09-05.md`, sha256 `de6672119010bf561179014748e21836bff5c0ebf6efa10379213c59de5203fe` |
| pre-run seal | `research/v52/V52_COORDINATE_SCALE_PRERUN_SEAL_2026-09-05.json`, git blob `52605626a403bc385cc6e1f0e3fe43970099d76c`, commit `2a070062` |
| package head before seal | `59ae1b53d3c4e524621d87a08b396f72a8332816` |
| trigger (once) | commit `680b10b8a3ef3dd55a5a05fe47f6fb5fa6d931d0`, 2026-09-07T07:06:19Z |
| LoCoMo result commit | `f1bbb50` (runner-authored, 07:07:20Z) |
| LongMemEval result commit | `bce57b64dd2451d4d7bc0cd2c6e61d84e35261c8` (runner-authored, 07:11:15Z) |
| environment (both) | `numpy==2.3.5 pandas==2.2.3 scipy==1.17.0 scikit-learn==1.8.0` |
| Head Researcher authorization | chat text 2026-09-07 ("yetki sende devam et"); L-054 on `main` |

Persisted result bytes at `bce57b64`:

| file | git blob | sha256 (per-question) |
|---|---|---|
| `locomo_scale_outputs/locomo_scale_summary.json` | `2664f722` | — |
| `locomo_scale_outputs/locomo_scale_per_question.csv.gz` | `63b81385` | `b7abd942c13cf9ce…` (278,724 bytes; the LoCoMo summary carries no `artifacts` block — a runner omission, recorded here instead) |
| `longmemeval_scale_outputs/longmemeval_scale_summary.json` | `c7829cae` | — |
| `longmemeval_scale_outputs/longmemeval_scale_per_question.csv.gz` | `1619a668` | matches the summary's `per_question_sha256` (94,324 bytes) |

Verification performed by the Continuity Lead (not an audit): both summaries' `frac_full` and
`frac_block` were recomputed from the per-question rows and match to better than `1e-9`.

## 2. Controls — all preregistered controls passed on both benchmarks

| control | LoCoMo | LongMemEval |
|---|---|---|
| native reproduction vs frozen anchor | `0.23654714666441054`, error `0.0` | `0.5419751773049645`, error `1.1e-16` |
| `SCALED_NATIVE` bit-identical to `NATIVE` on distances | PASS | PASS |
| within-representation norm max abs error (TOL 1e-12) | `5.3e-15` | `7.1e-15` |
| within-representation dot max abs error (TOL 1e-12) | `1.1e-13` | `5.7e-14` |
| per-question rows expected / actual | 92,100 / 92,100 (1,535 q × 10 seeds × 6 arms) | 28,200 / 28,200 (470 × 10 × 6) |
| degenerate coordinates (eps 1e-12) | max 0, flagged 0 of 10 archives | max 0, flagged 0 of 470 archives |
| `CV(sigma)` before rescaling, median [range] | 0.494 [0.438, 0.508] | 0.497 [0.476, 0.553] |
| `CV(sigma)` after rescaling, max | `5.8e-16` | `5.7e-16` |

Note on the LoCoMo dot error: `1.1e-13` is within TOL with roughly 9× headroom, less than the
`~1e-15` the audited stages reported. L-049 said in advance that such a value is information about
the check's scale and not licence to touch TOL. TOL was not touched.

## 3. Primary estimand — as preregistered (§7), reported per arm

Seed-panel means over rotation seeds `59001..59010`:

| arm | LoCoMo R@3 | LongMemEval R@3 |
|---|---:|---:|
| `NATIVE` (= `SCALED_NATIVE`) | 0.236547147 | 0.541975177 |
| `FULLHAAR_FRESH` | 0.139131063 | 0.380938652 |
| `SCALED_FULLHAAR` | 0.209865554 | 0.486632447 |
| `BLOCK32_FRESH` | 0.231215522 | 0.515704078 |
| `SCALED_BLOCK32` | 0.234689837 | 0.523807624 |

| quantity | LoCoMo | LongMemEval |
|---|---:|---:|
| denominator_full = NATIVE − FULLHAAR_FRESH | 0.097416 (sd 0.0052, se 0.0016, range 0.0886–0.1053) | 0.161037 (sd 0.0115, se 0.0036, range 0.1478–0.1849) |
| **`frac_full`** | **0.7261** | **0.6563** |
| `frac_full` per seed | 0.791, 0.650, 0.725, 0.730, 0.831, 0.638, 0.753, 0.723, 0.764, 0.667 | 0.666, 0.520, 0.649, 0.616, 0.736, 0.706, 0.701, 0.657, 0.707, 0.613 |
| `frac_full` band (§7) | `[SCALE ACCOUNTS FOR MOST OF THIS ARM'S DAMAGE]` (≥ 0.70) | `[PARTIAL]` (0.20 < 0.656 < 0.70) |
| denominator_block = NATIVE − BLOCK32_FRESH | 0.005332 (sd 0.0074, se 0.0023, **range −0.0066 to +0.0164**) | 0.026271 (sd 0.0088, se 0.0028, range 0.0098–0.0402) |
| **`frac_block`** | **0.6516** (on the seed-mean) | **0.3085** |
| `frac_block` per seed | 1.16, 2.21, 1.23, **−1.81**, 2.64, 0.23, 0.79, **−3.40**, 0.84, 0.56 | 0.71, 0.34, 0.60, 0.27, 0.30, 0.03, 0.25, **−0.13**, 0.44, 0.35 |
| `frac_block` band (§7) | `[PARTIAL]` — but see §4 | `[PARTIAL]` |

Secondary (§7): `I_frac = frac_full − frac_block` = **+0.074** (LoCoMo), **+0.348** (LongMemEval).

Descriptive only, barred from carrying any verdict (§7): `delta_full` = +7.07 pp (LoCoMo), +10.57 pp
(LongMemEval); `delta_block` = +0.35 pp, +0.81 pp.

## 4. Reading, strictly within §9 of the preregistration

**Full mixing.** On both benchmarks, rescaling the centered archive representation to unit
per-coordinate variance before a fresh full Haar rotation recovers most of the damage that rotation
does: 73% of it on LoCoMo (every seed above 0.63; the seed-panel mean clears the 0.70 band) and 66%
on LongMemEval (seeds 0.52–0.74; the mean falls in the preregistered `[PARTIAL]` band, 0.044 short
of `MOST`). Under §9 this **supports that relative coordinate scale participates** in the damage
from cross-band mixing. It does **not** establish exclusive mediation, does **not** identify the
mechanism, claims nothing about production retrieval, and does not transfer beyond this pipeline.

**The two benchmarks disagree on the band.** This is reported as heterogeneity, not averaged away:
LoCoMo `MOST`, LongMemEval `PARTIAL`. The preregistration set the bands per dataset; there is no
preregistered cross-benchmark rule, so none is applied.

**Block arm — LoCoMo fraction is not interpretable.** `BLOCK32_FRESH` loses almost nothing on
LoCoMo (denominator 0.0053, one twentieth of the full-mixing loss), the per-seed denominator changes
sign twice, and `frac_block` per seed ranges from −3.40 to +2.64. A ratio whose denominator crosses
zero inside its own seed envelope does not measure a share. The preregistered band on the seed-mean
(`[PARTIAL]`) is recorded as computed and **must not be quoted as a finding**. This is a design
limitation the pilot could not have seen: it assumed block mixing would carry a measurable loss. On
LongMemEval the block denominator is small but positive on every seed (0.0098–0.0402), and
`frac_block` = 0.31 (`[PARTIAL]`) is interpretable, with wide per-seed spread (−0.13 to 0.71).

**Interaction (secondary).** `I_frac` is +0.07 on LoCoMo and +0.35 on LongMemEval. Because the
LoCoMo block fraction is not interpretable, the LoCoMo interaction inherits that status. On
LongMemEval, rescaling helps full mixing more than within-block mixing on the fraction scale. §7 made
this secondary precisely because the pilot showed it can vanish; here it did not vanish on
LongMemEval, which is reported and not promoted.

**Where the real archives sit on the `CV(sigma)` axis** (§13, declared diagnostic): ≈ 0.49–0.50 on
both benchmarks, below the pilot's synthetic range where recovery was ≈ 1.0. The real recovery
(0.66–0.73) is lower than the synthetic model predicted at any heterogeneity it explored. The pilot
model had no inter-coordinate correlation structure; this gap is consistent with §9's statement that
a null or partial result does not exclude correlation structure or subspace alignment as the
operative channel. No mechanism is inferred from this.

## 5. By-product — the Full-Haar denominator now has a measured dispersion on BOTH benchmarks

`FULLHAAR_FRESH` gives the reference its own ten-seed panel (prereg §6, "closes as by-product"):

| benchmark | inherited Full-Haar R@3 (frozen) | fresh 10-seed mean | sd | se | difference fresh − inherited |
|---|---:|---:|---:|---:|---:|
| LoCoMo | 0.13770827054136 (5 seeds, dispersion **never committed**) | 0.139131 | 0.0052 | 0.00164 | +0.0014 (0.27 sd) |
| LongMemEval | 0.38271666666667 (5 seeds; sd 0.0149 from `audit_v52_t4c3`, L-051) | 0.380939 | 0.0115 | 0.00362 | −0.0018 (0.15 sd) |

This measures, for the first time from committed bytes, the LoCoMo denominator's sampling
dispersion — the item L-051 and the takeover prompt §7C left open as "needs a re-run". The
arithmetic consequence for the boundary-localization line is left to an additive sensitivity
addendum on the research track and to its auditor; it is **not** computed here, and the frozen
denominators in the audited stages are **not** replaced. Note the seed panels differ
(`43001..43005` / the LoCoMo original vs `59001..59010`), so these are independent draws of the
same distribution under the same pipeline, not a re-measurement of the same numbers.

## 6. What is not licensed

- No claim that scale is *the* mechanism, or the only one.
- No claim about the block arm on LoCoMo.
- No cross-benchmark pooled fraction.
- No re-run, no additional seeds, no alternate scale rule, no alternate `eps`, no threshold movement
  (§11 no-tuning rule). This stage is closed as computed.
- No citation of this stage before a cold-start independent audit reproduces §2–§3 from the
  persisted per-question rows and re-executes at least one benchmark end to end.

## 7. Outcome boundary

LoCoMo and LongMemEval only. No BEAM corpus, no Task 4F1 artifact, candidate, seal, authorization,
HMAC material or outcome was touched. Task 4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION /
OUTCOME ACCESS FORBIDDEN`.
