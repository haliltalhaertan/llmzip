# RACE-V independent recomputation report

Independent verifier (D1V-pattern). All numbers recomputed from raw artifacts
(pkls, cleaned JSONs, audit layer) with own implementations; runner sources read
for exact definitions only, never executed as authority. No network.
Interpreter for faiss checks: `~/muse-work/faiss-python` (faiss 1.15.0, numpy 2.5.3).

## 1. Seal integrity — EXACT
`sha256sum` of `rb2/race_sign.py` = `6dbb6240…b74a` and `rb3/race_faiss.py` =
`67a4b5e4…aec3`, both digit-identical to `PRE_RUN_SEAL_local.json`. Match.

## 2. Sign side (RB2) — all EXACT
a. **Native anchors** (own implementation, full cohorts): LME = 0.5419751773049645
   (diff 0.0), LoCoMo = 0.23654714666441054 n=1535 (diff 0.0). Tolerance 1e-12: PASS.
b. **12 FR spot-checks** spanning NATIVE96/SPREAD80/BOT80/RAND80_s2/TOP48/BOT48 x
   LME+LoCoMo, recomputed from pkls with own tie-protocol implementation
   (5_100_000+lex*100_000+t*100+99; LoCoMo stable_archive_seed(ci,t)+99; 20 trials;
   K=3; lexsort((priority, distance))): **12/12 diff 0.0** (bit-identical).
   (One fix during verification: LoCoMo fallback qids use the *raw* QA index while
   distance rows use the filtered Cat1-4 position — handled explicitly.)
c. **Aggregates:** 6 arm means recomputed from stored per-question arrays
   (LME NATIVE96/TOP48/SPREAD80; LoCoMo NATIVE96/BOT80/RAND80_s2): all diff 0.0.
   **MATH-1 model column** for 5 (qid, arm) pairs vs exact f(S,T) identity: all diff 0.0.
d. **Validity callouts:** TOP48 LME = 0.34949468085106383 (0.34949468 ✓),
   SPREAD80 LME = 0.525258865248227 (0.52526 ✓),
   BOT80 LoCoMo = 0.23546142203796927 (0.23546 ✓).

## 3. Faiss side (RB3)
a. **Byte replay** (pinned API, faiss 1.15.0): RQ96=20, RQ32=12, IndexPQ(96,12,8)=12,
   ext-2bit=44 — EXACT.
b. **Deterministic retrain:** PQ retrained twice each on LME `001be529` (N=514) and
   `locomo_1` (N=369) with the runner's exact call sequence
   (IndexPQ(96,12,8).train/add/search(k=N), threads=1): codes **bit-identical** both
   archives. Per-archive codes are NOT persisted in the JSON (only an aggregate
   `codes_sha256`), so a code-hash comparison against the runner's run is
   **not checkable**; functionally, **5/5 A6 FRs recomputed diff 0.0** (1 LME + 4 locomo_1).
c. **JSON self-consistency:** 8 arms x 2 benchmarks — arms_summary vs arms_per_q means
   diff 0.0 throughout; W/T/L counts recomputed exact (16/16); mean_gap_pp exact
   (max dev 1.8e-15, float-print level); masked = [] everywhere (mask stats 0). EXACT.
d. **RaBitQ32 spot:** A4_spread_rot94101 rebuilt from inputs (spread-32 + seeded QR
   rotation + IndexRaBitQ train/add/search), 3 LME FRs recomputed: 3/3 diff 0.0.
   (Direct per-q-input replay beyond this is not separately persisted; the FR comparison
   above is the feasible check — done exactly.)

## 4. Official-vs-build comparison — claims CONFIRMED
Full numeric-tree diff: **RB2: exactly 1 diff** — `/meta/elapsed_s` 92.33 vs 86.48
(timing only; "one timing diff" ✓). **RB3: exactly 4 diffs** — `byte_worksheet`
ONLY in build (grep count in runner source = 0, annotation-only ✓), one last-ulp
`A4_random_axes94203/LoCoMo_FR` drift Δ=1.39e-17 ✓, and two timing fields
(`timing_s`, `smokes/S1/eval_s`) ✓. No other numeric difference anywhere.

## 5. Disposition arithmetic (official numbers, sealed K=40/41 sets)
- LME: SIGN 0.5419751773049645 − max competitor SIGN:SPREAD80 0.525258865248227 =
  **+1.6716312056737515pp** (matches "≈+1.67pp moderate"). Zone **MID**
  (kill −6.4 / promote +2.0; below promote, above kill).
- LoCoMo: SIGN 0.23654714666441054 − max competitor SIGN:BOT80 0.23546142203796927 =
  **+0.10857246264412701pp** (matches "≈+0.11pp parity"). Zone **MID**
  (kill −3.7 / promote +2.0).
- Membership verified: 40 (30 RAND + 3 SPREAD + BOT48 + TOP48/TOP64 + 3 RQ32-primary
  + PQ1) and 41 (+BOT80/64/48, single TOP48) with the sealed exclusions
  (random-32 secondary, A5 wrapper, TOP32, A7) honored.

## Not checkable (with reason)
- Per-archive PQ/RaBitQ code bytes vs the runner's run: only aggregate `codes_sha256`
  persisted → covered by bit-identical retrain + exact FRs instead.
- Official manifests list the runner `.py` files, which are not shipped inside
  `official_run/{sign,faiss}/`; those entries verified instead via the `rb2`/`rb3`
  copies + seal (all other manifest entries OK).
- Bootstrap/CI 16-cell disposition: out of official-run scope (deferred to analysis phase).

## Verdict
26_exact/26_checks (seal 2, anchors 2, FR spots 12, aggregates 6, MATH-1 5, validity 3,
bytes 4, PQ retrain 2+5, self-consistency 32, RaBitQ 3, tree-diff 2 files, disposition 2 —
zero diffs beyond the disclosed timing/last-ulp/annotation items).
Official-run numbers verified: **yes**.
