## FINDINGS

| ID | Area | Verdict | Evidence |
|----|------|---------|----------|
| F1 | Protocol math | OK | Codes/threshold/Hamming/met/rh/lexsort/K3/NT20 verbatim |
| F2 | Tie seeds | OK | Formula matches adapter; lex over all 500 qids |
| F3 | Rotation impl | OK | hspec/happly identical incl. QR sign fix |
| F4 | Benign deviations | CAVEAT | 3-of-5 seeds; regen pkls unsealed; dead helper |
| F5 | E0 gate power | CAVEAT | 470/470 to 1e-16, yet blind to variance path |
| F6 | E1 leakage | OK | Variance + fixed RNG only; gold-free verified |
| F7 | E2/E3 gold labels | FAIL | Gold-derived, no per-field analysis-only tag |
| F8 | E4 construction | OK | Variance-matched perm; gold only in metric |
| F9 | Alone-FR tie lottery | CAVEAT | 0.0065–0.0097 unnormalized; ranking = pool size |
| F10 | E4 contrast | CAVEAT | n=3, Q-reuse confound; "halves damage" causal |
| F11 | E1 below-96 scope | CAVEAT | One benchmark/family; thin seeds; noise ≈ gaps |
| F12 | Causal wording | CAVEAT | "Wrong strategy" overgeneralizes; §5 hedges |
| F13 | NOES compliance | OK | Labels present; no citation claims found |
| F14 | IDXSTRIDE64 bug | FAIL | Yields 48 axes, mislabeled as 64-bit |
| F15 | Seed-scatter hiding | CAVEAT | RAND48 mean masks 3.5 pp spread |

Notes on key rows:

- **F1–F3.** `met`, `rh`, `D=(C>=0)`, `count_nonzero(...!=...)`, `lexsort((prio, dist))`, fractional R@3, and the `hspec`/`happly` QR path match the frozen producer's `evalq` block line-for-line. The one structural difference is deliberate subsetting (RSEEDS 43001–43003 of five; disclosed in-script).
- **F4.** Benign but real: inputs are `regen/.../cache_repr` pickles with no hash seal (frozen `verify()` provenance absent); `hspec_qs_only` is dead code; collision/tie helpers (`ct`) not replicated in the main script.
- **F5.** The gate is strong for what it covers (per-question 470/470 plus aggregate to 1.1e-16, ANY/ALL exact, E4 random arm reproduced to 5 dp). It cannot see float-magnitude paths: variance ordering (E1/E4-matched) and QR/BLAS behavior leave sign codes unchanged, so a variance-path bug passes E0 silently.
- **F7.** E1's selection is clean (variance + `default_rng(12000+s)`; no gold). But E2's `alone_top10/bottom10` ranks axes by gold-scored FR, and E3's delta is gold-conditioned by construction — both gold-informed, yet `pilot_results.json` carries only global pilot labels, no per-field `analysis-only` tag. Acceptable substance, failed labeling.
- **F9.** With a 1-bit distance, docs tie at d=0 en masse, so alone-FR ≈ 3/(tie-pool size) when gold agrees. REPORT §2 says "1 bit cannot rank" but never normalizes by pool size; the reported `corr_delta_vs_alone = 0.77` then mostly re-measures agreement-set size, not axis importance.
- **F10.** Matched pairing reuses the same Q blocks with a different perm, which changes both axis grouping *and* Q-to-axis assignment — not a pure variance-matching isolation. n=3 with large scatter (matched gaps −0.31/−1.95/−2.46 pp).
- **F14.** In `pilot_extra_arms.py`, `arange(96)[::2][:64]` yields only 48 axes, so `IDXSTRIDE64 == IDXSTRIDE48` (both 0.44448...). Genuine mislabel bug; REPORT's table omits that arm, limiting damage.
- **F15.** `E1_random_subset.48 = 0.4507` averages seeds spanning 0.4382–0.4729 (3.5 pp). REPORT discloses ±1.5 pp scatter; the JSON alone does not.

## Design verdict

As an exploratory instrument, the pilot is sound: verbatim eval math, a per-question reproduction gate that actually binds the tie pipeline, gold-free construction where it matters (E1, E4 pairing), and diagnostics that already test the leading alternative mechanisms (duplicates, ties, bucket sizes, mean-separation paradox). Its weaknesses are labeling and normalization, not plumbing — the alone-axis ranking is uninterpretable without tie-pool correction, gold-derived E2/E3 fields lack analysis-only tags, and one extra arm is mislabeled — all fixable without rerunning the core.

## Required corrections

- Tag E2 axis rankings and all E3 fields `analysis-only, gold-informed` in the JSON, or move them to a separate gold-informed block.
- Fix or drop `IDXSTRIDE64` (currently a 48-axis duplicate); recompute if a true 64-axis spread arm is wanted.
- Add tie-pool-normalized alone-FR (or publish pool sizes alongside `per_axis.csv`) and caveat `corr_delta_vs_alone`.
- Report seed scatter wherever a mean is given (RAND48 range, not just mean); extend random subsets beyond single seeds before any preregistration claim.
- Soften "variance-ordered selection is the wrong strategy" and "real contributor" to benchmark-scoped descriptive claims.

## Before any preregistration

- Disclose this pilot as the exploratory source (already labeled `[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]` in script, JSON, and REPORT — carry all four forward).
- Approached NOES items requiring preregistration: alternate bit widths (E1 k-subsets as programme claims), variance reweighting/selection (top-k ordering, matched-variance pairing), supervised-selection analogue (E2/E3 gold-ranked axes), extra random seeds (12000+s subset series). Not touched: whitening, PCA rotations, learned thresholds, reranking, alternate distance metrics.
- Carry over limits: single benchmark/family (no LoCoMo, no cross-embedder claim); no learned selection (train/test split correctly deferred to REPORT §6); E4 n=3 with Q-reuse confound — a fresh-Q matched arm and seeds 43004/43005 are the cheapest confirmatory upgrades; per-question W/T/L vs native (currently only vs RAND48-mean) and per-question tie-mass decomposition are the cheapest mechanism upgrades.

