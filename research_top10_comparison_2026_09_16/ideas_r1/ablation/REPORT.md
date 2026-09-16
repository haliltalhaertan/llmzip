# LSA-channel ablation pilot — RealTalk only

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

**Hypothesis under test (not confirmed):** LSA32 is derived from the word-tfidf
channel, so `Z = [LSA32 | word | char]` may double-count general topic similarity
and outvote the detail that distinguishes the answer. Removing it could improve
ranking and cut cost.

**Verdict on THIS benchmark: directionally supported, statistically inconclusive.**
NO_LSA is the best arm in all 6 metric × scorer cells, but every NO_LSA-vs-FULL
95% paired archive-clustered bootstrap CI includes zero. **RealTalk alone
(10 archive clusters) cannot settle the hypothesis — do not cite, do not ship on
this; replicate on PerLTQA/LME before any production decision.**

## Fidelity gate (see FIDELITY_GATE.json, written before ablation ran)

- **G1 PASS:** rebuilt FULL `sign(C)` vs cached `sign(C)`: **0 differing bits out
  of 858,624**, max abs float diff exactly 0.0, all 10 archives. QC rows compared
  by qid (see exclusions note): 0 sign diffs. Question texts and gold rows verified
  identical to cache for all 705 matched qids. Seeds exactly 5101 (LSA32) / 5204
  (SVD96), via the frozen module imported read-only.
- **G2 qscale PASS:** rebuilt FULL = Hit@10 **49.6454%** (= 350/705), FR@3
  **22.4099%** (→ 22.41%) — exact match to the coordinator reference.
- **G2 sym literal MISMATCH, diagnosed (criterion NOT changed):** rebuilt det-rule
  Hit@10 = **46.5248%** (328/705) vs reference 46.6809%. Root cause is in the
  reference label, not the rebuild: scoring the **cached** codes directly gives
  det-rule 46.5248% and exact expected-Hit@10-under-uniform-ties **46.6809%**.
  Arithmetic proof: 46.6809% × 705 = 329.1 queries — no deterministic top-10 rule
  over 705 binary outcomes can produce it (neighbours 329/705 = 46.6667%,
  330/705 = 46.8085%). **The sym reference is the expected-Hit@10 value,
  reproduced to 4 decimals; coordinator to confirm/rename.** Ablation contrasts
  remain comparable (G1 bit-exactness + identical scoring code across arms).

## Results (RealTalk only, n = 705; never averaged across benchmarks)

| arm | scorer | Hit@10 | FR@3 | Hit@3 | exp-Hit@10 |
|---|---|---|---|---|---|
| FULL | sym | 46.5248 | 22.8676 | 30.0709 | 46.6809 |
| FULL | qscale | 49.6454 | 22.4099 | 29.5035 | 49.6454 |
| NO_LSA | sym | 48.0851 | 24.0502 | 30.9220 | 47.7929 |
| NO_LSA | qscale | **52.0567** | **25.8543** | **33.9007** | 52.0567 |
| NO_CHAR | sym | 42.1277 | 20.6869 | 26.5248 | 42.2822 |
| NO_CHAR | qscale | 43.8298 | 21.2328 | 27.2340 | 43.8298 |
| WORD_ONLY | sym | 43.6879 | 20.1802 | 26.0993 | 43.9461 |
| WORD_ONLY | qscale | 46.2411 | 22.1265 | 28.7943 | 46.2411 |

(values in %; per-archive breakdown in RESULTS.json; per-query replay in
per_query.jsonl, 5640 rows = 705 q × 4 live arms × 2 scorers, replay-verified to 1e-9)

Contrasts vs FULL in percentage points, paired archive-clustered bootstrap
(20000 reps, seed 20260916; 10 clusters → wide, exploratory):

- NO_LSA − FULL / qscale: Hit@10 **+2.41 [−0.28, +5.15]**, FR@3 **+3.44
  [−0.56, +7.56]**, Hit@3 **+4.40 [−1.22, +9.96]** — all positive, all cross zero.
- NO_LSA − FULL / sym: Hit@10 +1.56 [−1.95, +5.07], FR@3 +1.18 [−1.00, +3.50],
  Hit@3 +0.85 [−2.40, +4.02] — same pattern, smaller.
- NO_CHAR − FULL / qscale: Hit@10 −5.82 [−8.85, −2.76] (clearly harmful);
  WORD_ONLY − FULL / qscale: Hit@10 −3.40 [−5.36, −1.63] (harmful).
- Reading: the **char** channel carries distinguishing detail (removing it hurts
  badly); the **LSA** channel looks redundant (removing it helps everywhere, but
  not significantly). LSA is only 32 of ~23–33k Z columns, so this is a weighting
  effect through the final SVD, not a capacity effect.

## Cost (decides cost, not quality)

- Payload per document: **12 B for every live arm** (confirmed via packed shape
  (N, 12)) — expected, since the bottleneck is the fixed 96-dim sign code.
- Z widths (per archive): FULL 23,422–33,257; NO_LSA −32 cols (~0.1%);
  NO_CHAR ≈ 7.7–9.9k (~1/3 of FULL).
- Index build time (10-archive total): FULL 9.4 s, NO_LSA 11.0 s, NO_CHAR 3.5 s,
  WORD_ONLY 3.6 s. Dropping LSA saves **no** build time or bytes (noise-level);
  dropping char saves ~3× build time but destroys quality. **No cost case for
  removing LSA; only a (currently non-significant) quality case.**

## Exclusions and blockers (nothing dropped quietly)

1. **23 queries excluded, count and reason pre-declared:** canonical export holds
   705 valid of 728 cached queries; the 23 cached-only qids exactly match
   `data/exclusions.json` (n_total 728 / n_valid 705 / n_excluded 23). One
   excluded query has empty gold (crashed a 728-query diagnostic with
   ZeroDivisionError — consistent with the validity filter, not touched further).
   Zero additional exclusions: all 705 valid queries scored in every live cell.
2. **LSA_ONLY arm BLOCKED (impossible under protocol, not worked around):**
   Z would be 32 wide < final SVD96 dim; the task's own `assert min(Z.shape) >
   96` fired on every archive before any score was computed. No numbers invented
   for it. Consequence: the "is LSA sufficient alone?" half-question is
   unanswerable at fixed 96 dims.
3. **Sym reference label** (above): needs coordinator confirmation; det-rule sym
   numbers in this report use the shared tie rule exactly.

## Files

`ablation.py` (runnable: `$HOME/muse-work/ml-python ablation.py`),
`FIDELITY_GATE.json`, `per_query.jsonl`, `RESULTS.json`, this `REPORT.md`.
Frozen builder and audit lib imported read-only, never modified; no input file
written; no network/pip/git used.
