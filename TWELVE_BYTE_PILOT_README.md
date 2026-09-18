# The twelve-byte pilot — what it was, and why it stopped

*Written 2026-09-18, after the round landed on `main`. Read this before opening any of the
3,475 files it added.*

---

## What was tried

Compress a document into **12 bytes** (later 24 and 48) and still retrieve the right document
for a question — without reading the document text at query time.

The pipeline: TF-IDF (word + character n-grams) → LSA → SVD to *k* dimensions → L2 normalise →
subtract the archive mean → keep the **sign** of each coordinate as one bit.
k=96 → 12 B, k=192 → 24 B, k=384 → 48 B.

Benchmarks: RealTalk (10 archives, 705 questions), PerLTQA (30 archives, 8,265), LoCoMo, LME.
Metrics: Hit@10 and fractional evidence recall@3. The competitor: **BM25**, classical lexical
retrieval from the 1990s.

## Why it stopped

A fairly configured BM25 beats the best 48-byte code.

| | Hit@10 | FR@3 |
|---|---:|---:|
| 48 B code (`qscale`, k=384) | 57.87 | 32.79 |
| BM25, textbook k1=1.2/b=0.75, frozen tokenizer | **61.70** | **36.05** |
| **gap** | **−3.83 pp** | **−3.26 pp** |

Earlier rounds had been comparing against a *handicapped* BM25 (a coarse tokenizer). Giving
BM25 the same tokenizer this project gave itself moved it from 55.32 to 61.70 — and the
apparent win disappeared.

**This is an exploratory engineering decision, not a preregistered scientific result.** The
stopping gates were written down and applied, but the implementation departs from the referee
contract (gate C1 was evaluated on one benchmark instead of two, without a confidence
interval; gates C2 and C4 were never implemented; C3's equal-rerank-budget control was never
stored). The direction survives all of that — the code loses the primary comparison outright —
but "we stopped by prespecified gates exactly as written" is not a claim this package supports.

## Which numbers stand

- **12 / 24 / 48 B** — correct as *document-code payload*. Not total system state: the query
  path additionally needs the fitted encoder (both TF-IDF vocabularies and IDF tables, both SVD
  matrices, the archive mean `mu`, and σ for the `qscale` arm). That state was never inside the
  headline figure.
- **The width ladder.** More bits genuinely help, and this is the round's most durable result.
  Under a *fixed encoder fitted on other archives*, 96 → 192 → 384 bits gains **+19.86 pp** —
  roughly twice the gain measured with a per-archive fit. Within this protocol the dimension
  budget acts as a lever that is not an artifact of corpus adaptation.

  **Scope:** RealTalk, `qscale`, the k∈{96,192,384} ladder, under the specific fixed-encoder
  (INDEP) construction of audit round R4. It is a benchmark-and-protocol result, not a general
  law about representation width, and it carries no confidence interval. Do not quote it as
  "more bits always help."
- **Per-archive projector fitting** is a preregistered design rule of this programme, documented
  in `COMMON_MODE_CLASSIFICATION.md`. Queries and gold labels never enter the fit.
- The per-query result files, the fidelity gates (0 differing bits of 858,624), and the
  producer code for the RealTalk/PerLTQA representations, which was audited directly and
  reproduced bit-identically on four archives.

## Which claims were withdrawn

- **"Transductive leakage."** An audit round labelled per-archive fitting as leakage. It is not:
  it is the documented design. The correct framing is **corpus-adaptation dependence** — a real
  and large portability limitation (fixing the encoder on other archives costs ~28–30 pp), but a
  property of the deployment regime, not a contaminated measurement.
- **"The PerLTQA decline at high k is rank overflow."** Disproved by this project's own T3 test:
  enforcing k<n removed every constant dimension and the decline persisted.
- **"...and the mechanism is σ-division."** Also wrong: the `sym` arm never divides by σ and
  declines anyway (53.88 → 48.71). **The mechanism is unresolved.**
- **"BM25 needs an inverted index and raw text at query time."** False. First-stage BM25 reads
  postings, IDF and document lengths only. The storage comparison had been drawn on an
  asymmetric boundary that favoured this project.
- **"All contrasts use a paired archive-clustered bootstrap."** False. Several headline numbers
  are point estimates, and the per-question data needed to build an interval was computed and
  then discarded.
- **"SIGN beats FLOAT by +10 pp."** True only against an *unstandardized* float reference.
  Standardizing the same float reverses the comparison. See ledger L-097.

## How this round was checked

Four internal audit rounds (34 Muse agent roles, evidence published on
`audit/hard-rounds-2026-09-18`, 551 files) found **eight** reporting defects. An external
reviewer reading the same repository afterwards found **six more** — including the most
consequential one, that the published −7.80 pp headline gap was measured against a BM25 variant
chosen by `max()` on the evaluation cohort rather than the referee-primary configuration.

All fourteen are corrected in place, each with a `CORRECTION`/`RETRACTION` note that quotes the
original wording. Nothing was silently edited — this programme's recurring failure has been
corrections that get written and never reach the file a reader opens.

## What remains open

1. **No held-out split exists anywhere in this package.** Configurations, subgroups and
   mechanisms were selected by looking at the same data they are evaluated on. The negative
   result is robust to this; the positive and mechanistic findings are exploratory until frozen
   and tested once on unseen data.
2. **C3's required control** — BM25 first stage with the identical reranker under the same
   candidate budget — was never stored.
3. **The mechanism** behind the high-k scorer-dependent decline is unknown.
4. **Twelve open defect records** inside the round were read but not re-executed.

## What this does NOT close

**This is a line closure, not a programme closure.** What stopped is the twelve-byte
TF-IDF/SVD-sign document-code line, on the benchmarks and under the protocol described above.

No project-wide STOP is established by this round, and none should be inferred from it. Other
lines in this repository — including the sealed Task 4F1 surface, and the dense / E1 / residual /
KV / inverse / storage directions raised in earlier rounds — are **untouched** by this merge.
This round neither ran nor read them, so it cannot pronounce on them. A merge that lands one
line's evidence does not mark the others failed, closed, or superseded.

If the programme as a whole is to be wound down, that is an **owner-level decision** about where
to spend effort, separate from and not licensed by the technical verdict recorded here.

Task 4F1 remains **SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN**,
unchanged by this round.

## Where things are

| | |
|---|---|
| Round contents | `research_top10_comparison_2026_09_16/`, `research_twelve_byte_pilot_2026_09_15/`, `research_f1_execution_2026_09_14/` |
| Start here | `research_top10_comparison_2026_09_16/FINAL_STATE.md` |
| Audit evidence | branch `audit/hard-rounds-2026-09-18`, `audits/` |
| Correction ledger | `audits/CORRECTION_LEDGER_2026-09-17.md` |
| Open questions (all lines) | [`OPEN_QUESTIONS_2026-09-18.md`](OPEN_QUESTIONS_2026-09-18.md) |
| External review prompt | `audits/EXTERNAL_REVIEW_PROMPT_2026-09-18.md` |

Everything in this round carries
`[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]`.
It does not authorize reading any sealed Task 4F1 outcome and changes no frozen number.

---

*In one sentence: an idea was tried, it lost to a thirty-year-old baseline, the loss was
confirmed honestly, and the reporting around it was corrected fourteen times — twice after
outside review.*
