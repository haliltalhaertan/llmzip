[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# REPORT.md — storage accounting pilot, final report (PREPARED, NOT ACCEPTED)

This work is PREPARED, NOT ACCEPTED. It seals, ratifies, and closes nothing.
Task4F1 SEAL held throughout (receipt in IMPLICATIONS.md §3).

## What was produced (all inside `research_storage_accounting_2026_09_14/`)

- `STATUS.md` — written first; plan, seal, and skeptic pre-commitment.
- `COST_MODEL.md` — the accounting model: `total(N) = S + 12N`,
  `effective(N) = 12 + S/N`, `N* = S/(B-12)`; instantiated at programme N
  (396/492.78/616), declared-only BEAM tiers, whole-benchmark totals, and all
  four projector encodings. Every input carries a locator.
- `RECONCILIATION.md` — verdict: 12 B and 88,886 B do NOT contradict; they are
  the marginal cap and the effective cost the same decision defines. Both
  definitions quoted verbatim. Honest-iff conditions stated; one recommended
  action list for the Head Researcher (mandatory effective reporting, the
  one-sentence qualifier, and the scoping question the ~234× ratio forces).
- `verify_cost.py` + `evidence/cost_results.json` — stdlib-only recomputation,
  9/9 checks PASS (run 2026-09-14; stdout captured in session). faiss figures
  enter as CITED CONSTANTS with locators, never recomputed. Sensitivity covers
  float16 projector, globally-shared (prereg-excluded) projector, 10× archives,
  and index-only arm ranking.
- `IMPLICATIONS.md` — symmetric cases, re-wording list with locators, and an
  explicit do-not-overclaim list.
- This `REPORT.md`.

## Headline numbers (all recomputed from declared inputs)

- Median shared projector (float32): 44,220,235 B/archive; median effective at
  programme scale: 88,886.36 B/vec (both VERIFIED against PROJECTOR_BYTES.json
  bytes; arithmetic rechecked 9/9 PASS).
- Whole LongMemEval: SIGN96 side ≈ 20.8 GB vs raw float32 ≈ 88.9 MB → ~233.7×.
  The 12-byte codes are ~0.013% of the persisted bytes.
- True beats-float32 break-even: N* = 118,872 vectors/archive (float32
  projector) — ~240× programme archives. The brief's "~3.7M" is S/12, the
  marginal-parity point (effective = 24), not a victory over floats.
- The framing survives total-accounting ONLY under a globally-shared projector
  (202.9 B/vec) — the deployment the preregistration explicitly excludes.

## What was verified vs not

- VERIFIED (read the bytes / ran the code): projector JSON aggregates and
  medians; budget decision + finding texts; EVIDENCE.json sizes, slopes,
  trainability, and archive_cost; replay equality with EVIDENCE; revision arm
  table + no-amortization rule + mandatory-effective rule; old-prereg BEAM
  tiers as declared-only; ledger "twelve-byte race" sentences present on main;
  every number in COST_MODEL.md recomputed by verify_cost.py (9/9 PASS).
- CLAIM (document says it; relied on with label): audit's inventory
  completeness, byte-exact re-derivation, and F-01–F-07 observations; pilot's
  component shares (85.1/11.4/2.6/0.9%); retrieval deltas and mechanism
  history from programme context (not re-examined by design).
- Could NOT do (and why): LoCoMo per-archive effective costs — no cited source
  gives LoCoMo per-archive N (question counts only); float16+zlib raw baseline
  — no cited source measures compressed raw vectors (script states exactly what
  would be needed); BEAM-scale S — corpus absent and must not be fetched (SEAL);
  any retrieval-quality statement — out of scope and sealed.

## Assumption most damaging to the conclusion, and its test

Pre-committed in STATUS.md: that the projector is SHARED across archives
rather than per-archive. Tested in sensitivity analysis: global sharing gives
202.9 B/vec and beats raw float32 — headline reversed. It does not rescue the
programme framing, because archive-local fitting is the preregistered
deployment ("Never amortize…", VERIFIED), so the reversal lives in a forbidden
counterfactual. A smaller correct deliverable was preferred throughout; open
ends are labeled UNAVAILABLE, not filled.

Local commit sha: `f1829b9` (namespace commit on branch
`muse/track1-storage-cost`; this sha line added in the follow-up commit).
