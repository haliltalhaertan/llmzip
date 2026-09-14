[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# The published theory of this effect exists, and a discriminating test against it

## The paper

**Wenxuan Xiao, "Covariance Structure and Coordinate Heterogeneity Govern Binary
Quantization of Contrastive Embeddings", arXiv:2605.17524v2, 29 May 2026** (Changsha
University; 21 pages, 18 datasets, 9 embedding families, dimensions 100-3072).
VERIFIED: fetched from arxiv.org/abs/2605.17524 and arxiv.org/html/2605.17524v2 by the
coordinator, independently of the literature session that found it.

Its subject is precisely this programme's open question: *why does binary quantization
work at all, and why do two leading systems (RaBitQ, which rotates to isotropy, and
QuIVer, which preserves coordinate axes) adopt opposite strategies and both succeed?*

Quoted from the abstract (VERIFIED): "coordinate heterogeneity (the non-uniformity of
per-coordinate variances) governs key design choices: how much each additional bit
contributes, and whether random rotation helps or hurts"; "the magnitude bit carries
information proportional to heterogeneity"; "random rotation destroys precisely the
signal that one paradigm exploits while creating the isotropy that the other requires";
"rotation equalizes variances, destroying the implicit weighting that Hamming distance
exploits".

## The tension with this session's story

| | mechanism |
|---|---|
| **This session** | sign quantization EQUALIZES axes: cosine over-weights high-variance axes, Hamming gives every axis one vote. The advantage is implicit whitening. |
| **Xiao (2026)** | Hamming EXPLOITS heterogeneity: high-variance coordinates carry reliable sign bits, low-variance ones are near coin flips. Rotation equalizes variances and destroys that. |

Both use the word "equalization" for opposite readings. Xiao's is about which BITS are
reliable; this session's is about which AXES the SCORE weights.

Two pieces of evidence already on record favoured Xiao before any new test:
- the Haar-rotation cost (-15.93 pp on LongMemEval) was **unexplained** under this
  session's story and is exactly his Corollary 3;
- the preregistered locus test killed "low-variance axes are the sign arm's friend"
  (Delta(bot16) < Delta(top16) on 7 of 8 units).

## The discriminating test (VERIFIED, `research/whitening_2026_09_14/xiao_test.py`)

All four frozen controls reproduced exactly before anything else: LME +10.053783,
PerLTQA -6.274728, REALTALK +5.300077, LoCoMo +6.655046.

**His prediction 1 - rotation equalizes variances and destroys the signal: CONFIRMED 4/4.**

| benchmark | CV(sigma) before | CV after rotation | 1-bit before | after | cost |
|---|---|---|---|---|---|
| LongMemEval | 0.4975 | 0.0853 | 0.542134 | 0.373475 | **-16.87 pp** |
| PerLTQA | 0.5191 | 0.0881 | 0.488945 | 0.465315 | -2.36 pp |
| REALTALK | 0.5222 | 0.1014 | 0.225535 | 0.149579 | -7.60 pp |
| LoCoMo | 0.4877 | 0.0821 | 0.237907 | 0.137912 | -10.00 pp |

Rotation collapses coordinate heterogeneity (CV 0.49-0.52 -> 0.08-0.10) exactly as his
Theorem 2 states, and the sign arm loses on all four. This is a mechanism this session
had measured but could not explain; his theory explains it.

**His prediction 2 - magnitude-bit gain monotone in heterogeneity: FAILS HERE 3/4.**

A 2-bit code (sign bit + magnitude bit at the per-axis median of |C|, 24 B/doc):

| benchmark | CV(sigma) | 1-bit | 2-bit | gain |
|---|---|---|---|---|
| LongMemEval | 0.4975 | 0.542134 | 0.490887 | **-5.12 pp** |
| PerLTQA | 0.5191 | 0.488945 | 0.492322 | +0.34 pp |
| REALTALK | 0.5222 | 0.225535 | 0.179028 | **-4.65 pp** |
| LoCoMo | 0.4877 | 0.237907 | 0.220945 | **-1.70 pp** |

`r(CV, 2bit-1bit gain) = +0.08` across benchmarks; `-0.13` across 30 PerLTQA archives;
`+0.02` across 470 LongMemEval archives. His appendix reports rho = +1.00 on an
intervention ladder.

**Coordinator caveat, stated plainly: this is a failure of MY 2-bit construction, not a
refutation of his theorem.** He does not specify that a magnitude bit must be the median
of |C| with both bits weighted equally in Hamming distance; RaBitQ-style schemes carry
per-vector scalar corrections, and his own formulation may weight or decode the bits
differently. What this test establishes is that the naive 2-bit extension does NOT
transfer to TF-IDF/SVD corpora, where his 9 families are all neural contrastive
embedders. Testing his actual construction requires reading his Section 5 in detail;
that is the next step, not a conclusion.

Note that the magnitude-bit result agrees with an older measurement on this programme's
own record: the AQS arm, which restores query-side magnitude, costs -3.56 pp.

## Verdict

**Both stories are partly right, at different levels, and Xiao's is the published one.**

- At the level of WHICH BITS ARE RELIABLE, Xiao is confirmed here: heterogeneity is
  what the sign code exploits, and destroying it by rotation costs 2.4-16.9 pp.
- At the level of WHICH AXES THE SCORE WEIGHTS, this session's whitening result stands
  as measured (whitened cosine beats plain cosine on 4/4 and subsumes the sign gain),
  but it is a rediscovery of the BERT-whitening line (Su et al. 2021; Huang et al. 2021;
  Jung et al. 2022), not a new mechanism.
- The naive magnitude bit hurts on 3 of 4 benchmarks here, which does NOT match his
  prediction 2 under my construction, and is the one place this data actively
  disagrees with the published account.

**Required disclosure wherever this programme's mechanism claim appears:** the mechanism
was published before this session measured it, in arXiv:2605.17524 for the binary-
quantization side and in arXiv:2103.15316 for the whitening side. This programme's
contribution is reduced to: an independent replication on a different corpus family
(TF-IDF/SVD rather than neural contrastive), the measured failure of the naive 2-bit
extension there, and the scope limits recorded in `SESSION2_FINDINGS.md` (K-dependence,
tie-accounting share, N-independence of boundary occupancy).

## Corrections to this programme's earlier claims, forced by the literature session

1. **"Our corpora are not anisotropic, so the Parupudi diagnostic does not apply" -
   WRONG.** That paper's rogue-dimension range is 0.002-0.411 with the crowded
   threshold at 0.01; local values 0.046-0.084 sit INSIDE its crowded band, near
   RoBERTa (0.084) and Pythia (0.059). The scope defence is withdrawn.
2. **The "failed" causal control was the wrong dose.** The coordinator projected out 3
   directions where that paper removes 10; the local attenuation (LME +11.59 -> +6.96,
   ~40%) matches its remove-1 effect (38%). Dose-response, not non-replication.
3. **The rotation result does not contradict RaBitQ.** In RaBitQ the rotation serves
   the error bound while centroid subtraction plus unit normalization does the
   de-skewing, so a rotation cost here is not evidence against it.
