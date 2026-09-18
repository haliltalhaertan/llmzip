[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# DO_NOT_RESCAN — sources already fetched and reviewed; genuine gaps for a new fetch

## A. Already fetched and reviewed — skip in any future round

### Round top10_literature_20260915 (11 sources, full stored copies + coordinator review)
1. PPLX — Diffusion-Pretrained Dense and Contextual Embeddings (arXiv:2602.11151v2).
   Files: `sources/pplx.html`, `pplx_full.txt`, `pplx_recovered.md`, `pplx.md`, `pplx.json`.
   Reviewed in `REPORT.md` §1, `quality_review.log` §1, `compression_review.log` §2.
2. Nemotron-3-Embed-8B model card (huggingface.co/nvidia/Nemotron-3-Embed-8B-BF16).
   Files: `sources/nemotron.md`, `nemotron_raw.md`, `nemotron.json`.
   Reviewed in `REPORT.md` §2, `quality_review.log` §4.
3. Qwen3 Embedding (arXiv:2506.05176v3). File: `sources/qwen.md`.
   Reviewed in `REPORT.md` §2, `quality_review.log` §2.
4. Anthropic Contextual Retrieval (engineering page). Files: `sources/anthropic_full.txt`,
   `anthropic.html`. Reviewed in `REPORT.md` §3.
5. Anthropic Contextual Retrieval Appendix II (PDF p3 chart). Files:
   `sources/anthropic_appendix.pdf`, `anthropic_appendix_text.txt`,
   `anthropic_page_1/2/3.png`, top-level `anthropic_chart_readback.json`.
   Visually inspected + transcribed by coordinator (`COORDINATOR_REVIEW.md` §8).
6. BPR — Binary Passage Retriever (arXiv:2106.00882). Files: `sources/bpr_full_recovered.md`,
   `bpr.md`, `bpr.json`. Reviewed in `REPORT.md` §4, `compression_review.log` §2–4.
7. Extended RaBitQ (arXiv:2409.09913v1). Files: `sources/rabitq_ext.md`,
   `rabitq_ext_full.txt`, `rabitq_ext.html`, `rabitq_ext.json`.
   Reviewed in `REPORT.md` §4, `compression_review.log` §2–4.
8. MUVERA (arXiv:2405.19504v1). Files: `sources/muvera_recovered.md`, `muvera.md`,
   `muvera.json`. Reviewed in `REPORT.md` §4, `compression_review.log` §2–4.
9. Independent MuSiQue embedding panel (arXiv:2608.16096v1).
   File: `sources/independent_musique.md`. Reviewed in `REPORT.md` §2, `quality_review.log` §5.
10. BGE-M3 (arXiv:2402.03216v3). Files: `sources/bge.md`, `bge.json`.
    Reviewed in `REPORT.md` §4, `quality_review.log` §3.
11. ConvMemory v2 (arXiv:2606.10842v1). File: `sources/convmemory.md`.
    Reviewed in `REPORT.md` §4, `quality_review.log` §6.
    Review artefacts: `REPORT.md`, `COORDINATOR_REVIEW.md`, `citations.json`,
    `source_index.json`, `source_index_complete.json`, `quality_review.log/.txt`,
    `compression_review.log/.txt`, `inspect_sources.py`.

### Round chat_literature_review_20260915 (13 snippet-level sources + full chat triage)
Snippet sources (first-hand snippet statements only; full papers NOT re-retrieved):
SBERT embedding-quantization doc; Jégou PQ (Searching with Quantization);
RaBitQ original (arXiv:2405.12497); Maclaurin reversible learning; RevNets;
BDIA / exact bit-level reversible Transformer; i-ResNet; KIVI; EchoKV; DEQ;
gradient-checkpointing (sublinear memory); Reformer; xKV.
Registry: `report_source_registry.json`, `report_citations.json`,
`literature/source_01–22.json/.txt`, `evidence_quotes.json`, `csv_inventory.json`.
Chat triage: `IDEA_REVIEW.md` (decision review),
`retrieval/REPORT.md` + `retrieval/inventory.json`,
`inverse/REPORT.md` + `inverse/inventory.json`,
`coverage/REPORT.md` + `coverage/inventory.json`
(conversation 1–16579 fully covered; `input/` chat exports + 180-row adversarial
CSV + 45-row Newton CSV parsed read-only).

### Corrections and incoming packages (do not re-derive)
- `next_route_round1/revised/LITERATURE_CORRECTION.md` (authoritative; supersedes
  LITERATURE_AND_XIAO.md attributions; `paper_s2.py` reference implementation).
- Incoming 2026-09-16 package `LLMZIP_LITERATUR_EK_HESAPLAR_2026-09-15/`:
  `complementarity.json/.csv`, `hypothetical_budget.json`, `diagnose_complementarity.py`.
- Own baseline `top10_comparison_r1/baseline/` (9440-query Top-10; REPORT.md +
  per_query_top10.jsonl) and coordinator `verify_incoming.py`/`verify_incoming.json`
  (12/12 old-arm cells exact; qscale exact; qsign_dstd mismatched) — per brief.

## B. Genuine gaps that would need a NEW fetch (nothing else justifies one)

1. BPR evaluation code / denominator resolution. The paper text's "percentage of
   positive passages in top-k" is ambiguous (follows DPR); resolving fractional
   evidence-recall vs Hit-style counting needs the authors' eval code
   (github.com/studio-ousia/bpr), not another read of the PDF.
2. Raw per-query data behind the Anthropic Appendix II chart (or any rerun of a
   150-candidate + rerank cascade on a fixed corpus with gold Hit@10 at exactly
   K=10). The stored chart gives rounded Recall@10 only.
3. Primary ConTEB source (Conti et al. 2025) for the voyage-context-3 79.45 and
   Anthropic 72.4 figures quoted second-hand inside the PPLX paper.
4. HippoRAG-2 / PropRAG / SAG / KET-RAG / GraphRAG primary papers, only if the
   team ever prices graph-system indexing or needs the NV-Embed-v2-anchored
   system numbers first-hand (currently RELAYED via the MuSiQue panel paper).
5. Full texts (not snippets) of KIVI / EchoKV / xKV / BDIA / MEFT / KVReviver —
   needed ONLY if the KV-cache inversion line reopens (currently toy-only with
   a specified-but-unrun decisive test).
6. Full RaBitQ original (Gao & Long 2024) and Jégou PQ primary — needed ONLY if
   the team implements the RaBitQ/PQ equal-byte ANN controls (recommended as
   compression-frontier controls, not as gold-Hit solutions).
7. Nemotron vendor RTEB/MMTEB table primary (leaderboard snapshot or model-card
   table capture) — the stored card excerpt inspected this session did not
   surface the 78.46 / 75.45 figures; they are currently CLAIM via the prior
   review's citations, worth one targeted re-capture before any citation.
8. Anything reporting gold Hit@10 at K=10 from ≤12–16 B/doc codes on any corpus.
   No stored source contains this; it does not exist in the fetched set. This is
   a NEW EXPERIMENT (local benchmark arms: asymmetric rescore, frozen B8/B-realloc,
   PPLX-0.6B BIN downward sweep), not a fetch — do not send another literature
   round looking for it in already-reviewed venues.

## C. Rescan hygiene

- Never reconvert metrics (nDCG↔Hit, FR@3↔Hit@10, ANN-recall↔gold) and never
  average across benchmarks — the two most common failure modes these rounds
  already caught and corrected.
- Treat worker-log assertions as superseded where `COORDINATOR_REVIEW.md`,
  `IDEA_REVIEW.md` §5, or `LITERATURE_CORRECTION.md` rules against them (listed
  in `LIT_ALREADY_COVERED.md`); re-opening one needs new primary evidence, not
  a fresh reading of the same stored copy.
