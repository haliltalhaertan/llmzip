[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# CROSS_BENCHMARK_TEST — H1 adversarial test (PREPARED, NOT ACCEPTED)

Hypothesis text frozen in `HYPOTHESIS.md` BEFORE this leg ran; it is not edited here.
Per-query recomputation: `analysis.py` xbench leg → `evidence/results.json`
(`xbench_realtalk`, `xbench_lme`, `xbench_locomo`). All inputs via `git show`
on `origin/research/e1-mechanism-checkpoint-frozen-2026-09-13` (no checkout).

## 1. REALTALK — H1 fails (VERIFIED)

- Input identity VERIFIED: SHA256 of `bench3/b3a_realtalk/details.json` matches E1's claimed
  `details_sha256 8bae1d38...` exactly. Valid n=705. Headline reproduced: mean Delta
  +5.224102217719238 (E1 CLAIM +5.224102217719239 — match to 1e-12), mean P64 +0.022066943363136.
- W/T/L = 104/558/43: nonzero queries are 70.75% wins. H1 Rule A (tie→loss) nonzero-conditional
  accuracy = 51.0% (75/147) — ~coin flip, 20pp BELOW the always-predict-win prior. F2 FAILS.
- Rank associations are null with H1-hostile signs: rho(Delta, boundary_tie) = +0.042 (H1 needs <0),
  rho(Delta, tail_gap) = -0.049 (H1 needs >0). P64 rho = +0.0746 reproduces E1 exactly (second route).
- Category levels non-monotone (F1 FAILS): cat2 wins most (+8.63) with the lowest tie rate (0.333) but the
  LARGEST mean gap (1.41); cat3 (+5.47) has the highest tie rate (0.419) and smallest gap (1.02);
  cat1 (+1.44) sits middle on both. No denser-loses ordering exists.
- Gold control: single-gold queries (n=319) win most (+8.23); multi-gold groups are small-n mixed.
  No H0 reversal pattern either.

## 2. LongMemEval — H1 fails (VERIFIED)

- Join VERIFIED 470/470 exact between `V52_T4C2_question_level.csv` and SIGN96_CENTERED rows of
  `V52_T4C2_tie_diagnostics.csv` (matches E1's 470/470 CLAIM). Mean Delta +10.037943262411346
  reproduces the frozen LME headline to all 15 decimals.
- Nonzero Delta is 73.5% wins (122/166; E1 delta_counts 122/304/44 CLAIM reproduced).
  Rule A nonzero-cond = 63.3% < 73.5% prior. Rule C (cand_at_boundary≥3 → loss) = 72.9% —
  within 0.6pp of the always-predict-win prior, i.e. it mimics the prior (heavy boundary mass is rare),
  adding no discrimination. F2 FAILS (both rules ≤ prior).
- Rhos null: rho(Delta, candidates_at_boundary) = -0.043, rho(Delta, top3_tie) = -0.012.
  H1-consistent signs, zero substance — on the benchmark SIGN wins by +10pp, competition is unrelated.
- Question-type levels contradict H1 (F1 FAILS): temporal-reasoning wins most (+12.45) with the HIGHEST
  tie rate (0.315); single-session-assistant wins least (+4.20) with the LOWEST tie rate (0.179).
  Backwards, exactly as on PerLTQA sections.

## 3. LoCoMo — untestable from committed caches (recorded, not support)

- `audits/audit1_cont/taskC_LoCoMo_perq.json` is present (n=1535) but carries only the 5-arm layout
  (BOT80/NATIVE96/RAND80_s2/SPREAD80/TOP48) — NO float arm, so per-query Delta is incomputable.
- `regen/locomo/counts_report.json` and `regen/locomo/task1_locoMo_stats.json` are archive-level
  stats, not per-query outcomes. No other committed per-query centered-float surface was found.
- LoCoMo H1 recomputation: UNAVAILABLE-UNDER-CACHE-GAP. R2 CLAIM-level context only (document says it):
  headline +6.828380125122796 pp; rho(Delta, strict gap) +0.0949, rho(Delta, gold-tie gap) +0.1038
  (`E1_V2_COMPETITION_CORRECTED_RESULT.json`, RELAYED). These weak-positive slopes do not rescue H1's
  level prediction, which is what the PerLTQA reversal is about.

## 4. Falsification scorecard (criteria F1–F3 from HYPOTHESIS.md)

| criterion | PerLTQA | REALTALK | LongMemEval | LoCoMo |
|---|---|---|---|---|
| F1 denser-loses levels | FAIL (backwards) | FAIL (non-monotone) | FAIL (backwards) | untestable |
| F2 rules beat majority prior | FAIL 0/5 strata | FAIL (51.0 vs 70.8) | FAIL (63.3/72.9 vs 73.5) | untestable |
| F3 directional rhos | tiny, mixed by section | null, hostile signs | null | CLAIM-only weak+ |

H1 is wrong as a regime explanation: it predicts loss from competition where the winners are densest
(PerLTQA profile, LME temporal) and finds no consistent slope where SIGN wins. A killed hypothesis,
cleanly reported, per the brief — no post-hoc adjustment is offered.

## 5. What survives H1's death (observed, not hypothesised post-hoc)

- Within-losing-regime modulation is real but small: PerLTQA events rho(Delta, gap) = +0.151 per-query
  and +0.437 character-level (n=30); tied events lose -19.41 vs untied -9.81. Competition deepens losses
  where SIGN already loses; it does not choose the regime. This independently mirrors the R2 audit's
  asymmetry (events competition-rho +0.398 strongest, profile +0.057 null) via a different metric and
  data path (committed native gap/tie vs Drive-backed per-gold gaps) — corroboration of the SHAPE only.
- The profile-regime intercept (+20.44 with the DENSEST boundaries) requires an unmeasured factor.
  Candidates still open (all UNAVAILABLE in committed caches): per-section strictly-closer-rival LEVELS,
  gold-distance tie-mass LEVELS, Q-magnitude distributions by section. R2 reports only competition SLOPES
  by section, never LEVELS — the level question H1 posed remains unanswered by anyone.

## 6. Post-hoc corrections to HYPOTHESIS.md

None to the hypothesis text (it stays as frozen). Two measurement notes for reuse:
(a) Rule A and Rule B are the same rule on PerLTQA (`tie` ⟺ `gap==0` construction identity, VERIFIED on
all 8265 queries) — future work should not count them twice. (b) Strict accuracy over all queries is
dominated by the 65–79% Delta==0 mass on every benchmark; nonzero-conditional accuracy vs the majority
prior is the informative score, and it is reported throughout.
