# Muse session — TECHNICAL IDEATION (new codec ideas from the mechanism findings)

You are an independent research ideator. Given the findings below, invent and prioritize CONCRETE
technical ideas that could push the bit-budget-vs-quality frontier further. Be specific and
quantitative where possible; mark speculation as speculation. Read-only; scratch /tmp/ideas/. No
network (flag anything that needs a literature check later).

## Established facts (all verified; details in the pinned reports)

Frozen anchor (retrieval quality = Fractional Evidence Recall@3; chance ≈ 0.6%):
LongMemEval-470 native SIGN96 (12 B) = 54.20%; float96 = 44.16%; ITQ96 = 37.61%; Haar96 = 38.27%.
LoCoMo-1535 native = 23.65%; Haar = 13.77%. Reports:
/mnt/c/Users/MDP/dev/llmzip-work/pilots/axis_attack_2026-09-12/REPORT.md (+ round2/ROUND2_REPORT.md).

Key facts from recent controlled pilots (all gold-free arms unless noted; all independently
recomputed EXACT):

1. **Bit-carrying structure is spread across ALL 96 axes** — every axis has weak positive
   gold-vs-nongold discrimination (min delta 0.066); no single axis is load-bearing (30/96
   drop-loss ≤ 0); per-coordinate variance is NOT a good importance proxy — ranking bits by
   variance is actively harmful.
2. **Subsets:** LME: 10 B ≈ −2.7 pp, 8 B ≈ −5.9, 6 B ≈ −9.2, 4 B ≈ −17, 2 B ≈ −34 vs native;
   random ≈ uniform-spread ≈ best on LME; on LoCoMo the BOTTOM-variance tail is best (10 B ≈ −0.1).
3. **Coordinate mixing destroys retrieval, damage monotone in variance disparity:** block-2
   matched-variance pairing ≈ native on LoCoMo; maximally-disparate pairing −4.3 pp.
4. **Separation paradox:** mean-distance statistics point the wrong way; retrieval is decided by
   fine tie structure at the top-3 boundary (mechanism OPEN).
5. **A learned train-only utility (mean drop-loss) gives a small premium:** +1.6 pp over the best
   of 3 random seeds at 64 bits on a held-out half (single split; modest).
6. **Determinism:** the whole encode chain is bit-reproducible under a pinned stack; codes are
   stable even across library versions in samples.

## Task

Brainstorm **concrete ideas** in these three areas (and any you add):

A) **Codec design under a total-bytes budget** (e.g. targets 4/6/8/12 bytes):
   - heterogeneous precision (different bits per axis under a budget): which allocation rules could
     win given facts 1–3? (e.g. bottom-tail emphasis, entropy-matched allocation, allocation from
     train-only utility, "isotropic spread + a few double-bits")?
   - alternatives to pure sign: 2-bit/3-bit quantization per selected axis? dithered/threshold
     tricks? (note: rotations are known-bad — but per-axis scalar transforms are NOT rotations;
     which scalar families are plausibly safe and why?)
   - combinations with per-question adaptivity ONLY where a gold-free predictor exists.
B) **Mechanism probes** that are cheap on existing frozen matrices: what single analysis would
   most sharpen "why do some questions survive small budgets and others don't"? (e.g. tie-mass
   decomposition at the top-3 boundary; bit-influence curves; effective-dimension measures; sign
   entropy per axis; cluster structure of duplicate codes...)
C) **Robustness/generalization ideas** runnable on existing data: cross-benchmark utility
   transfer, question-type-conditioned selection, split-robustness protocols.

For EACH idea: (i) one-paragraph description; (ii) expected effect size (with reasoning);
(iii) cheapest test design on the existing frozen matrices (arms, gates, kill criteria);
(iv) risk/failure mode; (v) whether it touches programme NOES items (alt bit widths as claims,
whitening, PCA/learned rotations, variance reweighting, learned thresholds, reranking,
supervised rotation) and what its exploratory→preregistration path would be.

End with: your **top-5 ranked ideas** (with a one-line "why this first"), and a list of ideas you
reject and why. Output: one structured markdown report. Confidence labels on every claim.
