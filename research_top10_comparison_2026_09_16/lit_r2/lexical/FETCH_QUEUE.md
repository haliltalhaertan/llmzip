[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# FETCH QUEUE — ranked lookup list for the coordinator (web access required)

How to read: each item states WHAT to fetch (with search terms, since my
recall of titles/venues may be wrong), WHAT IT SETTLES (the exact question +
verdict flip), and PASS/FAIL criteria. Ranks reflect decision value per fetch
cost. Items F1–F8 are new; prior-round fetches (ITQ, ABTT, RRF, Husbands,
ScaNN, BM25 primaries — `digest_r1/lit/LITERATURE_MAP.md` VERIFY_QUEUE) keep
their ranks and are NOT duplicated, except where a stored copy already answers
(marked AUDIT-ONLY: read on disk, no web needed).

**Global rule (from `DO_NOT_RESCAN.md`): never reconvert metrics
(nDCG↔Hit, FR@3↔Hit@10, ANN-recall↔gold) and never average across benchmarks
when grading these sources.**

---

## Rank 1 — F4: monoBERT passage reranking paper (Q3 mechanism anchor)

- **Search:** `Nogueira Cho "Passage Re-ranking with BERT" arXiv 1901.04085`
  (title/number from memory — confirm, do not trust).
- **Fetch:** full text (arXiv PDF).
- **What it settles:** whether the reranker-dominates-cascade pattern is a
  citable measured result (Q3-iii). Grade PASS if the paper contains ANY of:
  (a) reranked BM25 vs reranked dense (or weak-vs-strong first stage) finals
  converging; (b) an explicit statement that first-stage choice matters little
  given adequate top-k recall; (c) a candidate-depth (k=100/1000) ablation
  showing pool-recall saturation. Record: first-stage(s), depth k, reranker,
  metric (expect MRR/Recall — do NOT convert to our Hit@10; record as-is).
- **Verdict flip:** PASS → Q3 washout moves KNOWN-practice to KNOWN-measured
  (at least the dominance half); FAIL (no first-stage ablation at all) →
  stays folklore, escalate to F5.
- **Confidence it exists:** medium-high (paper); low-medium (contains the ablation).

## Rank 2 — F5: BEIR benchmark paper + MS MARCO overview (Q3 conditions + Q1 anchor)

- **Search:** `Thakur Reimers "BEIR" heterogeneous benchmark zero-shot 2021`;
  `Nguyen "MS MARCO" TREC Deep Learning overview`.
- **Fetch:** BEIR full text + results tables; MS MARCO dataset/overview (for
  cascade context only).
- **What it settles:** (Q3) whether any BEIR table fixes a reranker and varies
  the first stage (BM25 vs dense) with converging finals — the closest thing
  to a published washout-with-conditions; (Q1) the zero-shot BM25-beats-dense
  headline with exact datasets/scales (smallest corpus size = how close to
  our n≈400?). Record per-dataset corpus sizes; check whether ANY dataset is
  ≤1000 docs (that alone would shrink Q1's OPEN).
- **Verdict flip:** BEIR-with-rerank convergence found → Q3 PARTIALLY KNOWN
  with conditions; smallest-BEIR-corpus ≫ our n → Q1 regime confirmed OPEN
  (documented, not just recalled).
- **Confidence:** medium-high (BEIR exists, BM25-zero-shot headline right);
  low (contains fixed-reranker ablation).

## Rank 3 — F1: targeted null-search for small-collection dense-vs-BM25 (Q1 regime)

- **Search (all three, record strategy + hit counts):**
  (a) `"dense retrieval" "small collection" BM25 few hundred documents`;
  (b) `dense passage retrieval low-resource corpus size ablation BEIR smallest`;
  (c) `LSI LSA small collection size retrieval effectiveness TREC`.
- **Fetch:** only if a real ≤~2000-doc dense-vs-BM25 comparison surfaces;
  otherwise record the NULL (databases searched, terms, date, top-20 skimmed).
- **What it settles:** upgrades Q1's "OPEN (recalled)" to "OPEN (documented
  null)" — the strongest citable form of a negative claim, and the shield
  against a reviewer citing a study we missed.
- **Verdict flip:** hit → Q1 becomes PARTIALLY KNOWN (grade the hit by n and
  fitting regime); documented null → Q1 stays OPEN with higher confidence.
- **Confidence a hit exists:** low (my bet: nothing at n≈400 with BM25 as rival).

## Rank 4 — F7: per-paper storage audit (Q4 — bookkeeping, no theory needed)

- **AUDIT-ONLY (no fetch):** BPR stored copy
  (`inventory/literature/sources/bpr_full_recovered.md`): record the exact
  storage number quoted, what scope it covers (bits/doc? +rescore state?
  +query encoder? +text?), and what it omits that we charge (σ, means,
  encoder). One paragraph; this alone gives us a same-family precedent.
- **Fetch (in order, stop after 3–4 — diminishing returns beyond that):**
  (a) DPR paper (`Karpukhin "Dense Passage Retrieval" EMNLP 2020`): index
  size reported? Faiss overhead? text store charged?
  (b) ColBERT paper (`Khattab Zaharia "ColBERT" SIGIR 2020`): token-vector
  bytes stated where (table vs footnote)?
  (c) SPLADE paper (`Formal "SPLADE" SIGIR 2021` or v2): index MB + FLOPs as
  first-class metrics?
  (d) ONE neural-vs-BM25 hybrid the programme actually compares against
  (coordinator picks; BGE-M3 already scanned — audit stored copy first).
- **Record for each:** (1) exact storage number, (2) scope
  (payload/+index/+text/+model), (3) what it omits that we charge ourselves.
- **What it settles:** our reporting convention (dual field+honest vs single
  full-system with precedent). Cannot move before this audit — Q4 stays
  UNVERIFIED until then.
- **Confidence on outcome:** low-medium that vector-bytes-only is modal (do
  not pre-commit; the audit decides).

## Rank 5 — F2: DPR paper analysis section (Q1 mechanism + Q5 precedent)

- **Search:** `Karpukhin "Dense Passage Retrieval for Open-Domain QA" EMNLP 2020` full text.
- **Fetch:** full text; read ONLY the analysis/ablation sections (lexical
  overlap, BM25-complementarity, failure cases) + experimental setup (corpus
  size, training pairs).
- **What it settles:** (a) whether dense-wins-paraphrase / BM25-wins-rare is a
  measured claim with a citable figure (firms Q1's mechanism from folklore to
  KNOWN-analogy); (b) whether a lexical-overlap split of queries is published
  precedent for our S-A stratification (Q5 anchor).
- **Verdict flip:** PASS on either → cite and stop defending that half from
  first principles; FAIL → S-A stands on logic alone (still valid).
- **Confidence:** medium (paper exists, has analysis); low (contains the split).

## Rank 6 — F3: LSI collection-size / dimensionality studies (Q2 defensive)

- **Search:** (a) `Dumais LSI dimensionality TREC optimal dimensions`;
  (b) `Landauer Dumais LSA corpus size "Plato's problem"`;
  (c) `LSA "corpus size" retrieval effectiveness collection size ablation`.
- **Fetch:** only the best hit, if any addresses size-dependence; else record NULL.
- **What it settles:** purely defensive — confirms no minimum-size study
  exists (expected), or finds an adjacent result (dimensionality optimum,
  training-size curve) to cite as background. Changes NO number; Q2's
  grounding is derivational either way (LEXICAL_MAP.md Q2 steps 1–3).
- **Confidence a size study exists:** low.

## Rank 7 — F6: ANN first-stage evaluation framing (Q3 metric reform)

- **Search:** `ScaNN "anisotropic" quantization Guo 2020` (round 1 context);
  `Faiss billion-scale ANN recall latency benchmark`.
- **Fetch:** ScaNN paper ONLY if round-1 fetch did not already capture its
  eval framing; otherwise any one ANN paper's evaluation section.
- **What it settles:** whether "first stage evaluated on recall@depth per
  byte/latency, not standalone quality" is citable precedent for our proposed
  metric reform (pool recall@M per byte). One confirming quote suffices.
- **Confidence:** medium-high that the framing exists; low on which paper
  states it most cleanly.

## Rank 8 — F8: QPP / TREC Robust stratification precedent (Q5 principle)

- **Search:** `Hauff "query performance prediction" pre-retrieval predictors`;
  `TREC Robust 2004 hard topics`.
- **Fetch:** one QPP survey/overview section + Robust track overview (secondary
  priority; fetch only if F2 fails to give S-A a precedent).
- **What it settles:** citable precedent for pre-retrieval (scorer-free)
  stratification — the non-circularity principle behind S-A/S-B/S-C. Cite for
  the PRINCIPLE; explicitly do NOT adopt IDF-based predictors (would
  reintroduce circularity — see LEXICAL_MAP.md Q5 S-B trap note).
- **Confidence:** medium (literature exists); low-medium (needed — our splits
  stand without it).

---

## Explicitly NOT queued (and why)

- ITQ paper, all-but-the-top, RRF original, Husbands 2005, ScaNN loss, BM25
  saturation/length-norm, LSI log-entropy weighting: already queued in round 1
  (`digest_r1/lit/LITERATURE_MAP.md` VERIFY_QUEUE) — do not double-queue.
- KIVI/EchoKV/xKV/BDIA full texts, RaBitQ original, Jégou PQ primary,
  HippoRAG/GraphRAG family, ConTEB primary: ruled out-of-scope by
  `DO_NOT_RESCAN.md` §B unless named arms reopen — none did.
- BM25-handicap claims (frozen tokenizer +~3 pp; k1→0/b→0 42.11 vs 37.67):
  flagged in LEXICAL_MAP.md as UNASSESSED (artifacts not on my disk) — these
  are coordinator-internal verifications against OUR artifacts, not literature
  fetches; no queue item needed.
- Union-pool + rerank cell, S-A/S-C stratifications, M-sweep of the washout:
  EXPERIMENTS on disk, not fetches — listed in LEXICAL_MAP.md Q3-iv/Q5.

## Suggested fetch order for a limited round

If the coordinator can fetch only three: **F4 → F5 → F7** (Q3 anchor, Q3
conditions + Q1 anchor, storage bookkeeping). If five: add F1 (documented
null) and F2 (mechanism + precedent). F3/F6/F8 are background and can wait.
