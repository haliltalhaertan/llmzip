# 05_f1 audit — F1 execution & frozen contracts (HARD R2)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE].
Neutral: neither STOP nor CONTINUE presumed. Prior reports treated as fallible.

Scope of this role: previously unreviewed F1 execution + frozen contracts only
(R1 explicitly left `task4f1_*` / `research_f1_execution_2026_09_14/` internals
NOT REVIEWED — `audit_hard_r1/repro/HARD_AUDIT_REPRO.md:30-31`,
`audit_hard_r1/integrity/PROJECT_COVERAGE.csv` rows 6, 12). Total items checked:
**24 data rows in COVERAGE.csv** (25 lines incl. header, mechanically counted
with `wc -l` + csv parse). Of these: 8 REVIEWED, 2 REVIEWED+TESTED, 1 explicit
verification, 3 TESTED, 1 CHECKED, 4 SAMPLED, 5 NOT RUN / NOT REVIEWED variants.
Nothing not-run is presented as a pass.

## 1. What was actually located (decoder / protocol / references)

**Task4F1 BEAM decoder+protocol** (the only frozen execution path for the
preregistered scale profile) is
`task4f1_execution_candidate_v7_2026_09_03/v52_t4f1_beam_retrieval.py`
(runner sha256 `f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8`,
byte-identical since V4; copy in `originals/v52_t4f1_beam_retrieval.py`):
- Pins: BEAM commit `3e12035532eb85768f1a7cd779832b650c4b2ef9` (:38), cohort
  sha256 `9b70e16f…` (:39), `TOP_K=3` (:55), Haar seeds 43001–43005 (:56),
  ITQ seeds 101–505 (:58), `INVARIANCE_TOLERANCE=1e-12` (:61), tie prefix
  `V52_T4F0_TIE_PRIORITY_V1` (:62), auth schema `V52_T4F1_RUN_AUTHORIZATION_V4` (:76).
- Representation: archive-only TF-IDF word+char → normalize → SVD-32 → mixed-96
  → center (:461 `fit_archive_representation`); queries transformed after fit
  (:503 `transform_queries`). No query/label enters the fit.
- Retrieval: `C>=0` sign codes, Hamming + frozen SHA tie priority
  (:528 `rank_hamming`, `tie_priority` above it); signed-permutation control
  (:535), Haar rotation with orthonormality gate (:542), archive-only ITQ
  (:555), FR@3/ANY@3/ALL@3 (:570), 20 nuisance-trial replication rows (:577),
  sign-code digest (not float bytes) for canary (:615), per-archive eval (:628).
- **No run/finalize was executed here** (forbidden without fresh authorization).

**Governing acceptance contract** is the sealed prereg
`docs/v52/task4f1/TASK4F1_PREREGISTRATION_DRAFT_2026-09-03.md` (copy in
`originals/`), bound by `TASK4F1_PREREGISTRATION_SEAL_V3_2026-09-04.json`
(sha256 `e906c6d2…`). Estimand (draft:106):
`D_t = mean_i[FR@3(Native SIGN96)_i − mean-over-5-Haar FR@3(HAAR96_SIGN)_i]`,
Haar seeds fixed (:114), ceiling-free stratum `|gold|≤3` as cross-tier
instrument (:123–127), exact-rational sign classification with **no tolerance**
(:239–241), stop rule (:7), four binding execution conditions (:8). Seal
explicitly **does NOT authorize execution** and creates no HMAC key.

**F1 E1 contract** (different lineage from BEAM) is restated from bytes in
`originals/CONTRACT_CHECKLIST.md` (source
`origin/research/e1-v2-raw-cache-recovery-r2-2026-09-13:.../R2_COMPETITION_RERUN_CONTRACT.md`,
boxes C1–C10). Public numeric entrypoints exercised:
`originals/f1_competition.py:37/52/67/86/140/155/173/196/222/236`
(`col_mean_squares`, `topbot_axes`, `hamming_distances`, `competition_row`,
`query_row`, `average_ranks`, `spearman_rho`, `benchmark_summary`,
`check_headline_gates`, `cluster_bootstrap`). Original per-query reference
`INDEPENDENT_QUERY_ROWS.json` is **unpublished/absent** (see finding F-A).

## 2. Findings (severity-ordered)

### F-A [HIGH] F1 stays OPEN: identity, gates, LoCoMo, independence all unmet
- **Test:** FX5 applied contract `check_headline_gates(tol=1e-12)` to local
  `f1_real_fr3` means; FX6 equality check local vs branch evidence; manifest
  inspection (482 file rows, no tarball hashes).
- **Observed:** gates FAIL LME (`dsign=1.58e-04`, `dfloat=5.55e-17`), REALTALK
  (`dsign=7.6e-04`), PerLTQA (`dsign=2.8e-06`); LoCoMo missing. Local
  `results.json` == branch `evidence/f1_results_fr3.json` exactly (FX6 PASS,
  sha `c4682230…`), with delta diffs LME +0.0158 pp / PerLTQA +0.00027 pp /
  REALTALK +0.076 pp. `MANIFEST.sha256` carries 482 **file-level** shas only;
  contract C1 pins three **tarball** shas (`a16bdf95…`, `87d6312e…`,
  `370ea409…`) — irreproducible from extracted trees. LoCoMo leg absent
  everywhere readable. Same-model-family execution (coordinator-commissioned).
  `AUDIT_RESPONSE.md` concedes all of: still OPEN, not independent, gate
  skipped-then-failed, query-rows file unpublished.
- **Interpretation:** the six-coefficient reproduction is real but unlicensed as
  frozen-V2 values — exactly the contract's own F1 impact sentence ("not
  licensed … must be regenerated"). Blocker moved from "nobody ran it" to
  "no independent party can check it at 1e-12 without the missing file."
- **Limits:** did not re-open the 482 pickle caches (heavy); relied on
  committed manifests + branch bytes. Tarball absence taken from
  `CACHE_INVENTORY.md`/contract, spot-verified by manifest head.

### F-B [HIGH] Tie-estimator substitution changes the estimand (expectation ≠ value)
- **Test:** FX2 synthetic tied case (scores `[5,4,4,4,4,1]`, gold {1,2}, K=3):
  exact `E[FR@3]=0.5` vs 2000 Monte-Carlo draws and 100× NT=20 batch means.
- **Observed:** exact 0.5, MC mean 0.498, MC sd 0.29, NT=20 batch spread 0.275.
  Auditor-measured NT=20 seed spread 2.7e-03 dwarfs every residual (LME
  1.58e-04). FX2/FX2b PASS.
- **Interpretation:** frozen scorer averages NT=20 seeded permutations; R2
  execution uses exact expectation. The substitution is the better estimator
  (order-independent) but its relation to the frozen number is equality **in
  expectation**, not agreement in value. A 1e-12 gate is unmeetable by the
  exact estimator **and** by the frozen estimator against itself. Accept
  `AUDIT_RESPONSE.md` F-2/F-3 dispositions; do not cite residual size as
  replication precision.

### F-C [MEDIUM-HIGH] Matched-budget status differs between the two F1-adjacent claims
- **Test:** FX3 structural arithmetic (no heavy compute).
- **Observed:** SIGN96/HAAR96/ITQ96 = 96 bits = **12 B**. E1 `Delta_q` float arm
  (cosine on 96-D float) = 384 B (float32) / 768 B (float64) — 32–64× larger.
- **Interpretation:** Task4F1 `D_t` (Native vs mean-of-5-Haar) **is**
  12 B-vs-12 B matched. E1 F1 `Delta_q` (SIGN Hamming vs float cosine) is
  **unmatched by construction**. F1 `rho` magnitudes and `Delta_q` headline
  deltas (+10.05/−6.27/+5.30 pp) must never be cited as 12-byte-matched
  superiority evidence. The twelve-byte pilot/race track is a separate
  lineage (outside this role's scope; not adjudicated here).

### F-D [MEDIUM] "Frozen" labels on R2 numbers lack approval
- **Sources:** branch `README.md:27` ("Frozen headline control"),
  `coord_f1_real_fr3.py:118` `FROZEN={…10.037943/−6.275/5.2241}`,
  `results.json` `frozen_delta_pp` fields.
- **Observed:** values match auditor-recorded references to shown precision,
  but Seal V3 denies run authorization/outcome access and F1 C1/C3 are unmet.
- **Interpretation:** "frozen" here is coordinator shorthand, not a
  seal-approved or independently-accepted frozen value. Citation must carry
  the contract's own caveat. No evidence of intent to mislead (labels sit
  beside disclosed diffs and an OPEN disposition); still, downstream readers
  inherit the caveat only if it is propagated.

### F-E [MEDIUM] Precision downgrade: 4 dp comparison vs 1e-12 contract
- **Test:** FX4 max `|full−4dp|` over C7 targets = 4.6e-05 ≫ 1e-12.
- **Observed:** coordinator `AUD` dict uses `(0.1417, 0.1405 / 0.0979, 0.1228 /
  0.2542, 0.2798)`; contract targets are full-precision
  (`0.14168629…/0.14045379…` etc. in `f1_competition.py:212-219`). Reported
  diffs (≤2.75e-04) compound rounding with the F-B estimator change.
- **Interpretation:** "reproduced to rounding" is ~8 orders weaker than the
  contract gate. `AUDIT_RESPONSE.md` F-1 accepts this; remedy (publish
  `INDEPENDENT_QUERY_ROWS.json`) is the correct unblocker, still outstanding.

### F-F [LOW-MEDIUM, CLOSED] Errata attribution corrected (double-centering)
- **Test:** branch `ERRATA_COORDINATOR.md` CORRECTION table + FX1-path reasoning.
- **Observed:** E1 (re-centering pre-centered caches, colmean ~1e-16) moves LME
  by +0.000000 pp; E2 (ALL@3 vs FR@3) accounts for the full −0.376478 pp.
  Original joint attribution preserved + superseded in place per convention.
- **Interpretation:** handling is exemplary; no further action. E1 remains a
  genuine methodological hazard on non-pre-centered caches.

### F-G [LOW] Trial-row `.17g` + exact-rational rule verified, binding-8 gate open
- **Test:** FX7 round-trip on `2/3, 1/7, 0.1+0.2` → loss 0.0; runner:577-613
  formats fractional recall with `.17g`; draft:239-241 demands exact-rational
  `D_t` decidability with no tolerance.
- **Observed:** PASS; but classification must parse the decimal, never compare
  floats with tolerance. Seal binding 8 (pre-run rational-sign condition) is
  the remaining fidelity gate alongside the V7 package audit.
- **Limits:** binding-8 verifier bytes read only via seal description; the
  `tools/verify_preregistration_seal.py` 38-control suite NOT RUN.

### F-H [INFO] Real implementation vs staged plans
- **Real:** `f1_competition.py` proven on hand fixtures (FX1 exact match to
  report §3: `v=[2.0,3.8,3.8,3.0]`, `d_TOP=[0,2,2,0,2]`,
  `d_BOT=[0,2,0,2,1]`, gaps `(1.0,0.5)/(0.0,2.0)/(−2.0,0.5)`, min-gold
  `(0,0)/(0,2)/(−3,0)`; Spearman `0.5` / `−√3/2`; single-gold theorem holds on
  20/20 random 96-D trials). Coordinator FR@3 execution reproduces all six
  auditor coefficients to rounding on 470/8265/705 queries with disclosed
  multi-gold rates (62.98/28.09/54.75%).
- **Staged (not executed):** BEAM scale-profile `D_t` across 100K/500K/1M/10M
  (355/629/553/175 qs, 20/35/31/10 archives); V7 package close-out; any
  `run/finalize` with HMAC authorization. Runner execution behaviour
  audit-confirmed since V4, but packaging (V5/V6 BLOCKED, V7 Gates 2–7
  evidence at `16dc6131`) plus prereg seal still leave run BLOCKED per
  `START_HERE_V52_4F1.md`. The scale/role/levels/whitening narratives in
  `RESEARCH_SUMMARY.md` are exploratory probes on unsealed E1 caches, kill
  their own hypotheses, and establish no mechanism (eight dead candidates).

## 3. Open fidelity gates (checklist)
1. Publish `INDEPENDENT_QUERY_ROWS.json` (F-1 remedy) — else 1e-12 unreachable.
2. Settle estimator identity: exact expectation vs NT=20 sampling in the gate.
3. Supply LoCoMo per-query float surface + tarball-level archive identity.
4. Independent (different-family) re-execution.
5. Task4F1: V7 package acceptance + binding-8 pre-run condition + fresh V4
   authorization with Head-Researcher HMAC custody — run stays BLOCKED until all.

## 4. Limits & blockers
- `compute.sh` unusable (lock file on read-only FS) and `timeout(1)` blocked
  (`Operation not permitted`); fixtures are deliberately light (<10 s,
  single-thread BLAS, `PYTHONDONTWRITEBYTECODE=1`) so direct execution is
  compliant. No probe exceeded 180 s; no heavy recomputation attempted.
- Environment is not the BEAM lock (2.5.3/1.18.1/1.9.1 vs
  2.3.2/1.16.1/1.7.1); BEAM outcome gates therefore correctly NOT RUN.
- Full `verify_f1.py` (27 checks) not rerun; equivalent hand oracle rerun as
  explicit verification (FX1). Branch session analyses (scale/role/levels,
  whitening/Xiao) read at summary level, not re-verified query-by-query.
- Same-CLI agents give only partial independence (noted in branch and here).

## 5. Whole-project parts OUTSIDE this role's scope
Metrics/ties/FR@3-vs-ALL@3 join semantics (01); ITQ-vs-rotation five-init
comparison (02); geometry/sigma/sign-float theory (03); comparator fairness,
BM25/cascade/RRF ceilings (04); dense/MRL/residual/alternate lines (06);
KV/inverse-memory continuation (07); static-storage/rank/membership
certificates (08); clean-room portability T1–T3 (09); whole-project coverage
ledger, STOP authority, literature-novelty adjudication (10); twelve-byte
budget race, BEAM corpus materialization, Drive fetches, model downloads,
external APIs (all excluded by task constraints).

## Provenance
- Commits/refs: `ccedd56` (f1-execution tip), `689298e` (F1 contract
  execution), `5a609e3` (V8), `16dc6131`/`c88455b` (v7 evidence / v6 BLOCKED),
  `a590f62/641568d/6243ba6` (v3/v4/v5 audits, from REFS_BEFORE.txt lineage).
- Copies + shas in `originals/` (runner `f96cba2c…`, draft `5e618981…`, seal
  `e906c6d2…`, evidence `c4682230…`). Fixtures: `scripts/fixtures_f1.py` →
  `outputs/fixture_results.json`; this report + `COVERAGE.csv` +
  `evidence/evidence.json` + `STATUS.md`.
