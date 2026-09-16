[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Decision tests T1–T3 — gates were fixed before running, and all three fail

Gates (referee's stopping rule, `decision_r1/cost/REFEREE.md`, written before any of this ran):
- **C1** some arm ≤48 B beats a *fairly built* BM25 by ≥ +2.0 pp FR@3, CI excluding 0, on both benchmarks
- **C3** best code+rerank beats BM25-alone by ≥ +1.0 pp FR@3, CI excluding 0
- **S3** PerLTQA corrected for k<n is still flat-or-falling on *unstandardized* arms ⇒ real capacity law

Artifacts: `coordinator/decision_tests.py` → `DECISION_TESTS.json`;
`ablation_r2/perltqa/t3_ladder.py` → `T3_PERLTQA_KLTN.json`. Runtime 14 s + 36 s.

---

## T1 — Fair baseline. **C1 FAILS, and the gap is far larger than we reported.**

Four BM25 variants on RealTalk, all scored with our own deterministic tie-break:

| BM25 variant | Hit@10 | FR@3 |
|---|---:|---:|
| coarse tokenizer, textbook k1/b (**what we always quoted**) | 55.32 | 33.91 |
| frozen tokenizer, textbook k1/b | 61.70 | 36.05 |
| coarse tokenizer, IDF-only (k1→0, b=0) | 57.30 | 34.05 |
| **frozen tokenizer, IDF-only** | **65.67** | **40.02** |

Against the strongest honest BM25 (65.67):

| code | Hit@10 | vs BM25 | FR@3 | vs BM25 |
|---|---:|---:|---:|---:|
| 12 B qscale | 49.65 | **−16.03** | 22.41 | −17.61 |
| 24 B qscale | 55.32 | −10.35 | 29.75 | −10.27 |
| 48 B qscale | 57.87 | **−7.80** | 32.79 | −7.23 |

The tokenizer+parameter choice is worth **+10.35 pp** to BM25 — larger than our entire
12→48 byte ladder gain (+8.22 pp). Every historical "we beat BM25" line in this programme
compared a tuned code against an untuned opponent. Quadrupling the byte budget does not
close even half the honest gap.

## T2 — Rerank dissolution. **C3 FAILS on the arm we care about.**

Computed from 164,256 stored paired per-query rows in the incoming package; paired
archive-clustered bootstrap, 20000 reps, seed 20260916.

Our code + BM25 rerank, versus plain BM25 alone:

| benchmark | qscale96+rerank − BM25 alone | verdict |
|---|---|---|
| LME | −0.33 pp [−1.38, +0.62] | ns — **FAIL** |
| PerLTQA | +0.33 pp [−0.02, +0.67] | ns — **FAIL** |
| LoCoMo | +1.07 pp [+0.44, +1.72] | SIG — PASS (disputed gold) |

One pass of three, on the benchmark whose gold is under dispute.

**The stronger finding is the rank inversion.** First-stage FR@3 before → after reranking:

| LME first stage | before | after |
|---|---:|---:|
| float_std32 | 55.74 | 58.05 |
| qscale96 | 54.27 | 57.70 |
| **hamming96** | **53.86** | **58.23** ← worst-but-one before, best after |
| asym96 | 50.65 | 57.65 |
| **float_raw32** | **44.16** | **57.76** ← worst before, second-best after |

`float_raw32` starts **11.58 pp behind** the leader and finishes **0.29 pp ahead** of our
flagship. Order inversions: LME 4/10 pairs, LoCoMo 3/10, PerLTQA 6/10. Post-rerank spread
on LME is 0.58 pp across first stages that span 11.58 pp before reranking.

Once a text reranker is in the pipeline, first-stage quality is very nearly irrelevant.
Optimizing a compact first-stage code optimizes a quantity the reranker overwrites.

## T3 — PerLTQA with k<n. **My rank-overflow explanation was WRONG.**

Fidelity gate: **0 differing bits of 276,480** against cached production C.

Enforcing k_eff = min(k, n−1) on the 8 archives with n<384 (2,217 queries), the surplus
dimensions are gone — `constant_dims@384 = 0` in every one of the 8 archives. The decline
should therefore have disappeared. It did not:

| arm | 96 | 192 | 384 | 192→384 FR@3 |
|---|---:|---:|---:|---:|
| qscale (standardized) | 56.38 | 57.71 | 54.11 | **−3.60** |
| sym (standardized) | 51.69 | 53.88 | 48.71 | **−5.17** |
| asym (**un**standardized) | 57.09 | 60.79 | 61.09 | **+0.30** |

So the decline is **not** rank overflow. It is real, and it is specific to dividing by σ:
with k_eff ≈ n−1 the trailing directions are genuine but nearly singular, their σ is tiny
but nonzero, and dividing by it amplifies noise that `asym` never touches.

**This retracts my own explanation from `LADDER_REALTALK.md`.** The observation that
survives is the one the literature worker actually made — the decline is *scorer*-dependent,
not dimension-dependent. The cause I attached to it was wrong, and constant-dimension
counting disproves it directly.

Note the practical consequence: the best PerLTQA arm here is `asym` at 384 dims (61.09 FR@3),
which beats every standardized arm at every width. **We have been scoring with the wrong
readout at high k.**

## Readout against the prespecified gates

| gate | result |
|---|---|
| C1 (beat fair BM25 by ≥2 pp, both benchmarks) | **FAIL** — behind by 7.80 pp at 48 B on RealTalk |
| C3 (code+rerank beats BM25 alone by ≥1 pp) | **FAIL** — 1 of 3, on disputed-gold LoCoMo |
| S3 (decline persists on unstandardized arms) | **does not fire** — `asym` rises (+0.30) |

C1 and C3 both fail. Under the rule as written, the verdict is **STOP the retrieval-
optimization programme**.

## What the tests changed that is worth keeping

1. **A fourth retraction, this one mine and caught by my own test**: rank overflow does not
   explain the PerLTQA decline. Constant dims are zero under k<n and the decline persists.
2. **`asym` beats every standardized arm at 384 dims on PerLTQA.** If any work continues, the
   scorer is the lever, not the bit count — and this was visible in the incoming package's
   own table before we ran anything.
3. **The honest BM25 is 65.67, not 55.32.** Every comparison table in this programme's history
   needs the −10.35 pp correction applied before it is quoted again.
