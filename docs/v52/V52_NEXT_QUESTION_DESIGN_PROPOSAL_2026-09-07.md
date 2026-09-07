# V52 — Next Research Question: Short Design Proposal

Date: 2026-09-07
Author: Continuity Lead / co-chair
Status: **`[PROPOSAL ONLY — NOT A PREREGISTRATION, NOT SEALED, NOT AUTHORIZED]`**

No seeds are drawn, no runner exists, no workflow exists, no corpus is read. Nothing here authorizes
an experiment; the Head Researcher decides separately. If taken up, this becomes the input to a
preregistration, not a substitute for one.

---

## 1. The question

> **After coordinate scales are equalised, does the spectral 32/64 split still beat a matched-size
> random split?**

## 2. Why this question

Two things are on the record and they point at each other:

- **Audited and established:** *which* coordinates form the leading block matters, not merely 32/64
  block structure. The membership gap, from the committed boundary summaries at research
  `0c9916bd`, is large and the two arms do not overlap on any seed:

  | benchmark | B32 R@3 | RANDOM32 R@3 | gap | per-seed rho, B32 | per-seed rho, RANDOM32 |
  |---|---:|---:|---:|---|---|
  | LoCoMo | 0.228403218 | 0.143917128 | **8.448609 pp** | [0.0090, 0.2072] | [0.8699, 0.9865] |
  | LongMemEval | 0.516193972 | 0.384162766 | **13.203121 pp** | [0.0658, 0.2665] | [0.8800, 1.0917] |

- **Accepted as descriptive:** relative coordinate scale accounts for much of the damage that *full*
  mixing does.

Nobody has asked whether the second explains the first. That is the cheapest remaining question that
can actually move the mechanism account, and it is the natural successor to the stage just closed.

## 3. Why this design avoids the defect that closed the last stage

The coordinate-scale stage was limited by a ratio whose denominator approached zero: the block arm
loses almost nothing, so `frac_block` divided by noise (deviation-register D4). This design has no
such division. Its primary quantity is a **difference between two arms that are far apart** — 8.4
and 13.2 percentage points, with non-overlapping per-seed ranges on both benchmarks. The
percentage-point scale, which was barred in the last stage precisely because it was floor-confounded,
is legitimate here for that reason and the preregistration must say so explicitly rather than assume
it.

## 4. Sketch of the design

**Arms** (six, mirroring the validated structure):
`NATIVE`, `SCALED_NATIVE` (bit-identity abort), `B32_FRESH`, `SCALED_B32`, `RANDOM32_FRESH`,
`SCALED_RANDOM32`.

**The essential control**, inherited unchanged from the audited boundary stage: `B32` and `RANDOM32`
must use the **identical numeric** `Q32` / `Q64` blocks and differ only in which coordinates are
assigned to them. Scaled and unscaled partners share the same rotation matrices.

**Scale rule:** the already-validated `D = diag(1/σ)` on the centered archive representation, per
archive, `ε = 1e-12`, degenerate coordinates falling back to 1. No new rule is invented.

**Primary estimand**, defined per rotation seed and then averaged over the seed panel — applying the
`A` ruling of the acceptance decision **prospectively**, so the aggregation order is fixed in the
text before anything runs:

```
G_s        = R@3(B32_FRESH, s)   − R@3(RANDOM32_FRESH, s)
G_scaled_s = R@3(SCALED_B32, s)  − R@3(SCALED_RANDOM32, s)
Δ_s        = G_scaled_s − G_s
primary    = mean over seeds of Δ_s        (per-seed values reported)
```

**Bands, and the interpretation licence attached to the primary quantity** — this fixes the §7/§9
defect prospectively, and every threshold must be frozen before the run:

- `Δ ≥ −0.20 · G` → the membership effect is essentially **scale-independent**
- `Δ ≤ −0.60 · G` → rescaling removes most of it: **scale-mediated**
- otherwise → partial

Secondary, reported with its own dispersion: the ratio `G_scaled / G`, which is safe here only
because `G` is bounded away from zero on every seed — a condition the preregistration must state as
a precondition and check at run time.

**Seeds:** a fresh panel, and fresh matched partition seeds, following the boundary stage's scheme.
Ten seeds, once, per benchmark. No replacement seeds after outcome access.

**Uncertainty, frozen in advance this time:** question-level paired bootstrap on both benchmarks;
conversation-cluster bootstrap on **LoCoMo only**; **no** cluster bootstrap on LongMemEval, citing
the single-component decision, with the inherited-not-recomputed label attached.

**Controls:** the validated set — bit-exact sign identity with a negative-diagonal rejection,
orthogonality and within-representation invariance at `1e-12` in the narrowed query-archive scope,
native reproduction against the frozen anchors, per-question records persisted for every arm and
seed, and negative controls proving each check can fail.

**Cost:** the same order as the stage just completed — one LoCoMo job and a ten-shard LongMemEval
matrix, minutes of compute, no new corpus.

## 5. Expected information gain

Both outcomes are informative, which is the point.

- **`Δ ≈ 0` — the gap survives rescaling.** Coordinate scale is **not** the channel behind the
  membership effect. Combined with the accepted descriptive finding, this would separate two
  distinct damage channels: a scale channel for full mixing, and a non-scale channel for
  membership. It would be the first result in this line to point positively at the remaining
  candidates named in the preregistration's §9 — correlation structure and subspace alignment —
  rather than merely failing to exclude them.
- **`Δ ≈ −G` — the gap collapses.** One channel plausibly accounts for both findings, and the
  audited membership result becomes downstream of scale heterogeneity across the boundary. That is
  a unification, but it also **weakens the independence** of the membership finding, which any
  future write-up would have to carry.
- **Anything between** narrows the share, on a scale that cannot be floor-confounded.

What it would **not** do in any outcome: identify the mechanism, establish necessity or exclusivity,
claim production benefit, or transfer to other encoders or corpora.

## 6. The alternative I am not proposing first, and why

The largest standing threat to this line is not "wrong mechanism" but **"an effect specific to this
one representation"**: both benchmarks share a single TF-IDF/SVD pipeline, so the cross-benchmark
agreement is not an independent methodological replication. A different-encoder replication would
test that directly and is the higher-value experiment.

It is not proposed first because it is far more expensive, needs a new frozen pipeline and new
adapters, and cannot reuse any validated control. The question in §1 costs minutes and sharpens the
mechanism account inside the existing frozen apparatus. If the Head Researcher would rather spend
the next effort on generalisation than on mechanism, the encoder-replication question is the one to
ask, and this proposal should be set aside rather than run first.

## 7. Boundary

Proposal only. No corpus read, no seed drawn, no runner or workflow written, no experiment
preregistered, sealed, authorized or run. Task 4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION /
OUTCOME ACCESS FORBIDDEN` and is untouched by this document.
