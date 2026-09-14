[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# REPORT — PerLTQA reversal characterisation (PREPARED, NOT ACCEPTED)

## What was produced (all inside `research_perltqa_reversal_2026_09_14/`)

- `STATUS.md` — written first; seal/additive receipts appended through the session.
- `REVERSAL_FACTS.md` — first-hand re-derivation of all programme numbers.
- `HYPOTHESIS.md` — H1/H0/P64-baseline, frozen BEFORE the cross-benchmark leg (unedited since).
- `analysis.py` — stdlib-only recomputation; reads E1 caches via `git show` (no checkout);
  `python3 analysis.py --parts all --out evidence/results.json` reproduces the bundle.
- `evidence/results.json` — full numeric evidence (facts, geometry, h1_perltqa, xbench_*).
- `CROSS_BENCHMARK_TEST.md` — adversarial test incl. falsification scorecard (post-hoc notes separate).
- `VERDICT.md` — plain verdict + single next decisive measurement.
- This `REPORT.md`.

## What was verified first-hand (VERIFIED = ran/read the bytes)

1. Input identity: PerLTQA `results.json` SHA256 `ec9b8b2c…958` matches E1's claimed hash exactly;
   REALTALK `details.json` hash matches too.
2. Section deltas CONFIRMED to ≤1e-14: profile +20.43543543543544 (333), social -0.8056872037914609
   (844), events -12.411412793373222 (4346), dialogues -1.4762730808814364 (2742); overall
   -6.275007959803608; composition residual -1.15e-14.
3. Within-archive flip counts CONFIRMED field-for-field (30 chars; events<0 in 30/30; profile>0 in
   23/30; joint flip 22/30; 87/115 same-sign) — archive-only explanation REFUTED first-hand.
4. Frozen headlines reproduced without copying: LME +10.037943262411346 (15 decimals, 470/470 join),
   REALTALK +5.224102217719238, E1 rhos (tie-vs-Delta profile +0.2475/events -0.3486; P64 fractions).
5. H1 KILLED: level orderings backwards/non-monotone on all three testable benchmarks; per-query rules
   below majority priors in 7/7 comparisons; rhos null-to-tiny with inconsistent signs. H0 (gold
   multiplicity) killed immediately (profile/events/social 100% single-gold). LoCoMo per-query leg
   unavailable — recorded with exact file-level evidence, not waved through.

## What could NOT be done and why

- Query norm, participation ratio, axis alignment, gold-doc norm/spread, float-side margins:
  UNAVAILABLE-UNDER-CACHE-GAP. The eval-time `/tmp/b3b/cache_*.pkl` vectors were never committed;
  E1 checkpoint §8 and the R2 report confirm the full per-query V2 rows are still pending. No vectors
  were reconstructed (that would violate the no-refit rule and the seal posture).
- LoCoMo per-query H1 test: no committed per-query centered-float surface exists in git
  (`taskC_LoCoMo_perq.json` has 5 arms, no FLOAT); R2 numbers cited as CLAIM only.
- No BEAM/Task4F1 material touched; 4F1 seal steps deliberately not executed (would have stopped
  and recorded — none arose since all reads stayed in the E1 carve-out).
- Minor source discrepancies noted, none load-bearing: 140 (not 137) remote refs; 8 (not ten)
  `origin/research/e1-*` branches.

## Local commit

Analysis + evidence + 5 docs committed to own branch `muse/ultra-perltqa-mechanism` as
`db09ecb92cbd11c67e634189ce2c9b4e4fbc9f35` (7 files, +2947). This REPORT.md follows in a second
namespace-only commit. NEVER pushed; `main` untouched; no checkout performed at any point.
Head Researcher owns `docs/CONTINUITY_LEDGER.md` / `ops/CURRENT_STATE.json` — both untouched.
