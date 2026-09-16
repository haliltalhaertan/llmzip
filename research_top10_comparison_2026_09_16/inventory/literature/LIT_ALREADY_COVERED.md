[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# LIT_ALREADY_COVERED — questions the prior literature rounds already answered

Inventory of programme literature work already executed (2026-09-15 rounds + incoming
2026-09-16 package). Purpose: nobody re-derives these conclusions from scratch.
Every number below is CLAIM (producer-stated, inspected in stored copies) or RELAYED
(quoted second-hand); nothing was re-derived from raw per-query data in this inventory,
so nothing is VERIFIED. Per-row detail lives in `LIT_LEDGER.csv`.

## Round A — top10_literature_20260915 (retrieval-at-K literature shortlist)

Stored at `/mnt/c/Users/MDP/dev/llmzip-work/top10_literature_20260915/`.
Two worker review sessions (exit 0, raw logs kept as `quality_review.log`,
`compression_review.log`) plus coordinator disposition (`COORDINATOR_REVIEW.md`)
and final `REPORT.md`. 11 sources fetched and retained under `sources/`.

### A1. Already answered: best directly relevant compact-code candidate
Conclusion recorded (`REPORT.md` §1): **PPLX-embed (0.6B/4B) with native INT8
quantisation-aware training and post-hoc binary output** is the most relevant
compact-code candidate found; 0.6B is the cheaper encoder control.
Exact recorded numbers (all nDCG@10, NOT Hit@10): 4B INT8 69.66 / BIN 68.22,
0.6B INT8 65.41 / BIN 61.44 (MTEB Multilingual v2); PPLXQ2Q internal Recall@10:
4B INT8 73.46 / BIN 72.41 vs Qwen4B 67.90.
Already-recorded limitation: smallest reported code is 0.6B BIN ≈ **128 B/doc**,
4B BIN ≈ **320 B/doc** — no 12-byte operating point is reported anywhere in the file.
A paper-trained-but-unheadlined 128-D binary point would be 16 B; its quality at
that size is unmeasured.

### A2. Already answered: strongest full-size quality references
Conclusion recorded (`REPORT.md` §2): **Nemotron-3-Embed-8B** (vendor nDCG@10 78.46
RTEB-16 / 75.45 MMTEB Retrieval, dated 2026-07-16) alongside **Qwen3-Embedding**
(0.6B/4B/8B, MRL-supported, dims 1024/2560/4096) as references — explicitly
**references, not ceilings** (`COORDINATOR_REVIEW.md` §7: another representation
or scoring rule may beat any full-float reference).
Independent same-harness check already on file (`sources/independent_musique.md`):
13 embedders × 1000 MuSiQue Qs × 11,656 passages, brute-force cosine, no ANN —
Nemotron-3-Embed-8B Recall@5 69.79 / Recall@10 77.54 vs NV-Embed-v2 69.55 / 78.12
(differences not significant; "matches, does not beat"). BGE-M3 dense lands
second-last here (R@10 62.89) — recorded as proof that general-leaderboard
reputation does not transfer to a specific hard benchmark.

### A3. Already answered with CAUTION: near-100% exists, but only for a large pipeline
Conclusion recorded (`REPORT.md` §3 + `COORDINATOR_REVIEW.md` §8):
**Anthropic contextual retrieval + BM25 + rerank** reaches vendor-reported
Recall@10 of 96.5 / 92.8 / 98.0 / 97.5 / 99.3 across five domains
(macro 96.82 from rounded chart labels) — with the already-recorded cautions:
headline uses **Top-20 (must not be relabelled Top-10)**; pipeline retrieves
**150 candidates before reranking** and therefore accesses far more than a tiny
code per document (raw text, embeddings, BM25); chart values are computed from
**rounded failure labels, not raw query data**; not independently replicated;
not a pooled query-weighted metric. Retained artefacts: PDF appendix, page
renders, `anthropic_chart_readback.json`.

### A4. Already answered with CAUTIONS: compression controls and their traps
- **BPR-768** (`compression_review.log` §2, `COORDINATOR_REVIEW.md` §6): learned
  binary codes are **96 bytes, not 96 bits**. Table 1: NQ top-20 recall 77.9
  (DPR 78.4), top-100 85.7; index 2.0 GB vs 64.6 GB. Recorded cautions: reported
  K ∈ {1, 20, 100} — **none is Hit@10**; rescoring uses continuous query × binary
  passage (no doc float vectors — code-only through top-k) but the QA reader
  afterwards reads raw text; paper's "percentage of positive passages in top-k"
  **denominator was left unresolved** — retain author label "top-k recall", do not
  assert our gold-Hit protocol.
- **Extended RaBitQ** (`REPORT.md` §4, `COORDINATOR_REVIEW.md`): ">95% at ~6.4×,
  >99% at ~4.5× without raw-vector reranking" is **ANN recall = fraction of true
  nearest neighbours recovered, NOT gold-passage Hit@10**. Appropriate use
  recorded: compress a strong representation, then measure gold Hit@10 separately.
  Norms/estimator factors/rotations/IVF must be charged on top of packed bits.
- **MUVERA/ColBERT** (`REPORT.md` §4): PQ-compressed FDE example is **1,280 B**,
  and the cascade needs **document token vectors for Chamfer rescoring**
  (~2,300–21,000 floats/doc). NOT code-only. FDE Recall@100 82.82 / Recall@1000
  94.88 are **Chamfer-neighbour agreement, not gold Hit@10**.
- **BGE-M3 hybrid** (`quality_review.log` §3): dense 67.8 → All 70.0 MIRACL
  nDCG@10; hybrid stores dense CLS + per-token multi-vector matrix + per-term
  sparse weights and reranks top-200/1000 — **not a 12-byte comparator when all
  representations are stored**. Dense-only is the only tiny-code-eligible arm.
- **ConvMemory v2** (`REPORT.md` §4): reorders a protected top-10, so Recall@10
  and Hit@10 are **frozen by construction** — cannot improve Hit@10; not a
  candidate-admission solution. FULL: R@10 0.7798, MRR 0.5824→0.6560.
- **Coordinator-rejected worker assertions** (`COORDINATOR_REVIEW.md` §§1–2, do not
  re-litigate): (a) "Hit@10 should lie below nDCG headlines" — rejected, direction
  unsupported; keep the two metrics separate instead. (b) "PPLX contextual needs
  raw context at scoring time" — rejected; ConTEB scores cosine between query and
  stored chunk embeddings (code-only eligible after indexing; still one code per
  chunk plus indexing/model costs).

### A5. Already answered: no source establishes tiny-code near-100% gold Hit@10
Recorded verbatim in spirit (`REPORT.md` §Decision, `compression_review.log` §5):
**no inspected source reports gold Hit@10 from tiny codes alone**; the closest
tiny-code numbers are K≫10 (BPR Top-100 85.7%), non-gold (RaBitQ/MUVERA
ANN/Chamfer agreement), non-Hit (PPLX BIN nDCG@10 ≈61–68), or full-float
(MuSiQue Recall@10 ≈78%). "Bounded literature finding, not an impossibility
theorem" (`COORDINATOR_REVIEW.md` §9).

## Round B — chat_literature_review_20260915 (chat-history + snippet literature triage)

Stored at `/mnt/c/Users/MDP/dev/llmzip-work/chat_literature_review_20260915/`.
Decision review `IDEA_REVIEW.md`; track reports `retrieval/REPORT.md`,
`inverse/REPORT.md`, `coverage/REPORT.md`; 13 first-hand snippet sources in
`report_citations.json` + `literature/source_*.txt`.

### B1. Already answered: three problems must stay separate
Recorded (`IDEA_REVIEW.md` §2): (1) finding relevant text (compact doc vectors),
(2) saving inference KV memory, (3) saving training activation memory. A result
in one does not establish the others. FLOAT-top-K agreement is a fidelity
objective, not a semantic-quality verdict.

### B2. Already answered: prioritised ideas and their evidence status
- **Asymmetric query scoring first** (keep docs tiny, spend precision on the
  short-lived query): standard practice (SBERT binary→float rescore recipe;
  PQ asymmetric vector-to-code distance). Never built/measured in the chat's
  assigned lines; good engineering, not novelty. Cost to charge: query encoding,
  temporary memory, rescore latency, any axis/scale state.
- **One fixed-total-budget mixed-precision candidate** (B8 = 80×1-bit + 8×2-bit +
  8 dropped = 96 bits): only FLOAT-agreement support (+0.0079, provenance absent);
  **no qrels run exists** — decisive test specified but not run.
- **Lost-information ledger + checkpoints** (KV line): real toy signal only
  (4 bits/scalar/layer → ~1e-6 K/V error, ~98–99% lattice match on random-init
  MHA toys, ~28× CPU slowdown, dense-Jacobian Newton unscalable). Minimum
  decisive test specified (one small pretrained GQA model vs KIVI/KVQuant with
  task metrics + GPU latency) but not run. KIVI (tuning-free 2-bit KV,
  snippet-level) is the recorded baseline any ledger must beat.
- **Parked/rejected as stated**: more tie-only suffix widths (R8 +0.113 pp R@3,
  R16 −0.144 pp — tie reduction ≠ relevance gain); universal exact rational
  arithmetic (bit-blowup measured: one scalar → ~66 kbit after 5,000 steps);
  one-branch-bit inverts everything; predicting SIGN-wins from geometry stats
  (hypothesis, not finding — programme hypotheses already failed cross-benchmark
  checks); 12-byte *system* cost claim (projector/state ≈88.9 KB/vector and a
  denominator double-count bug documented in-chat — any cost claim needs the
  static-storage accounting).
- **Corrections to chat/worker claims** (`IDEA_REVIEW.md` §5, do not re-derive):
  NanoBEIR FLOAT is TF-IDF+SVD96, not a trained encoder; Newton CSV has only
  0–3 (4–6 extension is prose-only) and its `converged=True` column is hardcoded;
  contraction is sufficient not necessary for invertibility; returned K/V are
  post-RoPE; no denoising mechanism is established.

## Round C — next_route_round1/revised/LITERATURE_CORRECTION.md

Authoritative correction superseding affected attributions in
LITERATURE_AND_XIAO.md and earlier literature-fidelity drafts. Already decided,
do not reopen without new primary-source evidence:
- Withdraw "rotation loss confirms Corollary 3" (archived corollary is about the
  heterogeneity-dependent TWO-bit component; local run measured absolute ONE-bit level).
- Withdraw "local two-bit run tested the paper's method" (archived Eq. 2 uses
  per-vector mean-absolute-magnitude threshold + weighted signed products;
  historical xiao_test.py used per-axis medians + equal-weight Hamming).
- Historical losses stand **only for the historical construction**; they neither
  refute the paper's theorem nor transfer to a TF-IDF/SVD gold-FR@3 domain.
- Executable reference `paper_s2.py` implements archived S2 only; at 96-D its
  conceptual two-bit payload is **24 bytes — outside the 12-byte contest**.

## Round D — incoming 2026-09-16 literature/UI package

Stored under `/mnt/c/Users/MDP/dev/llmzip-work/incoming_20260916/extracted/LLMZIP_LITERATUR_EK_HESAPLAR_2026-09-15/`.
Already computed by the producer (CLAIM status here; coordinator verified the
separate headline arms, not these files):
- `complementarity.json/.csv` (status POST_HOC_DIAGNOSTIC): per-query oracle
  choice between sign96 and float_std32 gives hindsight max expected Hit@10 of
  LME 90.21 / PerLTQA 86.07 / RealTalk 54.98. Recorded by producer as an
  **upper bound for choosing between two scorers — not a top-k union rate, not
  a usable rule** (needs gold labels at selection).
- `hypothetical_budget.json` (status HYPOTHETICAL_DESIGN_ARITHMETIC): 96-D,
  510 archives, 252,838 docs → sign96 codes 3,034,056 B; conditional-centroid
  extra 391,680 B; PQ4 codebooks 3,133,440 B; OPQ rotation 18,800,640 B;
  **excludes encoder/IDs/query workspace/overhead/metadata**. Design arithmetic,
  not measured RAM.

## Standing measurement context (prior jobs, not literature)

- Own baseline `top10_comparison_r1/baseline/` (CLAIM here): 9,440 queries,
  Hit@10 sign96/float_raw/float_std/asym = PerLTQA .7568/.8081/.8396/.8019,
  LME .8638/.8255/.8830/.8574, RealTalk .4652/.3660/.4851/.4355; FR@3 replay
  gate PASSED (max dev 0.0, tol 1e-12). Coordinator cross-check: incoming
  "qscale" reproduced EXACTLY (LME 88.5106, PerLTQA 80.0000, RealTalk 49.6454);
  "qsign_dstd" did NOT match (+0.6383/−0.2662/−0.8511 pp) — both per brief.
