[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# SCALE_FACTS.md — first-hand facts about SIGN96 retrieval vs archive size N

All numbers below are **VERIFIED** (computed this session from the named cache bytes) unless
explicitly labelled CLAIM or RELAYED. Code: `control.py`, `scale.py`, `sweep.py`, `pin.py`,
`final.py`, `variants.py`, `mech.py`. Raw output: `evidence/*.txt`, `evidence/*.json`.

---

## F1. Control — frozen headlines reproduced BEFORE any new number

VERIFIED · `control.py` → `evidence/control.json` · exact tie expectation, no re-centering.

| family | sign FR@3 | float FR@3 | delta (pp) | frozen delta (CLAIM, task context) | residual |
|---|---|---|---|---|---|
| LongMemEval (470 q) | 0.5421335697399526 | 0.4415957446808511 | **+10.053783** | +10.037943 | +0.0158 pp |
| PerLTQA (8265 q, 30 arch) | 0.48894479616364206 | 0.551692074528853 | **−6.274728** | −6.275 | +0.0003 pp |
| REALTALK (705 q) | 0.22553482307028402 | 0.17253405381064957 | **+5.300077** | +5.2241 | +0.0760 pp |

The sign arm on LME matches the frozen gate `0.5419751773049645` to 1.6e-4 (the frozen number is a
20-seed Monte-Carlo average of the same expectation; the residual is the reference's sampling
noise, smallest on the largest sample). **Control passes. New numbers are trustworthy.**

Cache centering re-confirmed: column-mean abs max = 7.10e-16 (LME), 4.41e-16 (PerLTQA). Not
re-centered anywhere in this session.

## F2. Natural N ranges — the hard constraint on what "scale" can even be observed

VERIFIED · `evidence/control.json`.

| family | archives | N range | mean N |
|---|---|---|---|
| LongMemEval | 470 | **396 – 616** | 492.8 (median 490) |
| PerLTQA | 30 | **293 – 546** | 409.6 |
| LoCoMo | 10 | **369 – 689** | — |
| REALTALK | 10 | **410 – 1548** | — |

**No real archive in this programme exceeds N=1548.** Every claim about N≥2000 — the
coordinator's, the relayed one, and mine — is necessarily about *synthesised* large archives
(pooling or simulation), not about observed ones. This is the single most important fact in this
document.

## F3. P0 identity: `bc > slots` ≡ `gap == 0`, exactly

VERIFIED · `analyze.py` → 852,336 checks across sections A/B/C and K∈{1,3,5,10,20,50}:
**0 disagreements.** Proof: `strictly + bc ≥ K` always, so
`bc > K − strictly ⟺ #{d ≤ d_(K)} > K ⟺ d_(K+1) = d_(K)`.
→ *"`gap==0` vs `bc>slots`" is NOT a candidate explanation for the contradiction. Same event.*

## F4. Method (a) — POOLING independent archives: tie rate RISES

VERIFIED · `scale.py A` + `analyze.py` · all 470 LME queries at every rung (paired), nested pools.

| N | frozen tie (K=3) | shared (bc>1) | K=1 | K=10 | mean d₍₃₎ | mean bc |
|---|---|---|---|---|---|---|
| 493 | **0.234** | 0.385 | 0.128 | 0.626 | 28.13 | 1.53 |
| 986 | **0.260** | 0.396 | 0.138 | 0.677 | 27.98 | 1.56 |
| 1971 | **0.260** | 0.421 | 0.138 | 0.747 | 27.75 | 1.63 |
| 4928 | **0.285** | 0.445 | 0.155 | 0.766 | 27.41 | 1.77 |
| 9856 | **0.294** | 0.457 | 0.162 | 0.779 | 27.18 | 1.83 |
| 24640 | **0.345** | 0.504 | 0.162 | 0.804 | 26.76 | 1.95 |

Coordinator's six numbers (RELAYED in task): 0.233 / 0.250 / 0.217 / 0.317 / 0.342 / 0.367.
**Reproduced in level and direction** (mean abs diff 0.030; the 0.217 at N≈1978 vs my 0.260 is the
one visible discrepancy, consistent with a different pooling draw at n=120 vs my n=470).
Monotone rising, +11.1 pp over 50×N.

Float arm tie rate: **0.0000 at every rung** — continuous cosines essentially never tie. The float
arm cannot produce 54% under any N.

## F5. Method (b) — SUBSAMPLING rows inside ONE real archive: tie rate FALLS above N≈50

VERIFIED · `sweep.py F` (470 LME archives, 20 reps) and `variants.py` (pure random, no gold
forcing) and `final.py L`.

Pure random subsample, no gold forcing (`evidence/final.txt`):

| N | LME frozen | LoCoMo frozen | REALTALK frozen | mean d₍₃₎ (LME) |
|---|---|---|---|---|
| 10 | 0.285 | 0.268 | 0.270 | 45.04 |
| 25 | 0.353 | 0.336 | 0.335 | 41.90 |
| 50 | **0.355 (peak)** | 0.360 | 0.359 | 39.73 |
| 100 | 0.328 | 0.363 | 0.365 | 37.27 |
| 200 | 0.273 | 0.356 | 0.333 | 33.93 |
| 400 | **0.245** | 0.349 | 0.329 | 29.36 |
| 800 | — | — | 0.374 | — |
| 1400 | — | — | 0.373 | — |

**The tie rate is NON-MONOTONE: it rises to a peak near N≈50, then falls.** On LME it falls 0.355 →
0.245 between N=50 and N=400. Then — where real data runs out and pooling takes over — it rises
again, 0.234 → 0.345.

## F6. The mechanism that resolves the contradiction

VERIFIED · `mech.py` → `evidence/mech.txt`.

The controlling quantity is the **speed at which the K-th order statistic d₍₃₎ moves left** versus
the local density it lands in.

| growth mode | d₍₃₎ drift | tie rate |
|---|---|---|
| **within-archive** (subsample LME 10→396) | **−2.869 bits per doubling of N** | 0.276 → 0.236 (falls after peak) |
| **pooling** (unrelated archives, 493→24640) | **−0.244 bits per doubling of N** | 0.234 → 0.345 (rises) |

A factor of **11.8×** difference in drift rate. This is the whole story:

- Adding *related* rows (a real archive growing) supplies new rows that are genuinely close to the
  query, so d₍₃₎ marches left fast, into the sparse left tail, where the integer support is thinly
  occupied → fewer collisions → tie rate falls.
- Adding *unrelated* rows (pooling) supplies almost only far mass (mean distance 47.88 → 47.97;
  d_min barely moves, 22.08 → 21.59). d₍₃₎ is nearly pinned, so all the extra N does is pile more
  rows onto the *same* threshold integer: mean bc 1.53 → 1.95 → tie rate rises.

**Both directions are real. They are two different physical processes, not a measurement error.**

## F7. Method (c) — natural N spread, real archives only, no synthesis

VERIFIED · `scale.py C` + `analyze.py`; per-archive Pearson r against N.

| family | n_arch | N range | r(frozen tie, N) | r(shared, N) | per-query mean tie |
|---|---|---|---|---|---|
| LME | 470 | 396–616 | **+0.080** | +0.021 | 0.2340 |
| PerLTQA | 30 | 293–546 | **+0.301** | +0.312 | 0.2920 |
| LoCoMo | 10 | 369–689 | **+0.048** | +0.352 | 0.3448 |
| REALTALK | 10 | 410–1548 | **+0.417** | +0.694 | 0.3585 |

All four correlations are **positive**, but every family's N span is far too narrow (≤1.6× except
REALTALK's 3.8×) and n_arch too small (10–30 except LME) for these to be decisive. With n=10
archives, r=+0.417 is not significant (p≈0.23). LME's r=+0.080 over 470 archives is the tightest
estimate and it is essentially null over a 1.6× span.

**Per-archive vs per-query averaging changes nothing**: LME 0.2340 vs 0.2340; PerLTQA 0.2920 vs
0.2917; LoCoMo 0.3448 vs 0.3458; REALTALK 0.3585 vs 0.3589. That candidate explanation is dead.

## F8. The definition sweep — 48 definitions tested

VERIFIED · `sweep.py E`/`F`, `variants.py`, `pin.py`.

**On the POOLED ladder, every one of the 15 tie-flavour variants RISES.** Not one falls. Including:
`bc>slots`, `bc≥2`, `bc≥3`, `bc>slots+1`, `d₁=d₂`, `d₂=d₃`, `unique(top3)<3`, band-1, band-2,
overflow size, expected-random-fraction, K∈{1,2,5,10,20,50,100}. See `evidence/variants.txt`.

**On the SUBSAMPLE ladder (N=10→396), 8 of 15 variants FALL** after their N≈25–50 peak. See F5.

**Statistics that fall monotonically and hard, on BOTH ladders** — these are positional, not
tie-flavoured:
- `P(d₍₃₎ ≥ 40)`: subsample 0.990 (N=10) → 0.000 (N=400); pooled 0.000 flat.
- `P(d₍₃₎ ≥ 30)` on the POOLED ladder: **0.440 → 0.440 → 0.423 → 0.379 → 0.330 → 0.204** — falls
  by a factor 2.2 over exactly the N rungs where the frozen tie rate rises 0.234 → 0.345.
- `bc/N`: 0.056 → 0.003 (subsample). Falls by construction (bc grows sublinearly in N).

## F9. Where the relayed "54% → 26%" lives

VERIFIED · best L1 fits, `mech.py` → `evidence/mech.txt`.

| candidate | ladder | values | L1 err vs (0.54, 0.26) |
|---|---|---|---|
| `P(d₍₃₎ ≥ 30)` | **pooled 493→24640** | 0.440 / 0.440 / 0.423 / 0.379 / 0.330 / **0.204** | 0.155 |
| `P(d₍₃₎ ≥ 29)` | pooled | 0.500 / … / 0.379 | 0.159 |
| `bc ≥ 2` (shared) | **subsample 10→396** | 0.459 / 0.537 / 0.537 / 0.495 / 0.418 / **0.374** | 0.195 |
| `any dup in top-4` | subsample | 0.536 / … / 0.453 | 0.197 |

No definition I tested reproduces 0.54→0.26 exactly. The closest, and the one whose *mechanism
story matches the relayed one verbatim*, is the **positional statistic
`P(d₍₃₎ ≥ t)` for t≈29–30** — "is the 3rd-nearest still inside the concentrated mass, or has it
moved into the sparse tail?" That is *literally the sentence in the relayed mechanism story*, and
it genuinely falls. But it is **not a tie rate**: it is a statement about *where* d₍₃₎ sits, and
it is compatible with the frozen tie rate rising at the very same N.

## F10. SIGN-minus-float delta vs N

VERIFIED · `sweep.py G` → `evidence/EG.log`; paired, all 470 LME queries at every rung.

| N | sign FR@3 | float FR@3 | delta (pp) | paired Δ vs N=493 | t |
|---|---|---|---|---|---|
| 493 | 0.5421 | 0.4416 | **+10.05** | — | — |
| 986 | 0.5314 | 0.4416 | **+8.98** | −1.07 ± 0.32 | +3.31 |
| 1971 | 0.5218 | 0.4416 | **+8.02** | −2.03 ± 0.50 | +4.09 |
| 4928 | 0.4970 | 0.4398 | **+5.72** | −4.34 ± 0.75 | +5.81 |
| 9856 | 0.4820 | 0.4377 | **+4.43** | −5.63 ± 0.89 | +6.33 |
| 24640 | 0.4588 | 0.4320 | **+2.67** | −7.38 ± 1.05 | **+7.05** |

**This is the one place where sample size DOES permit a claim, and only because the design is
paired.** The coordinator's n=120 unpaired deltas (10.0 / 7.0 / 14.3 / 2.6 / 7.6 / 3.6 pp) looked
non-monotone and noise-dominated — at n=120 the unpaired SE is ≈3.3 pp, so that spread is
uninformative. At n=470 **paired on the same queries with a nested pool**, the same-query
difference has SE ≈ 0.3–1.1 pp and the trend is monotone with t=+7.05 at the far rung.

**The LME SIGN advantage decays monotonically with pooled N: +10.05 pp → +2.67 pp over 50×.**
The decay is driven almost entirely by the sign arm falling (0.5421 → 0.4588, −8.3 pp) while the
float arm is nearly flat (0.4416 → 0.4320, −1.0 pp).

CAVEAT, stated plainly: this is measured on **pooled** archives only. F6 shows pooling is a
physically different growth process from a real archive growing, so this decay curve is
**not** licensed as a prediction for a real 100K-row archive. Within real data the N span is too
narrow (1.6×) to measure any delta trend: LME r(delta, N) = −0.012 over 470 archives.

## F11. Synthetic controls

VERIFIED · `scale.py D` → `evidence/D.log`. 200 queries per cell.

| codes | N=50 | N=500 | N=5000 | N=25000 | N=100000 |
|---|---|---|---|---|---|
| uniform random signs | 0.420 | 0.560 | 0.545 | 0.560 | **0.615** |
| low-rank 8 (correlated) | 0.215 | 0.340 | 0.415 | **0.580** | — |
| low-rank 32 (correlated) | — | 0.440 | 0.505 | 0.550 | — |

All three **rise**. Uncorrelated uniform codes — the exact model behind the relayed mechanism
story ("concentrated mass at ~48 of 96 bits") — reach 0.42–0.62, i.e. **the ~54% level the relayed
measurement reports**, but they rise with N rather than falling. If the relayed run used synthetic
uniform codes it would have gotten the 54% level right and the direction wrong.

## F12. Adversarial self-checks

VERIFIED · `pin.py` → `evidence/pin.txt`.

- **J1** float32 matmul Hamming ≡ popcount Hamming, exact array equality. No numerical artifact.
- **J2** Pooling adds only far mass: d_min 22.08 → 21.59 over 50×N; mean distance 47.88 → 47.97.
  Confirms pooling's growth is qualitatively unlike real archive growth.
- **J3** *Most damaging assumption tested*: "the only real family with a wide natural N span agrees
  with pooling." REALTALK, 10 real archives, N=410→1548, **no pooling, no subsampling**:
  0.386 / 0.296 / 0.342 / 0.300 / 0.294 / 0.310 / 0.556 / 0.300 / 0.371 / 0.434; r = **+0.417**
  (p≈0.23, n=10). Direction agrees with pooling but is **not statistically significant**, and the
  0.556 at N=1162 is a single high-leverage archive. This check does not rescue either side.
- **J4** Tie statistics never read gold, so gold-forcing cannot bias any tie ladder. It *can* bias
  the F delta ladder (gold is 1/25 of the pool at N=25 vs 1/493 at full) — which is why the delta
  claim in F10 rests on the **pooled paired** design (G), not on F.
