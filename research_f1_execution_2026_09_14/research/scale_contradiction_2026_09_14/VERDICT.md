[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# VERDICT.md — the two measurements measure different things

## Ruling

**NEITHER measurement is wrong. They are two different physical processes, and — separately — the
relayed number is not a tie rate at all.** Three findings, in order of importance:

### 1. Pooling and real-archive growth move the tie rate in OPPOSITE directions. Both are real.

VERIFIED (SCALE_FACTS F4, F5, F6):

| growth mode | N span | frozen K=3 tie rate | d₍₃₎ drift |
|---|---|---|---|
| **pooling unrelated archives** | 493 → 24640 | **0.234 → 0.345 (RISES)** | −0.244 bits/doubling |
| **subsampling within one real archive** | 50 → 400 | **0.355 → 0.245 (FALLS)** | −2.869 bits/doubling |

The coordinator's six numbers reproduce (mean abs diff 0.030, same direction, same levels). The
subsample ladder, which isolates N from pooling, **disagrees with pooling and agrees in direction
with the relayed claim** over the range where real data exists.

The controlling variable is how fast the K-th order statistic moves left relative to the density it
lands in. Related rows push d₍₃₎ left **11.8× faster** than unrelated rows do. Fast leftward drift
lands d₍₃₎ in the sparse tail → fewer collisions → tie rate falls. Near-pinned d₍₃₎ just accumulates
more rows on the same integer (mean bc 1.53 → 1.95) → tie rate rises.

**So: is pooling an artifact?** Answering the question as asked — *does (b) agree with (a) or with
the relayed claim?* — **(b) agrees with the relayed claim's direction, not with pooling.**
Pooling is not an *error*, but it is **not a valid simulation of a real archive growing**, and any
statement of the form "at N=100K the tie rate will be X" that is backed by pooling is unsupported.

### 2. The relayed "54% → 26%" is most likely NOT a tie rate — it is a position statistic.

VERIFIED (SCALE_FACTS F8, F9). Across **48 definitions** tested on two independent N ladders:

- On the **pooled** ladder, **all 15 tie-flavour variants RISE**. Zero fall. That includes every
  candidate the task listed: other K (1,2,5,10,20,50,100), `gap==0`, `bc>slots`, shortlist NT=20,
  two-stage M=50, float arm, per-archive vs per-query averaging.
- The candidates the task listed are individually dead:
  - **`gap==0` ≡ `bc>slots`** — proved identical, 852,336 checks, 0 disagreements.
  - **float arm** — tie rate is **0.0000 at every N**. Cannot produce 54%.
  - **shortlist NT=20 / M=50** — bit-identical to the frozen statistic (0.234→0.345); a shortlist
    of size M≥K cannot change what happens at the K-th boundary.
  - **per-archive vs per-query averaging** — differs in the 4th decimal (0.2340 vs 0.2340 on LME).
  - **other K** — K=1 rises 0.128→0.162, K=10 rises 0.626→0.804, K=50 rises 0.928→0.972.

The statistic that **does** fall from ≈0.54 and whose mechanism story matches the relayed sentence
*word for word* is positional:

> **`P(d₍₃₎ ≥ 30)` on the pooled ladder: 0.440 / 0.440 / 0.423 / 0.379 / 0.330 / 0.204** — falls 2.2×
> over exactly the N rungs where the frozen tie rate rises 0.234 → 0.345.
>
> And within a real archive, `P(d₍₃₎ ≥ 40)`: **0.990 (N=10) → 0.000 (N=400)**.

The relayed mechanism — *"with few candidates the 3rd-nearest sits inside the concentrated mass;
with many candidates it moves into the sparse tail"* — is **a correct description of d₍₃₎'s
position** and a **false description of the tie rate**, because moving into the sparse tail does not
monotonically reduce collisions: the integer support gets thinner faster than the tail does, and
the frozen tie rate is non-monotone with a peak near N≈50.

**Exact answer to task item 4:**
- **FALLING**: `P(d₍₃₎ ≥ t)` for t≈29–30 (pooled: 0.440→0.204) or t≈40 (within-archive:
  0.990→0.000); and `bc/N` (0.056→0.003); and — over N=50..400 within a real archive — the frozen
  tie rate itself (0.355→0.245) plus 7 other tie variants.
- **RISING**: the frozen `bc>slots` tie rate on pooled archives (0.234→0.345), and every tie
  variant tested on that ladder.

I could not reproduce 0.54→0.26 exactly (best L1 error 0.155). The relayed session's exact
construction is not recoverable from here; I report the magnitude of the mismatch rather than
tuning to it.

### 3. The tie rate is NON-MONOTONE in N. Both "directions" are true on different segments.

VERIFIED (F5, pure random subsample, no gold forcing, 3 independent families):

```
N:        10     25     50    100    200    400    800   1400  | 493   24640  (pooled)
LME:     0.285  0.353  0.355  0.328  0.273  0.245    —      —   | 0.234  0.345
LoCoMo:  0.268  0.336  0.360  0.363  0.356  0.349    —      —   |
REALTALK:0.270  0.335  0.359  0.365  0.333  0.329  0.374  0.373 |
```

Peak at N≈50–100, then decline. A measurement that samples the left of the peak and a measurement
that samples the right of it will report opposite "directions" and both be correct.

---

## The fact that reframes the whole dispute

**No real archive in this programme has N > 1548.** (LME 396–616, PerLTQA 293–546, LoCoMo 369–689,
REALTALK 410–1548.) Every number either side quotes for N ≥ 2000 is about a *synthesised* archive.
Since F6 shows the synthesis method determines the sign of the effect, **the contradiction was never
resolvable by measuring harder — it was a disagreement about which fiction to extrapolate from.**
The programme has **zero** first-hand evidence about SIGN96 at its stated 100K–1M target scale.

## Impact on the frozen result's scope

VERIFIED (F10), paired on all 470 LME queries with nested pools:

**LME SIGN advantage decays monotonically with pooled N: +10.05 → +8.98 → +8.02 → +5.72 → +4.43 →
+2.67 pp** (paired t=+7.05 at the far rung, SE 1.05 pp). Sign arm falls 0.5421→0.4588; float arm is
nearly flat 0.4416→0.4320.

**Does my sample size permit a claim?** Split answer, stated plainly:

- **On pooled archives: YES, but only because of pairing.** The coordinator's n=120 unpaired deltas
  (10.0/7.0/14.3/2.6/7.6/3.6) have unpaired SE ≈3.3 pp and are genuinely uninformative — that
  spread is consistent with a constant delta. My n=470 *paired* design gives SE 0.32–1.05 pp on the
  same-query difference and a monotone t=+7.05 trend. So: the coordinator was right to distrust
  their delta numbers, and the trend is nonetheless real **on the pooled construction**.
- **On real archives: NO.** The N span within any family is ≤1.6× (except REALTALK's 3.8× with
  n=10 archives). LME r(delta, N) = −0.012 over 470 archives. No claim is licensed.

**Therefore the honest scope statement for the frozen result is:**
> The +10.04 pp LongMemEval SIGN advantage is established at N≈493. It is **not** established to
> persist at larger N, and the only available large-N evidence (pooling) shows it decaying to
> +2.67 pp at N≈24.6K. But pooling is a demonstrably wrong model of archive growth (11.8× wrong in
> the drift rate that controls the effect), so that decay is **not** a prediction for a real large
> archive either. The correct statement is that **the N-dependence of the effect is UNMEASURED**,
> and the programme cannot measure it with the archives it owns.

---

## Prediction post-mortem (PREDICTION.md was written before step 2 and is unedited)

| # | prediction | outcome |
|---|---|---|
| **P0** | `bc>slots` ≡ `gap==0` always, zero disagreements | **CORRECT.** 852,336 checks, 0 disagreements. |
| **P1** | frozen tie RISES with N and saturates; ~0.20–0.25 at N≈500 → ~0.35–0.45 at 25K | **CORRECT for pooling** (0.234→0.345, in range). **WRONG as a general statement**: I did not anticipate the non-monotone peak at N≈50 or that within-archive growth falls. |
| **P2** | pooling is NOT an artifact; (b) will agree with (a) | **WRONG — this was my central error.** (b) falls where (a) rises. My stated reason ("both change only the number of draws from a similar-shaped distribution") was exactly the false assumption: pooling changes the *shape* by adding only far mass, and that is the whole mechanism. My own hedge ("pooling could UNDER-state the rise") had the sign backwards. |
| **P3.1** | `bc>1` is the most likely home of 54%→26% | **PARTLY.** `bc≥2` does fall on the subsample ladder (0.537→0.374) and was the 3rd-best L1 fit, but the best fit and the story-matching statistic is positional `P(d₍₃₎≥t)`, which I did not anticipate. |
| **P3.2** | synthetic uniform codes could differ | **CORRECT on level, WRONG on direction.** Uniform codes hit 0.42–0.62 (the relayed ~54% level) but rise with N. |
| **P3.4** | float arm ≈ zero tie rate at every N | **CORRECT.** Exactly 0.0000 at all rungs. |
| **P3.5** | per-archive vs per-query changes <2 pp, no flip | **CORRECT.** Differs in the 4th decimal. |
| **P4** | no measurable delta trend; sample sizes forbid any claim | **WRONG, and usefully so.** I under-estimated the power of pairing. The paired design reaches t=+7.05 and shows a clean monotone decay. The claim is licensed on the pooled construction — though P4's conclusion survives for *real* archives. |
| **P5** | falsifier: "(b) falls while (a) rises ⇒ pooling IS the artifact" | **TRIGGERED.** (b) does fall. I accept the falsifier as I stated it, with the refinement that "artifact" is too strong: pooling measures a real but *different* process. |

I was wrong on my two central predictions (P2, P4) and right on the small technical ones. The
prediction file is unedited; this table is the correction record.

## Limitations — what I could not do

1. **No real archive above N=1548 exists in these caches.** The single most important limitation.
   Nothing here speaks to 100K–1M.
2. **Could not reproduce 0.54→0.26 exactly** (best L1 error 0.155 at `P(d₍₃₎≥30)` pooled). The
   relayed session's code was not available; I did not tune to the target.
3. **The coordinator's N≈1978 value (0.217) did not reproduce** (I get 0.260). Likely a different
   pooling draw at n=120. Direction and the other five rungs reproduce.
4. **F's within-archive delta ladder is confounded** by gold prevalence (gold is 1/25 of the pool at
   N=25 vs 1/493 at full), so I did not use it for any delta claim. Tie ladders are unaffected —
   they never read gold.
5. **J3 (REALTALK natural spread) is underpowered**: r=+0.417 at n=10 archives, p≈0.23, with one
   high-leverage point. It neither confirms nor refutes.
6. Subsampling itself is not a perfect model of a real archive *shrinking* either — a real small
   archive is a coherent shorter conversation, not a random row sample of a long one. This is the
   residual assumption I could not test with the data available.
