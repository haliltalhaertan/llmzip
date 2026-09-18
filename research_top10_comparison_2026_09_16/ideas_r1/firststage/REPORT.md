# First-stage pool comparison for a reranking architecture (RealTalk)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

RealTalk only, n=705 valid queries, 10 archives. Never averaged across benchmarks.
Reproduce: `$HOME/muse-work/ml-python firststage.py` (this dir). Per-query replay data:
`per_query.jsonl` (705 rows; CODE/BM25/RRF top-500 id lists, UNION pools per M, all
pool metrics). Aggregates: `RESULTS.json`.

## Direct answer

**On quality, the best first stage is the fusion (RRF, k=60 fixed pre-run) — not CODE
alone and not BM25 alone. On bytes, the order reverses: CODE is ~13x smaller than the
BM25 index alone and ~21x smaller than an honest BM25 deployment (index + the raw
text BM25 requires). Both facts side by side:**

| first stage (RealTalk, n=705) | pool Hit@100 | ceiling FR@3@100 | own Hit@10 | storage (bytes) |
|---|---|---|---|---|
| CODE (12-byte qscale) | 75.60% | 61.30% | 49.65% | **115,008** (107,328 packed + 7,680 sigma) |
| BM25 | 78.16% | 62.26% | 54.18% | **1,450,229** index + 998,654 raw text = **2,448,883** |
| RRF fusion (k=60) | **81.28%** | **66.15%** | **55.74%** | both: **2,563,891** |

RRF beats BM25 on pool Hit@100 by +3.12 pp (95% CI [+1.23, +4.92], W/L 33/11) and on
ceiling-FR@3 by +3.89 pp ([+2.44, +5.47]); it beats CODE by +5.67 pp
([+3.23, +8.20]) and +4.85 pp ([+2.96, +6.70]). CIs are paired archive-clustered
bootstrap, 20000 reps, seed 20260916, 10 clusters — wide and exploratory, but the
RRF contrasts exclude zero while BM25-minus-CODE covers zero (Hit@100 +2.55 pp,
[-1.17, +6.69]; ceiling +0.95 pp, [-2.37, +4.07]). So: **the uncomfortable fact
stands (BM25 > CODE), but fusion > BM25, at the cost of keeping both** (plus raw
text for any reranker that re-reads it anyway — see below).

Practical note: a reranking architecture re-reads the ORIGINAL TEXT of candidates
by definition, so the raw text (~1.0 MB) is kept regardless. The *incremental*
retrieval cost of fusion over a rerank pipeline is therefore BM25's index
(~1.45 MB) on top of CODE's 115 KB — not the full 2.45 MB. If even that is too
much, CODE alone is the budget pick, but its ceiling is then 61.30% FR@3 at M=100
vs 66.15% for fusion, and 172/705 queries have NO gold in CODE's top-100 at all
(pool Hit 75.60%; oracle-union still misses 105 — fusion leaves less on the table).

## Primary: pool quality at M = 10..500 (%, n=705)

POOL HIT@M = gold in pool. POOL RECALL@M = |gold ∩ pool|/|gold| (multi-gold is
common here: only 319/705 queries are single-gold; max gold size 22).
CEILING-FR@3@M = min(3, |gold ∩ pool|)/|gold| — the maximum FR@3 any reranker over
that pool could reach (oracle bound; real rerankers land far below).

| M | arm | pool Hit | pool recall | ceiling FR@3 |
|---|---|---|---|---|
| 10 | CODE | 49.65 | 37.00 | 36.95 |
| 10 | BM25 | 54.18 | 43.16 | 43.16 |
| 10 | RRF | 55.74 | 42.80 | 42.80 |
| 10 | UNION (pool only) | 54.61 | 42.17 | 42.17 |
| 20 | CODE | 58.16 | 44.46 | 44.29 |
| 20 | BM25 | 64.40 | 50.63 | 50.44 |
| 20 | RRF | 62.13 | 49.28 | 49.01 |
| 20 | UNION (pool only) | 61.70 | 48.30 | 48.23 |
| 50 | CODE | 67.38 | 54.38 | 53.70 |
| 50 | BM25 | 72.20 | 57.60 | 57.05 |
| 50 | RRF | 72.77 | 59.40 | 58.64 |
| 50 | UNION (pool only) | 72.62 | 58.26 | 57.69 |
| 100 | CODE | 75.60 | 62.37 | 61.30 |
| 100 | BM25 | 78.16 | 63.04 | 62.26 |
| 100 | RRF | 81.28 | 67.39 | 66.15 |
| 100 | UNION (pool only) | 78.72 | 64.72 | 63.65 |
| 200 | CODE | 85.25 | 72.40 | 70.45 |
| 200 | BM25 | 86.10 | 71.39 | 69.79 |
| 200 | RRF | 88.09 | 75.00 | 73.01 |
| 200 | UNION (pool only) | 85.11 | 71.81 | 70.24 |
| 500 | CODE | 95.18 | 87.95 | 83.84 |
| 500 | BM25 | 96.03 | 87.50 | 83.56 |
| 500 | RRF | 97.16 | 89.79 | 85.61 |
| 500 | UNION (pool only) | 94.61 | 84.58 | 81.07 |

Own achieved, no reranker (for reference): CODE Hit@10 49.65 / FR@3 22.41; BM25
54.18 / 33.07; RRF 55.74 / 31.45. (UNION is a pool, not a ranking: no own ranking
metrics.) Note RRF leads Hit@10 but BM25 leads FR@3 — top-3 density still favors
lexical; the reranker's job is exactly to fix that.

## Secondary: complementarity (the decision input)

Per-query pool-Hit 2x2, CODE vs BM25 (counts, n=705):

| M | both find | CODE-only | BM25-only | neither | ORACLE-UNION Hit (gold-using bound, NOT deployable) |
|---|---|---|---|---|---|
| 10 | 297 | 53 | 85 | 270 | 61.70% |
| 20 | 368 | 42 | 86 | 209 | 70.35% |
| 50 | 429 | 46 | 80 | 150 | 78.72% |
| 100 | 484 | 49 | 67 | 105 | 85.11% |
| 200 | 552 | 49 | 55 | 49 | 93.05% |
| 500 | 653 | 18 | 24 | 10 | 98.58% |

CODE finds gold BM25 misses on 49 queries at M=100 (and vice versa 67): the arms
are genuinely complementary, which is why fusion gains. RRF@100 (81.28%) captures
most but not all of the oracle bound (85.11%). UNION (top-50+top-50 deduped,
78.72%) underperforms RRF@100 because each arm contributes only half a list —
a fixed-budget pool halves both orderings instead of re-ranking them.

## Cost accounting (mandatory)

- CODE: 8944 docs x 12 B = 107,328 B + per-archive sigma (10 x 96 float64 =
  7,680 B) = **115,008 B total**. Needs no raw text.
- BM25: ACTUAL serialized inverted index per archive (pickle.dumps with
  HIGHEST_PROTOCOL of {N, postings {term: {row: tf}}, idf, doc_lens, avglen}):
  RT01 140,402; RT02 143,725; RT03 136,323; RT04 133,730; RT05 140,177;
  RT06 151,742; RT07 160,580; RT08 134,946; RT09 148,980; RT10 159,624;
  **total 1,450,229 B** — measured, not estimated. BM25 ALSO needs the raw text
  kept: 998,654 B UTF-8 (all 8944 docs). Honest BM25 deployment total: 2,448,883 B.
- Query time (wall, single-threaded, same machine, n=705) — **values below corrected
  2026-09-18 to match `RESULTS.json`; the previously published figures were 28–40% low
  and had no generating code (see correction note)**: CODE score+full-rank
  mean 1.37 ms / p95 2.59 ms; BM25 index-traversal score+full-rank mean 1.70 ms /
  p95 3.20 ms; RRF fusion+rank marginal mean 1.33 ms / p95 2.45 ms (honest
  end-to-end RRF ~= CODE+BM25+fusion); UNION dedupe marginal
  mean 0.103 ms / p95 0.155 ms given base rankings. Index build one-off 0.095 s.
  (This Python BM25 traversal is conservative; a production engine is faster —
  which only strengthens fusion's case on latency.)

  > **CORRECTION 2026-09-18.** The figures published here until today (CODE 0.99/1.90,
  > BM25 1.22/2.30, RRF 0.96/1.78, UNION 0.08/0.11, build 0.04 s) disagreed with this
  > line's own source of truth, `RESULTS.json` `timings.*`, by 28–40%. No script in the
  > package produces the old numbers; their provenance is unknown. The values above are
  > read directly from `RESULTS.json`. The **quality** results in this report were
  > independently recomputed from `per_query.jsonl` and match to 1.4e-14 — only the
  > latency table was wrong.

## Contrasts (paired archive-clustered bootstrap, 20000 reps, seed 20260916)

10 clusters -> wide CIs, exploratory only.

| contrast | metric @M=100 | point (pp) | 95% CI | W / L / = |
|---|---|---|---|---|
| BM25-CODE | pool Hit | +2.55 | [-1.17, +6.69] | 67 / 49 / 589 |
| BM25-CODE | ceiling FR@3 | +0.95 | [-2.37, +4.07] | 95 / 101 / 509 |
| RRF-CODE | pool Hit | +5.67 | [+3.23, +8.20] | 57 / 17 / 631 |
| RRF-CODE | ceiling FR@3 | +4.85 | [+2.96, +6.70] | 83 / 37 / 585 |
| RRF-BM25 | pool Hit | +3.12 | [+1.23, +4.92] | 33 / 11 / 661 |
| RRF-BM25 | ceiling FR@3 | +3.89 | [+2.44, +5.47] | 78 / 30 / 597 |
| UNION-RRF (pool, info only) | pool Hit | -2.55 | [-3.67, -1.44] | 2 / 20 / 683 |

BM25-vs-CODE at M=100 is NOT decisive (CI covers zero); RRF-vs-either excludes
zero on both metrics despite only 10 clusters.

## Evidence discipline / gate record

- Exclusions (23) decided BEFORE scores: empty gold_rows only; skipped qids match
  `data/exclusions.json` exactly (symdiff 0, gate G2). n=705, 10 archives (G1).
- G3/G4/G5 PASS: CODE Hit@10 49.6454 (anchor 49.6454), CODE FR@3 22.4099 (anchor
  22.41), BM25 Hit@10 54.1844 (anchor 54.1844).
- G7/G8 PASS: CODE/BM25 pool-Hit@100 and ceiling-FR@3@100 reproduce the
  coordinator's independent ceiling values to <0.01 pp.
- **G6 FAIL (recorded, not hidden): BM25 top10 ids match
  `audit/per_query_bm25_corrected.jsonl` on 704/705.** Sole mismatch RT01_q016
  rank 10: a TRUE 3-way score tie (rows 249/596/605 ~= 5.501322839570598, tie-hash
  order 605<249<596, neither candidate gold) resolved differently by 1-ulp float
  summation order (sorted-term vs the reference's `for t in set(q_tok)`).
  Proven: the reference convention itself is PYTHONHASHSEED-dependent (same
  formula yields {249,605} under seeds 0/1 vs {605,249} under seed 42), so
  bit-exact agreement with that file is ill-defined on ties. Primary uses
  deterministic sorted-term order (seed-independent). Sensitivity: alternative
  deterministic order (reverse-sorted) through the FULL pipeline (BM25 pools, RRF
  re-fusion, UNION re-pooling) moves max 0.0000 pp over 58 reported aggregates —
  zero metric impact. The gate stays FAIL in RESULTS.json; it was NOT redefined.
- Index-traversal BM25 scoring agrees with the naive doc-outer loop on 705/705
  top-500 and top-10 id lists. No queries/archives dropped for scores.
- RRF k=60 fixed before running (standard default), never tuned. ORACLE-UNION is
  a gold-using bound, NOT a deployable method. Ceilings assume an oracle
  reranker; real rerankers land far below. Exploratory pilot, not preregistered.

## Recommendation

Feed the reranker with **RRF fusion of CODE + BM25** (k=60): highest pool at
every M >= 50, highest ceiling (66.15% FR@3 @100 vs 62.26 BM25 / 61.30 CODE),
decisive contrasts, ~3.2 ms/query in this Python harness. Price: keep both
structures (~2.56 MB total; incremental ~1.45 MB over a pipeline that already
stores text for reranking). If storage is capped at ~115 KB, CODE alone is the
honest budget pick — but say so alongside its lower ceiling, not instead of it.
