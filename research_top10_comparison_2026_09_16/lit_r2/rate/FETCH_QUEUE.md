[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# FETCH QUEUE — rate cluster (bits vs retrieval quality)

Ranked by DECISION-RELEVANCE (what the coordinator's web access should settle first because
it changes what we run next), not by interest. Every source below is UNVERIFIED from disk
— all bibliographic details are [RECALLED-FROM-MEMORY] with confidence; the coordinator
verifies existence, title, authors, venue, year before any citation. Do NOT re-fetch anything
in `inventory/literature/DO_NOT_RESCAN.md` (BPR, Extended RaBitQ, MUVERA, PPLX, Nemotron,
Qwen3, Anthropic, BGE-M3, ConvMemory v2, MuSiQue panel, PQ/RaBitQ-original snippets beyond
what is ranked here). Round-1 verified facts (ITQ scope, ABTT arXiv:1702.01417, RRF SIGIR
2009, Husbands 2005) are taken as given not re-ranked. [MEASURED HERE — brief + inventory.]

Decisions at stake: (D1) stop the ladder at 24 B vs run a 4th rung / fix readout and continue;
(D2) which on-disk test runs next (cap-excluded re-aggregation, variance-weighted rescore,
per-archive k/n plot, nested-vs-refit); (D3) whether to quote any k(n) rule in planning;
(D4) whether Q1's "no bound" can be stated as a searched null vs a bare recall.

---

## F1. Deerwester et al. LSI original + Dumais LSI dimensionality experiments (optimum location, n, metric, SIG?)

- Search terms: `Deerwester Dumais Landauer Furnas Harshman 1990 latent semantic indexing
  JASIS`; `Dumais latent semantic indexing dimensionality dimensions optimum retrieval`.
- Likely source: [RECALLED-FROM-MEMORY: medium] Deerwester et al. 1990 J. Am. Soc. Inf. Sci.;
  Dumais follow-ups (1991-1995, Bellcore/Luce reports and SIGIR-adjacent). Verify each from
  the fetch, not from this line.
- Settles: Q2 candidate (i) — the only KNOWN-shape claim in the report. Record per plot:
  collection name + n, k grid, metric, peak k, post-peak fall SIG or plateau, float only.
- Changes: D1/D2 — a small-n optimum near k ~ 200 normalises stopping at 24 B; an optimum
  that never significantly declines sends us to the amplifier tests (weighted rescore) first.

## F2. Early small-collection LSI table: MED/CRAN/CACM/CISI/TREC-small sizes paired with reported k

- Search terms: `MEDLINE MED Cranfield CACM CISI collection documents number LSI dimensions`;
  `Landauer Foltz Laham introduction to latent semantic analysis k dimensions collection size`.
- Likely source: [RECALLED-FROM-MEMORY: medium-low] Landauer et al. "Introduction to LSI"
  review chapter; collection README counts (SMART distribution). Verify counts at source.
- Settles: Q4's era split + Q3's denominator — one table of (collection, n, reported k,
  metric) is the comparison RATE_MAP §Q3.2 needs (does any primary land at k/n ~ 0.2-0.5?).
- Changes: D3 — decides whether "fixed low-hundreds k" can be quoted as verified practice
  vs remains our post-hoc match; kills or keeps any sqrt(n)/n/c talk in planning.

## F3. Hughes 1968 peaking + Raudys & Jain 1991 small-sample survey (is k/n the governing ratio?)

- Search terms: `Hughes 1968 "mean accuracy of statistical pattern recognizers" peaking`;
  `Raudys Jain 1991 small sample size effects classification survey`.
- Likely source: [RECALLED-FROM-MEMORY: medium] Hughes, IEEE Trans. Inf. Theory 1968;
  Raudys & Jain, IEEE Trans. Pattern Anal. Mach. Intell. 1991. Verify scope (trained
  classifiers, NOT unsupervised spectral retrieval) before quoting.
- Settles: Q2 candidate (ii) — whether k/n framing has ANY primary behind it, and its
  boundary conditions (what breaks when the setting is unsupervised + sign-coded).
- Changes: D2 — a positive scope match promotes the per-archive k/n-delta plot to the next
  run; a clean mismatch (classifier-only) retires the Hughes analogy from the report.

## F4. Beyer et al. 1999 NN-meaningfulness + Radovanovic et al. hubness (rule concentration in/out)

- Search terms: `Beyer Goldstein Ramakrishnan Shaft 1999 "when is nearest neighbor
  meaningful"`; `Radovanovic Nanopoulos Ivanovic hubness high dimensional data nearest
  neighbors`.
- Likely source: [RECALLED-FROM-MEMORY: medium-low] Beyer et al., ICDT 1999; Radovanovic et
  al., SIAM Int. Conf. Data Mining ~2009-2010 + journal extension. Verify theorems assume
  i.i.d./L_p settings, not orthonormal SVD projections.
- Settles: Q2 candidate (iv) — the weakest hypothesis; wanted as a RULE-OUT so experiment
  design stops hedging on it.
- Changes: D2 — only if hub diagnostics (relative contrast, k-occurrence skew vs
  per-archive delta) are worth any CPU at all; expected answer is no.

## F5. Jegou et al. product quantization primary + Ge et al. OPQ (gold-vs-ANN curve shapes)

- Search terms: `Jegou Douze Schmid 2011 "product quantization for nearest neighbor
  search" recall bytes`; `Ge He Ke Sun 2013 "optimized product quantization"`.
- Likely source: [RECALLED-FROM-MEMORY: medium] Jegou et al., IEEE Trans. Pattern Anal.
  Mach. Intell. 2011; Ge et al., CVPR 2013. Full texts justified here (DO_NOT_RESCAN holds
  only a PQ snippet [MEASURED HERE — inventory §A], and the question is the CURVE SHAPE,
  not the method).
- Settles: Q1.5 — exhibit one ANN-recall-vs-bytes curve (expected monotone-saturating)
  against our gold-recall downturn; checks whether any PQ ablation plots width-vs-bits at
  fixed budget (cf. our IKI 96x2-vs-192x1 negative [MEASURED HERE — b_ideas audit Pkg 3]).
- Changes: D1 — reframes "more bytes must help" expectations in planning; no new run unless
  a width-vs-precision ablation is found that contradicts IKI-A.

## F6. ScaNN anisotropic quantization (reconstruction-vs-retrieval precedent, exact loss + scope)

- Search terms: `Guo Zhao et al. 2020 "accelerating large-scale inference with anisotropic
  vector quantization" ScaNN`.
- Likely source: [RECALLED-FROM-MEMORY: medium on thesis, low on details] Guo et al., ICML
  2020. Round-1 starter S3, never fetched; verify loss form, anisotropy handling, datasets,
  and that scope is dense embeddings (not TF-IDF/SVD sign codes).
- Settles: Q1.3's only "retrieval beats reconstruction at equal bitrate" precedent cited in
  RATE_MAP — principle support for the equal-vote amplifier story, not a quantitative cover.
- Changes: D2 — if the loss has a sign-code-compatible form, it becomes a candidate weighted
  readout; if dense-only, it stays a cited principle and nothing runs.

## F7. Targeted null-or-theorem search: bits -> gold-Recall@K bound (flip Q1 either way)

- Search terms: `rate distortion retrieval recall bound bits per document`;
  `hashing lower bound recall top-K bits information theoretic`;
  `"bits" "recall@k" binary codes gold retrieval bound`; `Fano retrieval binary code error bound`.
- Likely source: none recalled — that is the point [RECALLED-FROM-MEMORY: medium on the
  negative]. Success = a real theorem with a stated RETRIEVAL loss (not reconstruction, not
  ANN-approximation); equally valuable failure = a RECORDED search (databases, queries, hits,
  why each near-miss misses) that upgrades Q1 OPEN to "searched null".
- Settles: Q1 verdict status and D4 wording permission.
- Changes: D4 only — no experiment runs on any outcome; a live theorem would redirect theory
  effort, a null locks the honest "no plug-and-play bound" line.

## F8. Weiss et al. Spectral Hashing (balance/variance assumption behind ITQ-family thinking)

- Search terms: `Weiss Torralba Fergus 2008 "spectral hashing" NIPS balanced variance`.
- Likely source: [RECALLED-FROM-MEMORY: medium-low] Weiss et al., NeurIPS 2008. Verify the
  balance/variance design goals from the primary (round 1 recalls them as goals without a
  demonstrated balance-vs-retrieval tradeoff [MEASURED HERE — LITERATURE_MAP §Q1(c)]).
- Settles: whether "balanced bits = good bits" was ever more than an assumption — backdrop
  for our measured balance-worse phenomenon (rotation balanced bits 0.459-0.545 while hurting
  retrieval [MEASURED HERE — FINDINGS_DIGEST quantization layer]).
- Changes: nothing runs; lowest rank because round 1 + verified ITQ scope already cover the
  decision (rotations stay out of the pipeline).

## Explicitly NOT queued (and why)

- BPR full/eval code, RaBitQ-original full, PQ equal-byte ANN controls, ConTEB, graph-RAG
  primaries, Nemotron table re-capture: all owned by DO_NOT_RESCAN §B / GAP_TO_100 as
  conditional fetches for OTHER questions (denominator resolution, frontier controls,
  high-90s costing) [MEASURED HERE — inventory]. None decides D1-D4; re-requesting them
  here would waste the round.
- Cover & Thomas edition/page, Fano formula, LSH survey: textbook background for Q1.1-Q1.3
  wording; the coordinator can cite house copies without spending fetch priority. No fetch
  slot assigned beyond F7's search.
- Any "gold Hit@10 at K=10 from <=16 B/doc" hunt: GAP_TO_100 §B.8 already rules this is a
  NEW EXPERIMENT, not a fetch [MEASURED HERE — inventory]. Not queued.

## Suggested fetch order under limited web budget

Minimum useful set: F1 + F2 (one LSI-plot source plus one collection-size source often co-occur
in the same review chapter — try Landauer-style reviews first). If budget remains: F3, then
F5, then F7-search. F4/F6/F8 are rule-out/background slots; take them only with spare budget.
