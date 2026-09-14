[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# CONTRADICTION.md — arXiv 2606.29571 investigation

Paper: "Anisotropy Decides Cosine vs. Rank Metrics for Text Embeddings",
V. S. Raghu Parupudi, UC San Diego, arXiv:2606.29571v1 [cs.CL], 2026-06-28.
Fetched and read: landing page + full text (HTML) — status VERIFIED.
Evidence: `evidence/arxiv_2606_abs.html`, `evidence/arxiv_2606_html.html`,
`evidence/arxiv_2606_txt.txt` (plain-text extraction).

## 1. The relayed summary was accurate

The abstract (quoted verbatim from the fetched page) matches the second-hand
summary on every checkable point: 19 metrics x 19 encoders x 7 datasets;
cosine best when variance is spread; rank/L1-type metrics win under
anisotropy; "fraction of variance held by the single most dominant dimension"
as the one-number diagnostic; rank correlation 0.86, linear correlation 0.95;
project-out control that works "only on the encoders that were anisotropic to
begin with"; directional-not-magnitude (survives unit-length normalization).
No misrepresentation found in the relay.

## 2. The decisive number: the paper's reported f1 RANGE

The diagnostic is named **rogue-dimension dominance**: "the share of the total
variance held by the single biggest-variance dimension" (basis-dependent,
computed on raw coordinates; a principal-component version is also reported
and "predicts almost as well"). Full Table 1 (rogue values, VERIFIED from
full text), sorted high to low:

| Encoder | Rogue | | Encoder | Rogue |
|---|---|---|---|---|
| GPT-2 | 0.411 | | mBERT-base | 0.005 |
| Qwen2.5-7B | 0.150 | | SFR-Embedding-Mistral | 0.005 |
| Qwen2.5-1.5B | 0.141 | | all-MiniLM-L6 | 0.004 |
| ELECTRA-base | 0.101 | | paraphrase-mpnet | 0.004 |
| RoBERTa-base | 0.084 | | all-MiniLM-L12 | 0.004 |
| Pythia-410M | 0.059 | | all-mpnet-base | 0.003 |
| Mistral-7B | 0.032 | | BGE-base | 0.003 |
| E5-Mistral-7B | 0.026 | | multilingual-E5-large | 0.002 |
| BERT-base | 0.015 | | E5-large | 0.002 |
| (threshold) | **0.010** | | BGE-large | 0.002 |

Range: **0.002 – 0.411**. Crowded/anisotropic = rogue > 0.01 (9 encoders);
well-spread = below (10 encoders).

**Local f1 values 0.0459–0.0843 fall INSIDE the paper's crowded band** —
between E5-Mistral (0.026) and RoBERTa-base (0.084); near Pythia-410M (0.059)
and Mistral-7B (0.032). By the paper's own threshold every one of the four
local corpora counts as *anisotropic/crowded*, not isotropic.

Consequence: the local hypothesis — "these corpora are NOT anisotropic (top
direction only 4.6–8.4%), whereas the paper's encoders are far more
concentrated" — is **wrong under the paper's own definition**. Only GPT-2
(0.411) and the Qwen models are "far more concentrated"; six of the paper's
nine crowded encoders live at 0.015–0.101, exactly the local range. The
non-replication cannot be explained by "outside the paper's regime".

## 3. Verdict: (a) scope limit + (c) diagnostic/dosage mismatch — NOT (b)

**(a) Scope limit the paper effectively states.** The paper varies the
ENCODER (19 encoders, geometry pooled over all datasets per encoder) and
never varies the corpus holding the encoder fixed; its §6 Limitations state
encoders are mostly English and datasets short text, and the conclusion
restricts the claim to "across nineteen encoders". A cross-encoder
correlation of +0.95 licenses no prediction about cross-corpus correlation
within one fixed TF-IDF+SVD encoder. Further, the estimands differ on every
axis: their metric family is rank-based/L1 (Spearman-vector +0.053,
Canberra +0.051, Bray-Curtis, L0.5, Manhattan) over cosine on STS/paraphrase/
inference Spearman; the local estimand is *whitened-cosine* over cosine on
FR@3 memory retrieval. The paper never tests whitening/standardization as a
competitor at all — whitening (Su et al. 2021; Huang et al. 2021) is discussed
only as a "parallel line" that "repairs the space", explicitly set aside
("We instead hold the embeddings fixed and study the metric"). Neither does
it test any binary/sign/Hamming metric (full 19-metric list confirmed; no
sign, Hamming, or binarization entry). Expecting its +0.95 to transfer to a
whitening-gain-vs-f1 correlation across 4 corpora was never licensed.

**(c) Misreading of the diagnostic + weaker control dosage.**
(i) The paper's headline f1 is basis-dependent (raw-coordinate variance
share); the local f1 is a top principal-direction share. The paper says the
principal version "predicts almost as well", so this alone is not fatal, but
the two numbers are not directly comparable, and the comparison the programme
needs (principal-version slope/threshold) is not the headline 0.86/0.95.
(ii) The causal controls differ in dosage: the paper projects out the **top
10** principal directions (removing 1 already cuts the advantage 38%; 10 cuts
it 87%, cosine 0.324 → 0.417) with a random-10-directions control. The local
control removed only the **top 3**. A weaker intervention producing a weaker
attenuation (LME +11.59 → +6.96 is in fact a ~40% cut — same ballpark as the
paper's remove-1 effect of 38%) is dose-response, not non-replication. Only
PerLTQA fully collapsed, which is itself consistent with PerLTQA being the
least whitening-responsive corpus (+1.41) rather than with control failure.

**Statistics note.** r = −0.23 across n = 4 benchmarks is noise (with n = 4
essentially any |r| < 0.95 is non-significant); the informative null is the
+0.06 across 470 LongMemEval archives — a genuine zero, but a zero for a
prediction the paper never made (see (a)).

**(b) Real contradiction: NO.** Nothing in the paper predicts that whitening
gain must correlate with f1 across corpora, or that projecting out 3
directions must erase a whitening advantage. **(d) Local measurement wrong:
cannot be judged from literature**, except that the "not anisotropic" gloss
is refuted by Table 1 above.

## 4. One genuinely adjacent data point from inside the paper

Table 2 (VERIFIED): a **hyperbolic-tangent similarity** (from Parupudi 2025,
included as one of the 19 metrics) scores −0.009 vs cosine on crowded
encoders, −0.000 on well-spread ones — i.e. tanh-flavoured comparison does
*not* beat cosine on STS tasks. This is adjacent to local F3 (tanh soft-clip
beats sign), not a refutation: different construction (tanh as the similarity
vs. tanh as a per-axis soft clip before cosine), different task family.
