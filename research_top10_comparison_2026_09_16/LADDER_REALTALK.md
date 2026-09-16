[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# The RealTalk byte ladder — and why PerLTQA's decline was an artifact

`coordinator/ladder.py` → `coordinator/LADDER.json`. Fidelity gate: **0 differing bits of
858,624**. Anchors exact: k96 qscale Hit@10 49.6454 (frozen 49.6454, dev −0.0000);
k96 sym 46.5248 (dev +0.0000); k96 qscale FR@3 22.4099 (frozen 22.41).

## The ladder rises monotonically on RealTalk

| bytes/doc | dims | qscale Hit@10 | Δ | sym Hit@10 | qscale FR@3 |
|---:|---:|---:|---:|---:|---:|
| 12 | 96 | 49.65 | — | 46.52 | 22.41 |
| 24 | 192 | 55.32 | **+5.67** | 51.77 | 29.75 |
| 48 | 384 | **57.87** | **+2.55** | 54.18 | 32.79 |

No decline at 48 B. This directly contradicts the incoming package's PerLTQA result
(52.98 → 54.82 → 51.87, the 192→384 drop significant at CI [−3.87, −2.01]).

## Why the two disagree: rank overflow, not a bit-budget limit

A literature worker noticed the decline is **scorer-dependent**, and the coordinator
verified it on their raw `QUALITY_LEVELS.csv`. PerLTQA FR@3, 96 → 192 → 384:

| arm | standardized? | 96 | 192 | 384 | shape |
|---|---|---:|---:|---:|---|
| qscale | yes | 52.98 | 54.82 | 51.87 | peak, then fall |
| hamming | yes | 49.01 | 50.68 | 47.74 | peak, then fall |
| float_std | yes | 56.24 | 57.78 | 54.49 | peak, then fall |
| **asym** | **no** | 53.71 | 57.30 | **58.03** | **monotone rise** |
| **float_raw** | **no** | 55.03 | 58.55 | **60.43** | **monotone rise** |

Same subspaces, same documents, same dimensions — only the readout differs. Every
standardized arm falls; neither unstandardized arm does. "More dimensions is harmful"
cannot explain that.

**The cause.** PerLTQA archives are small: median 407 documents, minimum 293, and
**8 of 30 archives hold fewer than 384 documents**. A rank-384 decomposition of a
293-document archive cannot produce 384 informative directions; the surplus dimensions
are constant-filled (the ladder audit records effective ranks of 293–381 while still
charging the full 48 bytes, covering 2,217 queries = 26.8% of PerLTQA).

A constant dimension has standard deviation ≈ 0. `qscale` divides by that σ (floored at
1e-12), so the surplus dimensions inject enormous noise. `asym` and `float_raw` never
divide, so they are immune. That is the entire pattern.

RealTalk archives hold 410–1548 documents, so k < n holds at every rung — and the ladder
rises. LoCoMo archives are large too, and its ladder also rises (35.11 → 41.21 → 44.15).

**Consequence.** "Bits beyond 24 B do not help" was measured under a defect, not a law.
The honest rule is **k < n per archive**, and a fixed global k is the wrong design for a
corpus of heterogeneous archive sizes. Any future ladder must set k = min(k_target, n−1)
and report effective rank per archive.

## Two results that hold regardless

**BM25 was handicapped here too, by more than the external audit found.** Giving BM25 the
frozen word-channel tokenization (stopwords removed, `\b\w\w+\b`) is worth **+6.38 pp**
Hit@10 on RealTalk (55.32 → 61.70), against the ~3 pp the audit measured on PerLTQA and
LoCoMo. At 48 B our code beats the coarse-tokenizer BM25 by +2.55 pp but **loses to the
fairly-tokenized BM25 by −3.83 pp**. Quoting the coarse baseline flatters us.

**The channel mix costs more than the projection.** With no projection at all:
word-only 56.03 vs full Z 47.80 — the char and LSA channels together cost **8.23 pp** on
RealTalk. This independently reproduces the external auditor's LoCoMo finding (char channel
−12.25 pp in the rare bucket) on a benchmark they could not run. Our feature mix, not only
our compression, is losing points.

## Method note — a failure worth recording

The first run of this script died at the 3000 s timeout having written **nothing**: results
were held in memory until the end, and `k=768` on RT06 (1548 docs) alone took 27 minutes.
This is the second time the same design fault cost a run in this programme (the LME
ablation worker did it first). The rerun caches each archive to `LADDER_CACHE.jsonl` as it
completes and dropped `k=768` — with the reason recorded in the script rather than the grid
being changed silently. Total runtime after the fix: **124 s**.
