# Muse session — ROADMAP BRAINSTORM (strategy & prioritization)

You are an independent strategy advisor to a research programme. Read the briefing below, the
pointers, then **brainstorm and propose a prioritized roadmap**. This is a judgment task; be
opinionated, concrete, and honest about uncertainty. Read-only; scratch /tmp/roadmap/. No network.

## Briefing — the programme

**llmzip** studies compact long-term memory retrieval for LLM/agent systems: keep a very small
"routing code" for each memory document while preserving evidence retrieval. Frozen architecture
"V52": each document → float96 vector → centered sign code. **Native SIGN96 = 96 bits = 12 bytes**
(candidates: 384-byte float96). Retrieval = Hamming top-3 on codes; primary metric =
**Fractional Evidence Recall@3** (share of gold evidence docs inside the returned top-3, averaged
over questions). Chance ≈ 0.6%. Frozen anchors: LongMemEval-470 native **54.1975%**;
LoCoMo-1535 native **23.6547%**. Programme style: preregistration, seals, gates, independent
reviews, tolerance bands of 0.5/1.0/2.0 pp for compression decisions. Task 4F1 (BEAM scale-up) is
SEALED/BLOCKED — no outcome access. A NOES list forbids, without new preregistration: alternate
bit widths as programme claims, whitening, PCA/learned rotations, variance reweighting, learned
thresholds, reranking, supervised rotation, etc. Everything below is LOCAL EXPLORATORY — no push.

## Accepted frozen findings (programme)

- ITQ-family compression below 96 bits FAILED on LongMemEval.
- Centered SIGN96 BEATS float96 (+10.0 pp) and ITQ96 (+16.6 pp) on the frozen benchmark.
- Coordinate MIXING (Haar/block rotations) destroys retrieval: −15.9 pp LME, −9.9 pp LoCoMo;
  continuous geometry is preserved — the effect is a "native axis-structure" phenomenon.
- Cross-benchmark directional replication on LoCoMo. Variance-heterogeneity mediator: NOT established.

## Verified pilot findings (rounds 1+2, all independently recomputed EXACT)

Full reports: /mnt/c/Users/MDP/dev/llmzip-work/pilots/axis_attack_2026-09-12/REPORT.md and
.../round2/ROUND2_REPORT.md (read them for details).

1. **Budget curve (LME, simple subsets of native bits, gold-free):** 10 B ≈ 51.5 (−2.7 pp),
   8 B ≈ 48.3 (−5.9), 6 B ≈ 45.0 (−9.2, 5 seeds), 4 B ≈ 37 (−17), 2 B ≈ 20 (−34), 1 B (top-8) ≈ 9.
   LoCoMo: 10 B ≈ 23.5 with the *bottom*-variance subset (−0.1 pp), 8 B ≈ 21.7 (−1.9), 6 B ≈ 18.1.
2. **Variance-order is anti-optimal on BOTH benchmarks:** top-48-variance loses ~10 pp vs random
   48 on LME (W/T/L 91/179/200) and is the worst arm at every k on LoCoMo; random ≈ uniform-spread
   ≈ best on LME. Nuance: on LoCoMo the bottom tail is best; on LME spread/random win.
3. **Separation paradox:** top-48 wins every mean-distance statistic yet loses retrieval —
   decided by fine tie structure, not mean separation. Mechanism: OPEN.
4. **Per-axis structure:** all 96 axes carry weak positive gold-discrimination (delta ≥ 0.066);
   no single axis is load-bearing (30/96 drop-loss ≤ 0); information spread across axes; decisive
   questions appear to hinge on low-variance axes (descriptive).
5. **Mixing dose-response (block-2, 5 seeds, same rotations/different pairing):** damage monotone
   in variance disparity — matched-variance pairing ≈ native on LoCoMo (−0.04 pp), random −2.4,
   maximally-disparate −4.3 (LME: −1.6 / −3.8 / −5.4).
6. **Learned selection (train/test split 239/231, LME):** train-only utility "mean drop-loss"
   top-64 beats random64 on held-out questions: best-seed margin +1.62 pp (vs-mean +3.39);
   a second arm (alone-norm top-64) +0.39; pure variance control WORST at every k (replicates
   out-of-sample). Modest effect; single split; seed spread 3.34 pp at k=64.
7. Untested: sub-8-bit regimes, heterogeneous-precision codes, RaBitQ/PQ-family codecs under a
   total-bytes budget (a twelve-byte-budget arm set was designed in the programme but NOT run),
   non-frozen embedders, cross-benchmark utility transfer.

## Your task

Produce a **prioritized roadmap** (6–18 months of compute pace, but recommend what to do FIRST):

1. **Rank the candidate directions** below and argue why; refine/replace them if you see better:
   (a) multi-split robustness of the learned-selection premium; (b) formalize + preregister a
   twelve-byte budget experiment (native vs spread/random subsets vs learned selection vs
   RaBitQ-family); (c) mechanism deep-dive incl. a gold-free "failure predictor" for small budgets
   and possible per-question adaptive strategies; (d) heterogeneous-precision bit allocation and
   sub-8-bit exploration; (e) cross-benchmark utility transfer + embedder generality.
2. **Add directions we missed** (the programme rewards being right about the *scientific* story,
   not just the engineering; consider: what would make a reviewer say "that's the real result"?).
3. For your **top 3**, give the sharpest CHEAP experiment design: arms, controls, gates,
   kill criteria, what result would kill or promote the direction.
4. **Preregister vs keep exploratory:** which of these must be preregistered (and with what pilot
   disclosure), which should stay exploratory pilots.
5. **Risks & falsifiers:** what would falsify the pilot findings; failure modes of the plan;
   anything in the NOES/4F1 space to avoid touching.
6. **Sequencing:** dependencies, what runs in parallel, what the single most important next
   experiment is.

Output: a single structured markdown report (headings per section above), with concrete numbers
where possible. State your confidence levels and any assumptions openly.
