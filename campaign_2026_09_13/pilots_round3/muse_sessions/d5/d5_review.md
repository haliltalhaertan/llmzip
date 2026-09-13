**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

[REVIEW] [READ-ONLY; NOT AUTHORITATIVE]

# D5: Adversarial design review of Round-3 (Deney 1/2/4/5 + D1V/D3)

**Procedural note:** this session is write-disabled, so `/tmp/d5/d5_review.md` and `/tmp/d5/d5_details.json` were **not** written. The full content of both is below — the numbered findings are the review body, the JSON block at the end is the structured version. Save from here if needed.

**Scope actually inspected:** Deney-1 report + both details JSONs + both harness scripts (from the raw tree, since the `pilots/...` paths in the brief don't exist in the audit repo — they resolve under `/mnt/c/Users/MDP/dev/llmzip-work/`); `/tmp/d2/{d2_report.md,d2.py,d2_details.json}`; `/tmp/d4/{d4_report.md,d4.py,d4_lme.py,d4_details.json,d4_lme_details.json}`; `/tmp/d1v/{d1v_report.md,d1v_verify.py,d1v_details.json,d1v_run.log}`; `/tmp/d3/{d3_report.md,d3.py,d3_details.json}`; `/tmp/c2/{c2_report.md,c2.py,c2_details.json}`; roadmap `strategy/roadmap_2026-09-13/muse_strategy_roadmap.md`; all three session prompts (`muse_prompt_deney2_tiemass.md`, `muse_prompt_deney5_c2.md`, `muse_prompt_d1v_verify.md`); round-2 `ROUND2_REPORT.md`, `r2d_design_review.md`, `r2v_verification.md`. All arithmetic below was recomputed from the JSONs, not copied from reports.

## FAIL findings (block citation or verdict as written)

**F1 — D2's "provisional predictor claim" hides that its features require gold qrels.**
Severity: FAIL. Evidence: `/tmp/d2/d2.py:55-83` — `tie_mass_at_dgold` and `strictly_closer_than_gold` derive from `dmin` = min distance over gold docs (`dg = d[gidx]`); `d_gold_mean` likewise. Of T's 3 features only `margin` is gold-free; of M's 4 only `top20_entropy` is. The report's honesty section (`/tmp/d2/d2_report.md §7`) declares drop64 gold-informed but never states the *model features* need gold at inference, and §4's "deployable without baseline" invites a deployability misread (true only w.r.t. the RAND baseline, not w.r.t. gold). Consequence: T's AUC 0.798 (verified: test 0.79846, train 0.86656, n=130/161) cannot license a gold-free expectation — and indeed c2's gold-free COMBO drops to 0.686/0.558. The "licenses c2" reading is valid only as *descriptive license to explore*, not predictor validation.
Required correction: add "all T/M features except margin/top20_entropy require gold qrels; no deployable-router claim" to §7; downgrade verdict to "cleared the roadmap kill-bar; tie story graduates to c2 exploration."

**F2 — c2's LoCoMo promote-leg is vacuous; "PROMOTE" fires on letter while failing in substance.**
Severity: FAIL (gate design + verdict framing; the session's §5b honesty paragraph itself supplies the evidence). Evidence: `/tmp/c2/c2_details.json` `promote_gate` = {lme +3.086pp, loco +1.481pp, promote:true}; routing rows show LoCoMo random-abstention mean alone is +1.135pp at α=0.20 — i.e. *random routing passes the "≥+0.5pp same sign" leg without any model*. LoCoMo COMBO test AUC = 0.558 with all 12 univariates in 0.43–0.54: the leg carries zero predictor information. Provenance note: the +0.5pp number is prompt-level operationalization (`muse_prompt_deney5_c2.md:44-46`), not roadmap verbatim (roadmap §c2 says only "replicates on LoCoMo") — pre-declared at session level, but set *below* the null it was meant to beat. Meanwhile §5 states "Decision: PROMOTE" baldly while the qualification sits in §5b — a quotable unqualified PROMOTE exists.
Required correction: disposition must be "gate fired on letter; LoCoMo leg vacuous against random-abstention; PROMOTE is *conditional* on a preregistered follow-up carrying a binding vs-random superiority gate (model gain > random-range max at α=0.20); LoCoMo must not be called a replication." Restructure so §5 contains the qualification, not an appendix to it.

**F3 — Two of D1V's six "cannot-check" items are oversights, not limits.**
Severity: FAIL (scope claim; the recomputed numbers themselves all check out). Evidence: (1) `harness/deney1_loco.py:219-227` contains a fully reproducible split rule (`sha256('deney1loco|{s}|{q}')`, stratified by category, alternate assign) — D1V read this file yet claims membership "cannot" be checked, after performing the *identical* re-derivation for LME (EXACT on s=0/s=7). All inputs (valid qids, categories) are files D1V already reads. (2) `r2c_replicate.py` exists at `round2/session_scripts/r2c_replicate.py` (alongside `r2a.py`, `r2b.py`) — D1V repeated the exact path failure the brief warned about. Consequence: LoCoMo split-integrity (disjoint+complete, balance) is *unverified*, and LoCoMo-protocol independence from R2C is unestablished — the report's "10/10 disjoint+complete" LoCoMo gate rests on harness asserts only.
Required correction: re-run both checks; relabel the list as "not checked," never "cannot-check."

## CAVEAT findings

**C1 — Deney-1 kill aggregation has no uncertainty; win-rates are over-read.**
Evidence: per-split drop64 gaps recomputed `[-1.89,-1.85,+0.78,-3.11,-2.18,+1.14,-0.74,-0.87,-2.26,-1.48]`, mean −1.246083, SD≈1.3pp → across-split SE≈0.4pp, unreported (kill still robust vs +1.0pp, but unquantified). The 10 salts share questions across splits (same 470/1535 reshuffled), so effective N≪10. Secondary LME vs-mean 7/10 (+0.43pp) is noise-consistent under a coin flip (P(≥7/10)=17%) yet narrated as "panel ortalaması düzeyinde." LoCoMo vs-mean 10/10 (+1.11pp) looks strong but inherits the same split-correlation discount.
Required correction: report across-split SE with overlap caveat; soften secondary win-rate language to "nominal, correlation-undiscounted."

**C2 — Bar asymmetry in Deney-1 narrative.**
Evidence: learned is killed vs-best (a selection-lifted bar; report itself quantifies the lift ≈+1.2pp, LoCoMo §), while SPREAD is praised vs-mean (+1.1733pp, 9/10, recomputed) although SPREAD vs-best is 3/10, −0.502pp (recomputed). The decision rule is pre-declared (roadmap line 45, quoted verbatim in the report — provenance confirmed) and procedurally fine; the *framing* applies different bars to different arms on the same data.
Required correction: state both bars for both arms in one table; keep the kill (rule-bound) but drop "geçerli iyi bilinen kol" unless qualified with "vs-mean only."

**C3 — "SPREAD ≈ random" is bar-dependent by construction.**
Evidence: harness `deney1_lme.py:147-154` — SPREAD is one fixed deterministic arm (rank-linspace over train-variance order, eff_k asserted; col uniqueness verified: 45 LME + 42 LoCoMo arms all len==k, unique, ∈0..95). A fixed arm cannot systematically beat best-of-10 unless its edge exceeds selection lift. Vs-mean, SPREAD *does* separate (+1.17pp 9/10 LME; −0.33pp LoCoMo, recomputed −0.3260). "Statistically indistinguishable from random panels" is therefore a property of the chosen bar, not of SPREAD.
Required correction: present SPREAD-vs-mean and vs-best side by side (as C2) and note the fixed-vs-max structural disadvantage.

**C4 — D2 fragility not quantified.**
Evidence: single hash split; binary test n=130 (37 wins / 93 losses); Hanley-McNeil SE(T)≈0.047 (recomputed) — unreported; no CI on T−M (+0.1120, recomputed 0.79846−0.68643); 179/470 (38%) ties excluded so any "predictor" covers only 62% of questions while median gap is exactly 0.00. Threshold provenance is clean (roadmap §c1 + prompt "decision reference") — this caveat is about precision, not legitimacy. No capacity-advantage concern: T wins with *fewer* features (3 vs 4), both linear — credit where due.
Required correction: add AUC SEs + DeLong-style diff CI; state the 62%-coverage limit in the verdict, not just §7.

**C5 — D3 arithmetic is perfect (0/18 mismatches re-derived; counts 14/18+14/18 confirmed) but the report draws no conclusion its own data force.**
Evidence: Spearman drop +0.0971 / alone +0.0754; intersections vs chance (k=64: 45 vs 42.67; k=48: 25 vs 24.00; k=32: 13 vs 10.67) — chance-level; transferred utility *beats* own utility in `LOCO→LME/alone/48` (+1.41pp) and `/alone/64` (+2.17pp, recomputed), proving utility estimates are noise-dominated. Var-row "FAV" is vacuous (src==own by construction; var ordering identical across benchmarks, rho +0.9999) and the FAV rule is lax (−1.10pp vs own still FAV, `LME→LOCO/drop/48` recomputed). Table numbers spot-checked exact (e.g. src 0.1784/own 0.1895/rm 0.1644/rb 0.1728).
Required correction: state the licensed conclusion — "utilities are benchmark-local noise; transfer ≈ chance" — and mark var-row FAV as tautological (or N/A).

**C6 — D4 overstates n=2; seed-collision and subsetting undeclared.**
Evidence: strict-separation booleans all recomputed TRUE on stated seeds (LoCoMo fresh margins 1.1181pp/0.8847pp; LME fresh 44001/44002 exact), gates diff 0.0 — the numbers are fine. But: (a) n=2/arm/benchmark with within-arm spread ~1.2pp — "SURVIVES"/"ordering graduates" language (roadmap line 89's graduation criterion) overreaches; no p-value/CI. (b) Seeds 43004/43005 are *fresh* for LoCoMo but *pilot gate seeds* for LME (fresh = 44001/44002) — same numerals, different meanings, unflagged cross-benchmark hazard. (c) LME "original 43001-03" contrast silently drops gate seeds 43004/43005 (full-5 also fails strict separation — conclusion robust, subsetting undeclared; verified minM>maxR FALSE, minR>maxA FALSE on all five). (d) "Fresh-Q" = fresh Haar rotations, same 1535/470 questions (body clear, title ambiguous). R2D confound honestly declared unresolved — credit.
Required correction: "strict separation holds on 2 fresh draws; confirmatory only"; flag the seed-numeral collision; use all five LME pilot seeds in the contrast.

**C7 — C2 missing precision and ablation.**
Evidence: no CIs on routing gains (LME test fails=52; α=0.20 routes k=45); 10-draw random max is a noisy null with 4-α multiplicity (P≥1 exceedance ≈30% under null — LME exceeds at 3/4 α, suggestive but unquantified); no ablation of COMBO without `margin34_large`/`crowd3_large`, which require full-budget compute and sit inside the "router" that fires the gate (report declares them "analysis features" in §6 but the gate-firing gains depend on COMBO unablated). Univariate small-arm AUCs (boundary_share 0.696, crowd_pm1 0.672) suggest the signal isn't *only* LARGE-driven — which is exactly why the ablation is cheap and required.
Required correction: LARGE-free ablation + gain CIs + formal vs-random test before any preregistration.

**C8 — "Licensed by the roadmap rule" misframes an asymmetric rule.**
Evidence: roadmap line 59 ("Kill c2 if AUC<0.65 or Δ<0.05") and prompt line 65 ("Decision reference") confirmed as provenance — but the rule is a *kill-bar*, and clearing it is not positive validation. Consistent with F1: D2 cleared the bar to *not kill* c2-exploration; "provisional predictor claim licensed" upgrades clearance into endorsement.
Required correction: "cleared the kill-bar" language throughout D2 §4.

**C9 — D1V residual scope gaps (real, minor).**
Evidence: LoCoMo CI seed path (778000+s) not re-executed (seed-constant typos would go uncaught; CIs don't enter kill triggers — low stakes); LME delta64 utility cols unchecked (delta not in kill rule); `HASHES_ROUND3.txt` unverified though trivial — I spot-confirmed the file exists with full hashes matching the report's truncations (`556b67…`, `c2d3c0…`, `2dabcb…`, `7ffa7c…`, `90cae3…`, `c83e47…`), but byte-level `sha256sum -c` remains open.
Required correction: run the three cheap checks; until then cite D1V numbers, not "fully verified."

## NOTE-level (corroboration, no action)

- **N1.** Kill triggers exact: LME mean −1.2460826210826181→−1.25pp, wins 2/10; LoCoMo −0.14953631584987523→−0.15pp, 2/10. Both per-split tables match JSONs to rounding. s9-k64 exception exact (var64 0.4298 vs delta64 0.3998 — the "harmless" characterization holds: *another* arm is worse, so var-worst-fails ≠ pipeline-invalid; but *why* delta64 collapses at s9 is unexplored).
- **N2.** Bootstrap re-selecting best-of-10 *within* each resample (`deney1_lme.py:184-188`) is the correct, conservative-against-learned choice — a fixed-best-seed CI would understate random's edge. Credit; the gap is per-split CIs with no aggregate-level counterpart (C1).
- **N3.** Native anchors bit-consistent across all six sessions (LME 0.5419751773049645; LoCoMo 0.23654714666441054).
- **N4.** D2 RAND seeds 12000–12002 are prompt-declared ("same as pilot"); background W/T/L 63/250/157 (R2A, single-seed) vs 91/179/200 (D2, 3-seed mean target) correctly distinguished; R2B +3.39/+1.62 consistent with roadmap line 5.
- **N5.** Column-set identity (brief §6): Deney-1 vs D2 arms are *not* identical — different k (48 vs 64), seed families (12000s vs 91000s), utility scope (full-data vs train-only), and D2 lacks SPREAD/delta. No claim conflates them; D3's rand panels share Deney-1's s=0 seed family (91000+j) — lineage note, no bug.
- **N6.** No hash files for `/tmp` session outputs (d2/d3/d4/c2/d1v details JSONs) — provenance hygiene for future sessions.
- **N7.** Deney-1 report is Turkish; its quoted kill rule matches roadmap line 45 verbatim — no translation drift.

## (a) Citation-safe as-is

1. Kill-trigger numbers (−1.25pp / 2/10 / −0.15pp) and both per-split tables.
2. D1V's recomputed numbers (24 EXACT); *not* the "cannot-check" framing of items 1–2.
3. D4 per-seed FRs, gate diffs 0.0, strict booleans — cited as "on the stated n=2 fresh draws" only.
4. D3 cell numbers, Spearman rhos, intersections + chance expectations, FAV/FAIL flags *as rule outputs*.
5. C2 routing table, AUCs, base rates; gate firing *on letter*.
6. Roadmap/prompt gate wordings with document references above.

## (b) Claims needing correction before citation

1. D2 "provisional predictor claim" / "licenses c2" (F1, C8) — needs gold-dependence disclosure + "cleared kill-bar" downgrade.
2. c2 §5 "PROMOTE" (F2) — needs embedded qualification + binding re-gate; no "LoCoMo replication" language.
3. D1V "cannot-check" items 1–2 (F3) — relabel and fill.
4. D3 transfer reading (C5) — needs stated benchmark-local conclusion; var-row FAV fix.
5. D4 "SURVIVES"/graduation framing (C6).
6. Deney-1 secondary win-rate narration (C1) and SPREAD framing (C2–C3).

## (c) Three most important missing analyses

1. **Aggregate uncertainty for the Deney-1 kill** — across-split SE with split-overlap correlation + win-rate null under correlated splits. Determines whether the kill evidence is as hard as −1.25pp looks or partly bar placement (the OR-rule is kill-biased by construction: under null, mean-vs-best is negative via selection lift alone).
2. **C2 LARGE-free ablation + gain CIs + formal vs-random test** — determines whether any *deployable* (non-full-budget) signal exists, which is the only thing the preregistered experiment could use.
3. **D2 split-robustness + gold-free-only variant** — multi-split T−M AUC with CIs, and AUC of a strictly gold-free tie model. Determines whether the tie story survives without gold across splits — the direct premise of c2.

```json
{"review":"D5","read_only":true,"authoritative":false,
"findings":[
{"id":"F1","sev":"FAIL","target":"d2_report §4/§7","ev":"d2.py:55-83 gold-indexed features; T test AUC 0.79846 needs gold","fix":"disclose gold-dependence; 'cleared kill-bar' not 'predictor licensed'"},
{"id":"F2","sev":"FAIL","target":"c2_report §5 + prompt gate","ev":"c2_details promote_gate {3.086,1.481,true}; LOCO random-mean +1.135pp passes leg alone; COMBO test AUC 0.558","fix":"conditional PROMOTE with binding vs-random re-gate; no replication language"},
{"id":"F3","sev":"FAIL","target":"d1v_report cannot-check 1,2","ev":"deney1_loco.py:219-227 re-derivable splits; round2/session_scripts/r2c_replicate.py exists","fix":"run both checks; relabel 'not checked'"},
{"id":"C1","sev":"CAVEAT","target":"deney1_report aggregates","ev":"gap SD~1.3pp, SE~0.4pp unreported; 7/10 noise-consistent (p=0.17); correlated splits","fix":"across-split SE + overlap caveat; soften secondary language"},
{"id":"C2","sev":"CAVEAT","target":"deney1_report framing","ev":"learned vs-best (lifted bar) vs SPREAD vs-mean (+1.17pp 9/10; vs-best 3/10 -0.50pp)","fix":"both bars for both arms in one table"},
{"id":"C3","sev":"CAVEAT","target":"deney1_report SPREAD claim","ev":"fixed arm vs best-of-10; harness:147-154; cols verified unique len==k","fix":"note structural disadvantage; bar-dependence"},
{"id":"C4","sev":"CAVEAT","target":"d2_report §4","ev":"single split; test 37/93; SE~0.047; 38% ties excluded; median 0.00","fix":"AUC SEs + diff CI; 62%-coverage in verdict"},
{"id":"C5","sev":"CAVEAT","target":"d3_report §§2-5","ev":"0/18 mismatches; rho~0.08; overlap~=chance; src>own +1.41/+2.17pp; var FAV vacuous","fix":"state benchmark-local conclusion; fix var rows"},
{"id":"C6","sev":"CAVEAT","target":"d4_report §§2-3","ev":"n=2/arm; margins 1.12/0.88pp; seed collision 43004/05; 5-seed subset undeclared","fix":"confirmatory-only language; flag collision; full-5 contrast"},
{"id":"C7","sev":"CAVEAT","target":"c2_report §§3-4","ev":"test fails 52; 10-draw max + 4-alpha multiplicity; no LARGE-free ablation","fix":"ablation + gain CIs + formal vs-random test"},
{"id":"C8","sev":"CAVEAT","target":"d2_report §4 wording","ev":"roadmap:59 kill-bar + prompt:65 'decision reference' confirmed","fix":"'cleared the kill-bar' language"},
{"id":"C9","sev":"CAVEAT","target":"d1v_report scope","ev":"LOCO CI seeds, delta64 cols, HASHES_ROUND3.txt open (existence spot-confirmed)","fix":"run the three cheap checks"}],
"citation_safe":["kill numbers + per-split tables","d1v recomputed numbers (not framing)","d4 per-seed values as n=2 draws","d3 cell numbers as rule outputs","c2 tables + gate-on-letter","gate wordings with refs"],
"missing_top3":["aggregate uncertainty for kill (overlap-aware)","c2 LARGE-free ablation + gain CIs + formal vs-random","d2 multi-split + gold-free-only AUC"]}
```

D5_BEGIN — D5 adversarial review complete (READ-ONLY; /tmp/d5 not written — session write-disabled; content above is the deliverable).
Verdict sketch: numbers everywhere verify to the digit (kill triggers, 18/18 D3 cells, c2 routing, D4 separations, D1V spot-checks); gate provenance confirms for all three gates (roadmap + prompts). The failures are all interpretive/dispositional: D2's gold-informed "predictor" (F1), c2's vacuous LoCoMo leg with a quotable unqualified PROMOTE (F2), D1V's two false "cannot-checks" (F3). Top correction priority: F1+F2 rewording, then the three missing analyses (aggregate kill uncertainty; LARGE-free c2 ablation; gold-free multi-split D2). — D5_END
