# V52 — SIGN96 MECHANISM: SYSTEMATIC LITERATURE SCAN (COLD START)

You are a researcher on the llmzip V52 program, assigned a **literature scan**, not an experiment.

Your job is to establish, with evidence a sceptic would accept, **where our SIGN96 mechanism result
sits in the published literature**: what is already known, what is already claimed, what is genuinely
open, and whether anyone reports a stronger or contradicting result.

Türkçe cevap verebilirsiniz; raporu İngilizce yazın, kısa Türkçe özet ekleyebilirsiniz.

---

## 1. The result you are scanning around

Two frozen benchmarks, LoCoMo (n=1535) and LongMemEval (n=470). Archive-local SVD to 96
coordinates, centered, then sign-quantized (`>= 0`) to 96 bits. Retrieval by Hamming distance,
top-3, fractional evidence recall.

Three measured facts (already independently audited; treat them as **inputs**, not as things you
need to re-verify):

1. Native SIGN96 beats an unrestricted Haar rotation applied before sign quantization:
   `0.237` vs `0.138` (LoCoMo), `0.542` vs `0.383` (LongMemEval).
2. A **block-diagonal** Haar rotation — leading 32 coordinates rotated only among themselves, the
   remaining 64 only among themselves — preserves most of that advantage: `rho_2 = 0.107` and
   `0.157`, where `rho_2 = 1` means the intervention lost as much as full rotation and `0` means it
   lost nothing.
3. A **matched-size random** 32/64 partition — a random 32-subset rotated among itself, its
   complement among itself — loses almost everything: `rho_2 = 0.949` (LoCoMo).

The working interpretation: what matters is not the individual principal axes, and not merely the
presence of a 32/64 block structure, but **which coordinates are kept out of which block**.

Note for calibration: the leading block alone is *weak* (Head32-only R@3 ≈ 0.083 on LoCoMo against
Tail64-only ≈ 0.215). Do not scan on the assumption that "the head carries the information".

---

## 2. What a prior shallow scan already surfaced — treat every line as a CLAIM TO TEST

A previous, admittedly shallow scan produced the findings below. They are **hypotheses for you**,
not established results, and several may be wrong. Confirm or refute each from primary sources and
say which.

| # | Claim from the prior scan | Your job |
|---|---|---|
| C1 | Xiao (2026), *Covariance Structure and Coordinate Heterogeneity Govern Binary Quantization of Contrastive Embeddings*, arXiv 2605.17524, already explains **whether** random rotation helps or hurts, via coordinate heterogeneity `CV(sigma) = std(sigma_i)/mean(sigma_i)`, and reports it across 18 datasets / 9 embedding families | Confirm the claim, the metric, and the empirical scope |
| C2 | That paper considers **only full Haar rotation** and does **not** examine partial, block-diagonal or selective rotation, nor which spectral band must remain unrotated | **This is the load-bearing negative. Verify it directly in the text.** |
| C3 | QuIVer (arXiv 2605.02171) uses **no rotation at all**, preserves coordinate axes, and performs no principal-component or variance-band analysis | **Second load-bearing negative. Verify directly.** |
| C4 | RaBitQ (SIGMOD 2024) rotates before binarization and attains an asymptotically optimal, distribution-free error bound (Alon–Klartag, FOCS 2017) | Confirm; establish what the bound is *over* — worst case, or data-dependent |
| C5 | OPQ *Eigenvalue Allocation* (Ge, He, Ke, Sun, 2013) already studies which principal components go in which block, but prescribes **balancing** variance across subspaces — the opposite grouping to contiguous head/tail | Confirm, and determine how far the PQ/L2 objective transfers to sign codes + Hamming |
| C6 | R2PCAH (Neurocomputing 2017) splits a long code into short pieces, each taking only top PCA projections, with per-piece random rotation and shift | Full text is paywalled; obtain it legitimately or record the access failure |
| C7 | The `all-but-the-top` / rogue-dimension literature says removing top principal components *improves* embeddings, which is in apparent tension with a "leading block is special" reading | Establish whether the tension is real or dissolves under our metric |
| C8 | No published work applies binary/quantized retrieval representations to agent long-term-memory benchmarks (LoCoMo / LongMemEval / BEAM) | Try hard to refute this |
| C9 | Nobody uses block-diagonal or subspace-restricted rotation as a **causal ablation to localize where a retrieval representation's advantage lives**; the closest methodological analogue is in LLM interpretability (matched-rank random-subspace controls, DAS, angular steering) | Try hard to refute this. It is the core novelty claim. |

**A discrepancy you must resolve.** Two different contents were served for arXiv 2605.17524: a PDF
titled *"Covariance Structure and Coordinate Heterogeneity Govern Binary Quantization of Contrastive
Embeddings"* whose Theorem 2 reads *"Rotation uniformizes coordinate variances"*, and an HTML v1
titled *"Coordinate Heterogeneity Governs Binary Quantization: From InfoNCE to Recall"* whose
Theorem 2 reads *"Weak correlations accumulate"*, with different corollary numbering. **Pin exactly
one version, cite its identifier and date, and take all theorem/corollary numbering from it.** Until
that is done, nothing from this paper may be quoted in a project artifact.

---

## 3. Gaps to close — these are the assignment

1. **Forward citation graph.** Who cites Xiao 2026, QuIVer, RaBitQ / Extended RaBitQ, OPQ, IsoHash,
   ITQ, R2PCAH? Restrict to 2023–2026 for the modern ones. This was never done and is the single
   largest hole.
2. **Specific unopened items:** Extended RaBitQ (SIGMOD 2025); *Revisiting RaBitQ and TurboQuant*
   (arXiv 2604.19528); *Block-Sphere Vector Quantization* (arXiv 2605.19972 — the name suggests
   block structure, treat as high-risk-of-overlap); Locally Optimized PQ; Bilinear OPQ;
   *Foundations of Vector Retrieval* (arXiv 2401.09350) as a survey backbone.
3. **The precise novelty question**, stated so it can be refuted: *has anyone applied a rotation
   restricted to a subspace or a block partition, in order to measure which part of a representation
   a retrieval or similarity metric depends on?* Search hashing, ANN, vector databases, compressed
   sensing, and interpretability. A method that merely *builds* codes block-wise is prior art for the
   construction but **not** for the ablation use; keep those two separate in your report.
4. **Comparability.** Is there any published number that is genuinely comparable to fractional
   evidence recall@3 with binary codes on LoCoMo or LongMemEval? Note that the public leaderboards
   report end-to-end QA accuracy, and LongMemEval's own retrieval metric is a binary hit at
   session/round granularity. If nothing is comparable, say so and explain precisely why, rather
   than manufacturing a comparison.
5. **Beyond arXiv and English.** Journals behind paywalls, patents (there are relevant USPTO
   filings), theses, and non-English venues. Do not bypass any paywall; request access
   legitimately or record the failure.
6. **Theory backbone.** InfoNCE-induces-Gaussian-structure (ICLR 2026) → Gaussian models of binary
   quantization quality → heterogeneity. Establish whether that chain actually holds up or whether
   the prior scan over-connected it.

---

## 4. Method discipline

- **A search-engine summary is not evidence.** Neither is an abstract when the claim concerns what a
  paper does *not* do. For every load-bearing claim, open the source and read the relevant section.
  Say which you did for each claim.
- **Beware leading questions.** A summarizer asked "does this paper support X?" will tend to answer
  yes. Ask neutral questions, and prefer reading the text yourself.
- Record, for each source: identifier (arXiv id / DOI), version, date, venue, and whether you read
  the abstract, the relevant section, or the whole paper.
- Distinguish **established** from **not falsified**. "I searched and did not find it" is a
  statement about your search, not about the literature; report your queries so the claim can be
  reproduced and attacked.
- Where you disagree with the prior scan, say so plainly. A refutation of C2, C3 or C9 is the most
  valuable thing you can return — it would materially shrink what this program can claim.

---

## 5. Prohibitions

- Never invoke any Task 4F1 execution candidate with `--mode run` or `--mode finalize`; never call
  `run_archives`, `evaluate_archive` or `finalize_results`; never set `V52_T4F1_AUTH_HMAC_KEY_HEX`
  or construct an authorization; never access any Task 4F1 (BEAM) retrieval outcome. Task 4F1 is
  `BLOCKED`, outcome access is `FORBIDDEN`.
- Do not modify any sealed artifact, execution candidate, manifest, pinned corpus, historical audit
  namespace, or any research artifact on `research/v52-sign-mechanism-locomo-2026-09-04`. This is a
  scan; it writes only its own report.
- Do not run experiments. If the scan suggests one, propose it; do not execute it.
- Do not bypass paywalls or access controls.

---

## 6. Output

```
branch  research/v52-sign-mechanism-literature-scan-2026-09-04
files   research/v52/literature/LITERATURE_SCAN_REPORT.md
        research/v52/literature/CLAIMS_TABLE.md        (C1-C9: CONFIRMED / REFUTED / PARTIAL / NOT ESTABLISHED, with the evidence and how you read it)
        research/v52/literature/SEARCH_LOG.md          (every query, engine, date, and what it returned)
        research/v52/literature/BIBLIOGRAPHY.md        (identifier, version, venue, date, access level reached)
        plus a .sha256 sidecar for the report
```

The report must contain:

1. a **novelty assessment** that separates *construction* prior art from *ablation-use* prior art,
   and states plainly which of our three facts are already known;
2. the **strongest published claim that competes with ours**, stated in its authors' terms;
3. an explicit **"what I could not access"** section;
4. your resolution of the arXiv 2605.17524 version discrepancy;
5. a one-paragraph statement of **the narrowest claim our result can defensibly support** after your
   scan — written so that a hostile reviewer could not widen it.

Do not overstate. A scan that returns "most of this is already known, here is the one sentence that
survives" is worth more to this program than one that returns a novelty claim we cannot defend.
