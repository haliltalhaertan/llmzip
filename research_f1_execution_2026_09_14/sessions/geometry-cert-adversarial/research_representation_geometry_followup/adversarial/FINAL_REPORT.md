# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# FINAL REPORT — adversarial soundness suite for rank-cert repair

## Outcome

Delivered an additive, deterministic adversarial suite in
`research_representation_geometry_followup/adversarial/` (own directory only;
no production repair implemented, no candidate branch read). The suite FAILS
on the archived v2 exactly where the audit says it must (BULGU-1/BULGU-5
blocker reproduced from independent truth), passes sound v2 outputs, and
separates safety (soundness) from completeness (usefulness) bars.

## Exact v2 failures (archived `certify_v2.py`, sha pinned in results_v2.json)

Runner: 41 cases, **5 safety FAILs** (runner exit 1):

- `poc_K100`, `poc_K1000` — false `ISOLATED_TIES/-1` on a VARIES case
  (independent truth `{5/4:+1, 3/2:+1, 7/4:0, 5/2:-1, 4:-1}`); BULGU-1.
- `poc_reversed_K100` — mirrored false `ISOLATED_TIES/+1` (reversal is no cure).
- `invalidJ_empty` (`L==R`) — `STRICT/0` vs single-point truth `-1`.
- `invalidJ_inverted` (`L>R`) — silently certifies inverted J as
  `ISOLATED_TIES/-1` (v2 never validates J order).

36/41 pass safety on v2, incl. honest-budget twins (K=1/K=10 → sound VARIES),
both tangents, common-zero VARIES, endpoint ties, persistent, strict and
two-exact-roots searched classes, all 24 fuzz rows. Archived original
(`verify_orig_copy.py`) returns honest `UNRESOLVED` on the POC — sound
unknown, the posture a repair must preserve.

## Files (all under `research_representation_geometry_followup/adversarial/`)

- `truth.py` — independent integer-cross-product comparator + convolution
  polynomial route (never calls `v2.cmp_rank`).
- `oracle.py` — own Sturm counter + rational-root theorem + closed
  classification (Sturm-0 on every subinterval; sampling never proves absence).
- `repro_bulgu1.py` — exact-path import reproduction (exit 0 = BUG EXISTS).
- `build_corpus.py` → `cases.json` (41 frozen cases: POC K∈{1,10,100,1000},
  reversed, realizable/abstract tangents, common zero, endpoint L/R ties,
  P≡0, 3 invalid-J, 3 searched classes, 24 seeded fuzz) + `corpus_receipt.json`.
- `validate.py` — guarantees G1..G5 (directions vs frozen truth, genuine
  ties, tie/bracket coverage + crossing evidence, unknown-stays-unknown,
  invalid-J robustness).
- `run_suite.py` — collector (`--target`/`GATE_UNDER_TEST_PATH`, no skips,
  target faults are FAILs) → `results_v2.json`.
- `test_soundness.py` — 12/12 PASS (truth replay 157 pts, oracle reclosure
  57 intervals, M1 forged POC cert, M2 omitted root, M3 crossing-as-touch,
  M4 endpoint masking, M5 UNRESOLVED→STRICT flip, 13 positive controls,
  always-STRICT canary 32/41 FAIL, always-UNRESOLVED safety-PASS/completeness-FAIL,
  collector invariants + honest skipped-budget pin, results_v2 consistency).
- `ADVERSARIAL_SPEC.md` — acceptance bar for a future repair.
- `receipts/` — before/after hashes, manifest checks, per-phase JSON + stdout logs.

## Test invocation (exact; single thread; no bytecode)

```
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python3 -B build_corpus.py                                  # exit 0
python3 -B run_suite.py --out results_v2.json               # exit 1 (5 unsound, expected)
python3 -B test_soundness.py                                # exit 0, 12/12
python3 -B repro_bulgu1.py                                  # exit 0 (bug exists)
```

## Corroboration (second routes)

- Point truth: integer cross-products vs archived `cmp_rank` — agree on all
  157 frozen points (consistency, not unsoundness proof).
- Polynomial route: convolution coefficients == archived `P_coeffs` on all cases.
- Oracle vs archived primitives: Sturm 57/57, rational-roots 34/34 agree.

## Limitations (explicit)

- Finite corpus: no "certified safe generally" claim; fuzz is supplemental.
- Same model family as package authors: partial independence only, stated
  in every report header.
- Runner loads targets in-process (no subprocess isolation/timeout);
  repaired APIs with new status names will be flagged unknown-status (strict).
- **NOT YET AUDITED V3**: no verdict on any repair; reviewer runs the actual
  v3 through `run_suite.py` first.
- Remaining audit findings P1/P2 (BULGU-2/3/4/6/7/8, F-01..F-07) stay OPEN;
  this suite covers only the BULGU-1/BULGU-5 soundness blocker (+2 invalid-J
  robustness faults found here).

## Protection receipts

- Before: manifest 73/73 OK, HEAD == `75b7e05…`, tracked tree clean.
- After: published-tree hashes identical (74 files), manifest 73/73 OK,
  `git status` shows only the new untracked followup dir. No writes under
  `research_representation_geometry_2026_09_13/`, no push, no network.
