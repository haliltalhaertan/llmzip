[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# REPORT.md — literature search summary

Network verified live 2026-09-14 (Crossref + OpenAlex + EuropePMC + arXiv
landing/full-text fetches all returned real data; arXiv API, OpenAlex
search, and Semantic Scholar hit rate limits — substitutes used throughout).
All citations below were fetched; nothing is cited from memory. Raw evidence
in `evidence/` (≈20 files: API JSON, abs pages, full-text HTML/TXT, PDFs).

## Which of F1–F4 are already published?

- **F1 (sign beats cosine 3/4, loses PerLTQA): exact form NOT FOUND.**
  Adjacent: Xiao (2026) shows BQ effectiveness is distribution-dependent
  (competitive on contrastive embeddings, fails on others) — a sign flip in
  *whether BQ works*, but not binary *beating* float. No PerLTQA-style
  reversal found.
- **F2 (whitening subsumes the sign advantage; sign = crude variance
  equalization): interpretation ALREADY PUBLISHED, quantification NOVEL.**
  Xiao (2026), arXiv:2605.17524, VERIFIED in full text: "rotation equalizes
  variances, destroying the implicit weighting that Hamming distance
  exploits." The head-to-head numbers (whitened float beats/ties sign on all
  four; 44–86% of whitening gain at 1/32 storage) were not found anywhere.
  The whitening line itself (Su et al. 2021, WhiteningBERT 2021, Jung et al.
  2022 — all VERIFIED) never mentions binarization: the gap the programme
  thought it found is real **as a comparison**, but the *mechanism* is taken.
- **F3 (interior clip beats both endpoints): NOT FOUND.** Nearest point is a
  weak negative (tanh-similarity −0.009 vs cosine, Parupudi 2026 Table 2,
  different construction and task).
- **F4 (alpha knob; ±20/−12 pp query-type split): NOT FOUND.** Nearest:
  Xiao's partial-whitening alpha probe (causal probe, not a query contrast).

## Verdict on the contradiction (arXiv 2606.29571)

**(a) scope limit + (c) diagnostic/dosage mismatch — not a real
contradiction.** Full case in CONTRADICTION.md. Three sentences:
(1) The paper varies the *encoder* and never tests whitening or any
binary/sign metric, so it predicts nothing about cross-*corpus* whitening
gains — the +0.95 was applied outside its stated scope.
(2) The local "not anisotropic" gloss is refuted by the paper's own Table 1:
rogue range 0.002–0.411, crowded threshold >0.01, and all four local f1
values (0.046–0.084) sit inside the crowded band near RoBERTa (0.084) and
Pythia (0.059).
(3) The "failed" control removed 3 directions where the paper removes 10
(38% cut at 1, 87% at 10) — and the local LME attenuation (+11.59 → +6.96,
≈40%) matches the paper's remove-1 effect almost exactly.

## Single most important paper to read

**Xiao, Wenxuan (2026). "Covariance Structure and Coordinate Heterogeneity
Govern Binary Quantization of Contrastive Embeddings."
arXiv:2605.17524.** https://arxiv.org/abs/2605.17524 — it publishes F2's
mechanism, explains the local rotation cost (−15.93 pp) as theory predicts
(rotation equalizes variances → destroys Hamming's implicit weighting),
anticipates the alpha knob, and frames the exact BQ-vs-rotation design
choice the programme stumbled into. Read it before writing a word.

## Recommended disclosure line for any write-up

"Sign-quantization-as-implicit-variance-equalization was independently
described by Xiao (2026) for contrastive embeddings and ANN fidelity; our
contribution is the quantified head-to-head against explicit whitening
(which subsumes the sign gain) on TF-IDF+SVD memory retrieval, plus the
interior-clip optimum and the query-type alpha split, for which we found no
published antecedent. Against Parupudi (2026): no contradiction — different
axis of variation (corpus, not encoder), different metric family
(whitening, not rank/L1), and our corpora sit inside that paper's crowded
regime (rogue 0.046–0.084 vs. its 0.01 threshold)."
