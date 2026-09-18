[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# GAP_TO_100 — can gold be pushed into Top-10 at ~100% with ~12 bytes/document?

Question: with a very small per-document code, can gold be pushed into Top-10 at
~100%? Current best local RealTalk Hit@10 is 49.65% (12-byte codes, numeric scaled
query). Gap to ~100% is therefore ~50 points on RealTalk. All numbers below are
CLAIM or RELAYED (nothing re-derived this session); ledger in `LIT_LEDGER.csv`.
Benchmarks are kept separate throughout.

## Blunt answer

**No stored source supports ~100% Hit@10 at ~12 bytes/document — not at K=10, not
with gold labels, not on any corpus.** Every stored mechanism that reaches very
high Recall@10/Hit@10 territory does so by spending one or more of: (a) hundreds
to thousands of bytes per document, (b) raw text or token vectors at query time,
(c) a 100–500-candidate first stage plus a reranker, (d) a much larger encoder.
The single hardest stored fact: even full-float, brute-force, gold-measured
state-of-the-art sits at Recall@10 ≈ 77–78% on hard multi-hop (MuSiQue panel) —
and an oracle that picks the better of our own two scorers per query still only
reaches expected Hit@10 of 55.0% on RealTalk. The evidence is weak for ~100% at
12 B because the evidence for it is *absent*, while the evidence *against its
easiness* (strong systems falling far short with far bigger budgets) is present.

## What each documented high-recall mechanism costs

| # | Mechanism (stored source) | Best stored number (own metric, own corpus) | What it costs | ~12 B/doc compatible? |
|---|---|---|---|---|
| 1 | Larger/stronger encoders (Nemotron-3-Embed-8B, Qwen3-8B, PPLX-4B) | MuSiQue Recall@10 77.5–78.1 full-float; PPLX BIN nDCG@10 61–68 | 0.6–8B encoder params + compute; codes 128–8,192 B/doc; still 22+ pts off 100 on hard multi-hop | NO as sole fix — bigger encoders alone do not reach ~100 even at full precision |
| 2 | Contextual encoding (PPLX-context; Anthropic contextual chunks) | ConTEB nDCG@10 81.96 (INT8) / 80.46 (BIN) — separate benchmark | Document context at index time; late chunking; **one code per chunk** (multi-chunk docs pay multiple codes); model + index overhead | NO at 12 B/doc — per-chunk codes multiply the budget; and 81.96 is nDCG, not Hit@10 |
| 3 | Lexical + dense + multi-vector hybrid (BGE-M3 All; Anthropic emb+BM25) | MIRACL nDCG@10 70.0; Anthropic vendor Recall@10 macro 96.82 | Token-level multi-vector matrix + lexicon weights per doc; raw text at rank time; summed-score rerank over top-200/1000 (BGE) or 150 candidates + cross-encoder (Anthropic) | FUNDAMENTALLY MORE — requires stored text/vectors plus a large candidate pool, not a 12-B code |
| 4 | Large-candidate rerank cascades (Anthropic 150→10; Qwen reranker top-100; mxbai_top500; ConvMemory v1 top-500) | Anthropic Recall@10 92.8–99.3 (vendor, K=10 after rerank); mxbai_top500 R@10 0.8080 | 100–500 raw-text reads per query; 10–500 cross-encoder scorings; reranker weights (22.7M–large); full-pool retrieval underneath | FUNDAMENTALLY MORE — a reranker only reorders candidates the small code admitted; ConvMemory v2 proves the point: Hit@10 frozen by construction |
| 5 | Asymmetric scoring: float query × binary codes (BPR §3.3 rescore; SBERT recipe; PQ ADC) | BPR Top-20 recall 77.9 at 96 B (vs DPR 78.4) | Query-time float embedding + rescore latency over l=1000 candidates; axis/scale state | YES, compatible — but it only reorders within what the code retrieved; recorded gains are ordering gains, and BPR at 8× our budget still reports no K=10 gold Hit@10 |
| 6 | Learned binary codes (BPR-768) | Top-20 recall 77.9; Top-100 85.7 (NQ, 21M corpus) | 96 B/doc (8× budget); continuous-query rescore; raw-text reader for QA accuracy | CLOSEST family, still NO — 8× over budget, K≠10, denominator unresolved, reader needs text |
| 7 | Multi-bit ANN quantisers (Extended RaBitQ B=1–10; SQ/LVQ/PQ/OPQ controls) | >99% **ANN** recall at ~4.5× compression, no raw-vector rerank | 392–1,928 B/doc at D=3072 (32–160× budget); +2 floats/vector; rotations/centroids/IVF | NO — and conceptually capped: >99% preservation of the *float ranking* cannot exceed the float ranking's own gold rate (~78% R@10 on hard multi-hop) |
| 8 | MUVERA FDE + PQ + Chamfer rescore | FDE Recall@100 82.8 / Recall@1000 94.9 (Chamfer agreement) | 1,280 B FDE + full token-vector store (avg ~10k floats/doc MS MARCO) + exact Chamfer rescore | FUNDAMENTALLY MORE — token store + rescore are the system, the FDE is not standalone |
| 9 | Fixed-budget reallocation (B8 80×1+8×2; micro-residual R8) | R8 +0.113 pp R@3 (gold, NanoBEIR); B8 +0.0079 FLOAT-agreement only | Zero or +1 byte; threshold/axis state | YES, compatible — but measured effects are ~0.1 pp, and B8 has no qrels run at all |
| 10 | Oracle per-query scorer selection (incoming complementarity.json) | Hindsight max expected Hit@10: LME 90.21 / PerLTQA 86.07 / RealTalk 54.98 | Requires gold labels at selection time (unavailable at inference); not a union rate | NOT a mechanism — an upper bound, and on RealTalk the bound itself is 45 pts short of 100 |

## Reading the gap honestly

1. The ceiling evidence is sobering, not encouraging. Full-float SOTA with no
   compression at all reaches only ~78% Recall@10 on MuSiQue-hard multi-hop
   (multi-gold metric, so strictly harder than Hit@10 — but 22 points of headroom
   to 100 remain even before any compression). Compression can only preserve or
   lose that ranking, never conjure gold the float geometry lacks (RaBitQ's own
   framing: preserve the chosen geometry, then measure gold separately).
2. RealTalk is the binding constraint. Local best is 49.65% Hit@10; the oracle
   chooser between our two scorers caps at 55.0% expected. That means ~45 points
   of the gap survive even perfect per-query selection among existing scorers —
   new representation power is needed, not better selection, and no stored source
   exhibits that power at 12 B.
3. The only stored route to the high-90s (Anthropic-style: contextual chunks +
   lexical + 150-candidate + rerank over raw text) is a different system class
   with a different bill of materials. It is compatible with the programme only
   as a separately costed relaxed-budget arm — it answers "what does ~97% cost",
   not "12 bytes suffice".
4. Asymmetric scoring is the one compatible mechanism not yet exhausted locally
   (baseline `asym` arm exists; BPR-style continuous-query rescore over l=1000
   with latency accounting is the recorded next test). Expect ordering gains of
   single-digit points at best — the stored precedent (BPR) needed 96 bytes plus
   rescore to tie DPR at K=20, not to beat float at K=10.

## Verdict for planning

Do not plan around ~100% Hit@10 at ~12 B/doc: **no stored source supports it,
and two independent stored bounds (full-float SOTA ~78% R@10 on hard multi-hop;
oracle selection 55% on RealTalk) say the gap is structural, not a tuning
artefact.** The honest programme fork is: (a) measure how far compatible tricks
(asymmetric rescore, one frozen reallocation, stronger-but-small encoders such as
PPLX-0.6B BIN at 128 B) actually move gold Hit@10 per byte; (b) cost the
relaxed-budget cascade separately so the team knows the true price of high-90s.
Evidence strength: moderate that 12-B ~100% is unsupported (absence across 11
fetched sources + 2 review rounds is a bounded finding, not a proof); strong
that every known high-90s route violates the 12-B constraint.
