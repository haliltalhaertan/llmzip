[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# ALREADY_KNOWN.md — findings with published matches

Label key: VERIFIED = fetched and read in full text or abstract by this
search. CLAIM = from a fetched abstract only. All URLs below were fetched.

## A. F2 interpretation ("sign quantization is implicit, crude, lossy variance equalization") — EXACT interpretive match

**Xiao, Wenxuan (2026). "Covariance Structure and Coordinate Heterogeneity
Govern Binary Quantization of Contrastive Embeddings." arXiv:2605.17524
(2026-05-17).** https://arxiv.org/abs/2605.17524 — VERIFIED (abstract +
full text; `evidence/abs_2605_17524.html`, `evidence/html_2605_17524.html`,
`evidence/xiao_txt.txt`).

The paper's framework, in its own words (full text): "coordinate
heterogeneity (the non-uniformity of per-coordinate variances) governs ...
why rotation helps one system but hurts another (**rotation equalizes
variances, destroying the implicit weighting that Hamming distance exploits**
while creating the isotropy that linear correctors require)."
And: "Heterogeneity determines ... how much the magnitude bit adds".
The abstract: "random rotation destroys precisely the signal that one
paradigm exploits while creating the isotropy that the other requires."
It also runs a **partial-whitening intervention** (Appendix H): rescaling
per-coordinate standard deviations toward their mean with
alpha in {0.25, 0.50, 0.75, 1.0}, then re-normalizing to the unit sphere.

- Match to F2: **exact at the interpretation level** — Hamming-over-signs
  carries an implicit per-axis variance weighting, and equalizing variances
  destroys exactly what Hamming exploits. This is the local programme's
  claimed mechanism, published.
- Gaps preserving novelty: different setting (InfoNCE contrastive embeddings,
  Gaussian-model ANN ranking fidelity, 1–2 bit BQ, 18 datasets x 9 embedding
  families) — NOT TF-IDF+SVD memory retrieval; no head-to-head
  whitened-cosine-vs-sign comparison; no "whitening accounts for the entire
  sign advantage" quantification; no 12-bytes-vs-384-bytes result.
- Also relevant to F4: the alpha-parameterized partial-whitening probe is an
  adjacent antecedent of the axis-weight knob (different use: causal probe,
  not a query-type split instrument).
- Also relevant to F1/reversal: "BQ achieves competitive recall on
  contrastive embeddings but fails on others" — a published
  distribution-dependent sign flip in BQ *effectiveness* (CLAIM from fetched
  abstract; full text confirms the puzzle framing), though framed as
  parity-vs-failure, not binary *beating* float.

## B. Whitening line exists and improves cosine — but NEVER compares against binarization (gap VERIFIED, three papers)

1. **Su, Jianlin; Cao, Jiarun; Liu, Weijie; Ou, Yangyiwen (2021).
   "Whitening Sentence Representations for Better Semantics and Faster
   Retrieval." arXiv:2103.15316 (2021-03-29).**
   https://arxiv.org/abs/2103.15316 — VERIFIED (abstract + full text;
   `evidence/abs_2103_15316.html`, `evidence/html_2103_15316.html`).
   Full-text keyword scan: binar 0, quantiz 0, hamming 0 ("sign" hits are
   only "design/assign"). No comparison against, or remark about, binary
   quantization anywhere. (Adjacent note: it does claim reduced "storage
   cost" via dimensionality reduction — not via quantization.)
2. **Huang, Junjie; Tang, Duyu; Zhong, Wanjun; Lu, Shuai; Shou, Linjun;
   Gong, Ming; Jiang, Daxin; Duan, Nan (2021). "WhiteningBERT: An Easy
   Unsupervised Sentence Embedding Approach." Findings of EMNLP 2021.**
   DOI 10.18653/v1/2021.findings-emnlp.23 — VERIFIED metadata via Crossref
   (`evidence/crossref_wbert_full.json`); content via publisher PDF
   (`evidence/wbert.pdf`). PDF string scan: binar 0, quantiz 0, hamming 0.
   No binarization comparison.
3. **Jung, Euna; Park, Jungwon; Choi, Jaekeol; Kim, Sungyoon; Rhee, Wonjong.
   "Isotropic Representation Can Improve Dense Retrieval." arXiv:2209.00218
   (2022).** https://arxiv.org/abs/2209.00218 — VERIFIED (abstract + full
   text; `evidence/abs_2209_00218.html`, `evidence/html_2209_00218.html`).
   Full-text scan: binar 0, quantiz 0, hamming 0. Tests Normalizing Flow +
   whitening for ColBERT/RepBERT re-ranking only.

## C. RaBitQ: rotation is for the error bound, NOT a whitening substitute; centering+normalization is the de-skewing step (adjacent, clarifies the local rotation result)

**Gao, Jianyang; Long, Cheng (2024). "RaBitQ: Quantizing High-Dimensional
Vectors with a Theoretical Error Bound for Approximate Nearest Neighbor
Search." Proc. ACM on Management of Data (SIGMOD) 2024.**
DOI 10.1145/3654970; preprint arXiv:2405.12497 (2024-05-21).
https://arxiv.org/abs/2405.12497 — VERIFIED (abstract + full text;
`evidence/abs_rabitq.html`, `evidence/html_rabitq.html`,
`evidence/rabitq_txt.txt`).

- Pipeline (VERIFIED from full text): subtract data centroid c, normalize to
  unit vectors, THEN apply random orthogonal rotation P, then 1-bit
  quantization with a dedicated estimator. Setting is Euclidean ANN with a
  provable error bound on inner products.
- Skewness is removed by the **centering+normalization** step ("the
  normalized data vectors are expected to spread evenly on the unit
  hypersphere, removing the skewness of the data (if any) to some extent") —
  not by rotation. Rotation's stated role is making P^{-1}o uniform on the
  sphere so the estimator's error bound holds (Lemma B.1 machinery).
- RaBitQ never claims rotation *improves recall* over no rotation; it claims
  an error bound and beating PQ at equal memory. So the local −15.93 pp Haar
  rotation cost does not contradict RaBitQ: different objective (bound vs.
  retrieval accuracy), different estimator (corrected 1-bit code vs. plain
  Hamming on signs), and RaBitQ always rotates *centered unit-normalized*
  vectors. Adjacent, not contradictory.
- Note: the task brief's phrasing ("1-bit quantization suffered severe
  recall degradation on non-isotropic distributions") appears nowhere in
  RaBitQ's text (full-text scan: "isotrop" occurs once, inside a cited
  reference title). Treat that phrasing as second-hand; the verified
  adjacent claim is Xiao (2026) §A above.

## D. The 2606.29571 paper itself (constraints that bind the programme)

**Parupudi, V. S. Raghu (2026). "Anisotropy Decides Cosine vs. Rank Metrics
for Text Embeddings." arXiv:2606.29571v1 [cs.CL] (2026-06-28).**
https://arxiv.org/abs/2606.29571 — VERIFIED (abstract + full text).
Details in CONTRADICTION.md. Two bindings:
(i) it explicitly positions whitening as an untested "parallel line" and
tests NO binary/sign metric — so neither F2's head-to-head nor F1's
sign-vs-cosine exists there; (ii) its Table 2 tanh-similarity result
(−0.009 vs cosine on crowded encoders) is the closest published
tanh-related data point to F3, with a different construction.
