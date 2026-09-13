# 01c — ROUND-3 ADDENDUM (2026-09-13): roadmap Design-1 attack + mechanism round

**Labels: [LOCAL EXPLORATORY PILOTS — ROUND 3] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

Round 3 executed the first experiments from the programme's own roadmap (produced by two strategy
sessions on 2026-09-13). Method: Deney-1 robustness run in the local frozen harness (both
benchmarks; Windows venv, pinned stack), then five independent Muse sessions — D2 (tie-mass
analysis), D4 (fresh-Q confirmation), c2 (gold-free predictor + adaptive routing), D1V (independent
recomputation), D5 (adversarial design review). All gates EXACT; every review finding was
dispositioned (`pilots/axis_attack_2026-09-12/round3/muse_sessions/ERRATA_ROUND3_D5.md` + banners).
Full detail: `pilots/axis_attack_2026-09-12/round3/` (ROUND3_REPORT.md + DENEY1_REPORT.md + RUN_LOG.md
+ details JSONs + per-session reports/code).

## Headline results

1. **Deney 1 — the learned-selection premium is KILLED** (pre-declared gate; 3/3 triggers fired).
   10 stratified splits × 10 fresh random seeds per split; primary bar vs the BEST seed.
   LME `drop64` **−1.25 pp** (wins 2/10), `alone64` −3.15 pp (0/10); LoCoMo `drop64` **−0.15 pp**
   (2/10). Overlap-aware across-split bootstrap CI of the LME mean gap: **[−2.00, −0.41] pp**
   (P(mean > +1.0 pp) = 0.0000). The round-2 single-split "+1.62 pp vs best of 3 seeds" was
   seed/split luck. Consequence: the learned arm is EXCLUDED from the twelve-byte budget arm table
   (pre-declared gating); spread/random panels take its slot. Side-finding: the repaired SPREAD64
   (true rank-linspace, eff_k==k asserted) sits at +1.17 pp vs-mean (LME, 9/10) but −0.50 pp vs-best
   (3/10) — a fixed arm cannot beat a best-of-10 max without a real edge; both bars are reported.
2. **Deney 2 (c1) — tie-mass decomposition answers the separation paradox** (gold-informed
   mechanism; NOT a deployable predictor). Held-out flip-prediction AUC(T)=0.798 vs AUC(M)=0.686
   (Δ=+0.112; the pre-declared kill-bar 0.65/0.05 was cleared — "non-kill", not endorsement).
   The tell: docs *strictly closer than gold* 0.55 (wins) vs 5.51 (losses); tie-mass 1.87 vs 4.50 —
   while mean-distance statistics are identical (23.918 vs 23.905). `gold_bucket_size ≡ 1`:
   duplicate-code collapse plays no role at gold level.
3. **Deney 3 — axis-utility structure is benchmark-local.** Spearman LME↔LoCoMo +0.097 (drop) /
   +0.075 (alone); top-k intersections at chance. The variance ordering "transfers" (rho 0.9999)
   but is the embedding's fixed variance profile, not task signal — and the var arm is bad on both.
   Licensed conclusion: **transfer ≈ chance**; drop transfers only modestly at k∈{48,64} (below own
   utility, above random-mean); alone mostly fails; var-row FAV is tautological (src==own).
4. **Deney 4 — fresh-Q mixing confirmation.** Strict separation survives fresh rotation draws on
   both benchmarks (LoCoMo min(M)=0.22966 > max(R)=0.21848 > max(A)=0.20732; LME fresh separates
   more cleanly than the original seeds). **Confirmatory only (n=2)**; the R2D pairing/assignment
   confound remains unresolved; seed-numeral collision flagged (43004/05 are LoCoMo-fresh but LME
   gate-seed numerals; the LME fresh set is 44001/02).
5. **c2 (Deney 5) — gold-free failure predictor + adaptive budget routing is CONDITIONAL.**
   Gate fired on its letter (LME +3.09 pp, LoCoMo +1.48 pp @ α=0.20) but the LoCoMo leg is
   **vacuous vs random-abstention** (random alone gains +1.135 pp; COMBO AUC 0.558). "PROMOTE" is
   conditional on a future preregistration carrying a **binding vs-random superiority gate**
   (model gain > random-range max @α=0.20); prereg also requires a LARGE-free ablation + gain CIs +
   a formal vs-random test.

## Verification and review dispositions

- **D1V (independent recomputation):** 24/25 EXACT, 0 DIFF from raw artifacts; kill triggers
  re-derived to the digit. (F3 closed two overstated "cannot-check" items — see
  `round3/muse_sessions/d5/f3_rechecks.txt`: LoCoMo split counts+balance all-10 verified; 5
  nonzero-FR test qids recomputed EXACT; delta64 cols EXACT; manifests 6/6.)
- **D5 (adversarial design review):** every number verified; 3 FAIL + 9 CAVEAT — all dispositioned
  in ERRATA + per-session banners. Missing analyses (pre-preregistration candidates): kill OR-rule
  null simulation; c2 ablation package; D2 multi-split + fully-gold-free AUC.

## Limits (on top of 01 §G)

- D2 model features require gold qrels (mechanism analysis only; the deployable claim was tested
  and NOT supported by c2). D4 is confirmatory n=2. c2's LoCoMo leg does not replicate. LoCoMo
  split membership lists are not persisted in JSONs (counts + spot checks only). Round-3 kill rule
  and gates were pre-declared at session level (roadmap; quoted verbatim in DENEY1_REPORT.md), not
  by the frozen programme. Frozen accepted tasks (4C1–4D) untouched; Task 4F1 boundary untouched.

## Files (this bundle)

- `pilots/axis_attack_2026-09-12/round3/` — DENEY1_REPORT.md, ROUND3_REPORT.md, RUN_LOG.md,
  deney1_{lme,loco}_details.json, deney1_loco_peraxis.npz, HASHES_ROUND3_BUNDLE.txt,
  `muse_sessions/{d1v,d2,d3,d4,c2,d5}/`, ERRATA_ROUND3_D5.md, f3_rechecks.txt.
- `round3_sources/` — harness scripts (`deney1_lme.py`, `deney1_loco.py`, `f3_rechecks.py`,
  `missing1_kill_null.py`) and the eight session prompts.
- `verify_round3.py` — stdlib-only checker (run from bundle root).

## Missing analyses (D5 follow-ups) — completed same day

Three D5-required analyses closed the adaptive line: **m1** kill-null — a no-edge arm's expected
vs-best-of-10 gap is **−1.62pp (LME) / −1.20pp (LoCoMo)** (selection lift), and drop64 sits at the
**57th/89th percentile** of that null: the kill is data, not bar placement; the rule behaves as a
valid premium detector. **m2** D2 multi-split — the tie model is robust (AUC 0.821, Δ(T−M) +0.162,
10/10 splits) but a **fully gold-free** model clears 0/10 splits ≥0.65: the premise of c2 fails.
**m3** c2 ablation — formal vs-random (200 draws, Bonferroni): LME α=0.20 inside noise
(p_bonf 0.18); LoCoMo inside noise at all α → **c2 NOT prereg-ready**. Details + files under
`round3/missing_analyses/`. Consequence: the adaptive/router direction closes; the twelve-byte
budget race becomes the main programme line.
