[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# REPORT — the projector is common-mode; the head-to-head storage objection collapses

PREPARED, NOT ACCEPTED. Interim commit (deliverables): see stdout summary for
final branch sha. Namespace: `research_commonmode_cost_2026_09_14/` (additive
only; no existing file touched).

## What was produced (new files, own namespace only)

- `STATUS.md` — plan + running receipts.
- `COMMON_MODE_CLASSIFICATION.md` — Q1 (what float96 IS: same fitted
  pipeline, decisive lines quoted) + Q2 (component table: 100% of ~44 MB is
  COMMON-MODE; SIGN-ONLY / FLOAT-ONLY / QUERY-TIME-ONLY pipeline columns all
  empty; arm-specific codebooks listed separately).
- `RECOMPUTED_COMPARISON.md` — Q3 tables: (a) marginal, (b) index-only
  effective, (c) full-pipeline effective at N=500 and N*=118,872; five
  survive/flip rulings.
- `VERDICT.md` — Q4 (honest retrieval footprint per arm; saving at every N;
  per-archive vs shared with the L-088 prohibition cited and priced) + Q5
  (SPLIT verdict: head-to-head objection COLLAPSES, absolute-footprint
  warning SURVIVES; exact HR ruling needed with per-option numbers).
- `verify_commonmode.py` + `evidence/results.json` — stdlib verifier, ALL 14
  CHECKS PASSED (6 source assertions A1–A6, 8 arithmetic C/B/D checks).

## What was verified (each with locator)

- Same-Y-same-mu construction + 1e-12 abort gate: T4C2 script `:257-287`
  (A1–A3 PASS from bytes). Query needs fitted state (A3). Fit API takes
  archive texts only; cross-question fit prohibited (adapter `:147,363-367`;
  A4–A5 PASS). E1 consumes one C/qC pair, sign = where(C≥0) (A6 PASS).
- Median eff 88,886.36235, total 44,220,235, range, N=443–551 (B1–B2 PASS);
  components sum EXACTLY to total on median archive 078150f1: s96 37,634,304
  (85.11%), sv 5,041,664 (11.40%), vocab 1,151,987 (2.61%), IDF 391,896
  (0.89%), mu 384 (B3 PASS).
- Frozen 470 N: min 396, max 616, mean 492.78, total 231,606 (C1 PASS); OPQ
  index-only panel mean 287.6889713064 reproduced to 10 decimals (C2 PASS).
- SIGN-full < FLOAT-full at every probed N by 372−33/N (D2 PASS);
  SIGN-full < PQ-full everywhere (D3 PASS); N*=118,872 (D1 PASS);
  global-sharing lower bound 202.93 independently reproduces Attack 4 (D-supplement).
- CLAIM vs VERIFIED discipline kept: L-088 wording, prereg draft rules, and
  faiss S0 values are CLAIM (read from branch bytes, not re-executed);
  everything in results.json is VERIFIED recomputation.

## What could NOT be done, and why

- No complete serialized per-arm package (index S0 + pipeline + headers in
  one receipt) exists in the bytes — the prereg §4 gate is unbuilt. My
  full-pipeline table therefore ADDS independently-receipted parts
  (P_med + S0); a genuine single-package measurement could only move these
  UP (headers), never below the index-only floor. Direction of any error is
  against SIGN, which strengthens the "SIGN cheapest" finding.
- No retrieval-quality-under-cheapened-projector question touched (Q: does
  f16/zlib preserve recall?) — UNAVAILABLE-UNDER-SEAL (needs Task4F1
  authorization; correctly not probed).
- The ~234× figure recomputes as 231.47 under median convention (brief's
  value is convention-adjacent; immaterial). Frozen production artifact size
  remains unfound (re-fit proxy used throughout, as labeled).
- Seal compliance: no `--mode run/finalize`, no `run_archives` /
  `evaluate_archive` / `finalize_results`, no HMAC key, no authorization, no
  BEAM corpora/queries/labels/embeddings opened or fetched. Only inputs:
  public code blobs, committed JSON/CSV measurement artifacts, E1 caches'
  code (not their retrieval outcomes). E1 benchmark caches were authorized
  but unneeded — the E1 geometry CORE source alone settled the E1 point.

## Headline (for the skeptic)

The attack tested TRUE: the projector is common-mode, so the "234× worse"
comparison inverted reality — SIGN96 is the cheapest arm at every archive
size under every honest accounting (by 372 B/vector over float, ~197 B over
PQ at N=500). But the deployment warning is untouched: every arm stores
~89 kB/vector at programme scale, and "12 bytes" as a total-footprint
quotation remains false. Both statements are now receipted; the remaining
gap is a definitional ruling, stated exactly in VERDICT.md.
