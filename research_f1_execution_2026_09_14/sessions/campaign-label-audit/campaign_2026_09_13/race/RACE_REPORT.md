# TWELVE-BYTE RACE — result report (local, pre-registered-shape)

**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

[LOCAL] [NOT PUSHED] [EXPLORATORY — non-preregistered governance, prereg-shaped rules frozen pre-official-run]

**Question.** At the 12-byte marginal budget, is NATIVE SIGN96 “competitive” against the full
sealed competitor set (its own subset/sampling arms + RaBitQ32 + PQ), or does something beat it?

**Frozen lines (RB1 calibration, seed 94301, N=2M draws; `rb1/frozen_literals.json`).**
Kill: LME −6.4pp / LoCoMo −3.7pp (full-set null 2.5th, Bonferroni across 2 benchmarks ≤5%).
Promote: +2.0pp either benchmark (clears the null 97.5th by >2pp; also needs CI>0).
Null (no-edge): mean −3.14pp sd 1.60 (LME, K=40) / −1.82pp sd 0.93 (LoCoMo, K=41).

**Campaign chain.** RB1 (calibration) → RB2 (sign runner) → RB3 (faiss runner) →
seal `PRE_RUN_SEAL_local.json` (runner hashes frozen) → official run (both runners, exit 0)
→ RACE-V (independent recomputation) → official analysis (bootstrap + 16-cell).

## 1. Results (FR@3, fractional; official run)

| Arm (≤12B) | LME | LoCoMo |
|---|---|---|
| **NATIVE SIGN96 (12B)** | **0.54198** | **0.23655** |
| SPREAD80 (10B, rank-linspace) | 0.52526 (−1.672pp) | 0.22433 (−2.222pp) |
| BOT80 (10B, bottom-variance) | 0.52285 (−1.913pp) | **0.23546 (−0.109pp)** |
| RAND80 best seed (10B) | 0.52445 (−1.752pp) | 0.22513 (−1.142pp) |
| SPREAD64 (8B) | 0.49641 | 0.19372 |
| RAND64 best seed (8B) | 0.51787 | 0.20601 |
| SPREAD48 (6B) | 0.44273 | 0.16236 |
| RAND48 best seed (6B) | 0.45922 | 0.17391 |
| TOP48 (6B, top-variance) | 0.34949 | 0.13183 |
| RQ32 spread-rot best (12B) | 0.31167 (−23.0pp) | 0.09550 (−14.1pp) |
| PQ (12B) | 0.43074 (−11.1pp) | 0.15368 (−8.3pp) |

TOP-variance controls behaved as expected on LME (TOP48 −9.70pp / TOP64 −5.89pp vs
random-mean); LoCoMo TOP48 = −2.78pp — the prespecified ≥5pp margin was NOT met, but TOP did
not win, so the validity gate = OK (disclosed as expectation-not-met, not a failure).

## 2. Verification

- **RACE-V (independent session):** 26/26 checks EXACT — anchors diff 0.0; 12/12 FR spot
  checks 0.0; aggregates 6/6 + MATH-1 model 5/5 = 0.0; byte replay 20/12/12/44 exact; PQ
  retrain bit-identical; W/T/L 16/16; official-vs-build diffs exactly the disclosed 3 items
  (timing; one last-ulp 1.39e-17; build-only annotation field). `racev/racev_report.md`.
- Official-run outputs vs build outputs: bit-identical numerically (RB2: one timing diff).

## 3. Disposition (frozen 16-cell)

(LME, LoCoMo) zones = (MID, MID) → **HOLD-parity.** No kill; no promote; retain SIGN12B.
CIs all include 0 (primary: LME [−0.60,+2.12], LoCoMo [−0.91,+1.02]); point estimates
+1.67pp / +0.11pp vs the respective best competitors. Interpretation frame (frozen): under
the no-edge null SIGN should trail best-of-40 by −3.14/−1.82pp; merely reaching parity is a
97.5th-percentile event. LME's +1.67 sits in the descriptive “moderate” band but below the
promote floor (+2.0). Premium needed at expectation level: ≈+3.1pp (LME) / ≈+1.8pp (LoCoMo)
(80% power: ≈+4.4 / +2.6pp) — not achieved.

## 4. Honest limits

- **Sequence disclosure:** runner development/smoke runs preceded the seal by minutes
  (13:06–13:09 vs 13:10); the official run (13:12–13:14) re-executed the hash-frozen files
  and reproduced the numbers; this is a local exploratory process, not an institutional
  preregistration. `official_run/OFFICIAL_RUN.md` §Process.
- Not-checkable: per-archive code bytes (aggregate hash only); bootstrap phase local;
  A5 wrapper single unseeded draw (excluded from K per sealed rules); RQ96 (20B/arm) is
  out-of-budget and curve-only; R@3 ≠ end-to-end answer quality; two benchmarks, one
  representation family; third-party codec configs are the pinned faiss defaults (a
  better-tuned PQ/RaBitQ cannot be excluded).
- Sealed footnote (adopted from RB1 §6): *“Under the pre-seal exchangeable-competitor null
  (K=40 LME / 41 LoCoMo, per-width σ from Deney-1 random panels, half-split scale),
  SIGN−max has mean −3.14pp (sd 1.60) on LME and −1.82pp (sd 0.93) on LoCoMo; kill lines
  (null 2.5th, Bonferroni across 2 benchmarks) are −6.4/−3.7pp and the promote line is
  +2.0pp either benchmark (clears the null 97.5th by >2pp). A true premium of ≈+3.1pp (LME)
  / ≈+1.8pp (LoCoMo) puts the expected gap at the null's upper edge. Calibration:
  rb1/calib.py (seed 94301).”*

## 5. One-paragraph summary

**The twelve-byte budget race concludes HOLD-parity: nothing beats SIGN96 at 12B — not its
own subsets (10B costs ≈1.7pp LME / ≈0.1pp LoCoMo; 8B ≈2.4–4.6pp; 6B ≈8–10pp), and not the
third-party codecs (PQ −11/−8pp; RaBitQ32 −23/−14pp).** SIGN96 remains the champion at its
native budget; parity-with-positive-tilt, no kill, no promote; premium not established.

**Artefacts:** `rb1/` (calibration + literals) · `rb2/`, `rb3/` (runners + build outputs) ·
`PRE_RUN_SEAL_local.json` · `official_run/` (canonical) · `racev/` (verification) ·
`analysis/` (this analysis). Reproduce: rerun `official_run` runners (hashes in seal) then
`analysis/analysis.py`.
