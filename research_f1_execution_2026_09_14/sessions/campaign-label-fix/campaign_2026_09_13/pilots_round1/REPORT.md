# AXIS-ATTACK PILOT — exploratory results (2026-09-12)

**Labels: [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**
Computed locally on the frozen LongMemEval 470-question benchmark using the byte-frozen Task4C3
evaluation protocol verbatim. This is an exploratory instrument for the Head Researcher; if any of
these outcomes informs a future preregistration, this pilot must be disclosed with it.

## 0. Protocol fidelity & gates (all PASS)

| Gate | Result |
|---|---|
| Native Fractional R@3 (470, aggregate) | **0.5419751773049645** vs published 0.5419751773049646 (diff 1.1e-16, float-mean order) |
| Native per-question FR vs frozen `V52_T4C3_question_level.csv` | **470/470**, max abs diff **1.1e-16** |
| Native ANY / ALL R@3 | 0.7130851063829787 / 0.38457446808510637 — exact |
| E4 random-pairing arm vs FROZEN per-seed gaps | reproduced to 5 decimals: −3.4844 / −5.0628 / −2.3199 pp |

Evaluation pipeline: codes `D=(C>=0)`, `Q=(qC>=0)`; Hamming `count_nonzero`; 20 tie-priority
trials via `stable_archive_seed` (frozen adapter v1); `lexsort((prio, dist))`; K=3; metric =
fractional evidence recall. Script: `pilot_axis_attack.py` (this dir).

## 1. Budget curve — spending the 96 bits down (FR@3)

All arms gold-free. TOP/BOT = per-archive variance order; RAND = fixed random subset (seed 12000);
RANKSTRIDE = every 2nd–4th variance **rank** (uniform spread across the spectrum); RANKSPREAD =
rank-linspace at 64/32; IDXSTRIDE48 = even axis indices (the mislabeled IDXSTRIDE64 arm was dropped
— see §6).

| bits (bytes) | TOP-k variance | BOT-k variance | RANDOM | RANKSTRIDE / SPREAD |
|---:|---:|---:|---:|---:|
| 96 (12 B) | — native — | — | **0.541975** | — |
| 88 (11 B) | — | — | 0.5200 (1 seed) | — |
| 80 (10 B) | 0.4911 | — | 0.5147 (1 seed) | — |
| 64 (8 B) | 0.4325 | — | 0.4740/0.4893/0.4853 (3 seeds; mean 0.4829) | 0.4911 (rank-spread) |
| 48 (6 B) | **0.3495** | 0.4285 | 0.4729/0.4410/0.4382/0.4501/0.4471 (5 seeds; mean 0.4499, range 3.5 pp) | 0.4503 (rank-stride) |
| 32 (4 B) | 0.2545 | — | 0.3721 | 0.3605 / 0.3669 (spread) |
| 24 (3 B) | 0.2136 | — | 0.2869 | 0.3000 |
| 16 (2 B) | 0.1693 | 0.1812 | 0.2014 (3-seed mean) | — |
| 8 (1 B) | 0.0899 | — | — | — |

**Findings (benchmark-scoped, descriptive):**
- **In this benchmark, variance-ordered selection performed substantially worse than spread or random
  selection.** At 48 bits, TOP-48 (0.3495) is **−10.0 pp below the 5-seed random mean** (0.4499) and
  below even BOT-48 (0.4285). Paired per-question vs RAND48-mean: **W/T/L = 91/179/200**, and vs
  native: **27/259/184**; worst case −1.00 (total failure on some questions).
  TOP-16 is catastrophic: W/T/L vs native = 50/110/310.
- **Spread ≈ random ≈ best.** Uniform-over-spectrum arms (rank-stride / rank-linspace) ≈ RANDOM at
  every k tested (48: 0.4503 vs 0.4499; 32: 0.3605–0.3669 vs 0.3721; 24: 0.3000 vs 0.2869;
  64: 0.4911 vs 0.4829).
- **Best simple sub-12-byte numbers:** 8 B ≈ 48.3% FR (−5.9 pp vs native, 3-seed mean);
  6 B ≈ 45.0% (−9.2 pp, 5-seed); 10 B ≈ 51.5 (−2.7 pp); 11 B ≈ 52.0 (−2.2 pp);
  4 B ≈ 37 (−17); 3 B ≈ 29 (−25); 2 B ≈ 20 (−34). (Single-benchmark, simple subsets only.)

## 2. Per-axis structure (96 axes)

- **Every axis carries some gold-vs-non-gold signal**: per-axis discrimination delta (P(sign agrees
  with query | gold) − P(... | non-gold)) is positive on **all 96 axes** (mean 0.194; min 0.066).
- Strongest axes are the high-variance (low-index) ones (delta up to 0.31), but the relationship is
  weak in rank terms — **marginal per-axis informativeness ≠ joint retrieval value** (see §3).
- Drop-one-bit: 30 of 96 axes have **zero-or-negative** leave-one-out effect; the largest positive
  drop-loss is only +0.011 FR (axis 94) — i.e., **no single axis is load-bearing**.
- Single-axis ("alone") retrieval is hopeless everywhere (0.0065–0.0097) — 1 bit cannot rank.
- **Tie-pool normalization (applied per reviewer):** alone-FR ≈ 3/(agreement-pool size) when the gold
  agrees, so the raw ranking mostly tracks pool size. The normalized column `alone_fr_norm`
  (= alone_FR × pool/K, ≈ P(gold agrees); `per_axis_v2.csv`) spans 0.549–0.799 and now runs parallel
  to `delta_gold_mean` — as it should. Caveat: `corr_delta_vs_alone = 0.77` (pilot JSON) is inflated
  by the shared pool-size term and should not be read as independent corroboration.

## 3. The separation paradox (mechanism)

At 48 bits, TOP-48 wins **every mean-distance statistic** — smaller gold distance (13.4 vs 14.4),
smaller non-gold minimum (9.0 vs 10.6), smaller crowding (#non-gold ≤ d_gold: 40.2 vs 44.2–49.9),
better mean gold rank (18.7 vs 19.2–22.0) — and yet **loses FR by 10 pp**. Retrieval quality is
decided by the fine structure of the distance distribution (exact-tie mass, near-boundary
competition), not by mean separation. Consistent with this: TOP-48 has ~3× the duplicate-code
fraction (2.35% vs 0.7–0.9%) and more boundary ties (tie-rate 0.460 vs 0.426–0.451), but the duplicate-bucket
sizes are small (mean largest bucket 3.2 vs 2.5) and per-question gaps correlate ≈ 0 with bucket
excess — the deficit is **not** explained by duplicate collapse alone. (Mechanism: open.)

## 4. Mixing dose-response (E4, block-2, same rotations, different axis order; 5 seeds × 3 arms)

Gaps vs native in pp (negative = worse). "antimatched" = pairs formed by the i-th highest-variance
axis with the i-th lowest-variance axis (maximal disparity).

| pairing | 43001 | 43002 | 43003 | 43004 | 43005 | mean | range |
|---|---:|---:|---:|---:|---:|---:|---:|
| random pairs (frozen reproduction) | −3.48 | −5.06 | −2.32 | −5.10 | −3.05 | **−3.80** | −5.10…−2.32 |
| **variance-matched pairs** | −0.31 | −1.95 | −2.46 | −1.86 | −1.50 | **−1.62** | −2.46…−0.31 |
| antimatched (max disparity) | −6.42 | −7.39 | −3.82 | −6.45 | −3.09 | **−5.43** | −7.39…−3.09 |

In this benchmark the damage ordering is monotone in variance disparity (matched < random <
antimatched): variance-matched pairing cuts the 2×2 mixing damage roughly in half vs random pairing
(−1.6 vs −3.8 pp mean), while maximally disparate pairing worsens it (−5.4 pp). A residual loss
remains even when matched. Caveats: the pairing choice jointly changes axis grouping and the
Q-to-axis assignment (not a pure variance isolation); n=5 seeds with large per-seed scatter.

## 5. What this does NOT show (mandatory limits)

- Single benchmark (frozen LME 470), single frozen representation family; **no LoCoMo/cross-benchmark
  claim**; no claim about other embedders.
- Exploratory: arm set was chosen for exploration, not preregistered. Random-arm seeds: 5 at 48 bits
  (range 3.5 pp), 3 at 64 bits (range 1.5 pp); 80/88/32/24 arms are single-seed. The apparent
  "48≈64 plateau" seen with single seeds **disappears** with more seeds (64-bit mean 0.4829 vs
  48-bit mean 0.4499, +3.3 pp).
- E2/E3 and the derived W/T/L fields are **gold-informed analysis** (tagged in
  `pilot_results_corrections.json`); only E0/E1/E4-arm selection are gold-free.
- No causal claim about *why* top-variance fails; "separation paradox" is descriptive.
- The frozen-NOES list (alternate bit widths as a programme claim, alternate thresholds, whitening,
  PCA rotations, variance reweighting, supervised rotation, reranking, …) — everything here is
  labelled pilot; **before any of this becomes a programme experiment it must be preregistered with
  this pilot disclosed.** Frozen accepted results (T4C1–4D) are untouched by this note.

## 6. Independent review dispositions (both sessions read-only, same machine)

- **Independent recomputation (Muse `01a09754-f8c3-7cc3-…`):** recomputed from the raw pkls with the
  frozen protocol — **EXACT** on: E0 gate (470/470, aggregate to 1e-16), E1 top-k / RAND32 / RAND64 /
  BOT48, E2 spot axes {0,47,95}, E4 seed-43001 random+matched (bit-for-bit). Diagnostics sample
  CLOSE (sampling noise; formulas verified exact at full scale). One comparison clarified (3-seed
  mean vs single seed — no deviation). Report: `muse_pilot_verify.md`.
- **Adversarial design review (Muse `01a09754-f8c3-7270-…`):** verdict — *"sound as exploratory
  instrument; weaknesses are labeling and normalization, not plumbing."* 2 FAILs + 6 caveats, **all
  resolved in the corrections pass**: (F7) E2/E3 now tagged analysis-only gold-informed;
  (F14) the mislabeled `IDXSTRIDE64` (a 48-axis duplicate) dropped and replaced by a true
  rank-linspace 64-bit spread arm (0.4911); (F9) tie-pool normalization added (`per_axis_v2.csv`) +
  corr caveat; (F15) 5-seed scatter now reported; (F12) language softened to benchmark-scoped
  descriptive; (F10) E4 extended to 5 seeds × 3 arms (incl. antimatched). (F4 note: the pkls are
  byte-governed by `certification_report.json`'s 470-entry manifest, verified in the closure review.)
  Report: `muse_pilot_review.md`.

## 7. Suggested next steps (for the Head Researcher to decide / preregister)

1. **Train/test-split utility selection** (gold-informed on a train question split only; evaluate
   on held-out questions) — tests whether *learning* per-axis value beats spread/random selection,
   with a clean separation between selection and evaluation splits.
2. **LoCoMo replication** of the budget curve + the "spread beats variance-order" contrast.
3. **A proper sub-12-byte arm set** for the twelve-byte budget decision: native-spread subsets at
   6/8/10/12 bytes alongside the RaBitQ-family arms already proposed in the budget decision —
   because "which bits" turns out to matter more than the nominal width.
4. Mechanism follow-up: tie-mass decomposition at the top-3 boundary per question (why do 200
   questions flip against TOP-48 while their mean stats are better?).

## Files (this directory)

`pilot_axis_attack.py` (E0–E4) · `pilot_results.json` · `per_axis.csv` · `per_axis_matrices.npz` ·
`pilot_diagnostics.py` → `diagnostics.json` · `pilot_diagnostics2.py` → `diagnostics2.json` ·
`pilot_probe.py` → `probe48.json` · `pilot_extra_arms.py` → `extra_arms.json` ·
`pilot_corrections.py` → `pilot_results_corrections.json` + `per_axis_v2.csv` (5-seed/3-arm E4,
true 64-bit spread arm, pool-normalized alone, W/T/L vs native) ·
`muse_pilot_verify.md`, `muse_pilot_review.md` (independent review reports) · this REPORT.md
