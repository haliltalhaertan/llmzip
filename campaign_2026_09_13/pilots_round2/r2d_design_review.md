# R2D adversarial design review — round-2 outputs

Read-only review. All numeric claims below were recomputed from the evidence files (`round2/*.md`, `round2/wsl_details/*.json`, `REPORT.md`, `01_CANONICAL_STATUS.md`, both frozen protocol scripts, `per_axis_matrices.npz`).

## FINDINGS

| ID | Area | Verdict | Evidence |
|---|---|---|---|
| F1 | R2B prose | FINDING | Two false claims (see below) |
| F2 | R2B hygiene | OK | Train-only proven by recompute |
| F3 | R2B headline | CAVEAT | Vs-mean flatters; wide seeds |
| F4 | R2B candor | OK | Overfit + SPREAD disclosed |
| F5 | R2B gaps | CAVEAT | SPREAD cols hidden; minor items |
| F6 | R2C numbers | OK | Gate exact; tables match |
| F7 | R2C fidelity | CAVEAT | Construction unverifiable |
| F8 | R2A numbers | OK | All recomputes match |
| F9 | R2A mechanism | CAVEAT | Causal overreach; 1-seed base |
| F10 | Labels | FINDING | R2A, R2C unlabeled |
| F11 | Consistency | OK | Except F1; sums check |
| F12 | Free hunt | CAVEAT | Best-seed table; n=3 |

### Q1 — R2B design hygiene: OK (F2), with minor gaps (F5)

- **Split rule verified exactly.** Recomputing `train iff sha256(qid) first hex even` over the reported qid lists: 0 violations, disjoint, 239/231, total 470. Qid-derived ⇒ gold-free and content-free. Defensible for exploratory work. Caveats: single split only (no split-robustness), knowledge-update skew 43-vs-29 (honestly disclosed in md), test half harder than train (0.5190 vs 0.5642 — disclosed; harmless for within-test arm comparisons).
- **Train-only selection proven, with teeth.** `per_axis_matrices.npz` is per-question (470×96 + qids), so train-only aggregation is possible — and I confirmed it actually happened: recomputed train-mean drop-loss top-5 = [23,72,88,2,58] with mean 0.00197375, matching the reported utility **exactly** (mean to ~1e-16); full-data and test-only rankings both differ, so the check discriminates. Delta top-5 likewise matches train-only exactly and differs on full data. Drop64 cols equal the train-loss top-64 set (one adjacent near-tie swap at positions 16/17, values equal to 1e-16 — consistent with utilities recomputed from raw pkls via a slightly different float path, not copied from the npz; corroborating, not concerning).
- **Overfit gap: reported.** "drop64 train FR 0.5623 (≈ train native) vs test 0.4838" is in the md. Present.
- Minor (F5): SPREAD arms' `cols` in `r2b_details.json` is the sentinel `[-1]`, so SPREAD construction is unverifiable from the evidence (only outcome-equality SPREAD48≡SPREAD64 is checkable — confirmed bit-identical FRs). The `alone` utility's 5th pick (27 over raw-train 14; first four agree up to an adjacent swap) can't be reproduced from the npz, leaving a small provenance gap for that arm. The W/T/L comparator ("vs random mean") lives only in the json key name, not the md.

### Q2 — R2B statistical claims: CAVEAT + FINDING (F1, F3)

- Headline "+3.39pp vs mean" is arithmetically correct (0.48378 vs 0.44984) but flattering: RANDOM64 seed range is 0.4342–0.4676 (3.34pp wide), so the honest co-headline is **+1.62pp vs best seed**. The md does disclose all three seeds in Notes — good — but leads with the mean.
- **F1 — two factually false prose claims in `r2b_learned_selection.md`:**
  1. *"One arm, drop64, beats the RANDOM64 mean"* / *"All other learned arms are at or below their k-matched random mean"*: **alone64 test FR is 0.47154, gap +2.17pp above the mean** (table and json agree). So two arms beat the mean, not one.
  2. *"drop48/alone64 sit inside their random-seed ranges"*: alone64 (0.47154) **exceeds the best RANDOM64 seed** (0.46760) — it beats all three seeds (+0.39pp vs best), confirmed in json. (drop48's "inside" half is true.)
- Both errors understate the learned-selection success rather than oversell it, but they are factual errors in the headline results; the "one arm" framing must be corrected to two (drop64, alone64).
- SPREAD64≡SPREAD48 honestly disclosed with mechanism (stride-2 caps at 48). Genuinely good candor, including noting the gap differs only via reference mean.

### Q3 — R2C protocol fidelity: gate OK, construction CAVEAT (F6, F7)

- Gate is strong: native diff 0.0 exact; Haar mean diff −2.9e-15 is rounding-only (anchor kept 14 decimals). Seeds, cohort (1535 audit-valid), and per-category n-sums (282+320+92+841=1535) all consistent.
- Budget table (9 spot cells), block means (RANDPAIR .213006 / MATCHED .236101 / ANTI .193715), strict-separation inequality (min MATCHED .23023 > max RANDPAIR .22029 > max ANTI .19937), and per-category rows all match `r2c_details.json` to rounding.
- **But the asked fidelity questions cannot be verified from these files.** No code ships with round-2 (only `/tmp/r2c/` paths, out of scope), and `r2c_details.json` carries no column lists or hashes for the new constructions. So "same rng draw order, QR+sign-fix, Q-blocks bit-identical to RANDPAIR" and "variance rankings per-conversation (archive-local)" are **asserted in `protocol.interpretation_notes`, not evidenced**. Note the subtlety: the frozen T4D script has no matched/antimatched arms at all (only `hspec`-random pairing) — these are novel constructions in the pilot-E4 lineage, so "verbatim mirror of T4D" covers the shared pipeline (which the gate validates), not the new pairings. Verdict is CAVEAT (unverifiable), not a failure finding.

### Q4 — R2A mechanism claims: numbers OK, language CAVEAT (F8, F9)

- All numbers verify by recompute from `r2a_per_q.json`: gates 0.0, W/T/L 63/250/157, tie-metric means (gold rank 18.65 vs 20.96, strictly-closer 16.03 vs 18.13, cluster 6.40 vs 6.98, boundary rate 0.460 vs 0.426, dup fraction 0.0235), exactly 34 hard losers with gold-counts {1:31, 2:3}, both spot examples match per-question rows (loser 001be529: rank 18.15/14 closer/cluster 11 vs RAND 0/0/1; winner gpt4_468eb063 mirrors as described).
- **Causal overreach (F9).** *"The discriminative signal lived in low-variance axes"* is causal language for what the data support only descriptively: on the decisive subset TOP48 buries golds that RAND keeps closest. Against a general tie-collapse mechanism stand the md's own correlations (≈0 for tie-cluster 0.0198 and dup fraction −0.037) — the round-1 REPORT correctly left the mechanism "OPEN"; R2A's sentence closes it without new identifying evidence. Aggregate BOT48 > TOP48 supports "low-variance axes carry signal" descriptively; "lived in" claims more.
- Clarity: "Hard losers average: rank 10.8/cluster 6.1" matches the all-34 average (10.79/6.15, RAND side 0.64/1.32 ✓) but reads as describing the 10 listed losers (whose TOP rank averages 21.4). Ambiguous denominator.
- Baseline caveat missing: W/T/L vs **single-seed** RAND48_s0 with no seed-dispersion warning, while round-1 showed a 3.5pp range across 5 seeds at k=48 — the flip counts inherit that seed noise.

### Q5 — Cross-document consistency: OK except F1 (F11)

No md-vs-json numeric mismatches anywhere: R2A aggregates/WTL/per-type/corrs/losers/winners all exact; R2B all 15 test FRs and 15 gaps match to rounding (≤4e-5); R2C as above. Internal sums check (R2A per-type n/W/T/L = 470/63/250/157; R2B qtype 239/231). The sole inconsistency is F1's prose-vs-table contradiction inside R2B itself.

### Q6 — Label/limits hygiene: FINDING (F10)

- R2B: labeled (`[EXPLORATORY] [NOT PREREGISTERED]`, plus json labels). Pass.
- R2A: **no exploratory/not-preregistered/not-for-citation label anywhere**, no limits section, closes with "Nothing failed to reproduce" — reads citation-ready. Missing: single-benchmark scope, seed-dispersion, descriptive-only status.
- R2C: **no exploratory label** in md or json; "replicates strictly" claims from n=3 seeds without a scatter caution.

### Q7 — Free hunt + what cannot be checked (F12)

- R2C per-category table compares native against MATCHED_seed43003 — the best-of-3 matched seeds on aggregate — per category, without disclosing that selection step. Cat2/Cat4 "best beats native" (+0.5/+1.2pp) is best-seed-on-aggregate cherry-picking; with matched-seed range 1.2pp and anti range 1.7pp, n=3 cannot support "strict" language. (Credit: the k16 nuance — "spread beats top does not hold at k16" — is honestly reported.)
- **Cannot be checked from these files:** any code-level claim (R2C QR/draw order, R2B eval pipeline on test, R2A tie-metric code — no scripts in evidence); whether R2B test evaluation reused the frozen pipeline verbatim (gate covers natives only); provenance of the `alone` utility's 5th pick; SPREAD construction (sentinel cols); anything about generalization beyond these benchmarks.

## Required corrections

1. R2B md: replace "one arm" framing — two learned arms (drop64 +1.62pp, alone64 +0.39pp) beat all three k=64 seeds; headline both vs-mean and vs-best-seed gaps; fix or delete the "sit inside seed ranges" sentence for alone64.
2. R2A md: add `[EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION]` header + limits (single benchmark, single-seed baseline with 3.5pp round-1 dispersion, descriptive-only); soften "signal lived in" to subset-descriptive language; clarify "hard losers" denominator (all 34).
3. R2C md + json: add exploratory labels; qualify "replicates strictly" with n=3 seed scatter; disclose best-seed selection behind the per-category table.
4. R2B json: replace SPREAD `cols: [-1]` with real columns or an explicit "construction not logged" note.

## Before any preregistration (carry-over)

Single benchmark per finding (LME-470 for R2A/R2B; LoCoMo-1535 for R2C); exploratory, not preregistered; random-seed dispersion (3.5pp at 48-bit, 3.3pp at 64-bit, wide R2C block ranges); single arbitrary train/test split with KU skew and harder test half; learned utilities are gold-informed on train (disclose as E2/E3-class analysis inputs); no causal mechanism claim licensed; exact gates (R2A 0.0, R2B 1.1e-16, R2C native 0.0) cover shared pipelines only, not the novel R2C pairings; NOES items from round-1 §5 remain untouched-or-disclosed as applicable.
