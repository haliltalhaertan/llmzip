[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# STATUS — representation-geometry cert repair (root-cause repair engineer)

Role: root-cause repair engineer. Own additive directory:
`research_representation_geometry_followup/candidate/` only.
Do NOT read other worker branches/output (cold comparison later).

## Boundary compliance (checked 2026-09-13/14 session)

- Base commit EXACT `75b7e057abbda4c46aabe3a7fb0d51f98b245ad0`; branch
  `muse/geometry-cert-repair-v3`; isolated worktree, current worktree only.
- No network/API/installs, no push (local commit only at end).
- Untouched: main, ledger, ops/CURRENT_STATE.json, frozen round4 (1021083),
  ALL files under `research_representation_geometry_2026_09_13/`.
- Before-hash: manifest `sha256sum -c MANIFEST.sha256` → 73/73 OK, zero
  failures; full-tree hashes saved at
  `research_representation_geometry_followup/candidate/receipts/before_hashes.sha256`.
- Task4F1 seal: no corpus/queries/gold/recall/benchmark/embeddings/refit.
  Only synthetic rational certificate tests with exact `Fraction` arithmetic.

## Audit verdicts (read, not re-litigated)

- Measurements: PASS WITH OBSERVATIONS (F-01..F-07 noted, untouched here).
- Repairs: REQUEST_CHANGES. BULGU-1 (BLOCKING, executed proof) + BULGU-5
  (P2, validator hole) are owned by this task; BULGU-2/3/4/6/7/8 stay OPEN.
- No different-family independence claim (same-family sessions).
  Measurements are declared refits, 15/470 archives, one seed; variance loss
  is NOT retrieval harm. Projector/gate observations remain open.

## Root-cause hypothesis (BULGU-1, from full read of certify_v2.py)

- POC `p=(-100,100,0,10000)`, `q=(-200,200,70000,0)`, `J=[1,4]`: truth is
  VARIES (+1 on (1,7/4), tie at 7/4, -1 on (7/4,4)); v2 certifies
  `ISOLATED_TIES` direction `-1`. False certificate, executed proof pending.
- Mechanism (two coupled defects, both in `certify_pair`):
  1. `rational_roots` hits its `limit` budget on the K=100-scaled input
     (`skipped=True` → no exact pre-cut at 7/4), while the unscaled twin
     pre-cuts 7/4 and correctly returns VARIES. Enumeration-budget skip
     changes behavior under score-preserving scaling.
  2. In BOTH isolator branches, `n_cross` counts only `brackets` whose
     endpoint verdicts differ. `exacts` (here 7/4, found by exact-hit
     bisection) are logged as ties but NEVER classified as crossing vs
     tangent, and the cells on either side are never sampled. So
     `n_cross=0` → falls through to `dirs.add(vm)` where `vm` is ONE
     midpoint sample (5/2 → -1) of the whole parent interval — interval
     classified by one sample with an unhandled crossing root inside.
- `validate_cert` (BULGU-5) has no order sampling for single-direction
  `ISOLATED_TIES`, so it passes the counterfeit (`None`).

## Plan

1. RED regression vs archived v2 (fail = wrong claim, not import error).
2. Additive `certify_v3.py`, same `certify_pair`/`P4` surface: classify EVERY
   exact root (sign-filtered, proven root-free adjacent cells), sample every
   cell, refuse ambiguity (UNRESOLVED). Handle endpoint-coincident roots,
   multiple roots, split brackets, numerator-negative reversal, zero
   polynomial, invalid intervals/budgets, enumeration-cap skips.
3. RED→GREEN vertical tests: VARIES w/ per-cell evidence, scale invariance,
   score-preserving transforms, doc-swap inversion, exhaustion→UNRESOLVED.
4. BULGU-5: independent `cert_validator_v3.py` (own exact arithmetic, no
   import from certify_v3, no trust in claimed direction) + semantics tests;
   proof-based coverage validation, sample scans labeled as falsification.
5. Bounded synthetic fuzz + receipts; unresolved rate secondary to soundness.
6. FIX_DISPOSITION.md (old/new mappings, raw receipts, manifest), local
   commit of own dir only, final SHA + runnable reviewer command.

## Phase log

- [x] Before-hash (73/73 OK) + STATUS.md created.
- [x] RED run vs v2 (`receipts/red_vs_v2.txt`, exit 1, wrong claim).
- [x] certify_v3.py implemented (smoke exit 0, POC VARIES).
- [x] GREEN vertical tests (`receipts/green_vertical.txt`, 80/80).
- [x] Validator + BULGU-5 tests (`receipts/green_validator.txt`, 19/19).
- [x] Fuzz (`receipts/green_fuzz.txt`, n=2000 eff=1765, 0 violations) +
  after-hash compare (TREE_IDENTICAL) + FIX_DISPOSITION.md.
- [ ] Local commit of own directory only (next), then final SHA.
