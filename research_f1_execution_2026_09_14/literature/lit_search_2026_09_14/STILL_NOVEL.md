[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# STILL_NOVEL.md — what was NOT found published, with search coverage

All searches below were executed 2026-09-14 from the workspace machine.
Raw responses are in `evidence/`. Services that rate-limited are noted;
each blocked query was retried on at least one alternate service.

## 1. F2 head-to-head (whitened cosine vs. sign Hamming; "whitening accounts for the entire sign advantage") — NOT FOUND

Nobody found compares per-axis standardization followed by cosine against
1-bit sign/Hamming retrieval on the same corpus, let alone shows the former
subsuming the latter's gain. The mechanism is published (Xiao 2026, see
ALREADY_KNOWN.md §A); the *quantified head-to-head* is not.

## 2. F1 exact form (sign Hamming BEATING float cosine on TF-IDF+SVD conversational-memory retrieval) — NOT FOUND

Found: distribution-dependent BQ effectiveness (Xiao 2026: competitive on
contrastive embeddings, fails on others). Not found: any report of 1-bit
signs strictly beating float cosine on the same retrieval task, or the
PerLTQA-style reversal (sign wins 3/4, loses the 4th by 6.27 pp). The
industry framing encountered ("binary retains most of float performance",
i.e. always ≤ float) was not verified against a citable source — it remains
programme lore, NOT a literature claim; do not cite it as such.

## 3. F3 interior-clip optimum (clipped score peaking between cosine and Hamming; tanh(C/sigma) cosine beating hard sign) — NOT FOUND

Nearest published point is a negative: hyperbolic-tangent similarity −0.009
vs cosine on crowded encoders (Parupudi 2026, Table 2, VERIFIED from full
text) — but that is tanh as the similarity function on STS tasks, not a
per-axis soft clip interpolating cosine→Hamming on retrieval. No interior
optimum, no winsorized/clipped-cosine retrieval result found.

## 4. F4 (explicit v_j^(−alpha) knob; 32.75 pp query-type split over identical documents) — NOT FOUND

Nearest: Xiao (2026) Appendix H partial-whitening probe (alpha in
{0.25, 0.50, 0.75, 1.0}, VERIFIED from full text) — used as a causal probe
of heterogeneity, not as a query-type contrast instrument. No report of
opposite-signed alpha effects across query types was found.

## Coverage: searches run (so a reader can judge completeness)

- Crossref `query.bibliographic` + `query.title`: whitening sentence
  embeddings; whitening + isotropy; WhiteningBERT (hit);
  RaBitQ (hit: SIGMOD 2024 record); binary quantization outperforming
  full-precision retrieval (no on-point hits); winsorized cosine similarity
  (no on-point hits); binary quantization + anisotropy (no on-point hits).
- EuropePMC REST: "whitening embeddings" (hits, biomedical only);
  "RaBitQ" (0 hits — expected, out of scope for the index).
- arXiv API (`export.arxiv.org`): rate-limited ("Rate exceeded") on all
  queries attempted — recorded, nothing retrieved that way.
- arXiv HTML search pages (worked): "RaBitQ" (hit: original 2405.12497
  among results); `"binary quantization" embeddings whitening OR isotropy`
  (hit: Xiao 2605.17524); SimHash/anisotropic query (no parseable hits);
  binary-outperforms-float and soft-binarization/clipped queries (no
  parseable result blocks — recorded as no hits in `evidence/as_q3.html`,
  `evidence/as_q4.html`).
- OpenAlex: rate-limited (anonymous search under load, retryAfter 35s);
  Crossref + arXiv-HTML used as substitutes for every blocked query.
- Semantic Scholar API: 429 rate-limited; skipped per brief.
- Direct fetches (all VERIFIED): arxiv abs + full HTML for 2606.29571,
  2103.15316, 2209.00218, 2405.12497, 2605.17524; ACL PDF for WhiteningBERT;
  Crossref records for WhiteningBERT and RaBitQ.

## Honest limits

- No general web search engine was available; discovery ran through
  scholarly APIs + arXiv search. Industry grey literature (vector-DB docs,
  blog recall tables) was not systematically surveyed.
- Full-text keyword scans ("binar/quantiz/hamming" absence) were run on
  fetched HTML/PDF for Su 2021, Jung 2022, and WhiteningBERT — absence
  claims rest on those scans, saved in `evidence/`.
- Xiao (2026) postdates most programme work and is itself recent (May 2026);
  check for newer citations of it before publishing.
