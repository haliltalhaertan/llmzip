# CODE_REVIEW.md — Step 3: line-level audit of the three .py files

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Files (read-only): axis_budget_core.py, run_sweep.py, coord_readout.py under
/mnt/c/Users/MDP/dev/llmzip-work/agent_out/axis-budget/. Workspace copies:
their_core_copy.py, their_sweep_copy.py (this directory, unmodified copies).

## (a) m=96 internal consistency — PASS (VERIFIED)

- At m=96, TOP-96 == BOT-96 == all 96 axes by construction (`order[:96]`,
  `order[-96:]`), and random-96 draws the full set. Evidence (VERIFIED dump):
  sign_top == sign_bot == sign_rand exactly on all four benchmarks
  (LME 54.2134, LoCoMo 23.7907, REALTALK 22.5535, PerLTQA 48.8945).
- delta_matched == delta_vs_full96 at m=96 on 4/4 (LME +10.0538, LoCoMo +6.6550,
  REALTALK +5.3001, PerLTQA −6.2747). The budget-matched float DOES equal the
  full-96 float. Nothing is void.
- OBSERVATION (not a sweep error): the audit preamble's "frozen headlines"
  (LME +10.037943, REALTALK +5.2241, LoCoMo +6.82838) differ from the sweep's m=96
  row by 0.016 / 0.076 / 0.17 pp. The CRITICAL-FACTS controls (LME +10.053783,
  PerLTQA −6.274728, REALTALK +5.300077) match the sweep exactly. So the preamble
  headlines are stale (different pipeline vintage), and the sweep agrees with the
  newer exact-expectation controls. For LoCoMo no control was quoted; my independent
  recompute gives +6.655046, confirming the sweep over the preamble (+6.82838).

## (b) Axis ranking — CORRECT, with one unacknowledged overlap (VERIFIED)

- Per-ARCHIVE: `order` is computed inside the per-unit loop from that unit's own C
  (run_sweep.py line 56: `np.argsort(-(C ** 2).mean(axis=0), kind='stable')`).
  LME units are per-query archives; PerLTQA units are per-char archives. NOT pooled.
  No leak. Sort is descending. BOT-m = `order[-m:]` = the m lowest. Correct.
- FINDING (interpretation caveat, numbers unaffected): TOP-m and BOT-m OVERLAP
  whenever 2m > 96 (m=64: 32 shared axes; m=80: 64 shared; m=96: identical). Neither
  run_sweep.py nor coord_readout.py mentions this. At m=48 they partition exactly.
  Any reading of the m=64/80 BOT-vs-TOP trend as a pure high-vs-low contrast is
  diluted 2x–5x by shared axes (quantified in INTERPRETATION_REVIEW.md, test S6).

## (c) FR@3 exact tie expectation — CORRECT (VERIFIED by brute force)

- `fr_at_k_exact` implements E = (g_strict + g_tied·slots/bc)/|gold| with
  higher-better scores; the sign arm passes −Hamming so lower distance ranks first.
  Correct.
- VERIFIED (locator: test_ties.py): 300/300 randomized fuzz cases (integer
  Hamming-like scores with heavy ties + rounded float scores) and 9 hand edge cases
  (all-tied, N=K, N<K, multi-gold, gold-in-tie) match exhaustive permutation-average
  enumeration to 1e-12.
- Minor: `slots = max(kk − strictly, 0)` with `kk = min(K, N)` is dead-safe here
  (min N across all benchmarks is 293, so kk=3 always); duplicate gold row indices
  would double-count in `gold_size` but not in `Gmask` — no duplicates observed.

## (d) Cosine nan guard — BENIGN DEAD CODE (VERIFIED)

- `cos_batch` maps nan/±inf → −2.0, i.e. strictly below the [−1,1] cosine range, so
  affected rows rank last and tie among themselves. Sound placement (before the
  metric, so `fr_at_k_exact` never sees NaN). No systematic favouritism possible
  beyond "undefined similarities rank last", which is the only sane policy.
- VERIFIED (locator: interp.py test S7): ZERO zero-norm events across all four
  benchmarks × all nine budgets × TOP and BOT subsets (11,003 query-units × 18
  subsets). The guard never fires. Mutation M5 (guard removed) changes nothing —
  see MUTATIONS.md. The guard is harmless but untested-by-execution dead code; keep
  it, but nobody may cite it as load-bearing.

## (e) "Budget-matched" — TERMINOLOGY FINDING (no number error)

- The comparison matches AXIS COUNT (m bits of sign vs m float32 = 32m bits).
  Storage ratio is 32:1 in float's favour at every m. The honest name is
  "dimension-matched quantization isolation" — which run_sweep.py's own docstring
  says ("isolates quantization, not dimension"; full-96 float reported separately).
- CLAIM 1's "budget-matched" without that caveat invites a storage-budget reading.
  A storage-matched comparison would be e.g. SIGN-96 (96 bits ≈ 12 bytes) vs
  FLOAT-3 (3×32 = 96 bits), or SIGN-m vs FLOAT-m/32. Under a bit-budget, the sign
  arm's advantage would be far larger than reported; conversely the reported
  crossover says nothing about bit-efficiency. The numbers are right; the label is
  doing undisclosed work. Severity: observation / required relabelling.

## (f) Crossover precision — FINDING: indefensible (VERIFIED)

- m* is linear interpolation across a 16-wide grid gap (LME/REALTALK: 32→48;
  LoCoMo: 48→64). Reported to 0.1 axis (47.3, 42.5, 53.4). Grid quantization alone
  (±8 axes) dwarfs 0.1.
- VERIFIED (locator: interp.py test S3): approximate parametric bootstrap from the
  reported paired-difference SEs gives 95% intervals spanning ~7–14 axes
  (LME ≈ [41,48], REALTALK ≈ [33,47], LoCoMo ≈ [48,62]), and for LME only ~57% of
  draws even straddle zero in the 32–48 interval (v48 = +0.29 ± 1.64 SE).
  Caveat: approximate (no per-query data; likely conservative), but the grid floor
  (±8) stands regardless. Honest reporting: LME "crosses between 32 and 48",
  LoCoMo "between 48 and 64", REALTALK "between 32 and 48" — the decimals must go.
- Arithmetic of the point estimates themselves checks out (recomputed 47.29/42.45/
  53.41 → 47.3/42.5/53.4 ✓).
