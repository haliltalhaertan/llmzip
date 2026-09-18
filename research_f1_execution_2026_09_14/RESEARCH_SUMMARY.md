[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Three parallel research sessions, 2026-09-14

All three reproduced a frozen headline as a control before trusting any new number, froze a written
prediction before the test that could kill it, and reported their own errors. All three killed
their own primary hypothesis.

## 1. Scale contradiction: RESOLVED — both measurements were right

The relayed claim (tie rate falls with N) and the coordinator's measurement (tie rate rises) do
not contradict each other; they measure different processes.

| growth mode | N span | K=3 tie rate | 3rd-distance drift |
|---|---|---|---|
| pooling unrelated archives | 493 -> 24640 | 0.234 -> 0.345 RISES | -0.244 bits/doubling |
| subsampling one real archive | 50 -> 400 | 0.355 -> 0.245 FALLS | -2.869 bits/doubling |

An 11.8x drift difference is the whole mechanism: related rows push the 3rd-nearest distance into
the sparse tail, unrelated rows only add far mass and pile onto the same integer distance. The tie
rate is **non-monotone**, peaking near N=50, confirmed in LME, LoCoMo and REALTALK.

The relayed "54% -> 26%" is **not a tie rate** under any of 48 tested definitions (all 15
tie-flavour variants rise on the pooled ladder; `gap==0` is identical to `bc>slots` in 852,336
checks with 0 disagreements; the float arm's tie rate is exactly 0 at every N; NT=20 and M=50
shortlists are bit-identical to frozen). The statistic that DOES fall, and matches the relayed
mechanism sentence verbatim, is positional: `P(3rd distance >= 30)` = 0.440 / 0.440 / 0.423 /
0.379 / 0.330 / 0.204. The relayed reasoning was right about where the boundary sits and wrong
about what that does to ties.

**The finding that reframes everything:** no real archive in this programme exceeds **N=1548**
(LME 396-616, PerLTQA 293-546, LoCoMo 369-689, REALTALK 410-1548). Every N>=2000 number on either
side of the dispute describes a SYNTHESISED archive, and the synthesis method determines the sign
of the trend. **N-dependence is UNMEASURED and unmeasurable with the archives owned.** Paired over
all 470 LME queries the pooled delta does decline (+10.05 -> +2.67 pp, t=+7.05) but that is
licensed for the pooled construction only; across real archives r(delta, N) = -0.012.

## 2. Role separation: REFUTED as a mechanism

Mapping proven four ways before any claim (count match 470/470; gold-index match across 886 rows;
row-permutation control drives adjacency 31.98 -> 47.91 bits and AUC 0.914 -> 0.507; role-shuffle
drives asymmetry 6.90 -> 0.045 bits).

Relayed numbers were overstated but directionally real (Hamming 31.98 vs 47.96, AUC 0.9088,
cosine 0.705 vs -0.0023). "Near-copy is false" CONFIRMED exactly (0.1369% of pairs, 83.56%
non-adjacent). Role asymmetry is **6.90 bits, not ~1**. No role filter CONFIRMED at
`adapters/longmemeval_v52_adapter.py:80-103` (114,902 user / 116,704 assistant rows indexed).

Three independent kills:
1. Adjacent pairs reach the <=16-bit tail at 6.15%, same-session non-adjacent at 6.12% — adjacency
   confers no near-duplicate status.
2. **Lag-2 pairs (SAME speaker) are closer (25.48 bits) than lag-1 cross-speaker pairs (31.98)** —
   speaker pairing is not what creates proximity; role alternation interleaves dissimilar rows.
3. Cross-benchmark sign is backwards: LongMemEval has the densest gold neighbourhoods (median 18
   bits) and sign WINS +10.05 pp; PerLTQA is sparse (27 bits) and sign LOSES -6.27 pp.

One positive result, correctly named: LME shows a real -11.15 pp close-vs-far effect
[-17.79, -4.12], but adjacency contributes a null -1.67 pp [-10.24, +6.70] and a **cosine**
neighbour predictor reproduces -8.23 pp of it. So it is generic gold-neighbourhood density in the
float geometry, not sign-specific speaker duplication. Bonus: gold-gold adjacency is 9.10x
enriched in LoCoMo.

## 3. PerLTQA levels: both surviving pictures dead, plus a sixth

Gates passed first: PerLTQA float FR@3 exact (`0.551692074528853`), Delta -6.274727836521104 pp,
all four sections matching to 6 dp; and the per-gold rows reproduce the **independent R2 audit's**
published Spearman targets to <=1.2e-4 on 4/4 sections plus overall — an external surface that
could not have been tuned to.

Levels on PerLTQA: profile, the only SIGN winner (+20.355 pp), is the only section with a
**positive** STRICT_GAP (+4.733) and TIE_GAP (+3.207); events -21.880, social -25.109, dialogues
-74.826. Medians, fraction>0 and within-archive pairing (25/30) all agree. That kills the picture
requiring a negative gap at the winner.

Then the out-of-sample kill: **LongMemEval gap -19.17 with Delta +10.05 pp; PerLTQA gap -38.70
with Delta -6.27 pp — same gap sign, opposite Delta sign.** LoCoMo agrees with LME (-5.78, +6.66).
The stratum rule scored 11/24 = 45.8% against a 79.2% majority baseline. The session's own frozen
rule R (ALIGN) failed the whole-benchmark sign on 3/3 out-of-sample benchmarks — it predicted
negative Delta for 25 of 30 deciles and **zero** are negative. Not rescaled, not rescued.

**What survived:** `rho(Delta, strict_BOT64)` = -0.185 / -0.179 / -0.195 / -0.308 across four
benchmarks — the tightest cross-benchmark statistic the programme has. **The slope is stable; the
level is not.** Method note: `mean_i(C_ij^2)` and variance are identical here (ordering 30/30, max
diff 2.08e-17) because C is pre-centered.

Recommended next step, from that session: stop writing correlational per-query rules — six have
now died the same way — and instead **intervene on the representation with archives fixed**: an
axis-budget sweep m in {8..96} looking for a per-benchmark crossover (the frozen caches already
carry k=48/64/80 arms, so this is nearly free), and score `sign(C) * ||C_i||` to test whether the
per-benchmark offset is document-norm informativeness.

## Disclosed self-corrections

- Scale session: both central predictions wrong (P2 pooling-not-an-artifact, P4 no-delta-claim);
  could not reproduce the coordinator's N~1978 rung (0.217 vs 0.260), other five reproduce.
- Role session: two own-code bugs found and disclosed (inverted AUC tail 0.093 -> 0.909; a
  permutation control that masked on permuted labels but indexed original rows, fake 33.71-bit
  control vs true 47.91).
- Levels session: LoCoMo float headline off by 0.173 pp from the frozen candidate, attributed to
  `raw_evidence` gold resolution; reported, not tuned, affects no sign.

## Standing limits

Not the preregistered Task4F1 experiment. Exploratory probes on unsealed E1 caches. All sessions
are the same model family as the coordinator and were commissioned by him — partial independence
only. No mechanism is established; the count of dead candidate explanations is now **eight**.
