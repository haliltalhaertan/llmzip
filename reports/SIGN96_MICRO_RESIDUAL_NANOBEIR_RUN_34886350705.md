# SIGN96 micro-residual NanoBEIR post-run report

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## Provenance

- GitHub Actions run: `34886350705`
- Run head: `987152569fdcb0972f9acc3ae0cb0d696daee744`
- Branch: `bench/sign96-micro-residual-2026-09-14`
- Workflow: `.github/workflows/sign96-micro-residual-nanobeir.yml`
- Frozen protocol: `benchmarks/sign96_micro_residual_2026_09_14/PROTOCOL.md`
- 13/13 NanoBEIR task jobs completed successfully; summary job completed successfully.
- Summary artifact ID: `10365555505`
- Summary artifact digest: `sha256:9e0115735be1de586b066982a1b132290721e2ee416bd92d2f55fb86da1d2977`

## Frozen design

All methods use the same centered 96-dimensional V52 representation. FLOAT96 ranks by centered cosine. SIGN96 converts the same 96 coordinates to signs and ranks by Hamming distance.

The residual is corpus-only and relevance-free. Coordinates are ranked by `Var(|C_j|)` across corpus documents. For the selected coordinates, one residual bit records whether `|C_j|` is at least the corpus median for that coordinate. Query residual bits use the same corpus-derived coordinate list and thresholds.

The primary candidate was frozen before outcomes as `SIGN96_R8`: 96 sign bits plus 8 residual magnitude bits = 104 active bits, minimum 13 byte-aligned packed bytes. `R4` and `R16` were frozen as secondary dose-response controls.

Residual bits are only a tie-break. Ranking is lexicographic: base SIGN96 Hamming distance first, residual Hamming distance second, relevance-independent SHA-256 nuisance priority third. Therefore residual information cannot overturn a strict base-Hamming advantage.

All rankings for FLOAT96, SIGN96, R4, R8 and R16 were written to disk and SHA-256 frozen before qrels were loaded.

## Macro results across 13 frozen NanoBEIR tasks

| Method | Min byte-aligned active bytes | Recall@3 Δ vs FLOAT96 | W/T/L vs FLOAT96 | Recall@3 Δ vs SIGN96 | nDCG@10 Δ vs FLOAT96 | nDCG@10 Δ vs SIGN96 | Exact-code collision fraction | Top-3 boundary tie rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SIGN96 | 12 | +2.472 pp | 8/0/5 | +0.000 pp | +1.770 pp | +0.000 pp | 2.233% | 39.739% |
| SIGN96_R4 | 13 | +2.581 pp | 9/0/4 | +0.108 pp | +2.048 pp | +0.278 pp | 2.226% | 18.163% |
| **SIGN96_R8 (frozen primary)** | **13** | **+2.586 pp** | **8/1/4** | **+0.113 pp** | **+2.249 pp** | **+0.478 pp** | **2.216%** | **14.474%** |
| SIGN96_R16 | 14 | +2.328 pp | 7/1/5 | -0.144 pp | +1.984 pp | +0.214 pp | 2.201% | 9.394% |

Versus base SIGN96, R8 improved Recall@3 on 8 tasks, tied on 1 and worsened on 4. For nDCG@10, R8 improved 10 tasks and worsened 3.

On the five tasks where base SIGN96 lost Recall@3 to FLOAT96, R8 improved four, worsened zero and left one unchanged. Mean improvement on those five tasks was +0.509 pp.

## Per-task Recall@3 deltas versus FLOAT96

| Task | SIGN96 | R4 | R8 primary | R16 |
|---|---:|---:|---:|---:|
| NanoArguAna | -5.700 | -3.300 | -4.200 | -4.000 |
| NanoClimateFEVER | -1.767 | -1.167 | -1.167 | -1.167 |
| NanoDBPedia | +1.203 | +1.193 | +1.204 | +1.193 |
| NanoFEVER | +4.033 | +1.333 | +3.333 | +3.333 |
| NanoFiQA2018 | +2.981 | +3.594 | +4.044 | +3.378 |
| NanoHotpotQA | +7.200 | +8.350 | +7.650 | +7.000 |
| NanoMSMARCO | +0.400 | +2.000 | +0.000 | +0.000 |
| NanoNFCorpus | -0.685 | -0.673 | -0.639 | -0.706 |
| NanoNQ | -3.000 | -3.000 | -3.000 | -3.000 |
| NanoQuoraRetrieval | +9.033 | +8.200 | +8.200 | +7.833 |
| NanoSCIDOCS | -0.300 | +0.040 | +0.100 | -0.460 |
| NanoSciFact | +18.100 | +16.575 | +17.075 | +16.000 |
| NanoTouche2020 | +0.640 | +0.401 | +1.011 | +0.865 |

## What the experiment actually says

The user's proposed idea — add a tiny amount of extra information to distinguish items that SIGN96 treats as tied — works modestly in this first frozen implementation. The frozen 8-bit residual increases macro Recall@3 by only +0.113 pp over SIGN96, but increases macro nDCG@10 by +0.478 pp and improves ranking on 10 of 13 tasks by nDCG@10.

The main effect is not removal of exact duplicate 96-bit codes. Exact-code collision fraction changes only from 2.233% to 2.216% with R8. In contrast, the top-3 boundary tie rate falls from 39.739% to 14.474%. Thus the more important bottleneck appears to be large Hamming-distance shells / boundary ties: many distinct binary codes can still sit at the same Hamming distance from a query.

This also falsifies a simple collision-only explanation of SIGN96's earlier gains. NanoSciFact has zero exact-code collision under SIGN96 while SIGN96 beats FLOAT96 by +18.1 pp Recall@3; adding R8 actually reduces that advantage by 1.025 pp. Therefore exact duplicate codes are neither necessary for the large SIGN96 gain nor a sufficient explanation of the phenomenon.

More residual information is not monotonically better. R16 reduces the top-3 tie rate further, to 9.394%, yet worsens macro Recall@3 by 0.144 pp relative to SIGN96. This is consistent with the hypothesis that restoring too much magnitude information can reintroduce nuisance variation that sign binarization had discarded, though this experiment does not prove that mechanism.

The strongest licensed conclusion is therefore: a very small relevance-free secondary magnitude sketch can resolve a substantial fraction of Hamming boundary ties and modestly improve ranking, but the naive global median residual is not a universal cure and does not explain the main SIGN96 phenomenon.

## Next research target

The next candidate should remain outcome-blind and preserve SIGN96 as the primary key, but make the secondary sketch specifically target Hamming-shell ambiguity rather than simply selecting globally high-variance magnitude coordinates. A 4-8 bit corpus-only tie-aware secondary sketch is a natural next experiment. It should be developed without qrels and then tested on held-out full BEIR / BRIGHT / BIRCO tasks.

## Boundaries

- Exploratory run, not Task4F1.
- Not an external independent reproduction.
- No novelty claim.
- `12`, `13` and `14` byte figures are minimum byte-aligned active-code sizes only; they do not include shared projector/vectorizer/index/static state.
- Results are NanoBEIR results and should not be treated as full-corpus effect sizes.
