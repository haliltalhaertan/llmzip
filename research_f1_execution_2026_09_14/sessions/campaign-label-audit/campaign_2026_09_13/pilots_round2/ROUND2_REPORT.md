# ROUND 2 — Axis-attack follow-up (2026-09-13, local)

**Labels: [LOCAL EXPLORATORY PILOT — ROUND 2] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

Method: three parallel independent Muse executor sessions (R2A / R2B / R2C), each self-gated
against frozen values; orchestrator spot-checks; two further sessions (R2V recompute-verify,
R2D design review) run on the outputs. **All gates passed exactly** (see each section).

---

## 1. R2A — per-question flip analysis (why does TOP48 lose?)

Self-gate (exact, diff 0.0): TOP48 = 0.34949468085106383, RAND48_s0 = 0.47292553191489356,
BOT48 = 0.4284574468085106; per-question natives vs stored: 470/470, max abs diff 0.0.

Overall W/T/L (TOP48 vs RAND48_s0, tol 1e-12): **63 / 250 / 157**, mean gap −0.1234, median 0.0
(ties dominate — most questions are exact ties between the two arms).

Per `question_type` (sorted by mean gap; n / W/T/L / mean gap):

| type | n | W/T/L | mean gap |
|---|---:|---|---:|
| single-session-user | 64 | 3/36/25 | −0.3004 |
| knowledge-update | 72 | 13/26/33 | −0.1652 |
| single-session-assistant | 56 | 4/39/13 | −0.1473 |
| temporal-reasoning | 127 | 24/63/40 | −0.0749 |
| single-session-preference | 30 | 3/21/6 | −0.0628 |
| multi-session | 121 | 16/65/40 | −0.0599 |

Correlations of the gap with: N_archive −0.127, gold_count +0.149, RAND48 gold rank +0.135,
TOP48 tie-cluster +0.020, TOP48 dup fraction −0.037 — **all weak; no single variable explains
the flips.**

Losers/winners spot-check (the mechanism read):
- Hard loser `001be529`: RAND48 puts the gold uniquely closest every trial (rank 0.0, cluster 1.0)
  while TOP48 buries it (rank 18.2, 14 docs closer, tie-cluster 11). Winners are the mirror image
  (e.g. `gpt4_468eb063`: TOP48 rank 0.95/cluster 3 vs RAND48 rank 8.5).
- Hard losers average: TOP48 rank 10.8 / cluster 6.1 vs RAND48 rank 0.6 / cluster 1.3.
- Descriptive reading: for the decisive questions the discriminative signal lived in
  **low-variance axes**; TOP48 (per-question) collapses those golds into tie clusters outside
  top-3 while the random subset keeps them uniquely closest. (No causal claim; per-question
  variance-order effects are adaptive — another open thread.)
## 2. R2B — train/test-split learned axis selection (the preregisterable experiment)

Self-gates (all exact): split 239 train / 231 test (sha256-parity rule; orchestrator re-verified);
all-96 native recompute vs stored per-q natives max diff 1.1e-16. Test half is harder:
native mean test 0.5190 vs train 0.5642.

Utilities (TRAIN only): `drop` = mean drop-loss, `delta` = mean gold-discrimination,
`alone` = pool-normalized single-axis FR, `var` = variance-order control. Each arm = one fixed
global axis set `argsort(U)[::-1][:k]`, evaluated on TEST with the frozen protocol.

| arm | train FR | test FR | gap vs k-matched random mean |
|---|---:|---:|---:|
| delta32 | 0.4020 | 0.3244 | −2.15 pp |
| delta48 | 0.4808 | 0.3864 | −4.92 pp |
| delta64 | 0.5139 | 0.4317 | −1.82 pp |
| drop32 | 0.3816 | 0.3374 | −0.86 pp |
| drop48 | 0.4921 | 0.4444 | +0.88 pp |
| **drop64** | 0.5623 | **0.4838** | **+3.39 pp** |
| alone32 | 0.3722 | 0.2972 | −4.87 pp |
| alone48 | 0.4876 | 0.4053 | −3.03 pp |
| alone64 | 0.5232 | 0.4715 | +2.17 pp |
| var32/48/64 | … | 0.2376/0.3290/0.4063 | −10.8/−10.7/−4.4 pp |
| SPREAD32/48/64 | … | 0.3193/0.4218/0.4218* | −2.7/−1.4/−2.8 pp |
| RANDOM32/48/64 (3-seed mean) | … | 0.3459/0.4356/0.4498 | 0 |
| NATIVE96 (reference) | 0.5642 | 0.5190 | — |

- **Two learned arms beat their k-matched random mean on test** (corrected per R2D errata):
  `drop64` +3.39 pp (test 0.4838; W/T/L 63/124/44) and `alone64` +2.17 pp (test 0.4715).
  Vs the **best** of the three RANDOM64 seeds (0.4342 / 0.4676 / 0.4477): drop64 +1.62 pp,
  alone64 +0.39 pp. Moderate signal, small n; single-arm gaps near ±1 pp are noise-scale
  (seed spread 3.34 pp at k=64).
- Overfit gap visible and reported: drop64 train 0.5623 (≈train native) vs test 0.4838.
- The variance control (`var`) is the worst arm at every k — the round-1 top-variance finding
  replicates **out-of-sample on held-out questions** with learned utility replaced by pure
  variance order.
- Design artifact disclosed by the session: `SPREAD64 ≡ SPREAD48` (stride-2 over 96 axes caps at
  48; `[:64]` is a no-op) — reported honestly, not hidden.
- Utility top-5 (train): drop [23, 72, 88, 2, 58] — orchestrator recomputed exactly.
## 3. R2C — LoCoMo replication (cross-benchmark)

**GATE: native fractional R@3 = 0.23654714666441054, diff 0.0 exact** (re-extracted protocol from
the frozen T4D script; no re-fit — our certified matrices used). Haar96 mean reproduced to −2.9e-15
(rounding of the 14-decimal anchor). Cohort: 1540 Cat1–4 questions, 1535 audit-valid.

Bit-budget arms (fractional R@3; gap pp vs native):

| k | TOP (variance) | RANDOM (3 seeds) | BOT | SPREAD* |
|---|---|---|---|---|
| 16 | .0653 (−17.1) | .0590/.0574/.0635 | .0742 (−16.2) | .0491 (−18.8) |
| 32 | .0870 (−15.0) | .1173/.1219/.1219 | .1404 (−9.6) | .1096 (−12.7) |
| 48 | .1318 (−10.5) | .1591/.1598/.1683 | .1811 (−5.5) | .1603 (−7.6) |
| 64 | .1653 (−7.1) | .1886/.2025/.1977 | .2172 (−1.9) | (.1603)* |
| 80 | .2004 (−3.6) | .2277/.2108/.2257 | .2355 (−0.1) | (.1603)* |

\* SPREAD caps at 48 axes (stride-2); disclosed.

Block-2 pairing at 96 bits (per-seed gaps pp):

| arm | seed43001 | 43002 | 43003 | mean gap |
|---|---:|---:|---:|---:|
| random pairing | −3.16 | −1.63 | −2.27 | −2.35 |
| **matched-variance** | −0.09 | −0.63 | +0.59 | **−0.04** |
| antimatched | −3.75 | −5.38 | −3.72 | **−4.28** |

**Strict separation on every seed**: min matched (.2302) > max random (.2203) > max anti (.1994).

Cross-benchmark verdict (descriptive):
- "Top-variance selection is bad" **replicates** (TOP loses to RANDOM at every k ≥ 32).
- "Variance-disparity drives mixing damage" **replicates, even cleaner** than on LME (strict
  per-seed separation; matched ≈ native).
- **Difference from LME:** on LoCoMo the **BOTTOM**-variance subsets are the best simple arm
  (BOT ≈ native−0.1 pp at k=80), while on LME random/spread ≈ best and bottom sat slightly below.
  Where the "good bits" live differs across benchmarks — reported, not smoothed over.
- Per-category (native / matched-s43003 / Haar-mean): Cat1 .109/.100/.066; Cat2 .255/.260/.116;
  Cat3 .095/.090/.079; Cat4 .288/.300/.176.## 4. Synthesis — what round 2 added

1. **Mechanism (R2A):** the TOP48 deficit is concentrated in questions where the gold's
   discriminative bits live in low-variance axes; TOP48 buries those golds in tie clusters. No
   single metadata variable explains the flips (all |r| ≤ 0.15) — the effect is per-question
   geometry, not question-type composition.
2. **Learnability (R2B):** per-axis utility IS partially learnable beyond random: train-only
   `drop`-loss selection at 64 bits beats the random mean by +3.39 pp on held-out questions (and
   the best seed by +1.6 pp). But the gain is modest and the variance control remains disastrous —
   so "use spread/random, never variance-order" stands, with a small learned-selection premium as
   a candidate for a preregistered test with more seeds.
3. **Cross-benchmark (R2C):** the two core round-1 findings replicate on LoCoMo — top-variance is
   worst; variance-disparity ordering of mixing damage is strict per-seed. One nuance: LoCoMo's
   best simple subset is the BOTTOM tail, not random — the location of useful bits is benchmark-
   dependent (descriptive; mechanism open).
4. **Process:** all three sessions self-gated against frozen values (all EXACT); orchestrator
   independently re-verified the R2B split (239/231) and utility top-5 ([23,72,88,2,58]).

## 5. Verification status (of this round)

- R2V (independent recomputation) and R2D (adversarial design review): RUNNING when this report
  was written; their verdicts will be appended as §6 before packaging. Round-1 experience: treat
  these as required before citing the numbers in any future preregistration.
- All labels carry: `[LOCAL EXPLORATORY PILOT — ROUND 2] [NOT PREREGISTERED] [NOT FOR CITATION]
  [DISCLOSE-BEFORE-USE]`. Frozen accepted tasks (4C1–4D) untouched; Task 4F1 boundary untouched.

## 6. Independent review verdicts

- **R2D (adversarial design review, Muse `01a099bc-a16d-…`, read-only):** recomputed all numeric claims
  from the evidence files (spot tables, gates, splits, utilities) — **no md-vs-json numeric
  mismatches**. Found: (F1) two factual prose errors in the R2B session report — corrected by
  errata (two arms beat the mean; alone64 also beats the best seed); (F10) R2A/R2C session reports
  lacked exploratory labels/limits — errata added; (F9) one causal phrase in R2A softened to
  subset-description; (F7/F5) construction code for the novel R2C pairings and the R2B SPREAD arms
  was not shipped — now included (`session_scripts/`) + SPREAD note added to the details JSON;
  (F3/F12) headline framing now leads with vs-best-seed gaps and n=3 scatter. Verdict: numbers OK;
  weaknesses were labeling/prose, all corrected in this directory.
- **R2V (independent recomputation, Muse `01a099bc-a15b-…`):** recomputed every headline number
  from raw inputs with protocol sources copied verbatim (never read the other sessions' scratch) —
  **all EXACT**: R2B split 239/231; drop top-64 column list (full 64/64 identical); drop64 test
  0.4837806638 / train 0.5622907949790794; RANDOM64 seeds 0.4342/0.4676/0.4477; W/T/L 63/124/44;
  R2A W/T/L 63/250/157 + all per-type rows + the three arm means (worst deviation 5.6e-17 from
  float summation order); R2C gate 0.0, MATCHED/ANTIMATCHED means + per-seed gaps, k=48 BOT
  0.181122, and the `001be529` spot row. Notes (non-numeric): md roundings verified correct; the
  pkl-order gloss is immaterial (priorities are conversation-level; correction mapping verified
  156/156). Report: `r2v_verification.md`.

## 7. Files (this directory)

- `r2a_flip_analysis.md`, `r2b_learned_selection.md`, `r2c_loco_replication.md` — session reports
  (each with an ORCHESTRATOR ERRATA banner where R2D found prose/label issues)
- `r2d_design_review.md` — adversarial design review report (full)
- `wsl_details/r2a_per_q.json` (per-question arrays), `r2b_details.json` (24 arms × per-q FRs;
  SPREAD cols noted), `r2c_details.json` (LoCoMo arms)
- `session_scripts/` — the sessions' actual code (r2a.py, r2b.py, r2c_replicate.py) for
  construction-level verification of the novel pairings
- `r2a_r2.json`, `r2b_r2.json`, `r2c_r2.json` (+ `r2d_r2.json`) — raw session transcripts (Muse)
- `verify_round2.py` — stdlib checker for this round
- `HASHES_AXIS_PILOT_R2.txt` — manifest of this round (generated at packaging)