# RACE-1 D2 — Pre-seal calibration notebook (F4): kill/promote lines

**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

**Executable record:** `/tmp/rb1/calib.py` → `/tmp/rb1/calib_details.json`.
All numbers below are that script's output (N=2M draws, seed 94301 + offsets).
Gate: m1 LOO null reproduced from Deney-1 details within 0.05pp — PASS both benchmarks
(actual diffs 0.0000pp; recomputed mean/sd identical to `missing1_kill_null.json`).

## 1. Method (chosen and justified)

- **Model:** each competitor's aggregate FR (pp) is Gaussian; the sealed-race primary
  contrast `SIGN12B − max_comp` is simulated under the exchangeable no-edge null
  (H0: SIGN carries no premium; all K+1 aggregates share one location). Per-look sd is
  estimated **per width** from the existing random panels (pooled within-split across-seed
  sd — the scale at which selection lift operates), recomputed exactly:

| panel | LME sd (pp) | LoCoMo sd (pp) |
|---|---|---|
| RANDOM32 | 1.66 | 0.84 |
| RANDOM48 | 1.36 | 0.90 |
| RANDOM64 | 1.14 | 0.74 |

- **Competitor count (frozen):** LME K=40 (RANDOM30 + SPREAD3 + BOT48 + TOP48/TOP64 +
  RQ32-primary×3 + PQ1); LoCoMo K=41 (RANDOM30 + SPREAD3 + BOT80/64/48 + TOP48 +
  RQ32-primary×3 + PQ1). Curve-only A7-44B, TOP32-curve, random-32 secondary and the A5
  wrapper are excluded from the max (multiplicity cap). v2's "~27+" used ≥7 seeds; K=40/41
  uses the sealed 10-seed panels.
- **(i) Independence — PRIMARY for line-setting.** Validated, not merely conservative:
  at K=9 the independence simulation gives LME −1.70/1.33 vs empirical −1.62/1.38 and
  LoCoMo −1.09/0.86 vs −1.20/0.93 — match within ~0.1pp. Reason: shared-question level
  shifts cancel in the contrast (a within-test-set difference), so the operative spread is
  the code-driven within-split sd, which behaves as independent.
- **(ii) Equicorrelation — reported and REJECTED for lines.** Question-bootstrap aggregate
  correlations are high (LME same-width 0.79 / cross-width 0.66; LoCoMo 0.69/0.56), but
  feeding them into the K=9 model gives LME −0.77/0.60 and LoCoMo −0.61/0.48 — roughly
  HALF the empirical null. The levels-correlation describes shared test-set noise that
  cancels in differences; using it would set anti-conservative (shallow) lines. Both
  models are in `calib_details.json`; only (i) freezes literals.
- **Scale conservatism (stated):** pilot σ comes from half-split test sets (LME n=234,
  LoCoMo n=767); the race runs full benchmarks, whose null is tighter (≈1/√2, sensitivity
  row in json: LME p2.5 −4.47, LoCoMo −2.59). Lines calibrated at half-split scale are
  therefore conservative in BOTH directions (harder to kill, harder to promote). Width-mean
  differences (wider panels truly better) are absorbed the same way: centering all looks
  at one location overstates the max, i.e. conservative.

## 2. Null distribution of the primary contrast (per benchmark, pp)

| stat | LME (K=40) | LoCoMo (K=41) |
|---|---|---|
| mean | −3.14 | −1.82 |
| sd | 1.60 | 0.93 |
| 1st pct | −6.96 | −4.02 |
| **2.5th pct** | **−6.33** | **−3.67** |
| 5th pct | −5.80 | −3.36 |
| median | −3.12 | −1.81 |
| 95th pct | −0.55 | −0.31 |
| **97.5th pct** | **−0.07** | **−0.03** |
| P(contrast > 0) | 0.023 | 0.023 |

Reading: under no edge, SIGN trails the best of ~40 looks by ~3.1pp (LME) / ~1.8pp
(LoCoMo); merely reaching parity is already a 97.5th-percentile event.

## 3. LITERAL lines (frozen)

- **KILL line X = null 2.5th percentile, rounded outward to 0.1pp: LME −6.4pp,
  LoCoMo −3.7pp.** X=2.5% because the kill rule is an OR across 2 benchmarks:
  Bonferroni/union bound gives family-wise false-kill ≤ 2×2.5% = 5% (§5).
- **PROMOTE line Y = +2.0pp on EITHER benchmark (v1 literal retained, justification
  replaced).** The full-set null 97.5th sits at ≈−0.0pp on both benchmarks, so +2.0
  clears it by >2.0pp of margin (LME +2.07, LoCoMo +2.03) — the v1 defect (line 0.09pp
  above the observed null max) is closed with two full pp of daylight. Y plays two roles
  at once: null-clearing (97.5th) AND observed-lift consistency (a genuine premium, not a
  null tail event).
- **Zones (per benchmark, gap = SIGN − max_comp in pp):**
  KILL: gap < kill line · LOW: kill line ≤ gap < −0.5 · MID: −0.5 ≤ gap < +2.0 ·
  PRO: gap ≥ +2.0.
- **Point-vs-interval rule:** zone assignment is by POINT gap. Bootstrap is B=5000
  question-paired (seeds 94301 LME / 94302 LoCoMo; secondaries +10; argmax re-selected
  inside each resample) + LoCoMo conversation-cluster CI as a second interval
  (descriptive). A KILL stands unless the 95% CI lies entirely above the kill line
  (→ downgrade to HOLD-ambiguous, disclosed). A PROMOTE additionally requires the 95% CI
  lower bound > 0 on the promoted benchmark (win in the same direction, robustly).

## 4. Complete 16-cell decision table (row = LME zone, col = LoCoMo zone)

|  | LoCoMo KILL | LoCoMo LOW | LoCoMo MID | LoCoMo PRO |
|---|---|---|---|---|
| **LME KILL** | KILL | KILL | KILL | KILL |
| **LME LOW** | KILL | HOLD-weak | HOLD-weak | HOLD-split |
| **LME MID** | KILL | HOLD-weak | HOLD-parity | PROMOTE* |
| **LME PRO** | KILL | HOLD-split | PROMOTE* | PROMOTE* |

KILL dominates everywhere (OR rule). PROMOTE* = PRO on ≥1 bench with the other bench
≥ MID, plus §3 CI conditions, plus the recall-vs-bytes dominance check passed (no
"dominated everywhere" finding against SIGN). All other cells = HOLD (retain SIGN12B;
no kill, no promote). The MID band absorbs the draft's ±0.5 parity and +1.0–2.0 moderate
heritage as descriptive sub-labels; they carry no action.

## 5. Family-wise rule confirmation (Bonferroni across 2 benchmarks)

Kill: per-benchmark α=2.5% with an OR rule → family-wise P(false kill) ≤ 5% by the union
bound (no dependence assumption needed). Promote: PRO on ≥1 bench (each ≈2.5% under the
null, since +2.0 ≫ 97.5th) with the other bench ≥ MID, plus CI > 0 and the dominance
check — strictly more stringent than a single 2.5% test, so family-wise P(false
promote) < 5%. Secondaries are descriptive only and never enter gates (C10 cap intact).

## 6. Premium-needed update + footnote wording

v2's "+2.6pp to clear the vs-best-of-10 null" becomes, under the extended null: **a true
premium of ≈+3.1pp (LME) / ≈+1.8pp (LoCoMo) is needed for the EXPECTED gap to reach the
null 97.5th; ≈+4.4pp / ≈+2.6pp for 80% power against the +2.0 promote band.**
(Headline figure: expectation version.) Sealed footnote wording:

> "Under the pre-seal exchangeable-competitor null (K=40 LME / 41 LoCoMo, per-width σ
> from Deney-1 random panels, half-split scale), SIGN−max has mean −3.14pp (sd 1.60) on
> LME and −1.82pp (sd 0.93) on LoCoMo; kill lines (null 2.5th, Bonferroni across 2
> benchmarks) are −6.4/−3.7pp and the promote line is +2.0pp either benchmark (clears the
> null 97.5th by >2pp). A true premium of ≈+3.1pp (LME) / ≈+1.8pp (LoCoMo) puts the
> expected gap at the null's upper edge. Calibration: `/tmp/rb1/calib.py` (seed 94301)."

*D2: DONE. No race data used; nothing sealed here — the orchestrator adopts the
`frozen_literals.json` numbers as literals at seal.*
